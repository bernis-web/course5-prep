# -*- coding: utf-8 -*-
"""修 .docx（含表格单元格）与 pairwise_corrected.json 的错误数字。

docx 策略：先试单 run 精确替换（保留格式）；跨 run 时重建该段落（保留首 run 格式）。
每条声明 expected，命中数不符就跳过并报警。
"""
import json
from pathlib import Path

from docx import Document

ROOT = Path(r"D:\projects\course5-prep")
GANG = ROOT / "deliverables" / "课题5-组员交接总纲-20261104.docx"
CE = ROOT / "deliverables" / "课题5-组员入门手册-20261104.docx"
PW = ROOT / "results" / "bootstrap-20261030" / "pairwise_corrected.json"


def para_replace(par, old, new):
    if old not in par.text:
        return 0
    # 单 run 命中
    for r in par.runs:
        if old in r.text:
            r.text = r.text.replace(old, new)
            return 1
    # 跨 run：合并到首 run
    full = par.text.replace(old, new)
    if not par.runs:
        return 0
    first = par.runs[0]
    for r in par.runs[1:]:
        r._element.getparent().remove(r._element)
    first.text = full
    return 1


def docx_fix(path, items):
    doc = Document(str(path))
    hits = {}
    for old, new, exp in items:
        n = 0
        for par in doc.paragraphs:
            n += para_replace(par, old, new)
        for tbl in doc.tables:
            for row in tbl.rows:
                for cell in row.cells:
                    for par in cell.paragraphs:
                        n += para_replace(par, old, new)
        hits[old[:44]] = (n, exp)
        if n == exp:
            print(f"OK    {path.name:<34} {old[:44]}")
        else:
            print(f"SKIP  {path.name:<34} count={n} exp={exp}  {old[:44]}")
    doc.save(str(path))
    return hits


# ── A5 / B9 / B10 / B11 / A6（册）���─
docx_fix(GANG, [
    ("公平口径", "strict_cell 口径", 1),                       # B9（TABLE7 术语）
    ("`results/bootstrap-20261030/pairwise.json`（13 组）",
     "`results/bootstrap-20261030/pairwise_corrected.json`（13 组，旧 pairwise.json 已作废）", 1),  # B10
    ("saturn_convention_v2.json", "saturn_convention_mapv2.json", 1),  # B11 溯源指向
])

docx_fix(CE, [
    ("459–1309", "1499–1528", 1),        # A5：作废的 bug 分母
    ("300 倍", "约 104 倍", 1),          # A6
])

# ── B12：pairwise_corrected.json 两格回填 ──
d = json.loads(PW.read_text(encoding="utf-8"))
print("\n--- B12 修前 ---")


def walk(o, path=""):
    out = []
    if isinstance(o, dict):
        for k, v in o.items():
            out += walk(v, f"{path}.{k}" if path else k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            out += walk(v, f"{path}[{i}]")
    return out


before = {k: v for k, v in walk(d)}
fixed = 0
for k, v in list(before.items()):
    pass

# 直接按结构修：找 鼠→人 / 鼠→斑马鱼 的 saturn macro_f1
txt = PW.read_text(encoding="utf-8")
if "0.2147" in txt:
    print("命中 0.2147 次数:", txt.count("0.2147"))
if "0.36" in txt:
    print("含 0.36 片段:", [s for s in txt.split("\n") if "0.36" in s][:6])