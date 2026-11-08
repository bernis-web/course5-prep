"""SATURN 评价口径审计：预测落在 coarse 空间之外的细胞被丢弃，是否抬高 SATURN？

问题：oPCA / scVI 的预测天然只落在训练用 coarse 类集合内，永远不可能"预测到
coarse 空间之外"；SATURN 的标签迁移输出的是原始细胞类型，落在 coarse 空间之外
的预测会被统一口径脚本直接丢弃。于是 SATURN 的分母只包含"预测恰好可映射"的
细胞 → 按预测结果筛样本，系统性抬高 SATURN。

本脚本给出三种口径：
  published  当前交接文档口径：丢掉不可映射预测（= 现有 0.4147 / 0.6500 等）
  strict     保留细胞，不可映射预测按错误计（FN），且把 "<unmapped>" 作为
             一个零精度类计入 union —— 最保守
  strict_cell保留细胞，不可映射预测按错误计，但不额外引入新类
             —— 推荐的公平口径
输出：results/bootstrap-20261030/saturn_convention.json
"""
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "bootstrap-20261030" / "saturn_convention.json"
MAP_TSV = ROOT / "config" / "heart-celltype-map-v1.tsv"
CONF = ROOT / "results" / "pilot-v1" / "saturn-v99" / "raw" / "recovered-20261001" / "confusion"
SRC = {"human->mouse": ("human", "mouse"), "mouse->human": ("mouse", "human"),
       "human->zebrafish": ("human", "zebrafish"), "zebrafish->human": ("zebrafish", "human"),
       "mouse->zebrafish": ("mouse", "zebrafish"), "zebrafish->mouse": ("zebrafish", "mouse")}


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


def main():
    mapping = load_mapping()
    res = {"question": "SATURN 的 union macro-F1 是否因丢弃不可映射预测而被抬高？",
           "sources": str(CONF.relative_to(ROOT)).replace("\\", "/"),
           "directions": {}}
    for dr, (s, t) in SRC.items():
        conf = json.loads((CONF / f"coarse_{s}_to_{t}.json").read_text(encoding="utf-8"))
        pub_t, pub_p = [], []
        st_t, st_p = [], []
        cell_t, cell_p = [], []
        dropped = Counter()
        for k, v in conf.items():
            tr, pr = k.split("=>")
            ct = to_coarse(s, tr, mapping)
            cp = to_coarse(t, pr, mapping)
            if ct is None:
                continue          # truth 不可映射：三种口径都丢（没有真值）
            if cp is not None:
                pub_t.extend([ct] * v); pub_p.extend([cp] * v)
                cell_t.extend([ct] * v); cell_p.extend([cp] * v)
            else:
                dropped[pr] += v
                cell_t.extend([ct] * v); cell_p.extend(["<not_in_coarse>"] * v)
            st_t.extend([ct] * v)
            st_p.extend([cp if cp else "<unmapped>"] * v)
        rec = {
            "n_published": len(pub_t), "n_strict": len(st_t),
            "n_dropped_unmappable": len(st_t) - len(pub_t),
            "dropped_labels": dict(dropped),
            "published": {
                "acc": round(sum(a == b for a, b in zip(pub_t, pub_p)) / len(pub_t), 4),
                "mf1": round(macro_f1(pub_t, pub_p), 4)},
            "strict_cell": {
                "acc": round(sum(a == b for a, b in zip(cell_t, cell_p)) / len(cell_t), 4),
                "mf1": round(macro_f1(cell_t, cell_p), 4)},
            "strict": {
                "acc": round(sum(a == b for a, b in zip(st_t, st_p)) / len(st_t), 4),
                "mf1": round(macro_f1(st_t, st_p), 4)},
        }
        rec["mf1_inflation"] = round(rec["published"]["mf1"] - rec["strict_cell"]["mf1"], 4)
        res["directions"][dr] = rec
        print(f"{dr:18s} n_pub={len(pub_t):5d} n_strict={len(st_t):5d} "
              f"published mf1={rec['published']['mf1']:.4f} -> strict_cell mf1={rec['strict_cell']['mf1']:.4f} "
              f"(抬高 {rec['mf1_inflation']:+.4f})", flush=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    print("\nwrote", OUT)


if __name__ == "__main__":
    main()
