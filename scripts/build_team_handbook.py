#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
把 docs/team-handbook/part1..3.md 拼成一本带目录的 Word。
三片井号层级不一致，所以按语义（是不是"第 N 章" / "Q\d"）判，不按 # 个数。
"""
import re, os, glob, json
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BASE = r"D:\projects\course5-prep"
SRC = os.path.join(BASE, "docs", "team-handbook")
OUT = os.path.join(BASE, "deliverables", "课题5-组员入门手册-20261104.docx")
TOC_CACHE = os.path.join(SRC, "_toc_pages.json")

PAGES = {}
if os.path.exists(TOC_CACHE):
    with open(TOC_CACHE, encoding='utf-8') as _f:
        PAGES = json.load(_f)

def norm_heading(text):
    """返回 (级别, 纯文本)；级别 1=章 2=节 3=子节；0=片分隔（丢弃）"""
    t = text.strip()
    if re.search(r'第\s*\d+\s*章', t): return 1, t
    if re.match(r'^Q\d+', t): return 2, t
    if '片' in t and ('手册' in t or re.search(r'第\s*\d+\s*片', t)): return 0, t
    return None, t

def scan_outline(paths):
    out = []
    for p in paths:
        for line in open(p, encoding='utf-8').read().split('\n'):
            m = re.match(r'^(#{1,4})\s+(.*)$', line)
            if not m: continue
            lvl, txt = norm_heading(m.group(2))
            if lvl == 0: continue
            if lvl is None: lvl = min(len(m.group(1)), 3)
            # 「3.1」「4.2」这种不管原来几个井号，都是节（二级）
            if lvl == 3 and re.match(r'^\d+\.\d+', txt.strip()): lvl = 2
            if lvl <= 2: out.append((lvl, txt.strip()))
    return out

PARTS = [os.path.join(SRC, 'part1-问题与方法.md'),
         os.path.join(SRC, 'part2-口径陷阱与三场景.md'),
         os.path.join(SRC, 'part3-可复现与FAQ.md')]
OUTLINE = scan_outline([p for p in PARTS if os.path.exists(p)])

C_MAIN   = RGBColor(0x1F, 0x3B, 0x73)   # 深蓝，跟校模板一个色系
C_ACCENT = RGBColor(0xC0, 0x50, 0x00)   # 橙棕，强调
C_GREY   = RGBColor(0x59, 0x59, 0x59)

# ─────────── 底层样式工具 ───────────
def set_cell_bg(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear'); shd.set(qn('w:color'), 'auto'); shd.set(qn('w:fill'), hexcolor)
    tcPr.append(shd)

def set_font(run, size=None, bold=None, color=None, ascii_font='Consolas'):
    if size is not None: run.font.size = Pt(size)
    if bold is not None: run.font.bold = bold
    if color is not None: run.font.color.rgb = color
    run.font.name = ascii_font
    run._element.rPr.rFonts.set(qn('w:eastAsia'), '微软雅黑' if size and size > 12 else '等线')

def para(doc, text='', size=10.5, bold=False, color=None, align=None, space_before=0, space_after=4, indent=None, line=1.45):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(space_before); pf.space_after = Pt(space_after)
    pf.line_spacing = line
    if indent: pf.first_line_indent = Cm(indent)
    if align: p.alignment = align
    if text:
        r = p.add_run(text); set_font(r, size, bold, color)
    return p

INLINE = re.compile(r'(\*\*.+?\*\*|`[^`]+`)')
def rich(p, text, size=10.5, base_color=None):
    """渲染 **粗体** 和 `代码`"""
    for seg in INLINE.split(text):
        if not seg: continue
        if seg.startswith('**') and seg.endswith('**'):
            r = p.add_run(seg[2:-2]); set_font(r, size, True, base_color or C_MAIN)
        elif seg.startswith('`') and seg.endswith('`'):
            r = p.add_run(seg[1:-1]); set_font(r, size - 0.5, False, RGBColor(0x8B, 0x1A, 0x1A), 'Consolas')
        else:
            r = p.add_run(seg); set_font(r, size, False, base_color)

# ─────────── 文档骨架 ───────────
doc = Document()
sec = doc.sections[0]
sec.page_width  = Cm(21.0); sec.page_height = Cm(29.7)
sec.left_margin = sec.right_margin = Cm(2.4)
sec.top_margin  = Cm(2.2); sec.bottom_margin = Cm(2.0)

st = doc.styles['Normal']
st.font.name = '等线'; st.font.size = Pt(10.5)
st._element.rPr.rFonts.set(qn('w:eastAsia'), '等线')

for i, sz in ((1, 19), (2, 14), (3, 12)):
    h = doc.styles['Heading %d' % i]
    h.font.name = '微软雅黑'; h.font.size = Pt(sz); h.font.bold = True
    h.font.color.rgb = C_MAIN
    h._element.rPr.rFonts.set(qn('w:eastAsia'), '微软雅黑')
    h.paragraph_format.space_before = Pt(16 if i == 1 else 11)
    h.paragraph_format.space_after  = Pt(8 if i == 1 else 5)

# 页脚页码
def add_footer_page_number(section):
    p = section.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(); set_font(r, 9, False, C_GREY)
    for el, attr in (('w:fldChar', 'begin'), ('w:instrText', None), ('w:fldChar', 'end')):
        e = OxmlElement(el)
        if el == 'w:fldChar': e.set(qn('w:fldCharType'), attr)
        else: e.set(qn('xml:space'), 'preserve'); e.text = ' PAGE '
        r._r.append(e)
add_footer_page_number(sec)

# ─────────── 封面 ───────────
for _ in range(5): doc.add_paragraph()
para(doc, '课题 5 · XenoTransfer v1.0', 12, False, C_GREY, WD_ALIGN_PARAGRAPH.CENTER, space_after=6)
p = para(doc, '', align=WD_ALIGN_PARAGRAPH.CENTER, space_after=4)
r = p.add_run('组员入门手册'); set_font(r, 34, True, C_MAIN)
p = para(doc, '', align=WD_ALIGN_PARAGRAPH.CENTER, space_after=18)
r = p.add_run('跨物种单细胞整合：把这套流程讲到小白能复述'); set_font(r, 13, False, C_GREY)
para(doc, '—— 给没做过单细胞分析的组员 ——', 11, False, C_ACCENT, WD_ALIGN_PARAGRAPH.CENTER, space_before=6)
for _ in range(9): doc.add_paragraph()
para(doc, '课题 5  第三次汇报配套材料', 10.5, False, C_GREY, WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
para(doc, '2026-11-04', 10.5, False, C_GREY, WD_ALIGN_PARAGRAPH.CENTER)
doc.add_page_break()

# ─────────── 目录（静态，带真页码）───────────
h = doc.add_paragraph(); h.style = doc.styles['Heading 1']
r = h.add_run('目　录'); set_font(r, 19, True, C_MAIN)

if not PAGES:
    para(doc, '（首次排版，页码待回填；见 build 第二遍）', 9, False, C_GREY, space_after=8)

for lvl, txt in OUTLINE:
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(7 if lvl == 1 else 0)
    pf.space_after = Pt(2)
    pf.line_spacing = 1.25
    if lvl == 2: pf.left_indent = Cm(0.9)
    pf.tab_stops.add_tab_stop(Cm(15.8), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
    r = p.add_run(txt)
    set_font(r, 11.5 if lvl == 1 else 10, lvl == 1,
             C_MAIN if lvl == 1 else RGBColor(0x33, 0x33, 0x33))
    pn = PAGES.get(txt)
    r2 = p.add_run('\t' + (str(pn) if pn else ''))
    set_font(r2, 10.5, lvl == 1, C_GREY)

doc.add_page_break()

# ─────────── 解析 markdown ───────────
def emit_table(doc, rows):
    if not rows: return
    ncol = max(len(r) for r in rows)
    rows = [r + [''] * (ncol - len(r)) for r in rows]
    tb = doc.add_table(rows=len(rows), cols=ncol)
    tb.style = 'Table Grid'
    tb.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, row in enumerate(rows):
        for j, cell in enumerate(row):
            c = tb.cell(i, j)
            c.text = ''
            pp = c.paragraphs[0]
            pp.paragraph_format.space_before = Pt(2); pp.paragraph_format.space_after = Pt(2)
            if i == 0:
                set_cell_bg(c, '1F3B73')
                pp.alignment = WD_ALIGN_PARAGRAPH.CENTER
                rich(pp, cell, 9.5, RGBColor(0xFF, 0xFF, 0xFF))
                for run in pp.runs:
                    run.font.bold = True; run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            else:
                if i % 2 == 0: set_cell_bg(c, 'F2F5FA')
                rich(pp, cell, 9.5)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)

def md_to_docx(path, doc):
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.read().split('\n')

    i = 0
    buf_table = []
    while i < len(lines):
        ln = lines[i]
        s = ln.rstrip()

        # 表格
        if s.startswith('|') and s.count('|') >= 2:
            cells = [c.strip() for c in s.strip().strip('|').split('|')]
            if all(re.fullmatch(r':?-{2,}:?', c) for c in cells if c):
                i += 1; continue
            buf_table.append(cells); i += 1
            if i >= len(lines) or not lines[i].rstrip().startswith('|'):
                emit_table(doc, buf_table); buf_table = []
            continue
        else:
            if buf_table: emit_table(doc, buf_table); buf_table = []

        if not s.strip():
            i += 1; continue
        if s.strip() in ('---', '***', '___'):
            i += 1; continue

        # 标题
        m = re.match(r'^(#{1,4})\s+(.*)$', s)
        if m:
            lvl, txt = norm_heading(m.group(2))
            if lvl == 0:
                i += 1; continue
            if lvl is None:
                lvl = min(len(m.group(1)), 3)
            # 「3.1」「4.2」这类是节，不是三级子标题
            if lvl == 3 and re.match(r'^\d+\.\d+', txt.strip()): lvl = 2
            h = doc.add_paragraph(); h.style = doc.styles['Heading %d' % lvl]
            rich(h, txt, {1: 19, 2: 14, 3: 12}[lvl], C_MAIN)
            for run in h.runs:
                run.font.bold = True; run.font.color.rgb = C_MAIN
            i += 1; continue

        # 引用
        if s.startswith('>'):
            txt = s.lstrip('>').strip()
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(0.6)
            p.paragraph_format.space_before = Pt(4); p.paragraph_format.space_after = Pt(4)
            rich(p, txt, 9.5, C_GREY)
            pPr = p._p.get_or_add_pPr()
            bd = OxmlElement('w:pBdr'); lf = OxmlElement('w:left')
            lf.set(qn('w:val'), 'single'); lf.set(qn('w:sz'), '18')
            lf.set(qn('w:space'), '8'); lf.set(qn('w:color'), 'C05000')
            bd.append(lf); pPr.append(bd)
            i += 1; continue

        # 无序列表
        m = re.match(r'^(\s*)[-*+]\s+(.*)$', s)
        if m:
            depth = len(m.group(1)) // 2
            p = doc.add_paragraph(style='List Bullet' if depth == 0 else 'List Bullet 2')
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.line_spacing = 1.4
            rich(p, m.group(2), 10.5)
            i += 1; continue

        # 有序列表
        m = re.match(r'^(\s*)(\d+)[.)]\s+(.*)$', s)
        if m:
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(0.9)
            p.paragraph_format.first_line_indent = Cm(-0.5)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.line_spacing = 1.4
            r = p.add_run(m.group(2) + '. '); set_font(r, 10.5, True, C_MAIN)
            rich(p, m.group(3), 10.5)
            i += 1; continue

        # 普通段落
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(5)
        p.paragraph_format.line_spacing = 1.45
        p.paragraph_format.first_line_indent = Cm(0.74)
        rich(p, s.strip(), 10.5)
        i += 1

    if buf_table: emit_table(doc, buf_table)


parts = PARTS

for k, f in enumerate(parts):
    if not os.path.exists(f):
        print('缺文件:', f); continue
    if k > 0: doc.add_page_break()
    md_to_docx(f, doc)

doc.save(OUT)
print('已生成:', OUT)
print('大小: %.1f KB' % (os.path.getsize(OUT) / 1024))
print('段落数:', len(doc.paragraphs), '| 表格数:', len(doc.tables))
