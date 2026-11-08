"""Run the six-direction transductive-formal re-evaluation of v71/v72.

Consumes the bundles and build manifest produced by
``build_transductive_bundles.py``, verifies every hash, evaluates
exact/coarse/fine separately with the frozen evaluator, and writes one JSON
per direction/level plus a ``result-index.json`` summary.  No network access,
no DCS client, and no ``READY`` marker unless every step succeeded.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from build_transductive_bundles import SCOPE_STRING, _sha256_file, safe_file_stem  # noqa: E402
from evaluate_cross_species_transfer import (  # noqa: E402
    EvaluationError,
    evaluate_transfer,
    load_npz_bundle,
)

LEVELS = ("exact", "coarse", "fine")
SUMMARY_METRIC_KEYS = ("accuracy", "macro_f1", "micro_f1", "top1", "top3", "coverage", "abstention_rate")


class RunnerError(ValueError):
    """Raised when the v74 run cannot proceed without violating the audit contract."""


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RunnerError(f"cannot read JSON {path}: {exc}") from exc


def _verify_hash(path: Path, expected: str, label: str) -> None:
    if not path.is_file():
        raise RunnerError(f"{label} missing: {path}")
    actual = _sha256_file(path)
    if actual != expected:
        raise RunnerError(
            f"{label} SHA-256 mismatch for {path}: expected {expected}, got {actual}"
        )


def run_all(bundle_dir: Path, output_dir: Path, k: int = 15) -> Path:
    """Evaluate every direction/level bundle and write the result index."""
    bundle_dir = Path(bundle_dir)
    output_dir = Path(output_dir)
    manifest_path = bundle_dir / "build-manifest.json"
    if not manifest_path.is_file():
        raise RunnerError(f"build manifest missing: {manifest_path}")
    manifest = _load_json(manifest_path)
    if manifest.get("evaluation_scope") != SCOPE_STRING:
        raise RunnerError(
            "build manifest evaluation_scope missing or changed: "
            f"{manifest.get('evaluation_scope')!r}"
        )

    per_direction = manifest.get("per_direction")
    if not isinstance(per_direction, dict) or not per_direction:
        raise RunnerError("build manifest has no per_direction bundles")

    results_dir = output_dir
    results_dir.mkdir(parents=True, exist_ok=True)

    index_directions: dict[str, Any] = {}
    for direction, levels in sorted(per_direction.items()):
        for level in LEVELS:
            block = levels.get(level)
            if not isinstance(block, dict):
                raise RunnerError(f"{direction}/{level}: no bundle block in build manifest")
            bundle_rel = block.get("bundle")
            if not bundle_rel:
                raise RunnerError(f"{direction}/{level}: bundle path missing")
            bundle_path = bundle_dir / bundle_rel
            _verify_hash(bundle_path, block.get("bundle_sha256", ""), f"{direction}/{level} bundle")

            mapping_path = bundle_dir / "mappings" / f"{level}_{safe_file_stem(direction)}.json"
            mapping_sha = block.get("mapping_sha256")
            mapping: dict[str, str] = {}
            if level == "exact":
                if mapping_sha is None:
                    mapping_sha = _sha256_file(mapping_path)
                _verify_hash(mapping_path, mapping_sha, f"{direction}/{level} mapping")
            else:
                _verify_hash(mapping_path, mapping_sha or "", f"{direction}/{level} mapping")
                loaded = _load_json(mapping_path)
                if not isinstance(loaded, dict):
                    raise RunnerError(f"{mapping_path} must contain a JSON object")
                mapping = {str(key): str(value) for key, value in loaded.items()}

            bundle = load_npz_bundle(bundle_path)
            try:
                evaluation = evaluate_transfer(
                    bundle["reference_embeddings"],
                    bundle["reference_barcodes"].tolist(),
                    bundle["reference_labels"].tolist(),
                    bundle["query_embeddings"],
                    bundle["query_barcodes"].tolist(),
                    bundle["query_labels"].tolist(),
                    label_mapping=mapping,
                    k=k,
                    representation="obsm/macrogenes",
                    protocol="transductive",
                )
            except EvaluationError as exc:
                raise RunnerError(f"{direction}/{level}: {exc}") from exc

            result = {
                "direction": direction,
                "level": level,
                "bundle": bundle_rel,
                "bundle_sha256": block.get("bundle_sha256"),
                "mapping_sha256": mapping_sha,
                "protocol": "transductive",
                "k": k,
                "representation": "obsm/macrogenes",
                "evaluation_scope": SCOPE_STRING,
                "evaluation": evaluation,
            }
            result_path = results_dir / f"{level}_{safe_file_stem(direction)}.json"
            result_path.write_text(
                json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8"
            )

            metrics = evaluation.get("metrics", {})
            requested = metrics.get("exact" if level == "exact" else "mapped", {})
            summary_metrics = {
                key: requested[key] for key in SUMMARY_METRIC_KEYS if key in requested
            }
            index_directions.setdefault(direction, {})[level] = {
                "metrics": summary_metrics,
                "audit": evaluation.get("audit", {}),
                "n_predictions": len(evaluation.get("predictions", [])),
                "bundle": bundle_rel,
                "bundle_sha256": block.get("bundle_sha256"),
            }

    index = {
        "build_version": "v74",
        "evaluation_scope": SCOPE_STRING,
        "protocol": "transductive",
        "k": k,
        "representation": "obsm/macrogenes",
        "source_sha256": manifest.get("source_sha256"),
        "directions": index_directions,
    }
    index_path = results_dir / "result-index.json"
    index_path.write_text(
        json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    ready_path = results_dir / "READY.json"
    ready_path.write_text(
        json.dumps(
            {
                "ready": True,
                "index": index_path.name,
                "index_sha256": _sha256_file(index_path),
            },
            ensure_ascii=False,
            indent=1,
        ),
        encoding="utf-8",
    )
    return index_path


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Run the v74 transductive-formal six-direction re-evaluation."
    )
    parser.add_argument("--bundle-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--k", type=int, default=15)
    args = parser.parse_args()
    try:
        index_path = run_all(args.bundle_dir, args.output_dir, k=args.k)
    except (RunnerError, EvaluationError) as exc:
        print(json.dumps({"ran": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        raise SystemExit(2) from exc
    print(json.dumps({"ran": True, "index": str(index_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
