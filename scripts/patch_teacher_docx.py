# -*- coding: utf-8 -*-
"""老师七条意见回应稿（2026-10-30 提交版）修订注入。

原则：不改历史正文（那是已交付给老师的版本），只在头部加修订说明、文末加附录 A 对照表，
让每一个作废值都有「旧 → 现」的去处。依据全部落在 number-index-20261111.md 与
results/pairwise-20261111/pairwise_corrected.json。
"""
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

P = r"D:\projects\course5-prep\deliverables\课题5-老师七条意见回应-20261030.docx"
d = Document(P)

BANNER = [
    ("修订说明（2026-11-11）", True, 12, RGBColor(0x92, 0x68, 0x12)),
    ("本稿是 2026-10-30 提交给老师的版本，正文按当时口径原样保留，不回改。", False, 10.5, None),
    ("2026-11-08 到 11-11 的复核推翻了其中若干数值：SATURN 的偏高不是口径选择，是我们评测实现把物种词表查反了"
     "（真值应按目标物种、预测按源物种）；旧配对 Δ 用了错误分母；oPCA 四个鱼向用的是 v1 映射旧值。", False, 10.5, None),
    ("文中被推翻的 11 项数值，逐一列在文末「附录 A：旧值 → 现行值对照」。现行权威值以 "
     "docs/reports/number-index-20261111.md 为准，不再引用本稿正文里的旧数。", False, 10.5, None),
]

APPENDIX_TITLE = "附录 A：旧值 → 现行值对照（2026-11-11 补）"
ROWS = [
    ("本稿出现处", "旧值", "现行值 / 判定", "依据"),
    ("§2 配对检验 Δ（鼠→斑马鱼）", "−0.1713 CI[−0.2273,−0.1185]", "−0.0172 CI[−0.0580,+0.0230]，不显著", "results/pairwise-20261111/pairwise_corrected.json"),
    ("§2 配对检验 Δ（斑马鱼→鼠）", "−0.0709 CI[−0.1800,−0.0334]", "−0.1825 CI[−0.2147,−0.1518]，显著", "同上"),
    ("§2 Δ（人→斑马鱼，现口径）", "−0.2633（无 CI）", "−0.2732 CI[−0.3003,−0.2390]", "同上"),
    ("§2 Δ（斑马鱼→人，现口径）", "−0.2005（无 CI）", "−0.2904 CI[−0.3153,−0.2642]", "同上"),
    ("表 2 SATURN 错口径（鼠→斑马鱼 / 斑马鱼→鼠）", "0.6500 / 0.6510", "0.4076 / 0.2961（v2 映射，macro-F1）", "saturn_convention_mapv2.json"),
    ("表 2 SATURN 公平口径", "0.4560 / 0.4588", "该口径随查表 bug 一并作废，不再引用", "audit-saturn-payload-gate-20261111.md"),
    ("表 2 SATURN 虚高量", "+0.0428 / +0.1882 / +0.1940", "真实抬高 +0.0625–0.3549（最大：斑马鱼→鼠 +0.3549）", "audit-stats-20261111.md"),
    ("表 2 / 表 10 SATURN accuracy", "0.4147 / 0.4010 / 0.2479 / 0.4021", "0.5887 / 0.2271 / 0.1811 / 0.2147 / 0.3036 / 0.4565（accuracy，非 macro-F1）", "results/mapping-v2-20261111"),
    ("表 2 / 表 8 oPCA 鱼向", "0.1654 / 0.1512 / 0.2177 / 0.4405", "0.1506 / 0.2131 / 0.2816 / 0.4186（rerun-v2）", "results/mapping-v2-20261111/rerun-v2"),
    ("表 10 分母（459 / 1309）", "459 / 1309", "1469 / 1528（鱼向 1469＝1543−74）", "saturn_convention_mapv2.json"),
    ("§3 规模差", "300 倍", "约 104 倍（全量/子集每物种）；子集 4,606 vs 全量 140,471＝30.50×", "audit-scale-20261111.md"),
    ("§3 Orthers 865", "865（预测侧判成 Orthers）", "口径说明保留：本体仅 30 细胞，865 是预测侧计数，不是本体规模", "audit-stats-20261111.md"),
    ("§5 追加更正段六值", "0.1269 / 0.1640 / 0.3658 / 0.3563", "0.1282 / 0.1386 / 0.4076 / 0.2961（v2 映射终版）", "number-index-20261111.md"),
]


def p_with_runs(doc, anchor, items, bold_first=False):
    p = doc.add_paragraph()
    for i, (text, bold, size, color) in enumerate(items):
        r = p.add_run(text)
        r.bold = bold
        r.font.size = Pt(size)
        if color is not None:
            r.font.color.rgb = color
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(4)
    anchor._p.addprevious(p._p)
    return p


first = d.paragraphs[0]
for i, (text, bold, size, color) in enumerate(BANNER):
    p_with_runs(d, first, [(text, bold, size, color)])

# 文末附录
d.add_paragraph()
h = d.add_paragraph()
r = h.add_run(APPENDIX_TITLE)
r.bold = True
r.font.size = Pt(13)
r.font.color.rgb = RGBColor(0x15, 0x39, 0x57)

tb = d.add_table(rows=len(ROWS), cols=4)
tb.style = "Table Grid"
w = [2.1, 2.3, 3.4, 3.2]
for ri, row in enumerate(ROWS):
    for ci, val in enumerate(row):
        cell = tb.cell(ri, ci)
        cell.text = ""
        par = cell.paragraphs[0]
        run = par.add_run(val)
        run.font.size = Pt(9)
        run.bold = (ri == 0)

tail = d.add_paragraph()
tr = tail.add_run("本附录由 scripts/patch_teacher_docx.py 生成，依据文件均在仓库内，可逐条复核。")
tr.font.size = Pt(9)
tr.italic = True
tr.font.color.rgb = RGBColor(0x5E, 0x71, 0x82)

d.save(P)
print("saved", P)
print("段落数", len(d.paragraphs), "表格数", len(d.tables))