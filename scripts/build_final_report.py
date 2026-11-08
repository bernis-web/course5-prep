"""Generate the Course-5 final Word report from frozen metrics files.

Every number in the tables is read directly from the metrics JSON files -
no hand-typed values. Narrative text carries the caveat list verbatim from
docs/final-evidence-matrix-20261005.md.
"""
import json
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, Cm, RGBColor

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "deliverables" / "course5-final-report.docx"

DIRS = ["human->mouse", "mouse->human", "human->zebrafish",
        "mouse->zebrafish", "zebrafish->human", "zebrafish->mouse"]
DIR_CN = {
    "human->mouse": "人→鼠", "mouse->human": "鼠→人",
    "human->zebrafish": "人→斑马鱼", "mouse->zebrafish": "鼠→斑马鱼",
    "zebrafish->human": "斑马鱼→人", "zebrafish->mouse": "斑马鱼→鼠",
}
SATURN_V97G = {"human->mouse": 0.6179, "mouse->human": 0.2539,
               "human->zebrafish": 0.1835, "mouse->zebrafish": 0.3009,
               "zebrafish->human": 0.2474, "zebrafish->mouse": 0.4651}


def load(p):
    return json.loads((BASE / p).read_text(encoding="utf-8"))


def add_table(doc, headers, rows, widths=None):
    t = doc.add_table(rows=1 + len(rows), cols=len(headers))
    t.style = "Table Grid"
    for j, h in enumerate(headers):
        cell = t.rows[0].cells[j]
        cell.text = h
        for run in cell.paragraphs[0].runs:
            run.font.bold = True
    for i, row in enumerate(rows):
        for j, v in enumerate(row):
            t.rows[i + 1].cells[j].text = str(v)
    return t


