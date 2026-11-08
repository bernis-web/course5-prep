// 第 10/10 次汇报：阶段收口与下一阶段路线
// 来源：docs/reports/report-10-closure-and-next-phase-20261008.md、docs/evidence/status-matrix-20261008.md
const T = require('./lib/report-template.js');
const { newDeck, cover, chrome, box, band, table, notes, C } = T;

const pptx = newDeck({ title: '课题5第10次汇报：阶段收口与下一阶段' });
const out = 'D:/projects/course5-prep/results/stage-reports-20261009/课题5第10次汇报_收口与下一阶段.pptx';

// 1 封面
cover(pptx, {
  title: '课题5 第 10 次汇报：阶段收口与下一阶段路线',
  subtitle: 'Phase 1–8 完成清单、待决事项与下一阶段批准清单',
  meta: '汇报 10 / 10 · 全部数字可溯源至 SHA 锚定的 metrics.json ｜ 口径：transductive / in-sample · 单 seed（0）· 2026 年 10 月',
});

// 2 Phase 1-8 完成清单
let s = pptx.addSlide(); chrome(s, 'Phase 1–8 完成清单', 2);
table(s, [
  ['Phase', '内容', '门/状态'],
  ['1', 'v99 provenance 恢复与确认', 'Gate 1 pass（file-level confirmed）'],
  ['2', 'ortholog-PCA Gate-2 重写（neighbor 修复 + 口径统一）', '完成'],
  ['3', 'smoke 全绿', '113 tests'],
  ['4', 'ortholog-PCA 全量 candidate-final', 'Gate 4 pass'],
  ['5', 'SAMap v98 双变体修复', 'Gate 5 pass'],
  ['6', 'SAMap WDL 复现（14 次排障）', '复核通过（candidate-final）'],
  ['7', '导师邮件定稿（映射签认请求）', 'Claude/Genpilot 双审 pass'],
  ['8', 'Word 报告 + 终版 PPT + 证据矩阵 + inductive 设计', '完成'],
], 0.7, 1.82, 11.9, [1.0, 7.4, 3.5], 0.44, 10.5);
band(s, '八个 Phase 全部关账；本页同时是"做过什么"的最短索引。', 6.35);
notes(s, '完成清单：每一项都有对应关账报告与 SHA 锚点。');

// 3 最终数字一页
s = pptx.addSlide(); chrome(s, '最终数字一页（全部可溯源）', 3);
table(s, [
  ['数字', '来源文件', '验证方式'],
  ['0.8618 / 1297 / 1505（oPCA h→m）', 'ortholog-pca-v98/metrics.json（SHA b2b3ac6b…c725）', '本地逐细胞重算 ✓'],
  ['0.1961 / 294 / 1499（oPCA h→z）', '同上', '本地逐细胞重算 ✓'],
  ['0.6179（SATURN v97g h→m）', 'v74 证据文档（EVAL3G 日志）', '日志级（无逐细胞文件）'],
  ['0.4749 / 0.4844（SATURN v99）', 'saturn-v99/raw/recovered-20261001（SHA d1081cfd…dc261）', '本地逐细胞重算 ✓'],
  ['0.1050 / 158 / 1505（SAMap h→m）', 'samap-v98/wdl-run/extracted（SHA 3c719399…954f）', '本地 per_cell 重算 ✓'],
  ['映射表 v1（38 行）', 'config/heart-celltype-map-v1.tsv（SHA be985735…3165）', '五方对账 ✓（待导师签认）'],
], 0.7, 1.82, 11.9, [3.3, 5.6, 3.0], 0.48, 10);
box(s, 0.72, 5.32, 11.9, 0.9, '口径警示（随全部数字）',
  'transductive/in-sample；跨方法标签空间与分母不同不可直接排名；SATURN 双口径不合并；单 seed 点估计；SAMap 为探索性复现（脚本口径限制）。',
  { fill: C.goldLight, bodySize: 10 });
band(s, '全部数字的唯一出处：docs/final-evidence-matrix-20261005.md（版本冻结）。', 6.35);
notes(s, '数字总览页：给老师一个"抽查入口"清单。');

// 4 交付物清单
s = pptx.addSlide(); chrome(s, '交付物清单（版本化；可核实旧件保留）', 4);
table(s, [
  ['类别', '文件', '说明'],
  ['证据矩阵', 'docs/final-evidence-matrix-20261005.md', '全部数字唯一出处'],
  ['状态矩阵', 'docs/evidence/status-matrix-20261008.md（v1.1）', '26+6 项逐项状态，Claude pass'],
  ['Word 报告', 'deliverables/（Phase 8 版）', '阶段报告（旧版保留）'],
  ['PPT', 'results/phase1-revised-v2/ 终版 + 本阶段汇报序列 1–10', '老师批语修订版 + 校模板版'],
  ['审阅记录', 'docs/reports/claude-review-*.md', '逐阶段 Claude 审阅意见'],
  ['AI 复核意见书', 'docs/mapping-v1-ai-review-opinion-20261005.md', '映射表终签的降维材料'],
], 0.7, 1.82, 11.9, [2.2, 5.6, 4.1], 0.55, 10);
band(s, '可沿 SHA 回溯（SHA256SUMS.txt）；可核实原始旧件保留；中间修订版曾原地重建、未单独归档，历史"未覆盖"声明待基线核验。', 6.35);
notes(s, '交付清单强调"版本化 + 不覆盖"。');

