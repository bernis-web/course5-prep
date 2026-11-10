# -*- coding: utf-8 -*-
"""课题5 汇报 v3：学校模板 + 统一骨架 + 原生图表（2026-11-10）

改版依据（Claude 审稿 + 自己验证）：
  1. 第 2 页模板旧表格叠印 —— 已确认，本版彻底删 Table 0
  2. 骨架统一为「固定外壳 + 四种内容区」，不再五种排法混用
  3. 主结果与跨门改用原生条形图（不再手画格子）
  4. 全篇去掉红色，错误一律「深蓝 + 删除线」；金色只给结论
  5. 删「家底/¥2.47」页；4,606 进副标题；耗时进方法卡
  6. 「怎么证明」并入「错在哪」右侧证据块（4/4 精确复现）
  7. 新增跨门压力测试页（原版缺这一页，是硬伤）
  8. 14 页 → 10 页

输出：deliverables/课题5-汇报-v3-学校模板-20261110.pptx
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
OUT = ROOT / "deliverables" / "课题5-汇报-v3-学校模板-20261110.pptx"

# 模板令牌
NAVY = RGBColor(0x12, 0x36, 0x5A)
BLUE2 = RGBColor(0x4A, 0x7F, 0xA5)
BLUE3 = RGBColor(0x8F, 0xA9, 0xBC)
GREY = RGBColor(0xD9, 0xD9, 0xD9)
MUTED = RGBColor(0x60, 0x75, 0x8F)
GOLDD = RGBColor(0x8A, 0x4B, 0x00)
GOLD = RGBColor(0xFF, 0xC0, 0x00)
CREAM = RGBColor(0xD7, 0xE8, 0xF8)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
INK = RGBColor(0x1F, 0x2D, 0x3D)
BAND = RGBColor(0xFF, 0xF2, 0xCC)
RULE = RGBColor(0xB7, 0xC9, 0xD6)
FONT = "微软雅黑"

FOOTER = "课题5 · XenoTransfer v1.0 · 第三次汇报 · 2026-11-10"
CY = 1.95      # 内容区顶
CY_BOT = 5.85  # 内容区底


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


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


def style_chart(chart, maxv, colors, legend_top=True, label_size=9):
    chart.has_title = False
    chart.has_legend = legend_top
    if legend_top:
        chart.legend.position = XL_LEGEND_POSITION.TOP
        chart.legend.include_in_layout = False
        chart.legend.font.size = Pt(10)
        chart.legend.font.name = FONT
    plot = chart.plots[0]
    plot.gap_width = 55
    plot.overlap = -5
    plot.has_data_labels = True
    dl = plot.data_labels
    dl.font.size = Pt(label_size)
    dl.font.name = FONT
    dl.position = XL_LABEL_POSITION.OUTSIDE_END
    va = chart.value_axis
    va.minimum_scale = 0
    va.maximum_scale = maxv
    va.has_major_gridlines = False
    va.tick_labels.font.size = Pt(9)
    va.tick_labels.font.name = FONT
    va.format.line.fill.background()
    ca = chart.category_axis
    ca.tick_labels.font.size = Pt(11)
    ca.tick_labels.font.name = FONT
    ca.format.line.color.rgb = RULE
    for i, ser in enumerate(chart.series):
        ser.format.fill.solid()
        ser.format.fill.fore_color.rgb = colors[i % len(colors)]
    return plot


# ═══════════════════════════════════════════════
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


def body_slide(num, title, subtitle, takeaway, note):
    if num == 2:
        s = src.slides[1]
    else:
        s = src.slides.add_slide(LAYOUT)
        for el in DONOR:
            s.shapes._spTree.append(deepcopy(el))
    drop(s, "Table 0")                      # ★ 关键：删掉模板残留表格
    fill_text(find(s, "Text 2"), [title], 24, True, NAVY)
    fill_text(find(s, "Text 3"), [subtitle], 12.5, False, MUTED)
    fill_text(find(s, "Text 4"), [FOOTER], 8.5, False, MUTED)
    fill_text(find(s, "Text 5"), [f"{num:02d}"], 8.5, False, MUTED, align=PP_ALIGN.RIGHT)
    fill_text(find(s, "Text 7"), [takeaway], 13, True, GOLDD)
    notes(s, note)
    return s


# ═══════════════ P1 封面 ═══════════════
c = src.slides[0]
fill_text(find(c, "Text 1"), ["跨物种单细胞整合：四种方法，一张选型表"], 30, True, WHITE)
fill_text(find(c, "Text 2"), ["第三次汇报 · 含 2026-11-09 数字更正"], 16, False, CREAM)
fill_text(find(c, "Text 3"), ["三个难度档全部实测：近缘 · 远缘 · 跨门"], 13, False, CREAM)
fill_text(find(c, "Text 4"), ["中途我们查出一个会翻转排名的评测错误，本讲交代怎么发现的、改完变成什么样"], 13, False, CREAM)
fill_text(find(c, "Text 5"), ["4,606 个细胞 · 四方法 · 全部算力在平台完成 · 镜像内 6/6 复现"], 13, False, CREAM)
fill_text(find(c, "Text 6"), [FOOTER], 11.5, False, RGBColor(0xDD, 0xEB, 0xFA))
fill_text(find(c, "Text 8"), ["算得对是底线，分得对要人签字。"], 13, True, GOLDD)
notes(c, """【开场 25 秒】

