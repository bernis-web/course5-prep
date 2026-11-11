"""oPCA 正式配对检验（用粗类空间 KNN 的真实产物，不是重映射）

为什么要单独写：
    `scripts/pairwise_corrected.py` 里的 oPCA 列是由 `exact` 层重映射得到的，
    而 oPCA 官方的 coarse 层是**在粗类标签空间里另跑一次 KNN**产出的
    （`scripts/ortholog_pca_dcs_v3_fixkey.py:285-291`），两者不等价。
    本脚本改用真正跑过粗类 KNN 的逐细胞产物：
        results/mapping-v2-20261111/rerun-v2/predictions/coarse_<dir>.json
    这样 oPCA 与 scVI / SATURN 才是同一个口径下的公平比较。

口径：
    - coarse 标签空间，union macro-F1（真实 ∪ 预测，多预测类 F1=0）；
    - oPCA / scVI 用各自逐细胞粗类预测；SATURN 用修正后约定（真值→目标、预测→源）+ v2 映射；
    - 配对：只在与对照方法**共享的 query 细胞**上比；
    - bootstrap 2000 次，95% CI。

输出：results/pairwise-20261111/opca_official_paired.json / .md
"""
from __future__ import annotations

import csv
import gzip
import io
import json
import os
import sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
OUTDIR = ROOT / "results" / "pairwise-20261111"
OPCA_PRED = ROOT / "results" / "mapping-v2-20261111" / "rerun-v2" / "predictions"
SCVI_PRED = ROOT / "results" / "phase-20261019" / "scvi-cross-species" / "predictions"
SATURN_PAYLOAD = ROOT / "results" / "pilot-v1" / "saturn-v99" / "raw" / "recovered-20261001" / "payloads"
MAP_TSV = Path(os.environ.get("MAP_TSV", str(ROOT / "config" / "heart-celltype-map-v2.tsv")))
NB = 2000
RNG = np.random.RandomState(20261111)

SRC = {"human->mouse": ("human", "mouse"), "mouse->human": ("mouse", "human"),
       "human->zebrafish": ("human", "zebrafish"), "zebrafish->human": ("zebrafish", "human"),
       "mouse->zebrafish": ("mouse", "zebrafish"), "zebrafish->mouse": ("zebrafish", "mouse")}
DIRCN = {"human->mouse": "人→鼠", "mouse->human": "鼠→人",
         "human->zebrafish": "人→斑马鱼", "zebrafish->human": "斑马鱼→人",
         "mouse->zebrafish": "鼠→斑马鱼", "zebrafish->mouse": "斑马鱼→鼠"}
CODE = {"human": "hu", "mouse": "mo", "zebrafish": "zf"}
SAT = {"human->mouse": "p6_coarse_human_to_mouse", "mouse->human": "p1_coarse_mouse_to_human",
       "human->zebrafish": "p3_coarse_human_to_zebrafish", "zebrafish->human": "p2_coarse_zebrafish_to_human",
       "mouse->zebrafish": "p5_coarse_mouse_to_zebrafish", "zebrafish->mouse": "p4_coarse_zebrafish_to_mouse"}
SCV = {"human->mouse": "coarse_hu_to_mo", "mouse->human": "coarse_mo_to_hu",
       "human->zebrafish": "coarse_hu_to_zf", "zebrafish->human": "coarse_zf_to_hu",
       "mouse->zebrafish": "coarse_mo_to_zf", "zebrafish->mouse": "coarse_zf_to_mo"}


def load_mapping():
    m = {}
    for row in csv.DictReader(open(MAP_TSV, encoding="utf-8-sig", newline=""), delimiter="\t"):
        m[(row["source_species"].strip(), row["source_label"].strip())] = (
            row["coarse_level"].strip(), row["mapping_status"].strip())
    return m


def to_coarse(sp, lab, mapping):
    h = mapping.get((sp, str(lab).strip()))
    if not h:
        return None
    c, s = h
    return c if (s == "active" and c) else None


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


def norm(name):
    return "".join(c for c in name if c.isalnum())


def load_opca(dr):
    """真正跑过粗类 KNN 的逐细胞产物。

    注意文件命名：rerun-v2 用的是**全名** coarse_human_to_mouse.json，
    不是 scVI 那种 hu_to_mo 缩写——用 norm() 去掉下划线后匹配。
    """
    want = norm("coarse_" + dr.replace("->", "_to_") + ".json")
    for f in OPCA_PRED.iterdir():
        if norm(f.name) == want:
            out = {}
            for r in json.loads(f.read_text(encoding="utf-8")):
                if not r.get("included"):
                    continue
                out[r["prefixed_barcode"]] = (r["truth"], r["prediction"])
            return out
    return {}


