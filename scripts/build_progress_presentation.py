"""Build the Phase-1 progress presentation for course 5."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "deliverables" / "course5-progress-presentation.pptx"

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
    takeaway: str | None = None
    note: str | None = None


SLIDES: tuple[SlideSpec, ...] = (
    SlideSpec(
        title="跨物种细胞类型整合工具评测",
        subtitle="SATURN vs SAMap vs scVI ｜ 课题5 第一阶段进度汇报",
        bullets=(
            "组员：____、____、____",
            "本次汇报：数据、环境、首批基线结果",
            "当前状态：四道质量门全部通过，scVI 三物种基线已出数",
        ),
        note="开场：上次讲的是方案，这次讲的是干出来的进展——四道门全过，第一个方法的三物种成绩已经出来了。",
    ),
    SlideSpec(
        title="一页结论",
        bullets=(
            "四道质量门（G0 本地基线 / G1 数据 / G2 环境 / G3 全组批准）全部通过",
            "三物种心脏数据（人 3 万 / 鼠 6 万 / 斑马鱼 5 万细胞）已上传并逐字节校验",
            "scVI 首批基线：人 98.38% / 鼠 98.12% / 斑马鱼 92.51%（统一协议）",
            "SAMap 版本实测 1.0.16；SATURN 训练入口在平台容器内跑通",
        ),
        takeaway="要点：从“只有方案”到“有数据、有环境、有第一批数字”。",
        note="一页说完这次汇报的全部干货，后面每页展开。",
    ),
    SlideSpec(
        title="四道质量门全部通过",
        table=(
            ("质量门", "状态", "关键证据"),
            ("G0 本地基线", "✅ 通过", "60 项自动化测试全部绿色，可随时重跑"),
            ("G1 数据就绪", "✅ 通过（9-20）", "三物种 h5ad 上传后逐字节核对一致，标签列 celltype 三文件共有"),
            ("G2 环境核验", "✅ 通过（9-21，带三项记录例外）", "镜像内实测版本与页面一致；三项例外均有记录、责任人、截止条件"),
            ("G3 全组批准", "✅ 通过（9-21）", "批准材料含 kBET 方案对比与运行保险丝（单次限费限时）"),
        ),
        note="强调：每道门都有文档证据，例外也有记录和补证条件——不是“差不多就行”。",
    ),
    SlideSpec(
        title="数据就绪：三物种心脏图谱",
        table=(
            ("物种", "细胞数", "基因数", "文件", "大小"),
            ("人 Homo sapiens", "30,000", "32,732", "Homo_sapiens_sc.h5ad", "213 MB"),
            ("小鼠 Mus musculus", "60,471", "32,379", "Mus_musculus_sc.h5ad", "260 MB"),
            ("斑马鱼 Danio rerio", "50,000", "27,661", "Danio_rerio_sc.h5ad", "154 MB"),
        ),
        bullets=(
            "来源：课程指定的 HEART 心脏跨物种图谱（Science，CNP0006537）",
            "每个文件都带“标准答案”列 celltype（12 类细胞，如心肌细胞、成纤维细胞）",
            "上传后文件名、大小、可读性逐项核对；批次列按物种映射写进预检配置",
        ),
        note="强调“标准答案”概念：每个细胞已被专家标注类型，工具猜完对答案就算分。",
    ),
    SlideSpec(
        title="最大的障碍与突破：平台 notebook 打不开",
        process=("发现白屏", "定位原因", "官方确认", "自建通路"),
        bullets=(
            "现象：平台“个性分析”点开一直白屏，换网络、关代理都无效",
            "官方工单确认：该模块需要华大 VPN（校园网没有），属于公司安全策略，暂无解",
            "突破：发现平台“离线任务”通道走公网 API 就能提交脚本、读取结果——完全绕开白屏",
            "顺手建成 wheelhouse 离线装包通道：本地下载依赖包 → 上传 → 容器内安装",
        ),
        takeaway="要点：notebook 用不了，我们就自己修了一条完全公网可用的执行通路。",
        note="这一页是整个项目的转折点：之前被环境卡死，之后所有跑数都走这条路。",
    ),
    SlideSpec(
        title="镜像环境实测（不抄页面，进容器量）",
        table=(
            ("工具/组件", "页面声明", "容器内实测", "结论"),
            ("scvi-tools", "1.1.6.post2", "1.1.6.post2", "一致"),
            ("scanpy", "1.10.3", "1.10.3", "一致"),
            ("torch", "2.6.0 (CUDA 12.4)", "2.6.0+cu124", "一致"),
            ("SAMap", "1.0.1 或 1.0.16（页面矛盾）", "1.0.16", "以实测为准"),
            ("kBET（scib-metrics）", "无预装", "0.4.1 可用", "实测装上"),
        ),
        note="强调方法论：页面信息会自相矛盾，只有进容器量出来的才算数——这也是 G2 环境门存在的意义。",
    ),
    SlideSpec(
        title="首批基线结果：scVI 三物种",
        table=(
            ("物种", "细胞数", "KNN 分类准确率", "耗时"),
            ("人 Homo sapiens", "30,000", "98.38%", "68 秒"),
            ("小鼠 Mus musculus", "60,471", "98.12%", "129 秒"),
            ("斑马鱼 Danio rerio", "50,000", "92.51%", "275 秒"),
        ),
        bullets=(
            "统一协议：同样的预处理、同样的训练轮数、同样的评估方式、同一随机种子",
            "哺乳类两个物种接近 98%；斑马鱼低约 6 个百分点，与其红细胞占比高、类型更杂一致",
            "意义：这是三个工具对比的“第一行数据”，SATURN 和 SAMap 将按同协议补齐",
        ),
        note="解释准确率含义：把细胞压缩到低维空间后，让算法猜细胞类型，对答案算分。强调统一协议保证公平。",
    ),
    SlideSpec(
        title="SATURN：从装不上到训练跑通",
        process=("源码就位", "依赖补齐", "CUDA 补丁", "数据格式适配", "训练成功"),
        bullets=(
            "镜像里没有 SATURN 本体，且平台源缺包、容器编译器过老——逐项解决",
            "源码补丁：跳过写死的 CUDA 调用，让 CPU 节点也能训练（正式大跑仍可用 GPU）",
            "数据格式适配：物种清单 CSV + 每物种蛋白嵌入文件 + 高变基因参数",
            "冒烟结果：50 轮训练完整跑完、损失正常收敛、四个结果文件落盘",
        ),
        takeaway="要点：SATURN 是三个工具里环境最难的，现在训练入口已在平台容器内跑通。",
        note="说明“冒烟”含义：用小型合成数据验证全流程，确认代码能跑，再换真实数据。",
    ),
    SlideSpec(
        title="质量保障：怎么保证这些数字可信",
        table=(
            ("保障手段", "具体做法"),
            ("自动化测试", "60 项测试覆盖配置、流程、输出格式；每次改动全量重跑"),
            ("版本钉定", "所有软件版本进容器实测并记录，报告引用实测值"),
            ("全程留痕", "输入、参数、日志、结果存档在仓库，事后可查"),
            ("例外有账", "无法立即核验的三项，全部记录例外与补证条件，不悄悄放过"),
        ),
        note="回应“可复现”要求：任何一个数字都能追溯到一次具体的运行记录。",
    ),
    SlideSpec(
        title="下一步计划",
        process=("真实嵌入", "SATURN 全量", "SAMap 跑数", "统一评分"),
        bullets=(
            "下载官方 ESM2 基因嵌入（人/鼠/鱼），替换冒烟用的假数据",
            "SATURN 三物种正式训练：先小规模试跑，通过后再上全量（保险丝不变：限费限时）",
            "SAMap 按同协议出数；跨物种比较需要直系同源基因表，来源已锁定",
            "三方法 × 三物种矩阵填满后，统一脚本算分，写 Word 报告",
        ),
        takeaway="要点：通路已全部打通，剩下的是按既定协议把矩阵填满。",
        note="说明 GPU 使用计划：正式训练用单卡 GPU，保险丝仍为单次限费限时、到点即停。",
    ),
    SlideSpec(
        title="总结",
        bullets=(
            "数据：三物种心脏图谱就绪，标签齐全，逐字节校验",
            "环境：绕开平台白屏限制，自建离线执行与装包通路；三工具环境全部实测就位",
            "结果：scVI 三物种基线 98.38% / 98.12% / 92.51%；SATURN 训练入口跑通",
            "纪律：四道质量门 + 60 项测试 + 全程留痕，每个数字可追溯",
        ),
        takeaway="要点：方案变成了进展，流程变成了数字；下一阶段把矩阵填满、写出报告。",
        note="收尾回扣课程要求：可复现、有留痕、花钱有保险丝、全组可见。",
    ),
)


def _set_run(run, text, size, *, bold=False, color=DARK_TEXT):
    run.text = text
    run.font.name = FONT
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color


def _add_box(slide, text, left, top, width, height, size, *, fill=None, line=LINE, bold=False, color=DARK_TEXT, align=PP_ALIGN.LEFT):
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
    _set_run(run, text, size, bold=bold, color=color)
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


def _add_title(slide, title, subtitle=None):
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.55), Inches(0.48), Inches(0.13), Inches(0.58))
    bar.fill.solid()
    bar.fill.fore_color.rgb = TEAL
    bar.line.fill.background()
    _add_box(slide, title, 0.82, 0.42, 10.8, 0.55, 27, bold=True, color=NAVY, line=None)
    if subtitle:
        _add_box(slide, subtitle, 0.84, 0.97, 10.5, 0.32, 13, color=GRAY, line=None)


def _add_bullets(slide, bullets, top=1.48):
    if not bullets:
        return
    height = min(4.9, 0.42 + len(bullets) * 0.72)
    shape = slide.shapes.add_textbox(Inches(0.82), Inches(top), Inches(11.15), Inches(height))
    frame = shape.text_frame
    frame.clear()
    frame.word_wrap = True
    frame.margin_left = Inches(0.04)
    frame.margin_right = Inches(0.04)
    for index, item in enumerate(bullets):
        paragraph = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
        run = paragraph.add_run()
        _set_run(run, item, 17 if len(item) < 44 else 15)
        paragraph.space_after = Pt(15)
        paragraph.line_spacing = 1.28


def _add_takeaway(slide, text):
    band = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(5.68), Inches(13.333), Inches(1.0))
    band.fill.solid()
    band.fill.fore_color.rgb = LIGHT
    band.line.fill.background()
    shape = slide.shapes.add_textbox(Inches(0.82), Inches(5.82), Inches(11.7), Inches(0.72))
    frame = shape.text_frame
    frame.clear()
    frame.word_wrap = True
    paragraph = frame.paragraphs[0]
    run = paragraph.add_run()
    _set_run(run, text, 15, bold=True, color=NAVY)


def _table_widths(columns):
    if columns == 3:
        return (2.6, 3.6, 4.7)
    if columns == 4:
        return (3.2, 2.0, 3.4, 2.3)
    return (10.9 / columns,) * columns


def _add_table(slide, rows):
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
            _set_run(run, value, 12 if row_index == 0 else 11, bold=row_index == 0, color=WHITE if row_index == 0 else DARK_TEXT)


def _add_process(slide, steps):
    left = 0.72
    top = 1.52
    width = min(1.42, 10.9 / len(steps) - 0.16)
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
        _set_run(run, step, 10.5, bold=True, color=WHITE)
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


def _add_footer(slide, number):
    _add_box(slide, "课题5 | 跨物种单细胞整合工具评测", 0.75, 7.02, 5.0, 0.25, 9, color=GRAY, line=None)
    _add_box(slide, str(number), 11.7, 7.02, 0.45, 0.25, 9, color=GRAY, line=None, align=PP_ALIGN.RIGHT)


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
            _add_box(slide, spec.title, 0.85, 1.95, 10.6, 1.0, 34, bold=True, color=NAVY, line=None)
            if spec.subtitle:
                _add_box(slide, spec.subtitle, 0.88, 2.95, 9.8, 0.45, 18, color=TEAL, line=None)
            _add_bullets(slide, spec.bullets, top=3.75)
        else:
            _add_title(slide, spec.title, spec.subtitle)
            if spec.process:
                _add_process(slide, spec.process)
            if spec.table:
                _add_table(slide, spec.table)
            if spec.takeaway:
                _add_takeaway(slide, spec.takeaway)
            bullets_top = 2.35 if spec.process else (1.75 if spec.takeaway else 1.48)
            if not spec.table:
                _add_bullets(slide, spec.bullets, top=bullets_top)
            elif spec.bullets:
                _add_bullets(slide, spec.bullets, top=4.95)
        if spec.note:
            slide.notes_slide.notes_text_frame.text = spec.note
        _add_footer(slide, index)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    presentation.save(OUTPUT)
    return OUTPUT


if __name__ == "__main__":
    print(build())