"这次汇报讲两件事：我们测了四种跨物种迁移方法，得到一张选型表；以及，中途我们发现自己的评测错了一处，改完全部重算。"

不要念副标题的细节。""")

# ═══════════════ P2 任务与方法（4 卡） ═══════════════
s = body_slide(2, "任务：把细胞类型从一个物种搬到另一个物种",
               "4,606 个细胞（人 1,528 / 鼠 1,535 / 鱼 1,543）· 三种难度档",
               "留一个「土办法」当基线：任何复杂方法都得先打得过它。",
               """【这页给全貌，不要念参数】

"任务是把一个物种的细胞类型搬到另一个物种。数据 4,606 个细胞，三个物种，三档难度都测。

四种做法，性格不同：
oPCA 最土，只拿两物种共有的基因做对照表，27 秒、不用显卡。
scVI 是深度模型，干的事很朴素——让细胞住进同一个小区，按邻居判断。
SATURN 把基因翻译成蛋白质语言，看意思像不像。
SAMap 画族谱。"

最后一句："我们特意留了最土那个当基线。\"""")
add_tb = tb
cards = [
    ("oPCA（基线）", "只拿两物种共有的基因\n做对照表", "27 秒\n无 GPU · 峰值 1.3 GB", NAVY),
    ("scVI", "细胞住进同一个低维空间\n按邻居判断", "CPU 8.5 分钟\n平台含 IO 15m16s", BLUE2),
    ("SATURN", "基因翻成蛋白质语言\n看「意思」像不像", "需 GPU 训练\n无 CPU 对照口径", BLUE3),
    ("SAMap", "同源基因图\n按亲缘关系找", "依赖最多\n本数据上最不稳定", GREY),
]
cw, ch = 2.86, 2.10
x0, y0 = 0.67, 2.15
for i, (nm, meta, cost, col) in enumerate(cards):
    cx = x0 + i * (cw + 0.13)
    rect(s, cx, y0, cw, ch, WHITE, line=RGBColor(0xD9, 0xD2, 0xC4))
    rect(s, cx, y0, cw, 0.07, col)
    tb(s, cx + 0.2, y0 + 0.22, cw - 0.4, 0.35, [nm], 15, True, NAVY)
    tb(s, cx + 0.2, y0 + 0.56, cw - 0.4, 0.9, meta.split("\n"), 11.5, False, INK, spacing=1.3)
    tb(s, cx + 0.2, y0 + ch - 0.55, cw - 0.4, 0.45, cost.split("\n"), 9.5, False, MUTED, spacing=1.25)
tb(s, 0.67, 4.55, 11.9, 0.9,
   ["任务不是「哪个最好」，而是「什么场景用哪个」——所以结论落在一张选型表上。"], 15, False, INK)

