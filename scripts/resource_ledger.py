"""Aggregate measured resource consumption from DCS task records + local probes.

Platform fields come from GET /api/task/dcsTask/getUserTaskById?taskId=...
(analyseDuration = seconds of actual compute, analysisAmount = CNY).
Local fields come from results/resource-20261030/resource_summary.json
(in-process PeakWorkingSetSize, exact).

Output: results/phase-20261030/resource-ledger.json
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "phase-20261030" / "resource-ledger.json"

# verbatim from the platform API on 2026-10-30 (seconds, CNY, cells)
TASKS = [
    {"method": "ortholog-PCA", "variant": "FIXKEY v3, platform", "task": "W202610150090794",
     "workflow": "opca_v2", "cells": 4606, "genes": 15869,
     "analyse_sec": 866, "billing_sec": 926, "wall_total_sec": 1589,
     "cny": 0.19, "resource_class": "2c8g", "status": "completed",
     "mem_note": "平台未记录峰值内存字段；本地实测见 memory_local"},
    {"method": "scVI", "variant": "in-phylum 6 dir, platform", "task": "W202610190042919",
     "workflow": "scvi_cross2", "cells": 4606, "genes": 9018,
     "analyse_sec": 916, "billing_sec": 976, "wall_total_sec": 1513,
     "cny": 0.20, "resource_class": "2c8g", "status": "completed",
     "mem_note": "平台任务记录未返回峰值内存；早期记录为 2.37 GB（2c8g 档内实测）"},
    {"method": "scVI", "variant": "cross-phylum lamprey/mouse", "task": "W202610220063725",
     "workflow": "scvi_cross2", "cells": 55694, "genes": 6222,
     "analyse_sec": 9773, "billing_sec": 9833, "wall_total_sec": 10037,
     "cny": 2.06, "resource_class": "2c8g", "status": "completed",
     "mem_note": "早期记录 3.63 GB"},
    {"method": "SAMap", "variant": "joint embedding 4606x150", "task": "W202610260103163",
     "workflow": "runsamap", "cells": 4606, "genes": None,
     "analyse_sec": 354, "billing_sec": 414, "wall_total_sec": 566,
     "cny": 0.02, "resource_class": "1c4g", "status": "completed",
     "mem_note": "未测"},
]

LOCAL = json.loads((ROOT / "results" / "resource-20261030" / "resource_summary.json").read_text(encoding="utf-8"))

def main():
    total_cny = sum(t["cny"] for t in TASKS)
    ledger = {
        "generated": "2026-10-30",
        "sources": {
            "platform": "GET /api/task/dcsTask/getUserTaskById (analyseDuration / analysisAmount)",
            "local": "results/resource-20261030/resource_summary.json (PeakWorkingSetSize in-process)",
        },
        "platform_tasks": TASKS,
        "totals": {
            "n_tasks": len(TASKS),
            "compute_sec_sum": sum(t["analyse_sec"] for t in TASKS),
            "cny_sum": round(total_cny, 2),
        },
        "memory_local": {
            "method": LOCAL["method"], "n_runs": LOCAL["n_runs"],
            "peak_ws_mb_median": LOCAL["peak_ws_mb_median"],
            "peak_ws_mb_range": [LOCAL["peak_ws_mb_min"], LOCAL["peak_ws_mb_max"]],
            "peak_pagefile_mb_median": LOCAL["peak_pagefile_mb_median"],
            "wall_sec_median": LOCAL["wall_sec_median"],
            "wall_sec_range": [LOCAL["wall_sec_min"], LOCAL["wall_sec_max"]],
            "note": "白盒测量：在被测进程内部读 PeakWorkingSetSize，不是外部轮询",
        },
        "gaps": [
            "SATURN 任务没有 CPU/内存字段（GPU 任务，平台未记录）",
            "scVI / SAMap 的峰值内存来自早期单次记录，未重复测量",
            "本台账包含一次 5.5 万细胞重试运行（¥2.06），占总额 84%",
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ledger, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(ledger["totals"], ensure_ascii=False))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
