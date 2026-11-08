// 课题5 第 2/7 次汇报：数字来源链
// 版式：康复大学校模板（results/stage-reports-20261009/lib/report-template.js）
// 结构：纠偏引子（1 页）+ 数字来源链主体（5 页）+ 结果与计划（2 页）
const path = require('path');
const T = require(path.resolve(__dirname, '..', 'stage-reports-20261009', 'lib', 'report-template.js'));
const pptxgen = require('pptxgenjs');
const { newDeck, cover, chrome, box, band, table, notes, C, F, W, H } = T;

const OUT = 'D:/projects/course5-prep/results/stage-reports-20261019/课题5第02次汇报_数字来源链_校模板.pptx';
const pptx = newDeck({ title: '课题5 第2次汇报：数字来源链' });

// ---------------- 1 封面 ----------------
cover(pptx, {
  title: '课题5 第 2 次汇报：数字来源链',
  subtitle: '一个百分比是怎么来的 —— 从原始细胞到表格单元格的可复核路径',
  meta: '2026-10-19 ｜ 7 次汇报中的第 2 次 ｜ 口径：transductive / in-sample ｜ 单 seed（0）',
});

// ---------------- 2 任务定位与进度 ----------------
let s = pptx.addSlide();
chrome(s, '任务定位：本次讲的是哪一块', 2);
s.addText('课程原题', { x: 0.67, y: 1.70, w: 2.0, h: 0.26, fontFace: F, fontSize: 10.5, bold: true, color: C.muted, margin: 0 });
s.addText('跨物种单细胞整合：SATURN vs SAMap vs scVI 系的基准测试与场景化选型',
  { x: 0.67, y: 1.94, w: 11.98, h: 0.40, fontFace: F, fontSize: 16, bold: true, color: C.title, margin: 0, fit: 'shrink' });

table(s, [
  ['课程要求', '状态'],
  ['四方法对比（含自建 oPCA 基线）', '已完成'],
  ['主指标 macro-F1（统一口径）', '已完成'],
  ['场景：近缘 + 无 GPU', '已完成'],
  ['批次混合与生物保守性', '进行中（scVI 已测）'],
  ['时间与内存', '进行中（scVI 已测）'],
  ['场景：跨门（七鳃鳗 ↔ 鼠）', '未开始（数据已定位）'],
  ['文档 / Agent 友好度 + 容器化', '未开始'],
], 0.67, 2.52, 7.5, [5.3, 2.2], 0.415, 11.5);

// progress: 3 done / 2 ongoing / 2 not started
const px = 8.55, py = 2.52, pw = 4.05, seg = pw / 7;
const states = ['done','done','done','half','half','todo','todo'];
const cols = { done: '1F7A4D', half: 'FFC000', todo: 'DCE3E8' };
states.forEach((st, i) => {
  s.addShape('rect', { x: px + i * seg + 0.03, y: py, w: seg - 0.06, h: 0.30, fill: { color: cols[st] }, line: { color: cols[st] } });
});
s.addText('3 / 7 完成', { x: px, y: py + 0.42, w: pw, h: 0.34, fontFace: F, fontSize: 18, bold: true, color: '1F7A4D', margin: 0 });
s.addText('2 项进行中 · 2 项未开始', { x: px, y: py + 0.8, w: pw, h: 0.28, fontFace: F, fontSize: 10.5, color: C.muted, margin: 0 });

s.addShape('rect', { x: 8.55, y: 4.05, w: 4.05, h: 1.5, fill: { color: C.blueLight }, line: { color: C.line, width: 1 } });
s.addText('本次覆盖', { x: 8.72, y: 4.17, w: 3.7, h: 0.28, fontFace: F, fontSize: 11, bold: true, color: C.blue, margin: 0 });
s.addText('第 2 项「主指标」的底层：一个百分比是怎么算出来的', { x: 8.72, y: 4.47, w: 3.7, h: 1.0, fontFace: F, fontSize: 12.5, bold: true, color: C.title, margin: 0, fit: 'shrink' });

