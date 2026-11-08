# -*- coding: utf-8 -*-
"""
课题5 第3次汇报 —— 视觉改造 v2（去 AI 味 / 字号阶梯 4 档 / 版式分化）
硬约束：
  1. 文字、数字、结论一字不改（全部从 _content.json 取，逐字断言）
  2. 保留学校模板：slideMaster + DEFAULT 版式 + 封面背景图 + 顶栏 bar-blue/bar-gold + 校徽
  3. 输出 _candidate2.pptx，不覆盖正式文件
只改视觉：字号 40/28/16/12 + 数字档 52；三线表；结论下沉为页脚一行；留白 ≥25%。
"""
import json, os, re, math, shutil

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.enum.shapes import MSO_SHAPE, MSO_SHAPE_TYPE
from pptx.oxml.ns import qn
from lxml import etree

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, '课题5第03次汇报_三场景结论与可复现闭环.pptx')
DST = os.path.join(BASE, '_candidate2.pptx')
CONTENT = json.load(open(os.path.join(BASE, '_content.json'), encoding='utf-8'))

# ══════════════════════════ 设计令牌 ══════════════════════════
NAVY   = '12365A'
BODY   = '1F2D3D'
MUTED  = '60758F'
ACCENT = '8A4B00'
RULE_C = 'B7C9D6'
WHITE  = 'FFFFFF'
CJK    = '微软雅黑'
MONO   = 'Consolas'

S_COVER, S_TITLE, S_BODY, S_NOTE = 40, 28, 16, 12
S_HERO = 52

L, CW = 0.75, 11.833
R = L + CW
TITLE_Y, TITLE_H = 1.02, 0.56
LEAD_Y = 1.62
BAND_TOP, BAND_BOT = 2.26, 6.30
BAND_H = BAND_BOT - BAND_TOP
FOOT_RULE_Y = 6.72
FOOT_Y = 6.80
PROSE_W = 7.80

WARN = []

# ══════════════════════════ 度量 ══════════════════════════
def charw(ch, mono=False):
    if ord(ch) >= 0x2E80:
        return 1.0
    if mono:
        return 0.55
    if ch == ' ':
        return 0.30
    if ch.isdigit():
        return 0.56
    if 'A' <= ch <= 'Z':
        return 0.66
    if 'a' <= ch <= 'z':
        return 0.53
    if ch in '±×÷→←↔–—…·¥✓（）「」':
        return 0.85
    return 0.50


def textw(s, size, mono=False):
    return sum(charw(c, mono) for c in s) * size / 72.0


def nlines(s, w, size, mono=False, pad=0.0):
    if not s:
        return 1
    return max(1, int(math.ceil(textw(s, size, mono) / max(0.35, w - pad))))


def lsp(size, mult=1.5):
    return Pt(size * mult)


# ══════════════════════════ 基础绘制 ══════════════════════════
def style_run(run, size, bold, color, font=CJK):
    f = run.font
    f.size = Pt(size)
    f.bold = bold
    f.color.rgb = RGBColor.from_string(color)
    f.name = font
    rPr = run._r.get_or_add_rPr()
    for tag in ('a:ea', 'a:cs'):
        e = rPr.find(qn(tag))
        if e is None:
            e = etree.SubElement(rPr, qn(tag))
        e.set('typeface', font)


def tb(slide, x, y, w, h, text, size, *, bold=False, color=BODY, align='l',
       font=CJK, anchor='t', spacing=1.5):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = {'t': MSO_ANCHOR.TOP, 'm': MSO_ANCHOR.MIDDLE,
                          'b': MSO_ANCHOR.BOTTOM}[anchor]
    for i, line in enumerate(text.split('\n')):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = {'l': PP_ALIGN.LEFT, 'r': PP_ALIGN.RIGHT, 'c': PP_ALIGN.CENTER}[align]
        p.line_spacing = lsp(size, spacing)
        p.space_before = Pt(0)
        p.space_after = Pt(0)
        r = p.add_run()
        r.text = line
        style_run(r, size, bold, color, font)
    return box


