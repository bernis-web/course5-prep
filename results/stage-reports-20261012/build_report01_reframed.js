// 第 1/10 次汇报：先把比较做公平
// 本册只讲第一阶段的一个问题：如何建立可复核的共同比较起点。
// 详细数字来源放到汇报 2，三方法协议差异放到汇报 3，不在本册提前讲完。
const path = require('path');
const T = require(path.resolve(__dirname, '..', 'stage-reports-20261009', 'lib', 'report-template.js'));
const { newDeck, cover, chrome, box, band, table, notes, C } = T;

const pptx = newDeck({ title: '课题5第1次汇报：先把比较做公平' });
const out = 'D:/projects/course5-prep/results/stage-reports-20261012/课题5第01次汇报_先把比较做公平.pptx';

cover(pptx, {
  title: '课题5 第 1 次汇报：先把比较做公平',
  subtitle: '跨物种心脏细胞注释：建立同一份数据、同一套规则、同一条证据链',
  meta: '汇报 1 / 10 · 本次只完成“共同比较起点” · 详细算式与方法比较留到后续汇报',
});

let s = pptx.addSlide(); chrome(s, '我们先解决的不是“谁最高”，而是“能不能公平地比”', 2);
box(s, 0.68, 1.78, 3.72, 3.08, '输入：同一批跨物种数据',
  '人：1,528 个细胞\n鼠：1,535 个细胞\n斑马鱼：1,543 个细胞\n\n三物种都来自心脏单细胞数据，先固定输入文件与细胞筛选规则。',
  { fill: C.blueLight, bodySize: 11 });
box(s, 4.82, 1.78, 3.72, 3.08, '问题：方法数字为什么会不同',
  '同一个“准确率”，可能受到不同因素影响：\n\n表示层不同\n标签空间不同\nquery/reference 角色不同\n排除规则和分母不同',
  { fill: C.goldLight, bodySize: 11 });
box(s, 8.96, 1.78, 3.72, 3.08, '本轮目标：先固定比较规则',
  '先把输入、标签、分母、基线和证据等级写清楚。\n\n这样后面每一个数字都能回答：\n“从哪个文件、按什么规则算出来？”',
  { fill: C.greenLight, bodySize: 11 });
band(s, '本次汇报的成果不是“公布冠军”，而是把后续 9 次汇报都能复用的比较起点固定下来。', 5.42);
notes(s, '开场直接收窄范围：第一轮只解决公平比较的前提，不提前公布全部结果。');

s = pptx.addSlide(); chrome(s, '共同比较起点：三件事先冻结', 3);
table(s, [
  ['先冻结什么', '本轮采用的规则', '为什么必须先冻结'],
  ['输入数据', '三份 h5ad、只纳入 cell；输入文件登记 SHA-256', '避免不同版本或不同细胞集合造成假差异'],
  ['标签与分母', 'exact / coarse / fine 分层；每个方向单列 n_q 与 coverage', '排除规则会改变分母，不能只报一个百分比'],
  ['证据等级', '文件级、容器/日志级、已复算分别标注', '有数字不等于有逐细胞文件，也不等于已独立复算'],
], 0.68, 1.82, 11.98, [2.2, 5.0, 4.78], 0.68, 10.3);
box(s, 0.68, 4.9, 5.78, 1.05, '冻结后的共同输出',
  '每个方向至少同时保留：correct、n_q、accuracy、coverage、majority、shuffle_p，以及逐细胞预测/混淆矩阵（若该运行已产生）。',
  { fill: C.blueLight, bodySize: 10.3 });
box(s, 6.8, 4.9, 5.86, 1.05, '本轮不做的事',
  '不把不同标签空间的数字合成总排名；不把日志级数字写成文件级证据；不把 transductive 结果写成泛化能力。',
  { fill: C.roseLight, bodySize: 10.3 });
band(s, '结果表先有“口径列”，再有“分数列”。', 6.36);
notes(s, '这一页只建立规则，不展开三种方法的结果。');

