// 第 3/10 次汇报：三方法公平比较边界
// 数字来源：docs/evidence/method-comparison-matrix-20261008.md、docs/final-evidence-matrix-20261005.md
const T = require('./lib/report-template.js');
const { newDeck, cover, chrome, box, band, table, notes, C } = T;

const pptx = newDeck({ title: '课题5第3次汇报：三方法公平比较边界' });
const out = 'D:/projects/course5-prep/results/stage-reports-20261009/课题5第03次汇报_三方法公平比较边界.pptx';

// 1 封面
cover(pptx, {
  title: '课题5 第 3 次汇报：三方法公平比较边界',
  subtitle: '为什么不能把三列数字按一个总分排冠军',
  meta: '汇报 3 / 10 · 讲协议差异与适用范围，不报新跑分 ｜ 口径：transductive / in-sample · 单 seed（0）· 2026 年 10 月',
});

// 2 总览
let s = pptx.addSlide(); chrome(s, '同一批数据，三种完全不同的方法', 2);
table(s, [
  ['', 'ortholog-PCA', 'SATURN', 'SAMap'],
  ['同源信息载体', '1:1 直系同源基因表（硬过滤）', 'ESM2 蛋白语言模型（软嵌入）', '1:1 直系同源基因近邻图'],
  ['跨物种桥梁', '基因名匹配后取交集', '蛋白序列嵌入空间对齐', '基因-基因拓扑对齐'],
  ['降维/表示', '联合 PCA-50', 'macrogene 聚合（1000）', 'SAM 潜空间（npcs=100）'],
  ['整合范式', '零整合（零训练零校正）', '深度生成联合训练', '图对齐迭代'],
  ['标签使用', 'label-free（训练不用标签）', 'label-aware（labels 通道；ref_labels 仅评估）', 'label-aware（keys=cell_type）'],
  ['算力成本', 'CPU 秒级（17.9s）', 'GPU 4090（离线通道历史运行）', 'CPU 1c4g WDL（约 16 分钟）'],
], 0.7, 1.82, 11.9, [1.7, 3.4, 3.4, 3.4], 0.44, 10.5);
band(s, '三个方法回答的是三个不同的科学问题——列在一起是为了对照协议，不是为了排名。', 6.35);
notes(s, '开场先打破"排行榜"预期：这不是三个模型的分数对比，而是三种整合范式的协议对照。');

// 3 表示层与同源信息
s = pptx.addSlide(); chrome(s, '维度一：表示层与同源信息不同', 3);
box(s, 0.72, 1.82, 3.9, 4.3, 'ortholog-PCA：硬交集',
  '• 人鼠 1:1 直系同源 15,869 基因\n  （人鱼 9,131 / 鼠鱼 7,670）\n• 基因名匹配后取交集，不存在的\n  基因直接丢弃\n• 联合 PCA-50，零训练\n\n特点：\n• 完全可复现（固定基因表）\n• 信号上限由同源表质量决定\n• 简单、快、无随机性', { fill: C.blueLight, bodySize: 10.5 });
box(s, 4.72, 1.82, 3.9, 4.3, 'SATURN：软嵌入',
  '• ESM2 蛋白语言模型把每个基因\n  编码为蛋白嵌入\n• macrogene（1000）聚合基因表达\n• 联合训练对齐两物种嵌入空间\n\n特点：\n• 可表达"序列相似但不同名"的\n  同源关系（软桥）\n• 需要 GPU 训练，含随机性\n• 蛋白信号经消融验证为真', { fill: C.goldLight, bodySize: 10.5 });
box(s, 8.72, 1.82, 3.88, 4.3, 'SAMap：图对齐',
  '• 1:1 直系同源基因的近邻图\n• 迭代对齐基因-基因拓扑\n• SAM 潜空间（npcs=100）\n\n特点：\n• 不依赖基因名一一对应，\n  靠拓扑一致性\n• 原生工作流 keys=cell_type\n  （标签参与联合图构建）\n• CPU 可跑，成本中等', { fill: C.blueLight, bodySize: 10.5 });
