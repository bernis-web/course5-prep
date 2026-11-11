"""冻结唯一数字源：生成统一指标表（课题5 / XenoTransfer）

背景（老师 2026-11-11 反馈 + Claude 审查）：
  我们此前那张「coarse accuracy」表混了三样东西——
  ① 指标（SATURN 列填的是 macro-F1 而不是 accuracy）；
  ② 映射版本（oPCA 是 v2、scVI/SAMap 还是 v1）；
  ③ 分母（有的写 n、有的根本没写）。
  这张表把三者全部显式化：每行都带 metric / mapping_version / n_q / source_json。

口径约定（与项目既有脚本一致）：
  - coarse 标签空间；
  - macro-F1 用 **union 口径**：标签集 = 真实 ∪ 预测，预测里多出的类 F1 记 0；
  - accuracy = 命中 / 保留细胞数；
  - 「strict_cell」= 真值可映射的细胞全部保留、预测不可映射记错。

数据源（只读 JSON，不手写任何数字）：
  oPCA   results/mapping-v2-20261111/rerun-v2/metrics.json   （v2 映射；acc 现成，mf1 从混淆矩阵现算）
  scVI   results/bootstrap-20261030/bootstrap.json            （v1 映射，待按 v2 重跑）
  SATURN results/bootstrap-20261030/saturn_convention_mapv2.json（v2 映射，修正后）
  SAMap  results/bootstrap-20261030/bootstrap.json            （v1 映射）

输出：
  results/current-20261111/current-table.tsv
  results/current-20261111/current-table.md
  results/current-20261111/current-table.json
"""
from __future__ import annotations

import csv
import io
import json
import sys
from collections import Counter
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
OUTDIR = ROOT / "results" / "current-20261111"

DIRS = ["human->mouse", "mouse->human", "human->zebrafish",
        "zebrafish->human", "mouse->zebrafish", "zebrafish->mouse"]
DIRCN = {"human->mouse": "人→鼠", "mouse->human": "鼠→人",
         "human->zebrafish": "人→斑马鱼", "zebrafish->human": "斑马鱼→人",
         "mouse->zebrafish": "鼠→斑马鱼", "zebrafish->mouse": "斑马鱼→鼠"}
METHOD_CN = {"oPCA": "oPCA", "scVI": "scVI", "SATURN": "SATURN", "SAMap": "SAMap"}


def macro_f1_union(conf: dict) -> float:
    """从 {"a=>b": n} 形式的混淆矩阵算 union 口径 macro-F1。"""
    t, p, tp = Counter(), Counter(), Counter()
    for key, n in conf.items():
        a, b = key.split("=>")
        t[a] += n
        p[b] += n
        if a == b:
            tp[a] += n
    labels = set(t) | set(p)
    fs = []
    for c in labels:
        prec = tp[c] / p[c] if p[c] else 0.0
        rec = tp[c] / t[c] if t[c] else 0.0
        fs.append(2 * prec * rec / (prec + rec) if (prec + rec) else 0.0)
    return sum(fs) / len(fs) if fs else 0.0


def load(p: str):
    f = ROOT / p
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else None


