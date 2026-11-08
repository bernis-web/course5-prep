"""三行候选改法的敏感性分析（修正口径下）。

对每一条候选改动，单独把该行从 active 改成 unmapped，重算六方向 macro-F1 与分母，
给出「改这一行会动多少」。这是签字包里「披露四项」的第④项：敏感性结果。

候选：
  R36 zebrafish|Orthers        -> other/unmapped
  R21 mouse|Valve              -> other/unmapped
  R30 zebrafish|Perivascular   -> other/unmapped

输出：results/bootstrap-20261030/mapping_v2_sensitivity.json
"""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(r"D:\projects\course5-prep")
MAP = ROOT / "config" / "heart-celltype-map-v1.tsv"
CONF = ROOT / "results" / "pilot-v1" / "saturn-v99" / "raw" / "recovered-20261001" / "confusion"
OUT = ROOT / "results" / "bootstrap-20261030" / "mapping_v2_sensitivity.json"

SRC = {
    "human->mouse": ("human", "mouse"),
    "mouse->human": ("mouse", "human"),
    "human->zebrafish": ("human", "zebrafish"),
    "zebrafish->human": ("zebrafish", "human"),
    "mouse->zebrafish": ("mouse", "zebrafish"),
    "zebrafish->mouse": ("zebrafish", "mouse"),
}

CANDIDATES = {
    "R36_zebrafish_Orthers": ("zebrafish", "Orthers"),
    "R21_mouse_Valve": ("mouse", "Valve"),
    "R30_zebrafish_Perivascular": ("zebrafish", "Perivascular cells"),
}


def load(mutate=None):
    m = {}
    with open(MAP, encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            key = (row["source_species"].strip(), row["source_label"].strip())
            coarse, status = row["coarse_level"].strip(), row["mapping_status"].strip()
            if mutate and key == mutate:
                coarse, status = "other", "unmapped"
            m[key] = (coarse, status)
    return m


def co(sp, lab, m):
    hit = m.get((sp, str(lab).strip()))
    if not hit:
        return None
    c, st = hit
    return c if (st == "active" and c) else None


def macro_f1(t, p):
    tt, pp, tp = Counter(), Counter(), Counter()
    for a, b in zip(t, p):
        tt[a] += 1
        pp[b] += 1
        if a == b:
            tp[a] += 1
    labels = set(tt) | set(pp)
    fs = []
    for c in labels:
        pr = tp[c] / pp[c] if pp[c] else 0.0
        rc = tp[c] / tt[c] if tt[c] else 0.0
        fs.append(2 * pr * rc / (pr + rc) if (pr + rc) else 0.0)
    return (sum(fs) / len(fs) if fs else 0.0), len(t)


def run(m):
    res = {}
    for dr, (src, tgt) in SRC.items():
        conf = json.loads((CONF / f"coarse_{src}_to_{tgt}.json").read_text(encoding="utf-8"))
        t, p, dropped = [], [], Counter()
        for k, n in conf.items():
            tr, pr = k.split("=>")
            ct, cp = co(tgt, tr, m), co(src, pr, m)
            if ct is None:
                continue
            if cp is None:
                dropped[pr] += n
                cp = "<unmapped>"
            t.extend([ct] * n)
            p.extend([cp] * n)
        mf1, n = macro_f1(t, p)
        res[dr] = {"mf1": round(mf1, 4), "n_q": n, "dropped": sum(dropped.values())}
    return res


base = run(load())
report = {"baseline": base, "candidates": {}}

print("基线 mf1:", {k: v["mf1"] for k, v in base.items()})
print()

for name, key in CANDIDATES.items():
    cur = run(load(key))
    deltas = {dr: round(cur[dr]["mf1"] - base[dr]["mf1"], 4) for dr in SRC}
    ndrop = {dr: cur[dr]["dropped"] - base[dr]["dropped"] for dr in SRC if cur[dr]["dropped"] != base[dr]["dropped"]}
    report["candidates"][name] = {"changed_row": key, "after": cur,
                                  "delta_mf1": deltas, "extra_dropped": ndrop}
    print(f"== {name}")
    for dr in SRC:
        if deltas[dr] or dr in ndrop:
            print(f"   {dr:<18} {base[dr]['mf1']:.4f} -> {cur[dr]['mf1']:.4f}  ({deltas[dr]:+.4f})"
                  f"  n_q {base[dr]['n_q']} -> {cur[dr]['n_q']}")
    print()

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")
print("wrote", OUT)
