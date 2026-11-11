"""镜像内 6 值复现的口径对齐审计（2026-11-11）

背景（report-12 §7 唯一待办）：
  平台镜像 g5-opca-container 内复现 6 个冻结 accuracy 时，用的是 **v1** 映射表；
  而项目现行口径是 **v2 签认版**（`config/heart-celltype-map-v2.tsv`，`zebrafish|Orthers`
  从 active 改为 unresolved）。于是「镜像内 6/6 复现」这条证据与现行口径不一致。

本脚本回答两件事：
  A. oPCA 的 6 个 coarse accuracy 在 v1 / v2 下分别是多少，差多少；
  B. 先用 v1 复算出冻结值，证明本脚本的复算链是对的，再给 v2 的数。

口径与 `scripts/saturn_convention_audit_v2.py` 完全一致：
  - 真值用**目标**物种词表，预测用**源**物种词表（跨物种迁移方向）；
  - 只有 `mapping_status == active` 才算可映射；
  - `strict_cell`：真值可映射的细胞全部保留，预测不可映射记 `<not_in_coarse>`（算错）；
  - accuracy = 命中数 / 保留细胞数。

输入：results/phase-20261010/opca-fixkey-recovered-20261015/predictions/*.json（exact 层原始标签）
输出：results/mapping-v2-20261111/opca_v1_vs_v2.json
"""
from __future__ import annotations

import csv
import json
import os
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRED_DIR = ROOT / "results" / "phase-20261010" / "opca-fixkey-recovered-20261015" / "predictions"
OUT = ROOT / "results" / "mapping-v2-20261111" / "opca_v1_vs_v2.json"
V1 = ROOT / "config" / "heart-celltype-map-v1.tsv"
V2 = ROOT / "config" / "heart-celltype-map-v2.tsv"

# 方向 -> (源=参考书, 目标=被预测)
SRC = {
    "human->mouse": ("human", "mouse"),
    "mouse->human": ("mouse", "human"),
    "human->zebrafish": ("human", "zebrafish"),
    "zebrafish->human": ("zebrafish", "human"),
    "mouse->zebrafish": ("mouse", "zebrafish"),
    "zebrafish->mouse": ("zebrafish", "mouse"),
}
DIRCN = {"human->mouse": "人→鼠", "mouse->human": "鼠→人",
         "human->zebrafish": "人→斑马鱼", "zebrafish->human": "斑马鱼→人",
         "mouse->zebrafish": "鼠→斑马鱼", "zebrafish->mouse": "斑马鱼→鼠"}

# 冻结值（容器内 6/6 复现的那组；也是 report-12 §4 的 oPCA accuracy）
FROZEN = {"human->mouse": 0.8618, "mouse->human": 0.7369, "human->zebrafish": 0.1795,
          "zebrafish->human": 0.1734, "mouse->zebrafish": 0.2675, "zebrafish->mouse": 0.5814}
# 诊断交叉验证用：report-12 §4 给的就是 macro-F1，一并复算
FROZEN_MF1 = {"human->mouse": 0.6435, "mouse->human": 0.6729, "human->zebrafish": 0.1654,
              "zebrafish->human": 0.1512, "mouse->zebrafish": 0.2177, "zebrafish->mouse": 0.4405}


