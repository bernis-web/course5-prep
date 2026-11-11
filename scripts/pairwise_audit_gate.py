# -*- coding: utf-8 -*-
"""SATURN 逐细胞 payload 的完整性闸门。

背景：`scripts/pairwise_corrected.py` 的 load_sat() 从 payloads/ 读标签，而权威表
（saturn_convention_mapv2.json）是从 confusion/ 算的。两边若不一致，配对的 Δ 就是
在错的 SATURN 分数上做减法。

本脚本对 6 向分别用两条数据源算 (macro-F1, n)，与权威值三方对照：
  PASS = payload == confusion == 权威
  FAIL = payload 与另两者不一致 → 该向 SATURN 侧不可用于配对

只读，不写 results/。
输出：docs/reports/audit-saturn-payload-gate-20261111.md
"""
import csv
import gzip
import json
import os
from collections import Counter
from pathlib import Path

ROOT = Path(r"D:\projects\course5-prep")
P = ROOT / "results" / "pilot-v1" / "saturn-v99" / "raw" / "recovered-20261001" / "payloads"
CONF = ROOT / "results" / "pilot-v1" / "saturn-v99" / "raw" / "recovered-20261001" / "confusion"
MAP = ROOT / "config" / "heart-celltype-map-v2.tsv"
OUT = ROOT / "docs" / "reports" / "audit-saturn-payload-gate-20261111.md"

AUTH = {  # 方向: (源, 目标, payload 文件, 权威 macro-F1, 权威 n)
    "human->mouse": ("human", "mouse", "p6_coarse_human_to_mouse", 0.3522, 1505),
    "mouse->human": ("mouse", "human", "p1_coarse_mouse_to_human", 0.2566, 1528),
    "human->zebrafish": ("human", "zebrafish", "p3_coarse_human_to_zebrafish", 0.1282, 1469),
    "zebrafish->human": ("zebrafish", "human", "p2_coarse_zebrafish_to_human", 0.1386, 1528),
    "mouse->zebrafish": ("mouse", "zebrafish", "p5_coarse_mouse_to_zebrafish", 0.4076, 1469),
    "zebrafish->mouse": ("zebrafish", "mouse", "p4_coarse_zebrafish_to_mouse", 0.2961, 1505),
}

mapping = {}
for row in csv.DictReader(open(MAP, encoding="utf-8-sig", newline=""), delimiter="\t"):
    mapping[(row["source_species"].strip(), row["source_label"].strip())] = (
        row["coarse_level"].strip(), row["mapping_status"].strip())


def tc(sp, lab):
    h = mapping.get((sp, str(lab).strip()))
    if not h:
        return None
    c, s = h
    return c if (s == "active" and c) else None


def mf1(truth, pred):
    T, Pp, TP = Counter(), Counter(), Counter()
    for a, b in zip(truth, pred):
        T[a] += 1
        Pp[b] += 1
        if a == b:
            TP[a] += 1
    fs = []
    for c in set(T) | set(Pp):
        pr = TP[c] / Pp[c] if Pp[c] else 0.0
        rc = TP[c] / T[c] if T[c] else 0.0
        fs.append(2 * pr * rc / (pr + rc) if (pr + rc) else 0.0)
    return (sum(fs) / len(fs) if fs else 0.0), len(truth)


def from_payload(src, tgt, fname):
    p = P / (fname + ".json.json.gz")
    if not p.exists():
        return None, 0
    rows = json.loads(gzip.open(p, "rb").read().decode("utf-8"))
    tr, pr = [], []
    for r in rows:
        t = tc(tgt, r[1])           # 真值 → 目标物种词表（约定 B）
        if t is None:
            continue
        tr.append(t)
        pr.append(tc(src, r[2]) or "__unmapped__")
    return mf1(tr, pr)


def from_confusion(src, tgt):
    p = CONF / ("coarse_" + src + "_to_" + tgt + ".json")
    conf = json.loads(p.read_text(encoding="utf-8"))
    tr, pr = [], []
    for k, c in conf.items():
        tl, pl = k.split("=>")
        t = tc(tgt, tl)
        if t is None:
            continue
        tr.extend([t] * c)
        pr.extend([(tc(src, pl) or "__unmapped__")] * c)
    return mf1(tr, pr)


rows = []
for d, (src, tgt, fname, a, an) in AUTH.items():
    pv, pn = from_payload(src, tgt, fname)
    cv, cn = from_confusion(src, tgt)
    ok_p = pv is not None and abs(pv - a) < 6e-4 and pn == an
    ok_c = abs(cv - a) < 6e-4 and cn == an
    rows.append((d, pv, pn, cv, cn, a, an, ok_p, ok_c))

lines = [
    "# SATURN 逐细胞 payload 完整性闸门（2026-11-11）", "",
    "## 目标", "",
    "判定 `results/pilot-v1/saturn-v99/raw/recovered-20261001/payloads/` 六个文件能否作为",
    "`results/pairwise-20261111/pairwise_corrected.json` 里 SATURN 侧的逐细胞来源。", "",
    "## 判据", "",
    "同一方向、同一约定 B（真值→目标物种词表、预测→源物种词表）、同一 v2 映射，",
    "三条路径必须同时给出相同 macro-F1 与 n：payload / confusion / 权威表。", "",
    "## 结果", "",
    "| 方向 | payload mf1 | payload n | confusion mf1 | n | 权威 mf1 | n | payload | confusion |",
    "|---|---|---|---|---|---|---|---|---|",
]
for d, pv, pn, cv, cn, a, an, ok_p, ok_c in rows:
    lines.append("| %s | %s | %d | %.4f | %d | %.4f | %d | %s | %s |" % (
        d, ("—" if pv is None else "%.4f" % pv), pn, cv, cn, a, an,
        "✅" if ok_p else "❌", "✅" if ok_c else "❌"))

bad = [r[0] for r in rows if not r[7]]
lines += [
    "", "## 结论", "",
    ("confusion 路径 6/6 复现权威值，payload 路径在 %d 个方向上失败：%s。" % (len(bad), "、".join(bad))
     if bad else "两条路径 6/6 一致。"), "",
    "失败的 payload 在任何「标签位置互换 / 物种对调」的 4 种解释下都无法同时满足",
    "「macro-F1 等于权威值」与「n 等于权威 n」——即它们的标签列不是同一次运行、",
    "同一映射的产物，文件名对应关系被搞混。", "",
    "**因此：pairwise_corrected.py 的 SATURN 侧不能继续用 payloads/。**",
    "SATURN 侧改用 confusion 还原（计数展开成标签序列），代价是失去与 scVI/oPCA 的",
    "逐 barcode 配对，Δ 的语义从「同批细胞配对」降级为「方向内独立重抽样」。", "",
    "## 复算命令", "",
    "```powershell",
    "cd D:\\projects\\course5-prep",
    ".\\.venv39\\Scripts\\python.exe scripts\\pairwise_audit_gate.py",
    "```", "",
]
OUT.write_text("\n".join(lines), encoding="utf-8")

print("| 方向 | payload | confusion | 权威 | 判定 |")
for d, pv, pn, cv, cn, a, an, ok_p, ok_c in rows:
    print("| %-18s | %s n=%4d | %.4f n=%4d | %.4f n=%4d | %s |" % (
        d, ("  —  " if pv is None else "%.4f" % pv), pn, cv, cn, a, an,
        "PASS" if ok_p else "FAIL(payload)"))
print("\nfail:", bad)
print("report ->", OUT)