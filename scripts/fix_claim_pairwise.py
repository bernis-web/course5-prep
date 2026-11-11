# -*- coding: utf-8 -*-
"""第二波：把「scVI 四向最优」降级为「四向数值最高，其一不显著」，并记录 Δ 语义变化。"""
from pathlib import Path

ROOT = Path(r"D:\projects\course5-prep")
V8 = ROOT / "deliverables" / "场景化选型指南-v8-20261109.md"

FIXES = [
    (V8,
     "- **scVI 在远缘四向全部最优**：人↔鱼 0.4014 / 0.4290；鼠↔鱼 0.4248 / 0.4786。",
     "- **scVI 在远缘四向数值最高**：人↔鱼 0.4014 / 0.4290；鼠↔鱼 0.4248 / 0.4786。"
     "但 鼠→斑马鱼 与 SATURN 的差 Δ=−0.0172、独立重抽样 95% CI[−0.0580, +0.0230] 含 0，"
     "**该向差距不显著**，不进「显著最优」名单。"),
    (V8,
     "0.1282 / 0.1386 / 0.4076 / 0.2961（近缘两向不变）。**推荐结论不变**（scVI 仍四向最优）。",
     "0.1282 / 0.1386 / 0.4076 / 0.2961（近缘两向不变）。**推荐结论不变**"
     "（scVI 四向数值最高；其中 鼠→斑马鱼 Δ=−0.0172、CI 含 0，不显著）。\n"
     "> **2026-11-11 修订**：SATURN 侧改由 `confusion/` 还原后，"
     "`pairwise_corrected.json` 的 Δ 语义变为「两法各自独立重抽样」，不再是同批细胞配对；"
     "判定见 `docs/reports/audit-saturn-payload-gate-20261111.md`。"),
]

for path, old, new in FIXES:
    txt = path.read_text(encoding="utf-8")
    n = txt.count(old)
    if n != 1:
        print(f"SKIP count={n}  {old[:50]}")
        continue
    path.write_text(txt.replace(old, new), encoding="utf-8")
    print(f"OK    {path.name}  {old[:50]}")