# ═══════════════ P3 三场景选型 ═══════════════
s = body_slide(3, "三个场景，三种答案", "近缘 / 远缘 / 跨门 —— 三档都实测过",
               "没有全面赢家，所以不排总分，只做场景到方法的映射。",
               """【全场结论预览，一句话一档】

"近缘，人跟小鼠：最简单的方法就够，27 秒、不要显卡。
远缘，鱼参与的四个方向：统一选 scVI。
跨门，七鳃鳗跟小鼠：这一族方法都做不了——这是负结果，但我们认为有价值。"

不要在这里展开数字，下一页才有。""")
rows = [
    ("近缘", "人 ↔ 小鼠", "ortholog-PCA 首选", "与 scVI 基本打平，但 27 秒、无 GPU", NAVY),
    ("远缘", "人 ↔ 斑马鱼 · 鼠 ↔ 斑马鱼", "scVI（四向全部最优）", "0.40 / 0.43 / 0.42 / 0.48", BLUE2),
    ("跨门", "七鳃鳗 ↔ 小鼠", "这一族都做不了", "准确率 4.6–5.8%，低于随机猜 7.69%", MUTED),
]
y = 2.05
for tag, pair, pick, why, col in rows:
    rect(s, 0.67, y, 11.98, 1.15, WHITE, line=RGBColor(0xE2, 0xDC, 0xCF))
    rect(s, 0.67, y, 0.06, 1.15, col)
    tb(s, 0.95, y + 0.12, 0.9, 0.35, [tag], 13, True, col)
    tb(s, 0.95, y + 0.52, 3.9, 0.4, [pair], 12, False, MUTED)
    tb(s, 5.1, y + 0.16, 3.3, 0.4, [pick], 16, True, NAVY)
    tb(s, 5.1, y + 0.62, 7.2, 0.4, [why], 11.5, False, INK)
    y += 1.28

# ═══════════════ P4 主结果图 ═══════════════
s = body_slide(4, "六个方向的 macro-F1", "coarse 标签空间 · union 口径 · strict_cell（对不上算错）",
               "六行里五行 scVI 最高；只有「鼠→人」输给了最土的办法。",
               """【图中只读三条信息】

"金色标签是每行最高的。六行五行是 scVI。
第二，只有鼠→人这一行被最土的办法赢了——说明近缘简单方法够用。
第三，SAMap 只有人↔鼠两向能评，其余方向没有细胞能对上，所以没画进来。"

不要逐格念数字。""")
cats = ["斑马鱼→鼠", "鼠→斑马鱼", "斑马鱼→人", "人→斑马鱼", "鼠→人", "人→鼠"]
vals = {
    "oPCA": [0.4405, 0.2177, 0.1512, 0.1654, 0.6729, 0.6435],
    "scVI": [0.4786, 0.4248, 0.4290, 0.4014, 0.5895, 0.6683],
    "SATURN": [0.2961, 0.4076, 0.1386, 0.1282, 0.2566, 0.3522],
}
cd = CategoryChartData()
cd.categories = cats
for k, v in vals.items():
    cd.add_series(k, v)
gf = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(1.25), Inches(1.85),
                        Inches(11.40), Inches(3.75), cd)
chart = gf.chart
style_chart(chart, 0.75, [NAVY, BLUE2, BLUE3], label_size=9)
chart.plots[0].gap_width = 80
chart.plots[0].overlap = -20
chart.category_axis.tick_labels.font.size = Pt(11)
# 每行最高值标金
import itertools
for ci, cat in enumerate(cats):
    idx = cats.index(cat)
    series_vals = [(name, vals[name][idx]) for name in vals]
    best_name, best_v = max(series_vals, key=lambda x: x[1])
    si = list(vals.keys()).index(best_name)
    pt = chart.series[si].points[idx]
    pt.format.fill.solid()
    pt.format.fill.fore_color.rgb = GOLD
tb(s, 1.25, 5.70, 11.4, 0.3,
   ["SAMap 仅人↔鼠两向可评（0.1127 / 0.0401），其余方向 n=0 无法评估，故未入图。"], 10, False, MUTED)

