# -*- coding: utf-8 -*-
"""Render team_doc_content.json into a Word document."""
import json
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

SRC = "D:/projects/course5-prep/docs/reports/team_doc_content.json"
OUT = "D:/projects/course5-prep/deliverables/课题5-项目说明文档-组员版-20261023.docx"

BLUE = RGBColor(0x00, 0x5B, 0xAC)
INK = RGBColor(0x1F, 0x2D, 0x3D)
MUTED = RGBColor(0x60, 0x75, 0x8F)

doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
sec.left_margin = sec.right_margin = Cm(2.2)
sec.top_margin = sec.bottom_margin = Cm(2.0)

st = doc.styles["Normal"]
st.font.name = "宋体"
st.font.size = Pt(10.5)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
st.paragraph_format.line_spacing = 1.5
st.paragraph_format.space_after = Pt(4)


def rf(r, size=10.5, bold=False, color=INK, font="宋体"):
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = color
    r.font.name = font
    rPr = r._element.get_or_add_rPr()
    f = rPr.find(qn("w:rFonts"))
    if f is None:
        f = OxmlElement("w:rFonts")
        rPr.append(f)
    for a in ("w:eastAsia", "w:ascii", "w:hAnsi"):
        f.set(qn(a), font)


def P(text="", size=10.5, bold=False, color=INK, font="宋体",
      align=WD_ALIGN_PARAGRAPH.JUSTIFY, before=0, after=4):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_before = Pt(before)
    p.paragraph_format.space_after = Pt(after)
    if text:
        r = p.add_run(text)
        rf(r, size, bold, color, font)
    return p


def H1(t):
    p = P(t, 15, True, BLUE, "微软雅黑", WD_ALIGN_PARAGRAPH.LEFT, 18, 6)
    p.paragraph_format.keep_with_next = True


def H2(t):
    p = P(t, 12, True, BLUE, "微软雅黑", WD_ALIGN_PARAGRAPH.LEFT, 10, 4)
    p.paragraph_format.keep_with_next = True


def BUL(t):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.line_spacing = 1.45
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(t)
    rf(r, 10.5)


def NOTE(t):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.left_indent = Cm(0.4)
    r = p.add_run(t)
    rf(r, 9.5, False, MUTED)


def shade(c, hexc):
    tcPr = c._tc.get_or_add_tcPr()
    sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear")
    sh.set(qn("w:color"), "auto")
    sh.set(qn("w:fill"), hexc)
    tcPr.append(sh)


def T(spec):
    headers = spec["headers"]
    rows = spec["rows"]
    widths = spec.get("widths")
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    lay = OxmlElement("w:tblLayout")
    lay.set(qn("w:type"), "fixed")
    t._tbl.tblPr.append(lay)
    for i, h in enumerate(headers):
        c = t.rows[0].cells[i]
        c.text = ""
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        rf(r, 9.5, True, RGBColor(0xFF, 0xFF, 0xFF), "微软雅黑")
        shade(c, "005BAC")
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            p = cells[i].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if i == 0 else WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(str(v))
            rf(r, 9.5)
    if widths:
        for i, w in enumerate(widths):
            t.columns[i].width = Cm(w)
            for row in t.rows:
                row.cells[i].width = Cm(w)
    P("", size=6, after=2)


data = json.load(open(SRC, encoding="utf-8"))

P(data["title"], 24, True, RGBColor(0x12, 0x36, 0x5A), "微软雅黑", WD_ALIGN_PARAGRAPH.LEFT, 0, 2)
P(data["subtitle"], 12.5, True, MUTED, "微软雅黑", WD_ALIGN_PARAGRAPH.LEFT, 0, 2)
P(data["meta"], 9.5, False, MUTED, after=10)

for sec_item in data["sections"]:
    H1(sec_item["h1"])
    for b in sec_item["blocks"]:
        if "p" in b:
            P(b["p"], bold=b.get("bold", False))
        elif "h2" in b:
            H2(b["h2"])
        elif "bullets" in b:
            for item in b["bullets"]:
                BUL(item)
        elif "note" in b:
            NOTE(b["note"])
        elif "table" in b:
            T(b["table"])

P("", after=10)
P("本文所有数字来自平台产物或本地独立重算，未凭记忆填写。", 9, False, MUTED)

doc.save(OUT)
print("WROTE", OUT)
