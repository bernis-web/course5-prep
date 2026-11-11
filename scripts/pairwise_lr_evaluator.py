"""配对检验·LR 评估器下复检：换评估器会不会改变 oPCA vs scVI 的结论？

背景：
    `scripts/evaluator_ablation.py` 已证明换评估器（KNN-15 → logistic regression）
    会让 oPCA 的 accuracy 变动 **−0.1914 ~ +0.1309**，其中
    斑马鱼→鼠 降 0.19、斑马鱼→人 升 0.13、人→斑马鱼 升 0.12。
    → 那么基于 KNN-15 的配对结论（`pairwise_donor_level.json`）在 LR 下还成立吗？

本脚本把 oPCA 换成 **LR 评估器**，重做 `opca vs scVI` 与 `opca vs saturn` 的
个体级配对检验，逐方向对比结论是否翻转。

口径：coarse、union macro-F1、strict_cell；个体级整群重抽样 2000 次（评估侧物种的 donor/orig.ident）。
输出：results/pairwise-20261111/pairwise_lr_evaluator.{json,md}
"""
from __future__ import annotations

import csv
import gzip
import io
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(r"D:\projects\course5-prep")
OPCA_LR = ROOT / "results" / "evaluator-20261111" / "lr-variant" / "predictions"
OPCA_KNN = ROOT / "results" / "mapping-v2-20261111" / "rerun-v2" / "predictions"
SCVI = ROOT / "results" / "phase-20261019" / "scvi-cross-species" / "predictions"
SAT = ROOT / "results" / "pilot-v1" / "saturn-v99" / "raw" / "recovered-20261001" / "payloads"
MAP = ROOT / "config" / "heart-celltype-map-v2.tsv"
OUTDIR = ROOT / "results" / "pairwise-20261111"
NB = 2000
RNG = np.random.RandomState(20261111)

SRC = {"human->mouse": ("human", "mouse"), "mouse->human": ("mouse", "human"),
       "human->zebrafish": ("human", "zebrafish"), "zebrafish->human": ("zebrafish", "human"),
       "mouse->zebrafish": ("mouse", "zebrafish"), "zebrafish->mouse": ("zebrafish", "mouse")}
DIRCN = {"human->mouse": "人→鼠", "mouse->human": "鼠→人",
         "human->zebrafish": "人→斑马鱼", "zebrafish->human": "斑马鱼→人",
         "mouse->zebrafish": "鼠→斑马鱼", "zebrafish->mouse": "斑马鱼→鼠"}
CLUSTER_FIELD = {"human": "donor", "mouse": "orig.ident", "zebrafish": "orig.ident"}
PREFIX = {"human": "hu|", "mouse": "mo|", "zebrafish": "zf|"}
SATNAME = {"human->mouse": "p6_coarse_human_to_mouse", "mouse->human": "p1_coarse_mouse_to_human",
           "human->zebrafish": "p3_coarse_human_to_zebrafish", "zebrafish->human": "p2_coarse_zebrafish_to_human",
           "mouse->zebrafish": "p5_coarse_mouse_to_zebrafish", "zebrafish->mouse": "p4_coarse_zebrafish_to_mouse"}
SCVNAME = {"human->mouse": "coarse_hu_to_mo", "mouse->human": "coarse_mo_to_hu",
           "human->zebrafish": "coarse_hu_to_zf", "zebrafish->human": "coarse_zf_to_hu",
           "mouse->zebrafish": "coarse_mo_to_zf", "zebrafish->mouse": "coarse_zf_to_mo"}


def load_map():
    m = {}
    for row in csv.DictReader(open(MAP, encoding="utf-8-sig", newline=""), delimiter="\t"):
        m[(row["source_species"].strip(), row["source_label"].strip())] = (
            row["coarse_level"].strip(), row["mapping_status"].strip())
    return m


