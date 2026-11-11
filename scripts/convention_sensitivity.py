"""评测口径敏感性表：同一批预测，在多种口径下结论会不会变

Claude 咨询（`_claude/20261111-1248-*.md` §1.4）列了六种要重算的口径。本脚本做其中能本地做的四种：

  1. **union vs truth-only** macro-F1
     - union：标签集 = 真实 ∪ 预测，预测里多出的类 F1 记 0（我们一贯用的）
     - truth-only：标签集 = 只有真实标签，多预测的类不进分母（平台默认之一）
  2. **accuracy / macro-F1 / balanced accuracy** 三个指标分列
  3. **含 / 不含物种特有类**（如 `erythroid` 基本只在斑马鱼有）
  4. **strict-cell vs drop-unmapped**（SATURN 用已有的两份产物；oPCA/scVI 用 included 子集）

数据源：
  oPCA   results/mapping-v2-20261111/rerun-v2/metrics.json（confusion 现算，v2 映射）
  SATURN results/bootstrap-20261030/saturn_convention_mapv2.json（published vs strict_cell）

输出：results/convention-20261111/convention_sensitivity.{json,md}
"""
from __future__ import annotations

import io
import json
import sys
from collections import Counter
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(r"D:\projects\course5-prep")
OPCA = ROOT / "results" / "mapping-v2-20261111" / "rerun-v2" / "metrics.json"
SATURN = ROOT / "results" / "bootstrap-20261030" / "saturn_convention_mapv2.json"
OUTDIR = ROOT / "results" / "convention-20261111"
DIRCN = {"human->mouse": "人→鼠", "mouse->human": "鼠→人",
         "human->zebrafish": "人→斑马鱼", "zebrafish->human": "斑马鱼→人",
         "mouse->zebrafish": "鼠→斑马鱼", "zebrafish->mouse": "斑马鱼→鼠"}
# 物种特有类：erythroid 基本只见于斑马鱼
SP_ONLY = {"erythroid"}


def conf_to_pairs(conf: dict):
    t, p = [], []
    for key, n in conf.items():
        a, b = key.split("=>")
        t.extend([a] * n)
        p.extend([b] * n)
    return t, p


def acc(t, p):
    return sum(a == b for a, b in zip(t, p)) / len(t) if t else None


def macro_f1(t, p, union: bool):
    tc, pc, tpc = Counter(t), Counter(p), Counter()
    for a, b in zip(t, p):
        if a == b:
            tpc[a] += 1
    labels = (set(tc) | set(pc)) if union else set(tc)
    fs = []
    for c in labels:
        prec = tpc[c] / pc[c] if pc[c] else 0.0
        rec = tpc[c] / tc[c] if tc[c] else 0.0
        fs.append(2 * prec * rec / (prec + rec) if (prec + rec) else 0.0)
    return sum(fs) / len(fs) if fs else None


def balanced_acc(t, p):
    tc = Counter(t)
    per = []
    for c in tc:
        idx = [i for i, a in enumerate(t) if a == c]
        per.append(sum(p[i] == c for i in idx) / len(idx))
    return sum(per) / len(per) if per else None


