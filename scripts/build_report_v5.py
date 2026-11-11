# -*- coding: utf-8 -*-
"""课题5 汇报 v5：按 audit-design-20261111.md 的 G1–G12 + P01–P26 逐条修订。

改动来源（每条都能对应到清单编号）：
  G1/G4/G6/G7  所有文字块 x 统一 1.00，右缘 12.333（消除 0.67/1.00 双栅格）
  G2           标题 24 → 28pt（正文 11pt 时 2.55×，过 2.5× 线）
  G3           标题色 #12365A → #153957（令牌统一）
  G5           副标题 12 → 11pt（并入正文档位）
  G9           结论条 12.5 → 16pt（大字级，3:1 门槛下 4.47:1 达标）
  G10          每页 ≤4 档：封面 34/13/8.5，内页 28/16/11/8.5
  G11          卡片统一高 1.72 / 间距 0.41 / 内边距 0.30
  G12          #82929F 全部退到 ≥14pt 或装饰线，8.5–11pt 一律 #5E7182
  P01–P26      见各页注释

输出：deliverables/课题5-汇报-v5-20261111.pptx
"""
from copy import deepcopy
from pathlib import Path

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION, XL_LEGEND_POSITION
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

ROOT = Path(r"D:\projects\course5-prep")
TPL = ROOT / "results" / "stage-reports-20261102" / "课题5第03次汇报_三场景结论与可复现闭环.pptx"
OUT = ROOT / "deliverables" / "课题5-汇报-v5-20261111.pptx"

# ── 设计令牌（v5 定稿）──────────────────────────────────
INK    = RGBColor(0x15, 0x39, 0x57)   # 主文字 11.97:1
GREY   = RGBColor(0x5E, 0x71, 0x82)   # 次文字 5.05:1（8.5pt 也用这个）
GOLD_T = RGBColor(0x92, 0x68, 0x12)   # 结论条文字（16pt 大字级）
GOLD_F = RGBColor(0xC8, 0x8F, 0x18)   # 金色填充：图表"最高值"
BLUE   = RGBColor(0x08, 0x76, 0xB2)
TEAL   = RGBColor(0x14, 0x82, 0x90)
BRICK  = RGBColor(0xB4, 0x5C, 0x54)
SLATE  = RGBColor(0x6E, 0x8C, 0xA0)
BG1    = RGBColor(0xEF, 0xF6, 0xFA)
BG2    = RGBColor(0xE3, 0xEA, 0xF0)
BG3    = RGBColor(0xF5, 0xF8, 0xFB)
BG4    = RGBColor(0xEA, 0xF5, 0xF4)
BG5    = RGBColor(0xFA, 0xF3, 0xE6)
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
FONT = "微软雅黑"

M = 1.00          # G1 版心左界
RIGHT = 12.333    # G7 版心右界
CW = 11.333       # 版心宽
PAD = 0.36         # 卡片内边距（全篇唯一值；2026-11-11 对齐统一）
COL2 = 4.60        # 第二栏起点（相对版心左缘）
FOOTER = "课题5 · XenoTransfer v1.0 · 第三次汇报 · 2026-11-11"

# 字号四档（G10）
T_TITLE, T_CARD, T_BODY, T_SMALL = 28, 16, 11, 8.5
COVER_T, COVER_B = 34, 13


def ea(run, name=FONT):
    from lxml import etree
    rPr = run._r.get_or_add_rPr()
    for tag in ("a:latin", "a:ea", "a:cs"):
        el = rPr.find(qn(tag))
        if el is None:
            el = etree.SubElement(rPr, qn(tag))
        el.set("typeface", name)


def fill_text(shape, lines, size, bold=False, color=INK, align=None, spacing=1.25):
    tf = shape.text_frame
    tf.word_wrap = True
    for p in list(tf.paragraphs)[1:]:
        p._p.getparent().remove(p._p)
    p0 = tf.paragraphs[0]
    for r in list(p0.runs):
        r._r.getparent().remove(r._r)
    first = True
    for ln in lines:
        p = p0 if first else tf.add_paragraph()
        first = False
        p.line_spacing = spacing
        if align is not None:
            p.alignment = align
        r = p.add_run()
        r.text = ln
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.color.rgb = color
        ea(r)


