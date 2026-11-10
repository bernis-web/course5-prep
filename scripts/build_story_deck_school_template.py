# -*- coding: utf-8 -*-
"""在学校模板上重建「讲故事」汇报版（2026-11-10）

原则：
  1. 以学校模板文件为底（母版/顶栏蓝金条/校徽/底部结论条全部保留）
  2. 只复制模板页、只填内容，不新建空白版式
  3. 每页一个观点；讲稿写进备注
  4. 严格沿用模板排版：标题 24pt #12365A、副标题 12.5pt #60758F、
     底部结论句 13pt bold #8A4B00（浅金条 #FFF2CC 上）

输出：deliverables/课题5-汇报-讲故事版-学校模板-20261110.pptx
"""
from copy import deepcopy
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

ROOT = Path(r"D:\projects\course5-prep")
TPL = ROOT / "results" / "stage-reports-20261102" / "课题5第03次汇报_三场景结论与可复现闭环.pptx"
OUT = ROOT / "deliverables" / "课题5-汇报-讲故事版-学校模板-20261110.pptx"

# 模板令牌（从模板读出，不自己发明）
NAVY = RGBColor(0x12, 0x36, 0x5A)
MUTED = RGBColor(0x60, 0x75, 0x8F)
GOLDD = RGBColor(0x8A, 0x4B, 0x00)
GOLD = RGBColor(0xFF, 0xC0, 0x00)
CREAM = RGBColor(0xD7, 0xE8, 0xF8)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
INK = RGBColor(0x1F, 0x2D, 0x3D)
BAND = RGBColor(0xFF, 0xF2, 0xCC)
RULE = RGBColor(0xB7, 0xC9, 0xD6)
RED = RGBColor(0xA8, 0x32, 0x2A)
FONT = "微软雅黑"

FOOTER = "课题5 · XenoTransfer v1.0 · 对外汇报（含 11-09 更正）· 2026-11-10"


def ea(run, name=FONT):
    """同时设拉丁与中文（a:ea）字体，避免中文回落到宋体。"""
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


def add_tb(slide, x, y, w, h, lines, size, bold=False, color=INK,
           align=PP_ALIGN.LEFT, spacing=1.3, anchor=MSO_ANCHOR.TOP):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = 0
    tf.margin_top = tf.margin_bottom = 0
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


def add_rect(slide, x, y, w, h, color, line=None):
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid()
    s.fill.fore_color.rgb = color
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(0.75)
    s.shadow.inherit = False
    return s


def add_notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


# ═══════════════════════════════════════════════════════
src = Presentation(str(TPL))

# 删掉除封面(0)与正文样本(1)以外的页
# ⚠ 必须 drop_rel，否则部件仍留在包里，新页会产生同名 slideN.xml → 文件损坏
def delete_slide(prs, idx):
    lst = prs.slides._sldIdLst
    sld = list(lst)[idx]
    rId = sld.get(qn("r:id"))
    prs.part.drop_rel(rId)
    lst.remove(sld)


while len(src.slides._sldIdLst) > 2:
    delete_slide(src, len(src.slides._sldIdLst) - 1)

DONOR = [deepcopy(sh._element) for sh in src.slides[1].shapes]
LAYOUT = src.slide_layouts[0]


def new_body_slide():
    s = src.slides.add_slide(LAYOUT)
    for el in DONOR:
        s.shapes._spTree.append(deepcopy(el))
    drop(s, "Table 0")
    return s


def chrome(s, num, title, subtitle, takeaway, notes_text):
    fill_text(find(s, "Text 2"), [title], 24, True, NAVY)
    fill_text(find(s, "Text 3"), [subtitle], 12.5, False, MUTED)
    fill_text(find(s, "Text 4"), [FOOTER], 8.5, False, MUTED)
    fill_text(find(s, "Text 5"), [f"{num:02d}"], 8.5, False, MUTED, align=PP_ALIGN.RIGHT)
    fill_text(find(s, "Text 7"), [takeaway], 13, True, GOLDD)
    add_notes(s, notes_text)


