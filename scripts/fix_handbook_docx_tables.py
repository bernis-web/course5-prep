# -*- coding: utf-8 -*-
"""交接总纲 T2 与入门手册 T11 收敛；T13 是 v1 映射下的四约定对照表，只加口径注不 twist 数字。"""
from docx import Document
from docx.shared import Pt, RGBColor
from pathlib import Path

OPCA = {"0.1654": "0.1506", "0.1512": "0.2131", "0.2177": "0.2816", "0.4405": "0.4186"}
SAT = {"0.3658": "0.4076", "0.3563": "0.2961"}


def fix_cells(doc, t_idx, col, mp):
    n = 0
    for row in doc.tables[t_idx].rows:
        if col >= len(row.cells):
            continue
        cell = row.cells[col]
        t = cell.text.strip()
        if t in mp:
            for par in cell.paragraphs:
                if par.runs:
                    par.runs[0].text = mp[t]
                    for r in par.runs[1:]:
                        r.text = ""
            n += 1
    return n


# 1) 交接总纲：T2 的 oPCA 列（第 1 列）
p = Path(r"D:\projects\course5-prep\deliverables\课题5-组员交接总纲-20261104.docx")
d = Document(str(p))
print("总纲 T2 改:", fix_cells(d, 2, 1, OPCA))
d.save(str(p))

# 2) 入门手册：T11 的 SATURN 列（第 1 列）+ T13 加口径注
p = Path(r"D:\projects\course5-prep\deliverables\课题5-组员入门手册-20261104.docx")
d = Document(str(p))
print("手册 T11 改:", fix_cells(d, 11, 1, SAT))

note = d.add_paragraph()
r = note.add_run("口径注（2026-11-11）：上表是 **v1 映射**下的四种查表约定对照，用来说明「冻结值只能由约定 A 复现」；"
                 "v2 映射签认后的现行值不在此表，见 `docs/reports/number-index-20261111.md`。")
r.font.size = Pt(8.5)
r.font.color.rgb = RGBColor(0x5E, 0x71, 0x82)
d.save(str(p))
print("手册已加口径注")