const pptxgen = require("pptxgenjs");

// ── 调色板（主题：生命科学/基因组，深青绿主导 + 琥珀强调） ──
const BG = "FFFFFF";
const DARK = "0B3D3A";        // 深青绿（标题/收尾页背景）
const PRIMARY = "0D9488";     // 主青绿
const PRIMARY_L = "5EEAD4";   // 浅青绿（暗底上的次级）
const ACCENT = "D97706";      // 琥珀（关键数字/高亮）
const TEXT = "1E293B";
const MUTED = "64748B";
const LIGHT_TINT = "F0FDFA";  // 极浅青绿底

const F = "微软雅黑";

let p = new pptxgen();
p.layout = "LAYOUT_WIDE";
p.author = "课题5";
p.title = "课题5 第一阶段成果汇报";

const W = 13.33, H = 7.5, M = 0.6;

// ── S1 封面（深底） ──
let s = p.addSlide();
s.background = { color: DARK };
s.addText("课题5 第一阶段成果汇报", { x: M, y: 2.1, w: W - 2 * M, h: 1.1, fontSize: 48, bold: true, color: "FFFFFF", fontFace: F, align: "center" });
s.addText("跨物种心脏单细胞基准：三方法统一评估", { x: M, y: 3.3, w: W - 2 * M, h: 0.7, fontSize: 24, color: PRIMARY_L, fontFace: F, align: "center" });
s.addText("人 1,528 · 鼠 1,535 · 斑马鱼 1,543 细胞   |   真实 ESM2 蛋白嵌入   |   可审计统一评分协议", { x: M, y: 4.15, w: W - 2 * M, h: 0.5, fontSize: 16, color: "B8D8D4", fontFace: F, align: "center" });
s.addText("2026-09-29", { x: M, y: 6.6, w: W - 2 * M, h: 0.4, fontSize: 14, color: "7FB8B3", fontFace: F, align: "center" });

// ── S2 评估体系总览 ──
s = p.addSlide();
s.background = { color: BG };
s.addText("评估体系：三种方法，一把尺子", { x: M, y: 0.4, w: W - 2 * M, h: 0.7, fontSize: 32, bold: true, color: TEXT, fontFace: F });
const cards = [
  { t: "SATURN", d: "蛋白语言模型嵌入\n宏基因三元组训练\nDCS 平台 1,000 宏基因正式训练", c: PRIMARY },
  { t: "SAMap", d: "同源图联合嵌入\nv1.0.16 本地全管线\n规则合规重跑", c: "0F766E" },
  { t: "ortholog-PCA（本项目引入）", d: "1:1 直系同源基因\nPCA50 · 零整合基线\n用于校准 SOTA 的真实水平", c: ACCENT },
];
cards.forEach((c, i) => {
  const cw = 3.9, gap = 0.35, x = M + i * (cw + gap);
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y: 1.5, w: cw, h: 2.6, fill: { color: LIGHT_TINT }, rectRadius: 0.08, line: { color: "CCFBF1", width: 1 } });
  s.addText(c.t, { x: x + 0.25, y: 1.7, w: cw - 0.5, h: 0.5, fontSize: 20, bold: true, color: c.c === ACCENT ? "92400E" : DARK, fontFace: F });
  s.addText(c.d, { x: x + 0.25, y: 2.3, w: cw - 0.5, h: 1.6, fontSize: 14, color: TEXT, fontFace: F, lineSpacingMultiple: 1.2 });
});
s.addText([
  { text: "统一评分协议：", options: { bold: true, color: DARK } },
  { text: "KNN15 倒距离加权 · cosine · 冻结映射表 v1（38 行，人工锚定+数据验证） · 200 次置换检验 · 逐细胞预测与混淆矩阵留痕 · 全流程 SHA-256 溯源", options: { color: TEXT } },
], { x: M, y: 4.5, w: W - 2 * M, h: 0.9, fontSize: 16, fontFace: F });
s.addText([
  { text: "输入：", options: { bold: true, color: DARK } },
  { text: "三物种心脏单细胞（分层采样，seed=0）· 真实 ESM2 蛋白嵌入 · 冻结映射表排除 74 个低质量细胞并单列 coverage", options: { color: TEXT } },
], { x: M, y: 5.5, w: W - 2 * M, h: 0.8, fontSize: 16, fontFace: F });
s.addText("全部数字可由机器可读产物复算；91+ 单元测试守护工具链", { x: M, y: 6.6, w: W - 2 * M, h: 0.4, fontSize: 13, color: MUTED, fontFace: F });