band(s, '表示层是方法设计选择，不是"谁更先进"——每一种都对应不同的先验假设。', 6.35);
notes(s, '三个卡片分别讲清楚"同源信息怎么过桥"，这是理解后面数字差异的基础。');

// 4 标签与训练协议
s = pptx.addSlide(); chrome(s, '维度二：标签可见性与训练协议不同', 4);
table(s, [
  ['维度', 'ortholog-PCA', 'SATURN', 'SAMap'],
  ['训练阶段标签', '不使用（label-free）', 'labels 通道参与 miner（ref_labels 仅评估；运行时待核实）', 'keys=cell_type 参与联合图'],
  ['评估阶段标签', 'KNN 监督（同协议）', 'KNN 监督（同协议）', 'KNN 监督（同协议）'],
  ['label-aware / free', 'label-free', 'label-aware', 'label-aware'],
  ['训练参数', '无训练', 'epochs=50, macrogenes=1000', 'NUMITERS=3'],
  ['评分器', 'KNN15 · cosine · 倒距离加权', '同（v99 统一评分器）', '同（与 v99 同评分器）'],
], 0.7, 1.82, 11.9, [2.4, 3.4, 3.2, 2.9], 0.42, 10.5);
box(s, 0.72, 4.5, 5.8, 1.7, '这意味着什么',
  '• SATURN/SAMap 的训练机制使用细胞类型标签\n  （SATURN：species 前缀 labels；SAMap：keys=cell_type）\n• 该机制对本次分数的贡献尚未单独量化\n• 不能与 label-free 的 ortholog-PCA 直接互比', { fill: C.roseLight, bodySize: 11 });
box(s, 6.78, 4.5, 5.82, 1.7, '怎么比才公平',
  '• 同协议重跑（label-free 化训练，机制见备注）→ 属新任务\n• 或明确声明"这是 label-aware 协议下的结果"\n• 本轮全部结果：协议分列、不合并排名', { fill: C.blueLight, bodySize: 11 });
band(s, '标签可见性是方法设计的一部分；引用任何数字必须同时说明标签协议。', 6.35);
notes(s, '这一页是全套汇报最重要的边界之一：label-aware 与 label-free 不可互比。');

// 5 标签空间与分母
s = pptx.addSlide(); chrome(s, '维度三：标签空间与分母不同', 5);
table(s, [
  ['', 'ortholog-PCA', 'SATURN v97g', 'SATURN v99', 'SAMap v98'],
  ['coarse 标签空间', '映射词汇（9 粗类）', 'mapped-space（映射后粗类）', '原始标签+status 过滤', '原始标签+status 过滤'],
  ['排除规则', 'status≠active 双向', '规则合规列（74 细胞双向排除）', 'coarse/fine 排除；exact 不排除', 'status≠active 双向'],
  ['n_q（h→m）· coarse', '1,505', '≈1,505（日志级）', '1,505', '1,505'],
  ['n_q（h→m）· exact', '1,535', '1,535', '1,535', '1,535'],
  ['coverage_q · coarse', '0.9805', '0.9805（日志级）', '0.9805', '0.9805'],
], 0.7, 1.82, 11.9, [2.5, 2.3, 2.7, 2.6, 1.8], 0.40, 10);
box(s, 0.72, 4.35, 5.8, 1.85, '分母不同的直接后果',
  '• 同一个"准确率"，分母可能差 30–44 个细胞\n• 排除规则本身改变数字（汇报 2 已实证 729 案例）\n• 跨方法同表只能作方向性参考', { fill: C.goldLight, bodySize: 11 });
box(s, 6.78, 4.35, 5.82, 1.85, '引用纪律（写进任何报告）',
  '• 每个 acc 必须并列 n_q 与 coverage\n• 映射词汇 vs 原始标签：两套 coarse 不互换\n• v97g 与 v99：同方法内部也不合并', { fill: C.blueLight, bodySize: 11 });
band(s, '标签空间 + 分母 = 数字的可比性边界；缺任何一项，比较都无效。', 6.35);
notes(s, '分母效应在汇报 2 已经讲透，这里只强调跨方法的差异。');

