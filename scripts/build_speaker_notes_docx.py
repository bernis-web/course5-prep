# -*- coding: utf-8 -*-
"""从讲故事版 PPT 的备注里抽出「逐页讲稿单」docx（可打印）。

输出：deliverables/课题5-汇报讲稿-20261110.docx
每页三块：页码 + 页面观点（从首行文字取）+ 讲稿（备注原文）
"""
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from pptx import Presentation

ROOT = Path(r"D:\projects\course5-prep")
import sys
PPTX = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "deliverables" / "课题5-汇报-讲故事版-20261110.pptx"
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "deliverables" / "课题5-汇报讲稿-20261110.docx"
DATE = sys.argv[3] if len(sys.argv) > 3 else "2026-11-11"

FONT = "微软雅黑"
NAVY = RGBColor(0x0E, 0x1B, 0x2A)
GOLD = RGBColor(0xC9, 0x96, 0x2B)
TEXT = RGBColor(0x1F, 0x2D, 0x3D)
MUTED = RGBColor(0x6B, 0x77, 0x85)


def set_run(run, size=11, bold=False, color=TEXT, name=FONT):
    run.font.name = name
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    rpr = run._element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.append(rf)
    for a in ("w:eastAsia", "w:ascii", "w:hAnsi"):
        rf.set(qn(a), name)


prs = Presentation(str(PPTX))
doc = Document()

sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
sec.top_margin = sec.bottom_margin = Cm(1.7)
sec.left_margin = sec.right_margin = Cm(1.9)

style = doc.styles["Normal"]
style.font.name = FONT
style.font.size = Pt(11)
style.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)

props = doc.core_properties
props.title = "课题5 汇报讲稿"
props.subject = "逐页讲稿（配套讲故事版 PPT）"
props.author = "课题5 项目组"

# 标题
p = doc.add_paragraph()
p.paragraph_format.space_after = Pt(4)
r = p.add_run("课题5 汇报 · 逐页讲稿")
set_run(r, size=24, bold=True, color=NAVY)

p = doc.add_paragraph()
p.paragraph_format.space_after = Pt(14)
r = p.add_run("配套文件：%s　｜　用法：拿着纸念，不要看屏幕" % PPTX.name)
set_run(r, size=9.5, color=MUTED)

# 使用说明
p = doc.add_paragraph()
p.paragraph_format.space_before = Pt(2)
p.paragraph_format.space_after = Pt(10)
r = p.add_run("三条提醒")
set_run(r, size=12, bold=True, color=GOLD)

tips = [
    "方括号【】里的是动作提示，不要念出来。",
    "每页只讲一个观点；讲完停一秒再翻页——停顿比语速重要。",
    "被问到不会的，就说「这个我们没测，不能给结论」，比编一个强。",
]
for t in tips:
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.5)
    p.paragraph_format.space_after = Pt(3)
    r0 = p.add_run("· ")
    set_run(r0, size=11, color=GOLD)
    r1 = p.add_run(t)
    set_run(r1, size=10.5)

# 分隔
p = doc.add_paragraph()
p.paragraph_format.space_before = Pt(8)
p.paragraph_format.space_after = Pt(10)
pbdr = OxmlElement("w:pBdr")
b = OxmlElement("w:bottom")
b.set(qn("w:val"), "single"); b.set(qn("w:sz"), "8")
b.set(qn("w:space"), "2"); b.set(qn("w:color"), "C9962B")
pbdr.append(b)
p._p.get_or_add_pPr().append(pbdr)


def slide_headline(slide):
    """取「页面标题」当观点。

    不能用「最大字号」：数字页（如 P08）最大的字是英雄数字
    （27 s / 8.5 min / GPU，40pt），那是正文不是标题，会把标题抓成 "27 s"。
    标题的机器特征更稳：**字号 >= 20pt 且位置最靠上**。
    没命中时回退到「最大字号」，再不行才留空。
    """
    cands = []
    fallback, fsize = "", 0
    for sh in slide.shapes:
        if not sh.has_text_frame:
            continue
        for para in sh.text_frame.paragraphs:
            t = para.text.strip()
            if not t:
                continue
            sz = max((r.font.size.pt for r in para.runs if r.font.size), default=0)
            if sz > fsize:
                fallback, fsize = t, sz
            if sz >= 20:
                cands.append((sh.top, -sz, t))
    if cands:
        cands.sort()
        return cands[0][2], -cands[0][1]
    return fallback, fsize


for i, slide in enumerate(prs.slides, 1):
    note = slide.notes_slide.notes_text_frame.text.strip() if slide.has_notes_slide else ""
    head, _ = slide_headline(slide)

    # 页码 + 观点
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    r0 = p.add_run(f"P{i:02d}　")
    set_run(r0, size=10, bold=True, color=GOLD)
    r1 = p.add_run(head.replace("\n", " ") if head else "（图/表页）")
    set_run(r1, size=13, bold=True, color=NAVY)

    # 讲稿
    body = note if note else "（本页无备注，按页面内容即兴说明）"
    for ln in body.split("\n"):
        pp = doc.add_paragraph()
        pp.paragraph_format.space_before = Pt(0)
        pp.paragraph_format.space_after = Pt(2)
        pp.paragraph_format.line_spacing = 1.45
        rr = pp.add_run(ln if ln.strip() else " ")
        set_run(rr, size=11, color=TEXT if ln.strip() else MUTED)

    # 轻分隔
    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(2)
    sp.paragraph_format.space_after = Pt(2)
    pbdr = OxmlElement("w:pBdr")
    b = OxmlElement("w:bottom")
    b.set(qn("w:val"), "single"); b.set(qn("w:sz"), "4")
    b.set(qn("w:space"), "1"); b.set(qn("w:color"), "E2DCCF")
    pbdr.append(b)
    sp._p.get_or_add_pPr().append(pbdr)

# 页脚
footer = doc.sections[0].footer.paragraphs[0]
footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
fr = footer.add_run("课题5 汇报讲稿 · 共 %d 页 · %s" % (len(prs.slides), DATE))
set_run(fr, size=8, color=MUTED)

OUT.parent.mkdir(parents=True, exist_ok=True)
doc.save(str(OUT))
print("saved:", OUT, OUT.stat().st_size, "bytes")