s.addText('下次覆盖第 1 项与第 6 项的边界问题：为什么不能排冠军。', { x: 0.67, y: 6.03, w: 11.98, h: 0.3, fontFace: F, fontSize: 11, color: C.muted, margin: 0, fit: 'shrink' });
band(s, '先说清“讲的是哪一块、做到哪一步”，再进内容——避免每页都在解释上下文', 6.45);

// ---------------- 3 纠偏引子 ----------------
s = pptx.addSlide();
chrome(s, '老师反馈之后：先改交付物类型', 3);

const rows2 = [
  ['老师说的「偏」', '不是数字不准，而是整份材料回答错了问题——在讲“证据可不可信”，没讲“哪个方法该在什么场景用”。', C.roseLight, 'C00000'],
  ['根因', '交付物类型错了：课程要的是「场景 → 方法 → 指标 → 选型」的基准报告，我们交的是审计报告。', C.goldLight, '8A4B00'],
  ['本次怎么改', '保留证据链（它是对的），但把它从“全部篇幅”降为“支撑材料”；主线回到方法与场景。', C.greenLight, '1F6B3A'],
];
let yy = 1.85;
for (const [k, v, fill, col] of rows2) {
  s.addShape('rect', { x: 0.67, y: yy, w: 12.0, h: 1.18, fill: { color: fill }, line: { color: fill } });
  s.addText(k, { x: 0.9, y: yy + 0.42, w: 2.1, h: 0.34, fontFace: F, fontSize: 15, bold: true, color: col, margin: 0 });
  s.addText(v, { x: 3.0, y: yy + 0.12, w: 9.4, h: 0.94, fontFace: F, fontSize: 12.5, color: C.text, margin: 0, valign: 'middle', fit: 'shrink' });
  yy += 1.32;
}
s.addText('本次先补上“数字怎么来的”这一层，把可信度做成可复核的底子；下一次再讲“为什么不能排冠军”。',
  { x: 0.67, y: 5.9, w: 12.0, h: 0.5, fontFace: F, fontSize: 13, bold: true, color: C.title, margin: 0 });
band(s, '口径不变：所有数字都是 transductive / in-sample，不是留出评估', 6.45);

// ---------------- 3 来源链 ----------------
s = pptx.addSlide();
chrome(s, '从原始细胞到表格单元格：八个环节', 4);
const steps = [
  ['原始 h5ad', '三物种心脏单细胞'],
  ['归一化', 'normalize_total(1e4)+log1p'],
  ['表示层', '同源交集 + PCA-50'],
  ['角色划分', 'src=reference，tgt=query'],
  ['KNN15', 'cosine，倒距离加权'],
  ['逐细胞预测', '含 confidence 与排除原因'],
  ['排除与计数', 'correct / eligible = n_q'],
  ['metrics.json', 'SHA-256 锚定'],
];
const colw = 3.0, x0 = 0.67, y0 = 1.75, rowh = 1.55;
steps.forEach(([k, v], i) => {
  const r = Math.floor(i / 4), c = i % 4;
  const x = x0 + c * colw, y = y0 + r * rowh;
  s.addShape('ellipse', { x: x, y: y, w: 0.42, h: 0.42, fill: { color: C.blueLight }, line: { color: C.line, width: 0.75 } });
  s.addText(String(i + 1), { x: x, y: y + 0.05, w: 0.42, h: 0.32, fontFace: F, fontSize: 12, bold: true, color: C.blue, align: 'center', margin: 0 });
  s.addText(k, { x: x + 0.54, y: y - 0.02, w: colw - 0.7, h: 0.32, fontFace: F, fontSize: 15, bold: true, color: C.title, margin: 0 });
  s.addText(v, { x: x + 0.54, y: y + 0.3, w: colw - 0.7, h: 0.6, fontFace: F, fontSize: 10.5, color: C.muted, margin: 0, fit: 'shrink' });
  if (c < 3) {
    s.addShape('rightArrow', { x: x + colw - 0.42, y: y + 0.13, w: 0.26, h: 0.16, fill: { color: 'C3D2D7' }, line: { color: 'C3D2D7' } });
  }
});
s.addText('换掉任何一环的定义，最终百分比就会变——所以复核必须沿这条链走，而不是从表里抄数。',
  { x: 0.67, y: 4.95, w: 12.0, h: 0.4, fontFace: F, fontSize: 13.5, bold: true, color: C.title, margin: 0 });
