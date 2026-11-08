// 课题5 第 5/7 次汇报：跨门场景（七鳃鳗 ↔ 小鼠）
// 版式：康复大学校模板
const path = require('path');
const T = require(path.resolve(__dirname, '..', 'stage-reports-20261009', 'lib', 'report-template.js'));
const { newDeck, cover, chrome, box, band, table, C, F, W, H } = T;

const OUT = 'D:/projects/course5-prep/results/stage-reports-20261022/课题5第05次汇报_跨门场景.pptx';
const pptx = newDeck({ title: '课题5 第5次汇报：跨门场景' });

// 1 封面
cover(pptx, {
  title: '课题5 第 5 次汇报：跨门场景',
  subtitle: '七鳃鳗 ↔ 小鼠 —— 一个负结果，以及它排除了什么',
  meta: '2026-10-22 ｜ 7 次汇报中的第 5 次 ｜ 任务 W202610220063725 ｜ 口径：transductive',
});

// 2 任务定位
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
  ['批次混合与生物保守性', '进行中（仅 scVI）'],
  ['时间与内存', '部分（已补跨门）'],
  ['场景：跨门（七鳃鳗 ↔ 鼠）', '本次完成（负结果）'],
  ['文档 / Agent 友好度 + 容器化', '未开始'],
], 0.67, 2.52, 7.5, [5.3, 2.2], 0.415, 11.5);
const px = 8.55, py = 2.52, pw = 4.05, seg = pw / 7;
const states = ['done','done','done','half','half','done','todo'];
const cols = { done: '1F7A4D', half: 'FFC000', todo: 'DCE3E8' };
states.forEach((st, i) => {
  s.addShape('rect', { x: px + i * seg + 0.03, y: py, w: seg - 0.06, h: 0.30, fill: { color: cols[st] }, line: { color: cols[st] } });
});
s.addText('4 / 7 完成', { x: px, y: py + 0.42, w: pw, h: 0.34, fontFace: F, fontSize: 18, bold: true, color: '1F7A4D', margin: 0 });
s.addText('2 项进行中 · 1 项未开始', { x: px, y: py + 0.80, w: pw, h: 0.28, fontFace: F, fontSize: 10.5, color: C.muted, margin: 0 });
s.addShape('rect', { x: 8.55, y: 4.05, w: 4.05, h: 1.5, fill: { color: C.blueLight }, line: { color: C.line, width: 1 } });
s.addText('本次覆盖', { x: 8.72, y: 4.17, w: 3.7, h: 0.28, fontFace: F, fontSize: 11, bold: true, color: C.blue, margin: 0 });
s.addText('第 6 项：跨门场景（七鳃鳗 ↔ 小鼠），oPCA 与 scVI 双臂实测', { x: 8.72, y: 4.47, w: 3.7, h: 1.0, fontFace: F, fontSize: 12, bold: true, color: C.title, margin: 0, fit: 'shrink' });
band(s, '三场景至此全部覆盖：近缘 已完成 / 跨门 已完成（负结果）/ 无 GPU 已完成', 6.45);

// 3 为什么跨门难
s = pptx.addSlide();
chrome(s, '为什么跨门难：三个结构性障碍', 3);
const bars = [
  ['01', '基因对应稀疏', '七鳃鳗是现存最原始的脊椎动物，与小鼠的直系同源覆盖远低于人-鼠、人-鱼。'],
  ['02', '注释体系不对称', '七鳃鳗 13 类，小鼠 18 类；前者是后者的真子集，小鼠独有 6 类（EX/IN/SNCG/Purkinje/Golgi/Bergmann）。'],
  ['03', '数据规模失衡', '七鳃鳗 41,678 细胞；小鼠排除独有 6 类后只剩 14,016（占其 37.8%）。'],
];
let yy = 1.85;
for (const [n, k, v] of bars) {
  s.addText(n, { x: 0.67, y: yy, w: 0.8, h: 0.5, fontFace: F, fontSize: 22, bold: true, color: 'C2410C', margin: 0 });
  s.addText(k, { x: 1.55, y: yy + 0.02, w: 3.2, h: 0.42, fontFace: F, fontSize: 17, bold: true, color: C.title, margin: 0 });
  s.addText(v, { x: 4.9, y: yy, w: 7.7, h: 0.8, fontFace: F, fontSize: 12, color: C.text, margin: 0, fit: 'shrink' });
  s.addShape('rect', { x: 0.67, y: yy + 0.95, w: 11.98, h: 0.01, fill: { color: 'D9E0E4' }, line: { color: 'D9E0E4' } });
  yy += 1.35;
}
s.addText('跨门不是"再跑一次"，而是三个维度同时退化。', { x: 0.67, y: 5.95, w: 11.98, h: 0.4, fontFace: F, fontSize: 14, bold: true, color: C.title, margin: 0 });
band(s, '所以这里的关键不是调参，而是先看清约束', 6.45);

