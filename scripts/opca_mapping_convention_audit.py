"""镜像内 6 值复现的「口径标注」审计（2026-11-11）

要回答的问题（report-12 §7 唯一待办）：
  平台镜像 g5-opca-container 内 6/6 复现了 6 个冻结粗类 accuracy，
  但那份复现用的是镜像内嵌的映射表，**不是**项目现行的 v2 签认表。
  差多少？要不要重跑？

关键事实（本脚本用数据确认）：
  1) 容器内嵌映射 = `scripts/v99_mapping_embedded.json`（3160 B，sha256 d92e32aa…），
     与 `results/.../opca-fixkey-recovered-20261015/manifest.json` 的
     `mapping_sha256` 逐位一致 —— 说明那份产物就是这么算出来的。
  2) 冻结的 6 个值是 `included=True` 子集上的 accuracy：被排除的细胞
     `exclusion_reason="inactive"`、`truth="other"`，即**真值侧**不在粗类空间，
     属合理剔除（与 SATURN 当年「按预测侧丢样本」性质不同）。
  3) v2 签认表相对 v1 只改一行：`zebrafish|Orthers` 由 active 改为 unresolved，
     影响面只在两个斑马鱼为目标的方向。

输出：results/mapping-v2-20261111/opca_mapping_convention_audit.json
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import sys
from collections import Counter
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(r"D:\projects\course5-prep")
PRED = ROOT / "results" / "phase-20261010" / "opca-fixkey-recovered-20261015" / "predictions"
V99 = ROOT / "scripts" / "v99_mapping_embedded.json"
V1 = ROOT / "config" / "heart-celltype-map-v1.tsv"
V2 = ROOT / "config" / "heart-celltype-map-v2.tsv"
OUT = ROOT / "results" / "mapping-v2-20261111" / "opca_mapping_convention_audit.json"

CODE = {"human": "hu", "mouse": "mo", "zebrafish": "zf"}
DIRCN = {"human->mouse": "人→鼠", "mouse->human": "鼠→人",
         "human->zebrafish": "人→斑马鱼", "zebrafish->human": "斑马鱼→人",
         "mouse->zebrafish": "鼠→斑马鱼", "zebrafish->mouse": "斑马鱼→鼠"}
SRC = {
    "human->mouse": ("human", "mouse"), "mouse->human": ("mouse", "human"),
    "human->zebrafish": ("human", "zebrafish"), "zebrafish->human": ("zebrafish", "human"),
    "mouse->zebrafish": ("mouse", "zebrafish"), "zebrafish->mouse": ("zebrafish", "mouse"),
}
FROZEN = {"human->mouse": 0.8618, "mouse->human": 0.7369, "human->zebrafish": 0.1795,
          "zebrafish->human": 0.1734, "mouse->zebrafish": 0.2675, "zebrafish->mouse": 0.5814}


def norm(n: str) -> str:
    return "".join(c for c in n if c.isalnum())


def find_pred(dr: str) -> Path:
    s, t = SRC[dr]
    want = norm(CODE[s] + CODE[t] + ".json")
    for f in PRED.iterdir():
        if norm(f.name) == want:
            return f
    raise FileNotFoundError(dr)


def load_tsv(p: Path):
    m = {}
    for row in csv.DictReader(open(p, encoding="utf-8-sig", newline=""), delimiter="\t"):
        m[(row["source_species"].strip(), row["source_label"].strip())] = (
            row["coarse_level"].strip(), row["mapping_status"].strip())
    return m


def load_v99(p: Path):
    """{ "species|Label": [coarse, fine, status] } -> 同 tsv 的 (coarse, status) 形式"""
    raw = json.loads(p.read_text(encoding="utf-8"))
    m = {}
    for k, v in raw.items():
        sp, lab = k.split("|", 1)
        coarse, _fine, status = (list(v) + [None, None, None])[:3]
        m[(sp.strip(), lab.strip())] = (str(coarse).strip(), str(status).strip())
    return m, raw


def to_coarse(sp, lab, m):
    h = m.get((sp, str(lab).strip()))
    if not h:
        return None
    c, s = h
    return c if (s == "active" and c) else None


def evaluate(dr: str, mapping) -> dict:
    """按容器口径重算：真值→目标物种词表；预测→源物种词表；
    仅 active 可映射；真值不可映射的细胞剔除（对应 included=False）。"""
    src, tgt = SRC[dr]
    d = json.loads(find_pred(dr).read_text(encoding="utf-8"))
    ex, co = d["exact"], d["coarse"]
    t_lab, p_lab = [], []
    dropped_truth = Counter()
    for e in ex:
        ct = to_coarse(tgt, e["truth"], mapping)
        if ct is None:
            dropped_truth[str(e["truth"])] += 1
            continue
        cp = to_coarse(src, e["prediction"], mapping)
        t_lab.append(ct)
        p_lab.append(cp if cp else "<not_in_coarse>")
    acc = sum(a == b for a, b in zip(t_lab, p_lab)) / len(t_lab) if t_lab else None
    return {
        "n_exact": len(ex),
        "n_eval": len(t_lab),
        "n_truth_dropped": sum(dropped_truth.values()),
        "truth_dropped_labels": dict(dropped_truth),
        "acc": round(acc, 4) if acc is not None else None,
    }


def main() -> int:
    v99, raw99 = load_v99(V99)
    v1, v2 = load_tsv(V1), load_tsv(V2)

    sha99 = hashlib.sha256(V99.read_bytes()).hexdigest()
    res = {
        "date": "2026-11-11",
        "purpose": "给「镜像内 6 值复现」这条证据加口径标注，并给出 v2 签认表下的对应数值",
        "conventions": {
            "truth_side": "真值 → 目标物种词表",
            "pred_side": "预测 → 源物种词表",
            "mappable": "仅 mapping_status == active",
            "denominator": "剔除真值不可映射的细胞（= 产物里的 included=True 子集）",
        },
        "container_embedded_mapping": {
            "file": str(V99.relative_to(ROOT)).replace("\\", "/"),
            "sha256": sha99,
            "entries": len(raw99),
            "matches_manifest_mapping_sha256": sha99 ==
                json.loads((ROOT / "results" / "phase-20261010" /
                            "opca-fixkey-recovered-20261015" / "manifest.json")
                           .read_text(encoding="utf-8"))["mapping_sha256"],
        },
        "table_diff_v1_vs_v2": [
            {"key": f"{sp}|{lab}", "v1": v1[(sp, lab)], "v2": v2[(sp, lab)]}
            for (sp, lab) in sorted(set(v1) | set(v2))
            if v1.get((sp, lab)) != v2.get((sp, lab))
        ],
        "table_diff_v1tsv_vs_v99json": [
            {"key": f"{sp}|{lab}", "v1_tsv": v1.get((sp, lab)), "v99_json": v99.get((sp, lab))}
            for (sp, lab) in sorted(set(v1) | set(v99))
            if v1.get((sp, lab)) != v99.get((sp, lab))
        ],
        "frozen_in_image": FROZEN,
        "reproduce_with_v99": {},
        "v2_signed_mapping": {},
    }

    ok = 0
    for dr in SRC:
        a = evaluate(dr, v99)
        b = evaluate(dr, v2)
        hit = a["acc"] is not None and abs(a["acc"] - FROZEN[dr]) < 5e-5
        ok += 1 if hit else 0
        res["reproduce_with_v99"][dr] = {**a, "dir_cn": DIRCN[dr],
                                        "frozen": FROZEN[dr], "matches_frozen": hit}
        res["v2_signed_mapping"][dr] = {**b, "dir_cn": DIRCN[dr],
                                        "delta_acc_vs_v99": (round(b["acc"] - a["acc"], 4)
                                                             if a["acc"] is not None and b["acc"] is not None else None),
                                        "delta_n_eval": b["n_eval"] - a["n_eval"]}
        print(f"{DIRCN[dr]:7s} v99 acc={a['acc']} (n={a['n_eval']}, 冻结={FROZEN[dr]}, 命中={hit})  "
              f"v2 acc={b['acc']} (n={b['n_eval']})  Δacc={res['v2_signed_mapping'][dr]['delta_acc_vs_v99']}",
              flush=True)

    res["v99_reproduces_frozen_count"] = f"{ok}/6"
    res["verdict"] = ("容器口径已完全复现，复算链可信" if ok == 6
                      else "仍有差异，需继续定位（先不要据此改结论）")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"\nv99 命中冻结值 {ok}/6 -> {res['verdict']}")
    print("v1/v2 表差异条数:", len(res["table_diff_v1_vs_v2"]))
    print("v1tsv/v99json 差异条数:", len(res["table_diff_v1tsv_vs_v99json"]))
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
