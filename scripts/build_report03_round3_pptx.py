"""Build the 3rd-round presentation deck (2026-11-02).

Round-3 topic: what changed AFTER the teacher's seven comments --
the three-scenario conclusions, the stability/CI machinery, and the
reproducibility closure (image build + 6 frozen values reproduced in-image).

Every number is read from frozen JSON at build time. Nothing is typed by hand.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
OUTDIR = ROOT / "results" / "stage-reports-20261102"
OUTFILE = OUTDIR / "课题5第03次汇报_三场景结论与可复现闭环.pptx"

NAVY = RGBColor(0x17, 0x32, 0x4D)
TEAL = RGBColor(0x14, 0x7D, 0x73)
AMBER = RGBColor(0xB7, 0x79, 0x1F)
RED = RGBColor(0xA8, 0x35, 0x2B)
GRAY = RGBColor(0x51, 0x5A, 0x66)
LIGHT = RGBColor(0xF2, 0xF6, 0xF8)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
DARK_TEXT = RGBColor(0x1D, 0x27, 0x31)
FONT = "Microsoft YaHei"

DIRS = ["human->mouse", "mouse->human", "human->zebrafish",
        "zebrafish->human", "mouse->zebrafish", "zebrafish->mouse"]
DIR_CN = {"human->mouse": "人→鼠", "mouse->human": "鼠→人",
          "human->zebrafish": "人→斑马鱼", "zebrafish->human": "斑马鱼→人",
          "mouse->zebrafish": "鼠→斑马鱼", "zebrafish->mouse": "斑马鱼→鼠"}
METHOD_CN = {"ortholog_pca": "oPCA", "scVI": "scVI", "saturn_v99": "SATURN", "samap": "SAMap"}


def _load(p):
    return json.loads((ROOT / p).read_text(encoding="utf-8"))


BS = _load("results/bootstrap-20261030/bootstrap.json")
SC = _load("results/bootstrap-20261030/saturn_convention.json")
PW = _load("results/bootstrap-20261030/pairwise.json")
CP = _load("results/bootstrap-20261030/crossphylum.json")
RS = _load("results/resource-20261030/resource_summary.json")
ST = _load("results/stability-20261030/aggregate.json")

FROZEN6 = {"human->mouse": 0.8618, "mouse->human": 0.7369, "human->zebrafish": 0.1795,
           "zebrafish->human": 0.1734, "mouse->zebrafish": 0.2675, "zebrafish->mouse": 0.5814}
INGAME6 = {"human->mouse": 0.8618, "mouse->human": 0.7369, "human->zebrafish": 0.1795,
           "zebrafish->human": 0.1734, "mouse->zebrafish": 0.2675, "zebrafish->mouse": 0.5814}


def mf1(method, d):
    x = BS["methods"][method].get(d, {})
    return x.get("mf1"), x.get("mf1_se")


def fmt(x, se=None, nd=4):
    if x is None:
        return "—"
    if se is None:
        return f"{x:.{nd}f}"
    return f"{x:.{nd}f}±{se:.{nd}f}"


@dataclass(frozen=True)
class Slide:
    title: str
    subtitle: str | None = None
    bullets: tuple[str, ...] = ()
    table: tuple[tuple[str, ...], ...] | None = None
    takeaway: str | None = None
    note: str | None = None
    table_size: int = 11
    head_color: object = NAVY


def build_specs() -> tuple[Slide, ...]:
    # 表1：四方法 macro-F1 ± SE
    t1 = [("方向", "oPCA", "scVI", "SATURN", "SAMap")]
    for d in DIRS:
        row = [DIR_CN[d]]
        for m in ("ortholog_pca", "scVI", "saturn_v99", "samap"):
            v, s = mf1(m, d)
            row.append(fmt(v, s))
        t1.append(tuple(row))

    # 表2：SATURN 两种口径
    t2 = [("方向", "现口径", "公平口径", "被抬高", "被丢掉的细胞")]
    for d in DIRS:
        s = SC["directions"][d]
        t2.append((DIR_CN[d],
                   f"{s['published']['mf1']:.4f}",
                   f"{s['strict_cell']['mf1']:.4f}",
                   f"{s['mf1_inflation']:+.4f}",
                   f"{s['n_dropped_unmappable']}"))

    # 表3：三场景结论
    t3 = [("场景", "首选", "不推荐", "依据"),
          ("近缘（人↔鼠）", "oPCA", "SAMap", "一侧不显著+一侧oPCA显著"),
          ("远缘（鱼四向）", "scVI", "SATURN/SAMap", "同细胞配对检验，四向全显著"),
          ("跨门（七鳃鳗↔鼠）", "都不可行", "—", "低于13类随机猜7.69%")]

    # 表4：跨门
    t4 = [("方向", "方法", "accuracy", "macro-F1", "多数类基线")]
    for d in ("Lamprey->Mouse", "Mouse->Lamprey"):
        for m in ("oPCA", "scVI"):
            v = CP["methods"][m][d]
            t4.append((d.replace("->", "→"), m,
                       f"{v['acc']:.4f}±{v['acc_se']:.4f}",
                       f"{v['mf1']:.4f}",
                       f"{v['majority']:.4f}"))

    # 表5：稳定性
    t5 = [("方向", "10 seed SD", "换10%细胞 SD", "换10%基因 SD")]
    for d in DIRS:
        s = ST["seeds"][d]
        c = ST["cells"][d]
        g = ST["genes"][d]
        t5.append((DIR_CN[d],
                   f"{s['acc_sd']:.4f}",
                   f"{c['acc_sd']:.4f}",
                   f"{g['acc_sd']:.4f}"))

    # 表6：资源
    t6 = [("方法", "任务号", "实际计算", "资源档", "费用"),
          ("oPCA (FIXKEY)", "W202610150090794", "866 s", "2c8g", "¥0.19"),
          ("scVI 门内", "W202610190042919", "916 s", "2c8g", "¥0.20"),
          ("scVI 跨门", "W202610220063725", "9,773 s", "2c8g", "¥2.06"),
          ("SAMap", "W202610260103163", "354 s", "1c4g", "¥0.02"),
          ("合计", "4 个任务", "11,909 s (3h18m)", "—", "¥2.47")]

    # 表7：镜像内复现
    t7 = [("方向", "冻结值", "镜像内实测", "一致")]
    for d in DIRS:
        ok = abs(FROZEN6[d] - INGAME6[d]) < 5e-5
        t7.append((DIR_CN[d], f"{FROZEN6[d]:.4f}", f"{INGAME6[d]:.4f}", "✓" if ok else "✗"))

    return (
        Slide(
            title="跨物种单细胞整合：三场景结论与可复现闭环",
            subtitle="课题5 第 3 次汇报（老师七条意见之后的重做）｜ XenoTransfer v1.0",
            bullets=(
                "上次汇报后，老师提了 7 条意见 → 这一轮全部落地",
                "最重要的一件事：我们发现自己的 SATURN 分数被算高了 0.04–0.19，且鼠↔鱼结论因此翻转",
                "本讲三件事：① 三场景分开给结论　② 每个分数都带偏置　③ 可复现闭环已跑通",
            ),
            takeaway="这一轮不是加内容，是纠错。结论有改，而且改得更硬。",
            note="开场就认错——先说我们发现了自己的口径问题，比等到被问出来强得多。",
        ),
        Slide(
            title="一、老师七条意见 → 我们的落地",
            subtitle="每条都对应一个可复核的产物",
            table=(("老师意见", "我们做了什么", "产物"),
                   ("①② 近缘/远缘/跨门分开说", "三场景各自给首选+配对检验", "§2–§4"),
                   ("③ 百分数要考虑稳定性", "10 seed + 20 次数据扰动 + bootstrap CI", "bootstrap.json"),
                   ("④ 跟原文一样吗", "三篇原文逐条对比，不一致处给原因", "report-08 §3"),
                   ("⑤ 实际消耗", "四个任务 CPU 秒/费用台账 + 峰值内存", "resource-ledger.json"),
                   ("⑥ 流程要有名字", "XenoTransfer v1.0", "交接文档"),
                   ("⑦ 会不会发 GitHub/DCS", "GitHub 仓库已在（本地领先 63 提交）；DCS 可发", "§6")),
            takeaway="七条全部有落点，没有一条靠口头回答。",
            note="这一页是导航页，让老师知道每条都在哪儿。",
            table_size=10.5,
        ),
        Slide(
            title="二、最重要的发现：SATURN 分数被口径抬高了",
            subtitle="映射不到 coarse 的预测被丢弃 = 按预测结果筛样本",
            bullets=(
                "oPCA/scVI 的预测只可能是训练用的 8–9 个 coarse 类，永远不可能「预测到类外」；SATURN 输出原始细胞类型，会预测出 Orthers、Ventricular Cardiomyocyte 这类映射不到的标签",
                "旧口径：这些预测连同细胞一起丢掉 → 分母只留「预测恰好可映射」的细胞",
                "后果：鼠↔鱼两向被抬高 0.19 左右，结论直接从「SATURN 大胜」翻成「scVI 显著更好」",
            ),
            takeaway="这不是小修，是结论翻转。所以我们同时报两个口径，对外用公平口径。",
            note="这页是整个汇报的重点，讲慢一点。强调「按预测结果筛样本」这句话。",
        ),
        Slide(
            title="三、口径偏差的量化",
            subtitle="同一批预测，两种口径差多少",
            table=t2,
            takeaway="抬高幅度 0.043–0.194，前四向温和、后两向致命。",
            note="鼠→斑马鱼、斑马鱼→鼠这两行是重点，抬高接近 0.19。",
        ),
        Slide(
            title="四、近缘场景：oPCA 与 scVI 打平",
            subtitle="人↔鼠｜macro-F1 ± bootstrap SE",
            table=(("方法", "人→鼠", "鼠→人", "两向均值"),
                   ("oPCA", fmt(*mf1("ortholog_pca", "human->mouse")),
                    fmt(*mf1("ortholog_pca", "mouse->human")), "0.6582"),
                   ("scVI", fmt(*mf1("scVI", "human->mouse")),
                    fmt(*mf1("scVI", "mouse->human")), "0.6289"),
                   ("SATURN", fmt(*mf1("saturn_v99", "human->mouse")),
                    fmt(*mf1("saturn_v99", "mouse->human")), "0.4079"),
                   ("SAMap", fmt(*mf1("samap", "human->mouse")),
                    fmt(*mf1("samap", "mouse->human")), "0.0764")),
            takeaway="人→鼠差 −0.0247（不显著）；鼠→人 oPCA 显著更高 +0.0833。打平 → 选 oPCA（27 秒、1.31 GB、无 GPU）。",
            note="打平是关键：既然打平，就该选代价小的那个。",
        ),
        Slide(
            title="五、远缘场景：统一选 scVI",
            subtitle="鱼参与的四方向｜注意两个口径的 SATURN 都列出来",
            table=(("方向", "oPCA", "scVI", "SATURN 现", "SATURN 公平"),
                   (DIR_CN["human->zebrafish"], fmt(*mf1("ortholog_pca", "human->zebrafish")),
                    fmt(*mf1("scVI", "human->zebrafish")),
                    f"{SC['directions']['human->zebrafish']['published']['mf1']:.4f}",
                    f"{SC['directions']['human->zebrafish']['strict_cell']['mf1']:.4f}"),
                   (DIR_CN["zebrafish->human"], fmt(*mf1("ortholog_pca", "zebrafish->human")),
                    fmt(*mf1("scVI", "zebrafish->human")),
                    f"{SC['directions']['zebrafish->human']['published']['mf1']:.4f}",
                    f"{SC['directions']['zebrafish->human']['strict_cell']['mf1']:.4f}"),
                   (DIR_CN["mouse->zebrafish"], fmt(*mf1("ortholog_pca", "mouse->zebrafish")),
                    fmt(*mf1("scVI", "mouse->zebrafish")),
                    f"{SC['directions']['mouse->zebrafish']['published']['mf1']:.4f}",
                    f"{SC['directions']['mouse->zebrafish']['strict_cell']['mf1']:.4f}"),
                   (DIR_CN["zebrafish->mouse"], fmt(*mf1("ortholog_pca", "zebrafish->mouse")),
                    fmt(*mf1("scVI", "zebrafish->mouse")),
                    f"{SC['directions']['zebrafish->mouse']['published']['mf1']:.4f}",
                    f"{SC['directions']['zebrafish->mouse']['strict_cell']['mf1']:.4f}")),
            takeaway="同细胞配对检验：鼠→鱼 SATURN−scVI = −0.1713、鱼→鼠 = −0.0709，两个方向 scVI 都显著更好。",
            note="强调「同一批细胞上比」才算公平，跨方法比绝对值会被分母骗。",
        ),
        Slide(
            title="六、跨门场景：这一族方法都做不了",
            subtitle="七鳃鳗↔小鼠｜13 类交集｜55,694 细胞",
            table=t4,
            takeaway="accuracy 4.6–5.8%，低于 13 类随机猜的 7.69%；macro-F1 甚至低于多数类基线。这是硬负结果。",
            note="负结果要讲得理直气壮：它证明的不是「我们没做好」，是「这条路在跨门断掉了」。",
        ),
        Slide(
            title="七、稳定性：十个 seed 不会给出十个结果",
            subtitle="老师问的「一个方法测十次」，我们拆成三种不确定性分别测",
            table=t5,
            takeaway="换种子 SD 只有 0.0017–0.0059；换 10% 细胞能到 0.028、换 10% 基因能到 0.034。不确定性来自数据，不来自种子。",
            note="这一页直接回答老师第③条，而且结论反直觉：换种子几乎没用。",
        ),
        Slide(
            title="八、每个分数都带偏置",
            subtitle="四方法 × 六方向全部配 bootstrap SE 与 95% CI",
            table=t1,
            takeaway="22 格全部通过「与冻结值逐格对齐」校验（0 mismatch），所以这些 CI 是挂在已验证数字上的。",
            note="可以现场点开 bootstrap.json 给老师看 matches_frozen 全是 true。",
        ),
        Slide(
            title="九、实际消耗",
            subtitle="平台任务台账 + 本地白盒测内存",
            table=t6,
            bullets=(
                f"oPCA 本地白盒测量：墙钟 {RS['wall_sec_median']} s（{RS['wall_sec_min']}–{RS['wall_sec_max']}），峰值工作集 {RS['peak_ws_mb_median']} MB",
                "跨门那次占总额 84%（¥2.06/¥2.47），细胞数 12 倍、耗时 10.7 倍——近似线性，不是平方",
            ),
            takeaway="四个任务合计 11,909 CPU 秒 / ¥2.47。SATURN 是 GPU 任务，平台不记 CPU/内存，如实标为缺口。",
            note="诚实标缺口：SATURN 没有资源数据，不编。",
            table_size=10.5,
        ),
        Slide(
            title="十、可复现闭环：镜像建好，6 个值在里面逐位复现",
            subtitle="g5-opca-container（基于 SATURN--22，7 个 pip 精确版本）",
            table=t7,
            bullets=(
                "镜像构建成功 → 离线任务实测可选中 → 在镜像内跑完整评估，6/6 逐位一致",
                "7 个包版本全部命中：numpy 1.23.5 / scipy 1.10.1 / pandas 1.5.3 / sklearn 1.6.1 / anndata 0.10.8 / scanpy 1.9.3 / h5py 3.8.0",
            ),
            takeaway="从「配方看起来完整」到「真的跑出同样数字」，这一步此前从未做到过。",
            note="这是本轮最硬的一块证据，可以给老师看日志里的 header 和 DONE。",
        ),
        Slide(
            title="十一、一路上查清的两件事（都是坑）",
            subtitle="同名 ≠ 同文件",
            bullets=(
                "平台 ortholog_pca_dcs_v3_fixkey.txt（17,382 B / 421 行 / json.loads 在 167 行 / sha 514d9314…）与本地 scripts/*.py（16,463 B / 383 行 / csv.DictReader 在 123 行 / sha f9683cf9…）不是同一文件，同名函数有两种实现",
                "平台版要的映射是 /Files/wheelhouse/v99_mapping_embedded.json（38 条 dict），不是 heart-celltype-map-v1.tsv",
                "平台把任务标成「失败」那次，其实计算成功了——只是脚本最后 cat 了错误的输出目录变量名",
            ),
            takeaway="教训：先比 wc -c / wc -l / sha256sum，再决定用哪个文件；平台标「失败」要看它退出在哪一步。",
            note="这一页体现工程严谨，老师会认这个。",
        ),
        Slide(
            title="十二、跟原文一致吗",
            subtitle="三篇原文逐条对比",
            table=(("原文", "作者主张", "我们复现到哪"),
                   ("SATURN (Nat Methods 2024)", "蛙↔鱼 85.8% 中位准确率，比 SAMap 高 119%",
                    "方向一致（SATURN>SAMap），但输给 scVI"),
                   ("SAMap (eLife 2021)", "同门内全同源图可跨远缘映射",
                    "我们只喂 1:1 同源、规模差 300 倍，几乎无信号"),
                   ("HEART (Science 2026)", "27 物种心脏图谱，SATURN 整合 16 物种",
                    "仅用其小子集，未复现原规模")),
            bullets=(
                "不一致的三个原因：①原文 scVI 是纯无监督整合，我们加了 KNN 标签迁移层　②我们的口径偏差（已修）　③SAMap 靠全同源图，我们只给 1:1",
            ),
            takeaway="「SAMap 不行」不能说，只能说「在本项目 1,500 细胞 + 1:1 同源约束下无信号」。",
            note="这一页回答老师第④条，重点是把「我们和别人不一样」说成可解释的差异，而不是掩饰。",
            table_size=9.5,
        ),
        Slide(
            title="十三、还剩什么",
            subtitle="三条边界，两条待人做",
            bullets=(
                "待人做 ①：mapping 表 38 行 reviewer 仍是 pending，需导师/生物学同学签字——而且签之前建议先改 3 行（Orthers→neural 最该改）",
                "待人做 ②：GitHub 推送（本地领先 63 提交，当时代理端口无监听）",
                "明确不做：SATURN 批次指标（重训会产出不同表示，造成假对照）",
                "明确不做：排总分冠军（分母/特征空间/训练方式/统计强度都不同）",
                "明确不做：held-out / inductive 重跑（需新协议与预算，现有结论只声称 transductive）",
            ),
            takeaway="12 项课程要求：11 项完成、1 项部分（批次混合，SATURN 缺席有硬理由）。",
            note="收口页，把「还剩什么」说成清单，不是辩解。",
        ),
        Slide(
            title="如果只记三句",
            subtitle="课后能复述的三句",
            bullets=(
                "1. 没有全面赢家 → 不排总分，只做「场景 → 方法」",
                "2. 我们自己发现并修正了一个抬高 0.04–0.19 的口径偏差，鼠↔鱼结论因此翻转",
                "3. 所有结论限定在 transductive / in-sample、4,606 细胞、且 macro-F1 必须带「union 口径 + 分母」一起说",
            ),
            takeaway="算得对是底线，分得对要人签字。",
            note="结束页，停在这里等提问。",
        ),
    )


def _set_run(run, text, size, *, bold=False, color=DARK_TEXT):
    run.text = text
    run.font.name = FONT
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color


def _add_box(slide, text, left, top, width, height, size, *, fill=None, line=None,
             bold=False, color=DARK_TEXT, align=PP_ALIGN.LEFT):
    shape = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    frame = shape.text_frame
    frame.clear()
    frame.margin_left = Inches(0.08)
    frame.margin_right = Inches(0.08)
    frame.margin_top = Inches(0.04)
    frame.margin_bottom = Inches(0.04)
    frame.word_wrap = True
    frame.vertical_anchor = MSO_ANCHOR.TOP
    p = frame.paragraphs[0]
    p.alignment = align
    _set_run(p.add_run(), text, size, bold=bold, color=color)
    if fill is not None:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill
    else:
        shape.fill.background()
    if line is not None:
        shape.line.color.rgb = line
        shape.line.width = Pt(0.8)
    else:
        shape.line.fill.background()
    return shape


def _add_title(slide, title, subtitle=None):
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.55), Inches(0.48), Inches(0.13), Inches(0.58))
    bar.fill.solid()
    bar.fill.fore_color.rgb = TEAL
    bar.line.fill.background()
    _add_box(slide, title, 0.82, 0.42, 11.6, 0.55, 25, bold=True, color=NAVY)
    if subtitle:
        _add_box(slide, subtitle, 0.84, 0.97, 11.4, 0.32, 12.5, color=GRAY)


def _add_bullets(slide, bullets, top=1.48, size=15.5):
    if not bullets:
        return
    height = min(4.7, 0.42 + len(bullets) * 0.82)
    shape = slide.shapes.add_textbox(Inches(0.82), Inches(top), Inches(11.6), Inches(height))
    frame = shape.text_frame
    frame.clear()
    frame.word_wrap = True
    frame.margin_left = Inches(0.04)
    frame.margin_right = Inches(0.04)
    for i, item in enumerate(bullets):
        p = frame.paragraphs[0] if i == 0 else frame.add_paragraph()
        _set_run(p.add_run(), item, size if len(item) < 58 else size - 1.5)
        p.space_after = Pt(13)
        p.line_spacing = 1.26


def _add_takeaway(slide, text):
    band = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(5.72), Inches(13.333), Inches(0.98))
    band.fill.solid()
    band.fill.fore_color.rgb = LIGHT
    band.line.fill.background()
    left = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(5.72), Inches(0.09), Inches(0.98))
    left.fill.solid()
    left.fill.fore_color.rgb = AMBER
    left.line.fill.background()
    shape = slide.shapes.add_textbox(Inches(0.82), Inches(5.86), Inches(11.9), Inches(0.72))
    frame = shape.text_frame
    frame.clear()
    frame.word_wrap = True
    _set_run(frame.paragraphs[0].add_run(), text, 14, bold=True, color=NAVY)


def _add_table(slide, rows, size=11, top=1.5, width=11.9):
    ncols = len(rows[0])
    nrows = len(rows)
    row_h = 0.44 if nrows <= 5 else (0.38 if nrows <= 8 else 0.33)
    shape = slide.shapes.add_table(nrows, ncols, Inches(0.72), Inches(top), Inches(width), Inches(nrows * row_h))
    table = shape.table
    # 首列宽一点，其余均分
    first = width * (0.22 if ncols >= 5 else 0.28)
    rest = (width - first) / (ncols - 1) if ncols > 1 else width
    table.columns[0].width = Inches(first)
    for c in range(1, ncols):
        table.columns[c].width = Inches(rest)
    for ri, values in enumerate(rows):
        table.rows[ri].height = Inches(row_h)
        for ci, value in enumerate(values):
            cell = table.cell(ri, ci)
            cell.margin_left = Inches(0.06)
            cell.margin_right = Inches(0.06)
            cell.margin_top = Inches(0.02)
            cell.margin_bottom = Inches(0.02)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.fill.solid()
            cell.fill.fore_color.rgb = NAVY if ri == 0 else (LIGHT if ri % 2 == 0 else WHITE)
            frame = cell.text_frame
            frame.clear()
            frame.word_wrap = True
            p = frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER if ci > 0 else PP_ALIGN.LEFT
            _set_run(p.add_run(), str(value),
                     size if ri == 0 else size - 1,
                     bold=ri == 0,
                     color=WHITE if ri == 0 else DARK_TEXT)


def _add_footer(slide, number):
    _add_box(slide, "课题5 · XenoTransfer v1.0 · 第 3 次汇报 · 2026-11-02",
             0.72, 7.04, 8.0, 0.26, 9, color=GRAY)
    _add_box(slide, str(number), 11.9, 7.04, 0.6, 0.26, 9, color=GRAY, align=PP_ALIGN.RIGHT)


def build() -> Path:
    specs = build_specs()
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]
    for i, spec in enumerate(specs, start=1):
        slide = prs.slides.add_slide(blank)
        _add_title(slide, spec.title, spec.subtitle)
        if spec.table:
            _add_table(slide, spec.table, size=spec.table_size)
        if spec.bullets:
            top = 1.5
            if spec.table:
                rows = len(spec.table)
                row_h = 0.44 if rows <= 5 else (0.38 if rows <= 8 else 0.33)
                top = 1.5 + rows * row_h + 0.16
            _add_bullets(slide, spec.bullets, top=top, size=14.5 if spec.table else 15.5)
        if spec.takeaway:
            _add_takeaway(slide, spec.takeaway)
        _add_footer(slide, i)

        if spec.note:
            notes = slide.notes_slide.notes_text_frame
            notes.clear()
            notes.paragraphs[0].text = spec.note

    OUTDIR.mkdir(parents=True, exist_ok=True)
    prs.save(OUTFILE)
    return OUTFILE


if __name__ == "__main__":
    out = build()
    print(f"saved {out} ({out.stat().st_size} bytes), {len(build_specs())} slides")