s.addText('每一环都有落盘物：输入 h5ad、映射表、脚本 SHA、逐细胞预测、metrics.json。第三方可以据此重算任意一个单元格。',
  { x: 0.67, y: 5.42, w: 12.0, h: 0.7, fontFace: F, fontSize: 11.5, color: C.text, margin: 0, fit: 'shrink' });
band(s, '对应脚本 ortholog_pca_dcs_v3_fixkey.py ｜ 产物 results/phase-20261010/opca-fixkey-recovered-20261015/', 6.45);

// ---------------- 4 实例拆解 ----------------
s = pptx.addSlide();
chrome(s, '实例拆解：86.18% = 1,297 ÷ 1,505', 5);
table(s, [
  ['环节', '内容', '取值'],
  ['输入', 'reference = 人 ｜ query = 鼠', '1,528 / 1,535'],
  ['同源基因', '人鼠 1:1 直系同源交集', '15,869'],
  ['表示层', '人+鼠联合 PCA-50（seed 0）', '3,063 × 50'],
  ['评分', 'KNN15，cosine，倒距离加权', 'k = 15'],
  ['排除', '鼠侧 status ≠ active', '剔 30'],
  ['eligible query', '1,535 − 30', 'n_q = 1,505'],
  ['正确数', '逐细胞预测 == 真值', '1,297'],
], 0.67, 1.75, 8.4, [1.7, 4.5, 2.2], 0.44, 11.5);

s.addText('accuracy', { x: 9.35, y: 1.9, w: 3.3, h: 0.3, fontFace: F, fontSize: 11.5, bold: true, color: C.muted, align: 'center', margin: 0 });
s.addText('0.8618', { x: 9.35, y: 2.2, w: 3.3, h: 1.0, fontFace: F, fontSize: 48, bold: true, color: 'C00000', align: 'center', margin: 0 });
s.addText('正确预测数 ÷ 排除后仍有资格的 query 细胞', { x: 9.35, y: 3.25, w: 3.3, h: 0.7, fontFace: F, fontSize: 10.5, color: C.muted, align: 'center', margin: 0, fit: 'shrink' });
s.addText('不是从表里抄出来的', { x: 9.35, y: 4.05, w: 3.3, h: 0.3, fontFace: F, fontSize: 10.5, bold: true, color: C.muted, align: 'center', margin: 0 });
s.addText('逐类分解（confusion 摘录）：内皮 720/725、成纤维 255/360、免疫 197/202、心肌 19/47；错误集中在成纤维→平滑肌（82）与心肌→内皮（27）。',
  { x: 0.67, y: 5.5, w: 12.0, h: 0.8, fontFace: F, fontSize: 11, color: C.text, margin: 0, fit: 'shrink' });
band(s, '主源 results/pilot-v1/ortholog-pca-v98/metrics.json ｜ SHA b2b3ac6b…c725 ｜ 本地已独立复算', 6.45);

// ---------------- 5 分母与四个量 ----------------
s = pptx.addSlide();
chrome(s, '分母会变，所以必须一起报', 6);
s.addText('同一个 coarse 层，query 细胞 1,535 个，排除 30 个后不再进入分母。',
  { x: 0.67, y: 1.6, w: 12.0, h: 0.35, fontFace: F, fontSize: 12.5, color: C.text, margin: 0 });

const bx = 0.67, by = 2.06, bw = 11.98, bh = 0.36;
s.addShape('rect', { x: bx, y: by, w: bw, h: bh, fill: { color: 'DCE7E9' }, line: { color: 'DCE7E9' } });
s.addShape('rect', { x: bx + bw * (1 - 30 / 1535), y: by, w: bw * (30 / 1535) + 0.05, h: bh, fill: { color: 'C00000' }, line: { color: 'C00000' } });
s.addText('eligible 1,505（coverage 98.05%）', { x: bx, y: by + 0.44, w: 5.4, h: 0.3, fontFace: F, fontSize: 11, bold: true, color: C.blue, margin: 0 });
s.addText('排除 30', { x: bx + bw - 1.5, y: by + 0.44, w: 1.5, h: 0.3, fontFace: F, fontSize: 11, bold: true, color: 'C00000', align: 'right', margin: 0 });

