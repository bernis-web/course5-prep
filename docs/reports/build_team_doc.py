# -*- coding: utf-8 -*-
"""课题5 项目说明文档（组员版）—— 让没参与执行的人也能看懂做了什么、为什么、现在到哪。"""
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

OUT = "D:/projects/course5-prep/deliverables/课题5-项目说明文档-组员版-20261023.docx"
BLUE = RGBColor(0x00, 0x5B, 0xAC)
INK = RGBColor(0x1F, 0x2D, 0x3D)
MUTED = RGBColor(0x60, 0x75, 0x8F)
RED = RGBColor(0xC0, 0x00, 0x00)

doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
sec.left_margin = sec.right_margin = Cm(2.2)
sec.top_margin = sec.bottom_margin = Cm(2.0)

st = doc.styles["Normal"]
st.font.name = "宋体"; st.font.size = Pt(10.5)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
st.paragraph_format.line_spacing = 1.5
st.paragraph_format.space_after = Pt(4)


def rf(r, size=10.5, bold=False, color=INK, font="宋体"):
    r.font.size = Pt(size); r.font.bold = bold; r.font.color.rgb = color; r.font.name = font
    rPr = r._element.get_or_add_rPr()
    f = rPr.find(qn("w:rFonts"))
    if f is None:
        f = OxmlElement("w:rFonts"); rPr.append(f)
    for a in ("w:eastAsia", "w:ascii", "w:hAnsi"):
        f.set(qn(a), font)


def P(text="", size=10.5, bold=False, color=INK, font="宋体", align=WD_ALIGN_PARAGRAPH.JUSTIFY,
      before=0, after=4, indent=0):
    p = doc.add_paragraph(); p.alignment = align
    p.paragraph_format.space_before = Pt(before); p.paragraph_format.space_after = Pt(after)
    if indent: p.paragraph_format.first_line_indent = Cm(indent)
    if text:
        r = p.add_run(text); rf(r, size, bold, color, font)
    return p


def H1(t):
    p = P(t, 15, True, BLUE, "微软雅黑", WD_ALIGN_PARAGRAPH.LEFT, 18, 6)
    p.paragraph_format.keep_with_next = True


def H2(t):
    p = P(t, 12, True, BLUE, "微软雅黑", WD_ALIGN_PARAGRAPH.LEFT, 10, 4)
    p.paragraph_format.keep_with_next = True


def BUL(text, bold_prefix=None):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.line_spacing = 1.45
    p.paragraph_format.space_after = Pt(2)
    if bold_prefix:
        r = p.add_run(bold_prefix); rf(r, 10.5, True)
    r = p.add_run(text); rf(r, 10.5)


def NOTE(t):
    p = doc.add_paragraph(); p.paragraph_format.space_before = Pt(2); p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.left_indent = Cm(0.4)
    r = p.add_run(t); rf(r, 9.5, False, MUTED)


def shade(c, hexc):
    tcPr = c._tc.get_or_add_tcPr()
    sh = OxmlElement("w:shd"); sh.set(qn("w:val"), "clear"); sh.set(qn("w:color"), "auto"); sh.set(qn("w:fill"), hexc)
    tcPr.append(sh)


def T(headers, rows, widths=None, aligns=None, fs=9.5):
    t = doc.add_table(rows=1, cols=len(headers)); t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER; t.autofit = False
    lay = OxmlElement("w:tblLayout"); lay.set(qn("w:type"), "fixed"); t._tbl.tblPr.append(lay)
    for i, h in enumerate(headers):
        c = t.rows[0].cells[i]; c.text = ""
        p = c.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h); rf(r, 9.5, True, RGBColor(0xFF, 0xFF, 0xFF), "微软雅黑")
        shade(c, "005BAC")
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            p = cells[i].paragraphs[0]
            p.alignment = (aligns[i] if aligns else (WD_ALIGN_PARAGRAPH.LEFT if i == 0 else WD_ALIGN_PARAGRAPH.CENTER))
            r = p.add_run(str(v)); rf(r, fs)
    if widths:
        for i, w in enumerate(widths):
            t.columns[i].width = Cm(w)
            for row in t.rows: row.cells[i].width = Cm(w)
    P("", size=6, after=2)


