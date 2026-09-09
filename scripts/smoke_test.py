"""Synthetic evaluator smoke test for the course 5 benchmark design.

This module deliberately does not run SATURN, SAMap, scVI, or download data.
It validates the metric/output contract on a small synthetic embedding first.
"""

from __future__ import annotations

import argparse
import json
import platform
import time
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import chisquare
from sklearn.metrics import silhouette_score
from sklearn.neighbors import NearestNeighbors


def _as_strings(values: np.ndarray) -> np.ndarray:
    return np.asarray(values).astype(str)


def evaluate_labels(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, Any]:
    """Return per-class macro-F1 without assuming labels are numeric."""
    true = _as_strings(y_true)
    pred = _as_strings(y_pred)
    if true.shape != pred.shape or true.ndim != 1:
        raise ValueError("y_true and y_pred must be one-dimensional arrays of equal length")
    if len(true) == 0:
        raise ValueError("label arrays must not be empty")

    classes = np.unique(true)
    f1_values: list[float] = []
    per_class: dict[str, float] = {}
    for cls in classes:
        tp = float(np.sum((true == cls) & (pred == cls)))
        fp = float(np.sum((true != cls) & (pred == cls)))
        fn = float(np.sum((true == cls) & (pred != cls)))
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2.0 * precision * recall / (precision + recall) if precision + recall else 0.0
        per_class[str(cls)] = f1
        f1_values.append(f1)
    return {
        "macro_f1": float(np.mean(f1_values)),
        "n_labels": int(len(classes)),
        "per_class_f1": per_class,
    }


def evaluate_embedding(
    embedding: np.ndarray,
    labels: np.ndarray,
    batches: np.ndarray,
    neighbors: int = 15,
) -> dict[str, Any]:
    """Compute bounded embedding metrics for a fixed embedding.

    ``kbet_rejection_rate`` is intentionally named as a proxy: it applies a
    chi-square goodness-of-fit test to each cell's batch neighborhood. A full
    kBET package run should replace this field in the real benchmark.
    """
    x = np.asarray(embedding, dtype=float)
    label_values = _as_strings(labels)
    batch_values = _as_strings(batches)
    if x.ndim != 2 or len(x) < 3:
        raise ValueError("embedding must be a two-dimensional array with at least 3 rows")
    if len(label_values) != len(x) or len(batch_values) != len(x):
        raise ValueError("embedding, labels, and batches must have the same number of rows")
    if len(np.unique(label_values)) < 2:
        raise ValueError("silhouette requires at least two label classes")

    k = min(max(2, int(neighbors)), len(x) - 1)
    nn = NearestNeighbors(n_neighbors=k + 1).fit(x)
    indices = nn.kneighbors(return_distance=False)[:, 1:]
    unique_batches, global_counts = np.unique(batch_values, return_counts=True)
    global_prob = global_counts / global_counts.sum()
    ilisi_values: list[float] = []
    rejected = 0
    for row in indices:
        local = np.array([np.sum(batch_values[row] == batch) for batch in unique_batches], dtype=float)
        probabilities = local / local.sum()
        ilisi_values.append(float(1.0 / np.sum(probabilities**2)))
        expected = global_prob * local.sum()
        if len(unique_batches) > 1 and np.any(expected > 0):
            p_value = float(chisquare(local, expected)[1])
            rejected += int(p_value < 0.05)

    return {
        "silhouette": float(silhouette_score(x, label_values)),
        "ilisi": float(np.mean(ilisi_values)),
        "kbet_rejection_rate": float(rejected / len(indices)),
        "kbet_method": "chi2_neighborhood_proxy",
        "neighbors": int(k),
    }


def _synthetic_case(seed: int, n_cells: int, n_features: int) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    if n_cells < 12 or n_features < 2:
        raise ValueError("n_cells must be >= 12 and n_features must be >= 2")
    rng = np.random.default_rng(seed)
    class_names = np.array(["CM", "FB", "EDC"])
    labels = np.resize(class_names, n_cells)
    batches = np.resize(np.array(["species_1", "species_2", "species_3"]), n_cells)
    prototypes = np.zeros((3, n_features))
    prototypes[0, 0] = 3.5
    prototypes[1, 1] = 3.5
    prototypes[2, 0] = -3.5
    batch_offsets = {"species_1": 0.0, "species_2": 0.35, "species_3": -0.25}
    embedding = np.vstack(
        [prototypes[np.flatnonzero(class_names == label)[0]] for label in labels]
    )
    embedding += np.array([[batch_offsets[batch], 0.0] + [0.0] * (n_features - 2) for batch in batches])
    embedding += rng.normal(0.0, 0.35, size=(n_cells, n_features))
    prediction = np.array(
        [class_names[np.argmin(np.sum((prototypes - row) ** 2, axis=1))] for row in embedding]
    )
    return embedding, labels, batches, prediction


def run_smoke_test(outdir: Path, seed: int = 7, n_cells: int = 120, n_features: int = 12) -> dict[str, str]:
    outdir.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    embedding, labels, batches, prediction = _synthetic_case(seed, n_cells, n_features)
    metrics = {
        "label_transfer": evaluate_labels(labels, prediction),
        "embedding": evaluate_embedding(embedding, labels, batches),
    }
    metrics["runtime_seconds"] = round(time.perf_counter() - started, 6)
    metrics_path = outdir / "synthetic_metrics.json"
    manifest_path = outdir / "run_manifest.json"
    metrics_path.write_text(json.dumps(metrics, ensure_ascii=True, indent=2), encoding="utf-8")
    manifest = {
        "mode": "synthetic_evaluator",
        "seed": seed,
        "n_cells": n_cells,
        "n_features": n_features,
        "python": platform.python_version(),
        "metric_caveat": "kBET is a chi-square neighborhood proxy until the official implementation is installed.",
        "real_tools_executed": [],
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=True, indent=2), encoding="utf-8")
    return {"metrics_path": str(metrics_path), "manifest_path": str(manifest_path)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", type=Path, default=Path("smoke-output"))
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--n-cells", type=int, default=120)
    parser.add_argument("--n-features", type=int, default=12)
    args = parser.parse_args()
    print(json.dumps(run_smoke_test(args.outdir, args.seed, args.n_cells, args.n_features), ensure_ascii=True))


if __name__ == "__main__":
    main()
