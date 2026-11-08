// 第 5/10 次汇报：SATURN 结果与容量/协议效应
// 数字来源：docs/transductive-formal-v74-evidence-20260928.md（v97g 表）、results/pilot-v1/saturn-v99/raw/recovered-20261001/metrics.json（v99）、
//           docs/final-evidence-matrix-20261005.md §五（ESM2 消融 / seed / ceiling / pseudobulk）
const T = require('./lib/report-template.js');
const { newDeck, cover, chrome, box, band, table, notes, C } = T;

const pptx = newDeck({ title: '课题5第5次汇报：SATURN 结果与协议效应' });
const out = 'D:/projects/course5-prep/results/stage-reports-20261009/课题5第05次汇报_SATURN信号与协议效应.pptx';

// 1 封面
cover(pptx, {
  title: '课题5 第 5 次汇报：SATURN 信号与协议效应',
  subtitle: '信号来自哪里、为什么不能当作泛化性能',
  meta: '汇报 5 / 10 · 双口径：v97g（日志级）+ v99（文件级）｜ 口径：transductive / in-sample · label-aware（labels 通道）· 2026 年 10 月',
});

// 2 SATURN 是什么
let s = pptx.addSlide(); chrome(s, 'SATURN 的方法构成与本轮设置', 2);
box(s, 0.72, 1.82, 3.9, 4.3, '① 蛋白语言模型',
  '• ESM2 把每个基因编码为\n  蛋白序列嵌入\n• 跨物种桥梁建立在蛋白序列空间\n  而非基因名匹配\n• 可表达"序列相似但不同名"的同源关系', { fill: C.blueLight, bodySize: 10.5 });
box(s, 4.72, 1.82, 3.9, 4.3, '② macrogene 聚合',
  '• 1,000 个 macrogene 聚合基因表达\n• 相当于学习一个数据驱动的\n  降维 + 跨物种对应表\n• epochs=50 联合训练\n• 表示层为 1,000 维 macrogene 空间\n  （v99 评分读取 obsm["macrogenes"]，\n  形状 4,606 × 1,000）', { fill: C.goldLight, bodySize: 10.5 });
box(s, 8.72, 1.82, 3.88, 4.3, '③ 联合训练 + 评分',
  '• label-aware：labels 通道参与 cross_species miner\n  （ref_labels 仅为输出/评估真值；\n   运行时源码版本与训练命令待核实）\n• 输出 macrogene 嵌入空间\n• 评分：KNN15 · cosine · 倒距离加权\n  （v99 统一评分器，与 ortholog-PCA 同）\n• 置换检验：200 次预测向量洗牌', { fill: C.blueLight, bodySize: 10.5 });
band(s, '三个组件缺一不可：蛋白先验 + 容量控制 + 统一评分——这也决定了后面数字的读法。', 6.35);
notes(s, '先讲清楚方法构成，为"双口径"和"消融"两页做铺垫。');

// 3 双口径
s = pptx.addSlide(); chrome(s, '双口径：三个数字必须分开报告', 3);
table(s, [
  ['数字', '口径（评分器 + 标签空间）', '分母', '证据等级'],
  ['0.6179', 'v97g 评分器 · mapped-space（映射后粗类）', 'coverage 0.9805 → n_q≈1,505', 'confirmed（日志级）'],
  ['0.4749', 'v99 统一评分器 · exact（原始标签）', 'n_q = 1,535（无排除）', 'candidate（provenance confirmed）'],
  ['0.4844', 'v99 统一评分器 · coarse（原始标签+status 过滤）', 'n_q = 1,505', 'candidate（provenance confirmed）'],
], 0.7, 1.82, 11.9, [1.15, 6.4, 2.15, 2.2], 0.5, 10.5);
box(s, 0.72, 4.35, 5.8, 1.8, '三个数字的关系',
  '• 同一批 SATURN 嵌入（obsm/macrogenes）\n• 不同评分器（v97g vs v99 统一评分器）\n• 不同标签空间（mapped vs 原始标签）\n→ 不是"同一个指标的两次测量"', { fill: C.roseLight, bodySize: 10.5 });
box(s, 6.78, 4.35, 5.82, 1.8, '引用禁令',
  '• 不能写成"SATURN 从 61.79% 降到 48.44%"\n• 不能只报其中一个数字\n• 凡出现 SATURN 数字必须同时写：\n  评分器 / 标签空间 / 分母 / 证据等级', { fill: C.goldLight, bodySize: 10.5 });
band(s, '三个数字对应三种协议，各自成立——合并即误导。', 6.35);
notes(s, '这页与汇报 2 例 2 一致，此处作为 SATURN 专场的口径钉板。');

// 4 v97g 六方向
s = pptx.addSlide(); chrome(s, 'v97g 六方向：与多数类的对照', 4);
table(s, [
  ['direction', 'coarse（合规列）', '多数类', '超出/低于', 'coverage_q'],
  ['human→mouse', '0.6179', '0.4817', '+13.6 pt', '0.9805'],
  ['mouse→human', '0.2539', '0.3115', '−5.8 pt', '1.0000'],
  ['human→zebrafish', '0.1835', '0.3976', '−21.4 pt', '0.9715'],
  ['mouse→zebrafish', '0.3009', '0.3976', '−9.7 pt', '0.9715'],
  ['zebrafish→human', '0.2474', '0.3115', '−6.4 pt', '1.0000'],
  ['zebrafish→mouse', '0.4651', '0.4817', '−1.7 pt', '0.9805'],
], 0.7, 1.82, 11.9, [3.0, 2.6, 2.0, 2.3, 2.0], 0.46, 10.5);
band(s, '六方向中仅 human→mouse 明确高于多数类（+13.6 pt）；其余五方向低于或接近——这是 SATURN 自身在当前口径下的格局。', 6.35);
notes(s, 'v97g 为日志级证据（无逐细胞文件）；数字转录自 v74 证据文档表。');