// 4 数据与协议
s = pptx.addSlide();
chrome(s, '数据与协议：可复核的取舍', 4);
table(s, [
  ['项', '值'],
  ['来源', 'LBSPA 8CrossSpecies.rds（Seurat，13,172 基因 × 333,627 细胞，8 物种）'],
  ['细胞', 'Lamprey 41,678 + Mouse 14,016 = 55,694'],
  ['基因', '6,222（13,172 轴上两物种 min_cells≥3 的共同基因）'],
  ['评估空间', '13 类交集，仅 coarse'],
  ['协议', 'normalize_total(1e4)+log1p、KNN15 cosine、200 次置换、seed 0'],
  ['两臂', 'oPCA（联合 PCA-50）与 scVI（n_latent=10, batch_key=species, 50 epoch）'],
], 0.67, 1.72, 11.98, [2.6, 9.4], 0.52, 11.5);
box(s, 0.67, 5.15, 5.85, 1.15, '取舍一',
  '小鼠独有 6 类占其 62.2%，全部排除出评估——不合并、不臆造等价映射。', { fill: C.goldLight, bodySize: 11 });
box(s, 6.8, 5.15, 5.85, 1.15, '取舍二',
  '基因轴是「七鳃鳗检测 ∩ 小鼠高检测」，七鳃鳗非零基因仅 56.7%。', { fill: C.goldLight, bodySize: 11 });
band(s, '两个取舍都写进报告，不藏起来', 6.45);

// 5 结果
s = pptx.addSlide();
chrome(s, '结果：两个方法都失败', 5);
table(s, [
  ['方法', '七鳃鳗 → 鼠（acc / macro-F1）', '鼠 → 七鳃鳗（acc / macro-F1）'],
  ['ortholog-PCA', '0.0575 / 0.0711', '0.0516 / 0.0732'],
  ['scVI', '0.0582 / 0.0652', '0.0457 / 0.0802'],
  ['多数类基线', '0.2168', '0.3059'],
], 0.67, 1.72, 11.98, [3.0, 4.6, 4.38], 0.55, 13);
s.addText('13 类空间随机猜测约 7.7%，两方法实测 4.6–5.8%，低于随机；离多数类基线差 4–6 倍。',
  { x: 0.67, y: 4.05, w: 11.98, h: 0.45, fontFace: F, fontSize: 14, bold: true, color: 'C00000', margin: 0, fit: 'shrink' });
box(s, 0.67, 4.7, 11.98, 1.5, '置换检验怎么看',
  'oPCA p=0.345 / 0.860；scVI p=0.040 / 0.145。这个 p 只回答"是否优于随机打乱"，不回答"是否优于多数类基线"——scVI 的 0.040 不能读成"显著更好"。',
  { fill: C.roseLight, bodySize: 11.5 });
band(s, '这不是"差一点"，是完全没有成立', 6.45);

// 6 为什么 scVI 没救回来
s = pptx.addSlide();
chrome(s, '为什么 scVI 没救回来', 6);
s.addText('门内：scVI 在远缘明显更好', { x: 0.67, y: 1.65, w: 6.0, h: 0.32, fontFace: F, fontSize: 13, bold: true, color: C.blue, margin: 0 });
table(s, [
  ['方向', 'oPCA', 'scVI'],
  ['人 → 斑马鱼', '0.1682', '0.4014'],
  ['斑马鱼 → 人', '0.1585', '0.4290'],
], 0.67, 2.02, 5.7, [2.6, 1.55, 1.55], 0.44, 11.5);
s.addText('跨门：两者都塌到 0.07 量级', { x: 7.0, y: 1.65, w: 5.6, h: 0.32, fontFace: F, fontSize: 13, bold: true, color: 'C00000', margin: 0 });
table(s, [
  ['方向', 'oPCA', 'scVI'],
  ['七鳃鳗 → 鼠', '0.0711', '0.0652'],
  ['鼠 → 七鳃鳗', '0.0732', '0.0802'],
], 7.0, 2.02, 5.6, [2.5, 1.55, 1.55], 0.44, 11.5);
box(s, 0.67, 3.95, 11.98, 1.05, '门内的规律',
  '越远越要靠联合训练的潜空间方法（人→鱼 scVI 是 oPCA 的 2.4 倍）。', { fill: C.greenLight, bodySize: 11.5 });
