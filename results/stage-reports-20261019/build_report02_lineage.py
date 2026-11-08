# -*- coding: utf-8 -*-
"""课题5 第 2/10 次汇报：数字来源链
设计：python-pptx 原生形状 + 图表，13.333x7.5；深色封面/收尾 + 浅色正文（sandwich）。
无装饰色条、无圆角卡片网格；层级靠字号/字重/留白与发丝线。
"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION
from pptx.oxml.ns import qn
from lxml import etree

OUT = "D:/projects/course5-prep/results/stage-reports-20261019/课题5第02次汇报_数字来源链.pptx"
os.makedirs(os.path.dirname(OUT), exist_ok=True)

# ---- design tokens -------------------------------------------------------
W, H = 13.333, 7.5
M = 0.62
INK = "0F1A22"       # near-black
PAPER = "FFFFFF"
TEAL = "14505E"      # primary
TEAL_T = "E7F0F1"    # tint
ACCENT = "C2410C"    # one sharp accent
MUTED = "6B7A86"
LINE = "D9E0E4"
LATIN = "Segoe UI"
EA = "微软雅黑"

prs = Presentation()
prs.slide_width = Inches(W)
prs.slide_height = Inches(H)
BLANK = prs.slide_layouts[6]


def rgb(h):
    return RGBColor.from_string(h)


def set_run(run, size=16, bold=False, color=INK, latin=LATIN, ea=EA, italic=False):
    f = run.font
    f.size = Pt(size)
    f.bold = bold
    f.italic = italic
    f.color.rgb = rgb(color)
    f.name = latin
    rPr = run._r.get_or_add_rPr()
    for tag in ("a:ea", "a:cs"):
        el = rPr.find(qn(tag))
        if el is None:
            el = etree.SubElement(rPr, qn(tag))
        el.set("typeface", ea if tag == "a:ea" else latin)


def text(slide, x, y, w, h, s, size=16, bold=False, color=INK,
         align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, spacing=1.0, space_after=0):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.auto_size = None
    tf.vertical_anchor = anchor
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    lines = s.split("\n")
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        p.space_after = Pt(space_after)
        r = p.add_run()
        r.text = ln
        set_run(r, size=size, bold=bold, color=color)
    return tb


def rich(slide, x, y, w, h, parts, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, spacing=1.0):
    """parts: list of (text, size, bold, color)"""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = 0; tf.margin_right = 0; tf.margin_top = 0; tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    p = tf.paragraphs[0]
    p.alignment = align
    p.line_spacing = spacing
    for t, sz, b, c in parts:
        r = p.add_run()
        r.text = t
        set_run(r, size=sz, bold=b, color=c)
    return tb


def noshadow(sh):
    sh.shadow.inherit = False
    sp = sh._element
    style = sp.find(qn('p:style'))
    if style is not None:
        sp.remove(style)
    return sh


def bg(slide, color):
    f = slide.background.fill
    f.solid()
    f.fore_color.rgb = rgb(color)


def hair(slide, x, y, w, color=LINE, width=0.75):
    ln = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x), Inches(y),
                                    Inches(x + w), Inches(y))
    ln.line.color.rgb = rgb(color)
    ln.line.width = Pt(width)


def slide_head(s, title, kicker=None):
    if kicker:
        text(s, M, 0.42, W - 2 * M, 0.26, kicker, size=11.5, bold=True, color=MUTED)
    text(s, M, 0.72, W - 2 * M, 0.62, title, size=30, bold=True, color=INK)


def source_line(s, s_text):
    hair(s, M, 6.86, W - 2 * M, LINE)
    text(s, M, 6.94, W - 2 * M, 0.26, s_text, size=10.5, color=MUTED)


def new(dark=False):
    s = prs.slides.add_slide(BLANK)
    bg(s, INK if dark else PAPER)
    return s


# =========================== 1 封面 ===========================
s = new(dark=True)
text(s, M, 1.55, 8.6, 0.34, "课题5 · 第 2/10 次汇报", size=13, bold=True, color="8FA3AE")
text(s, M, 2.0, 8.7, 1.0, "数字来源链", size=58, bold=True, color=PAPER)
text(s, M, 3.15, 10.5, 0.55, "一个百分比是怎么来的", size=26, color="C9D6DC")
hair(s, M, 4.05, 4.2, "3E5561", 1.0)
text(s, M, 4.3, 8.2, 0.9,
     "从原始细胞到表格单元格，每一步都留文件、公式与 SHA-256。",
     size=15, color="A9BAC4")
text(s, M, 6.35, 11.9, 0.3,
     "2026-10-19 ｜ 口径：transductive / in-sample ｜ 单 seed（0）｜ K=15 cosine",
     size=11, color="7E929D")
rich(s, 9.6, 1.62, 3.1, 1.2, [("86.18%", 54, True, "FFFFFF")], align=PP_ALIGN.RIGHT)
text(s, 9.6, 2.86, 3.1, 0.3, "本次拆解的例子", size=11, color="8FA3AE", align=PP_ALIGN.RIGHT)

# =========================== 2 论点 ===========================
s = new()
slide_head(s, "一个百分比不是方法的属性", "论点")
text(s, M, 1.62, 11.2, 1.25,
     "换掉六个因素中的任何一个，同一个数字就会变。",
     size=27, bold=True, color=TEAL)

items = [
    ("01", "方法", "ortholog-PCA / SATURN / SAMap / scVI"),
    ("02", "表示层", "同源交集+PCA-50 / macrogene / 同源图 / 潜空间"),
    ("03", "标签空间", "exact / coarse / fine"),
    ("04", "角色划分", "谁是 reference、谁是 query"),
    ("05", "排除规则", "mapping_status、inactive 细胞是否剔除"),
    ("06", "分母", "n_q 变了，百分比就变了"),
]
y = 3.12
for num, k, v in items:
    rich(s, M, y, 0.75, 0.4, [(num, 15, True, ACCENT)])
    text(s, M + 0.78, y - 0.03, 1.85, 0.4, k, size=17, bold=True, color=INK)
    text(s, M + 2.7, y, 8.9, 0.4, v, size=14, color="44535D")
    hair(s, M, y + 0.52, W - 2 * M)
    y += 0.62
source_line(s, "来源：docs/reports/report-02-metric-lineage-20261008.md")

# =========================== 3 来源链 ===========================
s = new()
slide_head(s, "从原始细胞到表格单元格", "来源链")
steps = [
    ("原始 h5ad", "三物种心脏单细胞"),
    ("归一化", "normalize_total(1e4) + log1p"),
    ("表示层", "同源基因交集 + PCA-50"),
    ("角色划分", "src = reference，tgt = query"),
    ("KNN15", "cosine，倒距离加权"),
    ("逐细胞预测", "含 confidence 与排除原因"),
    ("排除 + 计数", "correct / eligible = n_q"),
    ("metrics.json", "SHA-256 锚定"),
]
x0, y0, colw, rowh = M, 1.92, (W - 2 * M) / 4, 1.02
for i, (k, v) in enumerate(steps):
    r, c = divmod(i, 4)
    x = x0 + c * colw
    y = y0 + r * rowh * 1.82
    # number badge
    badge = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(0.42), Inches(0.42))
    badge.fill.solid(); badge.fill.fore_color.rgb = rgb(TEAL_T)
    badge.line.fill.background()
    noshadow(badge)
    tf = badge.text_frame; tf.margin_left = 0; tf.margin_right = 0
    tf.margin_top = 0; tf.margin_bottom = 0
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    rr = p.add_run(); rr.text = str(i + 1)
    set_run(rr, size=12, bold=True, color=TEAL)
    text(s, x + 0.56, y - 0.02, colw - 0.7, 0.34, k, size=17, bold=True, color=INK)
    text(s, x + 0.56, y + 0.34, colw - 0.7, 0.4, v, size=12.5, color="5A6A75")
    if i % 4 != 3:
        ar = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(x + colw - 0.34), Inches(y + 0.12),
                                Inches(0.26), Inches(0.18))
        ar.fill.solid(); ar.fill.fore_color.rgb = rgb("C3D2D7"); ar.line.fill.background(); noshadow(ar)
text(s, M, 4.72, W - 2 * M, 0.5,
     "任何一步换个定义，最终百分比就会变——所以复核必须沿这条链走，而不是从表里抄数。",
     size=14, color=TEAL, bold=True)
hair(s, M, 5.42, W - 2 * M)
text(s, M, 5.62, 5.8, 1.05,
     "链路上的每一环都有落盘物：输入 h5ad、映射表、脚本 SHA、逐细胞预测、metrics.json。",
     size=13, color="44535D", spacing=1.35)
text(s, 6.8, 5.62, 5.9, 1.05,
     "因此任何一个单元格都能被第三方从文件重算一遍，而不需要相信汇报里的数字。",
     size=13, color="44535D", spacing=1.35)
source_line(s, "对应脚本：scripts/ortholog_pca_dcs_v3_fixkey.py ｜ 产物：results/phase-20261010/opca-fixkey-recovered-20261015/")

# =========================== 4 拆解 ===========================
s = new()
slide_head(s, "86.18% = 1,297 ÷ 1,505", "实例拆解：ortholog-PCA 人→鼠 coarse")
rows = [
    ("输入", "reference = 人 ｜ query = 鼠", "1,528 / 1,535"),
    ("同源基因", "人鼠 1:1 直系同源交集", "15,869"),
    ("表示层", "人+鼠联合 PCA-50（seed 0）", "3,063 × 50"),
    ("评分", "KNN15，cosine，倒距离加权", "k = 15"),
    ("排除", "鼠侧 status ≠ active", "剔 30"),
    ("eligible query", "1,535 − 30", "n_q = 1,505"),
    ("正确数", "逐细胞预测 == 真值", "1,297"),
]
y = 1.72
for k, v, num in rows:
    text(s, M, y, 1.9, 0.34, k, size=14, bold=True, color=TEAL)
    text(s, M + 1.95, y, 4.65, 0.34, v, size=13, color="44535D")
    text(s, M + 7.0, y, 1.95, 0.34, num, size=14, bold=True, color=INK, align=PP_ALIGN.RIGHT)
    hair(s, M, y + 0.42, 9.2)
    y += 0.55
text(s, 10.05, 1.95, 2.7, 0.3, "accuracy", size=12, bold=True, color=MUTED, align=PP_ALIGN.CENTER)
text(s, 10.05, 2.2, 2.7, 1.1, "0.8618", size=52, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)
text(s, 10.05, 3.35, 2.7, 0.85, "= 正确预测数\n÷ 排除后仍有资格的 query 细胞",
     size=11.5, color="5A6A75", align=PP_ALIGN.CENTER, spacing=1.25)
text(s, 10.05, 4.6, 2.7, 0.6, "不是从表里抄出来的", size=11, bold=True, color=MUTED, align=PP_ALIGN.CENTER)
text(s, M, 5.92, 9.0, 0.7,
     "逐类分解（confusion 摘录）：内皮 720/725 正确、成纤维 255/360、免疫 197/202、心肌 19/47；"
     "跨类错误集中在成纤维→平滑肌（82）与心肌→内皮（27）。",
     size=12.5, color="5A6A75", spacing=1.35)
source_line(s, "主源：results/pilot-v1/ortholog-pca-v98/metrics.json ｜ SHA b2b3ac6b…c725 ｜ 本地已独立复算")

# =========================== 5 分母与四个量 ===========================
s = new()
slide_head(s, "分母会变，所以必须一起报", "coverage 与四个量")
text(s, M, 1.62, 11.0, 0.4, "同一个 coarse 层，query 细胞 1,535 个，排除 30 个后被排除在分母之外。",
     size=14, color="44535D")
bar_x, bar_y, bar_w, bar_h = M, 2.18, W - 2 * M, 0.42
full = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(bar_x), Inches(bar_y), Inches(bar_w), Inches(bar_h))
full.fill.solid(); full.fill.fore_color.rgb = rgb("DCE7E9"); full.line.fill.background(); noshadow(full)
exc_w = bar_w * (30 / 1535)
exc = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(bar_x + bar_w - exc_w), Inches(bar_y),
                         Inches(max(exc_w, 0.06)), Inches(bar_h))
exc.fill.solid(); exc.fill.fore_color.rgb = rgb(ACCENT); exc.line.fill.background(); noshadow(exc)
text(s, bar_x, bar_y + 0.5, 5.0, 0.3, "eligible 1,505（98.05%）", size=12, bold=True, color=TEAL)
text(s, bar_x + bar_w - 2.1, bar_y + 0.5, 2.1, 0.3, "排除 30", size=12, bold=True,
     color=ACCENT, align=PP_ALIGN.RIGHT)

quants = [
    ("accuracy", "correct ÷ n_q", "主指标"),
    ("n_q / coverage", "进入分母的细胞数", "排除规则改变分母"),
    ("majority", "最大真值类占比", "无信息基线：准确率 0.4817，macro-F1 仅 0.0813"),
    ("shuffle_p", "预测向量置换检验", "只回答「是否优于随机」，不是多数类检验"),
]
y = 3.42
for k, v, why in quants:
    text(s, M, y, 2.5, 0.34, k, size=16, bold=True, color=TEAL)
    text(s, M + 2.6, y + 0.03, 3.2, 0.34, v, size=13, color="44535D")
    text(s, M + 5.95, y + 0.03, 5.9, 0.34, why, size=12.5, color="5A6A75")
    hair(s, M, y + 0.46, W - 2 * M)
    y += 0.62
text(s, M, 6.28, W - 2 * M, 0.34,
     "只报 accuracy，等于把分母的变化藏起来。",
     size=13, bold=True, color=ACCENT)
source_line(s, "majority 的两个数值含义不同：0.4817 是多数类分类器的准确率，0.0813 是它的 macro-F1")

# =========================== 6 macro-F1 口径 ===========================
s = new()
slide_head(s, "同一份预测，两个 macro-F1", "口径：truth-only 与 union")
text(s, M, 1.62, 11.6, 0.42,
     "差别只在「预测里出现、真实标签里不存在」的类，算不算进平均。",
     size=14, color="44535D")

# left / right columns
colw2 = 5.55
lx, rx = M, M + colw2 + 0.62
for x, lab, val, desc, col in [
    (lx, "truth-only", "0.4516", "只按真实标签集取平均；\n预测多出来的类被忽略。", MUTED),
    (rx, "union", "0.4014", "真实 ∪ 预测 一起取平均；\n预测多出来的类记 F1 = 0。", ACCENT),
]:
    text(s, x, 2.22, colw2, 0.3, lab, size=12, bold=True, color=MUTED)
    text(s, x, 2.5, colw2, 0.95, val, size=46, bold=True, color=col)
    text(s, x, 3.5, colw2, 0.85, desc, size=12.5, color="5A6A75", spacing=1.3)

hair(s, M, 4.55, W - 2 * M)
text(s, M, 4.78, 5.6, 0.34, "平台 scVI 脚本默认", size=13, bold=True, color=INK)
text(s, M, 5.14, 5.6, 0.9, "用 set(y_true)，即左边这个数。\n单独看没问题，但不能与别的方法并列。",
     size=12.5, color="5A6A75", spacing=1.3)
text(s, 6.4, 4.78, 6.2, 0.34, "本项目跨方法对比", size=13, bold=True, color=INK)
text(s, 6.4, 5.14, 6.2, 0.9, "统一用并集口径，从 18 个逐细胞预测文件独立重算。\n上例（人→斑马鱼 coarse）两个数差 0.05。",
     size=12.5, color="5A6A75", spacing=1.3)
source_line(s, "scVI 平台脚本 SHA f894119f… ｜ 重算结果：results/phase-20261019/scvi-cross-species/recomputed_union.json")

# =========================== 7 四方法结果 ===========================
s = new()
slide_head(s, "统一口径后的六方向结果", "coarse macro-F1 · 四方法")
cd = CategoryChartData()
cd.categories = ["人→鼠", "鼠→人", "人→斑马鱼", "斑马鱼→人", "鼠→斑马鱼", "斑马鱼→鼠"]
cd.add_series("ortholog-PCA", (0.6435, 0.6729, 0.1682, 0.1585, 0.2314, 0.4396))
cd.add_series("SATURN",       (0.4147, 0.4010, 0.2479, 0.4021, 0.6500, 0.6510))
cd.add_series("scVI",         (0.6683, 0.5895, 0.4014, 0.4290, 0.4248, 0.4786))
gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(M), Inches(1.62),
                        Inches(W - 2 * M), Inches(4.45), cd)
ch = gf.chart
ch.has_title = False
ch.has_legend = True
ch.legend.position = XL_LEGEND_POSITION.TOP
ch.legend.include_in_layout = False
ch.legend.font.size = Pt(11)
ch.legend.font.color.rgb = rgb("44535D")
plot = ch.plots[0]
plot.gap_width = 60
plot.overlap = -10
colors = [TEAL, "9AB6BE", ACCENT]
for ser, col in zip(plot.series, colors):
    ser.format.fill.solid()
    ser.format.fill.fore_color.rgb = rgb(col)
    ser.format.line.fill.background()
ch.value_axis.maximum_scale = 0.8
ch.value_axis.minimum_scale = 0.0
ch.value_axis.has_major_gridlines = True
ch.value_axis.major_gridlines.format.line.color.rgb = rgb("E8EDEF")
ch.value_axis.tick_labels.font.size = Pt(10)
ch.value_axis.tick_labels.font.color.rgb = rgb(MUTED)
ch.category_axis.tick_labels.font.size = Pt(11)
ch.category_axis.tick_labels.font.color.rgb = rgb("44535D")
ch.value_axis.format.line.color.rgb = rgb(LINE)
ch.category_axis.format.line.color.rgb = rgb(LINE)
plot.has_data_labels = True
dl = plot.data_labels
dl.font.size = Pt(7.5)
dl.font.color.rgb = rgb("44535D")
dl.number_format = "0.00"
dl.number_format_is_linked = False
dl.position = XL_LABEL_POSITION.OUTSIDE_END
source_line(s, "SAMap 未画出：三方向 n=0，其余 0.0401–0.1127 ｜ 分母：oPCA 100%、scVI 98–100%、SATURN 29–87%")

# =========================== 8 收尾 ===========================
s = new(dark=True)
text(s, M, 1.5, 10.8, 0.9, "每个数字都能沿 SHA 复核", size=42, bold=True, color=PAPER)
hair(s, M, 2.62, 4.2, "3E5561", 1.0)
pts = [
    ("主源唯一", "metrics.json 是唯一主源，日志级数字单独标注"),
    ("口径写明", "macro-F1 必须交代 truth-only 还是 union"),
    ("分母随规则变", "排除规则一变，n_q 变，百分比就变"),
]
y = 3.0
for k, v in pts:
    text(s, M, y, 3.2, 0.42, k, size=19, bold=True, color=PAPER)
    text(s, M + 3.4, y + 0.06, 8.2, 0.42, v, size=14, color="A9BAC4")
    hair(s, M, y + 0.62, 11.9, "2E424E")
    y += 0.78
text(s, M, 5.9, 11.9, 0.4, "下次（第 3/10 次）：三方法公平比较边界——为什么不能排冠军。",
     size=13, bold=True, color="8FA3AE")
text(s, M, 6.55, 11.9, 0.3, "2026-10-19 ｜ 课题5", size=11, color="63757F")

prs.save(OUT)
print("WROTE", OUT, "slides=", len(prs.slides.__iter__.__self__._sldIdLst))