def rich(slide, x, y, w, h, text, phrase, size, *, bold=False, color=BODY,
         phrase_color=ACCENT, spacing=1.5):
    """一句话里把一个已有词组换成强调样式；断言拼回去与原文逐字一致。"""
    assert phrase in text, 'emph phrase not in text: %r' % phrase
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.TOP
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    p.line_spacing = lsp(size, spacing)
    p.space_before = Pt(0)
    p.space_after = Pt(0)
    i = text.index(phrase)
    got = ''
    for seg, hit in ((text[:i], False), (phrase, True), (text[i + len(phrase):], False)):
        if not seg:
            continue
        got += seg
        r = p.add_run()
        r.text = seg
        style_run(r, size, bold or hit, phrase_color if hit else color)
    assert got == text, (got, text)
    return box


def rect(slide, x, y, w, h, color):
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.fill.solid()
    sh.fill.fore_color.rgb = RGBColor.from_string(color)
    sh.line.fill.background()
    sh.shadow.inherit = False
    return sh


def rule(slide, x, y, w, pt=0.75, color=RULE_C):
    return rect(slide, x, y, w, pt / 72.0, color)


def marker(slide, x, y, color=NAVY, s=0.062):
    return rect(slide, x, y, s, s, color)


# ══════════════════════════ 三线表 ══════════════════════════
NUMRE = re.compile(r'^[+\-−–]?[\d.,]+([±][\d.]+)?$|^[+\-−–]?[\d.,]+%?$|^✓$|^—$|^[\d,]+\s*(s|MB|GB)?$')


def is_num_col(rows, c):
    vals = [str(r[c]).strip() for r in rows[1:] if str(r[c]).strip()]
    return bool(vals) and all(NUMRE.match(v) for v in vals)


def col_widths(rows, size, total, minw=0.95, tiny=1.05):
    """列宽：按内容需求分配富余宽度；单字符列（✓ / —）钉死 tiny，不跟着放大。"""
    n = len(rows[0])
    need, tinyc = [], []
    for c in range(n):
        mx = max(textw(str(r[c]), size, mono=is_num_col(rows, c)) for r in rows)
        need.append(max(mx + 0.30, minw))
        tinyc.append(mx < 0.42)
    fixed = [tiny if tinyc[i] else 0.0 for i, tiny in enumerate([tiny] * n)]
    flex = [i for i in range(n) if not tinyc[i]]
    rest = total - sum(fixed)
    s = sum(need[i] for i in flex)
    out = [0.0] * n
    for i in range(n):
        out[i] = fixed[i] if tinyc[i] else need[i] * rest / s
    return out


def row_heights(rows, colw, size, row_h, vpad=0.14):
    hs = []
    for ri, row in enumerate(rows):
        ln = max(nlines(str(c), colw[ci], size, mono=is_num_col(rows, ci), pad=0.16)
                 for ci, c in enumerate(row))
        hs.append(max(row_h, ln * size * 1.5 / 72 + vpad))
    return hs


def table3(slide, rows, x, y, w, *, size=S_BODY, colw=None, emph=(), bold_rows=(),
           row_h=0.46, vpad=0.14):
    if colw is None:
        colw = col_widths(rows, size, w)
    colw = list(colw)
    colw[-1] += w - sum(colw)
    numc = [is_num_col(rows, c) for c in range(len(rows[0]))]
    hs = row_heights(rows, colw, size, row_h, vpad)

    rule(slide, x, y, w, pt=1.5, color=NAVY)
    yy = y
    for ri, row in enumerate(rows):
        cx = x
        for ci, cell in enumerate(row):
            hit = (ri, ci) in emph
            col = ACCENT if hit else (NAVY if ri == 0 else BODY)
            tb(slide, cx + 0.08, yy, colw[ci] - 0.16, hs[ri], str(cell), size,
               bold=bool(ri == 0 or hit or ri in bold_rows), color=col,
               align='r' if numc[ci] else 'l',
               font=(MONO if numc[ci] else CJK), anchor='m', spacing=1.25)
            cx += colw[ci]
        yy += hs[ri]
        if ri == 0:
            rule(slide, x, yy, w, pt=0.75, color=NAVY)
    rule(slide, x, yy, w, pt=1.5, color=NAVY)
    return sum(hs)