def load_mapping(path: Path):
    m = {}
    with open(path, encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            m[(row["source_species"].strip(), row["source_label"].strip())] = (
                row["coarse_level"].strip(), row["mapping_status"].strip())
    return m


def to_coarse(sp, lab, mapping):
    hit = mapping.get((sp, str(lab).strip()))
    if not hit:
        return None
    coarse, status = hit
    return coarse if (status == "active" and coarse) else None


def macro_f1(truth, pred):
    t, p, tp = Counter(), Counter(), Counter()
    for a, b in zip(truth, pred):
        t[a] += 1
        p[b] += 1
        if a == b:
            tp[a] += 1
    labels = set(t) | set(p)
    fs = []
    for c in labels:
        pr = tp[c] / p[c] if p[c] else 0.0
        rc = tp[c] / t[c] if t[c] else 0.0
        fs.append(2 * pr * rc / (pr + rc) if (pr + rc) else 0.0)
    return sum(fs) / len(fs) if fs else 0.0


CODE = {"human": "hu", "mouse": "mo", "zebrafish": "zf"}


def normalize(name: str) -> str:
    """只保留字母数字：方向分隔符是 U+F03E（私用区箭头），连字符/点号都剥掉，
    这样 'hu-\\uf03emo.json' 与 'hu-mo.json' 归一后都是 'humojson'。"""
    return "".join(ch for ch in name if ch.isalnum())


def pred_path(dr: str) -> Path:
    src, tgt = SRC[dr]
    want = normalize(f"{CODE[src]}{CODE[tgt]}.json")
    for f in PRED_DIR.iterdir():
        if normalize(f.name) == want:
            return f
    raise FileNotFoundError(f"{dr} ({want}) not in {PRED_DIR}")


def species_agreement(labels, mapping):
    """判断一组原始标签更像哪个物种的词表（返回两个物种的命中数）。"""
    out = {}
    for sp in ("human", "mouse", "zebrafish"):
        out[sp] = sum(1 for x in labels if (sp, str(x).strip()) in mapping)
    return out


def evaluate(dr: str, mapping) -> dict:
    src, tgt = SRC[dr]
    cells = json.loads(pred_path(dr).read_text(encoding="utf-8"))["exact"]

    t_raw = [c["truth"] for c in cells]
    p_raw = [c["prediction"] for c in cells]

    cell_t, cell_p = [], []
    truth_unmapped = Counter()
    for tr, pr in zip(t_raw, p_raw):
        ct = to_coarse(tgt, tr, mapping)          # 真值 → 目标物种词表
        if ct is None:
            truth_unmapped[tr] += 1
            continue
        cp = to_coarse(src, pr, mapping)          # 预测 → 源物种词表
        cell_t.append(ct)
        cell_p.append(cp if cp else "<not_in_coarse>")

    acc = sum(a == b for a, b in zip(cell_t, cell_p)) / len(cell_t) if cell_t else None
    return {
        "n_cells_file": len(cells),
        "n_cell_eval": len(cell_t),
        "n_truth_unmapped": sum(truth_unmapped.values()),
        "acc": round(acc, 4) if acc is not None else None,
        "mf1": round(macro_f1(cell_t, cell_p), 4) if cell_t else None,
    }


def main() -> int:
    v1, v2 = load_mapping(V1), load_mapping(V2)
    res = {
        "date": "2026-11-11",
        "purpose": "镜像内 6 值复现用的是 v1 映射；本表给出 v1/v2 两套口径下的 oPCA coarse 指标，"
                   "用于给那条证据加口径标注，并判断是否需要重跑。",
        "convention": "strict_cell；真值→目标物种词表，预测→源物种词表；仅 active 可映射；"
                      "预测不可映射记 <not_in_coarse> 且保留细胞",
        "sources": {
            "predictions": str(PRED_DIR.relative_to(ROOT)).replace("\\", "/"),
            "map_v1": str(V1.relative_to(ROOT)).replace("\\", "/"),
            "map_v2": str(V2.relative_to(ROOT)).replace("\\", "/"),
        },
        "frozen_in_image": FROZEN,
        "species_vocabulary_check": {},
        "directions": {},
    }

    # 0) 先确认 truth/pred 各自属于哪个物种词表（防止又出现方向颠倒）
    for dr in SRC:
        cells = json.loads(pred_path(dr).read_text(encoding="utf-8"))["exact"]
        src, tgt = SRC[dr]
        res["species_vocabulary_check"][dr] = {
            "truth_hits": species_agreement([c["truth"] for c in cells], v2),
            "pred_hits": species_agreement([c["prediction"] for c in cells], v2),
            "expected_truth_species": tgt,
            "expected_pred_species": src,
        }

    ok_v1 = 0
    for dr in SRC:
        a = evaluate(dr, v1)
        b = evaluate(dr, v2)
        diff = (round(b["acc"] - a["acc"], 4)
                if (a["acc"] is not None and b["acc"] is not None) else None)
        match_v1 = (a["acc"] is not None and abs(a["acc"] - FROZEN[dr]) < 5e-5)
        if match_v1:
            ok_v1 += 1
        res["directions"][dr] = {
            "dir_cn": DIRCN[dr],
            "v1": a, "v2": b,
            "frozen": FROZEN[dr],
            "v1_matches_frozen": match_v1,
            "acc_diff_v2_minus_v1": diff,
            "mf1_frozen_reference": FROZEN_MF1[dr],
        }
        print(f"{DIRCN[dr]:7s} v1 acc={a['acc']}  v2 acc={b['acc']}  Δ={diff}  "
              f"冻结={FROZEN[dr]}  v1命中={match_v1}  n_eval={a['n_cell_eval']}->{b['n_cell_eval']}",
              flush=True)

    res["v1_reproduces_frozen_count"] = f"{ok_v1}/6"
    res["verdict"] = ("复算链可信" if ok_v1 == 6 else "复算链与冻结值不符，先别下结论")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"\nv1 命中冻结值: {ok_v1}/6 -> {res['verdict']}")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