def to_coarse(sp, lab, m):
    h = m.get((sp, str(lab).strip()))
    if not h:
        return None
    c, s = h
    return c if (s == "active" and c) else None


def mf1(t, p):
    tc, pc, tpc = Counter(t), Counter(p), Counter()
    for a, b in zip(t, p):
        if a == b:
            tpc[a] += 1
    fs = []
    for c in set(tc) | set(pc):
        pr = tpc[c] / pc[c] if pc[c] else 0.0
        rc = tpc[c] / tc[c] if tc[c] else 0.0
        fs.append(2 * pr * rc / (pr + rc) if (pr + rc) else 0.0)
    return sum(fs) / len(fs) if fs else 0.0


def clusters(sp):
    import h5py
    d = h5py.File(ROOT / f"local_{sp}_s.h5ad", "r")
    obs = d["obs"]
    bcs = [x.decode() if isinstance(x, bytes) else str(x) for x in obs[obs.attrs["_index"]][:]]
    g = obs[CLUSTER_FIELD[sp]]
    if "codes" in g:
        cats = [x.decode() if isinstance(x, bytes) else str(x) for x in g["categories"][:]]
        labs = [cats[c] if c >= 0 else "NA" for c in g["codes"][:]]
    else:
        labs = [x.decode() if isinstance(x, bytes) else str(x) for x in g[:]]
    d.close()
    return dict(zip(bcs, labs))


def norm(s):
    return "".join(c for c in s if c.isalnum())


def load_opca(dr, base):
    want = norm("coarse_" + dr.replace("->", "_to_") + ".json")
    for f in base.iterdir():
        if norm(f.name) == want:
            return {r["prefixed_barcode"]: (r["truth"], r["prediction"])
                    for r in json.loads(f.read_text(encoding="utf-8")) if r.get("included")}
    return {}


def load_scvi(dr):
    p = SCVI / (SCVNAME[dr] + ".json")
    if not p.exists():
        return {}
    return {r["prefixed_barcode"]: (r["truth"], r["prediction"])
            for r in json.loads(p.read_text(encoding="utf-8")) if r.get("included", True)}


def load_saturn(dr, m):
    s, t = SRC[dr]
    p = SAT / (SATNAME[dr] + ".json.json.gz")
    if not p.exists():
        return {}
    out = {}
    for r in json.loads(gzip.open(p, "rb").read().decode("utf-8")):
        if r[3] != 1:
            continue
        ct = to_coarse(t, r[1], m)
        if not ct:
            continue
        cp = to_coarse(s, r[2], m)
        out[r[0]] = (ct, cp if cp else "<not_in_coarse>")
    return out


def paired_donor(truth, a, b, clus):
    groups = defaultdict(list)
    for i, c in enumerate(clus):
        groups[c].append(i)
    keys = list(groups)
    d0 = mf1(truth, a) - mf1(truth, b)
    ds = []
    for _ in range(NB):
        idx = []
        for j in RNG.choice(len(keys), len(keys), replace=True):
            idx.extend(groups[keys[j]])
        t = [truth[i] for i in idx]
        aa = [a[i] for i in idx]
        bb = [b[i] for i in idx]
        ds.append(mf1(t, aa) - mf1(t, bb))
    lo, hi = float(np.percentile(ds, 2.5)), float(np.percentile(ds, 97.5))
    return {"n": len(truth), "n_clusters": len(keys), "delta": round(d0, 4),
            "se": round(float(np.std(ds, ddof=1)), 4), "ci95": [round(lo, 4), round(hi, 4)],
            "significant_at_95": bool(lo > 0 or hi < 0)}


