# -*- coding: utf-8 -*-
"""只读：导出每张表的全部单元格文本，用于按内容长度校列宽。"""
import io
from pptx import Presentation

PPTX = r"D:\projects\course5-prep\results\stage-reports-20261102\课题5第03次汇报_三场景结论与可复现闭环.pptx"
OUT = r"D:\projects\course5-prep\results\stage-reports-20261102\_table_text.txt"
EMU = 914400.0

buf = io.StringIO()
prs = Presentation(PPTX)
for i, s in enumerate(prs.slides, 1):
    for sh in s.shapes:
        if not sh.has_table:
            continue
        tbl = sh.table
        cols = [c.width / EMU for c in tbl.columns]
        buf.write("\n=== slide %d  table cols=%s ===\n" % (i, [round(c, 3) for c in cols]))
        for ci in range(len(tbl.columns)):
            buf.write("  --- col%d (w=%.3f) ---\n" % (ci, cols[ci]))
            for ri in range(len(tbl.rows)):
                c = tbl.cell(ri, ci)
                p0 = c.text_frame.paragraphs[0]
                sz = p0.runs[0].font.size if p0.runs else None
                buf.write("    r%d sz=%s : %r\n" % (ri, (sz / 12700.0) if sz else None, c.text))
open(OUT, "w", encoding="utf-8").write(buf.getvalue())
print("written", OUT)
