"""Repeat memory/CPU probes for oPCA and emit a summary.

Each rep runs scripts/memprobe_run.py in a fresh process (exact in-process peak
memory accounting), 200 permutations, frozen data.
"""
import json
import os
import statistics
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = str(ROOT / ".venv39" / "Scripts" / "python.exe")
BASE = ROOT / "results" / "resource-20261030"


def main():
    reps = int(os.environ.get("RES_REPS", "5"))
    recs = []
    for i in range(reps):
        out = BASE / f"opca-rep{i}" / "output"
        if out.exists():
            print(f"SKIP rep{i}", flush=True)
            continue
        env = dict(os.environ)
        env.update({
            "OPCA_H5AD_DIR": str(ROOT),
            "OPCA_OUT": str(out),
            "STAB_SEED": str(i),
            "STAB_NPERM": "200",
            "PYTHONIOENCODING": "utf-8",
        })
        t0 = time.time()
        r = subprocess.run([PY, str(ROOT / "scripts" / "memprobe_run.py")], env=env,
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        line = next((l for l in (r.stdout or "").splitlines() if l.startswith("PEAK|")), None)
        if not line:
            print(f"[rep{i}] FAILED {(r.stderr or '')[-400:]}", flush=True)
            continue
        rec = json.loads(line[5:])
        rec["tag"] = f"opca-rep{i}"
        rec["outer_wall_sec"] = round(time.time() - t0, 2)
        recs.append(rec)
        print(f"[rep{i}] ws={rec['peak_working_set_mb']} MB pagefile={rec['peak_pagefile_mb']} MB "
              f"wall={rec['wall_sec_total']}s", flush=True)

    if recs:
        agg = {
            "method": "ortholog-PCA (fixkey v3, 4,606 cells x 3 species, 200 perms)",
            "host": "Windows 11 laptop, python 3.9.6, single process",
            "n_runs": len(recs),
            "wall_sec_median": round(statistics.median(r["wall_sec_total"] for r in recs), 2),
            "wall_sec_min": min(r["wall_sec_total"] for r in recs),
            "wall_sec_max": max(r["wall_sec_total"] for r in recs),
            "peak_ws_mb_median": round(statistics.median(r["peak_working_set_mb"] for r in recs), 1),
            "peak_ws_mb_min": min(r["peak_working_set_mb"] for r in recs),
            "peak_ws_mb_max": max(r["peak_working_set_mb"] for r in recs),
            "peak_pagefile_mb_median": round(statistics.median(r["peak_pagefile_mb"] for r in recs), 1),
            "runs": recs,
        }
        (BASE / "resource_summary.json").write_text(json.dumps(agg, indent=1), encoding="utf-8")
        print("SUMMARY|" + json.dumps({k: v for k, v in agg.items() if k != "runs"}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
