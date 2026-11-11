"""从 SATURN 输出 adata 算六方向准确率（正对照用）

背景（2026-11-11 第 40 轮查明）：
    SATURN 的 `--score_adatas` 没传时不算分；即使传了，
    `get_all_scores(..., sorted_species_names[0], sorted_species_names[1], ...)`
    **按字母序只算一对**（human vs mouse），而且需要 `--ct_map_path` 指向
    作者机器上的细胞类型对应表。**六个方向它不都算。**

所以本脚本自己做：从 SATURN 输出的 adata 直接算六方向。

输出 adata 的结构（`train-saturn.py:373-401` 的 `create_output_anndata`）：
    X                 SATURN embedding（低维）
    obs['labels']     带物种前缀的标签，如 "human_Adipocyte"
    obs['labels2']    去前缀的标签，如 "Adipocyte"
    obs['species']    物种名
    obsm['macrogenes']

「species_2_logreg_accuracy」的语义 = **用源物种细胞训 logistic regression → 预测目标物种细胞**。
本脚本对六方向各算一遍，并同时给 KNN 作为对照（对应 §2.6 的评估器发现）。

用法：
    python scripts/saturn_output_scores.py --adata <run_name.h5ad> [--map config/heart-celltype-map-v2.tsv]
    # 不带 --map 就是 SATURN 原生口径（直接用 labels2，不做粗类映射）
    # 带 --map 则额外输出「v2 映射 + union macro-F1」那一套

输出：
    results/saturn-official-20261111/saturn_scores.json
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
DIRCN = {"human->mouse": "人→鼠", "mouse->human": "鼠→人",
         "human->zebrafish": "人→斑马鱼", "zebrafish->human": "斑马鱼→人",
         "mouse->zebrafish": "鼠→斑马鱼", "zebrafish->mouse": "斑马鱼→鼠"}
SPECIES = ["human", "mouse", "zebrafish"]


def load_mapping(map_tsv: Path):
    m = {}
    for row in csv.DictReader(open(map_tsv, encoding="utf-8-sig", newline=""), delimiter="\t"):
        m[(row["source_species"].strip(), row["source_label"].strip())] = (
            row["coarse_level"].strip(), row["mapping_status"].strip())
    return m


def to_coarse(sp, lab, m):
    h = m.get((sp, str(lab).strip()))
    if not h:
        return None
    c, s = h
    return c if (s == "active" and c) else None


def mf1_union(truth, pred):
    tc, pc, tpc = Counter(), Counter(), Counter()
    for a, b in zip(truth, pred):
        tc[a] += 1
        pc[b] += 1
        if a == b:
            tpc[a] += 1
    fs = []
    for c in set(tc) | set(pc):
        pr = tpc[c] / pc[c] if pc[c] else 0.0
        rc = tpc[c] / tc[c] if tc[c] else 0.0
        fs.append(2 * pr * rc / (pr + rc) if (pr + rc) else 0.0)
    return sum(fs) / len(fs) if fs else 0.0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--adata", required=True, help="SATURN 输出的 {run_name}.h5ad")
    ap.add_argument("--map", default=None, help="可选：v2 映射表；给了就额外输出粗类口径")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    import anndata as ad
    from sklearn.linear_model import LogisticRegression
    from sklearn.neighbors import KNeighborsClassifier

    a = ad.read_h5ad(args.adata)
    print("adata:", a.shape, "obs:", list(a.obs.columns))
    if "species" not in a.obs:
        print("!! obs 里没有 'species'，无法分物种。实际列：", list(a.obs.columns))
        return 2
    label_col = "labels2" if "labels2" in a.obs else "labels"
    sp = np.asarray([str(x) for x in a.obs["species"]])
    lab = np.asarray([str(x) for x in a.obs[label_col]])
    X = np.asarray(a.X, dtype=np.float32)
    print("species 分布:", Counter(sp))
    print("用标签列:", label_col, "标签数:", len(set(lab)))

    mapping = load_mapping(Path(args.map)) if args.map else None

    res = {"date": "2026-11-11",
           "source_adata": str(Path(args.adata).name),
           "label_col": label_col,
           "metric_note": "lr = 源物种训 LR 预测目标物种（= SATURN 的 species_2_logreg_accuracy 等价物）；"
                          "knn = 同数据换 KNN 评估器",
           "directions": {}}
    lines = ["# SATURN 输出 adata 的六方向准确率", "",
             f"> 来源：`{Path(args.adata).name}`；标签列 `{label_col}`。",
             "> `lr` = 源物种训 logistic regression 预测目标物种（SATURN 原生指标等价物）；",
             "> `knn` = 同数据换 KNN 评估器（用于对上 §2.6 的评估器发现）。", "",
             "| 方向 | n_src | n_tgt | **LR acc** | KNN acc | 目标物种多数类 |", "|---|---|---|---|---|---|"]

    for src in SPECIES:
        for tgt in SPECIES:
            if src == tgt:
                continue
            ms, mt = sp == src, sp == tgt
            if ms.sum() == 0 or mt.sum() == 0:
                continue
            Xs, ys = X[ms], lab[ms]
            Xt, yt = X[mt], lab[mt]
            # LR（SATURN 原生指标）
            lr = LogisticRegression(max_iter=1000, n_jobs=-1)
            lr.fit(Xs, ys)
            pl = lr.predict(Xt)
            acc_lr = float((pl == yt).mean())
            # KNN（对照）
            knn = KNeighborsClassifier(n_neighbors=15, metric="cosine", weights="distance")
            knn.fit(Xs, ys)
            pk = knn.predict(Xt)
            acc_knn = float((pk == yt).mean())
            maj = max(Counter(yt).values()) / len(yt)
            dr = f"{src}->{tgt}"
            rec = {"n_src": int(ms.sum()), "n_tgt": int(mt.sum()),
                   "lr_acc": round(acc_lr, 4), "knn_acc": round(acc_knn, 4),
                   "target_majority": round(maj, 4)}
            # 可选：粗类口径
            if mapping is not None:
                ts = [to_coarse(tgt, y, mapping) for y in yt]
                ps_lr = [to_coarse(src, p, mapping) for p in pl]
                keep = [i for i, t in enumerate(ts) if t]
                if keep:
                    T = [ts[i] for i in keep]
                    P = [ps_lr[i] if ps_lr[i] else "<not_in_coarse>" for i in keep]
                    rec["coarse_n"] = len(keep)
                    rec["coarse_lr_acc"] = round(float(np.mean([a_ == b_ for a_, b_ in zip(T, P)])), 4)
                    rec["coarse_lr_mf1_union"] = round(mf1_union(T, P), 4)
            res["directions"][dr] = rec
            lines.append(f"| {DIRCN.get(dr,dr)} | {rec['n_src']} | {rec['n_tgt']} | "
                         f"**{acc_lr:.4f}** | {acc_knn:.4f} | {maj:.4f} |")
            print(f"{DIRCN.get(dr,dr):8s} n_src={rec['n_src']:5d} n_tgt={rec['n_tgt']:5d} "
                  f"LR={acc_lr:.4f} KNN={acc_knn:.4f} maj={maj:.4f}", flush=True)

    vals = [v["lr_acc"] for v in res["directions"].values()]
    if vals:
        res["summary"] = {"lr_acc_min": min(vals), "lr_acc_max": max(vals),
                          "lr_acc_mean": round(sum(vals) / len(vals), 4)}
        lines += ["", f"- LR acc 范围 **{min(vals):.4f} ~ {max(vals):.4f}**，均值 {sum(vals)/len(vals):.4f}"]

    out = Path(args.out) if args.out else (ROOT / "results" / "saturn-official-20261111" / "saturn_scores.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    (out.parent / "saturn_scores.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\nwrote", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