// ── S3 核心数字总表 ──
s = p.addSlide();
s.background = { color: BG };
s.addText("核心数字：六方向 × 三方法（coarse 粒度）", { x: M, y: 0.4, w: W - 2 * M, h: 0.7, fontSize: 32, bold: true, color: TEXT, fontFace: F });
const th = { fill: { color: DARK }, color: "FFFFFF", bold: true, fontFace: F, fontSize: 14, align: "center", valign: "middle" };
const td = { fontFace: F, fontSize: 14, align: "center", valign: "middle", color: TEXT };
const hl = { fill: { color: "FEF3C7" }, bold: true, color: "92400E" };
const dim = { color: MUTED };
const tbl = [
  [{ text: "方向", options: th }, { text: "ortholog-PCA", options: th }, { text: "SATURN", options: th }, { text: "SAMap", options: th }, { text: "majority", options: th }],
  [{ text: "人 → 鼠", options: { ...td, bold: true } }, { text: "80.9%", options: { ...td, ...hl } }, { text: "61.8%", options: { ...td, ...hl } }, { text: "≈2%", options: { ...td, ...dim } }, { text: "48.2%", options: td }],
  [{ text: "鼠 → 人", options: td }, { text: "38.3%", options: { ...td, ...hl } }, { text: "25.4%", options: { ...td, ...dim } }, { text: "17.2%", options: { ...td, ...dim } }, { text: "31.2%", options: td }],
  [{ text: "人 → 斑马鱼", options: td }, { text: "40.5%", options: { ...td, ...hl } }, { text: "17.8%", options: { ...td, ...dim } }, { text: "≈0%", options: { ...td, ...dim } }, { text: "38.6%", options: td }],
  [{ text: "鼠 → 斑马鱼", options: td }, { text: "22.4%", options: { ...td, ...dim } }, { text: "30.1%", options: { ...td, ...hl } }, { text: "≈39%(=基线)", options: { ...td, ...dim } }, { text: "38.6%", options: td }],
  [{ text: "斑马鱼 → 人", options: td }, { text: "11.9%", options: { ...td, ...dim } }, { text: "≈2%", options: { ...td, ...dim } }, { text: "≈0%", options: { ...td, ...dim } }, { text: "31.2%", options: td }],
  [{ text: "斑马鱼 → 鼠", options: td }, { text: "79.5%", options: { ...td, ...hl } }, { text: "≈2%", options: { ...td, ...dim } }, { text: "≈2%", options: { ...td, ...dim } }, { text: "47.2%", options: td }],
];
s.addTable(tbl, { x: M, y: 1.3, w: W - 2 * M, colW: [2.4, 2.6, 2.6, 2.6, 2.0], rowH: 0.52, border: { pt: 0.5, color: "CBD5E1" } });
s.addText("金色 = 显著超过该方向 majority 基线且为行内最优　|　灰 = 低于 majority（≤ 常数预测器）", { x: M, y: 5.35, w: W - 2 * M, h: 0.4, fontSize: 13, color: MUTED, fontFace: F });
s.addText([
  { text: "读法：", options: { bold: true, color: DARK } },
  { text: "仅有 人→鼠 一个方向，两种整合方法同时显著超过 majority；朴素基线 ortholog-PCA 在 4/6 方向领先两种 SOTA 方法。", options: { color: TEXT } },
], { x: M, y: 5.9, w: W - 2 * M, h: 0.8, fontSize: 16, fontFace: F });
s.addText("协议：transductive_formal_reassessment（非 inductive / 非 held-out）· 全部 shuffle_p 可查", { x: M, y: 6.75, w: W - 2 * M, h: 0.4, fontSize: 12, color: MUTED, fontFace: F });