# ═══════════════ P5 跨门压力测试 ═══════════════
s = body_slide(5, "最难那一档：七鳃鳗 ↔ 小鼠（跨门）",
               "55,694 个细胞（七鳃鳗 41,678 + 小鼠 14,016）· 共同基因轴 6,222",
               "两个方法都低于「全场都猜最多的类」——这是有价值的负结果。",
               """【这一页是补原来缺的证据页】

"跨门那档我们单独测了。55,694 个细胞，七鳃鳗跟小鼠。

准确率只有 4.6 到 5.8。13 类空间里随机猜是 7.69——也就是说，比瞎猜还低。

所以我们不说'哪个方法更好'，我们说'这一族方法在当前数据与注释体系下做不了'。"

如果被问"是不是跑错了"：答——正式评测里 6/6 复现、产物有 sha256，不是跑错，是确实不行。""")
cats5 = ["小鼠→七鳃鳗", "七鳃鳗→小鼠"]
cd5 = CategoryChartData()
cd5.categories = cats5
cd5.add_series("oPCA", [0.0516, 0.0575])
cd5.add_series("scVI", [0.0457, 0.0582])
gf5 = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(0.67), Inches(2.05),
                         Inches(7.2), Inches(2.7), cd5)
c5 = gf5.chart
style_chart(c5, 0.10, [NAVY, BLUE2], label_size=10)
tb(s, 8.15, 2.05, 4.5, 0.35, ["对照", ], 12, True, MUTED)
tb(s, 8.15, 2.45, 4.5, 1.6,
   ["随机猜（13 类）　7.69%", "多数类基线　　21.7% / 30.6%",
    "本组实测　　　4.6–5.8%"], 12, False, INK, spacing=1.5)
rect(s, 8.15, 3.9, 4.4, 0.02, RULE)
tb(s, 8.15, 4.05, 4.5, 0.9, ["macro-F1 0.0235–0.0267", "低于多数类基线（0.0274 / 0.0360）"], 11, False, GOLDD, spacing=1.4)

# ═══════════════ P6 错误 + 复现证据 ═══════════════
s = body_slide(6, "我们算错过一次：查表查反了语种",
               "每个物种的细胞类型是各自一套词，真值与预测分属两侧",
               "错能自己复现出来，才敢说改对了。",
               """【这页是全篇可信度的支点，语速放慢】

"在给结论之前，先说我们错在哪。

真值应该用被预测那方的词表，预测用参考书那方的词表。我们把两边搞反了。

后果是两边各丢一批细胞：真值查不到的跳过，预测查不到的记成'对不上'再丢一次。像拿法语词典查英语单词。

右边是证据：同一份结果，按四种查表方式各算一遍，只有错的那种能一字不差复现原来的全部旧数字——四个方向全中，准确率也全中。"

这里不要用"戏精"语气，就事论事。""")
# 顶部深蓝横带
rect(s, 0.67, 1.98, 11.9, 0.62, NAVY)
tb(s, 0.95, 2.14, 11.4, 0.35, ["两边各丢一批细胞，而且真值侧丢得更多"], 13, True, WHITE)

tb(s, 0.67, 2.8, 6.2, 0.32, ["规矩本来是对的"], 11, False, MUTED)
tb(s, 0.67, 3.12, 6.2, 0.8, ["真值 → 被预测方词表　　预测 → 参考书方词表"], 12.5, False, INK)
tb(s, 0.67, 3.62, 6.2, 0.32, ["我们写成了"], 11, False, MUTED)
tb(s, 0.67, 3.94, 6.2, 0.8, ["真值 → 参考书方词表　　预测 → 被预测方词表"], 12.5, False, NAVY)
# 删除线效果：在错的那行加一条线
rect(s, 0.67, 4.2, 5.6, 0.012, NAVY)

tb(s, 0.67, 4.55, 6.2, 1.2,
   ["后果：小鼠的「心肌细胞」在人词表里不存在，这些细胞静默消失，",
    "人→鼠分母从 1,535 掉到 1,309。"], 11.5, False, INK, spacing=1.45)

# 右侧证据块
rect(s, 7.15, 2.8, 5.4, 2.40, BAND, line=RGBColor(0xE8, 0xD2, 0x96))
tb(s, 7.45, 3.0, 4.9, 0.35, ["怎么证明不是事后找借口"], 11.5, True, GOLDD)
tb(s, 7.45, 3.4, 4.9, 2.1,
   ["同一份结果，按四种查表方式各算一遍。",
    "",
    "只有「查错的那种」能一字不差复现全部旧数字：",
    "· 六个方向 6/6 吻合",
    "· accuracy 也 6/6 吻合"], 11, False, INK, spacing=1.42)

