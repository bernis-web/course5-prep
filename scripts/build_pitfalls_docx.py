"""Render the master handoff (Markdown) to a styled DOCX.

Run with the SYSTEM python (python-docx lives there, not in .venv39):
    python scripts/build_master_handoff_docx.py

Parses the specific subset of Markdown used in 20261028-master-handoff.md:
  headings (#/##/###), paragraphs, bullet lists, numbered lists,
  pipe tables, blockquotes, and inline `code` / **bold**.
"""

from __future__ import annotations

import re
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "docs" / "execution" / "20261030-pitfalls.md"
OUT = ROOT / "deliverables" / "课题5-踩坑清单-20261030.docx"

FONT = "微软雅黑"
NAVY = RGBColor(0x12, 0x36, 0x5A)
BLUE = RGBColor(0x00, 0x5B, 0xAC)
TEXT = RGBColor(0x1F, 0x2D, 0x3D)
MUTED = RGBColor(0x5A, 0x6B, 0x80)
CODE = RGBColor(0x8A, 0x2B, 0x2B)


def set_run(run, size=10, bold=False, color=TEXT, name=FONT):
    run.font.name = name
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    for attr in ("w:eastAsia", "w:ascii", "w:hAnsi"):
        rfonts.set(qn(attr), name)


def shade(el_pr, fill):
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    el_pr.append(shd)


def left_border(paragraph, color="005BAC", size=18):
    ppr = paragraph._p.get_or_add_pPr()
    pbdr = OxmlElement("w:pBdr")
    left = OxmlElement("w:left")
    left.set(qn("w:val"), "single")
    left.set(qn("w:sz"), str(size))
    left.set(qn("w:space"), "6")
    left.set(qn("w:color"), color)
    pbdr.append(left)
    ppr.append(pbdr)


def bottom_border(paragraph, color="005BAC", size=8):
    ppr = paragraph._p.get_or_add_pPr()
    pbdr = OxmlElement("w:pBdr")
    b = OxmlElement("w:bottom")
    b.set(qn("w:val"), "single")
    b.set(qn("w:sz"), str(size))
    b.set(qn("w:space"), "2")
    b.set(qn("w:color"), color)
    pbdr.append(b)
    ppr.append(pbdr)


INLINE = re.compile(r"(`[^`]+`|\*\*[^*]+\*\*)")


def add_rich(paragraph, text, size=10, color=TEXT, base_bold=False):
    """Render inline `code` and **bold**, including code nested inside bold."""
    for part in INLINE.split(text):
        if not part:
            continue
        if part.startswith("`") and part.endswith("`") and len(part) > 2:
            run = paragraph.add_run(part[1:-1])
            set_run(run, size=size - 0.8, color=CODE, bold=base_bold)
        elif part.startswith("**") and part.endswith("**") and len(part) > 4:
            inner = part[2:-2]
            # code may be nested inside bold
            for sub in re.split(r"(`[^`]+`)", inner):
                if not sub:
                    continue
                if sub.startswith("`") and sub.endswith("`"):
                    run = paragraph.add_run(sub[1:-1])
                    set_run(run, size=size - 0.5, color=CODE, bold=True)
                else:
                    run = paragraph.add_run(sub)
                    set_run(run, size=size, bold=True, color=color)
        else:
            run = paragraph.add_run(part)
            set_run(run, size=size, bold=base_bold, color=color)


def add_table(doc, rows):
    header = [c.strip() for c in rows[0]]
    body = [[c.strip() for c in r] for r in rows[1:]]
    table = doc.add_table(rows=1, cols=len(header))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    ncol = len(header)
    total = 16.5
    def wlen(t):
        t = str(t)
        return sum(2 if ord(ch) > 0x2E80 else 1 for ch in t)
    raw = []
    for c in range(ncol):
        lens = [wlen(header[c])] + [wlen(r[c]) if c < len(r) else 1 for r in body]
        raw.append(max(3, max(lens)))
    mean = sum(raw) / ncol
    raw = [min(max(v, mean * 0.6), mean * 1.9) for v in raw]
    tot = sum(raw)
    widths = [total * v / tot for v in raw]
    tbl = table._tbl
    layout = OxmlElement("w:tblLayout")
    layout.set(qn("w:type"), "fixed")
    tbl.tblPr.append(layout)
    grid = tbl.tblGrid
    for i, w in enumerate(widths):
        grid.gridCol_lst[i].set(qn("w:w"), str(int(w * 567)))

    hdr = table.rows[0]
    for i, text in enumerate(header):
        cell = hdr.cells[i]
        cell.width = Cm(widths[i])
        shade(cell._tc.get_or_add_tcPr(), "005BAC")
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.15
        add_rich(p, text, size=8.5, color=RGBColor(0xFF, 0xFF, 0xFF), base_bold=True)
    trpr = hdr._tr.get_or_add_trPr()
    el = OxmlElement("w:tblHeader")
    el.set(qn("w:val"), "true")
    trpr.append(el)

    for ri, row in enumerate(body):
        new_row = table.add_row()
        trp = new_row._tr.get_or_add_trPr()
        trp.append(OxmlElement("w:cantSplit"))
        cells = new_row.cells
        for i in range(ncol):
            text = row[i] if i < len(row) else ""
            cell = cells[i]
            cell.width = Cm(widths[i])
            if ri % 2 == 1:
                shade(cell._tc.get_or_add_tcPr(), "F4F8FC")
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.2
            add_rich(p, text, size=8.5)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def split_row(line):
    inner = line.strip().strip("|")
    return [c for c in inner.split("|")]