def find(slide, name):
    for sh in slide.shapes:
        if sh.name == name:
            return sh
    return None


def drop(slide, name):
    sh = find(slide, name)
    if sh is not None:
        sh._element.getparent().remove(sh._element)


def tb(slide, x, y, w, h, lines, size, bold=False, color=INK,
       align=PP_ALIGN.LEFT, spacing=1.3, anchor=MSO_ANCHOR.TOP):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    first = True
    for ln in lines:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.alignment = align
        p.line_spacing = spacing
        r = p.add_run()
        r.text = ln
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.color.rgb = color
        ea(r)
    return box


def rect(slide, x, y, w, h, color=None, line=None):
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    if color is None:
        s.fill.background()
    else:
        s.fill.solid()
        s.fill.fore_color.rgb = color
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(0.75)
    s.shadow.inherit = False
    return s


def chip(slide, text, color=BLUE, bg=BG1):
    """G8：徽标定宽 1.29，右缘恒等于版心右界。"""
    w = 1.29
    x = RIGHT - w
    y = 1.545
    rect(slide, x, y, w, 0.32, bg)
    tb(slide, x + 0.14, y + 0.03, w - 0.28, 0.30, [text], T_BODY, True, color)


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


def style_chart(chart, maxv, colors, label_size=10, cat_size=11):
    chart.has_title = False
    chart.has_legend = True
    chart.legend.position = XL_LEGEND_POSITION.TOP
    chart.legend.include_in_layout = False
    chart.legend.font.size = Pt(11)
    chart.legend.font.name = FONT
    plot = chart.plots[0]
    plot.gap_width = 70
    plot.overlap = -15
    plot.has_data_labels = True
    dl = plot.data_labels
    dl.font.size = Pt(label_size)
    dl.font.name = FONT
    dl.position = XL_LABEL_POSITION.OUTSIDE_END
    va = chart.value_axis
    va.minimum_scale = 0
    va.maximum_scale = maxv
    va.has_major_gridlines = False
    va.tick_labels.font.size = Pt(10)
    va.tick_labels.font.name = FONT
    va.format.line.fill.background()
    ca = chart.category_axis
    ca.tick_labels.font.size = Pt(cat_size)
    ca.tick_labels.font.name = FONT
    ca.format.line.color.rgb = BG2
    for i, ser in enumerate(chart.series):
        ser.format.fill.solid()
        ser.format.fill.fore_color.rgb = colors[i % len(colors)]
    return plot


# ══════════════════════════════════════════════
src = Presentation(str(TPL))


def delete_slide(prs, idx):
    lst = prs.slides._sldIdLst
    sld = list(lst)[idx]
    prs.part.drop_rel(sld.get(qn("r:id")))
    lst.remove(sld)


while len(src.slides._sldIdLst) > 2:
    delete_slide(src, len(src.slides._sldIdLst) - 1)

DONOR = [deepcopy(sh._element) for sh in src.slides[1].shapes]
LAYOUT = src.slide_layouts[0]


def page(num, title, subtitle, takeaway, note):
    """G1–G7：标题/副标题/页脚/页码全部并入 1.00–12.333 单栅格。"""
    if num == 2:
        s = src.slides[1]
    else:
        s = src.slides.add_slide(LAYOUT)
        for el in DONOR:
            s.shapes._spTree.append(deepcopy(el))
    drop(s, "Table 0")
    t2 = find(s, "Text 2")
    t2.left = Inches(M)
    t2.width = Inches(CW)
    fill_text(t2, [title], T_TITLE, True, INK)
    t3 = find(s, "Text 3")
    t3.left = Inches(M)
    t3.width = Inches(CW)
    fill_text(t3, [subtitle], T_BODY, False, GREY)
    t4 = find(s, "Text 4")
    t4.left = Inches(M)
    fill_text(t4, [FOOTER], T_SMALL, False, GREY)
    t5 = find(s, "Text 5")
    t5.left = Inches(RIGHT - 1.06)
    t5.width = Inches(1.06)
    fill_text(t5, [f"{num:02d}"], T_SMALL, False, GREY, align=PP_ALIGN.RIGHT)
    fill_text(find(s, "Text 7"), [takeaway], T_CARD, True, GOLD_T)
    notes(s, note)
    return s


