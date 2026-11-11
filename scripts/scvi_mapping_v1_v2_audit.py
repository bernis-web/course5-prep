"""scVI 的 coarse 口径重算（v1 → v2）

背景：mapping v2 把 `zebrafish|Orthers` 由 active 改为 unresolved。
`Orthers` 是**斑马鱼真值标签**，因此凡目标物种为斑马鱼的方向
（人→斑马鱼、鼠→斑马鱼）分母都会缩小 30；
凡源物种为斑马鱼的方向（斑马鱼→人、斑马鱼→鼠）训练侧少 30 个 neural 样本。

oPCA 已用 `scripts/opca_mapping_convention_audit.py` +
`results/mapping-v2-20261111/rerun-{v1,v2}/` 完成重跑。
本脚本处理 **scVI**：它有 exact 层逐细胞预测，先验证
「coarse 预测 == map(exact 预测)」这个前提是否成立，
成立就直接用 v2 表重算，不需要重跑模型。

输出：results/mapping-v2-20261111/scvi_v1_vs_v2.json
"""
from __future__ import annotations

import csv
import io
import json
import sys
from collections import Counter
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(r"D:\projects\course5-prep")
PRED = ROOT / "results" / "phase-20261019" / "scvi-cross-species" / "predictions"
OUT = ROOT / "results" / "mapping-v2-20261111" / "scvi_v1_vs_v2.json"
V1 = ROOT / "config" / "heart-celltype-map-v1.tsv"
V2 = ROOT / "config" / "heart-celltype-map-v2.tsv"

# 文件名方向码 -> (源=参考, 目标=被预测)
FILES = {
    "hu_to_mo": ("human", "mouse"), "mo_to_hu": ("mouse", "human"),
    "hu_to_zf": ("human", "zebrafish"), "zf_to_hu": ("zebrafish", "human"),
    "mo_to_zf": ("mouse", "zebrafish"), "zf_to_mo": ("zebrafish", "mouse"),
}
DIRCN = {"hu_to_mo": "人→鼠", "mo_to_hu": "鼠→人", "hu_to_zf": "人→斑马鱼",
         "zf_to_hu": "斑马鱼→人", "mo_to_zf": "鼠→斑马鱼", "zf_to_mo": "斑马鱼→鼠"}


def load_tsv(p: Path):
    m = {}
    for row in csv.DictReader(open(p, encoding="utf-8-sig", newline=""), delimiter="\t"):
        m[(row["source_species"].strip(), row["source_label"].strip())] = (
            row["coarse_level"].strip(), row["mapping_status"].strip())
    return m


def to_coarse(sp, lab, m):
    h = m.get((sp, str(lab).strip()))
    if not h:
        return None
    c, s = h
    return c if (s == "active" and c) else None


def load_level(level: str, key: str):
    return json.loads((PRED / f"{level}_{key}.json").read_text(encoding="utf-8"))


def main() -> int:
    v1, v2 = load_tsv(V1), load_tsv(V2)
    res = {
        "date": "2026-11-11",
        "purpose": "scVI 的 coarse 指标在 v1/v2 映射下分别是多少（映射换代后哪些方向需要改数）",
        "premise_check": "先验证 coarse 预测是否等于「map(exact 预测)」",
        "directions": {},
    }

    for key, (src, tgt) in FILES.items():
        ex = load_level("exact", key)
        co = load_level("coarse", key)
        # 前提验证：coarse.prediction == map(src, exact.prediction) ？
        agree = tot = 0
        for e, c in zip(ex, co):
            if not c.get("included"):
                continue
            tot += 1
            if to_coarse(src, e["prediction"], v1) == c["prediction"]:
                agree += 1

        # v1 / v2 重算：真值→目标词表，预测→源词表；真值不可映射的细胞剔除
        out = {}
        for tag, mp in (("v1", v1), ("v2", v2)):
            t_lab, p_lab = [], []
            dropped = Counter()
            for e in ex:
                ct = to_coarse(tgt, e["truth"], mp)
                if ct is None:
                    dropped[str(e["truth"])] += 1
                    continue
                cp = to_coarse(src, e["prediction"], mp)
                t_lab.append(ct)
                p_lab.append(cp if cp else "<not_in_coarse>")
            acc = sum(a == b for a, b in zip(t_lab, p_lab)) / len(t_lab) if t_lab else None
            out[tag] = {
                "acc": round(acc, 4) if acc is not None else None,
                "n": len(t_lab),
                "n_truth_dropped": sum(dropped.values()),
                "dropped_labels": dict(dropped),
            }

        res["directions"][key] = {
            "dir_cn": DIRCN[key], "src": src, "tgt": tgt,
            "premise_coarse_equals_map_exact": f"{agree}/{tot}",
            "premise_holds": agree == tot,
            "v1": out["v1"], "v2": out["v2"],
            "delta_acc": (round(out["v2"]["acc"] - out["v1"]["acc"], 4)
                          if out["v1"]["acc"] is not None and out["v2"]["acc"] is not None else None),
            "delta_n": out["v2"]["n"] - out["v1"]["n"],
        }
        print(f"{DIRCN[key]:7s} 前提={agree}/{tot} "
              f"v1 acc={out['v1']['acc']} (n={out['v1']['n']})  "
              f"v2 acc={out['v2']['acc']} (n={out['v2']['n']})  Δ={res['directions'][key]['delta_acc']}",
              flush=True)

    # 与已冻结的 scVI 值对拍（recomputed_union.json）
    ru = json.loads((ROOT / "results" / "phase-20261019" / "scvi-cross-species" /
                     "recomputed_union.json").read_text(encoding="utf-8"))
    name = {"hu_to_mo": "human->mouse", "mo_to_hu": "mouse->human", "hu_to_zf": "human->zebrafish",
            "zf_to_hu": "zebrafish->human", "mo_to_zf": "mouse->zebrafish", "zf_to_mo": "zebrafish->mouse"}
    res["cross_check_vs_recomputed_union"] = {}
    for key in FILES:
        fz = ru.get(f"{name[key]}|coarse", {})
        mine = res["directions"][key]["v1"]
        ok = (mine["acc"] is not None and fz.get("acc") is not None
              and abs(mine["acc"] - fz["acc"]) < 5e-5)
        res["cross_check_vs_recomputed_union"][key] = {
            "frozen_acc": fz.get("acc"), "frozen_n": fz.get("n"),
            "my_v1_acc": mine["acc"], "my_v1_n": mine["n"], "match": ok,
        }

    hits = sum(1 for v in res["cross_check_vs_recomputed_union"].values() if v["match"])
    res["cross_check_result"] = f"{hits}/6"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"\n与 recomputed_union.json 对拍: {hits}/6")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
