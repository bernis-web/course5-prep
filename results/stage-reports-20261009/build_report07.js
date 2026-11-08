// 第 7/10 次汇报：三方法总矩阵与老师问题专页
// 数字来源：docs/final-evidence-matrix-20261005.md §二/§三/§四（唯一出处）
const T = require('./lib/report-template.js');
const { newDeck, cover, chrome, box, band, table, notes, C } = T;

const pptx = newDeck({ title: '课题5第7次汇报：三方法总矩阵与老师问题专页' });
const out = 'D:/projects/course5-prep/results/stage-reports-20261009/课题5第07次汇报_三方法总矩阵与老师问题.pptx';

// 1 封面
cover(pptx, {
  title: '课题5 第 7 次汇报：三方法总矩阵',
  subtitle: '用最终证据重做老师指出的那张表——既有含金量，又不误导',
  meta: '汇报 7 / 10 · 数字唯一出处：docs/final-evidence-matrix-20261005.md ｜ 口径：transductive / in-sample · 单 seed（0）· 2026 年 10 月',
});

// 2 老师问题回顾
let s = pptx.addSlide(); chrome(s, '老师指出的三个问题与本轮回应', 2);
table(s, [
  ['老师的问题', '旧 PPT 的状态', '本轮回应'],
  ['① 核心表数字过时', '仍用作废草表 80.9/38.3/40.5/22.4/11.9/79.5', '替换为 candidate-final 86.18/73.69/19.61/27.55/18.13/57.61（逐格可复核）'],
  ['② SAMap 表述过时', '写"v98 尚需修正复跑"', '改为"WDL 已完成；结果为当前数据/协议下的探索性复现"'],
  ['③ 数字含金量与防误读', '缺少来源链与协议差异说明', '本表每列附协议标签、coverage/n_q、证据等级；新增算式页与差异页'],
], 0.7, 1.82, 11.9, [2.6, 4.6, 4.7], 0.66, 10.5);
box(s, 0.72, 4.62, 11.9, 1.5, '修订纪律（贯穿本页所有数字）',
  '• 数字只从冻结证据矩阵生成，禁止手工改表\n'
  + '• 不把 0.6179（=61.79%，v97g mapped-space）与 0.4844（v99 coarse）混为同一个 SATURN 成绩\n'
  + '• 跨方法同表仅作方向性参考，不按总分排名（标签空间/分母/协议三重差异）', { fill: C.goldLight, bodySize: 10.5 });
band(s, '先认领问题，再给答案——这一页决定后面三页的可信度。', 6.35);
notes(s, '开场直接对齐老师的意见，三条逐一回应。');

// 3 总矩阵
s = pptx.addSlide(); chrome(s, '三方法总矩阵（coarse 主结论层，六方向）', 3);
table(s, [
  ['direction', 'ortholog-PCA', 'SATURN v97g', 'SAMap v98', 'v99 统一评分器', '多数类·映射空间', '多数类·原始标签'],
  ['human→mouse', '0.8618', '0.6179', '0.1050', '0.4844', '0.4817', '0.4618'],
  ['mouse→human', '0.7369', '0.2539', '0.0196', '0.1924', '0.3115', '0.2526'],
  ['human→zebrafish', '0.1961', '0.1835', '0.0341', '0.1127', '0.3976', '0.3976'],
  ['mouse→zebrafish', '0.2755', '0.3009', '0.0000', '0.1948', '0.3976', '0.3976'],
  ['zebrafish→human', '0.1813', '0.2474', '0.0000', '0.1872', '0.3115', '0.2526'],
  ['zebrafish→mouse', '0.5761', '0.4651', '0.0000', '0.3375', '0.4817', '0.4618'],
], 0.7, 1.82, 11.9, [2.3, 1.75, 1.6, 1.5, 1.8, 1.55, 1.4], 0.42, 10);
box(s, 0.72, 4.95, 11.9, 1.35, '每列的口径与分母（引用必须随带）',
  'ortholog-PCA：映射词汇 · label-free · candidate-final ｜ SATURN v97g：mapped-space · 日志级 · label-aware（n_q/coverage 保持日志级限定）｜ '
  + 'SAMap v98：原始标签+过滤 · label-aware · candidate-final（探索性复现）｜ v99：原始标签 · exact/coarse 双报 · provenance confirmed\n'
  + 'coarse 层 n_q 逐方向（h→m / m→h / h→z / m→z / z→h / z→m）：ortholog-PCA 与 v99 = 1,505 / 1,528 / 1,499 / 1,499 / 1,528 / 1,505；SAMap = 1,505 / 1,528 / 1,496 / 1,496 / 1,528 / 1,505（鱼方向差 3 待核验）\n'
  + '多数类按标签空间分列（映射空间 = oPCA/v97g；原始标签 = v99/SAMap）；SAMap 鱼方向 majority 0.3977 与 v99 的 0.3976 差异源于 n_q 差 3。', { fill: C.blueLight, bodySize: 8.5 });