# ═══════════════ P7 修正对比 ═══════════════
s = body_slide(7, "改完之后：排名没变，但理由变了",
               "SATURN 原口径 vs 修正口径（union / strict_cell）",
               "「鼠↔鱼用 SATURN」被推翻；「远缘用 scVI」没变。",
               """【先旧数再新数，落差说出来】

"原来 SATURN 在鼠↔鱼是 0.65，比 scVI 的 0.42 高一大截，所以我们当时写'鼠↔鱼用 SATURN'。
改完是 0.41，比 scVI 还低，六个方向一个都不赢。那条建议被推翻。

但'远缘用 scVI'没变——它本来就不靠那一格撑着。

顺带：映射表里斑马鱼的一个残差类别 Orthers（Others 的拼写错误）原来被算成神经，现在退出评估。"

不要在这一页谈到钱。""")
cats7 = ["斑马鱼→鼠", "鼠→斑马鱼", "斑马鱼→人", "人→斑马鱼", "鼠→人", "人→鼠"]
cd7 = CategoryChartData()
cd7.categories = cats7
cd7.add_series("原（错）", [0.6510, 0.6500, 0.4021, 0.2479, 0.4010, 0.4147])
cd7.add_series("修正后", [0.2961, 0.4076, 0.1386, 0.1282, 0.2566, 0.3522])
gf7 = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(0.67), Inches(1.98),
                         Inches(8.0), Inches(3.55), cd7)
c7 = gf7.chart
style_chart(c7, 0.75, [GREY, NAVY], label_size=8.5)
tb(s, 8.95, 2.05, 3.7, 0.32, ["变化要点"], 12, True, MUTED)
tb(s, 8.95, 2.45, 3.7, 2.6,
   ["· 最大虚高 +0.3549", "　（斑马鱼→鼠）",
    "· 六向全部下降", "· 分母同时拉齐到 1,469–1,528",
    "· 映射表：Orthers 退出评估"], 11, False, INK, spacing=1.45)

# ═══════════════ P8 时间与内存 ═══════════════
s = body_slide(8, "时间与内存：三种方法的真实代价",
               "平台实测 + 本机白盒测量（进程内 PeakWorkingSetSize）",
               "27 秒的基线和 8.5 分钟的深度模型，差 19 倍。",
               """【这页只讲代价，不要提钱】

"oPCA 全量六方向 27 秒，峰值内存 1.31 GB，纯 CPU。
scVI 在 CPU 上 8.5 分钟，平台 2 核含 IO 是 15 分 16 秒。
SATURN 要 GPU，所以没有 CPU 口径的对照。"

如果被问"多少钱"——"两个多块钱，但这不重要，重要的是时间与硬件门槛"。""")
nums = [
    ("27 s", "oPCA 全量六方向", "峰值内存 1.31 GB · 纯 CPU"),
    ("8.5 min", "scVI（门内）", "CPU · 平台含 IO 15m16s"),
    ("GPU", "SATURN 训练", "无 CPU 对照口径"),
]
x = 0.67
for big, lab, sub in nums:
    rect(s, x, 2.05, 3.85, 2.3, WHITE, line=RGBColor(0xD9, 0xD2, 0xC4))
    tb(s, x + 0.3, 2.25, 3.3, 0.9, [big], 38, True, NAVY)
    tb(s, x + 0.3, 3.2, 3.3, 0.35, [lab], 13, True, INK)
    tb(s, x + 0.3, 3.6, 3.3, 0.6, [sub], 10.5, False, MUTED, spacing=1.35)
    x += 4.0
tb(s, 0.67, 4.65, 11.9, 1.0,
   ["全部计算在 DCS 平台完成（4 个任务），镜像内 6 个冻结值逐位复现 6/6。"], 13, False, INK)

