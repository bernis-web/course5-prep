"""SATURN 修正口径下的 bootstrap 区间（2026-11-09）

背景：`scripts/bootstrap_ci.py` 的 `pairs_saturn()` 把真值按**源物种**词表查、
预测按**目标物种**词表查（方向颠倒，与 report-09 定位的同一个 bug）。
本脚本用**正确方向**重建逐细胞对，并支持切换 mapping（v1 / v2 签认版），
给出 macro-F1 ± bootstrap SE ± 95% CI。

协议与原脚本一致：query 细胞重抽样 1000 次，RandomState(20261030)，
union 口径（真实 ∪ 预测 一起平均），不可映射预测按错误计（strict_cell）。

用法：
    python scripts/bootstrap_saturn_fixed.py                    # v1 映射
    MAP_TSV=config/heart-celltype-map-v2.tsv python scripts/bootstrap_saturn_fixed.py

输出：results/bootstrap-20261030/saturn_bootstrap_fixed.json
"""
from __future__ import annotations

import csv
import json
import os
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "bootstrap-20261030"
MAP_TSV = Path(os.environ.get("MAP_TSV", str(ROOT / "config" / "heart-celltype-map-v1.tsv")))
OUT_JSON = OUT / (os.environ["OUT_NAME"] if os.environ.get("OUT_NAME") else "saturn_bootstrap_fixed.json")
CONF = ROOT / "results" / "pilot-v1" / "saturn-v99" / "raw" / "recovered-20261001" / "confusion"

NB = 1000
SEED = 20261030

SRC = {
    "human->mouse": ("human", "mouse"),
    "mouse->human": ("mouse", "human"),
    "human->zebrafish": ("human", "zebrafish"),
    "zebrafish->human": ("zebrafish", "human"),
    "mouse->zebrafish": ("mouse", "zebrafish"),
    "zebrafish->mouse": ("zebrafish", "mouse"),
}


def load_mapping():
    m = {}
    with open(MAP_TSV, encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            m[(row["source_species"].strip(), row["source_label"].strip())] = (
                row["coarse_level"].strip(), row["mapping_status"].strip())
    return m


def to_coarse(sp, lab, mapping):
    hit = mapping.get((sp, str(lab).strip()))
    if not hit:
        return None
    c, st = hit
    return c if (st == "active" and c) else None


def macro_f1_union(truth, pred):
    t, p, tp = Counter(), Counter(), Counter()
    for a, b in zip(truth, pred):
        t[a] += 1
        p[b] += 1
        if a == b:
            tp[a] += 1
    labels = set(t) | set(p)
    fs = []
    for c in labels:
        pr = tp[c] / p[c] if p[c] else 0.0
        rc = tp[c] / t[c] if t[c] else 0.0
        fs.append(2 * pr * rc / (pr + rc) if (pr + rc) else 0.0)
    return sum(fs) / len(fs) if fs else 0.0


def boot(truth, pred, nb=NB, seed=SEED):
    rng = np.random.RandomState(seed)
    n = len(truth)
    ta = np.array(truth, dtype=object)
    pa = np.array(pred, dtype=object)
    vals = []
    for _ in range(nb):
        idx = rng.randint(0, n, n)
        vals.append(macro_f1_union(ta[idx], pa[idx]))
    vals = np.array(vals)
    return {
        "n_q": n,
        "acc": round(float((ta == pa).mean()), 4),
        "mf1": round(macro_f1_union(truth, pred), 4),
        "mf1_se": round(float(vals.std(ddof=1)), 4),
        "mf1_ci95": [round(float(np.percentile(vals, 2.5)), 4),
                     round(float(np.percentile(vals, 97.5)), 4)],
    }


def main() -> int:
    mapping = load_mapping()
    try:
        _map_label = str(MAP_TSV.resolve().relative_to(ROOT.resolve())).replace("\\", "/")
    except ValueError:      # MAP_TSV 在沙箱/外部目录，或本身是相对路径
        _map_label = MAP_TSV.name
    res = {
        "method": "saturn_v99",
        "protocol": f"bootstrap over query cells, {NB} resamples, RandomState({SEED})",
        "label_space": "coarse / union, 不可映射预测按错误计 (strict_cell)",
        "mapping": _map_label,
        "orientation_fix": "truth -> 目标物种词表; pred -> 源物种词表（修正 bootstrap_ci.py 的对调）",
        "directions": {},
    }
    print(f"mapping = {res['mapping']}")
    print(f'{"direction":<18}{"n_q":>6}{"acc":>9}{"mf1":>9}{"±SE":>9}{"95% CI":>20}')
    for dr, (src, tgt) in SRC.items():
        conf = json.loads((CONF / f"coarse_{src}_to_{tgt}.json").read_text(encoding="utf-8"))
        truth, pred = [], []
        for k, v in conf.items():
            tr, pr = k.split("=>")
            ct = to_coarse(tgt, tr, mapping)     # 真值 → 目标物种
            if ct is None:
                continue
            cp = to_coarse(src, pr, mapping)     # 预测 → 源物种
            if cp is None:
                cp = "<unmapped>"
            truth.extend([ct] * v)
            pred.extend([cp] * v)
        r = boot(truth, pred)
        res["directions"][dr] = r
        print(f'{dr:<18}{r["n_q"]:>6}{r["acc"]:>9.4f}{r["mf1"]:>9.4f}'
              f'{r["mf1_se"]:>9.4f}   [{r["mf1_ci95"][0]:.4f}, {r["mf1_ci95"][1]:.4f}]')

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    print("\nwrote", OUT_JSON)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
