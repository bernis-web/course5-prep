"""生成 oPCA 的「logistic regression 评估器」变体并运行

为什么做（Claude 咨询 §1.4 第 6 条）：
    官方 SATURN 的跨物种准确率用 **logistic regression**（`species_2_logreg_accuracy`,
    train-saturn.py:844）；我们全程用的是 **KNN-15**。
    评估器不同，分数就不可直接比——这是「复现协议」的一部分。

做法：不改原脚本，用文本替换生成变体：
    - `KNeighborsClassifier(...)`  →  `LogisticRegression(...)`
    - 去掉 `kneighbors(...)`（LR 没有邻居）并把 neighbor_barcodes 置空
    - 保留其余全部逻辑（PCA、gene dedup、layer_labels、strict_cell 口径）

输出：
    results/evaluator-20261111/knn_vs_lr.{json,md}
    results/evaluator-20261111/lr-variant/   （LR 变体的 metrics.json）
"""
from __future__ import annotations

import io
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = Path(r"D:\projects\course5-prep")
BASE = ROOT / "scripts" / "ortholog_pca_dcs_v3_fixkey.py"
VARIANT = ROOT / "scripts" / "_opca_lr_variant.py"
OUTDIR = ROOT / "results" / "evaluator-20261111"
DIRCN = {"human->mouse": "人→鼠", "mouse->human": "鼠→人",
         "human->zebrafish": "人→斑马鱼", "zebrafish->human": "斑马鱼→人",
         "mouse->zebrafish": "鼠→斑马鱼", "zebrafish->mouse": "斑马鱼→鼠"}


def make_variant() -> int:
    src = BASE.read_text(encoding="utf-8")
    n = 0

    # 1) 换分类器
    pat = re.compile(r"knn = KNeighborsClassifier\([^)]*\)")
    if pat.search(src):
        src = pat.sub(
            'knn = LogisticRegression(max_iter=2000, n_jobs=-1, random_state=SEED)',
            src)
        n += 1
    else:
        print("!! 没找到 KNeighborsClassifier 定义")
        return 2

    # 2) 去掉 kneighbors 调用（LR 无邻居）——把该行替换成空列表
    src = re.sub(r"neigh_idx = knn\.kneighbors\([^\n]*\)\n",
                 "neigh_idx = None  # LR 变体：无邻居\n", src)
    n += 1

    # 3) neighbor_barcodes 置空
    src = src.replace(
        '"neighbor_barcodes": [str(x) for x in bc_ref_kept[neigh_idx[j]]],',
        '"neighbor_barcodes": [],  # LR 变体')
    n += 1

    # 4) 确保 LogisticRegression 已 import（保留锚点行的缩进——import 块在函数体内）
    if "from sklearn.linear_model import LogisticRegression" not in src:
        m = re.search(r"^(\s*)from sklearn\.neighbors import KNeighborsClassifier\s*$",
                      src, re.M)
        if m:
            indent = m.group(1)
            src = src.replace(
                m.group(0),
                m.group(0) + f"\n{indent}from sklearn.linear_model import LogisticRegression", 1)
            n += 1
        else:
            m2 = re.search(r"^(\s*)import sklearn\s*$", src, re.M)
            indent = m2.group(1) if m2 else ""
            src = src.replace(
                m2.group(0) if m2 else "import sklearn",
                (m2.group(0) if m2 else "import sklearn") +
                f"\n{indent}from sklearn.linear_model import LogisticRegression", 1)
            n += 1

    VARIANT.write_text(src, encoding="utf-8")
    print(f"变体已生成：{VARIANT}（{n} 处替换）")
    return 0


def run_variant() -> int:
    out = OUTDIR / "lr-variant"
    if out.exists():
        print("产出已存在，跳过运行:", out)
        return 0
    env = dict(os.environ)
    env.update({
        "OPCA_H5AD_DIR": str(ROOT),
        "OPCA_ORTH_DIR": str(ROOT / "ortholog"),
        "OPCA_ORTH_MGI": str(ROOT / "ortholog" / "MGI_HOM_MouseHumanSequence.rpt"),
        "OPCA_ORTH_HF": str(ROOT / "ortholog" / "human_orthos.txt"),
        "OPCA_ORTH_MF": str(ROOT / "ortholog" / "mouse_orthos.txt"),
        "OPCA_MAPPING": str(ROOT / "config" / "heart-celltype-map-v2.tsv"),
        "OPCA_OUT": str(out),
    })
    OUTDIR.mkdir(parents=True, exist_ok=True)
    log = OUTDIR / "lr-variant.log"
    print("开始跑 LR 变体（约 1 分钟）…")
    with log.open("w", encoding="utf-8") as fh:
        r = subprocess.run([str(ROOT / ".venv39" / "Scripts" / "python.exe"), str(VARIANT)],
                           env=env, cwd=str(ROOT), stdout=fh, stderr=subprocess.STDOUT)
    print("rc =", r.returncode)
    print(log.read_text(encoding="utf-8")[-800:])
    return r.returncode


