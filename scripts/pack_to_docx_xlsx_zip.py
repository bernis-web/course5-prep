# -*- coding: utf-8 -*-
"""把交接包合成「一份 docx + 一份 xlsx + 一个 zip」，方便微信直发。"""
import zipfile
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

ROOT = Path(r"D:\projects\course5-prep")
PACK = ROOT / "deliverables" / "PPT交接包"
DOCX = ROOT / "deliverables" / "课题5-PPT制作交接包-20261110.docx"
XLSX = PACK / "03_素材" / "数据源.xlsx"
ZIPF = ROOT / "deliverables" / "课题5-PPT制作交接包-20261110.zip"

FONT = "微软雅黑"
NAVY = RGBColor(0x12, 0x36, 0x5A)
GOLD = RGBColor(0x8A, 0x4B, 0x00)
TEXT = RGBColor(0x1F, 0x2D, 0x3D)
MUTED = RGBColor(0x60, 0x75, 0x8F)

# ── 1. xlsx ──────────────────────────────────────────
SHEETS = {
    "主结果": [["方向", "oPCA", "scVI", "SATURN", "SAMap"],
               ["人→鼠", 0.6435, 0.6683, 0.3522, 0.1127],
               ["鼠→人", 0.6729, 0.5895, 0.2566, 0.0401],
               ["人→斑马鱼", 0.1654, 0.4014, 0.1282, 0.0477],
               ["斑马鱼→人", 0.1512, 0.4290, 0.1386, None],
               ["鼠→斑马鱼", 0.2177, 0.4248, 0.4076, None],
               ["斑马鱼→鼠", 0.4405, 0.4786, 0.2961, None]],
    "标准误": [["方向", "oPCA", "scVI", "SATURN", "SAMap"],
               ["人→鼠", 0.0186, 0.0206, 0.0127, 0.0141],
               ["鼠→人", 0.0215, 0.0140, 0.0140, 0.0051],
               ["人→斑马鱼", 0.0152, 0.0117, 0.0091, 0.0042],
               ["斑马鱼→人", 0.0070, 0.0119, 0.0060, None],
               ["鼠→斑马鱼", 0.0135, 0.0155, 0.0143, None],
               ["斑马鱼→鼠", 0.0144, 0.0114, 0.0116, None]],
    "修正对比": [["方向", "原口径（错）", "修正后", "虚高"],
                 ["人→鼠", 0.4147, 0.3522, 0.0625],
                 ["鼠→人", 0.4010, 0.2566, 0.1444],
                 ["人→斑马鱼", 0.2479, 0.1282, 0.1197],
                 ["斑马鱼→人", 0.4021, 0.1386, 0.2635],
                 ["鼠→斑马鱼", 0.6500, 0.4076, 0.2424],
                 ["斑马鱼→鼠", 0.6510, 0.2961, 0.3549]],
    "跨门": [["方向", "oPCA 准确率", "scVI 准确率", "oPCA macroF1", "scVI macroF1"],
             ["七鳃鳗→小鼠", 0.0575, 0.0582, 0.0235, 0.0241],
             ["小鼠→七鳃鳗", 0.0516, 0.0457, 0.0257, 0.0267]],
    "时间内存": [["方法", "耗时", "内存", "备注"],
                 ["oPCA", "27 秒（六方向）", "1.31 GB", "纯 CPU，确定性"],
                 ["scVI", "CPU 8.5 分钟", "2.37 GB", "平台含 IO 15m16s"],
                 ["SATURN", "—", "—", "需 GPU，平台未记录"],
                 ["SAMap", "5 分 54 秒", "未测", "1c4g 联合嵌入"]],
}

wb = Workbook()
wb.remove(wb.active)
HFILL = PatternFill("solid", fgColor="12365A")
HFONT = Font(name=FONT, size=11, bold=True, color="FFFFFF")
BFONT = Font(name=FONT, size=11, color="1F2D3D")
thin = Side(style="thin", color="D9D9D9")
BORDER = Border(bottom=thin)

for name, rows in SHEETS.items():
    ws = wb.create_sheet(name)
    for ri, row in enumerate(rows, 1):
        for ci, val in enumerate(row, 1):
            c = ws.cell(row=ri, column=ci, value=val)
            c.font = HFONT if ri == 1 else BFONT
            c.alignment = Alignment(horizontal="center", vertical="center")
            if ri == 1:
                c.fill = HFILL
            else:
                c.border = BORDER
                if isinstance(val, float):
                    c.number_format = "0.0000"
    ws.row_dimensions[1].height = 24
    ws.column_dimensions["A"].width = 16
    for ci in range(2, len(rows[0]) + 1):
        ws.column_dimensions[get_column_letter(ci)].width = 15
    ws.freeze_panes = "A2"

XLSX.parent.mkdir(parents=True, exist_ok=True)
wb.save(str(XLSX))
print("xlsx:", XLSX)


