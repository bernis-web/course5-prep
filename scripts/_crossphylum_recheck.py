# -*- coding: utf-8 -*-
"""复核跨门 macro_f1_union：从混淆矩阵按 union 口径重算。"""
import json
import numpy as np

p = r"D:\projects\course5-prep\results\phase-20261022\crossphylum\metrics.json"
d = json.load(open(p, encoding="utf-8"))

def macro_f1_union(cm):
    cm = np.array(cm, dtype=float)
    truth_labels = cm.sum(axis=1)          # 行 = 真值
    pred_labels = cm.sum(axis=0)           # 列 = 预测
    n = len(truth_labels)
    f1s = []
    for k in range(n):
        tp = cm[k, k]
        fp = pred_labels[k] - tp
        fn = truth_labels[k] - tp
        denom = 2 * tp + fp + fn
        f1s.append(0.0 if denom == 0 else 2 * tp / denom)
    return float(np.mean(f1s))

for method in ("opca", "scvi"):
    for dkey, ckey in (("Lamprey->Mouse", "Lamprey=>Mouse"), ("Mouse->Lamprey", "Mouse=>Lamprey")):
        info = d[method]["directions"][dkey]
        cm = d[method]["confusion_matrices"][ckey]
        rows = list(cm.keys())
        mat = [[cm[r].get(c, 0) for c in rows] for r in rows]
        acc = np.trace(np.array(mat)) / np.array(mat).sum()
        print(f"{method:5s} {dkey:16s} stored_mf1={info['macro_f1_union']:.4f} "
              f"recomputed_mf1={macro_f1_union(mat):.4f} stored_acc={info['acc']:.4f} recomputed_acc={acc:.4f}")