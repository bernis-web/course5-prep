// 第 2 次汇报：纠偏（7-8 分钟 / 7 页）
// 数字来源：docs/reports/unified-coarse-macro-f1-20261017.md（零算力重算）
const path = require('path');
const T = require(path.resolve(__dirname, '..', 'stage-reports-20261009', 'lib', 'report-template.js'));
const { newDeck, cover, chrome, box, band, table, C } = T;

const pptx = newDeck({ title: '课题5 第2次汇报：纠偏' });
const out = 'D:/projects/course5-prep/results/stage-reports-20261017/课题5第02次汇报_纠偏_7分钟版.pptx';

// 1 封面
cover(pptx, {
  title: '课题5 第 2 次汇报：纠偏',
  subtitle: '从「证据是否可信」回到「哪个方法该在什么场景用」',
  meta: '汇报 2 · 7–8 分钟 ｜ 口径：transductive / in-sample · 数据截至 2026-10-17',
});

// 2 一句话结论
let s = pptx.addSlide(); chrome(s, '一句话结论', 2);
box(s, 0.7, 1.75, 11.9, 1.05, '根因',
  '老师说的「偏」，根因不是数字不准，而是交付物类型错了。',
  { fill: C.roseLight, bodySize: 17, titleSize: 13 });
box(s, 0.7, 3.0, 5.8, 1.5, '课程要的',
  '「场景 → 方法 → 指标 → 选型建议」的基准报告',
  { fill: C.blueLight, bodySize: 13 });
box(s, 6.78, 3.0, 5.82, 1.5, '我们交的',
  '「数字如何可信」的审计报告',
  { fill: C.goldLight, bodySize: 13 });
box(s, 0.7, 4.75, 11.9, 1.3, '后果',
  '此前汇报里，没有一页回答「近缘 / 跨门 / 无 GPU 该选哪个方法」。证据治理本身是对的，但它占了 100% 篇幅，本次降到附录。',
  { fill: C.blueLight, bodySize: 12 });
band(s, '本次汇报做三件事：① 换对指标重算 ② 补上选型指南 ③ 说清还缺什么', 6.35);

// 3 换指标后结论翻转
s = pptx.addSlide(); chrome(s, '换对指标后，4 个结论翻转', 3);
box(s, 0.7, 1.7, 11.9, 0.85, '前提',
  '课程要求 macro-F1，我们此前用 accuracy。统一到 coarse 标签空间重算后：',
  { fill: C.blueLight, bodySize: 12 });
table(s, [
  ['方向', '方法', 'accuracy 判定', 'macro-F1 判定', '翻转'],
  ['人 → 斑马鱼', 'ortholog-PCA', '低于多数类', '高于多数类', '翻转'],
  ['人 → 斑马鱼', 'SATURN v99', '低于多数类', '高于多数类', '翻转'],
  ['斑马鱼 → 人', 'ortholog-PCA', '低于多数类', '高于多数类', '翻转'],
  ['鼠 → 斑马鱼', 'ortholog-PCA', '低于多数类', '高于多数类', '翻转'],
], 0.7, 2.75, 11.9, [3.0, 3.0, 2.6, 2.6, 0.7], 0.42, 11);
box(s, 0.7, 4.95, 11.9, 1.2, '机制与含义',
  '多数类分类器 accuracy 有 0.31–0.48，但 macro-F1 只有 0.06–0.08（它在所有少数类上 F1=0）。所以此前「含斑马鱼方向普遍低于基线」的负结论，主要是度量选择造成的假象。',
  { fill: C.roseLight, bodySize: 11.5 });
band(s, '零算力重算：只用现有 confusion / per_cell，未跑任何模型', 6.35);

// 4 统一指标后的主表
s = pptx.addSlide(); chrome(s, '统一 coarse 空间后的 macro-F1', 4);
table(s, [
  ['方向', 'ortholog-PCA', 'SATURN v99', 'SAMap', '多数类基线'],
  ['人 → 鼠', '0.6435', '0.4147', '0.1127', '0.0813'],
  ['鼠 → 人', '0.6729', '0.4010', '0.0401', '0.0594'],
  ['人 → 斑马鱼', '0.1682', '0.2479', '0.0477', '0.0711'],
  ['斑马鱼 → 人', '0.1585', '0.4021', 'n/a', '0.0594'],
  ['鼠 → 斑马鱼', '0.2314', '0.6500', 'n/a', '0.0711'],
  ['斑马鱼 → 鼠', '0.4396', '0.6510', 'n/a', '0.0813'],
], 0.7, 1.75, 11.9, [3.4, 2.4, 2.3, 1.9, 1.9], 0.44, 11.5);
box(s, 0.7, 4.95, 11.9, 1.15, '新发现',
  '远缘场景下 SATURN 反而优于 ortholog-PCA（人→鱼 0.2479 vs 0.1682）。说明 macrogene 压缩表示在物种距离越远时越有价值。',
  { fill: C.greenLight, bodySize: 12 });
