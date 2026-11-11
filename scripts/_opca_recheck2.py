# -*- coding: utf-8 -*-
"""复核：oPCA v2 六向 macro-F1（union），用 rerun-v2/confusion 的 "真值=>预测" 稀疏计数重算。"""
import json, glob, os
import numpy as np

BASE = r"D:\projects\course5-prep\results\mapping-v2-20261111\rerun-v2\confusion"
CT = json.load(open(r"D:\projects\course5-prep\results\current-20261111\current-table.json", encoding="utf-8"))
rows = CT["rows"] if isinstance(CT, dict) else CT
want = {r["direction"]: r["value"] for r in rows if r["method"] == "oPCA" and r["metric"] == "macro_f1"}
want_acc = {r["direction"]: r["value"] for r in rows if r["method"] == "oPCA" and r["metric"] == "accuracy"}

def load(p):
    d = json.load(open(p, encoding="utf-8"))
    cells = {}
    for k, n in d.items():
        t, p_ = k.split("=>")
        cells[(t, p_)] = cells.get((t, p_), 0) + n
    labels = sorted({t for t, _ in cells} | {p for _, p in cells})
    idx = {l: i for i, l in enumerate(labels)}
    cm = np.zeros((len(labels), len(labels)))
    for (t, p_), n in cells.items():
        cm[idx[t], idx[p_]] += n
    return cm, labels

def macro_f1_union(cm):
    t = cm.sum(axis=1); p = cm.sum(axis=0); out = []
    for k in range(cm.shape[0]):
        tp = cm[k, k]
        den = 2 * tp + (p[k] - tp) + (t[k] - tp)
        out.append(0.0 if den == 0 else 2 * tp / den)
    return float(np.mean(out)), float(np.trace(cm) / cm.sum())

print(f"{'file':46s} {'mf1':>8s} {'ct':>8s} {'Δ':>8s} {'acc':>8s} {'ct_acc':>8s}")
for f in sorted(glob.glob(os.path.join(BASE, "coarse_*.json"))):
    name = os.path.basename(f).replace("coarse_", "").replace(".json", "")
    src, tgt = name.split("_to_")
    dkey = f"{src}->{tgt}"
    cm, labels = load(f)
    mf1, acc = macro_f1_union(cm)
    ctv = want.get(dkey); ctacc = want_acc.get(dkey)
    dv = (mf1 - ctv) if ctv is not None else float("nan")
    print(f"{dkey:46s} {mf1:8.4f} {str(ctv):>8s} {dv:+8.4f} {acc:8.4f} {str(ctacc):>8s}")