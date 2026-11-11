"""配对检验·inductive oPCA 口径下复核：结论还成立吗？

背景（2026-11-11 第 75-77 轮）：
    发现 `ortholog_pca_dcs_v3_fixkey.py:278-282` 的 PCA 在「源+目标」上联合拟合
    → **我们的 oPCA 是 transductive 的**。改成 inductive 后，
    鼠→人 0.7369→**0.5144**（−0.2225）、斑马鱼→人 0.2788→**0.0949**（−0.1839）。

    → 所以**基于 transductive oPCA 的配对结论必须在 inductive 口径下复核**
    （第 77 轮列入引用纪律的连带待办）。

本脚本：把 oPCA 换成 inductive 变体，与 scVI / saturn 做个体级配对检验，
并与 transductive 口径下的结果并列，看结论是否翻转。

口径：coarse、union macro-F1、strict_cell；个体级整群重抽样 2000 次。
输出：results/pairwise-20261111/pairwise_inductive.json / .md
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
OPCA_T = ROOT / "results" / "mapping-v2-20261111" / "rerun-v2" / "predictions"
OPCA_I = ROOT / "results" / "transductive-20261111" / "inductive-variant" / "predictions"
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
SCV = {"human->mouse": "coarse_hu_to_mo", "mouse->human": "coarse_mo_to_hu",
       "human->zebrafish": "coarse_hu_to_zf", "zebrafish->human": "coarse_zf_to_hu",
       "mouse->zebrafish": "coarse_mo_to_zf", "zebrafish->mouse": "coarse_zf_to_mo"}
SATNAME = {"human->mouse": "p6_coarse_human_to_mouse", "mouse->human": "p1_coarse_mouse_to_human",
           "human->zebrafish": "p3_coarse_human_to_zebrafish", "zebrafish->human": "p2_coarse_zebrafish_to_human",
           "mouse->zebrafish": "p5_coarse_mouse_to_zebrafish", "zebrafish->mouse": "p4_coarse_zebrafish_to_mouse"}


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
    p = SCVI / (SCV[dr] + ".json")
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


def paired(truth, a, b, clus):
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
           "purpose": "inductive oPCA 口径下的配对复核（transductive 结论是否成立）",
           "opca_t": "results/mapping-v2-20261111/rerun-v2/predictions",
           "opca_i": "results/transductive-20261111/inductive-variant/predictions",
           "comparisons": {}}
    lines = ["# 配对检验·inductive oPCA 口径复核", "",
             "> oPCA 换成 **inductive** 变体（PCA 只用源细胞拟合），scVI / SATURN 不变；",
             "> 重抽样单位仍为**个体**。目的是检查 transductive 下的结论是否成立。", "",
             "| 方向 | 比较 | 聚类 | transductive Δ | 显著 | **inductive Δ** | **显著** | 是否翻转 |",
             "|---|---|---|---|---|---|---|---|"]
    flips = []
    ccache = {}
    for dr in SRC:
        tgt = SRC[dr][1]
        if tgt not in ccache:
            ccache[tgt] = clusters(tgt)
        cmap = ccache[tgt]; pre = PREFIX[tgt]
        sc, sa = load_scvi(dr), load_saturn(dr, m)
        store = {}
        for tag, base in (("t", OPCA_T), ("i", OPCA_I)):
            op = load_opca(dr, base)
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
                store[f"{tag}|opca_vs_{B}"] = paired(truth, va, vb, cl)
        for B in ("scVI", "saturn"):
            t = store.get(f"t|opca_vs_{B}"); i = store.get(f"i|opca_vs_{B}")
            if not t or not i:
                continue
            flip = t["significant_at_95"] != i["significant_at_95"]
            if flip:
                flips.append({"direction": DIRCN[dr], "vs": B,
                              "transductive_sig": t["significant_at_95"],
                              "inductive_sig": i["significant_at_95"],
                              "transductive_delta": t["delta"], "inductive_delta": i["delta"]})
            lines.append(f"| {DIRCN[dr]} | oPCA vs {B} | {i['n_clusters']} | {t['delta']:+.4f} | "
                         f"{'SIG' if t['significant_at_95'] else 'ns'} | "
                         f"**{i['delta']:+.4f}** | **{'SIG' if i['significant_at_95'] else 'ns'}** | "
                         f"{'★翻转' if flip else '—'} |")
            print(f"{DIRCN[dr]:8s} opca vs {B:7s} transductive Δ={t['delta']:+.4f} "
                  f"({'SIG' if t['significant_at_95'] else 'ns'})  "
                  f"inductive Δ={i['delta']:+.4f} ({'SIG' if i['significant_at_95'] else 'ns'})  "
                  f"{'★翻转' if flip else ''}", flush=True)
        res["comparisons"][dr] = store

    res["flips"] = flips
    lines += ["", "## 结论", ""]
    if flips:
        lines.append(f"**{len(flips)} 条结论在 inductive 口径下翻转：**")
        for f in flips:
            lines.append(f"- {f['direction']} oPCA vs {f['vs']}："
                         f"transductive {'显著' if f['transductive_sig'] else '不显著'}"
                         f"（Δ{f['transductive_delta']:+.4f}）→ "
                         f"inductive {'显著' if f['inductive_sig'] else '不显著'}"
                         f"（Δ{f['inductive_delta']:+.4f}）")
    else:
        lines.append("**没有结论翻转。** → oPCA 与 scVI/SATURN 的比较**对拟合方式稳健**。")

    OUTDIR.mkdir(parents=True, exist_ok=True)
    (OUTDIR / "pairwise_inductive.json").write_text(
        json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    (OUTDIR / "pairwise_inductive.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\n翻转条数: {len(flips)}")
    print("wrote", OUTDIR / "pairwise_inductive.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
