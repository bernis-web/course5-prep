#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cross-phylum arm: Lamprey vs Mouse brain.

Input (produced by the R export step):
    <DATA_DIR>/counts.bin   float32, row-major (cell x gene),
                            8-byte header: n_cells(uint32) + n_genes(uint32), little-endian
    <DATA_DIR>/genes.txt    one gene symbol per line
    <DATA_DIR>/obs.csv      cell_id,species,celltype

Design (agreed with GenPilot, 2026-10-22):
  * Evaluation space = the 13 Lamprey classes (a proper subset of Mouse's classes).
    Mouse cells outside those 13 are ALREADY excluded by the export step.
  * Gene axis = genes with min_cells>=3 in BOTH species (expected ~6,222).
  * Only the coarse level is evaluated: the object carries a single annotation set,
    so exact/fine have no cross-phylum counterpart.
  * Two arms, same KNN protocol as the in-domain comparison:
      - oPCA: per-direction joint PCA-50
      - scVI : joint training over both species, batch_key="species", n_latent=10
  * Transductive / in-sample, seed 0, K=15 cosine distance-weighted, 200 permutations.

Outputs: metrics.json, predictions/*.json, manifest.json, environment.txt, sha256.tsv
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import platform
import sys
import time
from pathlib import Path

import numpy as np

PROTOCOL = "transductive_formal_reassessment"
SEED = 0
K = 15
NPERM = 200
N_LATENT = 10
MAX_EPOCHS = 50
N_PCS = 50

SPECIES = ("Lamprey", "Mouse")


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def die(msg, code=2):
    print(f"HARDSTOP|{msg}", flush=True)
    sys.exit(code)


def load_subset(data_dir: Path):
    counts = data_dir / "counts.bin"
    genes_f = data_dir / "genes.txt"
    obs_f = data_dir / "obs.csv"
    for p in (counts, genes_f, obs_f):
        if not p.is_file():
            die(f"PREFLIGHT_FAIL missing {p}")

    with open(counts, "rb") as fh:
        head = fh.read(8)
        n_cells, n_genes = np.frombuffer(head, dtype="<u4")
        n_cells, n_genes = int(n_cells), int(n_genes)
        expected = n_cells * n_genes * 4
        fh.seek(0, os.SEEK_END)
        actual = fh.tell() - 8
        if actual != expected:
            die(f"BAD_BIN expected {expected} bytes, got {actual}")
        fh.seek(8)
        X = np.fromfile(fh, dtype="<f4", count=n_cells * n_genes)
    X = X.reshape(n_cells, n_genes)

    genes = [l.strip() for l in open(genes_f, encoding="utf-8") if l.strip()]
    if len(genes) != n_genes:
        die(f"GENE_COUNT_MISMATCH {len(genes)} vs {n_genes}")

    import csv

    obs_species, obs_type = [], []
    with open(obs_f, encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            obs_species.append(row["species"])
            obs_type.append(row["celltype"])
    if len(obs_species) != n_cells:
        die(f"OBS_COUNT_MISMATCH {len(obs_species)} vs {n_cells}")

    print(f"loaded X={X.shape} genes={len(genes)}", flush=True)
    sp = np.array(obs_species)
    ct = np.array(obs_type)
    for s in SPECIES:
        print(f"  {s}: {int((sp == s).sum())} cells", flush=True)
    print(f"  classes: {len(set(ct))}", flush=True)
    return X, genes, sp, ct


def normalize_log1p(X: np.ndarray) -> np.ndarray:
    """normalize_total(target_sum=1e4) + log1p, row-wise, in place-safe."""
    totals = X.sum(axis=1, keepdims=True, dtype=np.float64)
    totals[totals == 0] = 1.0
    X = (X.astype(np.float32) / totals.astype(np.float32)) * 1e4
    np.log1p(X, out=X)
    return X


def macro_f1(y_true, y_pred, union=True):
    if union:
        labels = sorted(set(y_true) | set(y_pred))
    else:
        labels = sorted(set(y_true))
    f1s = []
    for lab in labels:
        tp = sum(1 for t, p in zip(y_true, y_pred) if t == lab and p == lab)
        fp = sum(1 for t, p in zip(y_true, y_pred) if t != lab and p == lab)
        fn = sum(1 for t, p in zip(y_true, y_pred) if t == lab and p != lab)
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec = tp / (tp + fn) if (tp + fn) else 0.0
        f1s.append(2 * prec * rec / (prec + rec) if (prec + rec) else 0.0)
    return float(np.mean(f1s)) if f1s else 0.0


def evaluate(Z, sp, ct, src, tgt, out_dir, level="coarse"):
    from sklearn.neighbors import KNeighborsClassifier

    m_s = sp == src
    m_t = sp == tgt
    ytr = ct[m_s]
    yte = ct[m_t]
    knn = KNeighborsClassifier(n_neighbors=K, metric="cosine", weights="distance")
    knn.fit(Z[m_s], ytr)
    pred = knn.predict(Z[m_t])
    proba = knn.predict_proba(Z[m_t])
    cls = list(knn.classes_)

    acc = float((pred == yte).mean())
    mf1 = macro_f1(list(yte), list(pred), union=True)
    vals, cnts = np.unique(yte, return_counts=True)
    maj = float(cnts.max() / cnts.sum()) if cnts.sum() else 0.0

    rng = np.random.RandomState(SEED)
    nulls = []
    for _ in range(NPERM):
        pp = pred.copy()
        rng.shuffle(pp)
        nulls.append(float((pp == yte).mean()))
    pval = float((np.array(nulls) >= acc).mean())

    conf = {}
    for t, p in zip(yte, pred):
        k = f"{t}=>{p}"
        conf[k] = conf.get(k, 0) + 1

    rows = []
    for j in range(len(pred)):
        c = str(pred[j])
        rows.append({
            "cell_index": int(j),
            "direction": f"{src}->{tgt}",
            "level": level,
            "truth": str(yte[j]),
            "prediction": c,
            "confidence": round(float(proba[j][cls.index(c)]), 4),
        })
    (out_dir / "predictions" / f"{level}_{src}_to_{tgt}.json").write_text(
        json.dumps(rows, ensure_ascii=False), encoding="utf-8")

    res = {
        "acc": round(acc, 4),
        "macro_f1": round(mf1, 4),
        "macro_f1_truth_only": round(macro_f1(list(yte), list(pred), union=False), 4),
        "majority": round(maj, 4),
        "shuffle_p": round(pval, 4),
        "n_ref": int(m_s.sum()),
        "n_q": int(m_t.sum()),
        "n_perm": NPERM,
        "n_classes_truth": int(len(vals)),
        "confusion": conf,
    }
    print(f"{src}->{tgt} done acc={acc:.4f} macroF1={mf1:.4f}", flush=True)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="directory with counts.bin / genes.txt / obs.csv")
    ap.add_argument("--out", required=True)
    ap.add_argument("--arms", default="opca,scvi")
    args = ap.parse_args()

    t0 = time.time()
    data_dir = Path(args.data)
    out = Path(args.out)
    if out.exists():
        die(f"OUT_EXISTS {out}", 3)
    out.mkdir(parents=True, exist_ok=False)
    (out / "predictions").mkdir()

    X, genes, sp, ct = load_subset(data_dir)
    X = normalize_log1p(X)

    arms = [a.strip() for a in args.arms.split(",") if a.strip()]
    metrics = {}
    manifest_extra = {}

    # ---------- oPCA arm ----------
    if "opca" in arms:
        from sklearn.decomposition import PCA

        Z = PCA(n_components=N_PCS, svd_solver="randomized", random_state=SEED).fit_transform(X)
        print(f"oPCA latent {Z.shape}", flush=True)
        res = {}
        for src, tgt in (("Lamprey", "Mouse"), ("Mouse", "Lamprey")):
            res[f"{src}->{tgt}"] = {"coarse": evaluate(Z, sp, ct, src, tgt, out)}
        metrics["opca"] = res
        manifest_extra["opca"] = {"n_pcs": N_PCS}
        del Z

    # ---------- scVI arm ----------
    if "scvi" in arms:
        import anndata as ad
        import scvi
        import torch

        torch.set_num_threads(min(2, os.cpu_count() or 1))
        scvi.settings.seed = SEED
        adata = ad.AnnData(X.copy())
        adata.obs["species"] = sp
        adata.obs["celltype"] = ct
        scvi.model.SCVI.setup_anndata(adata, batch_key="species")
        model = scvi.model.SCVI(adata, n_latent=N_LATENT)
        model.train(max_epochs=MAX_EPOCHS, early_stopping=True, enable_progress_bar=False)
        Z = model.get_latent_representation()
        print(f"scVI latent {Z.shape}", flush=True)
        res = {}
        for src, tgt in (("Lamprey", "Mouse"), ("Mouse", "Lamprey")):
            res[f"{src}->{tgt}"] = {"coarse": evaluate(Z, sp, ct, src, tgt, out)}
        metrics["scvi"] = res
        manifest_extra["scvi"] = {"n_latent": N_LATENT, "max_epochs": MAX_EPOCHS,
                                  "scvi_version": getattr(scvi, "__version__", "unknown")}

    (out / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=1), encoding="utf-8")

    try:
        import anndata as ad2
        import scanpy as sc2
        env = {"python": platform.python_version(), "platform": platform.platform(),
               "numpy": np.__version__, "anndata": ad2.__version__, "scanpy": sc2.__version__}
    except Exception:
        env = {"python": platform.python_version(), "platform": platform.platform(),
               "numpy": np.__version__}
    env["params"] = {"seed": SEED, "k": K, "nperm": NPERM, "protocol": PROTOCOL}
    env.update(manifest_extra)
    (out / "environment.txt").write_text(json.dumps(env, indent=1), encoding="utf-8")

    outputs = {}
    for p in sorted(out.rglob("*")):
        if p.is_file() and p.name != "sha256.tsv":
            outputs[str(p.relative_to(out)).replace(os.sep, "/")] = sha256_file(p)
    manifest = {
        "protocol": PROTOCOL,
        "method": "cross_phylum_lamprey_mouse",
        "variant": "13-class intersection, min_cells>=3 common genes, coarse only",
        "params": {"seed": SEED, "k": K, "nperm": NPERM, "n_pcs": N_PCS,
                   "n_latent": N_LATENT, "max_epochs": MAX_EPOCHS},
        "n_cells": int(len(ct)),
        "n_genes": int(len(genes)),
        "species_counts": {s: int((sp == s).sum()) for s in SPECIES},
        "n_classes": int(len(set(ct))),
        "script_sha256": sha256_file(__file__),
        "output_sha256": outputs,
        "started": _dt.datetime.utcfromtimestamp(t0).isoformat() + "Z",
        "elapsed_sec": round(time.time() - t0, 1),
    }
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    with open(out / "sha256.tsv", "w", encoding="utf-8", newline="\n") as fh:
        for p in sorted(out.rglob("*")):
            if p.is_file() and p.name != "sha256.tsv":
                fh.write(f"{sha256_file(p)}  {str(p.relative_to(out)).replace(os.sep, '/')}\n")

    print(f"DONE elapsed={manifest['elapsed_sec']}s out={out}", flush=True)


if __name__ == "__main__":
    main()