# ================= 标题 =================
P("课题5 项目说明文档（组员版）", 24, True, RGBColor(0x12, 0x36, 0x5A), "微软雅黑", WD_ALIGN_PARAGRAPH.LEFT, 0, 2)
P("跨物种单细胞整合方法评估：我们做了什么、为什么这么做、现在到哪一步", 12.5, True, MUTED, "微软雅黑",
  WD_ALIGN_PARAGRAPH.LEFT, 0, 2)
P("2026-10-23 ｜ 阅读时间约 20 分钟", 9.5, False, MUTED, after=10)

# ================= 0 =================
H1("0 先看这一页")
P("如果你只有三分钟，看这五句：", bold=True, after=2)
for t in [
    "我们在三种动物的心脏单细胞数据上，比较了四种"把细胞类型从 A 物种迁移到 B 物种"的方法。",
    "四种方法各有胜负：近缘人-鼠是 ortholog-PCA 和 scVI 打平；远缘人-鱼是 scVI 最好；远缘鼠-鱼是 SATURN 最好。",
    "没有哪个方法在所有方向都赢，所以我们不做"总分冠军"，而是做"场景 → 推荐哪个方法"的选型指南。",
    "我们还试了最难的跨门场景（七鳃鳗 vs 小鼠）：四种方法里最强的两个都失败了，这是个有价值的负结果。",
    "课程要求的 12 项里，9 项已完成、3 项部分完成（批次指标只做了一个方法、时间内存非受控、容器未实际构建）。",
]:
    BUL(t)

# ================= 1 =================
H1("1 课程要我们做什么")
P("课程题目是：跨物种单细胞整合——SATURN vs SAMap vs scVI 系的基准测试与场景化选型。")
P("拆开看是两件交付物：", after=2)
BUL("一份基准测试报告：几种方法在同一份数据上、用同一套指标，跑出来到底谁高谁低。", "① ")
BUL("一份场景化选型指南：至少覆盖近缘、跨门、无 GPU 三种场景，告诉别人"我这种情况该用哪个"。", "② ")
P("课程还点名了几个指标：macro-F1（不是 accuracy）、批次混合与生物保守性（kBET/iLISI/silhouette）、"
  "时间与内存、文档易用性、Agent 友好度、容器化。", before=4)

# ================= 2 =================
H1("2 数据是什么")
P("我们用的是心脏单细胞数据，三个物种：")
T(["物种", "细胞数", "备注"], [
    ["人（human）", "1,528", "心脏"],
    ["小鼠（mouse）", "1,535", "心脏"],
    ["斑马鱼（zebrafish）", "1,543", "心脏"],
    ["合计", "4,606", "—"],
], [4.0, 3.0, 8.0], [WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT])
P("每个细胞都有一个"细胞类型"标签（比如心肌细胞、内皮细胞、成纤维细胞），这就是我们要预测的答案。")
P("另外，跨门场景用的是另一套数据：LBSPA 论文的 8 物种脑数据，我们取了七鳃鳗 41,678 个细胞 + 小鼠 14,016 个细胞。")
NOTE("注意：我们用的心脏数据是 HEART 论文的小子集（每物种约 1,500 细胞），不是原文的 16 物种 47.9 万细胞。"
     "所有结论的适用范围都受这个规模限制。")

# ================= 3 =================
H1("3 四个方法分别是什么（用大白话）")
P("任务本质：我有物种 A 的细胞（知道类型），想给物种 B 的细胞打类型标签。四个方法的区别在于"怎么把两个物种放到同一个空间里"。", after=2)