// ── S4 发现1：基线反超（分组柱状图） ──
s = p.addSlide();
s.background = { color: BG };
s.addText("发现 1：朴素基线在多数方向领先 SOTA", { x: M, y: 0.4, w: W - 2 * M, h: 0.7, fontSize: 32, bold: true, color: TEXT, fontFace: F });
s.addChart(p.charts.BAR, [
  { name: "ortholog-PCA（零整合基线）", labels: ["人→鼠", "鼠→人", "人→鱼", "鼠→鱼", "鱼→人", "鱼→鼠"], values: [80.9, 38.3, 40.5, 22.4, 11.9, 79.5] },
  { name: "SATURN", labels: ["人→鼠", "鼠→人", "人→鱼", "鼠→鱼", "鱼→人", "鱼→鼠"], values: [61.8, 25.4, 17.8, 30.1, 24.7, 46.5] },
], {
  x: M, y: 1.25, w: W - 2 * M, h: 4.3, barDir: "col", barGapWidthPct: 60,
  chartColors: [ACCENT, PRIMARY],
  chartArea: { fill: { color: "FFFFFF" } },
  catAxisLabelColor: MUTED, catAxisLabelFontSize: 13, catAxisLabelFontFace: F,
  valAxisLabelColor: MUTED, valAxisLabelFontSize: 12, valAxisMaxVal: 100, valAxisMinVal: 0,
  valGridLine: { color: "E2E8F0", size: 0.5 }, catGridLine: { style: "none" },
  showValue: true, dataLabelPosition: "outEnd", dataLabelColor: TEXT, dataLabelFontSize: 11, dataLabelFontFace: F,
  showLegend: true, legendPos: "t", legendColor: TEXT, legendFontSize: 13, legendFontFace: F,
});
s.addText("要点：零整合的直系同源基因 PCA（琥珀色）在 人→鼠、鼠→人、人→鱼、鱼→鼠 四个方向领先；两个跨鱼方向对所有方法都困难——对齐信号在远缘物种间普遍衰减。", { x: M, y: 5.75, w: W - 2 * M, h: 0.9, fontSize: 15, color: TEXT, fontFace: F });
s.addText("数字：v97g 规则合规协议（coarse）；PCA 数字来自同协议 ortholog-PCA50。", { x: M, y: 6.7, w: W - 2 * M, h: 0.35, fontSize: 12, color: MUTED, fontFace: F });

// ── S5 发现2：消融 ──
s = p.addSlide();
s.background = { color: BG };
s.addText("发现 2：SATURN 的蛋白嵌入增益是真实的", { x: M, y: 0.4, w: W - 2 * M, h: 0.7, fontSize: 32, bold: true, color: TEXT, fontFace: F });
s.addText("消融实验：打乱“基因-嵌入”对应关系（保留真实向量分布），其余协议完全不变", { x: M, y: 1.2, w: W - 2 * M, h: 0.5, fontSize: 17, color: MUTED, fontFace: F });
s.addText("61.8%", { x: 1.2, y: 2.3, w: 4.2, h: 1.5, fontSize: 88, bold: true, color: PRIMARY, fontFace: F, align: "center" });
s.addText("真实 ESM2 嵌入\nhuman→mouse (coarse)", { x: 1.2, y: 3.9, w: 4.2, h: 0.9, fontSize: 17, color: TEXT, fontFace: F, align: "center" });
s.addText("→", { x: 5.7, y: 2.6, w: 1.6, h: 1.0, fontSize: 54, bold: true, color: MUTED, fontFace: F, align: "center" });
s.addText("20.4%", { x: 7.6, y: 2.3, w: 4.2, h: 1.5, fontSize: 88, bold: true, color: "94A3B8", fontFace: F, align: "center" });
s.addText("置换嵌入（对照）\n≈ 回落到随机水平", { x: 7.6, y: 3.9, w: 4.2, h: 0.9, fontSize: 17, color: TEXT, fontFace: F, align: "center" });
s.addShape(p.shapes.LINE, { x: M, y: 5.2, w: W - 2 * M, h: 0, line: { color: "E2E8F0", width: 1 } });
s.addText([
  { text: "结论：", options: { bold: true, color: DARK } },
  { text: "SATURN 在哺乳动物对的增益确实来自真实的蛋白同源信号，不是降维副产物——审稿人必问的对照，我们有了干净答案。", options: { color: TEXT } },
], { x: M, y: 5.5, w: W - 2 * M, h: 1.0, fontSize: 17, fontFace: F });

