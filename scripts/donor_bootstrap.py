"""供体级 cluster bootstrap：修正「逐细胞重抽样导致 CI 过窄」

为什么做（Claude 咨询第 9 条，标为「投稿前必须」）：
    我们此前所有置信区间都是**逐细胞**重抽样。但同一个供体/样本里的细胞彼此不独立
    （同一颗心脏、同一只动物、同一批建库），逐细胞重抽样等于假装有 n_q 个独立样本，
    **系统性低估不确定性**，给出的 CI 偏窄、p 值偏乐观。

正确做法：**以个体（供体 / 取样个体）为整群重抽样单位**，保持每个个体的细胞一起进出。

分层字段（本地 h5ad 实测）：
    human      donor       22 类
    mouse      orig.ident   4 类（MouseHeart1-4）
    zebrafish  orig.ident  15 类（含 Atrium / BA / Heart）
→ 各方向**评估侧（query）**的聚类数不同，必须逐个报出来，聚类太少的方向要标注不可靠。

口径：coarse、union macro-F1、strict_cell；每方向 2000 次 cluster bootstrap。
输出：results/bootstrap-donor-20261111/donor_bootstrap.{json,md}
"""
from __future__ import annotations

import io
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(r"D:\projects\course5-prep")
PRED = ROOT / "results" / "mapping-v2-20261111" / "rerun-v2" / "predictions"
OUTDIR = ROOT / "results" / "bootstrap-donor-20261111"
NB = 2000
RNG = np.random.RandomState(20261111)

# 方向 -> (源, 目标)；评估侧 = 目标
SRC = {"human->mouse": ("human", "mouse"), "mouse->human": ("mouse", "human"),
       "human->zebrafish": ("human", "zebrafish"), "zebrafish->human": ("zebrafish", "human"),
       "mouse->zebrafish": ("mouse", "zebrafish"), "zebrafish->mouse": ("zebrafish", "mouse")}
DIRCN = {"human->mouse": "人→鼠", "mouse->human": "鼠→人",
         "human->zebrafish": "人→斑马鱼", "zebrafish->human": "斑马鱼→人",
         "mouse->zebrafish": "鼠→斑马鱼", "zebrafish->mouse": "斑马鱼→鼠"}
# 每个物种用哪个 obs 字段当聚类单位
CLUSTER_FIELD = {"human": "donor", "mouse": "orig.ident", "zebrafish": "orig.ident"}
PREFIX = {"human": "hu|", "mouse": "mo|", "zebrafish": "zf|"}


def mf1(truth, pred):
    t, p, tp = Counter(), Counter(), Counter()
    for a, b in zip(truth, pred):
        t[a] += 1
        p[b] += 1
        if a == b:
            tp[a] += 1
    fs = []
    for c in set(t) | set(p):
        pr = tp[c] / p[c] if p[c] else 0.0
        rc = tp[c] / t[c] if t[c] else 0.0
        fs.append(2 * pr * rc / (pr + rc) if (pr + rc) else 0.0)
    return sum(fs) / len(fs) if fs else 0.0


def load_clusters(sp: str) -> dict:
    """barcode(去前缀) -> 聚类标签。"""
    import h5py
    f = ROOT / f"local_{sp}_s.h5ad"
    d = h5py.File(f, "r")
    obs = d["obs"]
    idx_key = obs.attrs["_index"]
    bcs = [x.decode() if isinstance(x, bytes) else str(x) for x in obs[idx_key][:]]
    col = CLUSTER_FIELD[sp]
    g = obs[col]
    if "codes" in g:                      # categorical
        codes = g["codes"][:]
        cats = [x.decode() if isinstance(x, bytes) else str(x) for x in g["categories"][:]]
        labs = [cats[c] if c >= 0 else "NA" for c in codes]
    else:
        labs = [x.decode() if isinstance(x, bytes) else str(x) for x in g[:]]
    d.close()
    return dict(zip(bcs, labs))