// 6 能回答/不能回答
s = pptx.addSlide(); chrome(s, '每个方法能回答什么、不能回答什么', 6);
table(s, [
  ['方法', '能回答的问题', '不能回答的问题'],
  ['ortholog-PCA', '同源基因投影本身携带多少跨物种信号？', '深度模型是否比简单基线更好（需同协议对比）'],
  ['SATURN', '蛋白语言模型嵌入在同数据上比零基线好多少？', 'label-free 场景下的表现（labels 通道参与了训练）'],
  ['SAMap', '转录组对齐在 label-aware 协议下能否产生可分联合流形？', 'label-free 场景的表现（keys 参与了联合图）'],
], 0.7, 1.82, 11.9, [2.2, 5.0, 4.7], 0.58, 10.5);
box(s, 0.72, 4.28, 5.8, 1.92, '用"谁更好"替代科学问题的后果',
  '• 会把协议差异误读成方法能力差异\n• 会让"简单方法赢"看起来像异常\n  （实际是零整合基线的真实信号）\n• 会掩盖 label-aware 的贡献来源', { fill: C.roseLight, bodySize: 11 });
box(s, 6.78, 4.28, 5.82, 1.92, '本课题的问法',
  '• 问题 1：跨物种信号是否真实存在？（三方法交叉验证）\n• 问题 2：协议差异如何影响数字？（分列报告）\n• 问题 3：泛化能力如何测？（需 inductive 新协议，见汇报 9）', { fill: C.blueLight, bodySize: 11 });
band(s, '先问"回答什么问题"，再谈"数字高低"——这是本轮汇报的立场。', 6.35);
notes(s, '把三个方法各自的问题域钉死，防止后面被问"到底谁最好"。');

// 7 不可比项清单 + 方向性观察
s = pptx.addSlide(); chrome(s, '不可比项清单与方向性观察', 7);
box(s, 0.72, 1.82, 6.3, 4.3, '五项不可比（引用禁令）',
  '① 标签空间两套：ortholog-PCA、SATURN v97g = 映射标签空间；\n    SATURN v99、SAMap = 原始标签空间（按各自规则过滤）\n    → 跨空间数值不可直接排名\n\n② SAMap label-aware vs ortholog-PCA label-free\n    → 不是同一问题的比较\n\n③ v97g（mapped-space）vs v99（原始标签空间）\n    → 同方法内部两套数字也不可合并\n\n④ 置换检验零分布定义不同（各自口径）\n\n⑤ 算力成本悬殊（17s CPU vs 4090 GPU vs 16min）\n    → 效率比较需另行设计', { fill: C.roseLight, bodySize: 10.5 });
box(s, 7.28, 1.82, 5.32, 4.3, '可讲的方向性观察（带警示）',
  '• 哺乳动物对（coarse）：\n  oPCA 0.8618 ≥ SATURN v97g 0.6179 ≥ SAMap 0.1050\n\n• 斑马鱼相关四方向（coarse，逐方向）：\n  oPCA：h→z 0.1961 ／ m→z 0.2755 ／ z→h 0.1813 ／ z→m 0.5761\n  SATURN v97g：h→z 0.1835 ／ m→z 0.3009 ／ z→h 0.2474 ／ z→m 0.4651\n  SAMap：h→z 0.0341 ／ m→z 0.0000 ／ z→h 0.0000 ／ z→m 0.0000\n\n• 读数：仅 oPCA 的 z→m（0.5761）超过其多数类 0.4817；\n  其余方向均弱或无信号\n\n• ESM2 蛋白信号为真（消融 67.4→20.4，v72-era 协议内配对）\n\n⚠ 跨列标签空间/协议不同——仅作方向性参考，不构成排名', { fill: C.blueLight, bodySize: 10.5 });
band(s, '边界讲清楚了，下一阶段（汇报 4）开始逐方法闭环：先讲 ortholog-PCA 基线。', 6.35);
notes(s, '左边是"不能做什么"，右边是"能谨慎说什么"——两边都要在报告里成对出现。');

pptx.writeFile({ fileName: out }).then(() => console.log('PPTX_DONE ' + out));
