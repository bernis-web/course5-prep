# -*- coding: utf-8 -*-
"""课题5 基准评估报告 v2（2026-10-23）—— 四方法 + 统一 macro-F1 + 跨门负结果。"""
import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

OUT = "D:/projects/course5-prep/deliverables/course5-final-report-v2-20261023.docx"
BLUE = RGBColor(0x00, 0x5B, 0xAC)
INK = RGBColor(0x1F, 0x2D, 0x3D)
MUTED = RGBColor(0x60, 0x75, 0x8F)

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


def run_fmt(r, size=10.5, bold=False, color=INK, font="宋体"):
    r.font.size = Pt(size); r.font.bold = bold; r.font.color.rgb = color; r.font.name = font
    rPr = r._element.get_or_add_rPr()
    rf = rPr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts"); rPr.append(rf)
    rf.set(qn("w:eastAsia"), font); rf.set(qn("w:ascii"), font); rf.set(qn("w:hAnsi"), font)


def P(text="", size=10.5, bold=False, color=INK, font="宋体", align=WD_ALIGN_PARAGRAPH.JUSTIFY,
      before=0, after=4, indent=0):
    p = doc.add_paragraph(); p.alignment = align
    p.paragraph_format.space_before = Pt(before); p.paragraph_format.space_after = Pt(after)
    if indent: p.paragraph_format.first_line_indent = Cm(indent)
    if text:
        r = p.add_run(text); run_fmt(r, size, bold, color, font)
    return p


def H1(t):
    p = P(t, 15, True, BLUE, "微软雅黑", WD_ALIGN_PARAGRAPH.LEFT, 16, 6); p.paragraph_format.keep_with_next = True


def H2(t):
    p = P(t, 12, True, BLUE, "微软雅黑", WD_ALIGN_PARAGRAPH.LEFT, 10, 4); p.paragraph_format.keep_with_next = True


def shade(cell, hexc):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd"); shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), hexc)
    tcPr.append(shd)


def T(headers, rows, widths=None, aligns=None, fs=9.5):
    t = doc.add_table(rows=1, cols=len(headers)); t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER; t.autofit = False
    lay = OxmlElement("w:tblLayout"); lay.set(qn("w:type"), "fixed"); t._tbl.tblPr.append(lay)
    for i, h in enumerate(headers):
        c = t.rows[0].cells[i]; c.text = ""
        p = c.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h); run_fmt(r, 9.5, True, RGBColor(0xFF, 0xFF, 0xFF), "微软雅黑")
        shade(c, "005BAC")
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            p = cells[i].paragraphs[0]
            p.alignment = (aligns[i] if aligns else (WD_ALIGN_PARAGRAPH.LEFT if i == 0 else WD_ALIGN_PARAGRAPH.CENTER))
            r = p.add_run(str(v)); run_fmt(r, fs, False, INK, "宋体")
    if widths:
        for i, w in enumerate(widths):
            t.columns[i].width = Cm(w)
            for row in t.rows: row.cells[i].width = Cm(w)
    P("", size=6, after=2)


# ---------- 标题 ----------
P("跨物种单细胞整合方法评估报告", 22, True, RGBColor(0x12, 0x36, 0x5A), "微软雅黑", WD_ALIGN_PARAGRAPH.LEFT, 0, 2)
P("四方法对照（ortholog-PCA / SATURN / SAMap / scVI）+ 场景化选型", 13, True, MUTED, "微软雅黑", WD_ALIGN_PARAGRAPH.LEFT, 0, 2)
P("课题5 · v2 · 2026-10-23", 9.5, False, MUTED)
P("口径声明：全部结果为 transductive / in-sample 重评估，不支持 held-out 或 inductive 泛化结论。", 9.5, False, MUTED, after=10)

# ---------- 1 摘要 ----------
H1("1 摘要")
P("本报告在同一心脏样本三物种 pilot 数据集（人 1,528 / 鼠 1,535 / 斑马鱼 1,543 细胞）上，"
  "对四种跨物种标签映射方法做统一协议对照：ortholog-PCA（自建零整合基线）、SATURN v99、SAMap v98、scVI。"
  "指标统一为 coarse 标签空间的 macro-F1（并集口径）。")
