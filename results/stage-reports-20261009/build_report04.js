// 第 4/10 次汇报：ortholog-PCA 基线闭环（旧草表 → candidate-final）
// 数字来源：docs/final-evidence-matrix-ortholog-pca-20261003.md、results/pilot-v1/ortholog-pca-v98/metrics.json
// 旧草表出处：docs/course5-longrun-state-20260930.md §2（v75c/v78b）；作废说明：docs/stale-numbers-audit-20261003.md
const T = require('./lib/report-template.js');
const { newDeck, cover, chrome, box, band, table, notes, C } = T;

const pptx = newDeck({ title: '课题5第4次汇报：ortholog-PCA 基线闭环' });
const out = 'D:/projects/course5-prep/results/stage-reports-20261009/课题5第04次汇报_ortholog-PCA基线闭环.pptx';

// 1 封面
cover(pptx, {
  title: '课题5 第 4 次汇报：ortholog-PCA 基线闭环',
  subtitle: '把早期草表正式替换为统一评分器 candidate-final——以及为什么简单基线有时超过复杂模型',
  meta: '汇报 4 / 10 · 数字唯一来源：results/pilot-v1/ortholog-pca-v98/ ｜ 口径：transductive / in-sample · 单 seed（0）· 2026 年 10 月',
});

// 2 为什么重做
let s = pptx.addSlide(); chrome(s, '旧草表为什么作废：两条硬伤', 2);
box(s, 0.72, 1.82, 5.8, 4.3, '硬伤一：排除规则失效',
  '旧草表用字符串过滤 coarse_level == \'unmapped\'\n\n• 实测：该过滤在冻结映射表中 0 行命中\n• 后果：本应排除的 74 个细胞\n  （mouse 30 / zebrafish 44）\n  全部留在分母里\n• 每个方向受影响细胞数不同\n  → 各方向偏差不一致，无法事后修正\n\n结论：排除规则不是"清洗细节"，\n它直接改变每个方向的 accuracy。', { fill: C.roseLight, bodySize: 10.5 });
box(s, 6.78, 1.82, 5.82, 4.3, '硬伤二：不是统一评分器',
  '旧草表出自 v75c / v78b 容器内输出\n（出处：course5-longrun-state-20260930 §2）\n\n• 与冻结的评分器定义存在实现差异：\n  KNN K=15 · cosine · 倒距离加权 1/(d+1e-12)\n  平票按字典序 · 200 次 RandomState(0) 置换\n• 未做预测向量置换检验\n• 无逐细胞预测文件、无输出 SHA\n\n结论：无法逐格复核的数字\n不能作为正式结论。', { fill: C.roseLight, bodySize: 10.5 });
band(s, '两条硬伤叠加 → 旧草表全部作废；正式引用一律以统一评分器复算结果为准。', 6.35);
notes(s, '诚实交代旧数字的问题，这页是"数据卫生"的示范。');

// 3 旧→新对照
s = pptx.addSlide(); chrome(s, '旧草表 → candidate-final：逐方向对照', 3);
table(s, [
  ['direction', '旧草表（作废）', '新 coarse（candidate-final）', 'query 侧排除', '变化'],
  ['human→mouse', '80.9%', '86.18%', '30（鼠）', '上升'],
  ['mouse→human', '38.3%', '73.69%', '0', '上升'],
  ['human→zebrafish', '40.5%', '19.61%', '44（鱼）', '下降'],
  ['mouse→zebrafish', '22.4%', '27.55%', '44（鱼）', '上升'],
  ['zebrafish→human', '11.9%', '18.13%', '0', '上升'],
  ['zebrafish→mouse', '79.5%', '57.61%', '30（鼠）', '下降'],
], 0.7, 1.82, 11.9, [2.5, 2.2, 3.0, 2.2, 2.0], 0.5, 10.5);
band(s, '旧草表两条硬伤同时作用（排除失效 + 评分器差异）；逐方向变化方向不一，不做单项定量归因。新表逐格可回溯（predictions/ 18 份 + confusion/ 18 份）。', 6.35);
notes(s, '对照表说明：变化不是"调参调出来的"，是修规则 + 统一评分器之后数字自己变准了。');

// 4 18 格全表
s = pptx.addSlide(); chrome(s, 'candidate-final：六方向 × 三层全表', 4);
table(s, [
  ['direction', 'exact', 'coarse（主层）', 'fine', 'coverage(q)', 'majority(coarse)', 'n_q'],
  ['human→mouse', '0.7824', '0.8618', '0.7980', '0.9805', '0.4817', '1,505'],
  ['mouse→human', '0.4084', '0.7369', '0.4103', '1.0000', '0.3115', '1,528'],
  ['human→zebrafish', '0.1698', '0.1961', '0.1801', '0.9715', '0.3976', '1,499'],
  ['mouse→zebrafish', '0.1659', '0.2755', '0.1748', '0.9715', '0.3976', '1,499'],
  ['zebrafish→human', '0.1453', '0.1813', '0.1695', '1.0000', '0.3115', '1,528'],
  ['zebrafish→mouse', '0.4769', '0.5761', '0.5010', '0.9805', '0.4817', '1,505'],
], 0.7, 1.82, 11.9, [2.4, 1.5, 2.0, 1.5, 1.7, 2.1, 0.7], 0.44, 10.5);
box(s, 0.72, 5.02, 11.9, 1.15, '口径（引用本表必须随带）',
  '全部为 transductive/in-sample 重评估（联合 PCA 含 query 表达值）；单 seed（0）；coarse/fine 剔除 status≠active（mouse 30 / zf 44）后计分；'
  + 'coarse 层 shuffle_p 六方向均 0.0（mouse→zebrafish 的 exact 层为 0.02；零分布 = 预测边际×真值边际对角积 E[null]，非多数类检验）。', { fill: C.goldLight, bodySize: 10 });