def main() -> int:
    res = {"date": "2026-11-11",
           "purpose": "供体级（个体级）cluster bootstrap，修正逐细胞重抽样导致的 CI 过窄",
           "cluster_field": CLUSTER_FIELD,
           "resamples": NB,
           "directions": {}}
    lines = ["# 供体级 cluster bootstrap（oPCA，v2 映射，coarse）", "",
             "> **为什么**：逐细胞重抽样假装细胞彼此独立，会低估不确定性。",
             "> 本表以**个体**为整群重抽样单位（人用 `donor`，鼠/鱼用 `orig.ident`）。", "",
             "| 方向 | 评估侧 | 聚类数 | n_q | mf1 | 细胞级 SE | **个体级 SE** | 倍数 |",
             "|---|---|---|---|---|---|---|---|"]

    caches = {}
    for dr, (src, tgt) in SRC.items():
        want = "".join(c for c in f"coarse_{src}_to_{tgt}.json" if c.isalnum())
        pf = None
        for f in PRED.iterdir():
            if "".join(c for c in f.name if c.isalnum()) == want:
                pf = f
                break
        if pf is None:
            print(f"{DIRCN[dr]}: 缺预测文件")
            continue
        rows = json.loads(pf.read_text(encoding="utf-8"))
        keep = [r for r in rows if r.get("included")]
        if tgt not in caches:
            caches[tgt] = load_clusters(tgt)
        cmap = caches[tgt]
        pre = PREFIX[tgt]

        truth, pred, clus = [], [], []
        for r in keep:
            bc = r["prefixed_barcode"]
            bc = bc[len(pre):] if bc.startswith(pre) else bc
            truth.append(r["truth"])
            pred.append(r["prediction"])
            clus.append(cmap.get(bc, "NA"))

        groups = defaultdict(list)
        for i, c in enumerate(clus):
            groups[c].append(i)
        keys = list(groups)
        n_cell = len(truth)

        # 点估计
        d0 = mf1(truth, pred)
        # 细胞级（对照）
        cell_deltas = []
        for _ in range(NB):
            idx = RNG.randint(0, n_cell, n_cell)
            t = [truth[i] for i in idx]
            p = [pred[i] for i in idx]
            cell_deltas.append(mf1(t, p))
        # 个体级
        ind_deltas = []
        for _ in range(NB):
            pick = RNG.choice(len(keys), len(keys), replace=True)
            idx = []
            for j in pick:
                idx.extend(groups[keys[j]])
            t = [truth[i] for i in idx]
            p = [pred[i] for i in idx]
            ind_deltas.append(mf1(t, p))

        se_cell = float(np.std(cell_deltas, ddof=1))
        se_ind = float(np.std(ind_deltas, ddof=1))
        ratio = se_ind / se_cell if se_cell else None
        rec = {"query_species": tgt, "cluster_field": CLUSTER_FIELD[tgt],
               "n_clusters": len(keys), "n_q": n_cell, "mf1": round(d0, 4),
               "se_cell_level": round(se_cell, 4), "se_individual_level": round(se_ind, 4),
               "se_ratio": round(ratio, 3) if ratio else None,
               "cluster_sizes": {k: len(v) for k, v in sorted(groups.items())},
               "note": ("聚类数 <5，个体级 CI 不可靠" if len(keys) < 5 else "")}
        res["directions"][dr] = rec
        lines.append(f"| {DIRCN[dr]} | {tgt} | {len(keys)} | {n_cell} | {rec['mf1']} | "
                     f"{se_cell:.4f} | **{se_ind:.4f}** | {ratio:.2f}× |" if ratio else "")
        print(f"{DIRCN[dr]:7s} 评估侧={tgt:9s} 聚类={len(keys):3d} n_q={n_cell:5d} "
              f"mf1={d0:.4f} SE_cell={se_cell:.4f} SE_ind={se_ind:.4f} "
              f"倍数={ratio:.2f}×" + (f"  {rec['note']}" if rec['note'] else ""), flush=True)

    OUTDIR.mkdir(parents=True, exist_ok=True)
    (OUTDIR / "donor_bootstrap.json").write_text(
        json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    (OUTDIR / "donor_bootstrap.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\nwrote", OUTDIR / "donor_bootstrap.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
