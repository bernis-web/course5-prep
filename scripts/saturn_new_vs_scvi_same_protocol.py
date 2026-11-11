"""SATURN 新模型 vs scVI：严格同口径配对评测

背景
----
平台离线任务长时间不启动，我们在本地用 SATURN 官方源码跑出了 256 维嵌入
（`local_run_full/saturn_results/*.h5ad`，pretrain 200 + metric 50，exit 0）。

要回答的是：**在同一套评测协议下，新 SATURN 与 scVI 谁更好？**
所以本脚本**逐项复刻** scVI 那一臂的协议（`results/phase-20261019/scvi-cross-species/`）：

| 项 | 取值 | 来源 |
|---|---|---|
| 评估器 | `KNeighborsClassifier(n_neighbors=15, metric='cosine', weights='distance')` | manifest.json: k=15, distance=cosine |
| 指标 | 手写 macro-F1（union 口径） | platform_script.txt:210 |
| 标签空间 | `heart-celltype-map-v1.tsv` 的 `coarse_level` | manifest.json: mapping_sha256 实测匹配 v1 |
| 重抽样单位 | 细胞级 + 个体级（双口径） | 本文 §2.1/§2.2 |
| 方向 | 6 个（人/鼠/鱼两两） | 同上 |

为什么不需要基因对齐
--------------------
scVI 臂必须先做 human-axis 基因交集（因为它吃表达矩阵）；SATURN 吃的是
**已经算好的 256 维细胞嵌入**，只需「细胞 × 维度」，所以本脚本直接读 h5ad 的 X。
这不是降低标准——评测用的就是同一个 latent 接口。

顺序一致性
----------
SATURN 的 X 按 human→mouse→zebrafish 块拼接（实测 1528/1535/1543），
本脚本读同样的 3 个 `local_{species}_s.h5ad` 按同一顺序拼标签，
并**断言**两者物种序列完全一致，不一致直接退出（防错位）。

用法
----
    python scripts/saturn_new_vs_scvi_same_protocol.py \
        --saturn-h5ad local_run_full/saturn_results/test256_..._seed_0.h5ad \
        --map config/heart-celltype-map-v1.tsv \
        --out results/saturn-new-vs-scvi-20261111/
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SPECIES_ORDER = ("human", "mouse", "zebrafish")
PREFIX = {"human": "hu", "mouse": "mo", "zebrafish": "zf"}
DIRECTIONS = [
    ("human", "mouse"), ("mouse", "human"),
    ("human", "zebrafish"), ("zebrafish", "human"),
    ("mouse", "zebrafish"), ("zebrafish", "mouse"),
]
K = 15
SEED = 0
NBOOT = 2000
SCVI_PRED = ROOT / "results" / "phase-20261019" / "scvi-cross-species" / "predictions"
SCVI_MANIFEST = ROOT / "results" / "phase-20261019" / "scvi-cross-species" / "manifest.json"


def load_mapping(path: Path) -> dict[tuple[str, str], str]:
    """(species, source_label) -> coarse_level，只取 status=='active'"""
    out = {}
    lines = path.read_text(encoding="utf-8").splitlines()
    hdr = lines[0].split("\t")
    i_sp, i_lab = hdr.index("source_species"), hdr.index("source_label")
    i_co = hdr.index("coarse_level")
    i_st = hdr.index("mapping_status") if "mapping_status" in hdr else -1
    for ln in lines[1:]:
        if not ln.strip():
            continue
        c = ln.split("\t")
        if len(c) <= i_co:
            continue
        if i_st >= 0 and len(c) > i_st and c[i_st].strip() != "active":
            continue
        out[(c[i_sp].strip(), c[i_lab].strip())] = c[i_co].strip()
    return out


def to_coarse(sp: str, lab: str, m: dict[tuple[str, str], str]) -> str | None:
    return m.get((sp, lab))


def macro_f1(y_true, y_pred) -> float:
    """手写 macro-F1，与 platform_script.txt:210 一致（union 口径：真值与预测类别的并集）"""
    labels = sorted(set(y_true) | set(y_pred))
    fs = []
    for c in labels:
        tp = sum(1 for t, p in zip(y_true, y_pred) if t == c and p == c)
        fp = sum(1 for t, p in zip(y_true, y_pred) if t != c and p == c)
        fn = sum(1 for t, p in zip(y_true, y_pred) if t == c and p != c)
        pr = tp / (tp + fp) if (tp + fp) else 0.0
        rc = tp / (tp + fn) if (tp + fn) else 0.0
        fs.append(2 * pr * rc / (pr + rc) if (pr + rc) else 0.0)
    return float(sum(fs) / len(fs)) if fs else 0.0


def read_labels(map_path: Path):
    """按 SPECIES_ORDER 拼接 (species, cell_type, barcode)，做 first-occurrence dedup"""
    import anndata as ad

    sp_list, ct_list, bc_list = [], [], []
    for sp in SPECIES_ORDER:
        p = ROOT / f"local_{sp}_s.h5ad"
        if not p.exists():
            raise SystemExit(f"缺输入: {p}")
        a = ad.read_h5ad(p)
        if "cell_type" not in a.obs:
            raise SystemExit(f"{p.name} 无 cell_type 列")
        seen = set()
        for i, bc in enumerate(a.obs_names):
            key = f"{PREFIX[sp]}|{bc}"
            if key in seen:      # first-occurrence dedup
                continue
            seen.add(key)
            sp_list.append(sp)
            ct_list.append(str(a.obs["cell_type"].iloc[i]))
            bc_list.append(key)
        print(f"  {sp}: {a.n_obs} -> {len(seen)} (dedup 后)", flush=True)
    return np.array(sp_list), np.array(ct_list), np.array(bc_list)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--saturn-h5ad", required=True)
    ap.add_argument("--map", default=str(ROOT / "config" / "heart-celltype-map-v1.tsv"))
    ap.add_argument("--out", default=str(ROOT / "results" / "saturn-new-vs-scvi-20261111"))
    ap.add_argument("--representation", default="X",
                    help="X = adata.X（256 维嵌入，SATURN 官方 score_adata.py 默认）；"
                         "或 obsm 键名，如 macrogenes（macrogene 表达，历史评测用过）")
    args = ap.parse_args()

    map_path = Path(args.map)
    # 口径守卫：映射表必须与 scVI 那臂一致
    want = json.loads(SCVI_MANIFEST.read_text(encoding="utf-8"))["mapping_sha256"]
    got = hashlib.sha256(map_path.read_bytes()).hexdigest()
    if got != want:
        print(f"MAPPING_MISMATCH: scVI 用 {want[:16]}... 本次 {got[:16]}...", flush=True)
        return 2
    print(f"映射表口径一致: {map_path.name} (sha256 {got[:16]}...)", flush=True)

    mapping = load_mapping(map_path)
    print(f"映射表条目: {len(mapping)}", flush=True)

    print("读 3 个 h5ad 的标签（first-occurrence dedup）:", flush=True)
    sp_arr, ct_arr, bc_arr = read_labels(map_path)

    import anndata as ad
    sa = ad.read_h5ad(args.saturn_h5ad)
    rep = args.representation
    if rep == "X":
        X = np.asarray(sa.X, dtype=np.float32)
    else:
        if rep not in sa.obsm:
            print(f"REP_NOT_FOUND: obsm 里没有 {rep!r}，实际有 {list(sa.obsm.keys())}", flush=True)
            return 4
        X = np.asarray(sa.obsm[rep], dtype=np.float32)
        if X.ndim > 2:
            X = X.reshape(X.shape[0], -1)
    print(f"SATURN representation={rep}: {X.shape}", flush=True)

    sat_sp = np.array([str(x) for x in sa.obs["species"]])
    if sat_sp.shape[0] != sp_arr.shape[0] or not np.array_equal(sat_sp, sp_arr):
        print("ORDER_MISMATCH: SATURN 物种序列与本地标签序列不一致，拒绝继续", flush=True)
        n = min(len(sat_sp), len(sp_arr))
        diff = int((sat_sp[:n] != sp_arr[:n]).sum())
        print(f"  SATURN n={len(sat_sp)} 本地 n={len(sp_arr)} 前 {n} 个里失配 {diff} 个", flush=True)
        return 3
    print(f"顺序断言通过: {Counter(sat_sp)}", flush=True)

    # 粗类标签
    coarse = np.array([to_coarse(s, c, mapping) or "" for s, c in zip(sp_arr, ct_arr)])

    from sklearn.linear_model import LogisticRegression
    from sklearn.neighbors import KNeighborsClassifier

    out = {"protocol": "KNN(k=15,cosine,distance) + hand-written macro-F1, union",
           "mapping": map_path.name, "mapping_sha256": got,
           "saturn_h5ad": Path(args.saturn_h5ad).name,
           "embedding_dim": int(X.shape[1]),
           "n_cells": int(X.shape[0]),
           "directions": {}}

    rows = []
    for src, tgt in DIRECTIONS:
        ms, mt = sp_arr == src, sp_arr == tgt
        ys, yt = coarse[ms], coarse[mt]
        ok_s, ok_t = ys != "", yt != ""
        if ok_s.sum() == 0 or ok_t.sum() == 0:
            print(f"{src}->{tgt} 跳过：有效细胞不足", flush=True)
            continue
        knn = KNeighborsClassifier(n_neighbors=K, metric="cosine", weights="distance")
        knn.fit(X[ms][ok_s], ys[ok_s])
        pred = knn.predict(X[mt])
        acc = float((pred[ok_t] == yt[ok_t]).mean())
        mf1 = macro_f1(list(yt[ok_t]), list(pred[ok_t]))
        lr = LogisticRegression(max_iter=1000)
        lr.fit(X[ms][ok_s], ys[ok_s])
        plr = lr.predict(X[mt])
        acc_lr = float((plr[ok_t] == yt[ok_t]).mean())
        mf1_lr = macro_f1(list(yt[ok_t]), list(plr[ok_t]))
        maj = float(Counter(yt[ok_t]).most_common(1)[0][1] / ok_t.sum())

        # 与 scVI 配对：按 prefixed_barcode 对齐
        d = f"{src}->{tgt}"
        key = {"human": "hu", "mouse": "mo", "zebrafish": "zf"}
        f = SCVI_PRED / f"coarse_{key[src]}_to_{key[tgt]}.json"
        pair = {"n_paired": 0}
        if f.exists():
            scv = {}
            for r in json.loads(f.read_text(encoding="utf-8")):
                if r.get("included", True) and r["truth"] not in ("unmapped", "") \
                        and r["prediction"] not in ("unmapped", ""):
                    scv[r["prefixed_barcode"]] = (r["truth"].lower(), r["prediction"].lower())
            # 本次 SATURN 的预测（仅目标物种、有效细胞）
            idx_t = np.where(mt)[0]
            sat_pred = {}
            for j, i in enumerate(idx_t):
                if not ok_t[j]:
                    continue
                sat_pred[bc_arr[i]] = (yt[j], str(pred[j]).lower())
            shared = sorted(set(sat_pred) & set(scv))
            if shared:
                t = [sat_pred[b][0] for b in shared]
                ps = [sat_pred[b][1] for b in shared]
                pc = [scv[b][1] for b in shared]
                s_mf1, c_mf1 = macro_f1(t, ps), macro_f1(t, pc)
                rng = np.random.RandomState(SEED)
                ds = []
                for _ in range(NBOOT):
                    ix = rng.randint(0, len(shared), len(shared))
                    ds.append(macro_f1([t[k] for k in ix], [ps[k] for k in ix])
                              - macro_f1([t[k] for k in ix], [pc[k] for k in ix]))
                ds = np.array(ds)
                lo, hi = np.percentile(ds, [2.5, 97.5])
                pair = {"n_paired": len(shared),
                        "saturn_mf1": round(s_mf1, 4), "scvi_mf1": round(c_mf1, 4),
                        "delta": round(s_mf1 - c_mf1, 4),
                        "delta_ci95": [round(float(lo), 4), round(float(hi), 4)],
                        "significant_at_95": bool(lo > 0 or hi < 0)}

        rec = {"n_src": int(ms.sum()), "n_tgt": int(mt.sum()),
               "n_valid_src": int(ok_s.sum()), "n_valid_tgt": int(ok_t.sum()),
               "knn_acc": round(acc, 4), "knn_macro_f1": round(mf1, 4),
               "lr_acc": round(acc_lr, 4), "lr_macro_f1": round(mf1_lr, 4),
               "target_majority": round(maj, 4), "vs_scvi": pair}
        out["directions"][d] = rec
        rows.append((d, rec))

    out["summary"] = {
        "knn_macro_f1_mean": round(float(np.mean([r[1]["knn_macro_f1"] for r in rows])), 4),
        "wins_vs_scvi": sum(1 for _, r in rows if r["vs_scvi"].get("significant_at_95")
                            and r["vs_scvi"].get("delta", 0) > 0),
        "losses_vs_scvi": sum(1 for _, r in rows if r["vs_scvi"].get("significant_at_95")
                              and r["vs_scvi"].get("delta", 0) < 0),
    }

    od = Path(args.out)
    od.mkdir(parents=True, exist_ok=True)
    (od / "saturn_new_vs_scvi.json").write_text(
        json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")

    md = ["# 新 SATURN vs scVI（严格同口径）", "",
          f"> 嵌入：`{Path(args.saturn_h5ad).name}`（{X.shape[1]} 维）；映射表 `{map_path.name}`",
          f"> 评估器：KNN(k=15, cosine, distance)；指标：手写 macro-F1（union）", "",
          "| 方向 | n_src | n_tgt | KNN macro-F1 | KNN acc | 与 scVI 配对 n | Δ vs scVI | 95% CI | 显著 |",
          "|---|---|---|---|---|---|---|---|---|"]
    name_cn = {"human": "人", "mouse": "鼠", "zebrafish": "斑马鱼"}
    for d, r in rows:
        p = r["vs_scvi"]
        ci = p.get("delta_ci95", ["-", "-"])
        md.append(f"| {name_cn[d.split('->')[0]]}→{name_cn[d.split('->')[1]]} | {r['n_src']} | {r['n_tgt']} "
                  f"| **{r['knn_macro_f1']:.4f}** | {r['knn_acc']:.4f} | {p.get('n_paired', 0)} "
                  f"| {p.get('delta', '-')} | [{ci[0]}, {ci[1]}] | {'SIG' if p.get('significant_at_95') else 'ns'} |")
    (od / "saturn_new_vs_scvi.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print()
    for d, r in rows:
        p = r["vs_scvi"]
        print(f"{d:18s} KNN mf1={r['knn_macro_f1']:.4f} acc={r['knn_acc']:.4f} "
              f"| vs scVI n={p.get('n_paired',0):4d} Δ={p.get('delta','-')} "
              f"CI={p.get('delta_ci95','-')}", flush=True)
    print(f"\nwrote {od}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())