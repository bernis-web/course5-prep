"""Stability campaign driver for ortholog-PCA (10 seeds + 5 cell + 5 gene perturbations).

Every run executes the frozen scoring script in a fresh subprocess via
scripts/opca_stability_run.py, so no in-process state leaks between runs.

Writes:
  results/stability-20261030/runs/<tag>/          full frozen-script outputs
  results/stability-20261030/summary.json         per-run coarse acc / mf1 / n_q
  results/stability-20261030/aggregate.json       mean / sd / min / max per direction
"""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = str(ROOT / ".venv39" / "Scripts" / "python.exe")
BASE = ROOT / "results" / "stability-20261030"
RUNS = BASE / "runs"
DIRS = ["human->mouse", "mouse->human", "human->zebrafish",
        "zebrafish->human", "mouse->zebrafish", "zebrafish->mouse"]


def mf1_union(conf):
    from collections import Counter
    truth, pred, tp = Counter(), Counter(), Counter()
    for k, v in conf.items():
        a, b = k.split("=>")
        truth[a] += v
        pred[b] += v
        if a == b:
            tp[a] += v
    fs = []
    for c in sorted(set(truth) | set(pred)):
        p = tp[c] / pred[c] if pred[c] else 0.0
        r = tp[c] / truth[c] if truth[c] else 0.0
        fs.append(2 * p * r / (p + r) if (p + r) else 0.0)
    return sum(fs) / len(fs)


def run(tag, seed, h5ad_dir, nperm=50):
    out = RUNS / tag
    if out.exists():
        print(f"SKIP {tag} (exists)", flush=True)
        return tag
    env = dict(os.environ)
    env.update({
        "OPCA_H5AD_DIR": str(h5ad_dir),
        "OPCA_OUT": str(out),
        "STAB_SEED": str(seed),
        "STAB_NPERM": str(nperm),
        "PYTHONIOENCODING": "utf-8",
    })
    r = subprocess.run([PY, str(ROOT / "scripts" / "opca_stability_run.py")],
                       env=env, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", cwd=str(ROOT))
    tail = (r.stdout or "").strip().splitlines()[-3:]
    print(f"[{tag}] exit={r.returncode} {' | '.join(tail)}", flush=True)
    if r.returncode != 0:
        print((r.stderr or "")[-2000:], flush=True)
    return tag


def collect():
    rows = []
    for d in RUNS.iterdir():
        if not d.is_dir():
            continue
        mp = d / "metrics.json"
        if not mp.exists():
            continue
        met = json.loads(mp.read_text(encoding="utf-8"))
        man = json.loads((d / "manifest.json").read_text(encoding="utf-8"))
        pert = d.parent.parent / "tmp" / "stab-data" / d.name
        row = {"tag": d.name, "seed": man["params"]["seed"], "elapsed_sec": man["elapsed_sec"]}
        for dr in DIRS:
            c = met[dr]["coarse"]
            row[dr] = {"acc": c["acc"], "mf1": round(mf1_union(c["confusion"]), 6),
                       "n_q": c["n_q"], "n_q_total": c["n_q_total"],
                       "majority": c["majority"]}
        rows.append(row)
    rows.sort(key=lambda x: x["tag"])
    (BASE / "summary.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False), encoding="utf-8")
    return rows


def aggregate(rows):
    import statistics
    fam = {
        "seeds": [r for r in rows if r["tag"].startswith("seed-")],
        "cells": [r for r in rows if r["tag"].startswith("cells-")],
        "genes": [r for r in rows if r["tag"].startswith("genes-")],
    }
    agg = {}
    for name, rs in fam.items():
        agg[name] = {"n_runs": len(rs)}
        for dr in DIRS:
            accs = [r[dr]["acc"] for r in rs]
            mf1s = [r[dr]["mf1"] for r in rs]
            nqs = [r[dr]["n_q"] for r in rs]
            agg[name][dr] = {
                "acc_mean": round(statistics.mean(accs), 4) if accs else None,
                "acc_sd": round(statistics.stdev(accs), 4) if len(accs) > 1 else 0.0,
                "acc_min": min(accs) if accs else None,
                "acc_max": max(accs) if accs else None,
                "acc_range": round(max(accs) - min(accs), 4) if accs else None,
                "mf1_mean": round(statistics.mean(mf1s), 4) if mf1s else None,
                "mf1_sd": round(statistics.stdev(mf1s), 4) if len(mf1s) > 1 else 0.0,
                "n_q_min": min(nqs) if nqs else None,
                "n_q_max": max(nqs) if nqs else None,
            }
    (BASE / "aggregate.json").write_text(json.dumps(agg, indent=1, ensure_ascii=False), encoding="utf-8")
    return agg


def main():
    RUNS.mkdir(parents=True, exist_ok=True)
    nperm = int(os.environ.get("STAB_NPERM", "50"))
    # 1) seed sweep on the frozen data (seed 0 = baseline, must match frozen values)
    for s in range(10):
        run(f"seed-{s}", s, ROOT, nperm)
        rows = collect()
        print(json.dumps([r for r in rows if r["tag"] == f"seed-{s}"], ensure_ascii=False), flush=True)

    # 2) perturbed data
    for kind, n in (("cells", 5), ("genes", 5)):
        for rep in range(1, n + 1):
            d = ROOT / "tmp" / "stab-data" / f"{kind}-{rep}"
            if not (d / "local_human_s.h5ad").exists():
                subprocess.run([PY, str(ROOT / "scripts" / "stab_make_perturbed_data.py"),
                                kind, str(rep)], cwd=str(ROOT), check=True)
            run(f"{kind}-{rep}", 0, d, nperm)
            collect()

    rows = collect()
    agg = aggregate(rows)
    print("COLLECTED", len(rows), "runs", flush=True)
    print(json.dumps(agg["seeds"], indent=1, ensure_ascii=False)[:1500], flush=True)


if __name__ == "__main__":
    main()