P("主要结论：", bold=True, after=2)
for t in [
    "近缘（人 ↔ 鼠）：ortholog-PCA（0.6435 / 0.6729）与 scVI（0.6683 / 0.5895）基本打平，oPCA 略优；SATURN 0.40 量级；SAMap 低于多数类基线。",
    "远缘（人 ↔ 鱼）：scVI 0.4014 / 0.4290 最高，SATURN 0.2479 / 0.4021 次之，oPCA 0.1682 / 0.1585 最弱。",
    "远缘（鼠 ↔ 鱼）：SATURN 0.6500 / 0.6510 显著领先，scVI 0.4248 / 0.4786 次之，oPCA 0.2314 / 0.4396 最弱。",
    "跨门（七鳃鳗 ↔ 小鼠）：oPCA 与 scVI 均失败（acc 4.6–5.8%，低于 13 类随机猜测 7.7%，远低于多数类基线 21.7%/30.6%）。",
    "四个方法没有全面赢家：scVI 四方向最高，oPCA 在鼠→人最高，SATURN 在两个鼠↔鱼方向最高。",
]:
    p = doc.add_paragraph(style="List Bullet"); p.paragraph_format.line_spacing = 1.45; p.paragraph_format.space_after = Pt(2)
    r = p.add_run(t); run_fmt(r, 10.5)
P("因此不按单一总分排名，而按场景给出推荐（见第 6 节与《场景化选型指南 v3》）。", bold=True, before=4)

# ---------- 2 数据与方法 ----------
H1("2 数据与方法")
H2("2.1 数据")
P("门内：心脏样本三物种 pilot 子集，人 1,528 / 鼠 1,535 / 斑马鱼 1,543 细胞；注释列 celltype，"
  "经冻结映射表 v1（SHA be985735…583165）转 coarse 9 类空间。")
P("跨门：LBSPA 8CrossSpecies.rds（Seurat，13,172 基因 × 333,627 细胞，8 物种）中的 Lamprey 41,678 与 "
  "Mouse 14,016 细胞；13 类交集，仅 coarse 层。")
H2("2.2 四种方法")
T(["方法", "表示层", "是否训练", "备注"], [
    ["ortholog-PCA", "同源基因交集 + PCA-50（每方向独立）", "否", "自建零整合基线"],
    ["SATURN v99", "ESM2 蛋白嵌入 + macrogenes", "是（GPU）", "第三方工具"],
    ["SAMap v98", "同源图对齐", "是", "第三方工具"],
    ["scVI", "联合训练潜空间（n_latent=10, batch_key=species）", "是（CPU 可跑）", "LBSPA 同款"],
], [2.6, 6.2, 2.6, 2.8], [WD_ALIGN_PARAGRAPH.LEFT]*4)
H2("2.3 评估协议")
P("KNN15、cosine、倒距离加权；200 次置换（RandomState(0)）；单 seed（0）。"
  "scVI 与 SATURN 为一次训练多方向评估（transductive），ortholog-PCA 为每方向独立 PCA。")

# ---------- 3 指标口径 ----------
H1("3 指标口径（关键）")
P("macro-F1 有两种算法，差别只在“预测里出现、真实标签里不存在的类”算不算进平均：", after=2)
T(["口径", "定义", "使用者"], [
    ["truth-only", "sorted(set(y_true))", "平台 scVI 脚本（metrics.json 原值）"],
    ["union", "sorted(set(y_true) | set(y_pred))", "本报告跨方法对比统一使用"],
], [3.0, 6.2, 6.0], [WD_ALIGN_PARAGRAPH.LEFT]*3)
P("同一格人→斑马鱼 coarse：truth-only 0.4516，union 0.4014，差 0.05。"
  "跨方法对比一律用 union；引用 metrics.json 原值时必须标注口径。", bold=True)
P("分母：oPCA 与 scVI 约 100%，SATURN 29–87%，SAMap 0–91%。分母不同，macro-F1 不能当绝对排名。")

# ---------- 4 门内结果 ----------
H1("4 门内四方法结果（coarse macro-F1，union）")
T(["方向", "ortholog-PCA", "SATURN v99", "SAMap", "scVI"], [
    ["人 → 鼠", "0.6435", "0.4147", "0.1127", "0.6683"],
    ["鼠 → 人", "0.6729", "0.4010", "0.0401", "0.5895"],
    ["人 → 斑马鱼", "0.1682", "0.2479", "0.0477", "0.4014"],
    ["斑马鱼 → 人", "0.1585", "0.4021", "n/a", "0.4290"],
    ["鼠 → 斑马鱼", "0.2314", "0.6500", "n/a", "0.4248"],
    ["斑马鱼 → 鼠", "0.4396", "0.6510", "n/a", "0.4786"],
], [3.4, 3.2, 3.0, 2.6, 2.6], [WD_ALIGN_PARAGRAPH.LEFT] + [WD_ALIGN_PARAGRAPH.CENTER]*4, 10)
P("注：SAMap 三个方向 n=0（无细胞通过映射），其余方向 0.0401–0.1127。", 9, False, MUTED)