# ═══════════════ P9 与原文对照 ═══════════════
s = body_slide(9, "和原论文一致吗", "三篇原文的主张 vs 我们复现到的位置",
               "不同要给出理由，尤其不能替原文下「它不行」的结论。",
               """【这页回答"你们凭什么和论文不一样"】

"我们跟三篇原文比。

SATURN 原文在蛙↔鱼上报很高的中位准确率，也明显高于 SAMap。我们复现到的方向一致——SATURN 确实强过 SAMap，但它输给 scVI。

SAMap 原文依赖全同源图；我们只喂 1:1 同源，规模差三百倍，所以它在我们这儿几乎没信号。这不等于它不行。

HEART 是 27 物种心脏图谱，我们只取了三个物种的子集，没复现原规模。"

最后一句：别说"SAMap 不行"，说"在我们这个约束下无信号"。""")
rows9 = [
    ("SATURN (Nat Methods 2024)", "蛙↔鱼中位准确率 85.8%，比 SAMap 高 119%", "方向一致（强于 SAMap），但输给 scVI"),
    ("SAMap (eLife 2021)", "同门内全同源图可跨远缘映射", "只喂 1:1 同源、规模差 300 倍，几乎无信号"),
    ("HEART (Science 2026)", "27 物种心脏图谱，SATURN 整合 16 物种", "仅取三物种子集，未复现原规模"),
]
y = 2.0
for name, claim, ours in rows9:
    rect(s, 0.67, y, 11.98, 1.1, WHITE, line=RGBColor(0xE2, 0xDC, 0xCF))
    tb(s, 0.92, y + 0.14, 3.6, 0.4, [name], 12, True, NAVY)
    tb(s, 0.92, y + 0.55, 3.6, 0.45, [claim], 9.5, False, MUTED, spacing=1.3)
    rect(s, 4.65, y + 0.15, 0.012, 0.78, RULE)
    tb(s, 4.9, y + 0.28, 7.5, 0.55, [ours], 11, False, INK, spacing=1.35)
    y += 1.2

# ═══════════════ P10 总结 ═══════════════
s = body_slide(10, "总结：三条结论 + 两件没做完",
                "结论限定在 4,606 个细胞、同批数据重评估",
                "算得对是底线，分得对要人签字。",
                """【收尾，一条一条说】

"三条结论：没有全面赢家，所以做选型表；近缘简单方法够；跨门这一族做不了。

两件没做完：容器最后一步没跑成（本机没有 WSL），映射表的签字只到授权层、不是生物学同行逐行看过。

如果只记一句：算得对是底线，分得对要人签字。"

不要煽情，说完停两秒。""")
concl = [
    ("没有全面赢家", "不排总分，只做「场景 → 方法」"),
    ("近缘，简单就够", "人↔鼠基本打平；最土的办法 27 秒、无 GPU"),
    ("跨门，这一族做不了", "比随机猜还低，是有价值的负结果"),
]
colx = [0.67, 4.72, 8.77]
for i, (head, sub) in enumerate(concl):
    x = colx[i]
    rect(s, x, 1.95, 3.75, 0.04, GOLD)
    tb(s, x, 2.10, 3.75, 0.4, [f"0{i + 1}"], 11, True, MUTED)
    tb(s, x, 2.45, 3.75, 0.5, [head], 17, True, NAVY)
    tb(s, x, 3.00, 3.75, 1.0, [sub], 11, False, INK, spacing=1.45)
rect(s, 0.67, 4.30, 11.98, 0.015, RULE)
tb(s, 0.67, 4.48, 5.6, 0.32, ["容器的一步没跑"], 12, True, NAVY)
tb(s, 0.67, 4.82, 5.6, 0.7, ["配方与平台镜像已验证，镜像内 6/6 复现；\n本机缺 WSL，docker build 未执行"], 9.5, False, MUTED, spacing=1.35)
tb(s, 6.85, 4.48, 5.6, 0.32, ["映射表签字只到「授权」"], 12, True, NAVY)
tb(s, 6.85, 4.82, 5.6, 0.7, ["38 行已签认留痕；不等于生物学同行\n逐行复核"], 9.5, False, MUTED, spacing=1.35)

OUT.parent.mkdir(parents=True, exist_ok=True)
src.save(str(OUT))
print("saved:", OUT)
print("slides:", len(src.slides._sldIdLst))
print("bytes:", OUT.stat().st_size)