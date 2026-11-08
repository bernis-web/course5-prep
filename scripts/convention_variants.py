"""判定实验：哪种「词表归属」约定能复现冻结的 SATURN macro-F1？

冻结值（docs/execution/20261028-master-handoff.md §2）——
    human->mouse 0.4147 / mouse->human 0.4010 / human->zebrafish 0.2479
    zebrafish->human 0.4021 / mouse->zebrafish 0.6500 / zebrafish->mouse 0.6510

四组约定分别重算 union macro-F1（只保留预测可映射的细胞）：
    A  truth→源物种, pred→目标物种   （scripts/saturn_convention_audit.py 的做法）
    B  truth→目标物种, pred→源物种   （按混淆矩阵实际词表推的正确方向）
    C  truth→源物种, pred→源物种
    D  truth→目标物种, pred→目标物种

输出：results/bootstrap-20261030/convention_variants.json
"""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "bootstrap-20261030" / "convention_variants.json"
MAP_TSV = ROOT / "config" / "heart-celltype-map-v1.tsv"
CONF = ROOT / "results" / "pilot-v1" / "saturn-v99" / "raw" / "recovered-20261001" / "confusion"

SRC = {
    "human->mouse": ("human", "mouse"),
    "mouse->human": ("mouse", "human"),
    "human->zebrafish": ("human", "zebrafish"),
    "zebrafish->human": ("zebrafish", "human"),
    "mouse->zebrafish": ("mouse", "zebrafish"),
    "zebrafish->mouse": ("zebrafish", "mouse"),
}

FROZEN = {
    "human->mouse": 0.4147,
    "mouse->human": 0.4010,
    "human->zebrafish": 0.2479,
    "zebrafish->human": 0.4021,
    "mouse->zebrafish": 0.6500,
    "zebrafish->mouse": 0.6510,
}


def load_mapping():
    m = {}
    with open(MAP_TSV, encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            m[(row["source_species"].strip(), row["source_label"].strip())] = (
                row["coarse_level"].strip(),
                row["mapping_status"].strip(),
            )
    return m


def coarse(sp, lab, mapping):
    hit = mapping.get((sp, str(lab).strip()))
    if not hit:
        return None
    c, s = hit
    return c if (s == "active" and c) else None


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
    return (sum(fs) / len(fs) if fs else 0.0), len(labels), len(truth)


def main() -> int:
    mapping = load_mapping()
    variants = {
        "A_truth_src_pred_tgt": ("src", "tgt"),
        "B_truth_tgt_pred_src": ("tgt", "src"),
        "C_truth_src_pred_src": ("src", "src"),
        "D_truth_tgt_pred_tgt": ("tgt", "tgt"),
    }
    res = {"frozen": FROZEN, "directions": {}}

    print(f'{"direction":<20}{"frozen":<9}{"A":<9}{"B":<9}{"C":<9}{"D":<9}  (n_q for each)')
    for dr, (src, tgt) in SRC.items():
        conf = json.loads((CONF / f"coarse_{src}_to_{tgt}.json").read_text(encoding="utf-8"))
        per = {}
        rowtxt = f'{dr:<20}{FROZEN[dr]:<9}'
        for name, (truth_side, pred_side) in variants.items():
            t_sp = src if truth_side == "src" else tgt
            p_sp = src if pred_side == "src" else tgt
            tt, pp = [], []
            for key, n in conf.items():
                tr, pr = key.split("=>")
                ct = coarse(t_sp, tr, mapping)
                cp = coarse(p_sp, pr, mapping)
                if ct is None or cp is None:
                    continue
                tt.extend([ct] * n)
                pp.extend([cp] * n)
            if tt:
                mf1, ncls, n = macro_f1(tt, pp)
            else:
                mf1, ncls, n = None, 0, 0
            per[name] = {"mf1": round(mf1, 4) if mf1 is not None else None,
                         "n_q": n, "n_classes": ncls,
                         "matches_frozen": (mf1 is not None and abs(mf1 - FROZEN[dr]) < 5e-4)}
            rowtxt += f'{(str(round(mf1,4)) if mf1 is not None else "NA"):<9}'
        print(rowtxt)
        res["directions"][dr] = per

    print()
    for name in variants:
        hits = sum(1 for dr in SRC if res["directions"][dr][name]["matches_frozen"])
        print(f'{name:<26} 复现冻结值 {hits}/6')

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    print("\nwrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