band(s, '规则：不做总分排名；跨列标签空间/分母不同，仅作方向性参考（表中未加粗，避免被读成排名）。', 6.35);
notes(s, '总矩阵是老师那张表的正式替代版；每列口径必须随表出现。');

// 4 旧→新替换
s = pptx.addSlide(); chrome(s, '逐项替换：旧 PPT → 本轮版本', 4);
table(s, [
  ['位置', '旧版本（作废/过时）', '本轮版本', '依据'],
  ['ortholog-PCA 表', '80.9 / 38.3 / 40.5 / 22.4 / 11.9 / 79.5', '86.18 / 73.69 / 19.61 / 27.55 / 18.13 / 57.61', '统一评分器 candidate-final（汇报 4）'],
  ['SAMap 列', '早期探索数字（约 2% / 39% 等）', 'WDL 六方向 0.1050 / 0.0196 / 0.0341 / 0 / 0 / 0', 'Phase 6 关账（汇报 6）'],
  ['SAMap 说明', '"v98 尚需修正复跑"', '"WDL 已完成；探索性复现（含口径限制）"', 'phase6-closure-20261005.md'],
  ['SATURN 列', '口径混用风险', 'v97g 与 v99 分列、不合并', 'v74 证据文档 + v99 恢复载荷'],
], 0.7, 1.82, 11.9, [2.0, 4.0, 4.0, 1.9], 0.72, 10);
band(s, '所有替换均有来源文件与 SHA；旧数字只保留为"作废历史草表"记录，不再引用。', 6.35);
notes(s, '替换表本身就是"数据卫生"的证据：每一格都能指出旧值错在哪、新值来自哪。');

// 5 算式页
s = pptx.addSlide(); chrome(s, '从原始数据到表格单元格：86.18% 的完整算式', 5);
table(s, [
  ['步骤', '内容', '值'],
  ['输入', 'reference = 人；query = 鼠', '1,528 / 1,535 细胞'],
  ['归一化', 'normalize_total(1e4) + log1p（全基因空间）', '等价 log1p(CPM/100)'],
  ['同源基因', '人鼠 1:1 直系同源交集', '15,869 基因'],
  ['表示层', '人+鼠联合 PCA-50（seed 0，transductive）', '3,063 × 50'],
  ['排除', '鼠侧 status≠active（Proliferating cell）', '剔 30'],
  ['分母', '1,535 − 30', 'n_q = 1,505'],
  ['正确数', '逐细胞预测 == 真值', '1,297'],
  ['accuracy', '1,297 ÷ 1,505', '0.8618'],
], 0.7, 1.82, 7.4, [1.3, 4.3, 1.8], 0.42, 10.5);
box(s, 8.3, 1.82, 4.3, 4.3, '这一页要传递的三件事',
  '① 每个百分比都能沿"输入 → 表示层 → 角色 → 评分 → 排除 → 分母 → SHA"完整回溯\n\n'
  + '② 分母不是"总细胞数"：排除 30 后 1,505 才是正确分母\n\n'
  + '③ 输出文件：\nresults/pilot-v1/ortholog-pca-v98/\nmetrics.json\nSHA b2b3ac6b…c725\n（18 份 predictions/ 与 18 份 confusion/ 全在本地，可逐细胞复算）', { fill: C.blueLight, bodySize: 10 });
