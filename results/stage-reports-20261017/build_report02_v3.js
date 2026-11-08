// 第 2 次汇报 v3：四方法 + 批次混合指标 + 跨门可行性（8 页 / 7-8 分钟）
// 数字来源：
//   oPCA / SATURN / SAMap → docs/reports/unified-coarse-macro-f1-20261017.md
//   scVI                  → docs/reports/scvi-cross-species-result-20261019.md（并集口径重算）
//   批次指标              → docs/reports/batch-mixing-and-crossphylum-feasibility-20261019.md
const path = require('path');
const T = require(path.resolve(__dirname, '..', 'stage-reports-20261009', 'lib', 'report-template.js'));
const { newDeck, cover, chrome, box, band, table, C } = T;

const pptx = newDeck({ title: '课题5 第2次汇报：纠偏（v3）' });
const out = 'D:/projects/course5-prep/results/stage-reports-20261017/课题5第02次汇报_纠偏_7分钟版_v3.pptx';

// 1 封面
cover(pptx, {
  title: '课题5 第 2 次汇报：纠偏',
  subtitle: '从「证据是否可信」回到「哪个方法该在什么场景用」',
  meta: '汇报 2 · 7–8 分钟 ｜ 四方法：oPCA / SATURN / SAMap / scVI ｜ 口径：transductive · 数据截至 2026-10-19',
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
box(s, 0.7, 4.75, 11.9, 1.3, '本次进展',
  '换对指标重算（4 个结论翻转）→ 选型指南 v2 → 补齐 scVI 臂 → 补批次混合指标 → 定位跨门数据。',
  { fill: C.blueLight, bodySize: 12 });
band(s, '本次汇报：① 指标已纠正 ② 四方法矩阵完整 ③ 批次与跨门有实测结论', 6.35);

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

// 4 四方法主表
s = pptx.addSlide(); chrome(s, '统一 coarse 空间后的 macro-F1（四方法）', 4);
table(s, [
  ['方向', 'ortholog-PCA', 'SATURN v99', 'SAMap', 'scVI', '多数类'],
  ['人 → 鼠', '0.6435', '0.4147', '0.1127', '0.6683', '0.0813'],
  ['鼠 → 人', '0.6729', '0.4010', '0.0401', '0.5895', '0.0594'],
  ['人 → 斑马鱼', '0.1682', '0.2479', '0.0477', '0.4014', '0.0711'],
  ['斑马鱼 → 人', '0.1585', '0.4021', 'n/a', '0.4290', '0.0594'],
  ['鼠 → 斑马鱼', '0.2314', '0.6500', 'n/a', '0.4248', '0.0711'],
  ['斑马鱼 → 鼠', '0.4396', '0.6510', 'n/a', '0.4786', '0.0813'],
], 0.7, 1.7, 11.9, [2.9, 2.2, 2.0, 1.7, 1.7, 1.4], 0.40, 10.5);
box(s, 0.7, 4.6, 5.8, 1.55, 'scVI 的定位',
  '六方向中 4 个最高（人→鼠、人→鱼、鱼→人、鱼→鼠）；鼠→人 输给 oPCA，鼠→鱼 输给 SATURN。没有全面赢家。',
  { fill: C.greenLight, bodySize: 11.5 });
box(s, 6.78, 4.6, 5.82, 1.55, '口径提醒',
  '平台 scVI 默认输出 truth-only 口径（偏高）。本表已统一按并集口径从逐细胞预测重算。',
  { fill: C.goldLight, bodySize: 11.5 });
band(s, '限定：四方法分母不同（oPCA 100%、scVI 98–100%、SATURN 29–87%、SAMap 0–91%）', 6.35);

// 5 批次混合指标（新增页）
s = pptx.addSlide(); chrome(s, '批次混合：scVI latent 上物种并未混匀', 5);
table(s, [
  ['指标', '数值', '怎么读'],
  ['silhouette（细胞类型，cosine）', '0.181', '结构存在，但不算清晰'],
  ['iLISI（物种，k=30）', '1.125', '理论 1–3；接近 1 = 邻居几乎全同物种'],
  ['kBET 接受率（α=0.05）', '0.0039', '几乎全部邻域被拒绝'],
], 0.7, 1.62, 11.9, [4.4, 2.2, 5.3], 0.40, 11);
box(s, 0.7, 3.42, 11.9, 1.32, '看起来矛盾的地方',
  '同一份 latent 上，跨物种标签迁移的 macro-F1 却有 0.67（人→鼠）和 0.40（人→鱼）。如果物种完全分离，KNN 本不该迁移得这么好。',
  { fill: C.goldLight, bodySize: 11.5 });
box(s, 0.7, 4.88, 11.9, 1.05, '最可能的解释',
  '潜空间把「细胞类型」与「物种」编码在近似正交的方向上：同类型细胞跨物种彼此靠近，但单个细胞最近的 30 个邻居仍以本物种为主。',
  { fill: C.blueLight, bodySize: 11.5 });
band(s, '所以：低 iLISI 不等于方法失败，但两组证据必须并列报告，不能只引其中一个', 6.35);

// 6 选型指南 v2
s = pptx.addSlide(); chrome(s, '场景化选型指南 v2', 6);
table(s, [
  ['场景', '首选', '次选', '不推荐', '证据强度'],
  ['近缘（人 ↔ 鼠）', 'ortholog-PCA', 'scVI（很接近）', 'SAMap', '中等'],
  ['远缘 · 人 ↔ 鱼', 'scVI', 'SATURN', 'SAMap', '中等'],
  ['远缘 · 鼠 ↔ 鱼', 'SATURN', 'scVI', 'SAMap', '中等'],
  ['跨门（七鳃鳗 ↔ 鼠）', '待跑', '—', '—', '数据已定位'],
  ['无 GPU', 'ortholog-PCA', 'scVI（8.5 min）', 'SATURN', '中等偏强'],
], 0.7, 1.75, 11.9, [3.3, 2.5, 2.6, 1.9, 1.6], 0.46, 11);
box(s, 0.7, 4.65, 5.8, 1.45, 'v1 → v2 改了什么',
  '远缘不再是一个场景：人↔鱼 scVI 领先，鼠↔鱼 SATURN 领先；无 GPU 场景下 scVI 实测仅 8.5 分钟。',
  { fill: C.blueLight, bodySize: 11.5 });
box(s, 6.78, 4.65, 5.82, 1.45, '跨门有新进展',
  'LBSPA 的 8 物种对象含 Lamprey 41,678 与 Mouse 37,047 细胞、19 类脑细胞、13,172 共同基因轴。',
  { fill: C.greenLight, bodySize: 11.5 });
band(s, '指南四条限定语：transductive、分母不同、不推荐≠方法差、macro-F1 口径必须统一', 6.35);

// 7 还缺什么
s = pptx.addSlide(); chrome(s, '还缺什么：课程要求 vs 现状', 7);
table(s, [
  ['课程要求', '现状', '状态'],
  ['三方法：SATURN / SAMap / scVI', '四方法齐全（加 oPCA）', '已补'],
  ['macro-F1', '统一并集口径重算', '已补'],
  ['近缘 / 跨门 / 无 GPU', '2.5 / 3', '跨门待跑'],
  ['kBET / iLISI / silhouette', 'scVI 已测；其余方法缺嵌入', '部分'],
  ['时间与内存', 'scVI 8.5 min / 2.37 GB', '缺受控测量'],
  ['文档易用性 / Agent 友好度', '未做', '缺'],
  ['容器化', '有方案无交付物', '缺'],
], 0.7, 1.75, 11.9, [4.6, 4.6, 2.7], 0.36, 10.5);
box(s, 0.7, 4.75, 11.9, 1.15, '最大的剩余缺口',
  '跨门能跑了，但还没跑：需要确认 13,172 基因的取值层、19 类每类细胞数、以及必须用原始矩阵而不是论文自带的 harmony 嵌入。',
  { fill: C.roseLight, bodySize: 11.5 });
band(s, '批次指标只有 scVI 有：其余三方法当时没保存嵌入，补齐需要重跑', 6.35);

// 8 下一步
s = pptx.addSlide(); chrome(s, '下一步与需要的决策', 8);
table(s, [
  ['优先级', '动作', '成本', '状态'],
  ['已完成', '统一 macro-F1 重算', '0', '4 个结论翻转'],
  ['已完成', '选型指南 v1 → v2', '0', '含 scVI'],
  ['已完成', 'scVI 跨物种臂', '≈0.05 元', '6 方向 × 3 层'],
  ['已完成', '批次混合指标（scVI）', '0', '三项已出'],
  ['P6', '跨门：Lamprey vs Mouse 子集', '0.2–0.5 元', '三前提待确认'],
  ['P3', '其余方法批次指标 + 文档/Agent', '需重跑', '待做'],
], 0.7, 1.7, 11.9, [2.0, 5.4, 2.2, 2.3], 0.38, 10);
box(s, 0.7, 4.4, 5.8, 1.4, '需要决定',
  '① 鱼方向数字是否改用修正口径；② 是否投入跨门（0.2–0.5 元，需先确认三前提）',
  { fill: C.goldLight, bodySize: 11.5 });
box(s, 6.78, 4.4, 5.82, 1.4, '不变的原则',
  '不把 transductive 写成 inductive；不按总分排冠军；限定语随数字出现',
  { fill: C.blueLight, bodySize: 11.5 });
band(s, '下次汇报起统一控制在 7–8 分钟', 6.35);

pptx.writeFile({ fileName: out }).then(f => console.log('WROTE', f));
