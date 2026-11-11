# -*- coding: utf-8 -*-
"""按 audit-stats-20261111.md 的 A/B 级问题修文档。

规则：每条替换声明 expected 次数，实际命中数不符就整条跳过并报警，
      绝不静默瞎替。
"""
import json
import sys
from pathlib import Path

ROOT = Path(r"D:\projects\course5-prep")
V8 = ROOT / "deliverables" / "场景化选型指南-v8-20261109.md"
H = ROOT / "docs" / "execution" / "20261028-master-handoff.md"

FIXES = [
    # ── A1：置信区间状态过期（3 处）──
    (V8, "- ⚠️ 单 seed（seed=0），无置信区间",
         "- ⚠️ 单 seed（seed=0）；已补 bootstrap ±SE（4,000 次重采样，95% CI 见 `bootstrap.json`），未做 seed 稳定性", 1),
    (V8, "- ⚠️ 单 seed，无置信区间；远缘方向的绝对分数都低",
         "- ⚠️ 单 seed；已补 bootstrap ±SE，远缘方向的绝对分数都低", 1),
    (V8, "4. 单 seed（0），无置信区间；",
         "4. 单 seed（0）；已补 bootstrap ±SE（`results/bootstrap-20261030/bootstrap.json`）；", 1),

    # ── A2：六行/五行（与自身表格矛盾）──
    (H, "**六行都是 scVI 最高**——更正后鼠↔鱼两行也正常加粗，不再存在「胜负取决于口径」的分歧。",
     "**六行里五行是 scVI 最高**；鼠→人一行 oPCA 0.6729 > scVI 0.5895，同批配对 Δ=+0.0833、CI[0.0386, 0.1238] 显著。", 1),

    # ── A3：accuracy 与 macro-F1 混比 ──
    (V8, "- 离多数类基线差 **11–13 倍**（0.3059 vs 0.0235–0.0267）；",
     "- 与多数类基线同向（macro-F1）比较：低 **12%–29%**（0.0235–0.0267 vs 0.0274 / 0.0360）；若按 accuracy 口径则是 3.8–6.7 倍；", 1),

    # ── A4：「分母拉齐」不成立（鱼向 n=1469 vs 1499）──
    (V8, "分母拉齐 1,469–1,528", "鱼向 n=1469、人鼠向 n=1499–1528", 1),
    (H, "更正后 oPCA / scVI / SATURN 三家分母已基本一致（1499–1528）",
     "更正后 oPCA / scVI / SATURN 三家分母基本一致（1499–1528），但**鱼向 SATURN 为 1469**（覆盖率 95.7%），跨方法比较仍需按同批细胞配对口径", 1),

    # ── A6：300 倍 → 约 104 倍 ──
    (V8, "规模差 300 倍", "规模差约 104 倍", 1),

    # ── B1：oPCA 人→鱼旧值 ──
    (V8, "门内人→斑马鱼 scVI 0.4014 vs oPCA 0.1682（2.4 倍）",
     "门内人→斑马鱼 scVI 0.4014 vs oPCA 0.1654（2.4 倍）", 1),

    # ── B2：SAMap 时间与费用（台账 354 s / ¥0.02）──
    (V8, "| SAMap | ⚠️ 可行但慢 | 16m24s（DCS 1c4g，¥0.18） | 单次记录 |",
     "| SAMap | ⚠️ 可行但慢 | 354 s（白盒单次，¥0.02） | 单次记录 |", 1),
    (V8, "| SAMap | 16m24s | 未测 | DCS 1c4g | 单次记录，¥0.18 |",
     "| SAMap | 354 s | 未测 | 本机白盒 | 单次记录，¥0.02 |", 1),

    # ── B4：跨门时长 3h29m → 2h43m（台账 9,773 s）──
    (V8, "| **跨门 oPCA + scVI** | **3h29m** |", "| **跨门 oPCA + scVI** | **2h43m（9,773 s）** |", 1),
    (V8, "（已补 scVI 门内 + 跨门 3h29m）", "（已补 scVI 门内 + 跨门 2h43m）", 1),

    # ── B5：内存口径标注 ──
    (V8, "| 1.19 GB | DCS 2c8g | 6 方向全量 |",
     "| 1.19 GB（平台峰值；白盒测 1.31 GB） | DCS 2c8g | 6 方向全量 |", 1),

    # ── B6：SAMap 是否低于基线 ──
    (V8, "| SAMap | ❌ 不推荐 | 0.1127 / 0.0401 | 低于多数类基线 |",
     "| SAMap | ❌ 不推荐 | 0.1127 / 0.0401 | 高于基线 0.0813，但仅两向可评 |", 1),
]

if __name__ == "__main__":
    log = []
    for path, old, new, exp in FIXES:
        if not path.exists():
            log.append({"file": str(path), "status": "MISSING_FILE", "old": old[:40]})
            continue
        txt = path.read_text(encoding="utf-8")
        n = txt.count(old)
        if n != exp:
            log.append({"file": path.name, "status": f"SKIP count={n} expected={exp}", "old": old[:50]})
            continue
        path.write_text(txt.replace(old, new), encoding="utf-8")
        log.append({"file": path.name, "status": "OK", "old": old[:50]})

    for r in log:
        print(f"{r['status']:<28} {r['file']:<40} {r['old']}")
    ok = sum(1 for r in log if r["status"] == "OK")
    print(f"\n应用 {ok}/{len(FIXES)}")
    (ROOT / "tmp" / "fix-log-md.json").write_text(json.dumps(log, ensure_ascii=False, indent=1), encoding="utf-8")