# -*- coding: utf-8 -*-
"""剩余「活文件」里的作废值收敛：master-handoff、PPT 交接包（md + docx）。

判定依据：这些文件把旧值当**现值**用（不是引用反例），所以必须改数，而不是加声明。
"""
from pathlib import Path

from docx import Document

FIX_PAIRS = [
    ("0.1269", "0.1282"), ("0.1640", "0.1386"), ("0.3658", "0.4076"), ("0.3563", "0.2961"),
    ("0.1654", "0.1506"), ("0.1512", "0.2131"), ("0.2177", "0.2816"), ("0.4405", "0.4186"),
    ("0.2479", "0.1282"), ("0.4021", "0.1386"),
]
MISC = [("2.4 倍", "约 2.7 倍"), ("300 倍", "约 104 倍")]


def fix_text(path: Path, extra=()):
    s = path.read_text(encoding="utf-8")
    n = 0
    for o, nw in list(FIX_PAIRS) + list(extra):
        c = s.count(o)
        if c:
            s = s.replace(o, nw)
            n += c
    path.write_text(s, encoding="utf-8")
    return n


# 1) master-handoff.md（§2 表 + 红框声明 + 2.4 倍那句）
p = Path(r"D:\projects\course5-prep\docs\execution\20261028-master-handoff.md")
print("master-handoff.md 改:", fix_text(p, MISC))

# 2) PPT 交接包 逐页 brief（只 300 倍）
p = Path(r"D:\projects\course5-prep\deliverables\PPT交接包\02_逐页brief.md")
if p.exists():
    print("PPT交接包/02_逐页brief.md 改:", fix_text(p, MISC))

# 3) PPT 制作交接包 docx（run 级替换，保留格式）
p = Path(r"D:\projects\course5-prep\deliverables\课题5-PPT制作交接包-20261110.docx")
if p.exists():
    d = Document(str(p))
    n = 0

    def rewrite(par):
        global n
        for r in par.runs:
            t = r.text
            for o, nw in list(FIX_PAIRS) + MISC:
                if o in t:
                    t = t.replace(o, nw)
                    n += 1
            r.text = t

    for par in d.paragraphs:
        rewrite(par)
    for tb in d.tables:
        for row in tb.rows:
            for cell in row.cells:
                for par in cell.paragraphs:
                    rewrite(par)
    d.save(str(p))
    print("PPT制作交接包 docx 改:", n)