"""Paired bootstrap over the SAME query cells: is method A really better than B?

Why paired: all four methods are scored on the same query cells, so resampling
cells (not methods) preserves the correlation between methods and gives a much
tighter -- and correct -- interval for the DIFFERENCE.  An unpaired comparison of
two 95% CIs would be needlessly conservative.

Output: results/bootstrap-20261030/pairwise.json
"""
import csv
import json
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "bootstrap-20261030"
NB = 2000
RNG = np.random.RandomState(20261030)

import sys
sys.path.insert(0, str(ROOT / "scripts"))
from bootstrap_ci import (DIRS, LOADERS, load_mapping, macro_f1_union)  # noqa: E402

PAIRS = [
    ("human->mouse", "ortholog_pca", "scVI"),
    ("mouse->human", "ortholog_pca", "scVI"),
    ("human->zebrafish", "scVI", "saturn_v99"),
    ("zebrafish->human", "scVI", "saturn_v99"),
    ("mouse->zebrafish", "saturn_v99", "scVI"),
    ("zebrafish->mouse", "saturn_v99", "scVI"),
    ("human->mouse", "scVI", "saturn_v99"),
    ("human->zebrafish", "scVI", "ortholog_pca"),
    ("mouse->zebrafish", "saturn_v99", "ortholog_pca"),
    ("zebrafish->mouse", "saturn_v99", "ortholog_pca"),
    ("human->mouse", "ortholog_pca", "saturn_v99"),
    ("human->zebrafish", "saturn_v99", "ortholog_pca"),
    ("zebrafish->human", "saturn_v99", "ortholog_pca"),
]


def aligned(dr, a, b, mapping):
    """Keep only query cells scored by BOTH methods, in the same order."""
    pa = dict()
    for t, p in LOADERS[a](dr, mapping):
        pa.setdefault((t, p), 0)
    # need per-cell identity -> rebuild from barcodes
    return None


def load_cells(method, dr, mapping):
    """barcode -> (truth, pred) in coarse space."""
    import gzip
    SRC = {"human->mouse": ("human", "mouse"), "mouse->human": ("mouse", "human"),
           "human->zebrafish": ("human", "zebrafish"), "zebrafish->human": ("zebrafish", "human"),
           "mouse->zebrafish": ("mouse", "zebrafish"), "zebrafish->mouse": ("zebrafish", "mouse")}
    from bootstrap_ci import SCVI_TAG, SAMAP_TAG, to_coarse
    src, tgt = SRC[dr]
    out = {}
    if method == "ortholog_pca":
        f = ROOT / "results/stability-20261030/runs/seed-0/predictions" / f"coarse_{dr.replace('->','_to_')}.json"
        for r in json.loads(f.read_text(encoding="utf-8")):
            if r["included"]:
                out[r["prefixed_barcode"]] = (r["truth"], r["prediction"])
    elif method == "scVI":
        f = ROOT / "results/phase-20261019/scvi-cross-species/predictions" / (SCVI_TAG[dr] + ".json")
        for r in json.loads(f.read_text(encoding="utf-8")):
            if r.get("included", True) and r["truth"] not in ("unmapped", "") and r["prediction"] not in ("unmapped", ""):
                out[r["prefixed_barcode"]] = (r["truth"], r["prediction"])
    elif method == "saturn_v99":
        from bootstrap_ci import SATURN_TAG
        f = ROOT / "results/pilot-v1/saturn-v99/raw/recovered-20261001/payloads" / (SATURN_TAG[dr] + ".json.json.gz")
        for r in json.loads(gzip.open(f, "rb").read().decode("utf-8")):
            if r[3] != 1:
                continue
            t = to_coarse(src, r[1], mapping)
            p = to_coarse(tgt, r[2], mapping)
            if t and p:
                out[r[0]] = (t, p)
    return out


def main():
    mapping = load_mapping()
    res = {"protocol": f"paired bootstrap over shared query cells, {NB} resamples, RandomState(20261030)",
           "statistic": "delta macro-F1 (union), A - B", "comparisons": []}
    cache = {}
    for dr, a, b in PAIRS:
        key = (dr, a), (dr, b)
        for m in (a, b):
            if (dr, m) not in cache:
                cache[(dr, m)] = load_cells(m, dr, mapping)
        ca, cb = cache[(dr, a)], cache[(dr, b)]
        shared = [bc for bc in ca if bc in cb]
        if len(shared) < 100:
            res["comparisons"].append({"direction": dr, "A": a, "B": b,
                                       "status": "too_few_shared_cells", "n_shared": len(shared)})
            print(f"{dr:18s} {a} vs {b}: only {len(shared)} shared cells -- cannot pair", flush=True)
            continue
        ta = [ca[bc][0] for bc in shared]
        pa = [ca[bc][1] for bc in shared]
        pb = [cb[bc][1] for bc in shared]
        d0 = macro_f1_union(ta, pa) - macro_f1_union(ta, pb)
        deltas = []
        n = len(shared)
        for _ in range(NB):
            idx = RNG.randint(0, n, n)
            t = [ta[i] for i in idx]
            p1 = [pa[i] for i in idx]
            p2 = [pb[i] for i in idx]
            deltas.append(macro_f1_union(t, p1) - macro_f1_union(t, p2))
        lo, hi = float(np.percentile(deltas, 2.5)), float(np.percentile(deltas, 97.5))
        se = float(np.std(deltas, ddof=1))
        sig = (lo > 0) or (hi < 0)
        rec = {"direction": dr, "A": a, "B": b, "n_shared": n,
               "mf1_A": round(macro_f1_union(ta, pa), 4),
               "mf1_B": round(macro_f1_union(ta, pb), 4),
               "delta": round(d0, 4), "delta_se": round(se, 4),
               "delta_ci95": [round(lo, 4), round(hi, 4)],
               "significant_at_95": bool(sig),
               "n_over_se": round(abs(d0) / se, 2) if se else None}
        res["comparisons"].append(rec)
        print(f"{dr:18s} {a:13s} {rec['mf1_A']:.4f} vs {b:10s} {rec['mf1_B']:.4f}  "
              f"Δ={rec['delta']:+.4f} CI[{lo:+.4f},{hi:+.4f}] {'SIG' if sig else 'ns'} "
              f"({rec['n_over_se']}SE, n={n})", flush=True)
    (OUT / "pairwise.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    print("\nwrote", OUT / "pairwise.json", flush=True)


if __name__ == "__main__":
    main()