s = pptx.addSlide(); chrome(s, '一个数字怎样进入表格：先看最短来源链', 4);
const steps = [
  ['1', '原始 h5ad', '固定物种、细胞和输入 SHA'],
  ['2', '表示层', '例如 1:1 ortholog 交集 + PCA-50'],
  ['3', '预测', 'reference 拟合，query 用 KNN15 预测'],
  ['4', '排除与计分', '按 mapping_status 得到 n_q，再算 correct / n_q'],
  ['5', '证据文件', 'metrics.json、predictions、confusion、SHA'],
];
steps.forEach((r, i) => {
  const x = 0.72 + i * 2.48;
  box(s, x, 2.03, 2.18, 2.35, r[0] + '  ' + r[1], r[2], {
    fill: i % 2 === 0 ? C.blueLight : C.goldLight,
    bodySize: 10.3,
    titleSize: 13.2,
  });
  if (i < steps.length - 1) s.addText('→', { x: x + 2.2, y: 2.94, w: 0.26, h: 0.34, fontFace: '微软雅黑', fontSize: 20, bold: true, color: C.blue, margin: 0, align: 'center' });
});
box(s, 0.72, 4.86, 5.84, 1.0, '本轮只展示一个例子：human → mouse / coarse',
  '1,297 个正确预测 ÷ 1,505 个合格 query = 86.18%；coverage = 1,505 ÷ 1,535 = 98.05%。',
  { fill: C.greenLight, bodySize: 11 });
box(s, 6.82, 4.86, 5.8, 1.0, '详细拆解留到汇报 2',
  '下一轮再逐步展开：15,869 个 1:1 ortholog、归一化、PCA、KNN、排除的 30 个细胞，以及混淆矩阵。',
  { fill: C.roseLight, bodySize: 10.4 });
band(s, '先让听众知道“86.18%从哪里来”，下一次再把每一步算式讲透。', 6.32);
notes(s, '本页故意只给一个方向作为示范，不把 18 格结果提前讲完。');

s = pptx.addSlide(); chrome(s, '本轮真正解决了什么问题', 5);
table(s, [
  ['之前容易发生的误读', '这次做的修正', '带来的变化'],
  ['同一张表出现多套旧数字', '冻结唯一数字源，作废草表并记录 SHA', '后续汇报不再靠记忆抄数字'],
  ['只看 accuracy，不知道分母', '每个方向并列 n_q、coverage、majority', '能区分“预测更准”与“分母变了”'],
  ['不同方法直接排高低', '把表示层、标签空间、协议和证据等级分开', '先比较问题和口径，再讨论结果'],
  ['有日志数字就当成完整结果', '区分文件级、容器/日志级、已复算', '知道哪些结论可以引用，哪些只能作参考'],
], 0.68, 1.82, 11.98, [3.55, 4.62, 3.81], 0.68, 10.2);
band(s, '这一步解决的是“结果可信不可信、能不能复核”，不是“哪种方法已经赢了”。', 6.3);
notes(s, '把本轮贡献说成证据和比较框架，不把项目状态清单当成科学结论。');

s = pptx.addSlide(); chrome(s, '本轮结论：起点已固定，结论还没有提前下', 6);
box(s, 0.72, 1.86, 5.78, 2.55, '今天可以明确说的',
  '• 三物种输入、标签层级、分母和证据等级已经分开记录；\n'
  + '• 后续每个数字都能回到 metrics / predictions / confusion / SHA；\n'
  + '• human→mouse/coarse 的 86.18% 已有完整的计算入口，但本次只作示例。',
  { fill: C.greenLight, bodySize: 10.8 });
box(s, 6.78, 1.86, 5.82, 2.55, '今天不能提前说的',
  '• 不能用这一页排出三方法总冠军；\n'
  + '• 不能把 transductive/in-sample 结果当作新物种泛化；\n'
  + '• 不能把日志级 SATURN 数字与文件级结果混成同一口径。',
  { fill: C.roseLight, bodySize: 10.8 });
box(s, 0.72, 4.82, 11.88, 1.0, '下一次汇报（第 2 / 10 次）',
  '只做一件事：把 human→mouse/coarse 的 86.18% 从原始 h5ad 讲到表格单元格，逐步展示输入、表示层、query/reference、排除、分母、正确数和 SHA。',
  { fill: C.blueLight, bodySize: 11.2, titleSize: 14.5 });
band(s, '第 1 次汇报到此为止：先把比较做公平，再逐轮回答“数字怎么来、方法差在哪、结论能走多远”。', 6.3);
notes(s, '明确节奏：本次只完成共同起点，下一次专门讲数字来源。');

pptx.writeFile({ fileName: out }).then(() => console.log('PPTX_DONE ' + out));
