"""Build the Monday course 5 presentation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "deliverables" / "course5-monday-presentation.pptx"

NAVY = RGBColor(0x17, 0x32, 0x4D)
TEAL = RGBColor(0x14, 0x7D, 0x73)
AMBER = RGBColor(0xB7, 0x79, 0x1F)
GRAY = RGBColor(0x51, 0x5A, 0x66)
LIGHT = RGBColor(0xF2, 0xF6, 0xF8)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LINE = RGBColor(0xD6, 0xDE, 0xE4)
DARK_TEXT = RGBColor(0x1D, 0x27, 0x31)
FONT = "Microsoft YaHei"


@dataclass(frozen=True)
class SlideSpec:
    title: str
    subtitle: str | None = None
    bullets: tuple[str, ...] = ()
    table: tuple[tuple[str, ...], ...] | None = None
    process: tuple[str, ...] | None = None
    note: str | None = None


SLIDES: tuple[SlideSpec, ...] = (
    SlideSpec(
        title="跨物种细胞类型整合工具评测",
        subtitle="SATURN vs SAMap vs scVI 系 | 课题5初步方案",
        bullets=(
            "组员：____、____、____",
            "课程阶段：下节课前方案汇报",
            "当前状态：G0 本地基线通过；G1/G2 只读排查完成，等待课程数据入口",
        ),
        note="开场说明：本次汇报的是可执行初步方案，不是工具结果排名。",
    ),
    SlideSpec(
        title="一页结论",
        bullets=(
            "目标：做可审计的跨物种单细胞整合基准评测",
            "路径：HEART 2-3 物种先打通流程，再扩展近缘/远缘/混合场景",
            "后置：LBSPA 七鳃鳗-小鼠 snRNA 只做单细胞主结论后的补充",
            "已完成：本地基线全绿；DCS 两区域只读排查完成（课程数据 0 命中）",
            "阻塞项：课程数据入口待老师回复；实例内版本与正式 kBET 待开实例核验",
            "镜像候选：SATURN--22/--21 页面同栈；平台无预置 kBET 镜像",
            "纪律：启动门未通过前，不创建实例、不上传数据、不安装包、不提交任务",
        ),
        note="强调当前是准备完成，不是实验完成；pending 是安全状态。",
    ),
    SlideSpec(
        title="课题理解：四层拆解",
        table=(
            ("层次", "核心问题", "当前设计"),
            ("数据", "用哪些物种、细胞和标签", "HEART pilot；后续覆盖近缘、远缘、混合"),
            ("方法", "如何公平比较", "相同输入、拆分、同源规则、随机种子"),
            ("评价", "什么算好", "macro-F1、kBET、iLISI、silhouette、资源"),
            ("复现", "别人能否接手", "manifest、参数、版本、日志、指标、资源文件"),
        ),
        note="说明为什么不能直接复用论文结果：我们的任务是评测工具，不是复现一张论文图。",
    ),
    SlideSpec(
        title="文献精读：HEART",
        bullets=(
            "论文：Science，DOI 10.1126/science.adw0855",
            "27 个物种多组学；scRNA-seq 14 物种、399,483 细胞",
            "保守性分析：SATURN 整合 16 物种、479,483 细胞；SAMap 做映射",
            "关键设置：ESM2B 蛋白嵌入、2,000 macrogenes、8,000 HVGs",
            "数据线索：CNGB CNP0006537；accession 不是 DCS 挂载路径",
            "对本课题：提供标签和物种范围，但不能替代小组统一评测",
        ),
        note="讲述时突出 HEART 为什么适合作为主数据，以及 accession 与平台路径的区别。",
    ),
    SlideSpec(
        title="文献精读：LBSPA",
        bullets=(
            "论文：Science，DOI 10.1126/science.aea2535",
            "七鳃鳗全脑 Stereo-seq：465,778 空间细胞、约 200 万估计细胞",
            "单核数据：41,678 个高质量 snRNA、209 个细胞簇",
            "七鳃鳗-小鼠比较：6,930 个一对一同源基因；scVI + Harmony",
            "对本课题：snRNA 作为跨门类后置补充；空间数据暂不进入主实验",
            "理由：避免同时混淆物种距离、模态差异和标签体系差异",
        ),
        note="老师已明确空间数据暂不做；LBSPA 不是被放弃，而是后置。",
    ),
    SlideSpec(
        title="数据与场景设计",
        table=(
            ("场景", "数据", "目的"),
            ("流程试跑", "HEART 2-3 物种 CM/FB", "验证端到端闭环"),
            ("近缘组合", "待 DCS 核实物种", "检验保守细胞类型标签转移"),
            ("远缘组合", "待 DCS 核实物种", "检验跨大距离整合能力"),
            ("混合类别", "待 DCS 核实物种", "检验类型结构差异"),
            ("LBSPA 补充", "七鳃鳗-小鼠 snRNA 小子集", "主结论后做稳健性补充"),
        ),
        note="物种名保持 pending，等页面证据；首轮 pilot 不做工具排名。",
    ),
    SlideSpec(
        title="统一评测协议",
        bullets=(
            "相同输入：同一批细胞、QC 规则、标签字段和同源基因规则",
            "评估方式：留一物种标签转移，报告每折与聚合 macro-F1",
            "随机种子：7、17、27；报告均值、标准差和失败折",
            "指标：macro-F1、正式 kBET、iLISI、silhouette、时间和峰值内存",
            "诊断：同时看批次混合、生物保守性和物种过度混合",
            "Agent 友好度：文档、CLI/API、参数、输出、失败诊断、复现六项",
        ),
        note="正式结果禁止使用本地 smoke test 的 kBET 代理。",
    ),
    SlideSpec(
        title="执行路线：R0-R6",
        process=("R0 认领", "R1 本地基线", "R2 只读证据", "R3 交叉复核", "R4 启动门", "R5 pilot", "R6 正式报告"),
        bullets=(
            "R0：2-4 小时，完成认领和证据清单",
            "R1：24 小时，每人提交 draft PR",
            "R2：24-36 小时，补 G1/G2 只读证据",
            "R3/R4：互审、补齐启动门并取得三人批准",
            "R5：单次 25 分钟硬停止；R6：正式场景与 Word 报告",
        ),
        note="R0-R4 均不消耗云资源；R5 前必须通过 startup_preflight。",
    ),
    SlideSpec(
        title="接手操作卡",
        bullets=(
            "1. clone 仓库，从 main 创建短分支",
            "2. pip install -r requirements.txt",
            "3. unittest discover -s tests -v",
            "4. smoke_test.py --outdir smoke-output",
            "5. plan_contract.py / budget_check.py --profile 4090x1",
            "6. startup_preflight.py：证据未齐时退出码 2 是安全阻塞",
            "7. A 查数据字段；B 查镜像版本；C 维护指标和 artifact 契约",
        ),
        note="这一页回应老师要求：非本课题同学拿到方案也能直接开始操作。",
    ),
    SlideSpec(
        title="启动门与预算",
        table=(
            ("控制项", "规则", "证据"),
            ("云动作", "G3 前禁止创建/上传/安装/提交", "startup-preflight.json"),
            ("硬件", "默认 4090x1", "dcs-budget-plan.json"),
            ("时间", "pilot 25 分钟硬停止", "resource_usage.json"),
            ("内存", "75 GB 峰值停止", "resource_usage.json"),
            ("成本", "单次 ¥10 上限", "budget_check.py 输出"),
            ("实例", "任务结束立即停止", "运行台账"),
        ),
        note="4090x2 只作为单卡内存不足后的例外，需要新证据和组内批准。",
    ),
    SlideSpec(
        title="分工与交叉复核",
        table=(
            ("成员", "主线", "当前小交付", "复核人"),
            ("____", "A 数据与生物学", "路径、字段、物种、标签、同源基因", "C"),
            ("____", "B 环境与算力", "镜像、版本、GPU、预算、停止规则", "A"),
            ("____", "C 评测与报告", "指标、留一物种、artifact、报告", "B"),
        ),
        bullets=(
            "主线可轮换；主责是推进人，不是审批人",
            "每次 PR 写清：改了什么、输入、验证方式、是否触碰 DCS",
        ),
        note="展示前把成员姓名补齐。",
    ),
    SlideSpec(
        title="风险与应对",
        table=(
            ("风险", "应对"),
            ("DCS 数据入口缺失", "两区域排查已留证据；已向老师提交精确问题，等待回复"),
            ("镜像版本冲突", "实例内只读 import/which/version，不按页面猜"),
            ("OOM 或超时", "保存失败 artifact，缩小物种/细胞/时间"),
            ("指标不可比", "统一输入、拆分、种子、版本和资源记录"),
            ("把论文结果当结论", "结论只引用本组运行 artifact"),
        ),
        note="风险应对的核心是留证据，而不是临时改参数。",
    ),
    SlideSpec(
        title="结论与下一步",
        bullets=(
            "方案已达到可交接标准：数据、方法、指标、预算、分工和停止线明确",
            "下一步：老师回复入口后补 G1（路径/字段/物种），再开实例补 G2",
            "G1/G2 通过后提交启动门审查，申请 4090x1 最小 pilot",
            "pilot 只验证流程；正式排名留给近缘/远缘/混合场景",
            "最终交付基准报告、场景化选型指南和 Word 结题报告",
        ),
        note="结尾回到老师要求：理解课题、精读文献、可执行方案和小组分工均已覆盖。",
    ),
)


def set_text(frame, text: str, size: int, *, bold: bool = False, color: RGBColor = DARK_TEXT) -> None:
    frame.text = text
    run = frame.paragraphs[0].runs[0]
    run.font.name = FONT
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color


def add_box(
    slide,
    text: str,
    left: float,
    top: float,
    width: float,
    height: float,
    size: int,
    *,
    fill: RGBColor | None = None,
    line: RGBColor | None = LINE,
    bold: bool = False,
    color: RGBColor = DARK_TEXT,
    align=PP_ALIGN.LEFT,
) -> None:
    shape = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    frame = shape.text_frame
    frame.clear()
    frame.margin_left = Inches(0.08)
    frame.margin_right = Inches(0.08)
    frame.margin_top = Inches(0.04)
    frame.margin_bottom = Inches(0.04)
    frame.word_wrap = True
    frame.vertical_anchor = MSO_ANCHOR.TOP
    paragraph = frame.paragraphs[0]
    paragraph.alignment = align
    run = paragraph.add_run()
    run.text = text
    run.font.name = FONT
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
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


def add_title(slide, title: str, subtitle: str | None = None) -> None:
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.55), Inches(0.48), Inches(0.13), Inches(0.58))
    bar.fill.solid()
    bar.fill.fore_color.rgb = TEAL
    bar.line.fill.background()
    add_box(slide, title, 0.82, 0.42, 10.8, 0.55, 27, bold=True, color=NAVY, line=None)
    if subtitle:
        add_box(slide, subtitle, 0.84, 0.97, 10.5, 0.32, 13, color=GRAY, line=None)


def add_bullets(slide, bullets: tuple[str, ...], top: float = 1.48) -> None:
    if not bullets:
        return
    height = min(4.9, 0.42 + len(bullets) * 0.58)
    shape = slide.shapes.add_textbox(Inches(0.82), Inches(top), Inches(11.15), Inches(height))
    frame = shape.text_frame
    frame.clear()
    frame.word_wrap = True
    frame.margin_left = Inches(0.04)
    frame.margin_right = Inches(0.04)
    for index, item in enumerate(bullets):
        paragraph = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
        run = paragraph.add_run()
        run.text = item
        run.font.name = FONT
        run.font.size = Pt(15 if len(item) < 48 else 14)
        run.font.color.rgb = DARK_TEXT
        paragraph.space_after = Pt(9)
        paragraph.line_spacing = 1.12


def add_table(slide, rows: tuple[tuple[str, ...], ...]) -> None:
    shape = slide.shapes.add_table(len(rows), len(rows[0]), Inches(0.75), Inches(1.48), Inches(10.9), Inches(3.9))
    table = shape.table
    widths = _table_widths(len(rows[0]))
    for column_index, width in enumerate(widths):
        table.columns[column_index].width = Inches(width)
    for row_index, values in enumerate(rows):
        table.rows[row_index].height = Inches(0.62 if row_index else 0.48)
        for column_index, value in enumerate(values):
            cell = table.cell(row_index, column_index)
            cell.margin_left = Inches(0.07)
            cell.margin_right = Inches(0.07)
            cell.margin_top = Inches(0.03)
            cell.margin_bottom = Inches(0.03)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.fill.solid()
            cell.fill.fore_color.rgb = NAVY if row_index == 0 else (LIGHT if row_index % 2 == 0 else WHITE)
            frame = cell.text_frame
            frame.clear()
            frame.word_wrap = True
            paragraph = frame.paragraphs[0]
            run = paragraph.add_run()
            run.text = value
            run.font.name = FONT
            run.font.size = Pt(12 if row_index == 0 else 11)
            run.font.bold = row_index == 0
            run.font.color.rgb = WHITE if row_index == 0 else DARK_TEXT


def _table_widths(columns: int) -> tuple[float, ...]:
    if columns == 3:
        return (1.75, 4.35, 4.8)
    if columns == 4:
        return (1.4, 2.7, 5.1, 1.7)
    return (10.9 / columns,) * columns


def add_process(slide, steps: tuple[str, ...]) -> None:
    left = 0.72
    top = 1.52
    width = 1.42
    height = 0.58
    for index, step in enumerate(steps):
        x = left + index * (width + 0.16)
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(top), Inches(width), Inches(height))
        shape.adjustments[0] = 0.16
        shape.fill.solid()
        shape.fill.fore_color.rgb = TEAL if index in (1, 4, 6) else NAVY
        shape.line.fill.background()
        frame = shape.text_frame
        frame.clear()
        frame.word_wrap = True
        frame.margin_left = Inches(0.03)
        frame.margin_right = Inches(0.03)
        frame.vertical_anchor = MSO_ANCHOR.MIDDLE
        paragraph = frame.paragraphs[0]
        paragraph.alignment = PP_ALIGN.CENTER
        run = paragraph.add_run()
        run.text = step
        run.font.name = FONT
        run.font.size = Pt(10.5)
        run.font.bold = True
        run.font.color.rgb = WHITE
        if index < len(steps) - 1:
            arrow = slide.shapes.add_shape(
                MSO_SHAPE.RIGHT_ARROW,
                Inches(x + width + 0.025),
                Inches(top + 0.20),
                Inches(0.11),
                Inches(0.18),
            )
            arrow.fill.solid()
            arrow.fill.fore_color.rgb = AMBER
            arrow.line.fill.background()


def add_footer(slide, number: int) -> None:
    add_box(slide, "课题5 | 跨物种单细胞整合工具评测", 0.75, 7.02, 5.0, 0.25, 9, color=GRAY, line=None)
    add_box(slide, str(number), 11.7, 7.02, 0.45, 0.25, 9, color=GRAY, line=None, align=PP_ALIGN.RIGHT)


def build() -> Path:
    presentation = Presentation()
    presentation.slide_width = Inches(13.333)
    presentation.slide_height = Inches(7.5)
    blank = presentation.slide_layouts[6]

    for index, spec in enumerate(SLIDES, start=1):
        slide = presentation.slides.add_slide(blank)
        background = slide.background.fill
        background.solid()
        background.fore_color.rgb = WHITE
        if index == 1:
            accent = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.22))
            accent.fill.solid()
            accent.fill.fore_color.rgb = TEAL
            accent.line.fill.background()
            add_box(slide, spec.title, 0.85, 1.95, 10.6, 1.0, 34, bold=True, color=NAVY, line=None)
            if spec.subtitle:
                add_box(slide, spec.subtitle, 0.88, 2.95, 9.8, 0.45, 18, color=TEAL, line=None)
            add_bullets(slide, spec.bullets, top=3.75)
        else:
            add_title(slide, spec.title, spec.subtitle)
            if spec.process:
                add_process(slide, spec.process)
            if spec.table:
                add_table(slide, spec.table)
            bullets_top = 2.35 if spec.process else 1.48
            if not spec.table:
                add_bullets(slide, spec.bullets, top=bullets_top)
            elif spec.bullets:
                add_bullets(slide, spec.bullets, top=4.95)
        if spec.note:
            slide.notes_slide.notes_text_frame.text = spec.note
        add_footer(slide, index)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    presentation.save(OUTPUT)
    return OUTPUT


def main() -> None:
    print(build())


if __name__ == "__main__":
    main()
