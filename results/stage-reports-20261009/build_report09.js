// 第 9/10 次汇报：最小 inductive 方案（仅设计，不运行）
// 来源：docs/plans/inductive-pilot-manifest-v1.md
const T = require('./lib/report-template.js');
const { newDeck, cover, chrome, box, band, table, notes, C } = T;

const pptx = newDeck({ title: '课题5第9次汇报：最小 inductive 方案' });
const out = 'D:/projects/course5-prep/results/stage-reports-20261009/课题5第09次汇报_最小inductive方案.pptx';

// 1 封面
cover(pptx, {
  title: '课题5 第 9 次汇报：最小 inductive 方案',
  subtitle: '从 transductive 到 inductive：需要新增什么证据（设计完成，未运行）',
  meta: '汇报 9 / 10 · 设计文档：docs/plans/inductive-pilot-manifest-v1.md ｜ 未经批准不提交任何任务 · 2026 年 10 月',
});

// 2 为什么要 inductive
let s = pptx.addSlide(); chrome(s, '为什么现有结论不能回答"泛化"', 2);
table(s, [
  ['问题', 'transductive（现有全部结果）', 'inductive（本次设计）'],
  ['目标物种的可见性', '整合阶段可见（oPCA 为 label-free：仅评估用标签；SATURN/SAMap 标签参与训练/联合图）', '训练阶段完全不可见（严格 held-out）'],
  ['回答的问题', '目标物种参与整合后，标签迁移有多好？', '训练时没见过的物种，模型能迁移吗？'],
  ['数字的含义', '可达性能（含目标物种信息）', '泛化性能（无目标物种信息；高低关系需实验验证）'],
  ['可以写成', 'transductive / in-sample 重评估', 'held-out benchmark（首次可写）'],
], 0.7, 1.82, 11.9, [2.6, 4.6, 4.7], 0.52, 10.5);
box(s, 0.72, 4.55, 11.9, 1.6, '两者关系（不可互相替代）',
  '• 两者差值可作描述性对照，不能直接定义为"记忆依赖"或单独的泛化能力度量（需实验验证）\n'
  + '• 现有 86.18% / 0.6179 / 0.1050 等全部为 transductive——本设计不修改、不替代它们\n'
  + '• 预期 inductive 低于 transductive（待实验验证）；本设计不预设上下界关系', { fill: C.goldLight, bodySize: 10.5 });
band(s, '一句话：transductive 已经做完，inductive 是"另一条轴"——本页只设计，不启动。', 6.35);
notes(s, '开场把两条轴的差别钉死，防止把 transductive 结果当泛化结论。');

// 3 设计总表
s = pptx.addSlide(); chrome(s, '设计：留一物种 × 3 方法 × 3 seed', 3);
table(s, [
  ['参数', '值', '说明'],
  ['留出策略', 'leave-one-species-out ×3', '轮流留出鼠 / 鱼 / 人作为严格 held-out query'],
  ['表示层训练', '仅用剩余两物种训练；第三物种投影时模型不更新', '与 transductive 的根本区别'],
  ['评估', 'KNN15 cosine + coverage + majority', '与 transductive 协议保持可比较'],
  ['方法', 'ortholog-PCA + SATURN + SAMap（同跑；投影接口待验证）', '公平比较'],
  ['seed', '0, 1, 2（均值 ± sd）', '解决单 seed 限制'],
  ['预期产物', '3 物种 × 3 方法 × 3 seed × 三层 = 81 格', '全部标注 inductive'],
  ['资源档', 'SATURN 需 GPU；其余 CPU', '预算见下页'],
], 0.7, 1.82, 11.9, [2.2, 5.6, 4.1], 0.48, 10.5);
band(s, '本设计为候选方案：投影接口可执行性需先逐一验证，方可进入运行申请；81 格 = 3 物种 × 3 方法 × 3 seed × 3 层。', 6.35);
notes(s, '设计参数逐项可核对；81 格的账先算清楚再谈运行。');