band(s, '限定：三方法分母不同（oPCA 100%、SATURN 30–87%、SAMap 0–91%），不能当绝对排名', 6.35);

// 5 选型指南
s = pptx.addSlide(); chrome(s, '场景化选型指南 v1', 5);
table(s, [
  ['场景', '首选', '次选', '不推荐', '证据强度'],
  ['近缘（人 ↔ 鼠）', 'ortholog-PCA', 'SATURN', 'SAMap', '中等'],
  ['远缘（人 ↔ 斑马鱼）', 'SATURN', 'ortholog-PCA', 'SAMap', '中等'],
  ['跨门（七鳃鳗 ↔ 鼠）', '—', '—', '—', '无证据'],
  ['无 GPU', 'ortholog-PCA', 'SAMap', 'SATURN', '中等'],
], 0.7, 1.8, 11.9, [3.4, 2.6, 2.4, 1.9, 1.6], 0.5, 11.5);
box(s, 0.7, 4.5, 5.8, 1.5, '覆盖情况',
  '近缘 ✅　远缘 ✅　无 GPU ✅；跨门 ❌ 无证据',
  { fill: C.blueLight, bodySize: 12 });
box(s, 6.78, 4.5, 5.82, 1.5, '跨门为什么没做',
  '自设 gate 要求「先有结论」，而项目又坚持「不能下结论」，于是永远不启动。',
  { fill: C.roseLight, bodySize: 11.5 });
band(s, '指南里跨门明确写 insufficient evidence，不假装覆盖', 6.35);

// 6 还缺什么
s = pptx.addSlide(); chrome(s, '还缺什么：课程要求 vs 现状', 6);
table(s, [
  ['课程要求', '现状', '缺口'],
  ['三方法：SATURN / SAMap / scVI', 'oPCA / SATURN / SAMap', '缺 scVI 臂'],
  ['macro-F1', '已重算（本次）', '已补'],
  ['kBET / iLISI / silhouette', '未做', '缺'],
  ['时间与内存', '部分', '缺受控测量'],
  ['文档易用性 / Agent 友好度', '未做', '缺'],
  ['近缘 / 跨门 / 无 GPU', '2.5 / 3', '缺跨门'],
  ['容器化', '有方案无交付物', '缺'],
], 0.7, 1.75, 11.9, [4.6, 4.0, 3.3], 0.36, 10.5);
box(s, 0.7, 4.75, 11.9, 1.15, '最硬的一条',
  '课程标题是「SATURN vs SAMap vs scVI 系」，我们的矩阵里没有 scVI。LBSPA 论文（已精读）用的正是 scVI，这条必须补。',
  { fill: C.roseLight, bodySize: 11.5 });
band(s, '已写出 scVI 跨物种臂设计方案（docs/plans/scvi-cross-species-design-20261017.md）', 6.35);

// 7 下一步
s = pptx.addSlide(); chrome(s, '下一步与需要的决策', 7);
table(s, [
  ['优先级', '动作', '成本', '状态'],
  ['已完成', '统一 macro-F1 重算', '0', '4 个结论翻转'],
  ['已完成', '选型指南 v1', '0', '3/4 场景'],
  ['P4', 'scVI 跨物种臂', '≤0.3 元', '设计完成，待批准'],
  ['P6', '跨门最小跑', '0.2–0.5 元', '数据待核实'],
  ['P3', '时间/内存 + 文档/Agent 评分', '0', '待做'],
], 0.7, 1.75, 11.9, [2.0, 5.4, 2.2, 2.3], 0.40, 10.5);
box(s, 0.7, 4.25, 5.8, 1.55, '需要决定',
  '① 鱼方向数字是否改用修正口径；② 是否批准 scVI 臂与跨门场景',
  { fill: C.goldLight, bodySize: 12 });
box(s, 6.78, 4.25, 5.82, 1.55, '不变的原则',
  '不把 transductive 写成 inductive；不按总分排冠军；限定语随数字出现',
  { fill: C.blueLight, bodySize: 11.5 });
band(s, '下次汇报起统一控制在 7–8 分钟', 6.35);

pptx.writeFile({ fileName: out }).then(f => console.log('WROTE', f));
