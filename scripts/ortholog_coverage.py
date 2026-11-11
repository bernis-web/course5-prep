"""量化同源图覆盖率：我们的 1:1 直系同源图 vs 全量基因

为什么做（目标③「输入」维度）：
    我们 SAMap 用的是 MGI/ZFIN 的 1:1 直系同源（`docs/execution/20261111-samap-blast-plan.md` 已确认），
    原文用的是 BLAST 全同源图。**但「差多少」一直没量化。**

本脚本给出可引用的数字：
    每个物种有多少基因、其中多少条被 1:1 图覆盖、覆盖率是多少。

数据源（都在本地）：
    基因列表：local_{human,mouse,zebrafish}_s.h5ad 的 var_names
    同源记录：ortholog/MGI_HOM_MouseHumanSequence.rpt（human↔mouse）
              ortholog/human_orthos.txt、ortholog/mouse_orthos.txt（含 zebrafish）

输出：results/ortholog-coverage-20261111/coverage.{json,md}
"""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = Path(r"D:\projects\course5-prep")
OUTDIR = ROOT / "results" / "ortholog-coverage-20261111"


def genes_of(sp: str) -> set:
    import h5py
    d = h5py.File(ROOT / f"local_{sp}_s.h5ad", "r")
    v = d["var"]
    key = v.attrs.get("_index", None)
    if key is None:
        names = list(v.keys())
        d.close()
        return set(names)
    raw = v[key][:]
    d.close()
    return {x.decode() if isinstance(x, bytes) else str(x) for x in raw}


def parse_mgi(path: Path) -> set:
    """MGI_HOM_MouseHumanSequence.rpt -> 人类符号集合。"""
    out = set()
    try:
        for line in open(path, encoding="utf-8", errors="replace"):
            parts = [p.strip() for p in line.rstrip("\n").split("\t")]
            # 该文件列：DB Class Key / Ortholog Group ID / NCBI Taxon ID / Symbol / ...
            if len(parts) >= 4 and parts[2] == "9606":      # 9606 = human
                s = parts[3].strip('" ')
                if s:
                    out.add(s)
    except Exception as e:
        print("MGI parse err:", e)
    return out


def parse_orthos(path: Path) -> tuple:
    """orthos 文件：取每行第一列作为人类符号，全部列作为对侧符号。"""
    hu, other = set(), set()
    try:
        for line in open(path, encoding="utf-8", errors="replace"):
            line = line.rstrip("\n")
            if not line.strip():
                continue
            parts = [p.strip('" ') for p in line.split("\t")]
            if parts and parts[0] and parts[0].lower() not in ("human", "nan"):
                hu.add(parts[0])
            for p in parts[1:]:
                if p and p.lower() not in ("nan", "zfin", "mgi"):
                    other.add(p)
    except Exception as e:
        print("orthos parse err:", e)
    return hu, other


def main() -> int:
    res = {"date": "2026-11-11",
           "purpose": "量化我们的 1:1 同源图覆盖率（目标③输入维度的基础数字）",
           "note": "覆盖率 = 该物种基因中「在同源记录里出现过」的比例",
           "species": {}, "graphs": {}}

    g = {}
    for sp in ("human", "mouse", "zebrafish"):
        try:
            g[sp] = genes_of(sp)
            print(f"{sp}: {len(g[sp])} 基因")
        except Exception as e:
            print(f"{sp}: ERR {e}")
            g[sp] = set()

    # MGI：human↔mouse
    mgi_h = parse_mgi(ROOT / "ortholog" / "MGI_HOM_MouseHumanSequence.rpt")
    # ZFIN orthos
    zh, zo = parse_orthos(ROOT / "ortholog" / "human_orthos.txt")
    mh, mo = parse_orthos(ROOT / "ortholog" / "mouse_orthos.txt")
    print(f"MGI human symbols: {len(mgi_h)}")
    print(f"human_orthos: hu={len(zh)} other={len(zo)}")
    print(f"mouse_orthos: hu={len(mh)} other={len(mo)}")

    # 我们实际用的图（源：local_samap3.py / run_samap_compliant_v98.py）
    hu_all = mgi_h | zh | mh
    mo_all = mgi_h | mo
    zf_all = zo

    for sp, mapped_pool in (("human", hu_all), ("mouse", mo_all), ("zebrafish", zf_all)):
        total = len(g[sp])
        hit = len(g[sp] & mapped_pool)
        rec = {"total_genes": total, "mapped_genes": hit,
               "unmapped_genes": total - hit,
               "coverage": round(hit / total, 4) if total else None}
        res["species"][sp] = rec
        print(f"{sp:10s} total={total:6d} mapped={hit:6d} unmapped={total-hit:6d} "
              f"coverage={rec['coverage']}")

    res["graphs"] = {
        "mgi_human_symbols": len(mgi_h),
        "human_orthos_human": len(zh), "human_orthos_other": len(zo),
        "mouse_orthos_human": len(mh), "mouse_orthos_other": len(mo),
    }

    lines = ["# 同源图覆盖率（我们的 1:1 直系同源 vs 全量基因）", "",
             "> **背景**：SAMap 侧我们用的是 MGI/ZFIN 的 1:1 直系同源（源码级确认），",
             "> 原文用 BLAST 全同源图。本表量化**差多少**。", "",
             "| 物种 | 基因总数 | 有同源记录 | 无同源记录 | **覆盖率** |",
             "|---|---|---|---|---|"]
    for sp, rec in res["species"].items():
        lines.append(f"| {sp} | {rec['total_genes']} | {rec['mapped_genes']} | "
                     f"{rec['unmapped_genes']} | **{rec['coverage']}** |")
    lines += ["", "## 同源记录规模", "",
              "| 来源 | 条目数 |", "|---|---|",
              f"| MGI_HOM（human 符号） | {len(mgi_h)} |",
              f"| human_orthos（含 zebrafish） | {len(zh)} |",
              f"| mouse_orthos（含 zebrafish） | {len(mh)} |", "",
              "**读法**：覆盖率低于 100% 的部分，是 1:1 图**根本映射不到**的基因；",
              "BLAST 全图会把这些基因里的一部分也连上。**这就是输入层的差异量级。**", ""]

    OUTDIR.mkdir(parents=True, exist_ok=True)
    (OUTDIR / "coverage.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    (OUTDIR / "coverage.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\nwrote", OUTDIR / "coverage.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