box(s, 0.67, 5.15, 11.98, 1.05, '跨门中断了',
  '可能的解释：门内三物种共享脊椎动物身体计划与器官（心脏），细胞类型同源；跨门脑区与细胞类型缺乏可靠对应，不是表示学习能补的。',
  { fill: C.roseLight, bodySize: 11 });
band(s, '一个方法在门内赢，不代表它在跨门也赢', 6.45);

// 7 限定与可重试条件
s = pptx.addSlide();
chrome(s, '限定与什么情况下值得重试', 7);
s.addText('必须随结果一起出现的五条', { x: 0.67, y: 1.62, w: 6.0, h: 0.3, fontFace: F, fontSize: 13, bold: true, color: C.blue, margin: 0 });
const lim = [
  '小鼠侧 62.2% 细胞被排除',
  '基因轴是交集，七鳃鳗非零仅 56.7%',
  '只有 coarse 单层，与门内三层不对等',
  '单 seed，无置信区间',
  '只能说"在这套数据/注释/规模下不成立"',
];
let ly = 2.0;
for (const t of lim) {
  s.addText('· ' + t, { x: 0.67, y: ly, w: 5.9, h: 0.34, fontFace: F, fontSize: 11.5, color: C.text, margin: 0, fit: 'shrink' });
  ly += 0.44;
}
s.addText('什么情况下值得重试', { x: 6.9, y: 1.62, w: 5.8, h: 0.3, fontFace: F, fontSize: 13, bold: true, color: '1F7A4D', margin: 0 });
const retry = [
  '更完整的跨门同源映射（含一对多/旁系）',
  '不裁剪到 13 类，保留全部 19 类做层级对应',
  '有 coarse→fine 的注释对应树',
];
let ry = 2.0;
for (const t of retry) {
  s.addText('· ' + t, { x: 6.9, y: ry, w: 5.75, h: 0.34, fontFace: F, fontSize: 11.5, color: C.text, margin: 0, fit: 'shrink' });
  ry += 0.5;
}
box(s, 0.67, 4.55, 11.98, 1.2, '不要这样写',
  '「跨门不可行」——过头了。正确写法是「在当前数据与注释体系下，oPCA 与 scVI 均未能实现跨门标签迁移」。',
  { fill: C.roseLight, bodySize: 11.5 });
band(s, '负结果的价值在于排除一条路，而不是宣布此路永不通', 6.45);

// 8 选型 v3 + 下一步
s = pptx.addSlide();
chrome(s, '选型指南 v3 与下一步', 8);
table(s, [
  ['场景', '首选', '次选', '不推荐', '证据'],
  ['近缘（人 ↔ 鼠）', 'oPCA', 'scVI（接近）', 'SAMap', '中等'],
  ['远缘 · 人 ↔ 鱼', 'scVI', 'SATURN', 'SAMap', '中等'],
  ['远缘 · 鼠 ↔ 鱼', 'SATURN', 'scVI', 'SAMap', '中等'],
  ['跨门（七鳃鳗 ↔ 鼠）', '不建议（两法均失败）', '—', '—', '中等（双臂实测）'],
  ['无 GPU', 'oPCA', 'scVI（8.5 min）', 'SATURN', '中等偏强'],
], 0.67, 1.62, 11.98, [3.3, 3.4, 2.4, 1.5, 1.4], 0.42, 11);
box(s, 0.67, 4.2, 5.85, 1.45, '本次改动',
  '跨门从「无证据」改为「两法均失败」；三场景至此全部覆盖。', { fill: C.greenLight, bodySize: 11.5 });
box(s, 6.8, 4.2, 5.85, 1.45, '下次（第 6 次）',
  '映射签认与证据责任：AI 复核 ≠ 导师签认。', { fill: C.blueLight, bodySize: 11.5 });
band(s, '三条限定语不变：transductive / 分母不同 / 不推荐≠方法差', 6.45);

pptx.writeFile({ fileName: OUT }).then(f => console.log('WROTE', f));