# ═══════════════════════════════════════════════════════
# P1 封面（填模板封面）
# ═══════════════════════════════════════════════════════
c = src.slides[0]
fill_text(find(c, "Text 1"), ["四种方法，一张选型表"], 32, True, WHITE)
fill_text(find(c, "Text 2"), ["拿一个物种的细胞图鉴，去推另一个物种——测了四种做法"], 17, False, CREAM)
fill_text(find(c, "Text 3"), ["三个难度档全部实测：近缘 · 远缘 · 跨门"], 13, False, CREAM)
fill_text(find(c, "Text 4"), ["并且，中途我们自己算错过一次——本期讲清怎么发现的、改完变成什么样"], 13, False, CREAM)
fill_text(find(c, "Text 5"), ["全流程可复现 · 平台算力 ¥2.47 · 镜像内 6/6 复现"], 13, False, CREAM)
fill_text(find(c, "Text 6"), [FOOTER], 11.5, False, RGBColor(0xDD, 0xEB, 0xFA))
fill_text(find(c, "Text 8"), ["算得对是底线，分得对要人签字。"], 13, True, GOLDD)
add_notes(c, """【开场 30 秒，看着人说，不要看屏幕】

"今天不讲一堆数字。就讲一件事：我们想知道，能不能拿一个物种的细胞图鉴，去推断另一个物种的细胞类型——以及，当我们以为找到答案的时候，是怎么发现自己错了的。"

停一秒再翻页。""")

# ═══════════════════════════════════════════════════════
# P2 场景钩子
# ═══════════════════════════════════════════════════════
s = src.slides[1]
chrome(s, 2, "先想象一件事", "不用任何术语，就一个场景",
       "整个项目，就是为了回答这个'要不要'。",
       """【讲这个场景，语速慢】

"你手上有一本'人的细胞图鉴'——每个细胞都标好了类型：心肌、内皮、免疫。

然后有人递给你一盒小鼠的细胞，但它没有标签。

你要不要用它，去猜？"

停一下，再翻页。""")
add_tb(s, 0.67, 2.0, 11.9, 0.7, ["你手上有一本"], 20, False, MUTED)
add_tb(s, 0.67, 2.45, 11.9, 1.0, ["人的细胞图鉴"], 40, True, NAVY)
add_tb(s, 0.67, 3.75, 11.9, 0.9, ["然后有人递给你一盒小鼠的细胞，", "但它没有标签。"], 24, False, INK, spacing=1.45)
add_rect(s, 0.67, 5.35, 2.2, 0.06, GOLD)
add_tb(s, 0.67, 5.55, 11.9, 0.7, ["你要不要——用它，去猜？"], 26, True, GOLDD)

# ═══════════════════════════════════════════════════════
# P3 三档难度
# ═══════════════════════════════════════════════════════
s = new_body_slide()
chrome(s, 3, "但「另一个物种」有三个难度档", "后面每次提到一个场景，先想它是哪一档",
       "三档都测，才有资格说「哪种方法在哪一档靠得住」。",
       """【这是全场框架，听众后面全靠它定位】

"人跟小鼠很近，都是哺乳动物，基因基本能一一对上。
人跟斑马鱼，中间隔了几亿年，只有一部分基因还对得上。
七鳃鳗跟小鼠，连门都不一样了。"

最后一句："很多论文只测最容易那档。我们三档都测。" """)
rows = [
    ("最容易", "人 ↔ 小鼠", "同属哺乳动物，基因基本能一一对上", NAVY),
    ("中间档", "人 ↔ 斑马鱼", "隔了几亿年，只有部分基因还对得上", MUTED),
    ("最难", "七鳃鳗 ↔ 小鼠", "连「门」都不同，几乎只能靠猜", RED),
]
y = 2.05
for tag, pair, desc, col in rows:
    add_rect(s, 0.67, y, 11.98, 0.015, RULE)
    add_tb(s, 0.67, y + 0.2, 1.5, 0.4, [tag], 12.5, False, MUTED)
    add_tb(s, 2.25, y + 0.1, 4.0, 0.6, [pair], 24, True, col)
    add_tb(s, 6.5, y + 0.22, 6.0, 0.5, [desc], 13, False, INK)
    y += 1.32