// 5 信号来源：ESM2 消融
s = pptx.addSlide(); chrome(s, '信号来源证据：ESM2 消融', 5);
table(s, [
  ['运行', '蛋白嵌入', 'h→m coarse', '说明'],
  ['正常 ESM2', '真实蛋白序列嵌入', '67.4%（v72-era 协议）', '该运行的历史基线'],
  ['消融（v80 置换运行）', '蛋白嵌入打乱', '20.4%', '置换后大幅下降'],
], 0.7, 1.82, 11.9, [3.4, 3.4, 2.4, 2.7], 0.55, 11);
box(s, 0.72, 4.35, 5.8, 1.8, '这说明什么',
  '• 该运行对蛋白嵌入置换敏感（67.4% → 20.4%，v72-era 协议内配对）\n• 支持蛋白先验在此配置中具有重要贡献\n• 不构成“能力全部来自 ESM2”或\n  “与训练技巧无关”的结论（单项消融不足）\n• 随机基线未在同一运行内给出，\n  不做“接近随机”判断', { fill: C.blueLight, bodySize: 10.5 });
box(s, 6.78, 4.35, 5.82, 1.8, '不能推出什么',
  '• 不能推出"蛋白信号 = 可泛化"\n  （消融在 transductive 协议内进行）\n• 不能推出 SATURN 优于其他方法\n  （跨方法协议不同，见汇报 3）\n• 20.4% 不是"最差表现"的下界', { fill: C.roseLight, bodySize: 10.5 });
band(s, '消融是"信号为真"的证据，不是"方法更好"的证据——两者必须分开说。', 6.35);
notes(s, '消融实验是 v80 置换运行，confirmed 级（方向性）。');

// 6 容量与稳定性
s = pptx.addSlide(); chrome(s, '容量、seed 与上限：三个必须随带的数字', 6);
box(s, 0.72, 1.82, 3.9, 4.3, '容量：1,000 macrogenes',
  '• 表示层容量由 macrogene 数控制\n• 1,000 是本轮设置\n• 与 PCA-50 的对比：不是同一维度量级\n  （1,000 维 vs 50 维）；macrogene 是\n  学习出来的聚合，PCA 是线性投影\n• 容量对比需要同协议实验，\n  本轮没有做（标注为缺口）', { fill: C.goldLight, bodySize: 10.5 });
box(s, 4.72, 1.82, 3.9, 4.3, 'seed：稳定 + 双峰',
  '• human→mouse：67.1 ± 3.8\n  → 稳定（波动 < 4 pt）\n• 鱼方向：11.3 / 48.8 / 8.3\n  → 明显双峰，单次运行不可信\n• 后果：所有单 seed 数字\n  对鱼方向只能作为点估计，\n  不能作为该方向的稳定值', { fill: C.roseLight, bodySize: 10.5 });
box(s, 8.72, 1.82, 3.88, 4.3, '上限：物种内 ceiling',
  '• 同物种内共享潜空间的对照：\n  85.5 / 93.5 / 74.2\n• 用途：给跨物种数字一个"天花板"参照\n• 跨物种与物种内的差值只能作\n  描述性参照，不能直接定义为\n  “迁移损失”（不同方法/协议）\n• 引用时必须成对出现\n  （跨物种数字 + ceiling）', { fill: C.blueLight, bodySize: 10.5 });
band(s, '稳定性、容量与上限是数字的"使用说明书"——缺任何一个都会过度解读。', 6.35);
notes(s, '三个卡片分别对应：容量缺口、seed 双峰、ceiling 参照。');

// 7 边界与结论
s = pptx.addSlide(); chrome(s, 'SATURN 的证据等级与边界', 7);
box(s, 0.72, 1.82, 6.3, 4.3, '可以说的（有证据）',
  '• 蛋白先验对该运行有重要贡献\n  （消融 67.4 → 20.4，v72-era 协议内配对；\n   v97g 协议下消融未重跑）\n\n• human→mouse 高于多数类\n  （v97g 0.6179 vs 0.4817；v99 0.4844 vs 0.4618）\n\n• 哺乳动物对信号稳定（67.1 ± 3.8）\n\n• 信号在 mapped-space 与原始标签空间下\n  方向一致（都指向"有信号但有限"）', { fill: C.blueLight, bodySize: 10.5 });
box(s, 7.28, 1.82, 5.32, 4.3, '不能说的（越界）',
  '• ✗ "SATURN 达到 61.79%，优于基线"\n  （标签空间+评分器+排除三重差异）\n\n• ✗ "SATURN 具备泛化能力"\n  （全部 transductive/in-sample）\n\n• ✗ "鱼方向表现差 = 方法无效"\n  （双峰 + 单 seed + 上限未知）\n\n• ✗ 把 v97g 与 v99 合并成单一成绩\n\n• ✗ 与其他方法按总分排名', { fill: C.roseLight, bodySize: 10.5 });
band(s, '下一阶段（汇报 6）：SAMap 复现与负结果——同样的纪律，更极端的数字。', 6.35);
notes(s, '收尾：左列"能说"右列"不能说"，与汇报 3 的边界页呼应。');

pptx.writeFile({ fileName: out }).then(() => console.log('PPTX_DONE ' + out));