# ═══ P1 封面（P01 标题 34pt；P02 三条说明合并一框；P03 删版本行）═══
c = src.slides[0]
fill_text(find(c, "Text 1"), ["跨物种单细胞整合：四种方法，一张选型表"], COVER_T, True, WHITE)
fill_text(find(c, "Text 2"), ["第三次汇报 · 含 2026-11-09 数字更正"], 18, False, RGBColor(0xD7, 0xE8, 0xF8))
merged = tb(c, 0.94, 3.22, 11.4, 1.30,
            ["三个难度档全部实测：近缘 · 远缘 · 跨门",
             "中途我们查出一个会翻转排名的评测错误，本讲交代怎么发现的、改完变成什么样",
             "4,606 个细胞 · 四方法 · 全部算力在平台完成 · 镜像内 6/6 复现"],
            COVER_B, False, RGBColor(0xD7, 0xE8, 0xF8), spacing=1.5)
drop(c, "Text 3")
drop(c, "Text 4")
drop(c, "Text 5")
drop(c, "Text 6")           # P03：版本行删除，页脚统一承载
fill_text(find(c, "Text 8"), ["算得对是底线，分得对要人签字。"], COVER_B, True, GOLD_T)
notes(c, """【开场 20 秒】

"讲两件事：四种跨物种迁移方法的选型结果；以及中途我们发现评测错了一处，全部重算。"
""")

# ═══ P2 任务与方法（P04 等式拆四框；P05 删下划线；P06 卡片加高）═══
s = page(2, "任务：把细胞类型从一个物种搬到另一个物种",
         "已标注的物种当参考书，去预测没有标注的物种",
         "任务不是「哪个最好」，而是「什么场景用哪个」。",
         """【给全貌，20 秒】

"左边是有标注的参考物种，右边是要预测的目标物种，中间做标签迁移。
数据：人 1,528 加鼠 1,535 加鱼 1,543，一共 4,606 个细胞；另外用七鳃鳗和小鼠做压力测试。
四种方法性格不同，我们还留了最土那个当基线。"
""")
chip(s, "研究设计")
rect(s, M, 2.05, CW, 0.92, BG1)
tb(s, M + PAD, 2.28, 3.6, 0.45, ["参考物种（已有细胞类型）"], 16, True, INK)
rect(s, M + 4.15, 2.47, 2.30, 0.025, BLUE)          # 箭头线（语义：迁移路径）
tb(s, M + 4.15, 2.14, 2.30, 0.30, ["标签迁移"], T_BODY, False, BLUE, align=PP_ALIGN.CENTER)
tri = s.shapes.add_shape(MSO_SHAPE.ISOSCELES_TRIANGLE, Inches(M + 6.42), Inches(2.38),
                         Inches(0.22), Inches(0.20))
tri.rotation = 90
tri.fill.solid(); tri.fill.fore_color.rgb = BLUE
tri.line.fill.background(); tri.shadow.inherit = False
tb(s, M + 6.95, 2.28, 4.10, 0.45, ["目标物种（需要预测）"], 16, True, INK)
# P04：等式拆四框，各列左对齐
rect(s, M, 3.12, 8.10, 0.62, BG3, line=BG2)
tb(s, 1.20, 3.26, 1.60, 0.36, ["人 1,528"], T_CARD, True, INK)
tb(s, 2.90, 3.26, 1.85, 0.36, ["+ 鼠 1,535"], T_CARD, True, INK)
tb(s, 4.90, 3.26, 2.45, 0.36, ["+ 斑马鱼 1,543"], T_CARD, True, INK)
tb(s, 7.50, 3.26, 1.50, 0.36, ["= 4,606"], T_CARD, True, BLUE)
rect(s, M + 8.35, 3.12, 2.98, 0.62, BG5, line=RGBColor(0xE8, 0xD2, 0x96))
tb(s, M + 8.62, 3.26, 2.60, 0.36, ["压力测试 55,694 细胞"], T_BODY, True, GOLD_T)
cards = [
    ("oPCA（基线）", "两物种共有基因 → PCA", "27 秒 · 无 GPU", BLUE, BG3),
    ("scVI", "联合潜空间 + KNN 迁移", "CPU 8.5 分钟", TEAL, BG4),
    ("SATURN", "蛋白质语言表示", "需 GPU 训练", GOLD_F, BG5),
    ("SAMap", "同源基因关系图", "依赖最多", BRICK, RGBColor(0xF9, 0xEE, 0xED)),
]
cwid, gap = 2.52, 0.41      # G11
for i, (nm, meta, cost, col, bgc) in enumerate(cards):
    cx = M + i * (cwid + gap)
    rect(s, cx, 4.02, cwid, 1.85, bgc, line=BG2)     # P06：h 1.72→1.85
    rect(s, cx, 4.02, cwid, 0.055, col)
    tb(s, cx + PAD, 4.24, cwid - 0.60, 0.34, [nm], T_CARD, True, INK)
    tb(s, cx + PAD, 4.66, cwid - 0.60, 0.62, [meta], T_BODY, False, GREY, spacing=1.4)
    tb(s, cx + PAD, 5.40, cwid - 0.60, 0.30, [cost], T_BODY, False, GREY)