# ── 2. 合并 docx ─────────────────────────────────────
def set_run(run, size=10.5, bold=False, color=TEXT):
    run.font.name = FONT
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    rpr = run._element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.append(rf)
    for a in ("w:eastAsia", "w:ascii", "w:hAnsi"):
        rf.set(qn(a), FONT)


doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
sec.top_margin = sec.bottom_margin = Cm(1.7)
sec.left_margin = sec.right_margin = Cm(1.9)

st = doc.styles["Normal"]
st.font.name = FONT
st.font.size = Pt(10.5)
st.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)

props = doc.core_properties
props.title = "课题5 PPT 制作交接包"
props.subject = "交给组员的 PPT 制作说明"
props.author = "课题5 项目组"


def h1(t):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run(t)
    set_run(r, 20, True, NAVY)
    pbdr = OxmlElement("w:pBdr")
    b = OxmlElement("w:bottom")
    b.set(qn("w:val"), "single"); b.set(qn("w:sz"), "12")
    b.set(qn("w:space"), "3"); b.set(qn("w:color"), "FFC000")
    pbdr.append(b)
    p._p.get_or_add_pPr().append(pbdr)


def h2(t):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run(t)
    set_run(r, 13, True, NAVY)


def para(t, size=10.5, color=TEXT, indent=0.0):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.4
    if indent:
        p.paragraph_format.left_indent = Cm(indent)
    r = p.add_run(t)
    set_run(r, size, False, color)
    return p


def bullet(t, indent=0.4):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(indent)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.35
    r0 = p.add_run("· ")
    set_run(r0, 10.5, False, GOLD)
    r1 = p.add_run(t)
    set_run(r1, 10.5)


def table(rows):
    t = doc.add_table(rows=len(rows), cols=len(rows[0]))
    t.style = "Table Grid"
    t.alignment = 1
    for ri, row in enumerate(rows):
        for ci, val in enumerate(row):
            cell = t.cell(ri, ci)
            cell.text = ""
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(str(val))
            set_run(r, 9.5, ri == 0, RGBColor(0xFF, 0xFF, 0xFF) if ri == 0 else TEXT)
            if ri == 0:
                tcPr = cell._tc.get_or_add_tcPr()
                shd = OxmlElement("w:shd")
                shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto")
                shd.set(qn("w:fill"), "12365A")
                tcPr.append(shd)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)


def parse_md(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    i = 0
    while i < len(lines):
        ln = lines[i]
        s = ln.strip()
        if not s:
            i += 1
            continue
        if s.startswith("# "):
            h1(s[2:]); i += 1; continue
        if s.startswith("## "):
            h2(s[3:]); i += 1; continue
        if s.startswith("### "):
            h2(s[4:]); i += 1; continue
        if s.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(set(c) <= set("-: ") for c in cells):
                    rows.append(cells)
                i += 1
            if rows:
                table(rows)
            continue
        if s.startswith("- [ ]") or s.startswith("- [x]"):
            bullet(("□ " if s.startswith("- [ ]") else "☑ ") + s[5:].strip(), 0.3); i += 1; continue
        if s.startswith("- ") or s.startswith("  - "):
            depth = 0.4 if ln.startswith("  - ") else 0.2
            bullet(s.lstrip("- ").strip(), depth); i += 1; continue
        if s.startswith(">"):
            para(s.lstrip("> ").strip(), 10, MUTED); i += 1; continue
        para(s)
        i += 1


# 封面
p = doc.add_paragraph()
p.paragraph_format.space_after = Pt(2)
r = p.add_run("课题5 第三次汇报")
set_run(r, 26, True, NAVY)
p = doc.add_paragraph()
p.paragraph_format.space_after = Pt(14)
r = p.add_run("PPT 制作交接包 · 2026-11-10")
set_run(r, 15, False, GOLD)
para("这份包给做 PPT 的同学：数字、结构、模板规范全在这里，你不需要懂单细胞分析。", 11, MUTED)

for f in ["00_README.md", "01_大纲.md", "02_逐页brief.md", "04_模板规范.md", "05_验收清单.md"]:
    p = PACK / f
    if p.exists():
        parse_md(p)

# 数据表附在最后
h1("附：数据源（与 03_素材/数据源.xlsx 一致）")
for name, rows in SHEETS.items():
    h2(name)
    table([[str(x) if x is not None else "—" for x in r] for r in rows])

DOCX.parent.mkdir(parents=True, exist_ok=True)
doc.save(str(DOCX))
print("docx:", DOCX)

# ── 3. zip ───────────────────────────────────────────
if ZIPF.exists():
    ZIPF.unlink()
with zipfile.ZipFile(ZIPF, "w", zipfile.ZIP_DEFLATED) as z:
    for f in sorted(PACK.rglob("*")):
        if f.is_file():
            z.write(f, f.relative_to(PACK.parent))
    z.write(DOCX, DOCX.name)
print("zip:", ZIPF, ZIPF.stat().st_size, "B")