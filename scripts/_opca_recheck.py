# -*- coding: utf-8 -*-
"""复核 oPCA v2 六向 macro-F1（union 口径）：用 rerun-v2 混淆矩阵现算，与 current-table 对账。"""
import json, glob, os
import numpy as np

base = r"D:\projects\course5-prep\results\mapping-v2-20261111\rerun-v2"
files = sorted(glob.glob(os.path.join(base, "**", "*.json"), recursive=True))
print("json files in rerun-v2:", len(files))
for f in files[:20]:
    print("   ", os.path.relpath(f, base))

def macro_f1_union(cm):
    cm = np.array(cm, dtype=float)
    t = cm.sum(axis=1); p = cm.sum(axis=0); out = []
    for k in range(len(t)):
        tp = cm[k, k]
        d = 2 * tp + (p[k] - tp) + (t[k] - tp)
        out.append(0.0 if d == 0 else 2 * tp / d)
    return float(np.mean(out)), float(np.trace(cm) / cm.sum())

ct = json.load(open(r"D:\projects\course5-prep\results\current-20261111\current-table.json", encoding="utf-8"))
rows = ct["rows"] if isinstance(ct, dict) else ct
want = {(r["direction"], r["metric"]): r["value"] for r in rows if r["method"] == "oPCA"}

for f in files:
    try:
        d = json.load(open(f, encoding="utf-8"))
    except Exception:
        continue
    if not isinstance(d, dict):
        continue
    for k, v in d.items():
        if not isinstance(v, dict) or "confusion" not in json.dumps(v)[:2000].lower():
            pass
    # 尝试识别混淆矩阵结构
    for k, v in d.items():
        if isinstance(v, dict) and "labels" in v and "matrix" in v:
            mf1, acc = macro_f1_union(v["matrix"])
            print(f"{os.path.relpath(f, base)}::{k}  mf1={mf1:.4f} acc={acc:.4f} "
                  f"| current-table mf1={want.get((k,'macro_f1'))}")