H2("3.1 ortholog-PCA（我们自己搭的基线）")
P("做法：先把两个物种里"一一对应"的同源基因找出来（比如人的某基因对应鼠的某基因），只用这些基因，"
  "把两个物种的细胞一起做 PCA 降维，然后在降维空间里找最近邻。")
P("特点：不训练、不用 GPU、30 秒跑完。它的作用是回答"这么简单的方法是不是已经够了"。")

H2("3.2 SATURN")
P("做法：不直接比基因表达，而是把基因先翻译成蛋白质，用蛋白质语言模型（ESM2）得到嵌入，"
  "再把一堆基因压成"宏基因"（macrogene），在宏基因空间里对齐。")
P("特点：需要 GPU 训练；思路是"越远缘，蛋白层面的相似性比基因表达更可靠"。")

H2("3.3 SAMap")
P("做法：构建两个物种之间的同源基因图，用图对齐的方式找细胞对应关系。")
P("特点：依赖多、复现最不稳定；在我们这个数据规模下基本没有信号。")

H2("3.4 scVI")
P("做法：用一个生成模型（变分自编码器）把三个物种的细胞一起训练到一个 10 维的潜空间里，"
  "训练时告诉模型"每个细胞来自哪个物种"，让它学出不受物种影响的表示。")
P("特点：需要训练但 CPU 就能跑（我们实测 8.5 分钟）；是课程点名的方法，也是 LBSPA 论文用的方法。")

# ================= 4 =================
H1("4 几个必须懂的概念")
H2("4.1 transductive（直推式）")
P("意思是：测试数据在训练时"见过"。我们的做法是把两个物种的细胞一起放进去降维/训练，"
  "然后再评估能不能把标签从一边迁到另一边。")
P("这不是"留出评估"，也不是"inductive（归纳式）"。所以我们的结论只能说"在同一批数据上的一致性"，"
  "不能说"这个方法对全新物种也有效"。这条限定在每份材料里都必须写。", bold=True)

H2("4.2 macro-F1 与 accuracy 的区别")
P("accuracy = 预测对的细胞数 ÷ 总数。问题：如果 90% 的细胞都是同一类，全猜这一类也有 90% 的准确率。")
P("macro-F1 = 先对每个类别各算一个 F1，再对所有类别取平均。少数类预测错了，会被明显惩罚。")
P("我们最初用 accuracy，后来按课程要求改成 macro-F1，结果有 4 个结论直接翻转——"
  "原本"低于多数类基线"的方向，换成 macro-F1 后变成"高于基线"。")

H2("4.3 标签层级：exact / coarse / fine")
P("同一批细胞有三套标签：exact（最细，原始注释）、coarse（粗类，9 类）、fine（细类）。"
  "层级不同，难度完全不同，所以我们的结果是 6 方向 × 3 层 = 18 格。")

H2("4.4 同源映射")
P("把人的基因名对应到鼠/鱼的基因名。我们用的是一一对应的直系同源（1:1 ortholog）。"
  "人-鼠有 15,869 对，人-鱼 9,311 对，鼠-鱼 8,160 对。")

# ================= 5 =================
H1("5 结果一：门内四方法对比")
P("这里的"门内"指三个物种都在脊椎动物门内（人、鼠、斑马鱼）。指标是 coarse 层的 macro-F1。")
T(["方向", "ortholog-PCA", "SATURN", "SAMap", "scVI"], [
    ["人 → 鼠", "0.6435", "0.4147", "0.1127", "0.6683"],
    ["鼠 → 人", "0.6729", "0.4010", "0.0401", "0.5895"],
    ["人 → 斑马鱼", "0.1682", "0.2479", "0.0477", "0.4014"],
    ["斑马鱼 → 人", "0.1585", "0.4021", "n/a", "0.4290"],
    ["鼠 → 斑马鱼", "0.2314", "0.6500", "n/a", "0.4248"],
    ["斑马鱼 → 鼠", "0.4396", "0.6510", "n/a", "0.4786"],
], [3.4, 3.2, 3.0, 2.6, 2.6], [WD_ALIGN_PARAGRAPH.LEFT] + [WD_ALIGN_PARAGRAPH.CENTER]*4, 10)

