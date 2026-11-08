"""Compute batch-mixing metrics (silhouette / iLISI / kBET) for a joint embedding.

Metric definitions are fixed to reproduce the values reported for the oPCA and
scVI arms in docs/reports/batch-mixing-and-crossphylum-feasibility-20261019.md
(§7.1):
  - silhouette: sklearn silhouette_score, metric="cosine", on mapped coarse labels
    (all cells that have a coarse mapping in config/heart-celltype-map-v1.tsv)
  - iLISI: inverse Simpson index of species composition over the k=30 nearest
    neighbours (self excluded), averaged over cells
  - kBET: per-cell chi-square test of local vs global species composition,
    k=30 (self excluded), acceptance rate at alpha=0.05

The same code applied to the scVI latent (4,606 x 10) reproduces
silhouette 0.181 / iLISI 1.120 (reported 1.125) / kBET 0.0039.

Usage:
  python scripts/compute_batch_metrics.py --embedding X.npy --obs obs.json \
      --out metrics.json [--mapping config/heart-celltype-map-v1.tsv]

obs.json accepts either
  [{"obs_name":..., "species":"human|mouse|zebrafish", "label":"..."}, ...]
or {"obs_names":[...], "species":[...], "labels":[...]}.
Rows must be in the same order as the embedding.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np
from scipy.stats import chi2_contingency
from sklearn.metrics import silhouette_score
from sklearn.neighbors import NearestNeighbors

SPECIES = ("human", "mouse", "zebrafish")
K = 30
ALPHA = 0.05


def load_obs(path: Path) -> tuple[list[str], np.ndarray, np.ndarray]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        names = [str(x) for x in raw["obs_names"]]
        species = np.array([str(x) for x in raw["species"]], dtype=object)
        labels = np.array([str(x) for x in raw["labels"]], dtype=object)
    else:
        names = [str(r["obs_name"]) for r in raw]
        species = np.array([str(r["species"]) for r in raw], dtype=object)
        labels = np.array([str(r["label"]) for r in raw], dtype=object)
    return names, species, labels


def load_mapping(path: Path) -> dict[tuple[str, str], tuple[str, str]]:
    out: dict[tuple[str, str], tuple[str, str]] = {}
    with open(path, encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            out[(row["source_species"].strip(), row["source_label"].strip())] = (
                row["coarse_level"].strip(),
                row["mapping_status"].strip(),
            )
    return out


def inv_simpson(counts: np.ndarray) -> float:
    total = counts.sum()
    if total <= 0:
        return float("nan")
    p = counts / total
    return float(1.0 / np.sum(p * p))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--embedding", required=True)
    ap.add_argument("--obs", required=True)
    ap.add_argument("--mapping", default="config/heart-celltype-map-v1.tsv")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    emb = np.load(args.embedding)
    if emb.ndim != 2:
        raise SystemExit(f"embedding must be 2-D, got {emb.shape}")
    names, species, labels = load_obs(Path(args.obs))
    if emb.shape[0] != len(names):
        raise SystemExit(f"row mismatch: embedding {emb.shape[0]} vs obs {len(names)}")
    uniq_sp = sorted(set(species))
    if sorted(SPECIES) != uniq_sp:
        raise SystemExit(f"unexpected species set: {uniq_sp}")

    mapping = load_mapping(Path(args.mapping))
    coarse = np.array(
        [mapping.get((s, l), (None, None))[0] for s, l in zip(species, labels)],
        dtype=object,
    )
    status = np.array(
        [mapping.get((s, l), (None, None))[1] for s, l in zip(species, labels)],
        dtype=object,
    )
    mapped = coarse != None  # noqa: E711 - object array elementwise
    n_mapped = int(mapped.sum())
    sil = float(silhouette_score(emb[mapped], coarse[mapped], metric="cosine"))

    nn = NearestNeighbors(n_neighbors=K + 1).fit(emb)
    idx = nn.kneighbors(emb, return_distance=False)[:, 1:]  # self excluded

    species_counts = np.array(
        [[(species[row] == s).sum() for s in SPECIES] for row in idx], dtype=float
    )
    ilisi = float(np.mean([inv_simpson(c) for c in species_counts]))

    global_freq = np.array([(species == s).mean() for s in SPECIES])
    global_counts = np.maximum((global_freq * len(species)).astype(int), 1)
    accepted = 0
    for counts in species_counts:
        try:
            _, p, _, _ = chi2_contingency(np.vstack([counts.astype(int), global_counts]))
        except ValueError:
            p = 1.0
        accepted += int(p > ALPHA)
    kbet = float(accepted / len(species_counts))

    result = {
        "embedding": str(args.embedding),
        "n_cells": int(emb.shape[0]),
        "dim": int(emb.shape[1]),
        "n_mapped_coarse": n_mapped,
        "n_coarse_classes": int(len(set(coarse[mapped]))),
        "silhouette_cosine_coarse": round(sil, 6),
        "ilisi_species_k30": round(ilisi, 6),
        "kbet_accept_k30_alpha005": round(kbet, 6),
        "k": K,
        "alpha": ALPHA,
        "species_counts": {s: int((species == s).sum()) for s in SPECIES},
        "mapping_status_counts": {
            str(k): int((status == k).sum()) for k in sorted(set(status), key=str)
        },
    }
    Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