def main() -> int:
    rows = []

    # ---------- oPCA：v2 映射，本地重跑产物 ----------
    opca = load("results/mapping-v2-20261111/rerun-v2/metrics.json")
    for d in DIRS:
        if not opca or d not in opca:
            continue
        c = opca[d]["coarse"]
        rows.append(dict(
            method="oPCA", direction=d, dir_cn=DIRCN[d],
            metric="accuracy", value=c["acc"], n_q=c["n_q"],
            ci_low=None, ci_high=None,
            mapping_version="v2",
            source_json="results/mapping-v2-20261111/rerun-v2/metrics.json",
            notes="本地重跑，6/6 命中 v1 冻结值的同一条链" if d in
                  ("human->mouse", "mouse->human") else ""))
        rows.append(dict(
            method="oPCA", direction=d, dir_cn=DIRCN[d],
            metric="macro_f1_union", value=round(macro_f1_union(c["confusion"]), 4),
            n_q=c["n_q"], ci_low=None, ci_high=None,
            mapping_version="v2",
            source_json="results/mapping-v2-20261111/rerun-v2/metrics.json",
            notes="本脚本从该文件混淆矩阵现算（union 口径）"))

    # ---------- scVI / SAMap：bootstrap.json（v1 映射） ----------
    bs = load("results/bootstrap-20261030/bootstrap.json")
    if bs:
        for meth_key, label in (("scVI", "scVI"), ("samap", "SAMap")):
            for d in DIRS:
                x = bs["methods"].get(meth_key, {}).get(d)
                if not x:
                    continue
                nq = x.get("n_q")
                note = "" if nq else "n_q 为 0 或缺失 → 不可评估"
                for metric, key, ci in (("accuracy", "acc", "acc_ci95"),
                                        ("macro_f1_union", "mf1", "mf1_ci95")):
                    val = x.get(key)
                    if val is None:
                        continue
                    c95 = x.get(ci) or [None, None]
                    rows.append(dict(
                        method=label, direction=d, dir_cn=DIRCN[d],
                        metric=metric, value=val, n_q=nq,
                        ci_low=c95[0] if len(c95) > 0 else None,
                        ci_high=c95[1] if len(c95) > 1 else None,
                        mapping_version="v1",
                        source_json="results/bootstrap-20261030/bootstrap.json",
                        notes=(note + ("；待按 v2 重跑" if d in
                                       ("human->zebrafish", "mouse->zebrafish",
                                        "zebrafish->human", "zebrafish->mouse") else "")).strip("；")))

    # ---------- SATURN：修正后的 v2 口径 ----------
    sat = load("results/bootstrap-20261030/saturn_convention_mapv2.json")
    if sat:
        for d in DIRS:
            rec = sat.get("directions", {}).get(d, {})
            sc = rec.get("strict_cell", {})
            for metric, key in (("accuracy", "acc"), ("macro_f1_union", "mf1")):
                if sc.get(key) is None:
                    continue
                rows.append(dict(
                    method="SATURN", direction=d, dir_cn=DIRCN[d],
                    metric=metric, value=sc[key], n_q=None,
                    ci_low=None, ci_high=None,
                    mapping_version="v2",
                    source_json="results/bootstrap-20261030/saturn_convention_mapv2.json",
                    notes="修正后（物种词表方向已纠正）；strict_cell 口径"))

    OUTDIR.mkdir(parents=True, exist_ok=True)
    fields = ["method", "dir_cn", "direction", "metric", "value", "n_q",
              "ci_low", "ci_high", "mapping_version", "source_json", "notes"]

    with (OUTDIR / "current-table.tsv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in fields})

    (OUTDIR / "current-table.json").write_text(
        json.dumps({"generated_from": "scripts/build_current_table.py",
                    "convention": {"label_space": "coarse",
                                   "macro_f1": "union（真实∪预测，多预测类 F1=0）",
                                   "accuracy": "命中/保留细胞",
                                   "strict_cell": "真值可映射细胞全保留、预测不可映射记错"},
                    "rows": rows},
                   ensure_ascii=False, indent=1), encoding="utf-8")

    # Markdown: accuracy 与 macro-F1 分两张表，避免再混
    lines = ["# 课题5 统一指标表（current）", "",
             "> 由 `scripts/build_current_table.py` 从 JSON 生成，**不含手写数字**。",
             "> 每行都带 `mapping_version` 与 `source_json`；`n_q` 为评估分母。", ""]
    for metric, title in (("accuracy", "一、accuracy"), ("macro_f1_union", "二、macro-F1（union 口径）")):
        lines += [f"## {title}", "",
                  "| 方向 | 方法 | 值 | n_q | 映射版本 | 来源 | 备注 |",
                  "|---|---|---|---|---|---|---|"]
        for r in rows:
            if r["metric"] != metric:
                continue
            lines.append("| {} | {} | {} | {} | {} | `{}` | {} |".format(
                r["dir_cn"], METHOD_CN.get(r["method"], r["method"]),
                r["value"], r["n_q"] if r["n_q"] is not None else "—",
                r["mapping_version"], Path(r["source_json"]).name, r["notes"]))
        lines.append("")
    lines += ["## 三、口径警告（读这张表之前必看）", "",
              "1. **scVI 与 SAMap 仍是 v1 映射**：凡目标物种为斑马鱼的方向，",
              "   分母应为 1469 而现在是 1499（差 30 个 `Orthers` 真值细胞）。**标注为待重跑**。",
              "2. **SATURN 无 CI**：修正后的口径只算了点估计，bootstrap 需重跑。",
              "3. **oPCA 的 macro-F1 是本脚本从混淆矩阵现算**，与 bootstrap.json 的 mf1",
              "   口径一致但不是同一文件产物，引用时注明来源。",
              "4. **不要跨方法比不同指标**：accuracy 与 macro-F1 是两回事，",
              "   这张表把它们分成了两张表正是为此。", ""]
    (OUTDIR / "current-table.md").write_text("\n".join(lines), encoding="utf-8")

    # 控制台摘要
    print(f"rows={len(rows)}")
    for metric in ("accuracy", "macro_f1_union"):
        sub = [r for r in rows if r["metric"] == metric]
        v1 = sum(1 for r in sub if r["mapping_version"] == "v1")
        print(f"  {metric:16s} {len(sub)} 行，其中 v1 口径 {v1} 行（待重跑）")
    print("wrote:", OUTDIR / "current-table.tsv")
    print("       ", OUTDIR / "current-table.md")
    print("       ", OUTDIR / "current-table.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