# ═══ P3 三个场景（P07 卡宽 10.80 / 高 1.22 / 间距 0.16；P08 色条 0.04）═══
s = page(3, "三个场景，三种答案", "难度不同，推荐不同",
         "没有全面赢家，所以不排总分，只做场景到方法的映射。",
         """【结论预览，一句话一档】

"近缘人鼠：最简单的方法就够，27 秒、不要显卡。
远缘鱼四向：统一选 scVI。
跨门：这一族都做不了，是负结果。"
""")
chip(s, "主实验结果")
rows = [
    ("近缘", "人 ↔ 小鼠", "ortholog-PCA 首选", "与 scVI 基本打平，但 27 秒、无 GPU", BLUE, BG3),
    ("远缘", "人 ↔ 斑马鱼 · 鼠 ↔ 斑马鱼", "scVI（四向全部最优）", "0.40 / 0.43 / 0.42 / 0.48", TEAL, BG4),
    ("跨门", "七鳃鳗 ↔ 小鼠", "这一族都做不了", "准确率 4.6–5.8%，低于随机猜 7.69%", BRICK, RGBColor(0xF9, 0xEE, 0xED)),
]
y = 2.08
for tag, pair, pick, why, col, bgc in rows:
    rect(s, M, y, 10.20, 1.20, bgc, line=BG2)
    rect(s, M, y, 0.04, 1.20, col)
    tb(s, M + PAD, y + 0.18, 1.10, 0.32, [tag], T_CARD, True, col)
    tb(s, M + PAD, y + 0.70, 3.90, 0.35, [pair], T_BODY, False, GREY)
    tb(s, M + COL2, y + 0.24, 3.70, 0.42, [pick], T_CARD, True, INK)
    tb(s, M + COL2, y + 0.74, 5.60, 0.36, [why], T_BODY, False, GREY)
    y += 1.38

# ═══ P4 主结果图（P09 图表并入 1.00 基线；P10 图例补金色语义；P11 脚注断行）═══
s = page(4, "六个方向的 macro-F1", "coarse 标签空间 · union 口径 · strict_cell（对不上算错）",
         "六行里五行 scVI 最高；只有「鼠→人」输给了最土的办法。",
         """【只读三条】

"金色是每行最高；六行五行 scVI；只有鼠→人输给最土的办法。
SAMap 只有两向能评，其余 n=0，所以没入图。"
""")
chip(s, "主实验结果")
cats = ["斑马鱼→鼠", "鼠→斑马鱼", "斑马鱼→人", "人→斑马鱼", "鼠→人", "人→鼠"]
vals = {
    "oPCA": [0.4186, 0.2816, 0.2131, 0.1506, 0.6729, 0.6435],
    "scVI": [0.4786, 0.4248, 0.4290, 0.4014, 0.5895, 0.6683],
    "SATURN": [0.2961, 0.4076, 0.1386, 0.1282, 0.2566, 0.3522],
}
cd = CategoryChartData()
cd.categories = cats
for k, v in vals.items():
    cd.add_series(k, v)
gf = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(M), Inches(2.02),
                        Inches(11.33), Inches(3.28), cd)
chart = gf.chart
style_chart(chart, 0.75, [BLUE, TEAL, SLATE], label_size=9, cat_size=11)
for ci in range(len(cats)):
    best = max(((k, vals[k][ci]) for k in vals), key=lambda x: x[1])[0]
    pt = chart.series[list(vals).index(best)].points[ci]
    pt.format.fill.solid()
    pt.format.fill.fore_color.rgb = GOLD_F