# ══════════════════════════ 外壳 ══════════════════════════
def reset_slide(slide, idx):
    for shp in list(slide.shapes):
        if shp.name in ('bar-blue', 'bar-gold'):
            continue
        if shp.shape_type == MSO_SHAPE_TYPE.PICTURE:
            if idx == 1 or (shp.left > Inches(9.5) and shp.top < Inches(1.0)):
                continue
        shp._element.getparent().remove(shp._element)


def head(slide, title, lead):
    tb(slide, L, TITLE_Y, CW, TITLE_H, title, S_TITLE, bold=True, color=NAVY,
       anchor='m', spacing=1.1)
    if lead:
        tb(slide, L, LEAD_Y, 11.6, 0.32, lead, S_BODY, color=MUTED, anchor='t', spacing=1.2)


def foot(slide, num, takeaway=None, rule_on=True):
    if rule_on:
        rule(slide, L, FOOT_RULE_Y, CW, pt=0.75, color=RULE_C)
    if takeaway:
        tb(slide, L, FOOT_Y, 10.5, 0.27, takeaway, S_NOTE, color=MUTED, spacing=1.2)
    tb(slide, R - 0.9, FOOT_Y, 0.9, 0.27, '%02d' % num, S_NOTE, color=MUTED,
       align='r', spacing=1.2)


def pageno(slide, num):
    tb(slide, R - 0.9, FOOT_Y, 0.9, 0.27, '%02d' % num, S_NOTE, color=MUTED,
       align='r', spacing=1.2)


# ══════════════════════════ 版式 ══════════════════════════
def lay_cover(slide, d):
    """封面：校园底图带 + 白底 40pt 主标题 + 一行副题 + 底部元信息"""
    PH = 2.72
    rect(slide, 0, PH, 13.333, 7.5 - PH, WHITE)
    logo = [s for s in slide.shapes if s.shape_type == MSO_SHAPE_TYPE.PICTURE][0]
    logo.left, logo.top = Inches(0.80), Inches(0.52)
    logo.width, logo.height = Inches(3.00), Inches(0.922)

    title = d['title']
    i = title.index('：') + 1
    lines = [title[:i], title[i:]]
    assert ''.join(lines) == title
    tb(slide, L, 3.12, 11.4, 1.42, '\n'.join(lines), S_COVER, bold=True, color=NAVY, spacing=1.2)
    tb(slide, L, 4.72, 11.4, 0.30, d['subtitle'], S_BODY, color=MUTED, spacing=1.2)
    y = 5.10
    for b in d['bullets']:
        tb(slide, L, y, 11.5, 0.30, b, S_BODY, color=BODY, spacing=1.2)
        y += 0.40
    tb(slide, L, 6.42, 11.5, 0.30, d['takeaway'], S_BODY, bold=True, color=ACCENT, spacing=1.2)
    tb(slide, L, 6.94, 11.5, 0.24, d['footer'], S_NOTE, color=MUTED, spacing=1.2)


def lay_table(slide, d, num, *, narrow=False, accent_cols=(), bold_rows=(), compact=False):
    head(slide, d['title'], d['subtitle'])
    rows = d['tables'][0]
    w = 10.2 if narrow else CW
    x = L + (CW - w) / 2.0 if narrow else L
    colw = col_widths(rows, S_BODY, w)
    vpad = 0.10 if compact else 0.14
    row_h = max(0.42, min(0.62, (BAND_H - 0.30) / len(rows)))
    hs = row_heights(rows, colw, S_BODY, row_h, vpad)
    total = sum(hs)
    if total > BAND_H:
        WARN.append('p%02d table %0.2f > band %0.2f' % (num, total, BAND_H))
    y0 = BAND_TOP + max(0.0, min(0.45, (BAND_H - total) / 2.0))
    emph = {(ri, ci) for ri in range(1, len(rows)) for ci in accent_cols}
    table3(slide, rows, x, y0, w, colw=colw, emph=emph, bold_rows=bold_rows,
           row_h=row_h, vpad=vpad)
    foot(slide, num, d['takeaway'])