add_rect(s, 0.67, y, 11.98, 0.015, RULE)

# ═══════════════════════════════════════════════════════
# P4 四种方法
# ═══════════════════════════════════════════════════════
s = new_body_slide()
chrome(s, 4, "四种做法，四种性格", "不用记名字，记它靠什么",
       "留一个「土办法」当基线：任何复杂方法都得先打得过它。",
       """【讲得轻快，用比喻，不要念参数】

"oPCA 最土：只拿两个物种共有的词做对照表，27 秒、不要显卡。
scVI 是深度模型，但干的事很朴素：让细胞住进同一个小区，按邻居判断。
SATURN 不查词了，把基因翻译成蛋白质语言，看意思像不像。
SAMap 画族谱，按亲缘关系找。"

最后补："我们特意留了最土那个当基线。" 不报任何分数。""")
cards = [
    ("ortholog-PCA", "只拿两本书共有的词\n做对照表", "27 秒 · 不用 GPU", GOLD),
    ("scVI", "让细胞住进同一个小区\n按邻居判断", "CPU 8.5 分钟", RULE),
    ("SATURN", "不查词了\n改看「意思」像不像", "要 GPU 训练", RULE),
    ("SAMap", "画一张两族人的族谱\n再对着找", "依赖最多、最不稳", RED),
]
cw, chh = 5.85, 1.85
x0, y0 = 0.67, 2.05
for i, (nm, meta, cost, line) in enumerate(cards):
    cx = x0 + (i % 2) * (cw + 0.28)
    cy = y0 + (i // 2) * (chh + 0.2)
    add_rect(s, cx, cy, cw, chh, WHITE, line=RGBColor(0xD9, 0xD2, 0xC4))
    add_rect(s, cx, cy, 0.05, chh, line)
    add_tb(s, cx + 0.28, cy + 0.16, cw - 0.5, 0.35, [nm], 17, True, NAVY)
    add_tb(s, cx + 0.28, cy + 0.62, cw - 0.5, 0.8, meta.split("\n"), 13, False, INK, spacing=1.35)
    add_tb(s, cx + 0.28, cy + chh - 0.38, cw - 0.5, 0.3, [cost], 10.5, False, MUTED)

# ═══════════════════════════════════════════════════════
# P5 家底
# ═══════════════════════════════════════════════════════
s = new_body_slide()
chrome(s, 5, "先交代家底", "这三个数字请记住",
       "4,606 很小——所以每个结论都要带「在这个规模上」。",
       """【这是可信度铺垫，不是炫耀】

"4,606 个细胞，三个物种。这个数字很小，我后面会反复提到。
三个难度档都跑了。
全部算力在平台上，四个任务，两块四毛七，三个小时出头。"

然后强调："4,606 很小。所以后面每个结论，都只能限定在这个规模上说。"

如果问"是不是太少了"——老实说"是"。""")
nums = [
    ("4,606", "个细胞", "人 1,528 · 鼠 1,535 · 鱼 1,543"),
    ("3", "个难度档", "近缘 / 远缘 / 跨门，全部实测"),
    ("¥2.47", "平台算力花费", "4 个任务 · 合计 3 小时 18 分"),
]
x = 0.67
for big, unit, sub in nums:
    add_tb(s, x, 2.15, 3.7, 1.0, [big], 46, True, NAVY)
    add_tb(s, x, 3.15, 3.7, 0.35, [unit], 14, False, INK)
    add_tb(s, x, 3.6, 3.7, 0.8, [sub], 11, False, MUTED, spacing=1.5)
    x += 4.0
add_rect(s, 0.67, 4.65, 11.98, 0.015, RULE)
add_tb(s, 0.67, 4.85, 11.9, 1.2,
       ["这些数不是为了好看，是为了让你知道：", "我们敢说的边界在哪里。"], 17, False, INK, spacing=1.5)

# ═══════════════════════════════════════════════════════
# P6 反直觉
# ═══════════════════════════════════════════════════════
s = new_body_slide()
chrome(s, 6, "第一个反直觉", "这条改变了我们的选型建议",
       "没有 GPU 的人，现在不只是能用最土的办法。",
       """【小高潮，要有语气】

"scVI 是深度生成模型，一般都要显卡。
但在我们这个规模上——四千多个细胞——它 CPU 八分半就跑完了。
所以没有 GPU 的人，现在不只是能用最土的办法，还能用 scVI。"

如果被追问："因为数据小。换成几十万细胞就未必。"——主动补这句。""")
add_tb(s, 0.67, 2.1, 11.9, 0.6, ["「深度学习必须用显卡」"], 30, True, NAVY)
add_tb(s, 0.67, 2.75, 11.9, 0.6, ["在这套数据上不成立。"], 30, True, GOLDD)
add_rect(s, 0.67, 3.55, 2.2, 0.06, GOLD)
add_tb(s, 0.67, 3.75, 11.9, 1.6,
       ["scVI 是深度生成模型，但要 4,606 个细胞、9,018 个基因这个规模，",
        "CPU 8.5 分钟就跑完了（平台实测含 IO：15 分 16 秒）。"], 15, False, INK, spacing=1.6)

# ═══════════════════════════════════════════════════════
# P7 结果表
# ═══════════════════════════════════════════════════════
s = new_body_slide()
chrome(s, 7, "谁赢了：一张表就够", "coarse macro-F1（每类等权平均，不被大类绑架）· 越大越好",
       "六行里五行是 scVI，只有「鼠→人」输给了最土的办法。",
       """【只念两行，别念完六行】

"只看三件事：
第一，金色的是每行最强。六行里五行是 scVI。
第二，只有一行被最土的办法赢了——鼠→人。说明近缘场景，简单方法真的够用。
第三，「—」不是 0 分，是那个方向没有细胞能对上，没法评。"

收："所以结论不是'哪个方法最好'，而是'什么场景用哪个'。\"""")
data = [
    ["方向", "最土基线", "scVI", "SATURN", "SAMap"],
    ["人 → 鼠", "0.64", "0.67", "0.35", "0.11"],
    ["鼠 → 人", "0.67", "0.59", "0.26", "0.04"],
    ["人 → 斑马鱼", "0.17", "0.40", "0.13", "0.05"],
    ["斑马鱼 → 人", "0.15", "0.43", "0.14", "—"],
    ["鼠 → 斑马鱼", "0.22", "0.42", "0.41", "—"],
    ["斑马鱼 → 鼠", "0.44", "0.48", "0.30", "—"],
]
gold_cells = {(1, 2), (2, 1), (3, 2), (4, 2), (5, 2), (6, 2)}
top, rowh = 2.1, 0.44
colx = [0.67, 3.05, 5.45, 7.85, 10.25]
colw = 2.15
for ri in range(7):
    for ci in range(5):
        if ri == 0:
            add_rect(s, colx[ci], top + ri * rowh, colw, 0.4, BAND)
        elif (ri, ci) in gold_cells:
            add_rect(s, colx[ci], top + ri * rowh, colw, 0.4, RGBColor(0xFF, 0xF7, 0xE0))
    add_rect(s, 0.67, top + ri * rowh + 0.4, 11.7, 0.01, RULE)

for ri, row in enumerate(data):
    for ci, val in enumerate(row):
        is_head = ri == 0
        strong = (ri, ci) in gold_cells
        add_tb(s, colx[ci] + 0.1, top + ri * rowh + 0.09, colw - 0.2, 0.28,
               [val], 11.5 if is_head else 13.5, (is_head or strong),
               MUTED if is_head else (GOLDD if strong else INK))
add_tb(s, 0.67, 5.5, 11.9, 0.5,
       ["「—」不是 0 分，是那个方向没有任何细胞能对上，无法评估。"], 11, False, MUTED)

# ═══════════════════════════════════════════════════════
# P8 转折
# ═══════════════════════════════════════════════════════
s = new_body_slide()
chrome(s, 8, "但在讲结论之前", "这一页是全场唯一一次「先认错」",
       "而且是会让排名反过来那种错。",
       """【全场最重要的三秒。停下来，看着大家】

"在讲结论之前，我得先承认一件事：我们中间算错过一次。"

（停三秒）

"不是小数点那种错。是会让排名反过来那种错。而且是我们自己查出来的。"

这页不要急着翻。后面的可信度全靠这页。""")
add_tb(s, 0.67, 2.15, 11.9, 0.5, ["我得先告诉你："], 16, False, MUTED)
add_tb(s, 0.67, 2.6, 11.9, 1.9, ["我们算错过一次。"], 46, True, RED)
add_rect(s, 0.67, 4.35, 2.4, 0.06, GOLD)
add_tb(s, 0.67, 4.6, 11.9, 1.1,
       ["而且是我们自己查出来的——查出来之后，所有数字重算了一遍。"], 16, False, INK)

# ═══════════════════════════════════════════════════════
# P9 错在哪
# ═══════════════════════════════════════════════════════
s = new_body_slide()
chrome(s, 9, "错在哪：查字典，查错了语种", "每个物种的细胞类型，是各自一套词",
       "不是查得慢，是查不到——然后你把它划掉了。",
       """【先讲比喻，再讲代码】

"人分心房肌、心室肌；小鼠统称心肌细胞；斑马鱼里甚至有个 Orthers，是 Others 的拼写错误。

规矩：真值用被预测那方的词表，预测用参考书那方的词表。我们把两边搞反了。

后果是两边各丢一批细胞：真值查不到的跳过，预测查不到的记成'对不上'再丢一次。

说白了就是拿法语词典查英语单词。"

讲完，听众应该能自己推出'分数会被抬高'。""")
add_tb(s, 0.67, 2.05, 5.4, 0.35, ["规矩本来是这样的"], 12, False, MUTED)
add_tb(s, 0.67, 2.4, 5.4, 1.0, ["真值 → 查【被预测方】词表", "预测 → 查【参考书方】词表"], 14, False, INK, spacing=1.5)
add_rect(s, 0.67, 3.55, 5.2, 0.015, RULE)
add_tb(s, 0.67, 3.72, 5.4, 0.35, ["我们写成了"], 12, False, MUTED)
add_tb(s, 0.67, 4.07, 5.4, 1.0, ["真值 → 查【参考书方】词表", "预测 → 查【被预测方】词表"], 14, True, RED, spacing=1.5)

add_rect(s, 6.5, 2.05, 0.015, 3.6, RULE)
add_tb(s, 6.85, 2.05, 5.8, 0.35, ["后果：两边各丢一批细胞"], 12, False, MUTED)
add_tb(s, 6.85, 2.45, 5.8, 2.9,
       ["① 真值查不到 → 直接跳过",
        "　 小鼠的「心肌细胞」在人词表里",
        "　 不存在（人分心房/心室）",
        "",
        "② 预测查不到 → 记成「对不上」",
        "　 再丢一次。人的「心房肌」",
        "　 在小鼠词表里也不存在"], 13, False, INK, spacing=1.45)

# ═══════════════════════════════════════════════════════
# P10 怎么证明
# ═══════════════════════════════════════════════════════
s = new_body_slide()
chrome(s, 10, "怎么证明「就是查错了」", "而不是我事后找借口",
       "这一步，是我们敢改结论的全部底气。",
       """【这页要讲得硬，这是挡箭牌】

"做法是：拿同一份结果，按四种查表方式各算一遍。

只有'查错的那种'，能一字不差复现我们原来的全部旧数字——六个方向全中，准确率也全中。

换句话说：不是我猜旧代码怎么写，是旧代码只能这么写，才可能算出那组数。"

如果问"怎么知道是旧的错"——答：生物学上真值只能是目标物种的注释，这不是约定，是事实。""")
add_tb(s, 0.67, 2.1, 11.9, 0.6, ["拿同一份结果，按四种查表方式各算一遍。"], 20, True, NAVY)
add_tb(s, 0.67, 2.85, 11.9, 1.0,
       ["只有「查错的那种」，能一字不差复现原来的全部旧数字——", "六个方向全中，准确率也全中。"], 15, False, INK, spacing=1.55)
add_rect(s, 0.67, 4.05, 11.7, 1.15, BAND)
add_tb(s, 0.95, 4.25, 11.1, 0.8,
       ["不是我猜旧代码怎么写，是旧代码只能这么写，才可能算出那组数。"], 17, True, GOLDD)

# ═══════════════════════════════════════════════════════
# P11 改完之后
# ═══════════════════════════════════════════════════════
s = new_body_slide()
chrome(s, 11, "改完之后：排名没变，但理由变了", "对外一律用「保留细胞、对不上算错」的口径",
       "「鼠↔鱼用 SATURN」被推翻；「远缘用 scVI」没变。",
       """【先给旧数，再给新数，落差要说出来】

"原来 SATURN 在鼠↔鱼是 0.65，比 scVI 的 0.42 高一大截，所以我们当时写'鼠↔鱼用 SATURN'。
改完是 0.41，比 scVI 还低，六个方向一个都不赢。所以那条建议被推翻。

但'远缘用 scVI'没变——它本来就不靠那一格撑着。\"""")
add_rect(s, 0.67, 2.05, 5.6, 2.2, RGBColor(0xF2, 0xF6, 0xFA), line=RULE)
add_tb(s, 0.95, 2.22, 5.0, 0.3, ["旧（错）"], 11.5, False, MUTED)
add_tb(s, 0.95, 2.55, 5.2, 0.7, ["SATURN 0.65"], 30, True, RED)
add_tb(s, 0.95, 3.35, 5.2, 0.6, ["比 scVI 的 0.42 高"], 14, False, INK)

add_rect(s, 6.65, 2.05, 6.0, 2.2, BAND, line=RGBColor(0xE8, 0xD2, 0x96))
add_tb(s, 6.95, 2.22, 5.4, 0.3, ["新（对）"], 11.5, False, MUTED)
add_tb(s, 6.95, 2.55, 5.4, 0.7, ["SATURN 0.41"], 30, True, GOLDD)
add_tb(s, 6.95, 3.35, 5.4, 0.8, ["比 scVI 的 0.42 低", "六个方向一个都不赢"], 14, False, INK, spacing=1.4)
add_tb(s, 0.67, 4.5, 11.9, 1.5,
       ["所以「鼠↔鱼用 SATURN」这条建议被推翻了。",
        "但「远缘用 scVI」这个结论没变——它本来就不靠那一格撑着。"], 15, False, INK, spacing=1.55)

# ═══════════════════════════════════════════════════════
# P12 第二个错
# ═══════════════════════════════════════════════════════
s = new_body_slide()
chrome(s, 12, "顺手还查出一个", "这条比上一条轻，但同样要交代",
       "残差桶不该被当成一个细胞类型。",
       """【语气放轻，这是第二个错】

"斑马鱼数据里有个类别叫 Orthers，是 Others 的拼写错误，意思是'实在归不了类'。
而我们的映射表把它整个算成了'神经细胞'。

处理：这一类直接退出评估——它本来就不是一个细胞类型。
另外两行，瓣膜算成纤维、血管周细胞算平滑肌，可以辩护，保留，但写清依据和影响。"

可补："旧文档写'865 个细胞错归'不准，865 是被预测成这个类别的细胞数，真值侧只有 30 个。\"""")
add_tb(s, 0.67, 2.2, 11.9, 1.0, ["「其他」被当成了「神经」。"], 34, True, NAVY)
add_rect(s, 0.67, 3.35, 2.2, 0.06, GOLD)
add_tb(s, 0.67, 3.55, 11.9, 1.5,
       ["斑马鱼数据里有个类别叫 Orthers——那是 Others 的拼写错误，「实在归不了类」。",
        "而我们的映射表，把它整个算成了「神经细胞」。"], 15, False, INK, spacing=1.6)
add_rect(s, 0.67, 5.05, 11.7, 0.015, RULE)
add_tb(s, 0.67, 5.2, 11.9, 1.0,
       ["处理：这一类直接退出评估（它本来就不是一个细胞类型）。",
        "另两行（瓣膜算成纤维、血管周细胞算平滑肌）保留，但写清依据与影响。"], 13, False, MUTED, spacing=1.5)

# ═══════════════════════════════════════════════════════
# P13 三条结论
# ═══════════════════════════════════════════════════════
s = new_body_slide()
chrome(s, 13, "所以，三条结论", "每条只讲一件事",
       "所有结论都限定在 4,606 个细胞、同批数据重评估。",
       """【一条一条说，每条停一下】

"第一，没有全面赢家。所以交付物不是'第一名'，是一张选型表。
第二，近缘场景，简单方法就够了。人跟小鼠基本打平，最土那个 27 秒、不要显卡。
第三，跨门，这一族方法都做不了。准确率比随机猜还低。我们把它当负结果写下来，不藏。"

时间紧就只讲第一和第三条。""")
concl = [
    ("没有全面赢家", "所以不排总分冠军，只做「什么场景用什么」的选型表"),
    ("近缘，简单就够", "人↔鼠基本打平；最土的办法 27 秒、不要显卡"),
    ("跨门，这一族都做不了", "七鳃鳗↔小鼠比随机猜还低——这是有价值的负结果"),
]
y = 2.1
for i, (head, sub) in enumerate(concl):
    add_tb(s, 0.67, y, 0.6, 0.5, [str(i + 1)], 22, True, GOLD)
    add_tb(s, 1.35, y - 0.05, 11.2, 0.5, [head], 22, True, NAVY)
    add_tb(s, 1.35, y + 0.48, 11.2, 0.4, [sub], 13, False, MUTED)
    if i < 2:
        add_rect(s, 0.67, y + 1.05, 11.7, 0.01, RULE)
    y += 1.32

# ═══════════════════════════════════════════════════════
# P14 还剩什么
# ═══════════════════════════════════════════════════════
s = new_body_slide()
chrome(s, 14, "最后，两件没做完的", "我们不想把它讲成一个完成的故事",
       "算得对是底线，分得对要人签字。",
       """【语气要平，不要像道歉】

"第一，容器的最后一步没跑成。配方验证过，平台镜像建好、镜像内六个值逐位复现；但本机没有 WSL，那条 docker build 没执行。我们知道差哪一步。

第二，映射表的签字只到'授权'层。38 行都签了、有留痕，但那不等于生物学同行逐行看过。要投稿建议再找个人抽查 20%。"

收尾那句，慢一点说。""")
items = [
    ("容器的一步没跑", "配方全部验证 · 平台镜像已建 · 镜像内 6 个值逐位复现；但本机缺 WSL，docker build 未执行"),
    ("生物学的签字只到「授权」", "38 行已签认留痕，但那是项目负责人授权 + 程序复核；不等于生物学同行逐行看过"),
]
y = 2.1
for head, body in items:
    add_rect(s, 0.67, y, 11.7, 0.015, RULE)
    add_tb(s, 0.67, y + 0.18, 11.5, 0.4, [head], 16, True, RED)
    add_tb(s, 0.67, y + 0.68, 11.5, 0.8, [body], 12.5, False, INK, spacing=1.5)
    y += 1.7
add_tb(s, 0.67, 5.75, 11.9, 0.5,
       ["如果只记一句：算得对是底线，分得对要人签字。"], 17, True, GOLDD)

OUT.parent.mkdir(parents=True, exist_ok=True)
src.save(str(OUT))
print("saved:", OUT)
print("slides:", len(src.slides.__iter__.__self__._sldIdLst))
print("bytes:", OUT.stat().st_size)