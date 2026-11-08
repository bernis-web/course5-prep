# -*- coding: utf-8 -*-
"""把第 2 次汇报内容稿导出为 Word（A4，宋体正文 + 微软雅黑标题）。"""
import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

OUT = "D:/projects/course5-prep/docs/reports/课题5第02次汇报_数字来源链_内容稿.docx"
INK = RGBColor(0x1F, 0x2D, 0x3D)
BLUE = RGBColor(0x00, 0x5B, 0xAC)
MUTED = RGBColor(0x60, 0x75, 0x8F)

doc = Document()

# page setup
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
sec.left_margin = sec.right_margin = Cm(2.4)
sec.top_margin = sec.bottom_margin = Cm(2.2)

# base style
st = doc.styles["Normal"]
st.font.name = "宋体"
st.font.size = Pt(10.5)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
st.paragraph_format.line_spacing = 1.5
st.paragraph_format.space_after = Pt(4)


def set_run(run, size=10.5, bold=False, color=INK, font="宋体"):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = font
    rPr = run._element.get_or_add_rPr()
    rf = rPr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rPr.append(rf)
    rf.set(qn("w:eastAsia"), font)
    rf.set(qn("w:ascii"), "Segoe UI" if font == "微软雅黑" else font)
    rf.set(qn("w:hAnsi"), "Segoe UI" if font == "微软雅黑" else font)


def para(text="", size=10.5, bold=False, color=INK, font="宋体",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=4):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    if text:
        r = p.add_run(text)
        set_run(r, size, bold, color, font)
    return p


def h1(text):
    p = para(text, size=16, bold=True, color=BLUE, font="微软雅黑",
             align=WD_ALIGN_PARAGRAPH.LEFT, space_before=14, space_after=6)
    p.paragraph_format.keep_with_next = True
    return p


def h2(text):
    p = para(text, size=12.5, bold=True, color=BLUE, font="微软雅黑",
             align=WD_ALIGN_PARAGRAPH.LEFT, space_before=12, space_after=4)
    p.paragraph_format.keep_with_next = True
    return p


def bullet(text):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(text)
    set_run(r, 10.5, False, INK, "宋体")


def shade(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hexcolor)
    tcPr.append(shd)


