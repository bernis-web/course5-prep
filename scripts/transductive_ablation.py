"""transductive vs inductive 消融：PCA 是否用了目标物种细胞

背景（2026-11-11 第 75 轮发现）：
    `scripts/ortholog_pca_dcs_v3_fixkey.py:278-282`：

        X_joint = np.vstack([Xs, Xt]).astype(np.float64)      # 源 + 目标一起堆
        Z = PCA(n_components=NPCS, random_state=SEED).fit_transform(X_joint)

    **PCA 在「源 + 目标」细胞上联合拟合** → 拟合时已看到目标细胞
    → **我们的 oPCA 是 transductive 的**，不是 inductive。

    这与 Claude 咨询第 5 条（「现有全部是 transductive，应补 held-out」）对应。

为什么重要：
    真实部署时**拿不到目标物种细胞**。transductive 拟合会泄漏目标分布信息，
    **系统性抬高分数**，并让我们的数与 inductive 方法不可直接比。

本脚本做的事：
    生成一个 **inductive 变体** —— 把 178 行改成「只用源细胞拟合 PCA，再 transform 目标」
    （KNN 部分不变），跑一遍，与 transductive 版对比。

变体改法（最小改动）：
    把
        Z = PCA(n_components=NPCS, random_state=SEED).fit_transform(X_joint)
    改成
        _pca = PCA(n_components=NPCS, random_state=SEED).fit(Xs)   # 只用源细胞
        Z = _pca.transform(X_joint)                                 # 再变换全部

输出：
    results/transductive-20261111/{transductive_vs_inductive.json,md}
    results/transductive-20261111/inductive-variant/metrics.json
"""
from __future__ import annotations

import io
import json
import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = Path(r"D:\projects\course5-prep")
BASE = ROOT / "scripts" / "ortholog_pca_dcs_v3_fixkey.py"
VARIANT = ROOT / "scripts" / "_opca_inductive_variant.py"
OUTDIR = ROOT / "results" / "transductive-20261111"
DIRCN = {"human->mouse": "人→鼠", "mouse->human": "鼠→人",
         "human->zebrafish": "人→斑马鱼", "zebrafish->human": "斑马鱼→人",
         "mouse->zebrafish": "鼠→斑马鱼", "zebrafish->mouse": "斑马鱼→鼠"}

OLD = "        Z = PCA(n_components=NPCS, random_state=SEED).fit_transform(X_joint)"
NEW = ("        _pca_ind = PCA(n_components=NPCS, random_state=SEED).fit(Xs)   # 只用源细胞拟合\n"
       "        Z = _pca_ind.transform(X_joint)                              # 再变换全部（inductive）")


def make_variant() -> int:
    src = BASE.read_text(encoding="utf-8")
    if OLD not in src:
        print("!! 没找到目标行：", OLD)
        return 2
    src = src.replace(OLD, NEW, 1)
    VARIANT.write_text(src, encoding="utf-8")
    print("变体已生成：", VARIANT)
    return 0


def run_variant() -> int:
    out = OUTDIR / "inductive-variant"
    if (out / "metrics.json").exists():
        print("产出已存在，跳过")
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
    log = OUTDIR / "inductive-variant.log"
    print("跑 inductive 变体…")
    with log.open("w", encoding="utf-8") as fh:
        r = subprocess.run([str(ROOT / ".venv39" / "Scripts" / "python.exe"), str(VARIANT)],
                           env=env, cwd=str(ROOT), stdout=fh, stderr=subprocess.STDOUT)
    print("rc =", r.returncode)
    print(log.read_text(encoding="utf-8")[-600:])
    return r.returncode


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


def compare() -> int:
    td = json.loads((ROOT / "results" / "mapping-v2-20261111" / "rerun-v2" /
                     "metrics.json").read_text(encoding="utf-8"))
    ind_p = OUTDIR / "inductive-variant" / "metrics.json"
    if not ind_p.exists():
        print("inductive 变体没产出 metrics.json")
        return 2
    id_ = json.loads(ind_p.read_text(encoding="utf-8"))

    res = {"date": "2026-11-11",
           "purpose": "PCA 是否用目标物种细胞（transductive vs inductive）",
           "finding": ("源码 `ortholog_pca_dcs_v3_fixkey.py:278-282` 显示 "
                       "X_joint = vstack([Xs, Xt])，PCA 在源+目标上联合拟合 → 原版是 transductive"),
           "transductive_source": "results/mapping-v2-20261111/rerun-v2/metrics.json",
           "inductive_source": str(ind_p.relative_to(ROOT)).replace("\\", "/"),
           "directions": {}}
    lines = ["# transductive vs inductive（oPCA）", "",
             "> **发现**：原版 `ortholog_pca_dcs_v3_fixkey.py:278-282` 里",
             "> `X_joint = np.vstack([Xs, Xt])`，**PCA 在源+目标细胞上联合拟合** → **是 transductive 的**。",
             "> 本表对比把它改成 inductive（**只用源细胞拟合 PCA**）后的分数变化。", "",
             "| 方向 | transductive acc | **inductive acc** | Δ | transductive mf1 | inductive mf1 | n_q |",
             "|---|---|---|---|---|---|---|"]
    for dr, cn in DIRCN.items():
        t = td.get(dr, {}).get("coarse"); i = id_.get(dr, {}).get("coarse")
        if not t or not i:
            continue
        d = round(i["acc"] - t["acc"], 4)
        res["directions"][dr] = {"transductive_acc": t["acc"], "inductive_acc": i["acc"],
                                 "delta_acc": d, "transductive_mf1": round(mf1_of(t), 4),
                                 "inductive_mf1": round(mf1_of(i), 4), "n_q": t["n_q"]}
        lines.append(f"| {cn} | {t['acc']} | **{i['acc']}** | **{d:+.4f}** | "
                     f"{mf1_of(t):.4f} | {mf1_of(i):.4f} | {t['n_q']} |")
        print(f"{cn:8s} transductive={t['acc']} inductive={i['acc']} Δ={d:+.4f}", flush=True)

    ds = [v["delta_acc"] for v in res["directions"].values()]
    if ds:
        res["summary"] = {"min_delta": min(ds), "max_delta": max(ds),
                          "mean_delta": round(sum(ds) / len(ds), 4)}
        lines += ["", "## 结论", "",
                  f"- Δ（inductive − transductive）范围 **{min(ds):+.4f} ~ {max(ds):+.4f}**，"
                  f"均值 **{sum(ds)/len(ds):+.4f}**",
                  "- **负值 = transductive 拟合抬高了分数**（泄漏了目标分布信息）；",
                  "- → 跨方法比较时**必须声明是 transductive 还是 inductive**，",
                  "  否则「我们的数高」可能只是因为我们看到了目标细胞。"]

    OUTDIR.mkdir(parents=True, exist_ok=True)
    (OUTDIR / "transductive_vs_inductive.json").write_text(
        json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    (OUTDIR / "transductive_vs_inductive.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\nwrote", OUTDIR / "transductive_vs_inductive.json")
    return 0


def main() -> int:
    if make_variant() != 0:
        return 2
    rc = run_variant()
    if rc != 0:
        return rc
    return compare()


if __name__ == "__main__":
    raise SystemExit(main())
