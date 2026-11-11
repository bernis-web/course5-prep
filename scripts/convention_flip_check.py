"""两种 oPCA 口径下，方法排名会不会翻转？

比较：
  A) oPCA = `exact` 层重映射（pairwise_corrected.py）
  B) oPCA = 粗类空间 KNN 真实产物（pairwise_opca_official.py）

这是论文主线的核心命题之一：「换口径会不会改变结论」。本脚本给出逐方向答案。
"""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = Path(r"D:\projects\course5-prep")
A = json.loads((ROOT / "results" / "pairwise-20261111" / "pairwise_corrected.json").read_text(encoding="utf-8"))
B = json.loads((ROOT / "results" / "pairwise-20261111" / "opca_official_paired.json").read_text(encoding="utf-8"))
DIRCN = {"human->mouse": "人→鼠", "mouse->human": "鼠→人", "human->zebrafish": "人→斑马鱼",
         "zebrafish->human": "斑马鱼→人", "mouse->zebrafish": "鼠→斑马鱼", "zebrafish->mouse": "斑马鱼→鼠"}

print("=== oPCA vs scVI：两种口径下的胜者 ===")
print(f"{'方向':10s} {'重映射':>9s} {'官方':>9s} {'重映射胜者':>10s} {'官方胜者':>10s}  翻转")
flips = 0
for d, cn in DIRCN.items():
    r = A["comparisons"][d]["opca_vs_scVI"]
    o = B["comparisons"][d]["opca_vs_scVI"]
    w_r = "oPCA" if r["delta"] > 0 else "scVI"
    w_o = "oPCA" if o["delta"] > 0 else "scVI"
    flip = "★翻转" if w_r != w_o else "-"
    flips += 1 if w_r != w_o else 0
    print(f"{cn:10s} {r['opca_mf1']:9.4f} {o['mf1_a']:9.4f} {w_r:>10s} {w_o:>10s}  {flip}")

print()
print("=== oPCA vs SATURN：两种口径下的胜者 ===")
print(f"{'方向':10s} {'重映射胜者':>10s} {'官方胜者':>10s}  翻转")
for d, cn in DIRCN.items():
    r = A["comparisons"][d]["saturn_v99_vs_opca"]      # delta = saturn - opca
    o = B["comparisons"][d]["opca_vs_saturn_v99"]      # delta = opca - saturn
    w_r = "SATURN" if r["delta"] > 0 else "oPCA"
    w_o = "oPCA" if o["delta"] > 0 else "SATURN"
    flip = "★翻转" if w_r != w_o else "-"
    flips += 1 if w_r != w_o else 0
    print(f"{cn:10s} {w_r:>10s} {w_o:>10s}  {flip}")

print()
print(f"合计翻转条数：{flips}")
print()
print("=== oPCA 数值本身差多少（重映射 - 官方）===")
for d, cn in DIRCN.items():
    r = A["comparisons"][d]["opca_vs_scVI"]["opca_mf1"]
    o = B["comparisons"][d]["opca_vs_scVI"]["mf1_a"]
    print(f"  {cn:10s} {r:.4f} - {o:.4f} = {r - o:+.4f}")
