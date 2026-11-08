"""Render the page-by-page walkthrough (report 02) to DOCX.

Reads docs/reports/report02-walkthrough-content.json and writes a styled Word
document. Content lives in JSON so Chinese quotes never collide with Python
string literals.
"""

from __future__ import annotations

import json
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "docs" / "reports" / "report02-walkthrough-content.json"
OUT = ROOT / "deliverables" / "课题5第02次汇报-逐页讲解稿-20261027.docx"

FONT = "微软雅黑"
NAVY = RGBColor(0x12, 0x36, 0x5A)
BLUE = RGBColor(0x00, 0x5B, 0xAC)
GOLD = RGBColor(0x8A, 0x4B, 0x00)
TEXT = RGBColor(0x1F, 0x2D, 0x3D)
MUTED = RGBColor(0x60, 0x75, 0x8F)


def set_run(run, size=10.5, bold=False, color=TEXT, name=FONT):
    run.font.name = name
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(qn("w:eastAsia"), name)
    rfonts.set(qn("w:ascii"), name)
    rfonts.set(qn("w:hAnsi"), name)


def shade_paragraph(paragraph, fill):
    ppr = paragraph._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    ppr.append(shd)


def left_border(paragraph, color="FFC000", size=18):
    ppr = paragraph._p.get_or_add_pPr()
    pbdr = OxmlElement("w:pBdr")
    left = OxmlElement("w:left")
    left.set(qn("w:val"), "single")
    left.set(qn("w:sz"), str(size))
    left.set(qn("w:space"), "6")
    left.set(qn("w:color"), color)
    pbdr.append(left)
    ppr.append(pbdr)


def bottom_border(paragraph, color="005BAC", size=10):
    ppr = paragraph._p.get_or_add_pPr()
    pbdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), str(size))
    bottom.set(qn("w:space"), "2")
    bottom.set(qn("w:color"), color)
    pbdr.append(bottom)
    ppr.append(pbdr)


def set_table_layout(table, widths):
    """Force fixed layout and real column widths (python-docx needs all three)."""
    tbl = table._tbl
    tblpr = tbl.tblPr
    layout = OxmlElement("w:tblLayout")
    layout.set(qn("w:type"), "fixed")
    tblpr.append(layout)
    tblw = OxmlElement("w:tblW")
    tblw.set(qn("w:w"), str(int(sum(widths) * 567)))
    tblw.set(qn("w:type"), "dxa")
    tblpr.append(tblw)
    grid = tbl.tblGrid
    for i, w in enumerate(widths):
        grid.gridCol_lst[i].set(qn("w:w"), str(int(w * 567)))
    for row in table.rows:
        for i, w in enumerate(widths):
            row.cells[i].width = Cm(w)


def repeat_header(row):
    trpr = row._tr.get_or_add_trPr()
    el = OxmlElement("w:tblHeader")
    el.set(qn("w:val"), "true")
    trpr.append(el)


def no_split(row):
    trpr = row._tr.get_or_add_trPr()
    el = OxmlElement("w:cantSplit")
    el.set(qn("w:val"), "true")
    trpr.append(el)


def shade_cell(cell, fill):
    tcpr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    tcpr.append(shd)


def cell_margins(cell, top=60, bottom=60, left=90, right=90):
    tcpr = cell._tc.get_or_add_tcPr()
    mar = OxmlElement("w:tcMar")
    for tag, val in (("top", top), ("bottom", bottom), ("start", left), ("end", right)):
        el = OxmlElement(f"w:{tag}")
        el.set(qn("w:w"), str(val))
        el.set(qn("w:type"), "dxa")
        mar.append(el)
    tcpr.append(mar)


def para(doc, text="", size=10.5, bold=False, color=TEXT, space_before=0, space_after=4,
         align=None, line=1.45, indent=None):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(space_before)
    pf.space_after = Pt(space_after)
    pf.line_spacing = line
    if indent is not None:
        pf.left_indent = Cm(indent)
    if align is not None:
        p.alignment = align
    if text:
        run = p.add_run(text)
        set_run(run, size=size, bold=bold, color=color)
    return p


def add_heading(doc, text, level=2):
    if level == 2:
        p = para(doc, text, size=14.5, bold=True, color=NAVY, space_before=16, space_after=8)
        bottom_border(p)
        p.paragraph_format.keep_with_next = True
        return p
    p = para(doc, text, size=12, bold=True, color=BLUE, space_before=12, space_after=5)
    p.paragraph_format.keep_with_next = True
    return p


def add_callout(doc, title, items, fill="EAF4FB", border="005BAC", title_color=NAVY):
    p = para(doc, title, size=11.5, bold=True, color=title_color, space_before=8, space_after=3)
    shade_paragraph(p, fill)
    left_border(p, color=border, size=24)
    for i, item in enumerate(items, 1):
        q = doc.add_paragraph()
        pf = q.paragraph_format
        pf.left_indent = Cm(0.55)
        pf.space_before = Pt(0)
        pf.space_after = Pt(3)
        pf.line_spacing = 1.4
        shade_paragraph(q, fill)
        left_border(q, color=border, size=24)
        r1 = q.add_run(f"{i}. ")
        set_run(r1, size=10.5, bold=True, color=title_color)
        r2 = q.add_run(item)
        set_run(r2, size=10.5, color=TEXT)
    tail = doc.add_paragraph()
    tail.paragraph_format.space_after = Pt(2)


