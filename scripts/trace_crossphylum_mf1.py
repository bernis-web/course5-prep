# -*- coding: utf-8 -*-
"""跨门 metrics.json 的 macro_f1_union 溯源：用混淆矩阵反推它到底是哪个口径算出来的。

候选：
  V1 13 类并集 · macro · zero_division=0
  V2 仅真值出现过的类 · macro · zero_division=0
  V3 仅预测出现过的类 · macro · zero_division=0
  V4 两法交集类 · macro · zero_division=0
  V5 micro
  V6 weighted
  V7 13 类并集 · macro · zero_division=1
"""
import json
from pathlib import Path

import numpy as np
from sklearn.metrics import f1_score

M = json.load(open(r"D:\projects\course5-prep\results\phase-20261022\crossphylum\metrics.json",
                   encoding="utf-8"))


def to_arrays(cm: dict):
    labels = sorted(cm)
    y_true, y_pred = [], []
    for t in labels:
        row = cm[t]
        for p, n in row.items():
            if n:
                y_true.extend([t] * n)
                y_pred.extend([p] * n)
    return np.array(y_true), np.array(y_pred), labels


def variants(y_true, y_pred, labels):
    present_true = sorted(set(y_true))
    present_pred = sorted(set(y_pred))
    inter = sorted(set(present_true) & set(present_pred))
    out = {}
    out["V1 13类并集"] = f1_score(y_true, y_pred, labels=labels, average="macro", zero_division=0)
    out["V2 真值现过的类"] = f1_score(y_true, y_pred, labels=present_true, average="macro", zero_division=0)
    out["V3 预测现过的类"] = f1_score(y_true, y_pred, labels=present_pred, average="macro", zero_division=0)
    out["V4 交集类"] = f1_score(y_true, y_pred, labels=inter, average="macro", zero_division=0)
    out["V5 micro"] = f1_score(y_true, y_pred, average="micro", zero_division=0)
    out["V6 weighted"] = f1_score(y_true, y_pred, average="weighted", zero_division=0)
    out["V7 并集 zd=1"] = f1_score(y_true, y_pred, labels=labels, average="macro", zero_division=1)
    out["V8 交集 zd=1"] = f1_score(y_true, y_pred, labels=inter, average="macro", zero_division=1)
    return out, len(present_true), len(present_pred), len(inter)


for meth in ("opca", "scvi"):
    print(f"===== {meth} =====")
    cms = M[meth]["confusion_matrices"]
    dirs = M[meth]["directions"]
    for key, cm in cms.items():
        y_true, y_pred, labels = to_arrays(cm)
        vs, nt, npd, ni = variants(y_true, y_pred, labels)
        d = dirs.get(key.replace("=>", "->")) or dirs.get(key) or {}
        stored = d.get("macro_f1_union")
        acc = d.get("acc")
        print(f"-- {key}  n={len(y_true)}  类数: 并集{len(labels)} 真值{nt} 预测{npd} 交集{ni}"
              f"  存值 mf1_union={stored:.4f} acc={acc:.4f}")
        for k, v in vs.items():
            mark = " ★命中" if stored is not None and abs(v - stored) < 5e-5 else ""
            print(f"     {k:14} = {v:.4f}{mark}")