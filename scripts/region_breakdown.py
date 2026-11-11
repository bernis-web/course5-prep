"""按解剖区（region）拆分对比表 —— 目标④的「器官」维度

为什么做：
    `report-12` 的老师口径与 Claude 咨询都提到「拆开测才看得出哪里好」。
    我们此前只报整体六方向，没有按解剖区拆。

可用性（本地 h5ad 实测）：
    **只有 human 有 `region`**（8 区：SAN/AVN/RA/LA/RV/LV/SP/AX）。
    所以按 region 分层只能用在**评估侧是 human** 的方向：
        mouse→human、zebrafish→human
    其余方向的评估侧是鼠/鱼，只有 `orig.ident`（供体/器官混在一起），
    不能冒充「按器官」——报告里必须写清。

口径：coarse、union macro-F1、strict_cell；带 n 与多数类基线。
输出：results/region-20261111/region_breakdown.{json,md}
"""
from __future__ import annotations

import io
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(r"D:\projects\course5-prep")
PRED = ROOT / "results" / "mapping-v2-20261111" / "rerun-v2" / "predictions"
OUTDIR = ROOT / "results" / "region-20261111"
# 评估侧是 human 的方向（只有这些能用 region）
DIRS = {"mouse->human": "鼠→人", "zebrafish->human": "斑马鱼→人"}
PREFIX = "hu|"


def mf1(t, p):
    tc, pc, tpc = Counter(t), Counter(p), Counter()
    for a, b in zip(t, p):
        if a == b:
            tpc[a] += 1
    fs = []
    for c in set(tc) | set(pc):
        pr = tpc[c] / pc[c] if pc[c] else 0.0
        rc = tpc[c] / tc[c] if tc[c] else 0.0
        fs.append(2 * pr * rc / (pr + rc) if (pr + rc) else 0.0)
    return sum(fs) / len(fs) if fs else 0.0


def load_human_region():
    import h5py
    d = h5py.File(ROOT / "local_human_s.h5ad", "r")
    obs = d["obs"]
    bcs = [x.decode() if isinstance(x, bytes) else str(x) for x in obs[obs.attrs["_index"]][:]]
    g = obs["region"]
    if "codes" in g:
        cats = [x.decode() if isinstance(x, bytes) else str(x) for x in g["categories"][:]]
        labs = [cats[c] if c >= 0 else "NA" for c in g["codes"][:]]
    else:
        labs = [x.decode() if isinstance(x, bytes) else str(x) for x in g[:]]
    d.close()
    return dict(zip(bcs, labs))


def main() -> int:
    region = load_human_region()
    res = {"date": "2026-11-11",
           "purpose": "按 human 解剖区拆分（目标④的器官维度）",
           "caveat": "只有 human 有 region；因此仅评估侧为 human 的两个方向可按 region 分层",
           "region_source": "local_human_s.h5ad 的 obs['region']（8 区）",
           "directions": {}}
    lines = ["# 按解剖区拆分（oPCA，v2 映射，coarse）", "",
             "> **限制**：只有 human 有 `region`（8 区）。所以只做了**评估侧是 human** 的两个方向。",
             "> 其余方向评估侧是鼠/鱼，只有 `orig.ident`（供体与器官混在一起），**不能冒充「按器官」**。", "",
             f"human `region` 取值：{sorted(set(region.values()))}", ""]

    for dr, cn in DIRS.items():
        want = "".join(c for c in f"coarse_{dr.replace('->','_to_')}.json" if c.isalnum())
        pf = None
        for f in PRED.iterdir():
            if "".join(c for c in f.name if c.isalnum()) == want:
                pf = f
                break
        if pf is None:
            print(f"{cn}: 缺文件"); continue
        rows = [r for r in json.loads(pf.read_text(encoding="utf-8")) if r.get("included")]

        groups = defaultdict(lambda: ([], []))
        for r in rows:
            bc = r["prefixed_barcode"]
            bc = bc[len(PREFIX):] if bc.startswith(PREFIX) else bc
            reg = region.get(bc, "NA")
            t, p = groups[reg]
            t.append(r["truth"]); p.append(r["prediction"])

        rec = {}
        lines += [f"## {cn}", "", "| 解剖区 | n | accuracy | macro-F1(union) | 多数类基线 |", "|---|---|---|---|---|"]
        # 整体
        allt = [r["truth"] for r in rows]; allp = [r["prediction"] for r in rows]
        acc_all = sum(a == b for a, b in zip(allt, allp)) / len(allt) if allt else None
        maj_all = max(Counter(allt).values()) / len(allt) if allt else None
        lines.append(f"| **整体** | {len(allt)} | {acc_all:.4f} | {mf1(allt, allp):.4f} | {maj_all:.4f} |")
        rec["_all"] = {"n": len(allt), "accuracy": round(acc_all, 4),
                       "macro_f1_union": round(mf1(allt, allp), 4), "majority": round(maj_all, 4)}
        for reg in sorted(groups):
            t, p = groups[reg]
            if not t:
                continue
            acc = sum(a == b for a, b in zip(t, p)) / len(t)
            maj = max(Counter(t).values()) / len(t)
            rec[reg] = {"n": len(t), "accuracy": round(acc, 4),
                        "macro_f1_union": round(mf1(t, p), 4), "majority": round(maj, 4)}
            lines.append(f"| {reg} | {len(t)} | {acc:.4f} | {mf1(t, p):.4f} | {maj:.4f} |")
            print(f"{cn:8s} {reg:5s} n={len(t):5d} acc={acc:.4f} mf1={mf1(t,p):.4f} maj={maj:.4f}", flush=True)
        res["directions"][dr] = rec

        # 区域间差距
        if len(rec) > 2:
            accs = [v["accuracy"] for k, v in rec.items() if k != "_all"]
            lines += ["", f"- 区间 accuracy 跨度：**{min(accs):.4f} ~ {max(accs):.4f}**（差 {max(accs)-min(accs):+.4f}）", ""]

    OUTDIR.mkdir(parents=True, exist_ok=True)
    (OUTDIR / "region_breakdown.json").write_text(
        json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    (OUTDIR / "region_breakdown.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\nwrote", OUTDIR / "region_breakdown.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