def main():
    m = load_map()
    res = {"date": "2026-11-11", "resamples": NB,
           "purpose": "换评估器（KNN-15 → LR）后，配对结论是否改变",
           "opca_source_lr": "results/evaluator-20261111/lr-variant/predictions",
           "opca_source_knn": "results/mapping-v2-20261111/rerun-v2/predictions",
           "unit": "个体级整群重抽样",
           "comparisons": {}}
    lines = ["# 配对检验·LR 评估器下复检", "",
             "> oPCA 换成 logistic regression（官方评估器），scVI/SATURN 不变；",
             "> 重抽样单位仍为**个体**（评估侧 donor / orig.ident）。", "",
             "| 方向 | 比较 | 聚类 | KNN 下 Δ | KNN 显著 | **LR 下 Δ** | **LR 显著** | 是否翻转 |",
             "|---|---|---|---|---|---|---|---|"]

    ccache = {}
    flips = []
    for dr in SRC:
        tgt = SRC[dr][1]
        if tgt not in ccache:
            ccache[tgt] = clusters(tgt)
        cmap = ccache[tgt]; pre = PREFIX[tgt]
        sc, sa = load_scvi(dr), load_saturn(dr, m)
        variants = {
            "knn": load_opca(dr, OPCA_KNN),
            "lr": load_opca(dr, OPCA_LR),
        }
        store = {}
        for tag, op in variants.items():
            if not op:
                continue
            for B, lb in (("scVI", sc), ("saturn", sa)):
                if not lb:
                    continue
                shared = [bc for bc in op if bc in lb]
                if not shared:
                    continue
                truth, va, vb, cl = [], [], [], []
                for bc in shared:
                    truth.append(op[bc][0]); va.append(op[bc][1]); vb.append(lb[bc][1])
                    b2 = bc[len(pre):] if bc.startswith(pre) else bc
                    cl.append(cmap.get(b2, "NA"))
                store[f"{tag}|opca_vs_{B}"] = paired_donor(truth, va, vb, cl)

        for B in ("scVI", "saturn"):
            k = store.get(f"knn|opca_vs_{B}")
            l = store.get(f"lr|opca_vs_{B}")
            if not k or not l:
                continue
            flip = (k["significant_at_95"] != l["significant_at_95"])
            if flip:
                flips.append({"direction": DIRCN[dr], "vs": B,
                              "knn_sig": k["significant_at_95"], "lr_sig": l["significant_at_95"]})
            lines.append(
                f"| {DIRCN[dr]} | oPCA vs {B} | {l['n_clusters']} | {k['delta']:+.4f} | "
                f"{'SIG' if k['significant_at_95'] else 'ns'} | **{l['delta']:+.4f}** | "
                f"**{'SIG' if l['significant_at_95'] else 'ns'}** | {'★翻转' if flip else '—'} |")
            print(f"{DIRCN[dr]:7s} opca vs {B:7s} 聚类={l['n_clusters']:3d} "
                  f"KNN Δ={k['delta']:+.4f} ({'SIG' if k['significant_at_95'] else 'ns'})  "
                  f"LR Δ={l['delta']:+.4f} ({'SIG' if l['significant_at_95'] else 'ns'})  "
                  f"{'★翻转' if flip else ''}", flush=True)
        res["comparisons"][dr] = store

    res["flips"] = flips
    lines += ["", "## 结论", ""]
    if flips:
        lines.append(f"**{len(flips)} 条结论在换评估器后翻转：**")
        for f in flips:
            lines.append(f"- {f['direction']} oPCA vs {f['vs']}："
                         f"KNN {'显著' if f['knn_sig'] else '不显著'} → "
                         f"LR {'显著' if f['lr_sig'] else '不显著'}")
    else:
        lines.append("**没有任何结论翻转。** → oPCA vs scVI/SATURN 的比较对评估器选择稳健。")

    OUTDIR.mkdir(parents=True, exist_ok=True)
    (OUTDIR / "pairwise_lr_evaluator.json").write_text(
        json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    (OUTDIR / "pairwise_lr_evaluator.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\n翻转条数: {len(flips)}")
    print("wrote", OUTDIR / "pairwise_lr_evaluator.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