// 5 待决事项
s = pptx.addSlide(); chrome(s, '待决事项（需要人做决定的部分）', 5);
table(s, [
  ['#', '事项', '谁决定', '状态'],
  ['1', '发送导师邮件（映射签认 + 阶段汇报）', '用户/导师', '待发送'],
  ['2', '映射表 v1 人工签认（5 个议题，涉及 6 条源映射）', '导师', 'needs-reviewer'],
  ['3', '平台工单回复（镜像地址修正）', '用户/平台', '待回复'],
  ['4', 'inductive 实验是否运行（GPU 预算）', '用户/导师', '待批准'],
  ['5', 'Codex 只读审计（第 1 轮已回：revise）', '用户', '修订后复审'],
], 0.7, 1.82, 11.9, [0.7, 5.6, 2.4, 3.2], 0.5, 10.5);
box(s, 0.72, 4.95, 11.9, 1.3, '本地材料已就绪；逐册评审与外部确认待闭环',
  '• 邮件文本、附件清单、锚点 SHA 已备好（Claude 审阅 pass）\n'
  + '• 签认只解除 mapping 相关的 needs-reviewer 标注；其它结论的证据等级不因签认改变\n'
  + '• inductive 方案为候选设计：批准后先验证投影接口，再跑最小版', { fill: C.blueLight, bodySize: 10 });
band(s, '本阶段状态：材料初稿齐备；逐册评审与外部确认（签认/预算/审计）待闭环。', 6.35);
notes(s, '待决事项页把"需要人做的事"和"已做完的事"分开列。');

// 6 下一阶段路线
s = pptx.addSlide(); chrome(s, '下一阶段路线（等反馈后启动）', 6);
table(s, [
  ['触发条件', '下一步动作', '产物'],
  ['导师反馈（签认/修改意见）', '按意见修订映射表 v2 并重走 hash 链与对账', 'mapping v2 + 对账记录'],
  ['导师反馈（对结论的意见）', '定向修订 Word/PPT（保留旧版）', '修订版报告（带 diff 说明）'],
  ['预算与通道批准', '先验证投影接口，再跑 inductive 最小版（鱼留出 × 3 方法 × seed 0）', '3 格 inductive 结果'],
  ['最小版通过', '扩到完整 81 格（3 物种 × 3 seed × 三层）', '泛化矩阵 + seed 稳定性'],
  ['平台通道修复', '可选：Phase 5 修复版脚本重投 SAMap（精确对齐 Gate-5 口径）', '口径统一版 SAMap 结果'],
], 0.7, 1.82, 11.9, [3.4, 5.6, 2.9], 0.66, 10);
band(s, '全部下一步都有明确的触发条件与停止条件——不因等待而空转，也不因进度而抢跑。', 6.35);
notes(s, '路线页：每个下一步都绑定触发条件，避免"等反馈期间乱动"。');

// 7 收口结论
s = pptx.addSlide(); chrome(s, '收口结论', 7);
box(s, 0.72, 1.82, 6.3, 4.3, '本阶段做到了什么',
  '• 六个方向数字可复核：oPCA/SAMap 逐细胞复算；v99 载荷逐细胞复算；SATURN v97g 为日志级\n'
  + '• 每个百分比都能沿"输入 → 表示层 → 角色 → 评分\n  → 排除 → 分母 → SHA"完整回溯\n'
  + '• 方法边界写清楚了：标签空间、分母、label 属性、\n  算力差异、transductive 限制\n'
  + '• 负结果（SAMap）与弱信号（鱼方向）如实报告，\n  并给出可复核的证据链\n'
  + '• 下一阶段（inductive）设计就绪，预算与停止条件明确', { fill: C.blueLight, bodySize: 10.5 });
box(s, 7.28, 1.82, 5.32, 4.3, '本阶段没有做什么（如实声明）',
  '• 没有跑 inductive（设计 ≠ 运行）\n'
  + '• 没有做多 seed（除 SATURN 侧已有的稳定性证据）\n'
  + '• 没有做湿实验验证\n'
  + '• 没有对每个方法调参到最优（不是调参竞赛）\n'
  + '• 没有把任何 AI 复核当成人工签认\n\n'
  + '以上缺口均已在证据矩阵与状态矩阵中登记。', { fill: C.roseLight, bodySize: 10.5 });
band(s, '汇报材料 1–10 初稿齐备；逐册 Claude 评审与外部确认待闭环，之后按反馈定向修订。', 6.35);
notes(s, '收口：左边成果、右边缺口，两边都写，才算完整交代。');

pptx.writeFile({ fileName: out }).then(() => console.log('PPTX_DONE ' + out));