# P10：手工补第 4 个图例项，消掉"图里多一种金色"的二义
rect(s, 4.90, 1.66, 0.16, 0.16, GOLD_F)
tb(s, 5.12, 1.62, 2.20, 0.24, ["金 = 该方向最高"], T_BODY, False, GREY)
# P11：脚注断成两行，行宽 ≤34 em
tb(s, M, 5.76, 8.60, 0.44,
   ["SAMap 仅人↔鼠两向可评（0.1127 / 0.0401），", "其余方向 n=0，故未入图。"],
   T_BODY, False, GREY, spacing=1.35)

# ═══ P5 跨门（P12 图加高；P13 对照卡共底；P14 两列拆框；P15 删分隔线）═══
s = page(5, "最难那一档：七鳃鳗 ↔ 小鼠", "55,694 个细胞 · 共同基因轴 6,222",
         "两个方法都低于「全场都猜最多的类」——这是有价值的负结果。",
         """【这页补证据】

"跨门单独测了，55,694 细胞。准确率 4.6 到 5.8，13 类随机猜是 7.69，比瞎猜还低。
所以不说哪个方法更好，说这一族方法在当前数据下做不了。"
""")
chip(s, "跨门压力测试", BRICK, RGBColor(0xF9, 0xEE, 0xED))
cd5 = CategoryChartData()
cd5.categories = ["小鼠→七鳃鳗", "七鳃鳗→小鼠"]
cd5.add_series("oPCA", [0.0516, 0.0575])
cd5.add_series("scVI", [0.0457, 0.0582])
gf5 = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(M), Inches(2.05),
                         Inches(6.20), Inches(3.60), cd5)
style_chart(gf5.chart, 0.10, [BLUE, TEAL], label_size=10, cat_size=11)
rect(s, 8.00, 2.05, 4.33, 3.60, BG5, line=RGBColor(0xE8, 0xD2, 0x96))
tb(s, 8.30, 2.22, 3.70, 0.28, ["对照"], T_BODY, True, GOLD_T)
# P14：两列绝对坐标，不靠全角空格
lbls = ["随机猜（13 类）", "多数类基线", "本组实测"]
vals5 = ["7.69%", "21.7% / 30.6%", "4.6–5.8%"]
ry = 2.70
for lb, vv in zip(lbls, vals5):
    tb(s, 8.30, ry, 2.00, 0.26, [lb], T_BODY, False, GREY)
    tb(s, 10.30, ry, 1.80, 0.26, [vv], T_BODY, True, INK, align=PP_ALIGN.RIGHT)
    ry += 0.42
tb(s, 8.30, 4.05, 3.70, 0.30, ["macro-F1"], T_BODY, False, GREY)
tb(s, 8.30, 4.40, 3.70, 0.62, ["0.0235–0.0267", "低于多数类基线 0.0274 / 0.0360"], T_BODY, False, GOLD_T, spacing=1.4)

# ═══ P6 错误（P16 删红线；P17 收空高）═══
s = page(6, "我们算错过一次：查表查反了语种", "真值与预测分属两个物种的词表",
         "错能自己复现出来，才敢说改对了。",
         """【可信度支点，语速慢】

"真值应该用被预测那方的词表，预测用参考书那方的词表，我们搞反了。
后果是两边各丢一批细胞。右边是证据：四种查表方式重算，只有错的那种能复现全部旧数字。"
""")
chip(s, "过程与校验", BRICK, RGBColor(0xF9, 0xEE, 0xED))
rect(s, M, 2.02, CW, 0.56, INK)
tb(s, M + PAD, 2.16, 11.0, 0.32, ["两边各丢一批细胞 —— 真值侧丢得更多"], T_CARD, True, WHITE)
tb(s, M, 2.78, 4.60, 0.28, ["正确的查法"], T_BODY, False, GREY)
tb(s, M, 3.08, 5.20, 0.34, ["真值 → 被预测方词表　　预测 → 参考书方词表"], T_BODY, False, INK)
tb(s, M, 3.58, 4.60, 0.28, ["我们写成了"], T_BODY, False, GREY)
tb(s, M, 3.88, 5.20, 0.34, ["真值 → 参考书方词表　　预测 → 被预测方词表"], T_BODY, True, BRICK)
tb(s, M, 4.42, 5.40, 1.00,
   ["小鼠的「心肌细胞」在人词表里不存在，", "这些细胞静默消失：分母从 1,535 掉到 1,309。"],
   T_BODY, False, GREY, spacing=1.45)