// ── S6 发现3：容量效应 ──
s = p.addSlide();
s.background = { color: BG };
s.addText("发现 3：宏基因容量是决定性超参数", { x: M, y: 0.4, w: W - 2 * M, h: 0.7, fontSize: 32, bold: true, color: TEXT, fontFace: F });
s.addText("3.4%", { x: 1.0, y: 2.2, w: 3.3, h: 1.3, fontSize: 72, bold: true, color: "94A3B8", fontFace: F, align: "center" });
s.addText("16 宏基因\n（烟测配置）", { x: 1.0, y: 3.6, w: 3.3, h: 0.8, fontSize: 16, color: TEXT, fontFace: F, align: "center" });
s.addChart(p.charts.LINE, [{ name: " capacity", labels: ["16", "", "", "", "1000"], values: [3.4, 12, 30, 48, 61.8] }], {
  x: 4.6, y: 1.8, w: 4.2, h: 3.4, lineSize: 0, lineDataSymbol: "circle", lineDataSymbolSize: 10,
  chartColors: [PRIMARY], catAxisLabelColor: MUTED, valAxisLabelColor: MUTED,
  valAxisMaxVal: 80, valAxisMinVal: 0, showLegend: false, showValue: false,
  catAxisTitle: "macrogenes", showCatAxisTitle: true, catAxisTitleColor: MUTED, catAxisTitleFontSize: 12,
  valGridLine: { color: "E2E8F0", size: 0.5 },
});
s.addText("61.8%", { x: 9.0, y: 2.2, w: 3.3, h: 1.3, fontSize: 72, bold: true, color: PRIMARY, fontFace: F, align: "center" });
s.addText("1,000 宏基因\n（论文默认配置）", { x: 9.0, y: 3.6, w: 3.3, h: 0.8, fontSize: 16, color: TEXT, fontFace: F, align: "center" });
s.addText("17×", { x: 8.4, y: 1.5, w: 1.4, h: 0.8, fontSize: 30, bold: true, color: ACCENT, fontFace: F });
s.addShape(p.shapes.LINE, { x: M, y: 4.8, w: W - 2 * M, h: 0, line: { color: "E2E8F0", width: 1 } });
s.addText([
  { text: "含义：", options: { bold: true, color: DARK } },
  { text: "SATURN 类方法的跨物种能力对宏基因容量极度敏感；文献默认值 1,000 并非可有可无的细节。中段曲线为示意图（两端为实测锚点）。", options: { color: TEXT } },
], { x: M, y: 5.1, w: W - 2 * M, h: 1.0, fontSize: 16, fontFace: F });
s.addText("注：16→1000 两点均为实测；中间连线仅示意趋势，非逐点测量。", { x: M, y: 6.3, w: W - 2 * M, h: 0.35, fontSize: 12, color: MUTED, fontFace: F });

