"""Build perturbed copies of the three species .h5ad files for stability runs.

Two perturbation families, both applied to the INPUT (never to the scoring code):

  cells   subsample 90% of cells per species with RandomState(r), so the KNN
          reference/query sets and the accuracy denominator both shift
  genes   keep 90% of genes per species with RandomState(r), so the shared
          1:1 ortholog set and PCA basis shift

Output layout matches what the frozen script expects: OPCA_H5AD_DIR/<dir>/
local_<species>_s.h5ad
"""
import json
import sys
from pathlib import Path

import anndata as ad
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SPECIES = ["human", "mouse", "zebrafish"]
CELL_FRAC = 0.9
GENE_FRAC = 0.9


def main():
    kind = sys.argv[1]          # cells | genes
    rep = int(sys.argv[2])      # replicate index
    frac = CELL_FRAC if kind == "cells" else GENE_FRAC
    rng = np.random.RandomState(1000 + rep)
    outdir = ROOT / "tmp" / "stab-data" / f"{kind}-{rep}"
    outdir.mkdir(parents=True, exist_ok=True)
    report = {}
    for sp in SPECIES:
        src = ROOT / f"local_{sp}_s.h5ad"
        a = ad.read_h5ad(str(src))
        n_cells, n_genes = a.shape
        if kind == "cells":
            keep = np.sort(rng.choice(n_cells, size=int(n_cells * frac), replace=False))
            b = a[keep].copy()
        else:
            keep = np.sort(rng.choice(n_genes, size=int(n_genes * frac), replace=False))
            b = a[:, keep].copy()
        b.write_h5ad(str(outdir / f"local_{sp}_s.h5ad"))
        report[sp] = {"from": [int(n_cells), int(n_genes)], "to": [int(b.shape[0]), int(b.shape[1])]}
        print(f"{kind}-{rep} {sp}: {n_cells}x{n_genes} -> {b.shape[0]}x{b.shape[1]}", flush=True)
    (outdir / "_perturb.json").write_text(
        json.dumps({"kind": kind, "rep": rep, "frac": frac, "rng_seed": 1000 + rep,
                    "shapes": report}, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
