# -*- coding: utf-8 -*-
"""v2 改数器：只改"现值型"命中，放过"叙述型"和"引用型"。

相对 v1 的三条护栏（v1 盲替换把「SATURN 从 0.6500 掉到 0.4076」改成「从 0.4076 掉到 0.4076」）：
  1. 引用标记：所在段含 旧值/原（错）/对照/作废/更正/推翻/冻结/附录 → 跳过
  2. 叙述标记：所在段含 从…掉到/涨到/变成/提升/下降/→/vs/倍 → 跳过（这类句子里的旧值是历史叙事）
  3. 只认"列表或表格"形态：同一段至少出现 2 个不同旧值，或以 | 开头（表格行）→ 才替换
"""
from collections import Counter
from pathlib import Path

from docx import Document

MAP = [
    ("0.4147", "0.3522"), ("0.4010", "0.2566"), ("0.2479", "0.1282"), ("0.4021", "0.1386"),
    ("0.6500", "0.4076"), ("0.6510", "0.2961"),
    ("0.1269", "0.1282"), ("0.1640", "0.1386"), ("0.3658", "0.4076"), ("0.3563", "0.2961"),
    ("0.1654", "0.1506"), ("0.1512", "0.2131"), ("0.2177", "0.2816"), ("0.4405", "0.4186"),
]
CTX = ["旧值", "原（错）", "对照", "作废", "更正", "推翻", "错口径", "冻结值", "已废", "附录"]
NARR = ["掉到", "涨到", "变成", "提升", "下降", "→", "vs", "倍", "从 0", "从0"]

DOCX = [
    "deliverables/课题5-PPT制作交接包-20261110.docx",
    "deliverables/课题5-组员入门手册-20261104.docx",
    "deliverables/课题5-组员汇报说明-小白版-20261110.docx",
]
MD = [
    "docs/team-handbook/part1-问题与方法.md",
    "docs/team-handbook/part2-口径陷阱与三场景.md",
    "docs/team-handbook/part3-可复现与FAQ.md",
    "docs/team-handbook/part4-汇报说明小白版.md",
    "docs/execution/20261111-repro-manifest.md",
]
ROOT = Path(r"D:\projects\course5-prep")


def eligible(txt: str) -> bool:
    if any(k in txt for k in CTX) or any(k in txt for k in NARR):
        return False
    present = {o for o, _ in MAP if o in txt}
    if len(present) >= 2:
        return True
    return txt.lstrip().startswith("|") or txt.lstrip().startswith("•")


def fix_par(par, tally):
    txt = par.text
    if not eligible(txt):
        return
    for r in par.runs:
        t = r.text
        for o, n in MAP:
            if o in t:
                tally[o] += t.count(o)
                t = t.replace(o, n)
        r.text = t


report = ["# CURRENT 文件改数回执 v2（2026-11-11）", "",
          "v1 盲替换弄坏了两处叙述句（「从 0.6500 掉到 0.4076」→「从 0.4076 掉到 0.4076」），已回滚重做。",
          "本版护栏：引用标记跳过 / 叙述标记跳过 / 只改列表与表格形态。",
          "", "| 文件 | 改数处 | 明细 |", "|---|---|---|"]
for rel in DOCX:
    p = ROOT / rel
    if not p.exists():
        report.append(f"| `{rel}` | - | 不存在 |")
        continue
    d = Document(str(p))
    tally = Counter()
    for par in d.paragraphs:
        fix_par(par, tally)
    for tb in d.tables:
        for row in tb.rows:
            for cell in row.cells:
                for par in cell.paragraphs:
                    fix_par(par, tally)
    d.save(str(p))
    detail = ", ".join(f"{o}→{n}×{tally[o]}" for o, n in MAP if tally[o])
    report.append(f"| `{rel}` | {sum(tally.values())} | {detail or '无需改'} |")
    print(f"{rel}: {sum(tally.values())}")

for rel in MD:
    p = ROOT / rel
    if not p.exists():
        continue
    out, tally = [], Counter()
    for ln in p.read_text(encoding="utf-8").splitlines(keepends=True):
        body = ln.rstrip("\n")
        if eligible(body):
            for o, n in MAP:
                if o in body:
                    tally[o] += body.count(o)
                    body = body.replace(o, n)
            ln = body + ("\n" if ln.endswith("\n") else "")
        out.append(ln)
    p.write_text("".join(out), encoding="utf-8")
    detail = ", ".join(f"{o}→{n}×{tally[o]}" for o, n in MAP if tally[o])
    report.append(f"| `{rel}` | {sum(tally.values())} | {detail or '无需改'} |")
    print(f"{rel}: {sum(tally.values())}  {detail}")

(ROOT / "docs" / "reports" / "fix-current-values-20261111.md").write_text("\n".join(report), encoding="utf-8")
print("写出 docs/reports/fix-current-values-20261111.md")