"""配对 bootstrap：SATURN vs scVI / oPCA（修正物种词表方向 + v2 映射）

为什么要重写：
    `scripts/saturn_vs_scvi_paired.py` 第 75 行写的是
        ct, cp = to_coarse(s, r[1]), to_coarse(t, r[2])
    即「真值查**源**物种词表、预测查**目标**物种词表」——**两边正好反了**。
    这是 `docs/reports/report-09-corrections-20261108.md` 记录的同一个 bug。
    正确约定：**真值 → 目标物种词表；预测 → 源物种词表**。
    同时旧脚本用的是 v1 映射表，现行为 v2 签认表。

    `results/bootstrap-20261030/pairwise.json` 里涉及 saturn_v99 的 10 条比较
    就是在旧约定下算出来的（见 `docs/execution/20261111-obsolete-numbers.md` 作废 3），
    因此需要本脚本重跑。

口径：
    - 标签空间 coarse；macro-F1 用 union 口径（真实 ∪ 预测，多预测的类 F1=0）；
    - 映射表 v2（可用 MAP_TSV 环境变量覆盖）；
    - 配对：只在**两种方法共享的 query 细胞**上比（同细胞配对检验）；
    - `strict_cell`：真值可映射的细胞全保留，预测不可映射记 `<not_in_coarse>`（算错）。

输出：
    results/pairwise-20261111/pairwise_corrected.json
    results/pairwise-20261111/pairwise_corrected.md
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
MAP_TSV = Path(os.environ.get("MAP_TSV", str(ROOT / "config" / "heart-celltype-map-v2.tsv")))
SATURN_PAYLOAD = ROOT / "results" / "pilot-v1" / "saturn-v99" / "raw" / "recovered-20261001" / "payloads"
CONF_DIR = ROOT / "results" / "pilot-v1" / "saturn-v99" / "raw" / "recovered-20261001" / "confusion"
SCVI_PRED = ROOT / "results" / "phase-20261019" / "scvi-cross-species" / "predictions"
OPCA_PRED = ROOT / "results" / "phase-20261010" / "opca-fixkey-recovered-20261015" / "predictions"
NB = 2000
RNG = np.random.RandomState(20261111)

SRC = {"human->mouse": ("human", "mouse"), "mouse->human": ("mouse", "human"),
       "human->zebrafish": ("human", "zebrafish"), "zebrafish->human": ("zebrafish", "human"),
       "mouse->zebrafish": ("mouse", "zebrafish"), "zebrafish->mouse": ("zebrafish", "mouse")}
DIRCN = {"human->mouse": "人→鼠", "mouse->human": "鼠→人",
         "human->zebrafish": "人→斑马鱼", "zebrafish->human": "斑马鱼→人",
         "mouse->zebrafish": "鼠→斑马鱼", "zebrafish->mouse": "斑马鱼→鼠"}
SAT = {"human->mouse": "p6_coarse_human_to_mouse", "mouse->human": "p1_coarse_mouse_to_human",
       "human->zebrafish": "p3_coarse_human_to_zebrafish", "zebrafish->human": "p2_coarse_zebrafish_to_human",
       "mouse->zebrafish": "p5_coarse_mouse_to_zebrafish", "zebrafish->mouse": "p4_coarse_zebrafish_to_mouse"}
SCV = {"human->mouse": "coarse_hu_to_mo", "mouse->human": "coarse_mo_to_hu",
       "human->zebrafish": "coarse_hu_to_zf", "zebrafish->human": "coarse_zf_to_hu",
       "mouse->zebrafish": "coarse_mo_to_zf", "zebrafish->mouse": "coarse_zf_to_mo"}
CODE = {"human": "hu", "mouse": "mo", "zebrafish": "zf"}


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


def load_sat(dr, mapping):
    """SATURN：**修正后**的方向 —— 真值查目标物种、预测查源物种。"""
    s, t = SRC[dr]
    p = SATURN_PAYLOAD / (SAT[dr] + ".json.json.gz")
    if not p.exists():
        return {}
    rows = json.loads(gzip.open(p, "rb").read().decode("utf-8"))
    out = {}
    for r in rows:
        if r[3] != 1:          # 只取 included 的细胞
            continue
        ct = to_coarse(t, r[1], mapping)      # ← 修正：目标物种
        if not ct:
            continue
        cp = to_coarse(s, r[2], mapping)      # ← 修正：源物种
        out[r[0]] = (ct, cp if cp else "<not_in_coarse>")
    return out


def _norm(name):
    return "".join(c for c in name if c.isalnum())


def load_scv(dr, mapping):
    s, t = SRC[dr]
    p = SCVI_PRED / (SCV[dr] + ".json")
    if not p.exists():
        return {}
    out = {}
    for r in json.loads(p.read_text(encoding="utf-8")):
        if not r.get("included", True):
            continue
        out[r["prefixed_barcode"]] = (r["truth"], r["prediction"])
    return out


def load_opca(dr, mapping):
    """oPCA：exact 层重映射（真值→目标、预测→源），与 saturn 同约定。"""
    s, t = SRC[dr]
    want = _norm(CODE[s] + CODE[t] + "json")
    for f in OPCA_PRED.iterdir():
        if _norm(f.name) != want:
            continue
        d = json.loads(f.read_text(encoding="utf-8"))
        out = {}
        for e in d.get("exact", []):
            ct = to_coarse(t, e["truth"], mapping)
            if not ct:
                continue
            cp = to_coarse(s, e["prediction"], mapping)
            out[e["prefixed_barcode"]] = (ct, cp if cp else "<not_in_coarse>")
        return out
    return {}


def load_sat_conf(dr, mapping):
    """SATURN：从 confusion/ 计数还原标签序列（约定 B）。

    为什么不用 payloads/：`scripts/pairwise_audit_gate.py` 实测 6 向里
    mouse->human、mouse->zebrafish 两向的 payload 给出 0.2147 / 0.3600，
    与 confusion 和权威表的 0.2566 / 0.4076 不一致；4 种标签位置/物种对调解释
    都无法同时满足 mf1 与 n —— 该目录不是同一次运行的一致产物。
    confusion 路径 6/6 复现权威值，故以它为准（代价：无 barcode，改用独立重抽样）。
    """
    src, tgt = SRC[dr]
    p = CONF_DIR / ("coarse_" + src + "_to_" + tgt + ".json")
    conf = json.loads(p.read_text(encoding="utf-8"))
    tr, pr = [], []
    for k, c in conf.items():
        tl, pl = k.split("=>")
        t = to_coarse(tgt, tl, mapping)      # 真值 → 目标物种
        if t is None:
            continue
        tr.extend([t] * c)
        pr.extend([(to_coarse(src, pl, mapping) or "__unmapped__")] * c)
    return tr, pr


def unpaired(ta, pa, tb, pb, label_a, label_b):
    """两法样本不共享细胞时的 Δ：各自独立重抽样，Δ = mf1(a) - mf1(b)。"""
    na, nb_ = len(ta), len(tb)
    d0 = mf1(ta, pa) - mf1(tb, pb)
    deltas = []
    for _ in range(NB):
        ia = RNG.randint(0, na, na)
        ib = RNG.randint(0, nb_, nb_)
        deltas.append(mf1([ta[i] for i in ia], [pa[i] for i in ia])
                      - mf1([tb[i] for i in ib], [pb[i] for i in ib]))
    lo, hi = float(np.percentile(deltas, 2.5)), float(np.percentile(deltas, 97.5))
    return {
        "n_a": na, "n_b": nb_,
        f"{label_a}_mf1": round(mf1(ta, pa), 4),
        f"{label_b}_mf1": round(mf1(tb, pb), 4),
        "delta": round(d0, 4),
        "delta_se": round(float(np.std(deltas, ddof=1)), 4),
        "delta_ci95": [round(lo, 4), round(hi, 4)],
        "significant_at_95": bool((lo > 0) or (hi < 0)),
        "pairing": "independent（非同批细胞）",
    }


def paired(truth, a, b, label_a, label_b):
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
    return {
        "n": n,
        f"{label_a}_mf1": round(mf1(truth, a), 4),
        f"{label_b}_mf1": round(mf1(truth, b), 4),
        "delta": round(d0, 4),
        "delta_se": round(float(np.std(deltas, ddof=1)), 4),
        "delta_ci95": [round(lo, 4), round(hi, 4)],
        "significant_at_95": bool((lo > 0) or (hi < 0)),
    }


def main() -> int:
    mapping = load_mapping()
    res = {
        "date": "2026-11-11",
        "purpose": "重跑配对检验：修正物种词表方向 + 换 v2 映射",
        "supersedes": "results/bootstrap-20261030/pairwise.json（涉 saturn_v99 的 10 条比较作废）",
        "convention": {
            "truth_side": "目标物种词表（修正前写成了源物种）",
            "pred_side": "源物种词表（修正前写成了目标物种）",
            "macro_f1": "union（真实∪预测，多预测类 F1=0）",
            "pairing": "saturn 涉及项为独立重抽样（confusion 还原、无 barcode）；scVI vs oPCA 为同批细胞配对",
            "saturn_source": "confusion/（payloads/ 6 向中 2 向与权威不符，已由 scripts/pairwise_audit_gate.py 判定弃用）",
            "mapping": str(MAP_TSV.relative_to(ROOT)).replace("\\", "/"),
        },
        "comparisons": {},
    }

    lines = ["# 配对检验（修正后）", "",
             f"> 映射：`{res['convention']['mapping']}`；union macro-F1；"
             f"配对 bootstrap {NB} 次；只在两法共享细胞上比。", "",
             "## 有效范围（读之前必看）", "",
             "**`saturn_v99 vs scVI` 这 6 条用的是独立重抽样，不是同批细胞配对。**",
             "原因：SATURN 侧改由 `confusion/` 还原（`payloads/` 在 mouse->human、",
             "mouse->zebrafish 两向给出 0.2147 / 0.3600，与权威 0.2566 / 0.4076 不符，",
             "判定见 `docs/reports/audit-saturn-payload-gate-20261111.md`）。",
             "confusion 无 barcode，故 Δ 语义为「两法各自独立重抽样的差值」。", "",
             "**涉及 `opca` 的比较（12 条）只作参考，不是官方 oPCA 数值。**",
             "原因：本脚本 oPCA 列由 `exact` 层逐细胞预测**重新映射**得到，而 oPCA 官方 coarse 层是",
             "**在粗类空间里另跑一次 KNN**（`scripts/ortholog_pca_dcs_v3_fixkey.py:285-291`），两者不等价：", "",
             "| 方向 | 本表（重映射） | 官方（粗类 KNN） |",
             "|---|---|---|",
             "| 人→鼠 | 0.6150 | 0.6435 |",
             "| 鼠→人 | 0.5967 | 0.6729 |",
             "| 人→斑马鱼 | 0.1520 | 0.1654 |",
             "| 斑马鱼→人 | 0.1282 | 0.1512 |",
             "| 鼠→斑马鱼 | 0.2469 | 0.2177 |",
             "| 斑马鱼→鼠 | 0.3795 | 0.4405 |", "",
             "oPCA 的正式配对检验必须用 `results/mapping-v2-20261111/rerun-v2/` 的逐细胞产物。**待办。**", "",
             "## 比较表", "",
             "| 方向 | A vs B | n | A mf1 | B mf1 | Δ | 95% CI | 显著 | 配对方式 |",
             "|---|---|---|---|---|---|---|---|---|"]

    pairs = [("saturn_v99", "scVI"), ("saturn_v99", "opca"), ("opca", "scVI")]
    for dr in SRC:
        sat_tr, sat_pr = load_sat_conf(dr, mapping)
        sc = load_scv(dr, mapping)
        op = load_opca(dr, mapping)
        vec = {
            "saturn_v99": (sat_tr, sat_pr),
            "scVI": ([v[0] for v in sc.values()], [v[1] for v in sc.values()]),
            "opca": ([v[0] for v in op.values()], [v[1] for v in op.values()]),
        }
        store = {}
        for A, B in pairs:
            ta, pa = vec[A]
            tb, pb = vec[B]
            if not ta or not tb:
                continue
            if "saturn_v99" in (A, B):
                r = unpaired(ta, pa, tb, pb, A, B)
                nn, tag = f"{r['n_a']}/{r['n_b']}", "indep"
            else:
                shared = [bc for bc in sc if bc in op]
                if not shared:
                    continue
                r = paired([sc[bc][0] for bc in shared],
                           [sc[bc][1] for bc in shared],
                           [op[bc][1] for bc in shared], A, B)
                nn, tag = str(r["n"]), "paired"
            store[f"{A}_vs_{B}"] = r
            flag = "**SIG**" if r["significant_at_95"] else "ns"
            lines.append("| {} | {} vs {} | {} | {} | {} | {:+} | [{:+}, {:+}] | {} | {} |".format(
                DIRCN[dr], A, B, nn, r[f"{A}_mf1"], r[f"{B}_mf1"],
                r["delta"], r["delta_ci95"][0], r["delta_ci95"][1], flag, tag))
            print(f"{DIRCN[dr]:7s} {A:10s} vs {B:9s} n={nn:>10s} "
                  f"{r[f'{A}_mf1']:.4f} vs {r[f'{B}_mf1']:.4f} Δ={r['delta']:+.4f} "
                  f"CI[{r['delta_ci95'][0]:+.4f},{r['delta_ci95'][1]:+.4f}] {flag} [{tag}]", flush=True)
        if store:
            res["comparisons"][dr] = store

    OUTDIR.mkdir(parents=True, exist_ok=True)
    (OUTDIR / "pairwise_corrected.json").write_text(
        json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    (OUTDIR / "pairwise_corrected.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\nwrote", OUTDIR / "pairwise_corrected.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
