"""配对检验·个体级复检：显著性判断在正确的重抽样单位下还成立吗？

背景：
    `scripts/pairwise_corrected.py` 与 `scripts/pairwise_opca_official.py` 的配对检验
    用的是**逐细胞** bootstrap。而 `scripts/donor_bootstrap.py` 已证明
    个体级 SE 是细胞级的 **1.47–3.88 倍** → 那些「显著」结论可能站不住。

本脚本把同样的配对检验换成**个体级整群重抽样**（评估侧物种的 donor / orig.ident），
逐方向复检 Δ 的 95% CI 是否仍排除 0。

对比对象（都用 v2 映射）：
    opca    vs scVI       ← 近缘打平 / 远缘 scVI 胜 的依据
    opca    vs saturn     ← SATURN 是否真的全输
    saturn  vs scVI

输出：results/pairwise-20261111/pairwise_donor_level.{json,md}
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
OPCA = ROOT / "results" / "mapping-v2-20261111" / "rerun-v2" / "predictions"
SCVI = ROOT / "results" / "phase-20261019" / "scvi-cross-species" / "predictions"
SAT = ROOT / "results" / "pilot-v1" / "saturn-v99" / "raw" / "recovered-20261001" / "payloads"
MAP = ROOT / "config" / "heart-celltype-map-v2.tsv"
OUTDIR = ROOT / "results" / "pairwise-20261111"
NB = 2000
RNG = np.random.RandomState(20261111)

SRC = {"human->mouse": ("human", "mouse"), "mouse->human": ("mouse", "human"),
       "human->zebrafish": ("human", "zebrafish"), "zebrafish->human": ("zebrafish", "human"),
       "mouse->zebrafish": ("mouse", "zebrafish"), "zebrafish->mouse": ("zebrafish", "mouse")}
DIRCN = {k: v for k, v in [("human->mouse", "人→鼠"), ("mouse->human", "鼠→人"),
                           ("human->zebrafish", "人→斑马鱼"), ("zebrafish->human", "斑马鱼→人"),
                           ("mouse->zebrafish", "鼠→斑马鱼"), ("zebrafish->mouse", "斑马鱼→鼠")]}
CODE = {"human": "hu", "mouse": "mo", "zebrafish": "zf"}
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


def load_opca(dr):
    want = norm("coarse_" + dr.replace("->", "_to_") + ".json")
    for f in OPCA.iterdir():
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
    res = {"date": "2026-11-11", "resamples": NB, "unit": "个体级整群重抽样",
           "why": "细胞级 SE 被证明低估 1.47–3.88 倍，显著性判断必须复检",
           "comparisons": {}}
    lines = ["# 配对检验·个体级复检", "",
             "> 重抽样单位改为**评估侧物种的个体**（human→donor，mouse/zebrafish→orig.ident）。",
             "> 用来检验：细胞级 bootstrap 下那些「显著」结论，换正确单位后还成立吗。", "",
             "| 方向 | A vs B | 聚类数 | n | Δ | 个体级 SE | 95% CI | 显著 |",
             "|---|---|---|---|---|---|---|---|"]

    ccache = {}
    for dr in SRC:
        tgt = SRC[dr][1]
        if tgt not in ccache:
            ccache[tgt] = clusters(tgt)
        cmap = ccache[tgt]
        pre = PREFIX[tgt]
        op, sc, sa = load_opca(dr), load_scvi(dr), load_saturn(dr, m)
        srcs = {"opca": op, "scVI": sc, "saturn": sa}
        store = {}
        for A, B in (("opca", "scVI"), ("saturn", "scVI"), ("opca", "saturn")):
            la, lb = srcs[A], srcs[B]
            if not la or not lb:
                continue
            shared = [bc for bc in la if bc in lb]
            if not shared:
                continue
            truth, va, vb, cl = [], [], [], []
            for bc in shared:
                truth.append(la[bc][0])
                va.append(la[bc][1])
                vb.append(lb[bc][1])
                b2 = bc[len(pre):] if bc.startswith(pre) else bc
                cl.append(cmap.get(b2, "NA"))
            r = paired_donor(truth, va, vb, cl)
            store[f"{A}_vs_{B}"] = r
            flag = "**SIG**" if r["significant_at_95"] else "ns"
            lines.append(f"| {DIRCN[dr]} | {A} vs {B} | {r['n_clusters']} | {r['n']} | "
                         f"{r['delta']:+.4f} | {r['se']:.4f} | "
                         f"[{r['ci95'][0]:+.4f}, {r['ci95'][1]:+.4f}] | {flag} |")
            print(f"{DIRCN[dr]:7s} {A:6s}vs{B:6s} 聚类={r['n_clusters']:3d} n={r['n']:5d} "
                  f"Δ={r['delta']:+.4f} SE={r['se']:.4f} "
                  f"CI[{r['ci95'][0]:+.4f},{r['ci95'][1]:+.4f}] {flag}", flush=True)
        if store:
            res["comparisons"][dr] = store

    OUTDIR.mkdir(parents=True, exist_ok=True)
    (OUTDIR / "pairwise_donor_level.json").write_text(
        json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    (OUTDIR / "pairwise_donor_level.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\nwrote", OUTDIR / "pairwise_donor_level.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