# ---------- 5 批次混合 ----------
H1("5 批次混合与结构保持（scVI latent）")
T(["指标", "值", "含义"], [
    ["silhouette（细胞类型，cosine）", "0.181", "结构存在但不清晰"],
    ["iLISI（物种，k=30）", "1.125", "理论 1–3，接近 1 = 邻居几乎全同物种"],
    ["kBET 接受率（α=0.05）", "0.0039", "几乎全部邻域被拒绝"],
], [5.6, 2.6, 7.0], [WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT])
P("三项一致指向：scVI latent 中三物种几乎未混合。但同一 latent 上跨物种迁移 macro-F1 达 0.67，"
  "合理解释是潜空间把「细胞类型」与「物种」编码在近似正交方向。两组证据必须并列报告。")
P("仅 scVI 有这三项指标；其余三方法当时未保存嵌入，补齐需重跑。", 9, False, MUTED)

# ---------- 6 跨门 ----------
H1("6 跨门场景（七鳃鳗 ↔ 小鼠）")
T(["方法", "七鳃鳗 → 鼠（acc / macro-F1）", "鼠 → 七鳃鳗（acc / macro-F1）"], [
    ["ortholog-PCA", "0.0575 / 0.0711", "0.0516 / 0.0732"],
    ["scVI", "0.0582 / 0.0652", "0.0457 / 0.0802"],
    ["多数类基线", "0.2168", "0.3059"],
], [3.4, 6.2, 6.2], [WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER], 10)
P("13 类空间随机猜测约 7.7%，两方法实测 4.6–5.8%，低于随机；离多数类基线差 4–6 倍。")
P("scVI 在门内的远缘优势没有延伸到跨门：门内人→鱼 scVI 0.4014 vs oPCA 0.1682（2.4 倍），"
  "跨门两者都在 0.065–0.080 量级。")
P("限定：小鼠侧 62.2% 细胞被排除；基因轴为两物种共同检测集（6,222 个，Lamprey 非零仅 56.7%）；"
  "仅 coarse 层；单 seed。论断范围限于“当前数据/注释/规模下不成立”。", 9.5, False, MUTED)

# ---------- 7 选型 ----------
H1("7 场景化选型建议")
T(["场景", "首选", "次选", "不推荐", "证据强度"], [
    ["近缘（人 ↔ 鼠）", "ortholog-PCA", "scVI（很接近）", "SAMap", "中等"],
    ["远缘 · 人 ↔ 鱼", "scVI", "SATURN", "SAMap", "中等"],
    ["远缘 · 鼠 ↔ 鱼", "SATURN", "scVI", "SAMap", "中等"],
    ["跨门（七鳃鳗 ↔ 鼠）", "不建议（两法均失败）", "—", "—", "中等（双臂实测）"],
    ["无 GPU", "ortholog-PCA", "scVI（8.5 min）", "SATURN", "中等偏强"],
], [4.0, 3.6, 3.0, 2.2, 2.2], [WD_ALIGN_PARAGRAPH.LEFT]*5, 9.5)
P("详见《场景化选型指南 v3》（deliverables/场景化选型指南-v3-20261022.md）。")

# ---------- 8 局限 ----------
H1("8 局限")
for t in [
    "全部为 transductive / in-sample；不做留出或 inductive 判断。",
    "单 seed（0），无置信区间；置换检验只回答“是否优于随机”，不回答“是否优于多数类”。",
    "数据规模为 HEART 原文的小子集（1,500 细胞/物种），不能外推到 16 物种规模。",
    "四种方法的特征空间按各自方法学约束定义，非同一数量，不做横向比较；可比性限于输出层面。",
    "跨门结果受注释裁剪影响大（小鼠 62.2% 细胞被排除），且只有 coarse 层。",
    "kBET / iLISI / silhouette 仅有 scVI 值，缺其余三方法。",
]:
    p = doc.add_paragraph(style="List Bullet"); p.paragraph_format.line_spacing = 1.45; p.paragraph_format.space_after = Pt(2)
    r = p.add_run(t); run_fmt(r, 10.5)

# ---------- 9 复现 ----------
H1("9 复现与产物")
T(["内容", "位置"], [
    ["门内四方法结果", "docs/reports/unified-coarse-macro-f1-20261017.md"],
    ["scVI 门内结果与核对", "docs/reports/scvi-cross-species-result-20261019.md"],
    ["批次指标与跨门", "docs/reports/batch-mixing-and-crossphylum-feasibility-20261019.md"],
    ["跨门产物", "results/phase-20261022/crossphylum/"],
    ["选型指南", "deliverables/场景化选型指南-v3-20261022.md"],
    ["总交接文档", "docs/execution/20261019-handoff-full.md"],
], [4.4, 12.0], [WD_ALIGN_PARAGRAPH.LEFT]*2, 9.5)

P("", after=8)
P("本报告全部数字来自平台产物或本地独立重算，未凭记忆填写。", 9, False, MUTED)

doc.save(OUT)
print("WROTE", OUT)