// ── S7 发现4：seed 双峰 ──
s = p.addSlide();
s.background = { color: BG };
s.addText("发现 4：远缘方向对随机种子剧烈敏感", { x: M, y: 0.4, w: W - 2 * M, h: 0.7, fontSize: 32, bold: true, color: TEXT, fontFace: F });
s.addText("同一配置、仅换 seed（coarse，SATURN human→mouse 稳定 / zebrafish→mouse 双峰）", { x: M, y: 1.2, w: W - 2 * M, h: 0.5, fontSize: 17, color: MUTED, fontFace: F });
const seedRows = [
  [{ text: "seed", options: th }, { text: "human→mouse", options: th }, { text: "zebrafish→mouse", options: th }],
  [{ text: "0", options: td }, { text: "67.4%", options: td }, { text: "11.3%", options: td }],
  [{ text: "1", options: td }, { text: "71.5%", options: td }, { text: "48.8%", options: { ...td, ...hl } }],
  [{ text: "2", options: td }, { text: "62.3%", options: td }, { text: "8.3%", options: td }],
  [{ text: "均值±SD", options: { ...td, bold: true } }, { text: "67.1 ± 3.8", options: { ...td, bold: true } }, { text: "双峰分布", options: { ...td, bold: true, color: "B91C1C" } }],
];
s.addTable(seedRows, { x: M, y: 1.9, w: 7.2, colW: [1.6, 2.8, 2.8], rowH: 0.5, border: { pt: 0.5, color: "CBD5E1" } });
s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 8.3, y: 1.9, w: 4.5, h: 2.9, fill: { color: LIGHT_TINT }, rectRadius: 0.08 });
s.addText([
  { text: "解读\n", options: { bold: true, fontSize: 17, color: DARK } },
  { text: "远缘方向的结果呈双峰：单一运行报告的鱼方向数字不可信。人→鼠方向稳定（±3.8pp），适合作为主结论。", options: { fontSize: 14, color: TEXT } },
], { x: 8.55, y: 2.1, w: 4.0, h: 2.5, fontFace: F });
s.addText([
  { text: "对报告的约束：", options: { bold: true, color: DARK } },
  { text: "凡涉鱼方向的结论必须报告多 seed 分布，单次运行不进入正文表格。", options: { color: TEXT } },
], { x: M, y: 5.3, w: W - 2 * M, h: 0.7, fontSize: 16, fontFace: F });

// ── S8 物种内 ceiling ──
s = p.addSlide();
s.background = { color: BG };
s.addText("物种内 ceiling：把“潜空间质量”与“跨物种对齐”分开归因", { x: M, y: 0.4, w: W - 2 * M, h: 0.7, fontSize: 30, bold: true, color: TEXT, fontFace: F });
s.addChart(p.charts.BAR, [
  { name: "SATURN 潜空间（物种内 50/50）", labels: ["human", "mouse", "zebrafish"], values: [85.5, 93.5, 74.2] },
  { name: "scVI 基线", labels: ["human", "mouse", "zebrafish"], values: [98.4, 98.1, 92.5] },
], {
  x: M, y: 1.3, w: 7.4, h: 4.4, barDir: "col", barGapWidthPct: 80,
  chartColors: [PRIMARY, "94A3B8"],
  catAxisLabelColor: MUTED, catAxisLabelFontSize: 14, catAxisLabelFontFace: F,
  valAxisLabelColor: MUTED, valAxisMaxVal: 100, valAxisMinVal: 0,
  valGridLine: { color: "E2E8F0", size: 0.5 }, catGridLine: { style: "none" },
  showValue: true, dataLabelPosition: "outEnd", dataLabelColor: TEXT, dataLabelFontSize: 12,
  showLegend: true, legendPos: "t", legendColor: TEXT, legendFontSize: 13,
});
s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 8.4, y: 1.4, w: 4.4, h: 4.1, fill: { color: LIGHT_TINT }, rectRadius: 0.08 });
s.addText([
  { text: "归因分解\n", options: { bold: true, fontSize: 17, color: DARK } },
  { text: "跨物种掉分 = 潜空间质量损失 + 跨物种对齐损失\n\n", options: { fontSize: 14, color: TEXT } },
  { text: "SATURN 潜空间本身已比 scVI 低 5–18pp；再叠加跨物种对齐损失，才得到最终 60.6%。\n\n", options: { fontSize: 14, color: TEXT } },
  { text: "这两个因素此前从未被分开度量。", options: { bold: true, fontSize: 14, color: DARK } },
], { x: 8.65, y: 1.6, w: 3.9, h: 3.7, fontFace: F, lineSpacingMultiple: 1.15 });
s.addText("协议：同物种 50/50 分半、KNN15，与跨物种评估完全一致。", { x: M, y: 6.0, w: W - 2 * M, h: 0.35, fontSize: 12, color: MUTED, fontFace: F });