def main() -> int:
    m = json.loads(OPCA.read_text(encoding="utf-8"))
    sat = json.loads(SATURN.read_text(encoding="utf-8"))
    res = {"date": "2026-11-11",
           "purpose": "同一批预测在多种评测口径下的数值与结论差异",
           "opca_source": "results/mapping-v2-20261111/rerun-v2/metrics.json",
           "saturn_source": "results/bootstrap-20261030/saturn_convention_mapv2.json",
           "directions": {}}

    lines = ["# 评测口径敏感性表", "",
             "> 同一批预测、同一个粗类标签空间，只换评测口径。",
             "> **看这张表的意义**：如果换口径就换结论，那结论必须带口径限定语。", "",
             "## 一、oPCA（v2 映射，逐细胞混淆矩阵现算）", "",
             "| 方向 | n | accuracy | mf1(union) | mf1(truth-only) | balanced acc | 含物种特有类 | 剔除物种特有类后 mf1(union) |",
             "|---|---|---|---|---|---|---|---|"]

    for dr, cn in DIRCN.items():
        d = m.get(dr, {}).get("coarse")
        if not d or not d.get("confusion"):
            continue
        t, p = conf_to_pairs(d["confusion"])
        # 剔除物种特有类
        keep = [(a, b) for a, b in zip(t, p) if a not in SP_ONLY]
        t2, p2 = [a for a, _ in keep], [b for _, b in keep]
        rec = {
            "n": len(t),
            "accuracy": round(acc(t, p), 4),
            "macro_f1_union": round(macro_f1(t, p, True), 4),
            "macro_f1_truth_only": round(macro_f1(t, p, False), 4),
            "balanced_accuracy": round(balanced_acc(t, p), 4),
            "n_without_species_specific": len(t2),
            "macro_f1_union_without_species_specific": round(macro_f1(t2, p2, True), 4) if t2 else None,
        }
        rec["delta_union_minus_truthonly"] = round(rec["macro_f1_union"] - rec["macro_f1_truth_only"], 4)
        res["directions"][dr] = rec
        lines.append(f"| {cn} | {rec['n']} | {rec['accuracy']} | {rec['macro_f1_union']} | "
                     f"{rec['macro_f1_truth_only']} | {rec['balanced_accuracy']} | "
                     f"{rec['n_without_species_specific']} | {rec['macro_f1_union_without_species_specific']} |")
        print(f"{cn:7s} n={rec['n']:5d} acc={rec['accuracy']:.4f} "
              f"mf1_union={rec['macro_f1_union']:.4f} mf1_truthonly={rec['macro_f1_truth_only']:.4f} "
              f"Δ={rec['delta_union_minus_truthonly']:+.4f} balacc={rec['balanced_accuracy']:.4f}", flush=True)

    lines += ["", "## 二、SATURN（published vs strict_cell）", "",
              "| 方向 | published mf1 | strict_cell mf1 | 被抬高 |", "|---|---|---|---|"]
    for dr, cn in DIRCN.items():
        s = sat.get("directions", {}).get(dr, {})
        pub, st = s.get("published", {}), s.get("strict_cell", {})
        if pub.get("mf1") is None or st.get("mf1") is None:
            continue
        lines.append(f"| {cn} | {pub['mf1']} | {st['mf1']} | {round(pub['mf1'] - st['mf1'], 4):+} |")
        res.setdefault("saturn", {})[dr] = {"published_mf1": pub["mf1"], "strict_cell_mf1": st["mf1"],
                                            "inflation": round(pub["mf1"] - st["mf1"], 4)}

    # 结论：哪些口径差异大到能改变排序
    deltas = [v["delta_union_minus_truthonly"] for v in res["directions"].values()]
    bal_gaps = {DIRCN[d]: round(v["accuracy"] - v["balanced_accuracy"], 4)
                for d, v in res["directions"].items()}
    worst = max(bal_gaps, key=lambda k: abs(bal_gaps[k]))
    lines += ["", "## 三、口径差异有多大（oPCA）", "",
              f"- union 与 truth-only 的 macro-F1 差：范围 **{min(deltas):+.4f} ~ {max(deltas):+.4f}**",
              "- 差值**全部 ≤ 0** → **union 口径系统性低于或等于 truth-only**",
              "  （因为预测里多出的类在 union 下被记为 F1=0，而 truth-only 不看这些类）",
              "- 跨论文比较时**必须说明用的是哪种**；原文多为 truth-only 或类似口径，",
              "  拿我们的 union 值直接比会显得偏低。",
              "",
              "## 四、accuracy 与 balanced accuracy 的差距（类别不平衡的贡献）", "",
              "| 方向 | accuracy | balanced acc | 差 |", "|---|---|---|---|"]
    for d, v in res["directions"].items():
        lines.append(f"| {DIRCN[d]} | {v['accuracy']} | {v['balanced_accuracy']} | "
                     f"{round(v['accuracy'] - v['balanced_accuracy'], 4):+} |")
    lines += ["",
              f"- 最大差距出现在 **{worst}**（{bal_gaps[worst]:+.4f}）→ "
              "该方向的 accuracy 明显受益于类别不平衡，**不能只用 accuracy 报**。"]

    OUTDIR.mkdir(parents=True, exist_ok=True)
    (OUTDIR / "convention_sensitivity.json").write_text(
        json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    (OUTDIR / "convention_sensitivity.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nunion - truth-only 差值范围: {min(deltas):+.4f} .. {max(deltas):+.4f}")
    print("wrote", OUTDIR / "convention_sensitivity.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
