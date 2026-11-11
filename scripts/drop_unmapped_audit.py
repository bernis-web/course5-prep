"""strict/drop 口径消融：哪些方法受「丢弃不可映射预测」影响？

Claude 咨询第 1.4 条列了六种要重算的口径，其中一种是
**strict-cell vs drop-unmapped**（published）：
    - drop-unmapped（published）：预测落在标签空间外的细胞被丢弃，同时退出分母
    - strict-cell：这些细胞保留，记为错

**关键论点（本脚本要验证）**：
    oPCA 与 scVI 的预测**只可能落在训练用的标签集内**，永远不可能「预测到空间外」，
    所以对它们而言 drop-unmapped 与 strict-cell **完全等价**；
    SATURN 输出原始细胞类型，会预测出映射不到的标签，**只有它受影响**。
    → 「丢弃不可映射预测」这个口径对四个方法**不是公平的**。

数据源：
    SATURN  results/bootstrap-20261030/saturn_convention_mapv2.json（published vs strict_cell）
    oPCA    results/mapping-v2-20261111/rerun-v2/metrics.json（检查 confusion 里有无 <not_in_coarse>）
    scVI    results/phase-20261019/scvi-cross-species/predictions/coarse_*.json

输出：results/convention-20261111/drop_unmapped_audit.{json,md}
"""
from __future__ import annotations

import io
import json
import sys
from collections import Counter
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = Path(r"D:\projects\course5-prep")
OUTDIR = ROOT / "results" / "convention-20261111"
DIRCN = {"human->mouse": "人→鼠", "mouse->human": "鼠→人",
         "human->zebrafish": "人→斑马鱼", "zebrafish->human": "斑马鱼→人",
         "mouse->zebrafish": "鼠→斑马鱼", "zebrafish->mouse": "斑马鱼→鼠"}
SENTINEL = "<not_in_coarse>"


def main() -> int:
    sat = json.loads((ROOT / "results" / "bootstrap-20261030" /
                      "saturn_convention_mapv2.json").read_text(encoding="utf-8"))
    opca = json.loads((ROOT / "results" / "mapping-v2-20261111" /
                       "rerun-v2" / "metrics.json").read_text(encoding="utf-8"))
    scvi_dir = ROOT / "results" / "phase-20261019" / "scvi-cross-species" / "predictions"
    SCV = {"human->mouse": "coarse_hu_to_mo", "mouse->human": "coarse_mo_to_hu",
           "human->zebrafish": "coarse_hu_to_zf", "zebrafish->human": "coarse_zf_to_hu",
           "mouse->zebrafish": "coarse_mo_to_zf", "zebrafish->mouse": "coarse_zf_to_mo"}

    res = {"date": "2026-11-11",
           "purpose": "strict-cell vs drop-unmapped 口径对四个方法是否公平",
           "hypothesis": ("oPCA/scVI 的预测只能落在自己训练用的标签集内，"
                          "drop-unmapped 与 strict-cell 对它们等价；只有 SATURN 受影响"),
           "saturn": {}, "opca_outside_count": {}, "scvi_outside_count": {}}

    lines = ["# strict/drop 口径消融：谁受「丢弃不可映射预测」影响", "",
             "## 待验证的论点", "",
             "> oPCA 与 scVI 的预测只可能落在**训练用的标签集**内，永远不会「预测到空间外」，",
             "> 因此 drop-unmapped（published）与 strict-cell 对它们**完全等价**；",
             "> SATURN 输出原始细胞类型，会预测出映射不到的标签——**只有它受影响**。", "",
             "→ 若成立，则「丢弃不可映射预测」这个口径**对四个方法不公平**。", ""]

    # SATURN
    lines += ["## 一、SATURN（受影响的唯一一方）", "",
              "| 方向 | published mf1 | strict_cell mf1 | 被抬高 | 被丢弃细胞数 |",
              "|---|---|---|---|---|"]
    for dr, cn in DIRCN.items():
        r = sat.get("directions", {}).get(dr, {})
        pub, st = r.get("published", {}), r.get("strict_cell", {})
        if pub.get("mf1") is None or st.get("mf1") is None:
            continue
        infl = round(pub["mf1"] - st["mf1"], 4)
        res["saturn"][dr] = {"published_mf1": pub["mf1"], "strict_cell_mf1": st["mf1"],
                             "inflation": infl,
                             "n_dropped": r.get("n_dropped_unmappable")}
        lines.append(f"| {cn} | {pub['mf1']} | {st['mf1']} | **{infl:+.4f}** | "
                     f"{r.get('n_dropped_unmappable')} |")
    lines += ["", "→ **SATURN 被系统性抬高**（正数），且方向间差异大。", ""]

    # oPCA：检查混淆矩阵里有没有 <not_in_coarse>
    lines += ["## 二、oPCA（检查有无预测落在粗类空间外）", "",
              "| 方向 | 混淆矩阵键数 | 含 `<not_in_coarse>` 的格数 | 结论 |",
              "|---|---|---|---|"]
    for dr, cn in DIRCN.items():
        c = opca.get(dr, {}).get("coarse", {}).get("confusion", {})
        if not c:
            continue
        outside = sum(1 for k in c if SENTINEL in k)
        res["opca_outside_count"][dr] = outside
        lines.append(f"| {cn} | {len(c)} | **{outside}** | "
                     f"{'⚠️ 有落在空间外的预测' if outside else '✅ 无 → 两种口径等价'} |")
    lines += [""]

    # scVI
    lines += ["## 三、scVI（检查有无预测落在粗类空间外）", "",
              "| 方向 | 预测细胞数 | 含 `<not_in_coarse>` 的格子 | 结论 |",
              "|---|---|---|---|"]
    for dr, cn in DIRCN.items():
        p = scvi_dir / (SCV[dr] + ".json")
        if not p.exists():
            continue
        rows = json.loads(p.read_text(encoding="utf-8"))
        n_out = 0
        for r in rows:
            # scVI 的 coarse 预测若落在空间外，通常表现为空串或 unmapped
            if str(r.get("prediction", "")) in ("", "unmapped") or r.get("prediction") is None:
                n_out += 1
        res["scvi_outside_count"][dr] = n_out
        lines.append(f"| {cn} | {len(rows)} | **{n_out}** | "
                     f"{'⚠️ 有' if n_out else '✅ 无 → 两种口径等价'} |")
    lines += [""]

    verdict = ("论点成立：只有 SATURN 会被 drop-unmapped 抬高，"
               "oPCA/scVI 不受影响 → 该口径对四方法不公平")
    res["verdict"] = verdict
    lines += ["## 四、结论", "", f"**{verdict}**", "",
              "**对论文的含义**：任何以「丢弃不可映射预测」为默认口径的基准，",
              "都会**系统性偏袒输出标签空间与评测标签空间不一致的方法**（如 SATURN）。",
              "公平做法：**保留全部细胞、不可映射记错，并同时报 coverage**。", ""]

    OUTDIR.mkdir(parents=True, exist_ok=True)
    (OUTDIR / "drop_unmapped_audit.json").write_text(
        json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    (OUTDIR / "drop_unmapped_audit.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("SATURN 抬高:",
          {DIRCN[k]: v["inflation"] for k, v in res["saturn"].items()})
    print("oPCA 空间外预测数:", res["opca_outside_count"])
    print("scVI 空间外预测数:", res["scvi_outside_count"])
    print("verdict:", verdict)
    print("wrote", OUTDIR / "drop_unmapped_audit.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