table(s, [
  ['必须并列报的量', '定义', '为什么必须报'],
  ['accuracy', 'correct ÷ n_q', '主指标'],
  ['n_q / coverage', '进入分母的细胞数', '排除规则一改，分母就变'],
  ['majority', '最大真值类占比', '无信息基线：准确率 0.4817，macro-F1 仅 0.0813'],
  ['shuffle_p', '预测向量置换检验', '只回答“是否优于随机”，不是多数类检验'],
], 0.67, 3.15, 11.98, [3.0, 3.3, 5.68], 0.5, 11.5);

band(s, '只报 accuracy，等于把分母的变化藏起来', 6.45);

// ---------------- 6 macro-F1 口径 ----------------
s = pptx.addSlide();
chrome(s, '同一份预测，两个 macro-F1', 7);
s.addText('差别只在“预测里出现、真实标签里不存在”的类算不算进平均。',
  { x: 0.67, y: 1.6, w: 12.0, h: 0.35, fontFace: F, fontSize: 12.5, color: C.text, margin: 0 });

s.addText('truth-only（平台 scVI 脚本默认）', { x: 0.9, y: 2.2, w: 5.6, h: 0.3, fontFace: F, fontSize: 11.5, bold: true, color: C.muted, margin: 0 });
s.addText('0.4516', { x: 0.9, y: 2.5, w: 5.6, h: 1.0, fontFace: F, fontSize: 44, bold: true, color: '8FA3AE', margin: 0 });
s.addText('只按真实标签集取平均；预测多出来的类被忽略。', { x: 0.9, y: 3.5, w: 5.6, h: 0.6, fontFace: F, fontSize: 11, color: C.muted, margin: 0, fit: 'shrink' });

s.addText('union（本项目跨方法统一口径）', { x: 6.9, y: 2.2, w: 5.6, h: 0.3, fontFace: F, fontSize: 11.5, bold: true, color: C.muted, margin: 0 });
s.addText('0.4014', { x: 6.9, y: 2.5, w: 5.6, h: 1.0, fontFace: F, fontSize: 44, bold: true, color: 'C00000', margin: 0 });
s.addText('真实 ∪ 预测 一起取平均；预测多出来的类记 F1 = 0。', { x: 6.9, y: 3.5, w: 5.6, h: 0.6, fontFace: F, fontSize: 11, color: C.muted, margin: 0, fit: 'shrink' });

s.addText('差值从哪来：被预测出来、但真值里根本不存在的类。这类越多，两个口径差得越大；人→斑马鱼这一格的差值就有 0.05。',
  { x: 0.67, y: 4.5, w: 12.0, h: 0.6, fontFace: F, fontSize: 11.5, color: C.muted, margin: 0, fit: 'shrink' });
s.addText('结论：单独看 truth-only 没问题，但它不能和别的方法并列；跨方法对比一律用 union，从 18 个逐细胞预测文件独立重算。',
  { x: 0.67, y: 5.25, w: 12.0, h: 0.9, fontFace: F, fontSize: 12.5, bold: true, color: C.title, margin: 0, fit: 'shrink' });
band(s, '例：人→斑马鱼 coarse，两个口径差 0.05 —— 足以改变“是否高于基线”的判断', 6.45);