band(s, '表格里的 0.8618 不是抄来的——它是这个算式的终点，也是可复核链的起点。', 6.35);
notes(s, '算式页直接回应老师"数字要有含金量"的要求：含金量 = 可复核性。');

// 6 为什么数字不同
s = pptx.addSlide(); chrome(s, '为什么方法数字不同：六项对照', 6);
table(s, [
  ['维度', 'ortholog-PCA', 'SATURN', 'SAMap'],
  ['表示层', '1:1 同源 + PCA50', 'ESM2 → macrogenes（1000）', '同源基因图 + 潜空间'],
  ['标签空间', '映射词汇（9 粗类）', 'v97g：mapped-space；v99：原始标签+过滤', '原始标签 + status 过滤'],
  ['标签可见性', 'label-free', 'label-aware（ref_labels）', 'label-aware（keys=cell_type）'],
  ['分母 n_q（h→m）', '1,505（排除 30）', 'v99 coarse 1,505；v97g≈1,505（日志级）', '1,505'],
  ['协议', 'transductive', 'transductive', 'transductive'],
  ['算力/失败模式', 'CPU 17.9s；无失败', 'GPU 4090；离线通道历史问题', 'CPU 1c4g 16min；14 次环境排障'],
], 0.7, 1.82, 11.9, [2.2, 3.1, 3.3, 3.3], 0.44, 10.5);
box(s, 0.72, 5.02, 11.9, 1.15, '结论',
  '同一批细胞上的三列数字差异，来自以上六项的协议差异——不是三个"模型能力"的直接对比。'
  + '这正是为什么总矩阵不排冠军、只作方向性参考。', { fill: C.goldLight, bodySize: 10.5 });
band(s, '老师问题专页到此闭环：表更新、来源齐、协议明、不误导。', 6.35);
notes(s, '六项对照与汇报 3 的协议矩阵一致，此处压缩成一页供老师快速核对。');

// 7 引用纪律与结论
s = pptx.addSlide(); chrome(s, '引用纪律与下一阶段', 7);
box(s, 0.72, 1.82, 6.3, 4.3, '写进任何报告/PPT 的引用纪律',
  '① 每个 acc 必须并列 n_q 与 coverage\n\n② 跨方法 coarse 层不排总分（标签空间不同）\n\n③ SATURN 双口径分列：0.6179（=61.79%，v97g）与 0.4844（v99）不合并\n\n④ 全部标注 transductive / in-sample\n\n⑤ 单 seed 点估计（鱼方向 seed 双峰已证实）\n\n⑥ SAMap 标注探索性复现 + 脚本口径限制\n\n⑦ 数字唯一出处：final-evidence-matrix-20261005.md', { fill: C.blueLight, bodySize: 10.5 });
box(s, 7.28, 1.82, 5.32, 4.3, '下一阶段（汇报 8-10）',
  '• 汇报 8：mapping v1 人工签认与证据责任\n  （AI 复核 ≠ 导师签认）\n\n• 汇报 9：最小 inductive 方案\n  （留一物种 × 3 方法 × 3 seed = 81 格设计，\n  仅设计，不自动运行）\n\n• 汇报 10：阶段收口与下一阶段路线\n  （版本化 Word/PPT + 批准清单）', { fill: C.goldLight, bodySize: 10.5 });
band(s, '本页同时是给老师的一页速查：表已更新、口径已列明、下一步已规划。', 6.35);
notes(s, '收尾页兼顾"汇报结论"与"老师速查卡"两个用途。');

pptx.writeFile({ fileName: out }).then(() => console.log('PPTX_DONE ' + out));