band(s, '18 格全部可逐细胞复算：predictions/ 18 份 + confusion/ 18 份；输出 SHA b2b3ac6b…c725（manifest 锚定）。', 6.35);
notes(s, '主结论层是 coarse；exact 和 fine 作为参考层同时给出，防止"挑层报数"。');

// 5 读数一：哺乳动物对
s = pptx.addSlide(); chrome(s, '读数一：哺乳动物对信号强', 5);
table(s, [
  ['direction', 'coarse', '多数类', '超出多数类', 'n_q'],
  ['human→mouse', '0.8618', '0.4817', '+38.0 pt', '1,505'],
  ['mouse→human', '0.7369', '0.3115', '+42.5 pt', '1,528'],
], 0.7, 1.82, 11.9, [3.2, 2.4, 2.4, 2.4, 1.5], 0.55, 11);
box(s, 0.72, 4.0, 5.8, 2.1, '为什么可信',
  '• 双向都强（不是单向巧合）\n• 超出多数类 38–42 个百分点\n• 混淆矩阵显示主要类别命中率高\n  （h→m：内皮 720/725、免疫 197/202）\n• 与 pseudobulk 映射验证一致（人鼠 8 对全进 top5）', { fill: C.blueLight, bodySize: 10.5 });
box(s, 6.78, 4.0, 5.82, 2.1, '为什么仍然只是 candidate-final',
  '• 单 seed（0）点估计\n• 物种内 ceiling（85.5/93.5/74.2，SATURN 侧、不同方法/协议）\n  仅作辅助参照，不能当作本基线天花板\n• 结论限于当前数据子集（每物种 ~1.5k 细胞）\n• transductive 口径，不能外推泛化能力', { fill: C.goldLight, bodySize: 10.5 });
band(s, '哺乳动物对强信号是本课题最稳的结论；但"强"是相对多数类，不是绝对可用。', 6.35);
notes(s, '强调双向一致 + 混淆矩阵 + pseudobulk 三方互证，再讲边界。');

// 6 读数二：鱼方向
s = pptx.addSlide(); chrome(s, '读数二：斑马鱼方向弱，一个例外', 6);
table(s, [
  ['direction', 'coarse', '多数类', '判断', 'n_q'],
  ['human→zebrafish', '0.1961', '0.3976', '低于多数类', '1,499'],
  ['mouse→zebrafish', '0.2755', '0.3976', '低于多数类', '1,499'],
  ['zebrafish→human', '0.1813', '0.3115', '低于多数类', '1,528'],
  ['zebrafish→mouse', '0.5761', '0.4817', '高于多数类（唯一例外）', '1,505'],
], 0.7, 1.82, 11.9, [3.4, 2.0, 2.0, 3.0, 1.5], 0.46, 10.5);
box(s, 0.72, 4.28, 5.8, 1.92, '弱方向的读法（防两个误读）',
  '• 不能读成"方法失效"——零整合基线本来就不含\n  鱼方向所需的深度信号\n• 不能把 shuffle_p=0.0 读成"显著优于多数类"\n  （p 只回答"优于随机预测向量"）', { fill: C.roseLight, bodySize: 10.5 });
box(s, 6.78, 4.28, 5.82, 1.92, 'z→m 例外的读法',
  '• 57.61% > 多数类 48.17%，是六方向中唯一\n  鱼→哺乳动物的正信号\n• 但同为单 seed 点估计；鱼方向 seed 双峰已证实\n  （SATURN 侧 11.3 / 48.8 / 8.3）\n• 是否稳定需要 inductive 多 seed 协议回答（汇报 9）', { fill: C.blueLight, bodySize: 10.5 });
band(s, '方向性格局：哺乳动物对强、鱼方向弱、z→m 例外——单 seed 限制对全表生效。', 6.35);
notes(s, '鱼方向是审阅重点：既不能夸大（z→m 例外）也不能贬低（工具无效）。');

// 7 与 SATURN 对比 + 结论
s = pptx.addSlide(); chrome(s, '方法学结论：简单基线为什么难超越', 7);
table(s, [
  ['同方向（coarse）', 'ortholog-PCA', 'SATURN v97g', '差'],
  ['human→mouse', '0.8618', '0.6179', '+24.4 pt'],
  ['mouse→human', '0.7369', '0.2539', '+48.3 pt'],
  ['zebrafish→mouse', '0.5761', '0.4651', '+11.1 pt'],
], 0.7, 1.82, 11.9, [3.4, 3.0, 3.0, 2.5], 0.5, 10.5);
box(s, 0.72, 4.35, 5.8, 1.8, '为什么零整合基线能领先',
  '• 同源基因表是高质量的"先验知识"：1:1 直系同源\n  已经完成了大部分跨物种对齐工作\n• PCA-50 在共享同源子空间上几乎无损\n• 深度方法引入了训练噪声与标签依赖，\n  在这批小样本上不一定摊得回来', { fill: C.blueLight, bodySize: 10.5 });
box(s, 6.78, 4.35, 5.82, 1.8, '引用纪律（三条）',
  '• 跨方法 coarse 标签空间不同（映射词汇 vs 原始标签）\n  → 同表仅作方向性参考\n• SATURN 为 v97g 日志级口径（0.6179），与 v99 不可合并\n• 全部 transductive；不能表述为"超越 SOTA"', { fill: C.goldLight, bodySize: 10.5 });
band(s, '本页回答："为什么简单方法有时赢"——赢在同源先验，且仅在当前数据/协议/口径下。', 6.35);
notes(s, '这一页是老师最可能追问的点：先给解释，再给引用纪律。');

pptx.writeFile({ fileName: out }).then(() => console.log('PPTX_DONE ' + out));