// ── S9 工程资产 ──
s = p.addSlide();
s.background = { color: BG };
s.addText("工程与流程资产：让每个数字可复算", { x: M, y: 0.4, w: W - 2 * M, h: 0.7, fontSize: 32, bold: true, color: TEXT, fontFace: F });
const assets = [
  ["DCS 离线通道全线打通", "任务提交/取消/日志/哈希溯源 API 化；AES 加密直连提交；1c4g 免费档全流程复现"],
  ["统一评分器 + 显式 bundle", "NPZ 显式表示层输入，无隐式回退；逐细胞预测、混淆矩阵、角色表留痕"],
  ["冻结映射表 v1", "38 行双层 coarse/fine；文献锚定 + 1:1 ortholog pseudobulk 验证（人鼠 8/8 进 top5）"],
  ["统计纪律", "每个数字带 majority 基线 + 200 次置换经验 p 值 + bootstrap CI；多重实现交叉验证（人鼠四位小数吻合）"],
];
assets.forEach((a, i) => {
  const y = 1.4 + i * 1.25;
  s.addText(String(i + 1).padStart(2, "0"), { x: M, y: y, w: 0.8, h: 0.8, fontSize: 30, bold: true, color: PRIMARY, fontFace: F });
  s.addText(a[0], { x: 1.6, y: y, w: 10.8, h: 0.45, fontSize: 19, bold: true, color: TEXT, fontFace: F });
  s.addText(a[1], { x: 1.6, y: y + 0.45, w: 10.8, h: 0.55, fontSize: 14, color: MUTED, fontFace: F });
  if (i < assets.length - 1) s.addShape(p.shapes.LINE, { x: 1.6, y: y + 1.08, w: 10.8, h: 0, line: { color: "E2E8F0", width: 0.75 } });
});

// ── S10 下一步 ──
s = p.addSlide();
s.background = { color: BG };
s.addText("下一阶段计划", { x: M, y: 0.4, w: W - 2 * M, h: 0.7, fontSize: 32, bold: true, color: TEXT, fontFace: F });
const next = [
  ["映射表 reviewer 签认", "签名请求稿已备好，等导师/组内确认（映射表 v1 已冻结 SHA-256）"],
  ["v99 provenance 回收", "只读任务已提交：命令、哈希、逐细胞预测、混淆矩阵全量回收"],
  ["inductive 留出重训", "门控中：留一物种 / 分层留出，把“正式泛化基准”立起来（最小版 = 3 次训练）"],
  ["统一比较矩阵冻结 → 报告", "SATURN/SAMap/PCA 同表，协议标签 + 证据等级分列，先冻 Markdown 再出 Word"],
];
next.forEach((a, i) => {
  const y = 1.5 + i * 1.15;
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: M, y: y, w: 0.85, h: 0.85, fill: { color: DARK }, rectRadius: 0.06 });
  s.addText(String(i + 1), { x: M, y: y, w: 0.85, h: 0.85, fontSize: 26, bold: true, color: PRIMARY_L, fontFace: F, align: "center", valign: "middle" });
  s.addText(a[0], { x: 1.7, y: y + 0.02, w: 11.0, h: 0.45, fontSize: 19, bold: true, color: TEXT, fontFace: F });
  s.addText(a[1], { x: 1.7, y: y + 0.47, w: 11.0, h: 0.4, fontSize: 14, color: MUTED, fontFace: F });
});

// ── S11 收尾（深底） ──
s = p.addSlide();
s.background = { color: DARK };
s.addText("一句话结论", { x: M, y: 1.4, w: W - 2 * M, h: 0.6, fontSize: 20, color: PRIMARY_L, fontFace: F, align: "center" });
s.addText("跨物种对齐信号主要由直系同源基因携带；\nSOTA 整合方法有真实但有限的蛋白嵌入增益，\n且在远缘物种间普遍失效。", { x: 1.5, y: 2.3, w: W - 3, h: 2.4, fontSize: 30, bold: true, color: "FFFFFF", fontFace: F, align: "center", lineSpacingMultiple: 1.3 });
s.addText("全部数字可复算 · 全部结论有对照 · 全部产物可溯源", { x: M, y: 5.3, w: W - 2 * M, h: 0.5, fontSize: 17, color: PRIMARY_L, fontFace: F, align: "center" });
s.addText("课题5 · 2026-09-29", { x: M, y: 6.6, w: W - 2 * M, h: 0.4, fontSize: 14, color: "7FB8B3", fontFace: F, align: "center" });

p.writeFile({ fileName: "D:/projects/course5-prep/results/pilot-v1/课题5第一阶段成果汇报.pptx" }).then(() => console.log("PPTX_DONE"));