// 4 预算与停止条件
s = pptx.addSlide(); chrome(s, '预算、停止条件与前置条件', 4);
box(s, 0.72, 1.82, 5.8, 4.3, '预算与保险丝',
  '• 单次 GPU 运行 ≤ ¥50（保险丝不变）\n• SATURN 需要 GPU：3 物种留出 × 3 seed\n  = 9 次 GPU 运行（上限）\n• 其余方法 CPU 档（1c4g/2c8g 级）\n• 预计总预算与资源档在运行申请单中列明\n\n纪律：\n• 不自动重试；任何失败 → 停止 → 分析原因\n  → 用户批准后方可重试', { fill: C.goldLight, bodySize: 10.5 });
box(s, 6.78, 1.82, 5.82, 4.3, '前置条件（缺一不启动）',
  '① mapping v1 获导师签认\n   （或按导师意见修订 v2 后签认）\n\n② 离线调度通道恢复，或 WDL 通道\n   被批准为正式运行通道\n\n③ 用户明确批准 GPU 预算\n\n④ 本设计经 Claude 审阅通过\n\n⑤ Genpilot 平台可执行性审查\n   （镜像/依赖/资源档）', { fill: C.blueLight, bodySize: 10.5 });
band(s, '前置条件全部满足之前，本方案保持"设计完成、未运行"状态。', 6.35);
notes(s, '预算与前置条件是给老师的"安全阀"：不因进度快就烧算力。');

// 5 最小可行版本
s = pptx.addSlide(); chrome(s, '最小可行版本：先回答一个问题', 5);
box(s, 0.72, 1.82, 6.3, 4.3, '如果预算受限，最小版本这样做',
  '• 只留出斑马鱼（最弱方向，信息量最大）\n• 三方法各跑 1 个 seed（seed 0）\n• 只报 coarse 层\n\n产物：3 方法 × 1 物种 × 1 seed = 3 格\n\n它能回答：\n→ 最弱方向上，"见过/没见过"的差距有多大？\n→ 哪个方法对目标物种的依赖最强？', { fill: C.blueLight, bodySize: 10.5 });
box(s, 7.28, 1.82, 5.32, 4.3, '完整版与最小版的关系',
  '• 完整版（81 格）：泛化矩阵 + seed 稳定性\n• 最小版（3 格）：先验证协议本身可行\n\n推进顺序：\n① 最小版跑通（验证 manifest 可执行）\n② 再按预算扩到完整版\n\n风险控制：\n• 每步都有独立停止条件\n• 最小版不达标（协议错误）→ 不进入完整版', { fill: C.roseLight, bodySize: 10.5 });
band(s, '先花小钱验证协议，再花大钱拿结论——这是本设计的推进纪律。', 6.35);
notes(s, '最小版本是给"预算不批"情形准备的降级路径。');

// 6 设计完成 ≠ 已运行
s = pptx.addSlide(); chrome(s, '状态声明与下一步', 6);
table(s, [
  ['项', '状态'],
  ['设计文档', 'docs/plans/inductive-pilot-manifest-v1.md（已完成）'],
  ['任务提交', '未提交任何任务（DCS / WDL / GPU 全部未启动）'],
  ['预算占用', '0 元'],
  ['下一步（需要批准）', '① 投影接口可执行性验证 ② 导师签认映射表 ③ 批准预算与通道 ④ 审阅后先跑最小版'],
], 0.7, 1.82, 11.9, [2.6, 9.3], 0.52, 10.5);
box(s, 0.72, 4.55, 11.9, 1.6, '本页要防的误读',
  '• "有设计 = 有结果"：❌ 本页全部为设计内容，没有任何 inductive 数字\n'
  + '• "transductive 结论可以外推"：❌ 外推必须由本设计跑出的数字支撑\n'
  + '• "批准设计 = 批准预算"：❌ 设计与预算是两个独立批准事项', { fill: C.roseLight, bodySize: 10.5 });
band(s, '下一阶段（汇报 10）：阶段收口——全部产物清单、待决事项与下一阶段路线。', 6.35);
notes(s, '状态声明页：设计完成、零预算占用、等批准。');

pptx.writeFile({ fileName: out }).then(() => console.log('PPTX_DONE ' + out));
