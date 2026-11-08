# -*- coding: utf-8 -*-
"""只读：dump 每页 shape 几何 + 表格列宽 + 字号，输出到 utf-8 文件。不改任何文件。"""
import io
from pptx import Presentation

PPTX = r"D:\projects\course5-prep\results\stage-reports-20261102\课题5第03次汇报_三场景结论与可复现闭环.pptx"
OUT = r"D:\projects\course5-prep\results\stage-reports-20261102\_layout_audit.txt"
EMU = 914400.0

buf = io.StringIO()
def w(s=""):
    buf.write(s + "\n")

prs = Presentation(PPTX)
w("slide size: %.3f x %.3f in" % (prs.slide_width / EMU, prs.slide_height / EMU))

for i, s in enumerate(prs.slides, 1):
    w("\n=== slide %d ===" % i)
    for sh in s.shapes:
        txt = ""
        if sh.has_text_frame:
            txt = sh.text_frame.text.replace("\n", "\\n")[:64]
        w("  %-12s %-14s L=%5.2f T=%5.2f W=%5.2f H=%5.2f :: %s" % (
            str(sh.shape_type).split()[0], sh.name[:14],
            sh.left / EMU, sh.top / EMU, sh.width / EMU, sh.height / EMU, txt))
        if sh.has_table:
            tbl = sh.table
            cols = [c.width / EMU for c in tbl.columns]
            w("     table: cols=%s rows=%d total=%.2f top=%.2f" % (
                [round(c, 3) for c in cols], len(tbl.rows), sum(cols), sh.top / EMU))
            for ri in range(min(2, len(tbl.rows))):
                for ci in range(len(tbl.columns)):
                    c = tbl.cell(ri, ci)
                    p0 = c.text_frame.paragraphs[0]
                    sz = p0.runs[0].font.size if p0.runs else None
                    w("       r%dc%d w=%.2f align=%-6s sz=%s marL=%.3f txt=%r" % (
                        ri, ci, cols[ci], str(p0.alignment).split()[0],
                        (sz / 12700.0) if sz else None,
                        (c.margin_left or 0) / EMU, c.text[:36]))
            # 行高
            w("       rowheights=%s" % [round(r.height / EMU, 3) for r in tbl.rows])
        if sh.has_text_frame and sh.text_frame.text.strip():
            for pi, para in enumerate(sh.text_frame.paragraphs[:6]):
                szs = set()
                for r in para.runs:
                    if r.font.size:
                        szs.add(r.font.size / 12700.0)
                if szs:
                    w("       para%d sizes=%s align=%s spaceAft=%s" % (
                        pi, sorted(szs), str(para.alignment).split()[0],
                        (para.space_after / 12700.0) if para.space_after else None))

open(OUT, "w", encoding="utf-8").write(buf.getvalue())
print("written", OUT)