def compare() -> int:
    knn_m = json.loads((ROOT / "results" / "mapping-v2-20261111" / "rerun-v2" /
                        "metrics.json").read_text(encoding="utf-8"))
    lr_p = OUTDIR / "lr-variant" / "metrics.json"
    if not lr_p.exists():
        print("LR 变体没产出 metrics.json")
        return 2
    lr_m = json.loads(lr_p.read_text(encoding="utf-8"))

    res = {"date": "2026-11-11",
           "purpose": "评估器消融：KNN-15（我们）vs logistic regression（官方）",
           "knn_source": "results/mapping-v2-20261111/rerun-v2/metrics.json",
           "lr_source": str(lr_p.relative_to(ROOT)).replace("\\", "/"),
           "directions": {}}
    lines = ["# 评估器消融：KNN-15 vs logistic regression（oPCA）", "",
             "> 官方 SATURN 用 **logistic regression**（`train-saturn.py:844 species_2_logreg_accuracy`）；",
             "> 我们全程用 **KNN-15**。本表量化换评估器的影响。", "",
             "| 方向 | KNN-15 acc | LR acc | Δ(LR−KNN) | KNN mf1 | LR mf1 | n_q |",
             "|---|---|---|---|---|---|---|"]

    from collections import Counter
    def mf1_of(d):
        tc, pc, tpc = Counter(), Counter(), Counter()
        for k, n in d.get("confusion", {}).items():
            a, b = k.split("=>")
            tc[a] += n; pc[b] += n
            if a == b:
                tpc[a] += n
        fs = []
        for c in set(tc) | set(pc):
            pr = tpc[c] / pc[c] if pc[c] else 0.0
            rc = tpc[c] / tc[c] if tc[c] else 0.0
            fs.append(2 * pr * rc / (pr + rc) if (pr + rc) else 0.0)
        return sum(fs) / len(fs) if fs else None

    for dr, cn in DIRCN.items():
        k = knn_m.get(dr, {}).get("coarse")
        l = lr_m.get(dr, {}).get("coarse")
        if not k or not l:
            continue
        d_acc = round(l["acc"] - k["acc"], 4)
        rec = {"knn_acc": k["acc"], "lr_acc": l["acc"], "delta_acc": d_acc,
               "knn_mf1": round(mf1_of(k), 4), "lr_mf1": round(mf1_of(l), 4),
               "n_q": k["n_q"]}
        res["directions"][dr] = rec
        lines.append(f"| {cn} | {k['acc']} | {l['acc']} | **{d_acc:+.4f}** | "
                     f"{rec['knn_mf1']} | {rec['lr_mf1']} | {k['n_q']} |")
        print(f"{cn:7s} KNN={k['acc']} LR={l['acc']} Δ={d_acc:+.4f} "
              f"mf1 {rec['knn_mf1']}->{rec['lr_mf1']}", flush=True)

    ds = [v["delta_acc"] for v in res["directions"].values()]
    if ds:
        res["summary"] = {"min_delta": min(ds), "max_delta": max(ds),
                          "mean_delta": round(sum(ds) / len(ds), 4)}
        lines += ["", "## 结论", "",
                  f"- Δ 范围：**{min(ds):+.4f} ~ {max(ds):+.4f}**，均值 **{sum(ds)/len(ds):+.4f}**",
                  "- 若 Δ 很小 → **评估器不是我们低分的主因**，可以排除这一项；",
                  "- 若 Δ 很大 → 评估器必须和原文对齐后才能比分数。"]

    OUTDIR.mkdir(parents=True, exist_ok=True)
    (OUTDIR / "knn_vs_lr.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    (OUTDIR / "knn_vs_lr.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\nwrote", OUTDIR / "knn_vs_lr.json")
    return 0


def main() -> int:
    if make_variant() != 0:
        return 2
    rc = run_variant()
    if rc != 0:
        print("变体运行失败，先不比对")
        return rc
    return compare()


if __name__ == "__main__":
    raise SystemExit(main())