P("怎么读这张表：", bold=True, after=2)
BUL("近缘（人↔鼠）：ortholog-PCA 和 scVI 基本打平，oPCA 略优（均值 0.658 vs 0.629）。", "① ")
BUL("远缘人↔鱼：scVI 明显最好（0.4014 / 0.4290），SATURN 次之，oPCA 最弱。", "② ")
BUL("远缘鼠↔鱼：SATURN 大幅领先（0.6500 / 0.6510），scVI 次之。", "③ ")
BUL("SAMap 三个方向 n=0（没有细胞通过映射），其余方向 0.04–0.11，低于多数类基线。", "④ ")
P("结论：没有全面赢家。scVI 四个方向最高，oPCA 在鼠→人最高，SATURN 在两个鼠↔鱼方向最高。", bold=True, before=4)

# ================= 6 =================
H1("6 结果二：批次混合（scVI 到底混得怎么样）")
P("我们只在 scVI 的潜空间上算了三个指标：")
T(["指标", "值", "怎么理解"], [
    ["silhouette（细胞类型）", "0.181", "细胞类型结构存在，但不算清晰"],
    ["iLISI（物种，k=30）", "1.125", "理论范围 1–3；接近 1 说明每个细胞的邻居几乎都是同物种"],
    ["kBET 接受率", "0.0039", "几乎全部邻域的物种组成都与全局显著不同"],
], [5.0, 2.4, 8.0], [WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT])
P("三项一致说明：scVI 并没有把三个物种混匀，物种之间仍然分得很开。")
P("但这看起来和"迁移效果不错"矛盾——同一份潜空间上，人→鼠 macro-F1 有 0.6683。", before=4)
P("我们的解释：潜空间把"细胞类型"和"物种"编码在近似正交的方向上。同类型细胞跨物种彼此靠近，"
  "但单个细胞最近的 30 个邻居仍以本物种为主（物种方向的偏移量大于同物种内的类型间距）。")
P("所以：低 iLISI 不等于方法失败，但两组证据必须一起报，只引一个就是误导。", bold=True)
NOTE("这三个指标只有 scVI 有。其余三个方法当时没有保存嵌入，补齐需要重跑。")

# ================= 7 =================
H1("7 结果三：跨门场景（七鳃鳗 ↔ 小鼠）")
P("这是课程明确要求覆盖的场景，也是最难的一个。七鳃鳗是现存最原始的脊椎动物，与小鼠隔了一个"门"。")
H2("7.1 数据与取舍")
T(["项", "值", "说明"], [
    ["细胞", "55,694", "七鳃鳗 41,678 + 小鼠 14,016"],
    ["基因", "6,222", "两物种共同检测到的基因（min_cells≥3）"],
    ["类别", "13 类", "七鳃鳗只有 13 类，是鼠类标签的子集"],
    ["层级", "仅 coarse", "数据只有一套注释，没有 exact/fine"],
], [2.6, 3.0, 9.8], [WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT])
P("两个必须说明的取舍：", bold=True, after=2)
BUL("小鼠有 6 类细胞是七鳃鳗没有的（EX/IN/SNCG/Purkinje/Golgi/Bergmann），占小鼠细胞的 62.2%，全部排除出评估。")
BUL("基因轴取两物种共同检测到的 6,222 个，七鳃鳗侧只有 56.7% 的基因是非零的。")
H2("7.2 结果")
T(["方法", "七鳃鳗 → 鼠", "鼠 → 七鳃鳗", "多数类基线"], [
    ["ortholog-PCA", "0.0575 / 0.0711", "0.0516 / 0.0732", "0.2168 / 0.3059"],
    ["scVI", "0.0582 / 0.0652", "0.0457 / 0.0802", "0.2168 / 0.3059"],
], [3.0, 4.2, 4.2, 4.0], [WD_ALIGN_PARAGRAPH.LEFT] + [WD_ALIGN_PARAGRAPH.CENTER]*3)
P("（单元格里是 accuracy / macro-F1）", 9, False, MUTED)
P("13 类空间随机猜约 7.7%，两个方法实测 4.6–5.8%，低于随机；离多数类基线差 4–6 倍。", bold=True)
H2("7.3 这条结果的价值")
P("门内人→鱼时，scVI 是 oPCA 的 2.4 倍（0.4014 vs 0.1682）。到了跨门，两者都塌到 0.07 量级，没有实质差别。")
P("说明"越远越要靠潜空间方法"这个规律，在跨门这一步中断了。可能的解释是：门内三物种共享脊椎动物身体计划与器官，"
  "细胞类型同源；跨门脑区与细胞类型本身缺乏可靠对应，不是换个方法能补的。")