rect(s, M + 6.10, 2.78, 4.90, 2.55, BG5, line=RGBColor(0xE8, 0xD2, 0x96))
tb(s, M + 6.46, 2.96, 4.30, 0.30, ["怎么证明不是事后找借口"], T_BODY, True, GOLD_T)
tb(s, M + 6.46, 3.36, 4.30, 1.42,
   ["同一份结果，按四种查表方式各算一遍。",
    "只有「查错的那种」能一字不差复现全部旧数字：",
    "· 六个方向 6/6 吻合",
    "· accuracy 也 6/6 吻合"], T_BODY, False, INK, spacing=1.4)

# ═══ P7 修正对比（P18 图与右框共顶共底）═══
s = page(7, "改完之后：排名没变，但理由变了", "SATURN 原口径 vs 修正口径",
         "「鼠↔鱼用 SATURN」被推翻；「远缘用 scVI」没变。",
         """【先旧后新，落差说出来】

"原来 0.65，比 scVI 高一大截；改完 0.41，比 scVI 还低，六个方向一个都不赢。
那条建议被推翻，但远缘用 scVI 没变。
映射表里斑马鱼一个残差类别 Orthers 原来被算成神经，现在退出评估。"
""")
chip(s, "过程与校验", BRICK, RGBColor(0xF9, 0xEE, 0xED))
cd7 = CategoryChartData()
cd7.categories = cats
cd7.add_series("原（错）", [0.6510, 0.6500, 0.4021, 0.2479, 0.4010, 0.4147])
cd7.add_series("修正后", [0.2961, 0.4076, 0.1386, 0.1282, 0.2566, 0.3522])
gf7 = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(M), Inches(2.02),
                         Inches(7.33), Inches(3.55), cd7)
style_chart(gf7.chart, 0.75, [BG2, BLUE], label_size=9, cat_size=11)
rect(s, 8.80, 2.02, 3.53, 3.55, BG3, line=BG2)
tb(s, 8.80 + PAD, 2.22, 3.00, 0.30, ["变化要点"], T_BODY, True, INK)
tb(s, 8.80 + PAD, 2.66, 3.00, 2.60,
   ["· 最大虚高 +0.3549", "　（斑马鱼→鼠）", "· 六向全部下降",
    "· 鱼向 n=1469（覆盖 95.7%）", "· Orthers 退出评估"], T_BODY, False, GREY, spacing=1.6)

# ═══ P8 时间与内存（P19 卡加高；P20 第三卡改破折号）═══
s = page(8, "时间与内存：三种方法的真实代价", "平台实测 + 本机白盒测量",
         "27 秒的基线和 8.5 分钟的深度模型，差 19 倍。",
         """【只讲代价，不要提钱】

"oPCA 全量 27 秒、峰值 1.31 GB、纯 CPU；scVI 在 CPU 上 8.5 分钟，平台含 IO 是 15 分 16 秒。
SATURN 要 GPU，没有 CPU 口径。"
""")
chip(s, "资源实测")
nums = [("27 s", "oPCA 全量六方向", "峰值内存 1.31 GB · 纯 CPU", BLUE),
        ("8.5 min", "scVI（门内）", "CPU · 平台含 IO 15m16s", TEAL),
        ("—", "SATURN 训练", "未测 · 无 CPU 口径", GREY)]
for i, (big, lab, sub, col) in enumerate(nums):
    cx = M + i * 3.92
    rect(s, cx, 2.08, 3.51, 3.40, BG3, line=BG2)
    rect(s, cx, 2.08, 3.51, 0.055, col)
    tb(s, cx + PAD, 2.28, 3.00, 1.22, [big], 40, True, col if col != GREY else INK)
    tb(s, cx + PAD, 3.40, 3.00, 0.32, [lab], T_CARD, True, INK)
    tb(s, cx + PAD, 3.92, 3.00, 0.60, [sub], T_BODY, False, GREY, spacing=1.4)