// ---------------- 7 四方法结果 ----------------
s = pptx.addSlide();
chrome(s, '统一口径后的六方向结果', 8);
const chart = s.addChart(pptx.ChartType.bar, [
  { name: 'ortholog-PCA', labels: ['人→鼠', '鼠→人', '人→斑马鱼', '斑马鱼→人', '鼠→斑马鱼', '斑马鱼→鼠'], values: [0.6435, 0.6729, 0.1682, 0.1585, 0.2314, 0.4396] },
  { name: 'SATURN', labels: ['人→鼠', '鼠→人', '人→斑马鱼', '斑马鱼→人', '鼠→斑马鱼', '斑马鱼→鼠'], values: [0.4147, 0.4010, 0.2479, 0.4021, 0.6500, 0.6510] },
  { name: 'scVI', labels: ['人→鼠', '鼠→人', '人→斑马鱼', '斑马鱼→人', '鼠→斑马鱼', '斑马鱼→鼠'], values: [0.6683, 0.5895, 0.4014, 0.4290, 0.4248, 0.4786] },
], {
  x: 0.67, y: 1.62, w: 12.0, h: 4.35,
  barDir: 'col', barGrouping: 'clustered', barGapWidthPct: 60,
  chartColors: ['14505E', '9AB6BE', 'C2410C'],
  showValue: true, dataLabelFontSize: 8, dataLabelColor: '44535D', dataLabelPosition: 'outEnd', dataLabelFormatCode: '0.00',
  valAxisMaxVal: 0.8, valAxisMinVal: 0, valAxisMajorUnit: 0.1,
  catAxisLabelFontSize: 11, valAxisLabelFontSize: 9.5,
  showLegend: true, legendPos: 't', legendFontSize: 10.5,
  valGridLine: { color: 'E8EDEF', size: 0.5 }, catGridLine: { style: 'none' },
});
s.addText('读数：scVI 四个方向最高，但鼠→人输给 oPCA、鼠→鱼输给 SATURN——没有全面赢家。',
  { x: 0.67, y: 6.0, w: 12.0, h: 0.35, fontFace: F, fontSize: 12, bold: true, color: C.title, margin: 0, fit: 'shrink' });
band(s, 'SAMap 未画出：三方向 n=0，其余 0.0401–0.1127 ｜ 分母：oPCA 100%、scVI 98–100%、SATURN 29–87%', 6.45);

// ---------------- 8 选型指南 v0 ----------------
s = pptx.addSlide();
chrome(s, '场景化选型指南 v0', 9);
table(s, [
  ['场景', '首选', '次选', '不推荐', '证据强度'],
  ['近缘（人 ↔ 鼠）', 'ortholog-PCA', 'scVI（很接近）', 'SAMap', '中等'],
  ['远缘 · 人 ↔ 鱼', 'scVI', 'SATURN', 'SAMap', '中等'],
  ['远缘 · 鼠 ↔ 鱼', 'SATURN', 'scVI', 'SAMap', '中等'],
  ['跨门（七鳃鳗 ↔ 鼠）', '待跑', '—', '—', '数据已定位'],
  ['无 GPU', 'ortholog-PCA', 'scVI（8.5 min）', 'SATURN', '中等偏强'],
], 0.67, 1.70, 11.98, [3.4, 2.6, 2.6, 1.78, 1.6], 0.455, 12);

s.addText('三条限定语（必须随表一起出现）', { x: 0.67, y: 4.62, w: 6.0, h: 0.3, fontFace: F, fontSize: 12, bold: true, color: C.title, margin: 0 });
s.addText('① 全部为 transductive / in-sample，不是留出评估　② 四方法分母不同（oPCA 100%、scVI 98–100%、SATURN 29–87%、SAMap 0–91%）　③ 「不推荐」≠「方法差」',
  { x: 0.67, y: 4.96, w: 11.98, h: 0.62, fontFace: F, fontSize: 11.5, color: C.text, margin: 0, fit: 'shrink' });
s.addText('一句话：近缘先试 oPCA；跨得越远越要靠联合训练的潜空间方法，但人↔鱼与鼠↔鱼的首选不同；没有 GPU 时 scVI 只要 8.5 分钟。',
  { x: 0.67, y: 5.62, w: 11.98, h: 0.45, fontFace: F, fontSize: 12.5, bold: true, color: C.title, margin: 0, fit: 'shrink' });
band(s, '跨门仍是 insufficient evidence：数据已定位，但尚未跑；下次（第 3 次）讲四方法公平比较边界', 6.45);

pptx.writeFile({ fileName: OUT }).then(f => console.log('WROTE', f));
