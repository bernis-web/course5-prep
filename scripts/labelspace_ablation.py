"""标签空间粒度消融：exact / fine / coarse 三层下的方法表现

为什么做：
    `report-12` §1.2 的老师口径、Claude 咨询的第 4 条「评测协议」都指出——
    我们只在 coarse（9 粗类）上报数，而**原文多在 fine / 细胞类型级评估**，
    口径不可直接比。这张表把三层放在一起，量化「粒度」对分数与结论的影响。

数据源（v2 映射、本地重跑产物，非重映射）：
    results/mapping-v2-20261111/rerun-v2/metrics.json
    其中每个方向都有 exact / coarse / fine 三层的 acc / majority / n_ref / n_q / confusion

口径：
    - macro-F1 用 union 口径（真实 ∪ 预测，多预测的类 F1=0），从 confusion 现算；
    - 三层各自的 n_q 不同（层级越细，可映射的细胞越少）——**必须连 n_q 一起报**。

输出：results/labelspace-20261111/labelspace_ablation.{json,md}
"""
from __future__ import annotations

import io
import json
import sys
from collections import Counter
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(r"D:\projects\course5-prep")
SRC = ROOT / "results" / "mapping-v2-20261111" / "rerun-v2" / "metrics.json"
OUTDIR = ROOT / "results" / "labelspace-20261111"
DIRCN = {"human->mouse": "人→鼠", "mouse->human": "鼠→人",
         "human->zebrafish": "人→斑马鱼", "zebrafish->human": "斑马鱼→人",
         "mouse->zebrafish": "鼠→斑马鱼", "zebrafish->mouse": "斑马鱼→鼠"}
LEVELS = ["exact", "fine", "coarse"]


def mf1_union(conf: dict) -> float:
    t, p, tp = Counter(), Counter(), Counter()
    for key, n in conf.items():
        a, b = key.split("=>")
        t[a] += n
        p[b] += n
        if a == b:
            tp[a] += n
    fs = []
    for c in set(t) | set(p):
        prec = tp[c] / p[c] if p[c] else 0.0
        rec = tp[c] / t[c] if t[c] else 0.0
        fs.append(2 * prec * rec / (prec + rec) if (prec + rec) else 0.0)
    return sum(fs) / len(fs) if fs else 0.0


def main() -> int:
    m = json.loads(SRC.read_text(encoding="utf-8"))
    res = {
        "date": "2026-11-11",
        "purpose": "标签空间粒度对分数与结论的影响（exact/fine/coarse 三层）",
        "source": "results/mapping-v2-20261111/rerun-v2/metrics.json",
        "method": "oPCA（FIXKEY），v2 映射，strict_cell 口径",
        "convention": {"macro_f1": "union（真实∪预测，多预测类 F1=0）",
                       "note": "层级越细，可映射细胞越少 → 必须连 n_q 一起看"},
        "directions": {},
    }
    lines = ["# 标签空间粒度消融（oPCA，v2 映射）", "",
             "> 三层各自的 `n_q` 不同（层级越细，能映射到该层标签空间的细胞越少），**必须连 n_q 一起读**。", "",
             "| 方向 | 层 | accuracy | macro-F1(union) | n_q | 多数类基线 | 相对多数类 |",
             "|---|---|---|---|---|---|---|"]

    for dr, cn in DIRCN.items():
        if dr not in m:
            continue
        row = {}
        for lvl in LEVELS:
            d = m[dr].get(lvl)
            if not d:
                continue
            acc = d.get("acc")
            nq = d.get("n_q")
            maj = d.get("majority")
            f1 = round(mf1_union(d.get("confusion", {})), 4) if d.get("confusion") else None
            rel = ("高于多数类" if (acc is not None and maj is not None and acc > maj)
                   else ("低于多数类" if (acc is not None and maj is not None) else "—"))
            row[lvl] = {"accuracy": acc, "macro_f1_union": f1, "n_q": nq,
                        "majority": maj, "vs_majority": rel}
            lines.append(f"| {cn} | {lvl} | {acc} | {f1} | {nq} | {maj} | {rel} |")
            print(f"{cn:7s} {lvl:7s} acc={acc} mf1={f1} n_q={nq} maj={maj} {rel}", flush=True)
        res["directions"][dr] = row
        lines.append("")

    # 一句话结论：粒度变化会不会改变「是否高于多数类」
    flips = []
    for dr, row in res["directions"].items():
        vals = {lvl: row[lvl]["vs_majority"] for lvl in row}
        if len(set(vals.values())) > 1:
            flips.append({"direction": DIRCN[dr], "by_level": vals})
    res["granularity_changes_verdict"] = flips

    lines += ["## 粒度是否改变「高于/低于多数类基线」的判断", ""]
    if flips:
        for f in flips:
            lines.append(f"- **{f['direction']}**：{f['by_level']}")
    else:
        lines.append("六方向全部一致，粒度没有改变该判断。")
    lines.append("")

    OUTDIR.mkdir(parents=True, exist_ok=True)
    (OUTDIR / "labelspace_ablation.json").write_text(
        json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    (OUTDIR / "labelspace_ablation.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n粒度改变判断的方向数:", len(flips))
    print("wrote", OUTDIR / "labelspace_ablation.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