def table(headers, rows, widths=None, aligns=None):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    tblPr = t._tbl.tblPr
    layout = OxmlElement("w:tblLayout")
    layout.set(qn("w:type"), "fixed")
    tblPr.append(layout)
    hdr = t.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = ""
        p = hdr[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        set_run(r, 10, True, RGBColor(0xFF, 0xFF, 0xFF), "微软雅黑")
        shade(hdr[i], "005BAC")
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            p = cells[i].paragraphs[0]
            p.alignment = (aligns[i] if aligns else
                           (WD_ALIGN_PARAGRAPH.LEFT if i == 0 else WD_ALIGN_PARAGRAPH.CENTER))
            r = p.add_run(str(v))
            set_run(r, 9.5, False, INK, "宋体")
    if widths:
        for i, w in enumerate(widths):
            t.columns[i].width = Cm(w)
            for row in t.rows:
                row.cells[i].width = Cm(w)
    para("", size=6, space_after=2)
    return t


def note(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.left_indent = Cm(0.4)
    r = p.add_run(text)
    set_run(r, 9.5, False, MUTED, "宋体")


# ---------------- 标题 ----------------
para("课题5 第 2 次汇报（第 2/7 次）", size=11, bold=True, color=MUTED, font="微软雅黑",
     align=WD_ALIGN_PARAGRAPH.LEFT, space_after=2)
para("数字来源链：一个百分比是怎么来的", size=22, bold=True, color=RGBColor(0x12, 0x36, 0x5A),
     font="微软雅黑", align=WD_ALIGN_PARAGRAPH.LEFT, space_after=4)
para("配套 PPT：results/stage-reports-20261019/课题5第02次汇报_数字来源链_校模板.pptx（9 页，7 分 55 秒）",
     size=8.5, color=MUTED)
para("口径：全部 transductive / in-sample；单 seed（0）；K=15 cosine 倒距离加权 ｜ 日期：2026-10-19",
     size=8.5, color=MUTED, space_after=10)

# ---------------- 节奏 ----------------
h1("汇报节奏")
table(["页", "内容", "建议用时"], [
    ["1", "封面", "10 秒"],
    ["2", "任务定位与进度", "45 秒"],
    ["3", "老师反馈与本次调整", "55 秒"],
    ["4", "来源链八环节", "60 秒"],
    ["5", "86.18% 拆解", "80 秒"],
    ["6", "分母与四个量", "60 秒"],
    ["7", "macro-F1 两种口径", "55 秒"],
    ["8", "四方法结果", "50 秒"],
    ["9", "选型指南 v0", "60 秒"],
], widths=[1.2, 8.0, 3.0])
note("合计约 7 分 55 秒。")

# ---------------- 1 ----------------
h1("第 1 页 · 封面")
para("标题：课题5 第 2 次汇报：数字来源链")
para("副标题：一个百分比是怎么来的 —— 从原始细胞到表格单元格的可复核路径")
h2("口播")
para("这次不讲新结果，讲现有数字是怎么来的。")

# ---------------- 2 ----------------
h1("第 2 页 · 任务定位：本次讲的是哪一块")
para("顶部先给课程原题：跨物种单细胞整合：SATURN vs SAMap vs scVI 系的基准测试与场景化选型。")
table(["课程要求", "状态"], [
    ["四方法对比（含自建 oPCA 基线）", "已完成"],
    ["主指标 macro-F1（统一口径）", "已完成"],
    ["场景：近缘 + 无 GPU", "已完成"],
    ["批次混合与生物保守性", "进行中（scVI 已测）"],
    ["时间与内存", "进行中（scVI 已测）"],
    ["场景：跨门（七鳃鳗 ↔ 鼠）", "未开始（数据已定位）"],
    ["文档 / Agent 友好度 + 容器化", "未开始"],
], widths=[8.5, 5.0])
para("进度：3 / 7 完成，2 项进行中，2 项未开始。")
para("本次覆盖：第 2 项「主指标」的底层——一个百分比是怎么算出来的。")
para("下次覆盖第 1 项与第 6 项的边界问题：为什么不能排冠军。")
h2("口播提示")
para("这页只花 45 秒，作用是让老师立刻知道“现在讲到任务的哪一块、整体到哪一步”，后面就不用每页再解释上下文。")

# ---------------- 3 ----------------
h1("第 3 页 · 老师反馈之后：先改交付物类型")
bullet("老师说的「偏」：不是数字不准，而是整份材料回答错了问题——在讲“证据可不可信”，没讲“哪个方法该在什么场景用”。")
bullet("根因：交付物类型错了。课程要的是「场景 → 方法 → 指标 → 选型」的基准报告，我们交的是审计报告。")
bullet("本次怎么改：保留证据链（它是对的），但把它从“全部篇幅”降为“支撑材料”；主线回到方法与场景。")
para("收束句：本次先补上“数字怎么来的”这一层，把可信度做成可复核的底子；下一次再讲“为什么不能排冠军”。", space_before=4)
h2("口播提示")
para("这页要快，不要自我检讨太久；重点是“改了什么”，不是“错在哪”。")

# ---------------- 4 ----------------
h1("第 4 页 · 从原始细胞到表格单元格：八个环节")
table(["#", "环节", "落盘物"], [
    ["1", "原始 h5ad", "三物种心脏单细胞"],
    ["2", "归一化", "normalize_total(1e4) + log1p"],
    ["3", "表示层", "同源交集 + PCA-50"],
    ["4", "角色划分", "src = reference，tgt = query"],
    ["5", "KNN15", "cosine，倒距离加权"],
    ["6", "逐细胞预测", "含 confidence 与排除原因"],
    ["7", "排除与计数", "correct / eligible = n_q"],
    ["8", "metrics.json", "SHA-256 锚定"],
], widths=[1.2, 4.0, 9.0], aligns=[WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT])
para("核心句：换掉任何一环的定义，最终百分比就会变——所以复核必须沿这条链走，而不是从表里抄数。")
para("补充：每一环都有落盘物，第三方可以据此重算任意一个单元格。")

# ---------------- 5 ----------------
h1("第 5 页 · 实例拆解：86.18% = 1,297 ÷ 1,505")
table(["环节", "内容", "取值"], [
    ["输入", "reference = 人 ｜ query = 鼠", "1,528 / 1,535"],
    ["同源基因", "人鼠 1:1 直系同源交集", "15,869"],
    ["表示层", "人+鼠联合 PCA-50（seed 0）", "3,063 × 50"],
    ["评分", "KNN15，cosine，倒距离加权", "k = 15"],
    ["排除", "鼠侧 status ≠ active", "剔 30"],
    ["eligible query", "1,535 − 30", "n_q = 1,505"],
    ["正确数", "逐细胞预测 == 真值", "1,297"],
], widths=[3.2, 7.0, 4.0], aligns=[WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER])
para("核心句：86.18% = 正确预测数 ÷ 排除后仍有资格的 query 细胞。不是从表里抄出来的。", bold=True)
para("逐类分解（confusion 摘录）：内皮 720/725、成纤维 255/360、免疫 197/202、心肌 19/47；错误集中在成纤维→平滑肌（82）与心肌→内皮（27）。")
note("主源：results/pilot-v1/ortholog-pca-v98/metrics.json，SHA b2b3ac6b…c725，本地已独立复算。")

# ---------------- 6 ----------------
h1("第 6 页 · 分母会变，所以必须一起报")
para("同一个 coarse 层，query 细胞 1,535 个，排除 30 个后不再进入分母。eligible 1,505，coverage 98.05%。")
table(["必须并列报的量", "定义", "为什么必须报"], [
    ["accuracy", "correct ÷ n_q", "主指标"],
    ["n_q / coverage", "进入分母的细胞数", "排除规则一改，分母就变"],
    ["majority", "最大真值类占比", "无信息基线：准确率 0.4817，macro-F1 仅 0.0813"],
    ["shuffle_p", "预测向量置换检验", "只回答“是否优于随机”，不是多数类检验"],
], widths=[3.4, 4.4, 6.0], aligns=[WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT])
para("核心句：只报 accuracy，等于把分母的变化藏起来。", bold=True)

# ---------------- 7 ----------------
h1("第 7 页 · 同一份预测，两个 macro-F1")
bullet("truth-only（平台 scVI 脚本默认）：0.4516 —— 只按真实标签集取平均；预测多出来的类被忽略。")
bullet("union（本项目跨方法统一口径）：0.4014 —— 真实 ∪ 预测一起取平均；预测多出来的类记 F1 = 0。")
para("差值来源：被预测出来、但真值里根本不存在的类。这类越多，两个口径差得越大。", space_before=4)
para("核心句：单独看 truth-only 没问题，但它不能和别的方法并列；跨方法对比一律用 union，从 18 个逐细胞预测文件独立重算。", bold=True)
para("例子：人→斑马鱼 coarse，两个口径差 0.05——足以改变“是否高于基线”的判断。")

# ---------------- 8 ----------------
h1("第 8 页 · 统一口径后的六方向结果")
table(["方向", "ortholog-PCA", "SATURN", "scVI"], [
    ["人→鼠", "0.6435", "0.4147", "0.6683"],
    ["鼠→人", "0.6729", "0.4010", "0.5895"],
    ["人→斑马鱼", "0.1682", "0.2479", "0.4014"],
    ["斑马鱼→人", "0.1585", "0.4021", "0.4290"],
    ["鼠→斑马鱼", "0.2314", "0.6500", "0.4248"],
    ["斑马鱼→鼠", "0.4396", "0.6510", "0.4786"],
], widths=[3.4, 3.6, 3.4, 3.4], aligns=[WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER])
para("读数：scVI 四个方向最高，但鼠→人输给 oPCA、鼠→鱼输给 SATURN——没有全面赢家。", bold=True)
para("限定（口头带过）：SAMap 未画出，三方向 n=0，其余 0.0401–0.1127；分母 oPCA 100%、scVI 98–100%、SATURN 29–87%。")

# ---------------- 9 ----------------
h1("第 9 页 · 场景化选型指南 v0")
table(["场景", "首选", "次选", "不推荐", "证据强度"], [
    ["近缘（人 ↔ 鼠）", "ortholog-PCA", "scVI（很接近）", "SAMap", "中等"],
    ["远缘 · 人 ↔ 鱼", "scVI", "SATURN", "SAMap", "中等"],
    ["远缘 · 鼠 ↔ 鱼", "SATURN", "scVI", "SAMap", "中等"],
    ["跨门（七鳃鳗 ↔ 鼠）", "待跑", "—", "—", "数据已定位"],
    ["无 GPU", "ortholog-PCA", "scVI（8.5 min）", "SATURN", "中等偏强"],
], widths=[4.4, 2.6, 2.8, 2.2, 2.0], aligns=[WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT])
para("三条限定语（必须随表一起出现）：", space_before=4)
bullet("全部为 transductive / in-sample，不是留出评估；")
bullet("四方法分母不同（oPCA 100%、scVI 98–100%、SATURN 29–87%、SAMap 0–91%）；")
bullet("「不推荐」≠「方法差」。")
para("一句话：近缘先试 oPCA；跨得越远越要靠联合训练的潜空间方法，但人↔鱼与鼠↔鱼的首选不同；没有 GPU 时 scVI 只要 8.5 分钟。", space_before=4, bold=True)
para("跨门仍是 insufficient evidence：数据已定位，但尚未跑。")

# ---------------- 速查 ----------------
h1("附一 · 数字速查（回答提问时用）")
table(["项", "值"], [
    ["人→鼠 coarse accuracy", "0.8618（1,297 / 1,505）"],
    ["同源基因（人鼠）", "15,869"],
    ["联合 PCA", "3,063 × 50"],
    ["排除", "30（鼠侧 status ≠ active）"],
    ["coverage", "0.9805"],
    ["majority 准确率", "0.4817"],
    ["majority macro-F1", "0.0813"],
    ["macro-F1 人→斑马鱼 coarse", "truth-only 0.4516 / union 0.4014"],
    ["四方法分母", "oPCA 100%、scVI 98–100%、SATURN 29–87%、SAMap 0–91%"],
], widths=[5.6, 8.2], aligns=[WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT])

# ---------------- 追问 ----------------
h1("附二 · 两个预设追问")
h2("“为什么不直接用 macro-F1 报就好了？”")
para("macro-F1 对少数类敏感，但它依赖标签集合的定义；同一份预测在 truth-only 与 union 下差 0.05。所以指标之外必须同时交代口径与分母。")
h2("“这些数字能复现吗？”")
para("能。主源是 metrics.json + 逐细胞预测文件，脚本与输入的 SHA-256 都记在 manifest 里；本地已用独立实现重算过 accuracy（18/18 一致）与 macro-F1（差异全部可由口径解释）。")

# ---------------- 页脚 ----------------
para("", space_after=10)
note("本文所有数字来自平台产物或本地独立重算，未凭记忆填写。口径：transductive / in-sample，单 seed（0）。")

doc.save(OUT)
print("WROTE", OUT)