# ═══ P9 与原文对照（P21 卡宽 10.60/高 1.30/间距 0.16；P22 色条中性；P23 删竖线）═══
s = page(9, "和原论文一致吗", "三篇原文的主张 vs 我们复现到的位置",
         "不同要给出理由，尤其不能替原文下「它不行」的结论。",
         """【回答"你们凭什么和论文不一样"】

"方向一致但结论不同，要说明为什么：SATURN 强过 SAMap 但输给 scVI；
SAMap 只喂 1:1 同源、规模差约 104 倍；HEART 我们只取了三个物种子集。"
""")
chip(s, "对照")
rows9 = [("SATURN（Nat Methods 2024）", "蛙↔鱼中位准确率 85.8%，比 SAMap 高 119%", "方向一致（强于 SAMap），但输给 scVI"),
         ("SAMap（eLife 2021）", "同门内全同源图可跨远缘映射", "只喂 1:1 同源、规模差约 104 倍，几乎无信号"),
         ("HEART（Science 2026）", "27 物种心脏图谱，SATURN 整合 16 物种", "仅取三物种子集，未复现原规模")]
y = 2.06
for nm, claim, ours in rows9:
    rect(s, M, y, 10.20, 1.24, BG3, line=BG2)
    rect(s, M, y, 0.04, 1.24, GREY)
    tb(s, M + PAD, y + 0.14, 4.10, 0.36, [nm], T_CARD, True, INK)
    tb(s, M + PAD, y + 0.60, 4.10, 0.54, [claim], T_BODY, False, GREY)
    tb(s, M + 4.60, y + 0.44, 5.40, 0.46, [ours], T_BODY, False, INK)
    y += 1.42

# ═══ P10 总结（P24 色条 0.06；P25 四条压一行；P26 删分隔线）═══
s = page(10, "总结：三条结论 + 两件没做完", "结论限定在 4,606 个细胞、同批数据重评估",
         "算得对是底线，分得对要人签字。",
         """【收尾，一条条说】

"三条结论：没有全面赢家，所以做选型表；近缘简单方法够；跨门这一族做不了。
两件没做完：容器最后一步没跑成；映射表签字只到授权层。"
""")
chip(s, "结论与局限")
concl = [("没有全面赢家", "不排总分，只做「场景 → 方法」", BLUE),
         ("近缘，简单就够", "人↔鼠基本打平；最土的办法 27 秒、无 GPU", TEAL),
         ("跨门，这一族做不了", "比随机猜还低，是有价值的负结果", BRICK)]
for i, (head, sub, col) in enumerate(concl):
    cx = M + i * 3.86
    rect(s, cx, 2.08, 3.45, 0.06, col)
    tb(s, cx, 2.26, 3.45, 0.30, [f"0{i+1}"], T_BODY, True, GREY)
    tb(s, cx, 2.58, 3.45, 0.40, [head], T_CARD, True, INK)
    tb(s, cx, 3.06, 3.45, 0.96, [sub], T_BODY, False, GREY, spacing=1.5)
tb(s, M, 4.30, CW, 0.34,
   ["未完成：容器 build 未执行（本机缺 WSL）· 映射表签字仅到授权层（38 行已签认）"],
   T_BODY, False, GREY)
# 末页补「下一步」：排序依据来自 scale 审计（评测可信 > 排名公平 > 规模）
rect(s, M, 4.86, CW, 1.16, BG3, line=BG2)
tb(s, M + PAD, 5.00, 8.60, 0.30,
   ["下一步（按「评测可信 > 排名公平 > 规模」排序）"], T_BODY, True, INK)
tb(s, M + PAD, 5.38, 10.70, 0.58,
   ["T0 挂载探测 2 分钟 / ¥0.02  →  T1 全量 oPCA（32c128g，≈7.3 h）  →  T2 全量 scVI（≈6.5 h）",
    "T4 SATURN 需 GPU（无实测时长）；正对照 oracle 先做，1 天，否则负结果会被当成又一个 bug"],
   T_BODY, False, GREY, spacing=1.35)

OUT.parent.mkdir(parents=True, exist_ok=True)
src.save(str(OUT))
print("saved:", OUT)
print("slides:", len(src.slides._sldIdLst), "bytes:", OUT.stat().st_size)



