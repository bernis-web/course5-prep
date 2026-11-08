"""Paired bootstrap for SATURN vs scVI under BOTH conventions.

published : SATURN cells whose prediction falls outside the coarse space are dropped
strict_cell: those cells are kept and counted as wrong (fair vs oPCA/scVI, which
             can never predict outside their training label set)

Output: results/bootstrap-20261030/saturn_vs_scvi.json
"""
import csv
import gzip
import json
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "bootstrap-20261030" / "saturn_vs_scvi.json"
MAP_TSV = ROOT / "config" / "heart-celltype-map-v1.tsv"
SATURN_PAYLOAD = ROOT / "results" / "pilot-v1" / "saturn-v99" / "raw" / "recovered-20261001" / "payloads"
SCVI_PRED = ROOT / "results" / "phase-20261019" / "scvi-cross-species" / "predictions"
NB = 2000
RNG = np.random.RandomState(20261030)

SRC = {"human->mouse": ("human", "mouse"), "mouse->human": ("mouse", "human"),
       "human->zebrafish": ("human", "zebrafish"), "zebrafish->human": ("zebrafish", "human"),
       "mouse->zebrafish": ("mouse", "zebrafish"), "zebrafish->mouse": ("zebrafish", "mouse")}
SAT = {"human->mouse": "p6_coarse_human_to_mouse", "mouse->human": "p1_coarse_mouse_to_human",
       "human->zebrafish": "p3_coarse_human_to_zebrafish", "zebrafish->human": "p2_coarse_zebrafish_to_human",
       "mouse->zebrafish": "p5_coarse_mouse_to_zebrafish", "zebrafish->mouse": "p4_coarse_zebrafish_to_mouse"}
SCV = {"human->mouse": "coarse_hu_to_mo", "mouse->human": "coarse_mo_to_hu",
       "human->zebrafish": "coarse_hu_to_zf", "zebrafish->human": "coarse_zf_to_hu",
       "mouse->zebrafish": "coarse_mo_to_zf", "zebrafish->mouse": "coarse_zf_to_mo"}
TARGET = ["mouse->zebrafish", "zebrafish->mouse", "zebrafish->human", "human->zebrafish"]


def load_mapping():
    m = {}
    for row in csv.DictReader(open(MAP_TSV, encoding="utf-8-sig", newline=""), delimiter="\t"):
        m[(row["source_species"].strip(), row["source_label"].strip())] = (
            row["coarse_level"].strip(), row["mapping_status"].strip())
    return m


def to_coarse(sp, lab, mapping):
    h = mapping.get((sp, str(lab).strip()))
    if not h:
        return None
    c, s = h
    return c if (s == "active" and c) else None


def mf1(truth, pred):
    t, p, tp = Counter(), Counter(), Counter()
    for a, b in zip(truth, pred):
        t[a] += 1
        p[b] += 1
        if a == b:
            tp[a] += 1
    fs = []
    for c in set(t) | set(p):
        pr = tp[c] / p[c] if p[c] else 0.0
        rc = tp[c] / t[c] if t[c] else 0.0
        fs.append(2 * pr * rc / (pr + rc) if (pr + rc) else 0.0)
    return sum(fs) / len(fs) if fs else 0.0


def load_sat(dr, mapping):
    s, t = SRC[dr]
    rows = json.loads(gzip.open(SATURN_PAYLOAD / (SAT[dr] + ".json.json.gz"), "rb").read().decode("utf-8"))
    out = {}
    for r in rows:
        if r[3] != 1:
            continue
        ct, cp = to_coarse(s, r[1], mapping), to_coarse(t, r[2], mapping)
        if ct:
            out[r[0]] = (ct, cp if cp else "<not_in_coarse>")
    return out


def load_scv(dr, mapping):
    s, t = SRC[dr]
    out = {}
    for r in json.loads((SCVI_PRED / (SCV[dr] + ".json")).read_text(encoding="utf-8")):
        if not r.get("included", True):
            continue
        if r["truth"] in ("unmapped", "") or r["prediction"] in ("unmapped", ""):
            continue
        out[r["prefixed_barcode"]] = (r["truth"], r["prediction"])
    return out


def main():
    mapping = load_mapping()
    res = {"protocol": f"paired bootstrap over shared query cells, {NB} resamples",
           "conventions": {
               "published": "SATURN cells with out-of-coarse predictions dropped",
               "strict_cell": "those cells kept, counted wrong (fair against oPCA/scVI)"},
           "comparisons": {}}
    for dr in TARGET:
        sa = load_sat(dr, mapping)
        sc = load_scv(dr, mapping)
        shared = [bc for bc in sa if bc in sc]
        out = {"n_shared": len(shared)}
        for conv in ("published", "strict_cell"):
            if conv == "published":
                cells = [bc for bc in shared if sa[bc][1] != "<not_in_coarse>"]
            else:
                cells = shared
            truth = [sa[bc][0] for bc in cells]
            ps_ = [sa[bc][1] for bc in cells]
            pc_ = [sc[bc][1] for bc in cells]
            n = len(cells)
            d0 = mf1(truth, ps_) - mf1(truth, pc_)
            deltas = []
            for _ in range(NB):
                idx = RNG.randint(0, n, n)
                t = [truth[i] for i in idx]
                a = [ps_[i] for i in idx]
                b = [pc_[i] for i in idx]
                deltas.append(mf1(t, a) - mf1(t, b))
            lo, hi = float(np.percentile(deltas, 2.5)), float(np.percentile(deltas, 97.5))
            se = float(np.std(deltas, ddof=1))
            out[conv] = {
                "n": n,
                "saturn_mf1": round(mf1(truth, ps_), 4),
                "scvi_mf1": round(mf1(truth, pc_), 4),
                "delta": round(d0, 4), "delta_se": round(se, 4),
                "delta_ci95": [round(lo, 4), round(hi, 4)],
                "significant_at_95": bool((lo > 0) or (hi < 0)),
            }
            print(f"{dr:16s} [{conv:11s}] n={n:5d} SATURN={out[conv]['saturn_mf1']:.4f} "
                  f"scVI={out[conv]['scvi_mf1']:.4f} Δ={d0:+.4f} CI[{lo:+.4f},{hi:+.4f}] "
                  f"{'SIG' if out[conv]['significant_at_95'] else 'ns'}", flush=True)
        res["comparisons"][dr] = out
    OUT.write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    print("\nwrote", OUT)


if __name__ == "__main__":
    main()
