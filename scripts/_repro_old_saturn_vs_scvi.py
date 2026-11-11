"""复现历史数字：用旧 SATURN 载荷 + scVI 预测，确认评测实现与 2026-10-30 那版一致

为什么要做
----------
新训练的 SATURN 在六向上都显著赢 scVI（Δ +0.23~+0.34），这与历史结论
（`saturn_vs_scvi.json`：SATURN 六向全不赢）**直接冲突**。

在相信任何一方之前，必须先排除「评测代码不一样」这个解释。
本脚本用 2026-10-01 恢复出来的旧 SATURN 载荷 + 同一份 scVI 预测，
按 `saturn_vs_scvi_paired.py` 的两种 convention 复算：

    published  : 丢掉 SATURN 预测落在粗类外的细胞（n 变小）
    strict_cell: 那些细胞保留并算错

如果能复现 0.6491 / 0.6206 这类数字，就说明：
  - 我的评测实现是对的；
  - 新旧差距来自**模型**，不是来自口径；
  - 历史结论的 `published` 口径本身建立在「只在 SATURN 预测得好的细胞上比较」
    这个选择性样本上——这正是它失真的原因。
"""
from __future__ import annotations

import gzip
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from saturn_new_vs_scvi_same_protocol import load_mapping, to_coarse, macro_f1  # noqa: E402

PAYLOAD = ROOT / "results" / "pilot-v1" / "saturn-v99" / "raw" / "recovered-20261001" / "payloads"
SCVI_PRED = ROOT / "results" / "phase-20261019" / "scvi-cross-species" / "predictions"
MAP = ROOT / "config" / "heart-celltype-map-v1.tsv"

SAT = {
    ("human", "mouse"): "p6_coarse_human_to_mouse",
    ("mouse", "human"): "p1_coarse_mouse_to_human",
    ("human", "zebrafish"): "p3_coarse_human_to_zebrafish",
    ("zebrafish", "human"): "p2_coarse_zebrafish_to_human",
    ("mouse", "zebrafish"): "p5_coarse_mouse_to_zebrafish",
    ("zebrafish", "mouse"): "p4_coarse_zebrafish_to_mouse",
}
SCV = {
    ("human", "mouse"): "coarse_hu_to_mo",
    ("mouse", "human"): "coarse_mo_to_hu",
    ("human", "zebrafish"): "coarse_hu_to_zf",
    ("zebrafish", "human"): "coarse_zf_to_hu",
    ("mouse", "zebrafish"): "coarse_mo_to_zf",
    ("zebrafish", "mouse"): "coarse_zf_to_mo",
}


def load_sat(src, tgt, mapping):
    """旧载荷格式：[barcode, truth_label, pred_label, include_flag]"""
    f = PAYLOAD / (SAT[(src, tgt)] + ".json.json.gz")
    if not f.exists():
        return None
    rows = json.loads(gzip.open(f, "rb").read().decode("utf-8"))
    out = {}
    for r in rows:
        if r[3] != 1:
            continue
        ct = to_coarse(src, r[1], mapping)
        cp = to_coarse(tgt, r[2], mapping)
        if ct:
            out[r[0]] = (ct, cp if cp else "<not_in_coarse>")
    return out


def load_scv(src, tgt):
    f = SCVI_PRED / (SCV[(src, tgt)] + ".json")
    if not f.exists():
        return None
    out = {}
    for r in json.loads(f.read_text(encoding="utf-8")):
        if not r.get("included", True):
            continue
        if r["truth"] in ("unmapped", "") or r["prediction"] in ("unmapped", ""):
            continue
        out[r["prefixed_barcode"]] = (r["truth"], r["prediction"])
    return out


def main() -> int:
    mapping = load_mapping(MAP)
    print(f"映射表: {MAP.name}  条目 {len(mapping)}")
    print(f"旧载荷: {PAYLOAD.relative_to(ROOT)}")
    print()
    hdr = f"{'方向':16s} {'conv':11s} {'n':>5s} {'SATURN':>8s} {'scVI':>8s} {'Δ':>8s}"
    print(hdr)
    print("-" * len(hdr))

    for (src, tgt) in [("human", "mouse"), ("mouse", "human"), ("human", "zebrafish"),
                       ("zebrafish", "human"), ("mouse", "zebrafish"), ("zebrafish", "mouse")]:
        sat = load_sat(src, tgt, mapping)
        scv = load_scv(src, tgt)
        if sat is None or scv is None:
            print(f"{src}->{tgt:12s} {'缺文件':11s}")
            continue
        shared_all = sorted(set(sat) & set(scv))
        if not shared_all:
            print(f"{src}->{tgt:12s} {'无共享':11s}")
            continue

        # published：丢掉 SATURN 预测落在粗类外的细胞
        pub = [b for b in shared_all if sat[b][1] != "<not_in_coarse>"]
        if pub:
            t = [sat[b][0] for b in pub]
            ps = [sat[b][1] for b in pub]
            pc = [scv[b][1] for b in pub]
            print(f"{src+'->'+tgt:16s} {'published':11s} {len(pub):5d} "
                  f"{macro_f1(t, ps):8.4f} {macro_f1(t, pc):8.4f} "
                  f"{macro_f1(t, ps) - macro_f1(t, pc):+8.4f}")

        # strict_cell：全保留，出粗类的算错
        t2 = [sat[b][0] for b in shared_all]
        ps2 = [sat[b][1] for b in shared_all]
        pc2 = [scv[b][1] for b in shared_all]
        print(f"{src+'->'+tgt:16s} {'strict_cell':11s} {len(shared_all):5d} "
              f"{macro_f1(t2, ps2):8.4f} {macro_f1(t2, pc2):8.4f} "
              f"{macro_f1(t2, ps2) - macro_f1(t2, pc2):+8.4f}")
        n_out = len(shared_all) - len(pub)
        print(f"{'':16s} {'(出粗类丢)':11s} {n_out:5d}  "
              f"{'':8s} {'':8s}   丢弃率 {n_out/len(shared_all):.1%}")
        print()

    print("判定：若上面数字能对上 results/bootstrap-20261030/saturn_vs_scvi.json，")
    print("      则评测实现一致，新旧差距来自模型本身；")
    print("      同时注意 published 口径的 n 远小于 strict_cell——它是选择性样本。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())