"""Render the stability + bootstrap tables into Markdown for the teacher reply."""
import json
import io
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
B = json.loads((ROOT / "results/bootstrap-20261030/bootstrap.json").read_text(encoding="utf-8"))
S = json.loads((ROOT / "results/stability-20261030/aggregate.json").read_text(encoding="utf-8"))
R = json.loads((ROOT / "results/resource-20261030/resource_summary.json").read_text(encoding="utf-8"))

DIRS = ["human->mouse", "mouse->human", "human->zebrafish",
        "zebrafish->human", "mouse->zebrafish", "zebrafish->mouse"]
CN = {"human->mouse": "人→鼠", "mouse->human": "鼠→人",
      "human->zebrafish": "人→斑马鱼", "zebrafish->human": "斑马鱼→人",
      "mouse->zebrafish": "鼠→斑马鱼", "zebrafish->mouse": "斑马鱼→鼠"}
MNAME = {"ortholog_pca": "oPCA", "scVI": "scVI", "saturn_v99": "SATURN", "samap": "SAMap"}

print("### 表 A · 逐方向 point estimate ± bootstrap SE（coarse macro-F1，union 口径）\n")
print("| 方向 | 方法 | macro-F1 | ±SE | 95% CI | 95% CI 宽度 | n_q |")
print("|---|---|---|---|---|---|---|")
for dr in DIRS:
    for m in ["ortholog_pca", "scVI", "saturn_v99", "samap"]:
        d = B["methods"][m].get(dr, {})
        if "error" in d or "status" in d or "mf1" not in d:
            continue
        lo, hi = d["mf1_ci95"]
        print(f"| {CN[dr]} | {MNAME[m]} | {d['mf1']:.4f} | ±{d['mf1_se']:.4f} | "
              f"{lo:.4f} – {hi:.4f} | {hi-lo:.4f} | {d['n_q']} |")
    print("| | | | | | | |")

print("\n### 表 B · accuracy ± bootstrap SE\n")
print("| 方向 | oPCA | scVI | SATURN | SAMap |")
print("|---|---|---|---|---|")
for dr in DIRS:
    row = [f"**{CN[dr]}**"]
    for m in ["ortholog_pca", "scVI", "saturn_v99", "samap"]:
        d = B["methods"][m].get(dr, {})
        row.append(f"{d['acc']:.4f} ± {d['acc_se']:.4f}" if "acc" in d else "—")
    print("| " + " | ".join(row) + " |")

print("\n### 表 C · oPCA 稳定性拆解（`results/stability-20261030/aggregate.json`）\n")
print("| 方向 | seed 0–9 均值 ± SD | 极差 | 细胞 90% 重采样 ± SD | 基因 90% 重采样 ± SD |")
print("|---|---|---|---|---|")
for dr in DIRS:
    s = S["seeds"][dr]
    c = S["cells"][dr]
    g = S["genes"][dr]
    print(f"| {CN[dr]} | {s['acc_mean']:.4f} ± {s['acc_sd']:.4f} | {s['acc_range']:.4f} | "
          f"{c['acc_mean']:.4f} ± {c['acc_sd']:.4f} | {g['acc_mean']:.4f} ± {g['acc_sd']:.4f} |")

print("\n### 表 D · oPCA 资源实测（5 次重复，200 次置换）\n")
print(f"| 指标 | 值 |")
print(f"|---|---|")
print(f"| 墙钟时间 | {R['wall_sec_median']} s（{R['wall_sec_min']}–{R['wall_sec_max']}） |")
print(f"| 峰值工作集 | {R['peak_ws_mb_median']} MB（{R['peak_ws_mb_min']}–{R['peak_ws_mb_max']}） |")
print(f"| 峰值提交内存 | {R['peak_pagefile_mb_median']} MB |")
print(f"| 运行次数 | {R['n_runs']} |")

print("\n### 表 E · oPCA v98 vs FIXKEY 口径差（4 个鱼方向）\n")
print("| 方向 | v98 acc | v98 mf1 | FIXKEY acc | FIXKEY mf1 | Δmf1 |")
print("|---|---|---|---|---|---|")
for dr in DIRS:
    d = B["opca_v98_vs_fixkey"][dr]
    print(f"| {CN[dr]} | {d['v98_acc']:.4f} | {d['v98_mf1']:.4f} | {d['fixkey_acc']:.4f} | "
          f"{d['fixkey_mf1']:.4f} | {d['fixkey_mf1']-d['v98_mf1']:+.4f} |")