def add_speech(doc, text):
    label = para(doc, "上台可以这么讲（可直接念）", size=9.5, bold=True, color=GOLD,
                 space_before=8, space_after=2)
    label.paragraph_format.keep_with_next = True
    shade_paragraph(label, "FFF2CC")
    left_border(label, color="FFC000", size=24)
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.left_indent = Cm(0.35)
    pf.right_indent = Cm(0.2)
    pf.space_before = Pt(0)
    pf.space_after = Pt(8)
    pf.line_spacing = 1.5
    pf.keep_together = True
    shade_paragraph(p, "FFF2CC")
    left_border(p, color="FFC000", size=24)
    run = p.add_run(text)
    set_run(run, size=10.5, color=RGBColor(0x33, 0x33, 0x33))


def add_table(doc, header, rows, widths):
    table = doc.add_table(rows=1, cols=len(header))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    hdr = table.rows[0]
    for i, text in enumerate(header):
        cell = hdr.cells[i]
        cell.width = Cm(widths[i])
        shade_cell(cell, "005BAC")
        cell_margins(cell)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.2
        run = p.add_run(text)
        set_run(run, size=9.5, bold=True, color=RGBColor(0xFF, 0xFF, 0xFF))
    for ri, row in enumerate(rows):
        cells = table.add_row().cells
        for i, text in enumerate(row):
            cell = cells[i]
            cell.width = Cm(widths[i])
            cell_margins(cell)
            if ri % 2 == 1:
                shade_cell(cell, "F4F8FC")
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.25
            run = p.add_run(text)
            set_run(run, size=9, color=TEXT)
    set_table_layout(table, widths)
    repeat_header(hdr)
    for row in table.rows:
        no_split(row)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return table


def add_kv(doc, rows):
    table = doc.add_table(rows=0, cols=2)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    for label, value in rows:
        cells = table.add_row().cells
        c0, c1 = cells[0], cells[1]
        c0.width = Cm(3.6)
        c1.width = Cm(12.9)
        shade_cell(c0, "EAF4FB")
        cell_margins(c0)
        cell_margins(c1)
        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_after = Pt(0)
        p0.paragraph_format.line_spacing = 1.25
        r0 = p0.add_run(label)
        set_run(r0, size=9.5, bold=True, color=NAVY)
        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_after = Pt(0)
        p1.paragraph_format.line_spacing = 1.35
        r1 = p1.add_run(value)
        set_run(r1, size=9.5, color=TEXT)
    set_table_layout(table, [3.6, 12.9])
    for row in table.rows:
        no_split(row)
    for row in table.rows[:-1]:
        for cell in row.cells:
            for par in cell.paragraphs:
                par.paragraph_format.keep_with_next = True
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def add_qa(doc, items):
    table = doc.add_table(rows=0, cols=2)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    for q, a in items:
        cells = table.add_row().cells
        c0, c1 = cells[0], cells[1]
        c0.width = Cm(5.2)
        c1.width = Cm(11.3)
        shade_cell(c0, "FFF2CC")
        cell_margins(c0)
        cell_margins(c1)
        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_after = Pt(0)
        p0.paragraph_format.line_spacing = 1.3
        r0 = p0.add_run(q)
        set_run(r0, size=9.5, bold=True, color=GOLD)
        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_after = Pt(0)
        p1.paragraph_format.line_spacing = 1.35
        r1 = p1.add_run(a)
        set_run(r1, size=9.5, color=TEXT)
    set_table_layout(table, [5.2, 11.3])
    for row in table.rows:
        no_split(row)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def add_footer_page_number(section):
    footer = section.footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("课题5 · 第 2 次汇报逐页讲解稿 · 第 ")
    set_run(run, size=8.5, color=MUTED)
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = "PAGE"
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run2 = p.add_run()
    set_run(run2, size=8.5, color=MUTED)
    run2._r.append(fld_begin)
    run2._r.append(instr)
    run2._r.append(fld_end)
    run3 = p.add_run(" 页")
    set_run(run3, size=8.5, color=MUTED)


def main():
    spec = json.loads(CONTENT.read_text(encoding="utf-8"))
    doc = Document()
    section = doc.sections[0]
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(1.8)
    section.left_margin = Cm(2.2)
    section.right_margin = Cm(2.2)
    add_footer_page_number(section)

    style = doc.styles["Normal"]
    style.font.name = FONT
    style.font.size = Pt(10.5)
    style.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)

    # title block
    p = para(doc, spec["title"], size=21, bold=True, color=NAVY, space_before=6, space_after=6)
    para(doc, spec["subtitle"], size=11.5, color=BLUE, space_after=4)
    para(doc, spec["meta"], size=9, color=MUTED, space_after=10)
    bottom_border(p, color="FFC000", size=18)

    for block in spec["blocks"]:
        kind = block["type"]
        if kind == "h2":
            add_heading(doc, block["text"], 2)
        elif kind == "h3":
            add_heading(doc, block["text"], 3)
        elif kind == "p":
            para(doc, block["text"], size=10.5, space_after=5)
        elif kind == "callout":
            add_callout(doc, block["title"], block["items"])
        elif kind == "speech":
            add_speech(doc, block["text"])
        elif kind == "table":
            add_table(doc, block["header"], block["rows"], block["widths"])
        elif kind == "kv":
            add_kv(doc, block["rows"])
        elif kind == "qa":
            add_qa(doc, block["items"])
        else:
            raise SystemExit(f"unknown block type: {kind}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT)
    print(f"saved {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
