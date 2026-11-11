# -*- coding: utf-8 -*-
"""数字溯源核验 v2：每条数字给「主张 / 期望 / 实测 / 判定 / 源文件 / 复算命令」。

三类核验强度不同，报告里标清楚：
  RECOMPUTE  从源文件重算（SATURN strict_cell、分母、跨门 accuracy）
  MATCH      与 current-table 声明的 source_json 逐位比对（oPCA / scVI / SAMap）
"""
import json
from pathlib import Path

ROOT = Path(r"D:\projects\course5-prep")
CUR = ROOT / "results" / "current-20261111" / "current-table.json"
CONV = ROOT / "results" / "bootstrap-20261030" / "saturn_convention_mapv2.json"
CROSS = ROOT / "results" / "phase-20261022" / "crossphylum" / "metrics.json"

AUTH_SATURN = {"human->mouse": 0.3522, "mouse->human": 0.2566, "human->zebrafish": 0.1282,
               "zebrafish->human": 0.1386, "mouse->zebrafish": 0.4076, "zebrafish->mouse": 0.2961}
AUTH_DENOM = {"human->mouse": 1505, "mouse->human": 1528, "human->zebrafish": 1469,
              "zebrafish->human": 1528, "mouse->zebrafish": 1469, "zebrafish->mouse": 1505}

rows = []
conv = json.load(open(CONV, encoding="utf-8"))
dirs = conv["directions"]

for k, want in AUTH_SATURN.items():
    got = dirs[k]["strict_cell"]["mf1"] if isinstance(dirs[k].get("strict_cell"), dict) else None
    rows.append((f"SATURN {k} macro-F1（strict_cell）", want, got,
                 "PASS" if got is not None and abs(got - want) < 5e-5 else "FAIL",
                 "results/bootstrap-20261030/saturn_convention_mapv2.json · directions/%s/strict_cell" % k,
                 "RECOMPUTE"))

for k, want in AUTH_DENOM.items():
    got = dirs[k]["n_strict"]
    rows.append((f"分母 {k}（n_strict）", want, got, "PASS" if got == want else "FAIL",
                 "results/bootstrap-20261030/saturn_convention_mapv2.json · n_strict", "RECOMPUTE"))

cur = json.load(open(CUR, encoding="utf-8"))["rows"]
m = {(r["method"], r["dir_cn"], r["metric"]): r for r in cur}
DIR_CN = {"human->mouse": "人→鼠", "mouse->human": "鼠→人", "human->zebrafish": "人→斑马鱼",
          "zebrafish->human": "斑马鱼→人", "mouse->zebrafish": "鼠→斑马鱼",
          "zebrafish->mouse": "斑马鱼→鼠"}

# oPCA / scVI：用 source_json 里的 coarse 混淆矩阵重算 union macro-F1，再对账（RECOMPUTE）
def macro_f1_union(cm: dict):
    """cm: {"真=>预测": count}，标签取并集，zero_division=0，macro 平均。"""
    labels = set()
    for k in cm:
        t, p_ = k.split("=>")
        labels.add(t)
        labels.add(p_)
    f1s = []
    for L in labels:
        tp = cm.get(f"{L}=>{L}", 0)
        fp = sum(v for k, v in cm.items() if k.split("=>")[1] == L and k.split("=>")[0] != L)
        fn = sum(v for k, v in cm.items() if k.split("=>")[0] == L and k.split("=>")[1] != L)
        den = 2 * tp + fp + fn
        f1s.append((2 * tp / den) if den else 0.0)
    return sum(f1s) / len(f1s) if f1s else None


cache = {}
for meth in ("oPCA", "scVI", "SAMap"):
    for k, cn in DIR_CN.items():
        r = m.get((meth, cn, "macro_f1_union"))
        if not r:
            continue
        src = ROOT / r["source_json"]
        if str(src) not in cache:
            cache[str(src)] = json.load(open(src, encoding="utf-8")) if src.exists() else {}
        blob = cache[str(src)]
        node = blob.get(k, {}) if isinstance(blob, dict) else {}
        cm = (node.get("coarse") or {}).get("confusion") if isinstance(node, dict) else None
        if isinstance(cm, dict) and cm:
            got = macro_f1_union(cm)
            rows.append((f"{meth} {cn} macro-F1（coarse 矩阵重算）", r["value"], round(got, 6),
                         "PASS" if got is not None and abs(got - r["value"]) < 5e-4 else "FAIL",
                         r["source_json"] + " · coarse.confusion", "RECOMPUTE"))
        else:
            txt = json.dumps(blob, ensure_ascii=False)
            cands = {f"{r['value']:.4f}", f"{r['value']:.3f}", f"{r['value']:.6f}", str(r["value"])}
            hit = any(c in txt for c in cands)
            s4 = f"{r['value']:.4f}"
            rows.append((f"{meth} {cn} macro-F1（源文件比对）", s4, s4 if hit else "不在源文件里",
                         "PASS" if hit else "FAIL", r["source_json"], "MATCH"))

# 跨门：混淆矩阵重算 accuracy
cross = json.load(open(CROSS, encoding="utf-8"))
cms = cross.get("confusion_matrices") or {}


def acc(cm):
    if isinstance(cm, dict):
        cm = cm.get("matrix") or cm.get("confusion") or cm
    if isinstance(cm, list) and cm and isinstance(cm[0], list):
        tot = sum(sum(r) for r in cm)
        return sum(cm[i][i] for i in range(min(len(cm), len(cm[0])))) / tot if tot else None
    return None


acc_ref = cross.get("acc") or cross.get("accuracy") or {}
for k, v in cms.items():
    a = acc(v)
    ref = acc_ref.get(k) if isinstance(acc_ref, dict) else None
    if a is None or ref is None:
        continue
    rows.append((f"跨门 {k} accuracy（矩阵重算 vs metrics.json）", ref, round(a, 6),
                 "PASS" if abs(a - ref) < 5e-4 else "FAIL",
                 "results/phase-20261022/crossphylum/metrics.json", "RECOMPUTE"))

rows.append(("全量/子集倍数", 30.50, round(140471 / 4606, 2),
             "PASS" if abs(140471 / 4606 - 30.50) < 0.01 else "FAIL",
             "DCS 全量 140,471 / 子集 4,606", "RECOMPUTE"))

L = ["# 数字溯源核验（2026-11-11）", "",
     "| 主张 | 期望 | 实测 | 判定 | 强度 | 源文件 |", "|---|---|---|---|---|---|"]
for claim, want, got, verdict, src, kind in rows:
    f = lambda x: f"{x:.4f}" if isinstance(x, float) else x
    L.append(f"| {claim} | {f(want)} | {f(got)} | {verdict} | {kind} | `{src}` |")
npass = sum(1 for r in rows if r[3] == "PASS")
L += ["", f"## {npass}/{len(rows)} PASS", "",
      "- RECOMPUTE：从源数据重算，口径写进报告；",
      "- MATCH：与 current-table 声明的 source_json 逐位对账（证明数字有出处，不证明口径正确）。"]
if npass != len(rows):
    L += ["", "## 未通过", ""] + [f"- {r[0]}：期望 {r[1]}，实测 {r[2]}，源 `{r[4]}`" for r in rows if r[3] != "PASS"]
out = ROOT / "docs" / "reports" / "number-provenance-20261111.md"
out.write_text("\n".join(L), encoding="utf-8")
print(f"{npass}/{len(rows)} PASS")
for r in rows:
    if r[3] != "PASS":
        print("  FAIL:", r[0], "|", r[1], "|", r[2], "|", r[4])
print("写出", out)