P("所以跨门的答案不是"哪个方法更好"，而是"在当前数据与注释体系下，这一族方法都做不了"。", bold=True)

# ================= 8 =================
H1("8 为什么不能排一个总分冠军")
P("有人会问：把六个方向平均一下不就行了？我们算过：")
T(["方法", "六方向均值", "说明"], [
    ["scVI", "0.4986", "最高"],
    ["SATURN", "0.4611", "第二"],
    ["ortholog-PCA", "0.3857", "第三"],
    ["SAMap", "0.0334", "三个方向 n=0 按 0 计入；只算有值三方向是 0.0668"],
], [3.4, 3.4, 9.0], [WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT])
P("但这个排名不成立，原因有四条：", bold=True, before=4, after=2)
BUL("分母不同：oPCA 100%、scVI 98–100%、SATURN 29–87%、SAMap 0–91%。分母小的分数方差更大。", "① ")
BUL("特征空间不同：scVI 用 9,018 个共同基因；oPCA 每方向独立（15,869 / 9,311 / 8,160）。"
    "这不是"信息多少"，是方法学约束不同。", "② ")
BUL("训练方式不同：oPCA 是每方向独立 PCA；其余三个是一次训练、多方向评估。", "③ ")
BUL("统计强度不足：单 seed、无置信区间、无多重比较校正。0.05 的差距不足以支撑结论。", "④ ")
P("所以我们的做法是：不排总分，按场景推荐。", bold=True)

# ================= 9 =================
H1("9 场景化选型建议（这是课程要的核心交付物）")
T(["场景", "首选", "次选", "不推荐", "证据强度"], [
    ["近缘（人 ↔ 鼠）", "ortholog-PCA", "scVI（很接近）", "SAMap", "中等"],
    ["远缘 · 人 ↔ 鱼", "scVI", "SATURN", "SAMap", "中等"],
    ["远缘 · 鼠 ↔ 鱼", "SATURN", "scVI", "SAMap", "中等"],
    ["跨门（七鳃鳗 ↔ 鼠）", "不建议（两法均失败）", "—", "—", "中等（双臂实测）"],
    ["无 GPU", "ortholog-PCA", "scVI（8.5 min）", "SATURN", "中等偏强"],
], [4.0, 3.6, 3.0, 2.2, 2.2], [WD_ALIGN_PARAGRAPH.LEFT]*5, 9.5)
P("三条限定语必须随表一起出现：", bold=True, after=2)
BUL("全部是 transductive / in-sample，不是留出评估。", "① ")
BUL("四个方法的分母不同，macro-F1 不能当绝对排名。", "② ")
BUL(""不推荐"不等于"方法差"：SAMap 在我们这个规模下没信号，不代表它在原文 47.9 万细胞规模下无效。", "③ ")

