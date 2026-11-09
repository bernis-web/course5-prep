"""Render the teammate handoff overview (Markdown) to a styled DOCX.

Same visual system as scripts/build_master_handoff_docx.py (this repo's
convention is one builder per deliverable), retargeted at
docs/execution/20261104-队友交接总纲.md.

Run with the SYSTEM python (python-docx lives there, not in .venv39):
    python scripts/build_team_handoff_overview_docx.py

Parses the specific subset of Markdown used in the overview:
  headings (#/##/###), paragraphs, bullet lists, numbered lists,
  pipe tables, blockquotes, fenced code, inline `code` / **bold**.
Emoji status marks are rewritten to plain text so the DOCX renders
without depending on an emoji font.
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
SRC = ROOT / "docs" / "team-handbook" / "part4-汇报说明小白版.md"
OUT = ROOT / "deliverables" / "课题5-组员汇报说明-小白版-20261110.docx"

FONT = "微软雅黑"
NAVY = RGBColor(0x12, 0x36, 0x5A)
BLUE = RGBColor(0x00, 0x5B, 0xAC)
TEXT = RGBColor(0x1F, 0x2D, 0x3D)
MUTED = RGBColor(0x5A, 0x6B, 0x80)
CODE = RGBColor(0x8A, 0x2B, 0x2B)

# 状态标记改成文字，避免依赖 emoji 字体
SANITIZE = [
    ("⚠️", "注意："),
    ("⚠", "注意："),
    ("✅", "○"),
    ("⏳", "[待做]"),
    ("❌", "×"),
    ("🔒", "[锁]"),
]


def san(text: str) -> str:
    for a, b in SANITIZE:
        text = text.replace(a, b)
    return text


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
    text = san(text)
    for part in INLINE.split(text):
        if not part:
            continue
        if part.startswith("`") and part.endswith("`") and len(part) > 2:
            run = paragraph.add_run(part[1:-1])
            set_run(run, size=size - 0.5, color=CODE, bold=base_bold)
        elif part.startswith("**") and part.endswith("**") and len(part) > 4:
            inner = part[2:-2]
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
        t = san(str(t))
        return sum(2 if ord(ch) > 0x2E80 else 1 for ch in t)

    # 用 90 分位而不是最大值估列宽：长路径/大表格不会把别的列挤成一条缝，
    # 同时给最宽那列塞下更多字符，避免 /Files/RawData/xxx.h5ad 被拆成三行。
    raw = []
    for c in range(ncol):
        lens = sorted(wlen(r[c]) if c < len(r) else 1 for r in body) or [3]
        mx = lens[-1]
        # 短内容列用最大值（别把 smooth_muscle、人名的中间拆开），
        # 长内容列用 90 分位（长路径不至于把整张表挤坏）
        est = mx if mx <= 24 else lens[min(len(lens) - 1, int(len(lens) * 0.9))]
        raw.append(max(3, max(est, wlen(header[c]))))
    # 直接折算成厘米再等比缩放：1 个宽度单位≈0.17cm（8.5pt 下文一个西文字符），
    # 每列给下限 1.5cm、上限 7.0cm，避免长列把短列压得拆词。
    cm = [max(1.5, min(v * 0.17, 7.0)) for v in raw]
    tot = sum(cm)
    widths = [total * v / tot for v in cm]
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
    props = doc.core_properties
    props.title = "课题5 组员汇报说明（小白版）"
    props.subject = "跨物种单细胞整合基准测试 — 组员汇报说明"
    props.author = "课题5 项目组"
    props.comments = (
        "由 docs/execution/20261104-队友交接总纲.md 渲染；"
        "数字来自 results/*/metrics.json 与 docs/execution/20261028-master-handoff.md"
    )

    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
    sec.top_margin = sec.bottom_margin = Cm(1.9)
    sec.left_margin = sec.right_margin = Cm(2.0)

    style = doc.styles["Normal"]
    style.font.name = FONT
    style.font.size = Pt(10)
    style.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)

    footer_p = sec.footer.paragraphs[0]
    footer_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = footer_p.add_run("课题5 组员汇报说明（小白版） · 第 ")
    set_run(r, size=8, color=MUTED)
    fb = OxmlElement("w:fldChar")
    fb.set(qn("w:fldCharType"), "begin")
    it = OxmlElement("w:instrText")
    it.set(qn("xml:space"), "preserve")
    it.text = "PAGE"
    fe = OxmlElement("w:fldChar")
    fe.set(qn("w:fldCharType"), "end")
    r2 = footer_p.add_run()
    set_run(r2, size=8, color=MUTED)
    r2._r.append(fb)
    r2._r.append(it)
    r2._r.append(fe)
    r3 = footer_p.add_run(" 页")
    set_run(r3, size=8, color=MUTED)

    i = 0
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
            i += 1
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
            add_rich(p, stripped[2:], size=22, color=NAVY, base_bold=True)
            bottom_border(p, color="FFC000", size=16)
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
            deferred = []
            while i < len(lines):
                s = lines[i].strip()
                if s.startswith("|"):
                    rows.append(split_row(s))
                    i += 1
                elif s == "":
                    # 空行只在"后面还是表格行"时跳过，否则表格结束
                    j = i + 1
                    while j < len(lines) and not lines[j].strip():
                        j += 1
                    if j < len(lines) and lines[j].strip().startswith(("|", ">")):
                        i += 1
                        continue
                    break
                elif s.startswith(">"):
                    # 表格中间夹的引用块：先记下，等表格画完再排，
                    # 否则后续行会被当成新表头或散段落
                    deferred.append(s.lstrip(">").strip())
                    i += 1
                else:
                    break
            add_table(doc, rows)
            joined = " ".join(x for x in deferred if x)
            if joined:
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Cm(0.3)
                p.paragraph_format.space_before = Pt(4)
                p.paragraph_format.space_after = Pt(6)
                p.paragraph_format.line_spacing = 1.35
                shade(p._p.get_or_add_pPr(), "EAF4FB")
                left_border(p, size=18)
                add_rich(p, joined, size=9.5, color=MUTED)
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