def lay_hero(slide, d, num, hero):
    """数字页：52pt 数字顶到标题下方当主角，表格降为佐证，结论退到数字下面的 12pt 说明。"""
    assert hero in d['takeaway'], 'hero 必须来自原文：%r' % hero
    head(slide, d['title'], d['subtitle'])
    tb(slide, L, 2.06, 8.6, 0.80, hero, S_HERO, bold=True, color=ACCENT,
       font=MONO, spacing=1.05)
    tb(slide, L, 2.94, 11.0, 0.27, d['takeaway'], S_NOTE, color=MUTED, spacing=1.2)

    rows = d['tables'][0]
    colw = col_widths(rows, S_BODY, CW)
    avail = BAND_BOT - 3.34
    row_h = max(0.42, min(0.58, avail / len(rows)))
    hs = row_heights(rows, colw, S_BODY, row_h, 0.10)
    if sum(hs) > avail:
        WARN.append('p%02d hero-table %0.2f > %0.2f' % (num, sum(hs), avail))
    emph = {(ri, 3) for ri in range(1, len(rows))} if len(rows[0]) > 4 else set()
    table3(slide, rows, L, 3.34, CW, colw=colw, emph=emph, row_h=row_h, vpad=0.10)
    pageno(slide, num)


def lay_prose(slide, d, num, *, emph_phrase=None):
    """论述页：7.8in 行宽（35 字），方块引导，右栏留白"""
    head(slide, d['title'], d['subtitle'])
    items = d['bullets']
    blocks = [nlines(it, PROSE_W, S_BODY) * S_BODY * 1.55 / 72.0 for it in items]
    gap = 0.36
    total = sum(blocks) + gap * (len(items) - 1)
    y = BAND_TOP + max(0.0, min(0.55, (BAND_H - total) / 2.0))
    for i, it in enumerate(items):
        marker(slide, L, y + 0.115)
        if emph_phrase and emph_phrase in it:
            rich(slide, L + 0.30, y, PROSE_W, blocks[i], it, emph_phrase, S_BODY)
        else:
            tb(slide, L + 0.30, y, PROSE_W, blocks[i], it, S_BODY, color=BODY, spacing=1.55)
        y += blocks[i] + gap
    foot(slide, num, d['takeaway'])


def lay_table_notes(slide, d, num, *, check_col=None):
    """表 + 表下说明（先试双栏，放不下退单栏）"""
    head(slide, d['title'], d['subtitle'])
    rows = d['tables'][0]
    colw = col_widths(rows, S_BODY, CW)
    row_h = max(0.42, min(0.56, (BAND_H - 0.30) / len(rows)))
    hs = row_heights(rows, colw, S_BODY, row_h, 0.10)
    t_total = sum(hs)
    y0 = BAND_TOP + 0.02
    t_bot = y0 + t_total

    CW2 = 5.62
    h2 = max(nlines(b, CW2, S_BODY) for b in d['bullets']) * S_BODY * 1.5 / 72.0
    h1 = sum(nlines(b, CW, S_BODY) for b in d['bullets']) * S_BODY * 1.5 / 72.0
    two_col = (t_bot + 0.34 + h2) <= (FOOT_RULE_Y - 0.12)
    if two_col:
        for i, b in enumerate(d['bullets']):
            tb(slide, L + i * (CW2 + 0.59), t_bot + 0.34, CW2, h2 + 0.05, b,
               S_BODY, color=BODY, spacing=1.5)
    else:
        yy = t_bot + 0.30
        for b in d['bullets']:
            hh = nlines(b, CW, S_BODY) * S_BODY * 1.5 / 72.0
            tb(slide, L, yy, CW, hh + 0.05, b, S_BODY, color=BODY, spacing=1.5)
            yy += hh + 0.14
        if yy > FOOT_RULE_Y:
            WARN.append('p%02d notes overflow %.2f > %.2f' % (num, yy, FOOT_RULE_Y))
    emph = {(ri, check_col) for ri in range(1, len(rows))} if check_col is not None else set()
    table3(slide, rows, L, y0, CW, colw=colw, emph=emph, row_h=row_h, vpad=0.10)
    foot(slide, num, d['takeaway'])