def load_scvi(dr):
    p = SCVI_PRED / (SCV[dr] + ".json")
    if not p.exists():
        return {}
    out = {}
    for r in json.loads(p.read_text(encoding="utf-8")):
        if not r.get("included", True):
            continue
        out[r["prefixed_barcode"]] = (r["truth"], r["prediction"])
    return out


def load_saturn(dr, mapping):
    s, t = SRC[dr]
    p = SATURN_PAYLOAD / (SAT[dr] + ".json.json.gz")
    if not p.exists():
        return {}
    rows = json.loads(gzip.open(p, "rb").read().decode("utf-8"))
    out = {}
    for r in rows:
        if r[3] != 1:
            continue
        ct = to_coarse(t, r[1], mapping)     # 真值 → 目标物种（修正后）
        if not ct:
            continue
        cp = to_coarse(s, r[2], mapping)     # 预测 → 源物种（修正后）
        out[r[0]] = (ct, cp if cp else "<not_in_coarse>")
    return out


def paired(truth, a, b):
    n = len(truth)
    d0 = mf1(truth, a) - mf1(truth, b)
    deltas = []
    for _ in range(NB):
        idx = RNG.randint(0, n, n)
        t = [truth[i] for i in idx]
        aa = [a[i] for i in idx]
        bb = [b[i] for i in idx]
        deltas.append(mf1(t, aa) - mf1(t, bb))
    lo, hi = float(np.percentile(deltas, 2.5)), float(np.percentile(deltas, 97.5))
    return {"n": n, "mf1_a": round(mf1(truth, a), 4), "mf1_b": round(mf1(truth, b), 4),
            "delta": round(d0, 4), "delta_se": round(float(np.std(deltas, ddof=1)), 4),
            "ci95": [round(lo, 4), round(hi, 4)],
            "significant_at_95": bool((lo > 0) or (hi < 0))}


def main() -> int:
    mapping = load_mapping()
    res = {"date": "2026-11-11",
           "purpose": "oPCA 正式配对检验（用粗类 KNN 真实产物，非重映射）",
           "opca_source": "results/mapping-v2-20261111/rerun-v2/predictions/coarse_*.json",
           "mapping": str(MAP_TSV.relative_to(ROOT)).replace("\\", "/"),
           "comparisons": {}}
    lines = ["# oPCA 正式配对检验", "",
             "> oPCA 用 `rerun-v2/predictions/coarse_*.json`（真正跑过粗类 KNN 的逐细胞产物），",
             "> 与 scVI / SATURN 同口径。union macro-F1，配对 2000 次 bootstrap。", "",
             "| 方向 | A vs B | n | A mf1 | B mf1 | Δ | 95% CI | 显著 |",
             "|---|---|---|---|---|---|---|---|"]

    for dr in SRC:
        op, sc, sa = load_opca(dr), load_scvi(dr), load_saturn(dr, mapping)
        store = {}
        for A, B, la, lb in (("opca", "scVI", op, sc), ("opca", "saturn_v99", op, sa)):
            if not la or not lb:
                continue
            shared = [bc for bc in la if bc in lb]
            if not shared:
                continue
            truth = [la[bc][0] for bc in shared]
            va = [la[bc][1] for bc in shared]
            vb = [lb[bc][1] for bc in shared]
            r = paired(truth, va, vb)
            store[f"{A}_vs_{B}"] = r
            flag = "**SIG**" if r["significant_at_95"] else "ns"
            lines.append("| {} | {} vs {} | {} | {} | {} | {:+} | [{:+}, {:+}] | {} |".format(
                DIRCN[dr], A, B, r["n"], r["mf1_a"], r["mf1_b"], r["delta"],
                r["ci95"][0], r["ci95"][1], flag))
            print(f"{DIRCN[dr]:7s} {A:5s} vs {B:10s} n={r['n']:5d} {r['mf1_a']:.4f} vs "
                  f"{r['mf1_b']:.4f} Δ={r['delta']:+.4f} CI[{r['ci95'][0]:+.4f},{r['ci95'][1]:+.4f}] {flag}",
                  flush=True)
        if store:
            res["comparisons"][dr] = store

    OUTDIR.mkdir(parents=True, exist_ok=True)
    (OUTDIR / "opca_official_paired.json").write_text(
        json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    (OUTDIR / "opca_official_paired.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\nwrote", OUTDIR / "opca_official_paired.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