def is_sep(line):
    return bool(re.match(r"^\s*\|?[\s:\-|]+\|[\s:\-|]*$", line)) and "-" in line


def main() -> int:
    lines = SRC.read_text(encoding="utf-8").splitlines()
    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
    sec.top_margin = sec.bottom_margin = Cm(1.9)
    sec.left_margin = sec.right_margin = Cm(2.0)

    style = doc.styles["Normal"]
    style.font.name = FONT
    style.font.size = Pt(10)
    style.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)

    # footer page number
    footer_p = sec.footer.paragraphs[0]
    footer_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = footer_p.add_run("课题5 踩坑清单 · 第 ")
    set_run(r, size=8, color=MUTED)
    fb = OxmlElement("w:fldChar"); fb.set(qn("w:fldCharType"), "begin")
    it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve"); it.text = "PAGE"
    fe = OxmlElement("w:fldChar"); fe.set(qn("w:fldCharType"), "end")
    r2 = footer_p.add_run(); set_run(r2, size=8, color=MUTED)
    r2._r.append(fb); r2._r.append(it); r2._r.append(fe)
    r3 = footer_p.add_run(" 页"); set_run(r3, size=8, color=MUTED)

    i = 0
    first_h1 = True
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if stripped.startswith("```"):
            i += 1
            buf = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1  # closing fence
            for code_line in buf:
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Cm(0.4)
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 1.2
                shade(p._p.get_or_add_pPr(), "F2F5F8")
                run = p.add_run(code_line if code_line.strip() else " ")
                set_run(run, size=9, color=CODE, name="Consolas")
            spacer = doc.add_paragraph()
            spacer.paragraph_format.space_after = Pt(4)
            continue

        if stripped == "---":
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            bottom_border(p, color="D6E2EF", size=6)
            i += 1
            continue

        if stripped.startswith("# "):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(8)
            run = p.add_run(stripped[2:])
            set_run(run, size=22, bold=True, color=NAVY)
            bottom_border(p, color="FFC000", size=16)
            first_h1 = False
            i += 1
            continue

        if stripped.startswith("## "):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(14)
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.keep_with_next = True
            add_rich(p, stripped[3:], size=14, color=NAVY, base_bold=True)
            bottom_border(p)
            i += 1
            continue

        if stripped.startswith("### "):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.keep_with_next = True
            add_rich(p, stripped[4:], size=11.5, color=BLUE, base_bold=True)
            i += 1
            continue

        if stripped.startswith("|") and i + 1 < len(lines) and is_sep(lines[i + 1]):
            rows = [split_row(stripped)]
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(split_row(lines[i]))
                i += 1
            add_table(doc, rows)
            continue

        if stripped.startswith(">"):
            buf = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip().lstrip(">").strip())
                i += 1
            text = " ".join(x for x in buf if x)
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(0.3)
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.line_spacing = 1.35
            shade(p._p.get_or_add_pPr(), "EAF4FB")
            left_border(p, size=18)
            add_rich(p, text, size=9.5, color=MUTED)
            continue

        if re.match(r"^\s*[-*]\s+", line):
            while i < len(lines) and re.match(r"^\s*[-*]\s+", lines[i]):
                text = re.sub(r"^\s*[-*]\s+", "", lines[i])
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Cm(0.55)
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.line_spacing = 1.35
                r0 = p.add_run("• ")
                set_run(r0, size=10, color=BLUE)
                add_rich(p, text, size=10)
                i += 1
            continue

        if re.match(r"^\s*\d+\.\s+", line):
            while i < len(lines) and re.match(r"^\s*\d+\.\s+", lines[i]):
                m = re.match(r"^\s*(\d+)\.\s+(.*)$", lines[i])
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Cm(0.55)
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.line_spacing = 1.35
                r0 = p.add_run(f"{m.group(1)}. ")
                set_run(r0, size=10, bold=True, color=BLUE)
                add_rich(p, m.group(2), size=10)
                i += 1
            continue

        # plain paragraph (possibly multi-line until blank)
        buf = [stripped]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(
            r"^\s*(#|\||>|[-*]\s|\d+\.\s|```)", lines[i]
        ):
            buf.append(lines[i].strip())
            i += 1
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(5)
        p.paragraph_format.line_spacing = 1.45
        add_rich(p, " ".join(buf), size=10)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT)
    print(f"saved {OUT} ({OUT.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