def lay_list(slide, d, num):
    """清单页：两组靠间距 + 灰度分开"""
    head(slide, d['title'], d['subtitle'])
    items = d['bullets']
    hs = [nlines(it, PROSE_W, S_BODY) * S_BODY * 1.55 / 72.0 for it in items]
    gaps = [0.26, 0.56, 0.24, 0.24]      # 组内 0.26 / 组间 0.56
    total = sum(hs) + sum(gaps)
    y = BAND_TOP + max(0.0, min(0.55, (BAND_H - total) / 2.0))
    for i, it in enumerate(items):
        g_b = i >= 2
        marker(slide, L, y + 0.115, MUTED if g_b else NAVY)
        tb(slide, L + 0.30, y, PROSE_W, hs[i], it, S_BODY,
           color=MUTED if g_b else BODY, spacing=1.55)
        y += hs[i] + (gaps[i] if i < len(gaps) else 0.0)
    foot(slide, num, d['takeaway'])


def lay_manifesto(slide, d, num):
    """结论页：28pt 大字压在深蓝块上（全篇唯一色块）"""
    head(slide, d['title'], d['subtitle'])
    items = d['bullets']
    line_h = S_TITLE * 1.35 / 72.0
    blocks = [nlines(it, CW - 1.0, S_TITLE) * line_h for it in items]
    gap = 0.34
    inner = sum(blocks) + gap * (len(items) - 1)
    pad = 0.40
    h = inner + pad * 2
    y0 = BAND_TOP + max(0.0, min(0.40, (BAND_H - h - 0.30) / 2.0))
    rect(slide, 0, y0, 13.333, h, NAVY)
    y = y0 + pad
    for i, it in enumerate(items):
        tb(slide, L, y, CW - 1.0, blocks[i], it, S_TITLE, bold=True, color=WHITE,
           spacing=1.35)
        y += blocks[i] + gap
    tb(slide, L, y0 + h + 0.22, 11.2, 0.30, d['takeaway'], S_BODY, bold=True,
       color=ACCENT, spacing=1.2)
    pageno(slide, num)
    if y0 + h + 0.22 + 0.30 > FOOT_RULE_Y:
        WARN.append('p%02d manifesto bottom %.2f' % (num, y0 + h + 0.52))


# ══════════════════════════ 主流程 ══════════════════════════
def main():
    bak = SRC + '.bak-aiv2-20261104'
    if not os.path.exists(bak):
        shutil.copy2(SRC, bak)
        print('backup ->', os.path.basename(bak))
    prs = Presentation(SRC)
    slides = list(prs.slides)
    assert len(slides) == len(CONTENT) == 15
    for i, s in enumerate(slides):
        reset_slide(s, i + 1)
    C = {d['slide']: d for d in CONTENT}

    lay_cover(slides[0], C[1])
    lay_table(slides[1], C[2], 2)
    lay_prose(slides[2], C[3], 3, emph_phrase='0.19')
    lay_hero(slides[3], C[4], 4, '0.043–0.194')
    lay_table(slides[4], C[5], 5, narrow=True)
    lay_table(slides[5], C[6], 6)
    lay_table(slides[6], C[7], 7, accent_cols=(2,))
    lay_hero(slides[7], C[8], 8, '0.0017–0.0059')
    lay_table(slides[8], C[9], 9, compact=True)
    lay_table_notes(slides[9], C[10], 10)
    lay_table_notes(slides[10], C[11], 11, check_col=3)
    lay_prose(slides[11], C[12], 12)
    lay_table(slides[12], C[13], 13)
    lay_list(slides[13], C[14], 14)
    lay_manifesto(slides[14], C[15], 15)

    prs.save(DST)
    print('saved ->', DST, os.path.getsize(DST), 'bytes')
    for w in WARN:
        print('WARN', w)

    prs2 = Presentation(DST)
    sizes = {}
    for i, s in enumerate(prs2.slides, 1):
        ss = set()
        for shp in s.shapes:
            if shp.has_text_frame:
                for p in shp.text_frame.paragraphs:
                    for r in p.runs:
                        if r.font.size:
                            ss.add(round(r.font.size.pt, 1))
        for v in ss:
            sizes[v] = sizes.get(v, 0) + 1
    print('字号种类:', sorted(sizes))
    print('masters=%d layouts=%d slides=%d' % (
        len(prs2.slide_masters), len(prs2.slide_layouts), len(prs2.slides)))


if __name__ == '__main__':
    main()
