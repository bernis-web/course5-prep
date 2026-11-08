"""Run an auditable, local kNN cross-species label-transfer evaluation.

The evaluator intentionally requires an explicit representation and explicit
reference/query arrays. It never falls back between X and obsm, and it does
not start cloud jobs or mutate source data.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np


class EvaluationError(ValueError):
    """Raised when an evaluation input violates the audit contract."""


def _matrix(value: Any, name: str) -> np.ndarray:
    array = np.asarray(value, dtype=float)
    if array.ndim != 2 or array.shape[0] == 0 or array.shape[1] == 0:
        raise EvaluationError(f"{name} must be a non-empty 2D matrix")
    if not np.isfinite(array).all():
        raise EvaluationError(f"{name} contains non-finite values")
    return array


def _strings(value: Sequence[Any], name: str, expected: int) -> list[str]:
    result = [str(item) for item in value]
    if len(result) != expected or any(not item for item in result):
        raise EvaluationError(f"{name} must contain exactly {expected} non-empty strings")
    return result


def _duplicate_values(values: Sequence[str]) -> list[str]:
    counts = Counter(values)
    return sorted(value for value, count in counts.items() if count > 1)


def _cosine_distances(reference: np.ndarray, query: np.ndarray) -> np.ndarray:
    ref_norm = np.linalg.norm(reference, axis=1)
    query_norm = np.linalg.norm(query, axis=1)
    if np.any(ref_norm == 0) or np.any(query_norm == 0):
        raise EvaluationError("zero-norm vectors are not supported for cosine distance")
    similarity = (query / query_norm[:, None]) @ (reference / ref_norm[:, None]).T
    return np.clip(1.0 - similarity, 0.0, 2.0)


def _f1_metrics(y_true: list[str], y_pred: list[str], labels: list[str]) -> tuple[float, float, dict[str, list[list[int]]]]:
    if not y_true:
        return 0.0, 0.0, {"labels": labels, "values": [[0 for _ in labels] for _ in labels]}
    counts = {label: {"tp": 0, "fp": 0, "fn": 0} for label in labels}
    matrix = [[0 for _ in labels] for _ in labels]
    index = {label: position for position, label in enumerate(labels)}
    for truth, prediction in zip(y_true, y_pred):
        matrix[index[truth]][index[prediction]] += 1
        for label in labels:
            if truth == label and prediction == label:
                counts[label]["tp"] += 1
            elif truth == label:
                counts[label]["fn"] += 1
            elif prediction == label:
                counts[label]["fp"] += 1
    f1_values = []
    for label in labels:
        item = counts[label]
        denominator = 2 * item["tp"] + item["fp"] + item["fn"]
        f1_values.append((2 * item["tp"] / denominator) if denominator else 0.0)
    macro = float(sum(f1_values) / len(labels)) if labels else 0.0
    total = sum(sum(row) for row in matrix)
    micro = float(sum(counts[label]["tp"] for label in labels) / total) if total else 0.0
    return macro, micro, {"labels": labels, "values": matrix}


def _score_label_set(
    truth: list[str],
    predictions: list[dict[str, Any]],
    truth_key: str,
    prediction_key: str,
) -> dict[str, Any]:
    eligible = [item for item in predictions if not item["abstained"]]
    y_true = [str(item[truth_key]) for item in eligible]
    y_pred = [str(item[prediction_key]) for item in eligible]
    labels = sorted(set(truth) | set(y_true) | set(y_pred))
    macro, micro, matrix = _f1_metrics(y_true, y_pred, labels)
    top1 = sum(item[prediction_key] == item[truth_key] for item in eligible) / len(eligible) if eligible else 0.0
    top3 = sum(item[truth_key] in item["top_k"][:3] for item in eligible) / len(eligible) if eligible else 0.0
    n_eligible = len(predictions)
    coverage = len(eligible) / n_eligible if n_eligible else 0.0
    by_class: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for item in predictions:
        label = str(item[truth_key])
        by_class[label][1] += 1
        if not item["abstained"]:
            by_class[label][0] += 1
    return {
        "n_eligible": n_eligible,
        "n_scored": len(eligible),
        "accuracy": top1,
        "macro_f1": macro,
        "micro_f1": micro,
        "top1_accuracy": top1,
        "top3_accuracy": top3,
        "coverage": coverage,
        "abstention_rate": 1.0 - coverage,
        "confusion_matrix": matrix,
        "per_class_coverage": {
            label: (values[0] / values[1] if values[1] else 0.0)
            for label, values in sorted(by_class.items())
        },
    }


def evaluate_transfer(
    reference_embeddings: Any,
    reference_barcodes: Sequence[Any],
    reference_labels: Sequence[Any],
    query_embeddings: Any,
    query_barcodes: Sequence[Any],
    query_labels: Sequence[Any],
    *,
    label_mapping: Mapping[str, str] | None = None,
    k: int = 15,
    abstain_below: float | None = None,
    representation: str = "explicit_input",
    protocol: str = "inductive",
) -> dict[str, Any]:
    """Evaluate reference-to-query transfer with auditable barcode filtering."""
    reference = _matrix(reference_embeddings, "reference_embeddings")
    query = _matrix(query_embeddings, "query_embeddings")
    if reference.shape[1] != query.shape[1]:
        raise EvaluationError("reference and query representations must have the same dimensions")
    ref_barcodes = _strings(reference_barcodes, "reference_barcodes", reference.shape[0])
    query_barcodes_all = _strings(query_barcodes, "query_barcodes", query.shape[0])
    ref_labels = _strings(reference_labels, "reference_labels", reference.shape[0])
    query_labels_all = _strings(query_labels, "query_labels", query.shape[0])
    if not isinstance(k, int) or isinstance(k, bool) or k < 1:
        raise EvaluationError("k must be a positive integer")
    if abstain_below is not None and not 0.0 <= float(abstain_below) <= 1.0:
        raise EvaluationError("abstain_below must be between 0 and 1")
    if protocol not in {"transductive", "inductive"}:
        raise EvaluationError("protocol must be 'transductive' or 'inductive'")

    ref_duplicates = _duplicate_values(ref_barcodes)
    query_duplicates = _duplicate_values(query_barcodes_all)
    ref_keep = np.array([barcode not in ref_duplicates for barcode in ref_barcodes], dtype=bool)
    query_overlap = sorted(set(ref_barcodes) & set(query_barcodes_all))
    query_keep = np.array(
        [barcode not in query_duplicates and barcode not in query_overlap for barcode in query_barcodes_all],
        dtype=bool,
    )
    if not ref_keep.any():
        raise EvaluationError("no unique reference barcodes remain after duplicate exclusion")
    if not query_keep.any():
        raise EvaluationError("no eligible query barcodes remain after overlap/duplicate exclusion")

    ref = reference[ref_keep]
    ref_ids = [value for value, keep in zip(ref_barcodes, ref_keep) if keep]
    ref_y = [value for value, keep in zip(ref_labels, ref_keep) if keep]
    q = query[query_keep]
    q_ids = [value for value, keep in zip(query_barcodes_all, query_keep) if keep]
    q_y = [value for value, keep in zip(query_labels_all, query_keep) if keep]
    distances = _cosine_distances(ref, q)
    mapping = {str(key): str(value) for key, value in (label_mapping or {}).items()}
    mapped_ref = [mapping.get(label, label) for label in ref_y]
    mapped_query = [mapping.get(label, label) for label in q_y]
    predictions: list[dict[str, Any]] = []
    neighbor_limit = min(k, len(ref_y))
    for row, (barcode, truth, mapped_truth) in enumerate(zip(q_ids, q_y, mapped_query)):
        order = np.lexsort((np.arange(len(ref_y)), distances[row]))[:neighbor_limit]
        scores: dict[str, float] = defaultdict(float)
        for index in order:
            scores[ref_y[int(index)]] += 1.0 / (float(distances[row, int(index)]) + 1e-12)
        ranked = sorted(scores, key=lambda label: (-scores[label], label))
        top_label = ranked[0]
        total = sum(scores.values())
        confidence = scores[top_label] / total if total else 0.0
        predictions.append(
            {
                "barcode": barcode,
                "truth_exact": truth,
                "truth_mapped": mapped_truth,
                "predicted_exact": top_label,
                "predicted_mapped": mapping.get(top_label, top_label),
                "top_k": ranked,
                "confidence": float(confidence),
                "abstained": bool(abstain_below is not None and confidence < float(abstain_below)),
                "neighbor_barcodes": [ref_ids[int(index)] for index in order],
            }
        )
    return {
        "representation": representation,
        "protocol": protocol,
        "parameters": {"k": k, "metric": "cosine", "abstain_below": abstain_below},
        "audit": {
            "n_reference_input": len(ref_barcodes),
            "n_query_input": len(query_barcodes_all),
            "n_reference": len(ref_y),
            "n_query": len(q_y),
            "n_scored": len(predictions),
            "excluded_reference_duplicate_barcodes": ref_duplicates,
            "excluded_query_duplicate_barcodes": query_duplicates,
            "excluded_query_overlap_barcodes": query_overlap,
            "self_barcode_exclusion": True,
            "duplicate_barcode_exclusion": True,
        },
        "metrics": {
            "exact": _score_label_set(q_y, predictions, "truth_exact", "predicted_exact"),
            "mapped": _score_label_set(mapped_query, predictions, "truth_mapped", "predicted_mapped"),
        },
        "predictions": predictions,
    }


REQUIRED_NPZ_KEYS = (
    "reference_embeddings",
    "query_embeddings",
    "reference_barcodes",
    "query_barcodes",
    "reference_labels",
    "query_labels",
)


def load_npz_bundle(path: Path) -> dict[str, Any]:
    """Load the explicit evaluator bundle without choosing a representation."""
    if not path.is_file():
        raise EvaluationError(f"input bundle does not exist: {path}")
    try:
        with np.load(path, allow_pickle=False) as archive:
            missing = [key for key in REQUIRED_NPZ_KEYS if key not in archive.files]
            if missing:
                raise EvaluationError(f"input bundle is missing keys: {', '.join(missing)}")
            return {key: archive[key] for key in REQUIRED_NPZ_KEYS}
    except OSError as exc:
        raise EvaluationError(f"cannot read input bundle {path}: {exc}") from exc


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-npz", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--representation",
        choices=("X", "obsm/macrogenes"),
        required=True,
        help="representation used to create the explicit NPZ bundle; no implicit fallback is allowed",
    )
    parser.add_argument("--k", type=int, default=15)
    parser.add_argument("--abstain-below", type=float, default=None)
    parser.add_argument("--label-mapping", type=Path, default=None)
    parser.add_argument("--protocol", choices=("transductive", "inductive"), required=True)
    args = parser.parse_args()
    try:
        bundle = load_npz_bundle(args.input_npz)
        mapping: dict[str, str] = {}
        if args.label_mapping is not None:
            value = json.loads(args.label_mapping.read_text(encoding="utf-8"))
            if not isinstance(value, dict) or not all(isinstance(key, str) and isinstance(item, str) for key, item in value.items()):
                raise EvaluationError("label mapping must be a JSON object of string to string")
            mapping = value
        result = evaluate_transfer(
            bundle["reference_embeddings"],
            bundle["reference_barcodes"].tolist(),
            bundle["reference_labels"].tolist(),
            bundle["query_embeddings"],
            bundle["query_barcodes"].tolist(),
            bundle["query_labels"].tolist(),
            label_mapping=mapping,
            k=args.k,
            abstain_below=args.abstain_below,
            representation=args.representation,
            protocol=args.protocol,
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    except (EvaluationError, OSError, json.JSONDecodeError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
