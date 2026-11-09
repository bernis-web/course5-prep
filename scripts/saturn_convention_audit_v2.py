"""SATURN 评价口径审计 · 修正版（v2）

背景：scripts/saturn_convention_audit.py（v1）存在物种方向错误。

在 SATURN 的跨物种标签迁移里：
  - **真值（truth）** 用的是**目标物种**的词表（被预测的那一方，有注释）；
  - **预测（pred）** 用的是**源物种**的词表（参考书那一方，SATURN 输出的
    是源物种的原始细胞类型）。

证据（逐对求和，见 confusion 文件）：
  coarse_human_to_mouse.json
    真值侧 = Adipocyte/Cardiomyocyte/Epicardium/Valve …      → 小鼠词表
    预测侧 = Atrial|Ventricular Cardiomyocyte/Mast/Mesothelial → 人词表
  coarse_zebrafish_to_human.json
    真值侧 = Atrial|Ventricular Cardiomyocyte/Mast/Mesothelial → 人词表
    预测侧 = Orthers/Epicardium/Fibroblast …                 → 斑马鱼词表

而 v1 写的是：
    ct = to_coarse(s, tr, mapping)   # s = 源物种  ← 应为目标物种
    cp = to_coarse(t, pr, mapping)   # t = 目标物种 ← 应为源物种
两边正好颠倒，后果有两个：
  1) 真值标签在源物种词表里查不到时 → `continue`，**这些细胞在三种口径里
     都被静默丢掉**（所以 v1 的 n_strict 不是该方向的总细胞数）；
  2) 预测标签在目标物种词表里查不到时（如 `Orthers` 不在人词表）→ 被判成
     "不可映射"丢弃，人为制造出「SATURN 靠丢样本抬高分数」的现象。

本脚本用正确方向重算同一套三口径，输出到独立文件，不覆盖 v1 产物。

用法：
    python scripts/saturn_convention_audit_v2.py
输出：
    results/bootstrap-20261030/saturn_convention_v2.json
"""
from __future__ import annotations

import csv
import json
import os
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "bootstrap-20261030" / "saturn_convention_v2.json"
MAP_TSV = Path(os.environ.get("MAP_TSV", str(ROOT / "config" / "heart-celltype-map-v1.tsv")))
CONF = ROOT / "results" / "pilot-v1" / "saturn-v99" / "raw" / "recovered-20261001" / "confusion"

# 方向 -> (源物种=参考书, 目标物种=被预测)
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
                row["coarse_level"].strip(),
                row["mapping_status"].strip(),
            )
    return m


def to_coarse(sp, lab, mapping):
    """把某一物种的词表标签映射到粗类；不可映射返回 None。"""
    hit = mapping.get((sp, str(lab).strip()))
    if not hit:
        return None
    coarse, status = hit
    return coarse if (status == "active" and coarse) else None


def macro_f1(truth, pred, extra_classes=()):
    t, p, tp = Counter(), Counter(), Counter()
    for a, b in zip(truth, pred):
        t[a] += 1
        p[b] += 1
        if a == b:
            tp[a] += 1
    labels = set(t) | set(p) | set(extra_classes)
    fs = []
    for c in labels:
        pr = tp[c] / p[c] if p[c] else 0.0
        rc = tp[c] / t[c] if t[c] else 0.0
        fs.append(2 * pr * rc / (pr + rc) if (pr + rc) else 0.0)
    return sum(fs) / len(fs) if fs else 0.0


def main() -> int:
    mapping = load_mapping()
    res = {
        "question": "SATURN 的 union macro-F1 是否因丢弃不可映射预测而被抬高？（修正物种方向后重算）",
        "sources": str(CONF.relative_to(ROOT)).replace("\\", "/"),
        "mapping": str(MAP_TSV.relative_to(ROOT)).replace("\\", "/"),
        "supersedes": "saturn_convention.json (v1, 物种方向颠倒)",
        "directions": {},
    }

    for dr, (src, tgt) in SRC.items():
        conf = json.loads((CONF / f"coarse_{src}_to_{tgt}.json").read_text(encoding="utf-8"))
        pub_t, pub_p = [], []
        st_t, st_p = [], []
        cell_t, cell_p = [], []
        dropped = Counter()
        truth_unmapped = Counter()

        for key, n in conf.items():
            tr, pr = key.split("=>")
            # 真值 → 目标物种词表；预测 → 源物种词表
            ct = to_coarse(tgt, tr, mapping)
            cp = to_coarse(src, pr, mapping)
            if ct is None:
                truth_unmapped[tr] += n   # 真值所在类本来就不进评估（如 unmapped 类）
                continue
            if cp is not None:
                pub_t.extend([ct] * n)
                pub_p.extend([cp] * n)
                cell_t.extend([ct] * n)
                cell_p.extend([cp] * n)
            else:
                dropped[pr] += n
                cell_t.extend([ct] * n)
                cell_p.extend(["<not_in_coarse>"] * n)
            st_t.extend([ct] * n)
            st_p.extend([cp if cp else "<unmapped>"] * n)

        rec = {
            "n_published": len(pub_t),
            "n_strict": len(st_t),
            "n_dropped_unmappable": len(st_t) - len(pub_t),
            "n_truth_unmapped": sum(truth_unmapped.values()),
            "truth_unmapped_labels": dict(truth_unmapped),
            "dropped_labels": dict(dropped),
            "published": {
                "acc": round(sum(a == b for a, b in zip(pub_t, pub_p)) / len(pub_t), 4) if pub_t else None,
                "mf1": round(macro_f1(pub_t, pub_p), 4) if pub_t else None,
            },
            "strict_cell": {
                "acc": round(sum(a == b for a, b in zip(cell_t, cell_p)) / len(cell_t), 4) if cell_t else None,
                "mf1": round(macro_f1(cell_t, cell_p), 4) if cell_t else None,
            },
            "strict": {
                "acc": round(sum(a == b for a, b in zip(st_t, st_p)) / len(st_t), 4) if st_t else None,
                "mf1": round(macro_f1(st_t, st_p), 4) if st_t else None,
            },
        }
        if rec["published"]["mf1"] is not None and rec["strict_cell"]["mf1"] is not None:
            rec["mf1_inflation"] = round(rec["published"]["mf1"] - rec["strict_cell"]["mf1"], 4)
        else:
            rec["mf1_inflation"] = None
        res["directions"][dr] = rec
        print(
            f"{dr:18s} n_pub={len(pub_t):5d} n_strict={len(st_t):5d} "
            f"truth_unmapped={sum(truth_unmapped.values()):4d} "
            f"pub_mf1={rec['published']['mf1']} -> strict_mf1={rec['strict_cell']['mf1']} "
            f"(差 {rec['mf1_inflation']})",
            flush=True,
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    print("\nwrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