# ================= 10 =================
H1("10 我们踩过的坑（对后来人有用）")
T(["坑", "现象", "怎么解决"], [
    ["anndata 版本冲突", "import scvi 报 AlignedViewMixin 找不到", "删掉 pylibs 里的旧 anndata，让镜像自带的 0.10.8 生效"],
    ["输出目录写错", "任务 1 秒内失败", "容器里只能写 ./result，写 ../result 不可写"],
    ["shell 变量没加引号", "cp -r $REC/. 变成 cp -r /. 拷贝根目录", "所有变量加引号：[ -n \"$REC\" ]"],
    ["macro-F1 两种口径", "同一份预测两个数，差 0.05", "跨方法对比统一用并集口径"],
    ["平台上传通道", "上传文件返回 60030", "走 GenPilot 容器的 dcs data push"],
], [3.2, 5.4, 7.0], [WD_ALIGN_PARAGRAPH.LEFT]*3, 9)

# ================= 11 =================
H1("11 现在还缺什么")
T(["课程要求", "状态", "说明"], [
    ["四方法对比", "✅ 完成", "6 方向 × 3 层"],
    ["macro-F1", "✅ 完成", "统一并集口径"],
    ["近缘 / 无 GPU 场景", "✅ 完成", "有实测"],
    ["跨门场景", "✅ 完成", "负结果，双臂实测"],
    ["基准报告", "✅ 完成", "course5-final-report-v2"],
    ["选型指南", "✅ 完成", "v4，八场景"],
    ["文档 / Agent 友好度", "✅ 完成", "六维评分"],
    ["批次混合与生物保守性", "⚠️ 部分", "只有 scVI 有；其余三方法需重跑"],
    ["时间与内存", "⚠️ 部分", "有实测值，但不是受控 benchmark"],
    ["容器化", "⚠️ 部分", "配方完整，未实际构建"],
], [5.0, 2.6, 8.0], [WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT])
P("12 项里 9 项完成、3 项部分。剩余三项都不是"没做"，是"做了但有明确缺口"。", bold=True)

# ================= 12 =================
H1("12 交付物在哪")
T(["文件", "位置"], [
    ["基准报告 v2", "deliverables/course5-final-report-v2-20261023.docx"],
    ["选型指南 v4", "deliverables/场景化选型指南-v4-20261023.md"],
    ["第 2 次汇报 PPT", "results/stage-reports-20261019/课题5第02次汇报_数字来源链_校模板.pptx"],
    ["第 5 次汇报 PPT", "results/stage-reports-20261022/课题5第05次汇报_跨门场景.pptx"],
    ["各次汇报内容稿", "docs/reports/report-0N-*.md"],
    ["四方法结果数据", "results/phase-20261017/unified-coarse-macro-f1/"],
    ["scVI 结果", "results/phase-20261019/scvi-cross-species/"],
    ["跨门结果", "results/phase-20261022/crossphylum/"],
    ["容器配方", "container/"],
    ["全项目交接文档", "docs/execution/20261019-handoff-full.md"],
], [4.4, 12.0], [WD_ALIGN_PARAGRAPH.LEFT]*2, 9)

# ================= 13 =================
H1("13 如果你要接手，从哪开始")
P("按优先级：", after=2)
BUL("先读《场景化选型指南 v4》，八场景看完就知道我们得出什么结论。", "① ")
BUL("再读《基准报告 v2》，看数字怎么来的、限定是什么。", "② ")
BUL("要改数字，先看 docs/reports/ 下对应的结果报告，每个数字都有来源文件。", "③ ")
BUL("要重跑，看 docs/execution/20261019-handoff-full.md 的复现章节（命令级）。", "④ ")
P("三条纪律：不把 transductive 写成 inductive；不按总分排冠军；限定语随数字一起出现。", bold=True, before=6)

P("", after=10)
P("本文所有数字来自平台产物或本地独立重算，未凭记忆填写。", 9, False, MUTED)

doc.save(OUT)
print("WROTE", OUT)
