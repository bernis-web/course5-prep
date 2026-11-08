"""算清「把 zebrafish|Orthers 从 neural 改成 unmapped」的后果（修正口径下）。

当前冻结口径：zebrafish|Orthers -> neural (active)
候选改法  ：zebrafish|Orthers -> other (unmapped)

影响两条：
  1) 真值侧：斑马鱼 30 个 Orthers 细胞退出评估 → 斑马鱼做真值的方向分母 -30
  2) 预测侧：zebrafish->human / zebrafish->mouse 两向里，被判成 Orthers 的 865 / 100 个预测
     原本映射到 neural（可判对），改后变成不可映射 → 全部记错

输出：results/bootstrap-20261030/orthers_variant_impact.json
"""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(r"D:\projects\course5-prep")
MAP = ROOT / "config" / "heart-celltype-map-v1.tsv"
CONF = ROOT / "results" / "pilot-v1" / "saturn-v99" / "raw" / "recovered-20261001" / "confusion"
OUT = ROOT / "results" / "bootstrap-20261030" / "orthers_variant_impact.json"

SRC = {
    "human->mouse": ("human", "mouse"),
    "mouse->human": ("mouse", "human"),
    "human->zebrafish": ("human", "zebrafish"),
    "zebrafish->human": ("zebrafish", "human"),
    "mouse->zebrafish": ("mouse", "zebrafish"),
    "zebrafish->mouse": ("zebrafish", "mouse"),
}


def load(override_orhters: bool):
    m = {}
    with open(MAP, encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            key = (row["source_species"].strip(), row["source_label"].strip())
            coarse, status = row["coarse_level"].strip(), row["mapping_status"].strip()
            if override_orhters and key == ("zebrafish", "Orthers"):
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
    return (sum(fs) / len(fs) if fs else 0.0), len(t), len(labels)


def run(m):
    res = {}
    for dr, (src, tgt) in SRC.items():
        conf = json.loads((CONF / f"coarse_{src}_to_{tgt}.json").read_text(encoding="utf-8"))
        t, p = [], []
        dropped = Counter()
        for k, n in conf.items():
            tr, pr = k.split("=>")
            ct = co(tgt, tr, m)          # 真值 → 目标物种词表
            cp = co(src, pr, m)          # 预测 → 源物种词表
            if ct is None:
                continue
            if cp is None:
                dropped[pr] += n
                cp = "<unmapped>"
            t.extend([ct] * n)
            p.extend([cp] * n)
        mf1, n, k = macro_f1(t, p)
        acc = sum(a == b for a, b in zip(t, p)) / n if n else 0.0
        res[dr] = {"mf1": round(mf1, 4), "acc": round(acc, 4), "n_q": n,
                   "n_classes": k, "dropped": sum(dropped.values()),
                   "dropped_labels": dict(dropped)}
    return res


a = run(load(False))
b = run(load(True))

print(f'{"方向":<18}{"现行 mf1":<10}{"改后 mf1":<10}{"Δ":<9}{"n_q 现":<8}{"n_q 后":<8}{"新丢预测"}')
for dr in SRC:
    d = round(b[dr]["mf1"] - a[dr]["mf1"], 4)
    print(f'{dr:<18}{a[dr]["mf1"]:<10}{b[dr]["mf1"]:<10}{d:<+9}{a[dr]["n_q"]:<8}{b[dr]["n_q"]:<8}{b[dr]["dropped"]}')

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps({"current": a, "orhters_unmapped": b}, indent=1, ensure_ascii=False),
               encoding="utf-8")
print("\nwrote", OUT)