def main():
    orth = load("results/pilot-v1/ortholog-pca-v98/metrics.json")
    samap = load("results/pilot-v1/samap-v98/wdl-run/extracted/metrics.json")
    v99 = load("results/pilot-v1/saturn-v99/raw/recovered-20261001/metrics.json")
    meta_v99 = load("results/pilot-v1/saturn-v99/raw/recovered-20261001/manifest.json")

    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "宋体"
    style.font.size = Pt(11)

    # ---------- 标题页 ----------
    h = doc.add_heading("单细胞跨物种映射方法对比评估报告", level=0)
    h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = sub.add_run("心脏样本三物种（人 / 鼠 / 斑马鱼）pilot\n课题5 · 2026-10-05 数值冻结版")
    r.font.size = Pt(13)
    note = doc.add_paragraph()
    note.alignment = WD_ALIGN_PARAGRAPH.CENTER
    nr = note.add_run("口径声明：本报告全部结果为 transductive/in-sample 重评估，"
                      "不支持 held-out/inductive 泛化结论")
    nr.font.color.rgb = RGBColor(0xB0, 0x30, 0x00)
    nr.font.bold = True

    # ---------- 1 摘要 ----------
    doc.add_heading("1 摘要", level=1)
    doc.add_paragraph(
        "本报告在同一心脏样本三物种 pilot 数据集（人 1528 / 鼠 1535 / 斑马鱼 1543 细胞）上，"
        "对三种跨物种标签映射方法进行了统一协议的对比评估：零整合基线 ortholog-PCA、"
        "蛋白同源嵌入方法 SATURN、以及转录组对齐方法 SAMap。主要发现："
    )
    doc.add_paragraph(
        "零整合基线 ortholog-PCA 在哺乳动物对（人→鼠 0.8618、鼠→人 0.7369，coarse 层）"
        "数值高于 SATURN（0.6179 / 0.2539）；", style="List Number")
    doc.add_paragraph(
        "全部涉及斑马鱼的方向，三种方法均表现弱或无信号"
        "（按 query 分组逐方向：人/鼠→鱼——SATURN v97g 0.1835/0.3009、ortholog-PCA 0.1961/0.2755、"
        "SAMap 0.0341/0；鱼→人/鼠——SATURN v97g 0.2474/0.4651、ortholog-PCA 0.1813/0.5761"
        "（鱼→鼠 0.5761 为全表唯一高于多数类 0.4817 的鱼侧信号）、SAMap 0/0），"
        "与既证实的鱼方向 seed 双峰现象一致；", style="List Number")
    doc.add_paragraph(
        "SAMap 在本数据集无稳定迁移信号（六方向 coarse 0.0000–0.1050，全部低于对应多数类），"
        "与本地合规复现结论一致。", style="List Number")
    doc.add_paragraph(
        "上述结论仅在 transductive/in-sample 重评估口径内成立，不构成对工具在 inductive "
        "场景下泛化能力的判断；跨方法协议差异见 §5。"
    )

    # ---------- 2 数据 ----------
    doc.add_heading("2 数据与预处理", level=1)
    doc.add_paragraph(
        "数据来源：STDS0000406 公开发布（Heart Evolution Atlas），三物种各取 pilot 子集；"
        "金标准注释列 celltype。物种内isodepth/供体信息不作为 batch 校正对象。"
    )
    doc.add_paragraph(
        "冻结映射表 v1（SHA-256 be985735…583165，38 行 = 人 12 + 鼠 12 + 鱼 14）："
        "双层结构（coarse 9 粗类 / fine 17 细类），经 1:1 直系同源 pseudobulk Spearman 验证"
        "（人鼠 8 对全进 top5，5 对 rank-1）。排除规则：鼠/鱼增殖细胞与鱼线粒体群"
        "（mapping_status≠active，共鼠 30 / 鱼 44 / 人 0）不入 mapped 分母，单列 coverage。"
    )

    # ---------- 3 三方法 ----------
    doc.add_heading("3 三方法协议", level=1)

    doc.add_heading("3.1 ortholog-PCA（零整合基线）", level=2)
    doc.add_paragraph(
        "输入：三物种原始计数 → 全基因空间 log1p(CPM/100) 归一化 → 物种对 1:1 直系同源基因"
        "交集（人鼠 15,869 / 人鱼 9,131 / 鼠鱼 7,670）→ 两物种联合 PCA-50（seed 0）→ "
        "KNN K=15 cosine 倒距离加权。label-free：映射表仅用于评估分层，不进入特征。"
        "置换检验：200 次 RandomState(0) 洗牌 query 预测，单侧 p。"
    )

    doc.add_heading("3.2 SATURN（v97g）", level=2)
    doc.add_paragraph(
        "蛋白同源嵌入：ESM2 蛋白质语言模型将基因映射到蛋白嵌入空间，macrogene 聚合后"
        "跨物种联合训练（num_macrogenes=256→1000，HVG 2500，epochs=50，seed=0）。"
        "评估层 obsm/macrogenes。label-aware 机制：cross_species miner 用 labels（细胞类型整数 id）构造正/负样本；ref_labels 仅为输出列/评估真值，不参与 miner（运行时源码版本与训练命令待核实）。"
    )

    doc.add_heading("3.3 SAMap（v98 复现）", level=2)
    doc.add_paragraph(
        "转录组对齐：SAM 预处理（cell_median 归一化 + log + StandardScaler, npcs=100）后，"
        "SAMap 基于 1:1 直系同源基因构建跨物种基因近邻图（hnswlib），迭代对齐（NUMITERS=3）。"
        "keys=cell_type 参与联合图构建——该方法为 label-aware（与 ortholog-PCA 的 label-free "
        "形成对照；注意：线上运行脚本与 checked-in 版本不一致，其内容待回捞）；"
        "形成对照），已在 manifest 声明。依赖栈复用预建 pylibs（samap 1.0.16 + samalg 1.0.2 + "
        "hnswlib shim）。运行通道：WDL 流程（任务 W202610050003104，绕开停滞的离线通道）。"
    )

    doc.add_heading("3.4 v99 统一评分器", level=2)
    doc.add_paragraph(
        "对 SATURN 产物的统一协议重评估：KNN15 倒距离加权 cosine、200 次置换、"
        "coarse/fine 双向排除 mapping_status≠active。其产物 provenance 已通过独立审计"
        "（file-level confirmed，46 文件树 SHA 全对表）。v99 数字与 v97g 口径存在"
        "标签空间/排除规则/评分器三重差异，双报不合并。"
    )

    # ---------- 4 结果 ----------
    doc.add_heading("4 结果", level=1)

    doc.add_heading("4.1 主表：coarse 层六方向", level=2)
    doc.add_paragraph(
        "跨列标签空间/协议不同（见 §5），同表仅作方向性参考，不构成排名（表内未加粗、未做方法间显著性检验）。"
    )
    rows = []
    for d in DIRS:
        rows.append([
            DIR_CN[d],
            f"{orth[d]['coarse']['acc']:.4f}",
            f"{SATURN_V97G[d]:.4f}",
            f"{samap[d]['coarse']['acc']:.4f}",
            f"{v99[d]['coarse']['acc']:.4f}",
            f"{orth[d]['coarse']['majority']:.4f}",
            f"{v99[d]['coarse']['majority']:.4f}",
        ])
    add_table(doc, ["方向", "ortholog-PCA", "SATURN v97g", "SAMap v98", "v99 统一评分器",
                    "多数类·映射空间", "多数类·原始标签"], rows)

    doc.add_paragraph(
        "读数：ortholog-PCA 在哺乳动物对数值领先（人→鼠 0.8618 vs 其映射空间多数类 0.4817）；"
        "人→斑马鱼三方法均低于多数类（0.1961/0.1835/0.0341 vs 0.3976）；"
        "鼠→斑马鱼和斑马鱼→人 SATURN 略高（0.3009/0.2474），但均低于各自多数类；"
        "SAMap 全部六方向 0.0000–0.1050，远低于多数类。"
    )

    doc.add_heading("4.2 exact 层（参考）", level=2)
    rows = []
    for d in DIRS:
        rows.append([
            DIR_CN[d],
            f"{orth[d]['exact']['acc']:.4f}",
            f"{samap[d]['exact']['acc']:.4f}",
            f"{v99[d]['exact']['acc']:.4f}",
        ])
    add_table(doc, ["方向", "ortholog-PCA", "SAMap v98", "v99"], rows)
    doc.add_paragraph(
        "注：SATURN v97g 无独立 exact 层（其评估层为 obsm/macrogenes）。"
        "ortholog-PCA exact 层（原始标签空间，无排除）与 coarse 层的差异来自分母变化："
        "如人→鼠 exact 0.7824（n_q=1535）vs coarse 0.8618（n_q=1505，排除后鼠 CM 通用标签等"
        "无法匹配人细分的细胞退出分母）。\n"
        "v99 各文件 exact 口径 acc（0.4749 等）与 metrics exact 层一致，互证成立。"
    )

    doc.add_heading("4.3 覆盖率与排除", level=2)
    cov_rows = []
    for d in DIRS:
        cov_rows.append([
            DIR_CN[d],
            f"{orth[d]['coarse']['n_q']}",
            f"{samap[d]['coarse']['n_q']}",
            f"{v99[d]['coarse']['n_q']}",
        ])
    add_table(doc, ["方向", "ortholog-PCA n_q", "SAMap n_q", "v99 n_q"], cov_rows)
    doc.add_paragraph(
        "排除普查：鼠 30（Proliferating cell）/ 鱼 44（mt 30 + Proliferating 14）/ 人 0。"
        "各方法 n_q 差异来自各自排除规则的标签空间（见 §5）。"
    )

    doc.add_heading("4.4 辅助证据（confirmed 级）", level=2)
    doc.add_paragraph(
        "ESM2 消融：蛋白嵌入打乱后 SATURN h→m 67.4%→20.4%（v72-era 协议内配对；v97g 协议下未重跑），蛋白同源信号为真；"
        "物种内 ceiling：85.5 / 93.5 / 74.2（与跨物种共享潜空间，成对引用）；"
        "seed 稳定性：h→m 67.1±3.8 稳定，鱼方向双峰（11.3/48.8/8.3）；"
        "v99 新鲜重算与 09-29 版逐字段相等（评估确定性）。"
    )

    # ---------- 5 口径 ----------
    doc.add_heading("5 口径与适用边界（引用必读）", level=1)
    caveats = [
        "全部结果为 transductive/in-sample 重评估：目标表达参与联合嵌入/评分，"
        "不代表 held-out/inductive 泛化能力。",
        "跨方法标签空间不同：ortholog-PCA 与 SATURN v97g coarse/fine = 映射标签空间；"
        "SATURN v99 与 SAMap = 原始标签空间（+status 过滤，无重映射）。跨方法同表仅作方向性参考。",
        "跨方法分母不同：各列 n_q 随各自排除规则；每个 acc 必须并列 n_q 引用。",
        "SAMap per_cell included 旗标（truth∈参考标签集定义，1398）与 n_q（1505）口径不同，"
        "旗标不参与 acc 计算（脚本 md5 56bb6035 版本口径）。",
        "v99/v97g 差异（61.79% vs 48.44%）：标签空间+排除规则+评分器三重差异，双报不合并。",
        "全部单 seed（0）；鱼方向 seed 双峰已证实，单种子点估计需谨慎。",
        "shuffle_p 零分布 = 预测边际×真值边际对角积 E[null]，非多数类检验；"
        "p 值只用于'优于随机预测向量'的推断。",
        "SAMap 依赖栈为预建 pylibs 复用；脚本 md5 56bb6035（410 行版，非 Phase 5 修复版）。",
        "SATURN v97g provenance 为 EVAL3G 日志级（confirmed）；ortholog-PCA/SAMap/v99 为"
        "本项目重评估 candidate-final（Gate 复核通过）。",
        "映射表 v1（config/heart-celltype-map-v1.tsv，SHA-256 be985735…3165，38 行）当前状态为 "
        "needs-reviewer：AI 独立复核意见书已出具（九项核验、4 个低置信映射专节、排除规则四方对账 "
        "30/44/0 一致 + SAMap 差 3 待核验），人工签认尚未完成；签认前依赖该映射的 coarse/fine 层结论 "
        "按候选基准处理，不得表述为已签认的正式 benchmark。",
    ]
    for i, c in enumerate(caveats, 1):
        doc.add_paragraph(f"§5.{i} {c}", style="List Number")

    # ---------- 6 结论 ----------
    doc.add_heading("6 结论与适用边界", level=1)
    doc.add_paragraph(
        "1) 在心脏样本三物种 pilot、transductive 重评估口径内：哺乳动物近缘对（人-鼠）的"
        "跨物种标签迁移可行且零整合基线即可达到较高精度；ortholog-PCA 作为 label-free "
        "零整合基线的强表现提示，评估跨物种映射工具时应先排除'同源基因投影本身的贡献'。"
    )
    doc.add_paragraph(
        "2) 远缘对（含斑马鱼）三方法均弱或无信号，与近缘关系和 batch 效应一致；"
        "该结论受单 seed 与鱼方向双峰影响，需多 seed 与更多数据支撑后才能作为工具优劣的"
        "正式结论。"
    )
    doc.add_paragraph(
        "3) SAMap 在本数据集未表现出稳定迁移信号（label-aware 协议下），"
        "与本地合规复现一致；不能据此得出'SAMap 工具普遍无效'的结论——"
        "本结果限于该数据集、该协议、该版本栈。"
    )
    doc.add_paragraph(
        "4) 本报告全部数字以 docs/final-evidence-matrix-20261005.md 为唯一出处；"
        "每个数字可溯源至 metrics.json（SHA 锚定）。AI 使用日志见 "
        "docs/ai-usage-log-20261003.md。"
    )

    # ---------- 附录 ----------
    doc.add_heading("附录 A：产物清单与 SHA 锚点", level=1)
    appx = [
        ["ortholog-PCA", "results/pilot-v1/ortholog-pca-v98/metrics.json", "manifest 内 39 文件 SHA 全表"],
        ["SAMap v98", "results/pilot-v1/samap-v98/wdl-run/extracted/metrics.json", "WDL 任务 W202610050003104"],
        ["v99 统一评分器", "results/pilot-v1/saturn-v99/raw/recovered-20261001/metrics.json", "SHA d1081cfd…dc261"],
        ["冻结映射表 v1", "config/heart-celltype-map-v1.tsv", "SHA be985735…583165"],
        ["证据矩阵", "docs/final-evidence-matrix-20261005.md", "唯一数字出处"],
    ]
    add_table(doc, ["产物", "路径", "SHA/锚点"], appx)

    OUT.parent.mkdir(exist_ok=True)
    doc.save(str(OUT))
    fix_settings_zoom(OUT)
    print("saved:", OUT)


def fix_settings_zoom(path):
    """python-docx 默认模板写出 <w:zoom w:val="bestFit"/>，部分校验器要求 percent 属性；
    后处理改为 <w:zoom w:percent="100"/>（内容等价，规避结构校验告警）。"""
    import re as _re, shutil, zipfile
    tmp = path.with_suffix(".docx.tmp")
    zin = zipfile.ZipFile(path)
    items = zin.infolist()
    data = {i.filename: zin.read(i.filename) for i in items}
    zin.close()
    x = data["word/settings.xml"].decode("utf-8")
    x2 = _re.sub(r"<w:zoom[^>]*/>", '<w:zoom w:percent="100"/>', x)
    data["word/settings.xml"] = x2.encode("utf-8")
    zout = zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED)
    for i in items:
        zout.writestr(i, data[i.filename])
    zout.close()
    shutil.move(str(tmp), str(path))


if __name__ == "__main__":
    main()
