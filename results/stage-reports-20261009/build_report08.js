// 第 8/10 次汇报：mapping reviewer 与证据责任
// 来源：docs/mapping-v1-ai-review-opinion-20261005.md、docs/phase7-email-final-20261005.md、config/heart-celltype-map-v1.tsv
const T = require('./lib/report-template.js');
const { newDeck, cover, chrome, box, band, table, notes, C } = T;

const pptx = newDeck({ title: '课题5第8次汇报：mapping 签认与证据责任' });
const out = 'D:/projects/course5-prep/results/stage-reports-20261009/课题5第08次汇报_映射签认与证据责任.pptx';

// 1 封面
cover(pptx, {
  title: '课题5 第 8 次汇报：映射表签认与证据责任',
  subtitle: 'AI 复核 ≠ 导师签认——人工终签前的透明说明',
  meta: '汇报 8 / 10 · 对象：config/heart-celltype-map-v1.tsv（SHA be985735…3165，38 行）｜ 状态：needs-reviewer ｜ 2026 年 10 月',
});

// 2 映射表是什么
let s = pptx.addSlide(); chrome(s, '映射表是什么、为什么每个数字都依赖它', 2);
table(s, [
  ['项', '内容'],
  ['文件', 'config/heart-celltype-map-v1.tsv（38 行数据）'],
  ['SHA-256', 'be9857354778535b76d1884d004c54691dc5ff2daa7b098d71dc719daf583165'],
  ['结构', '双层：coarse（9 粗类）+ fine（17 细类）；status 列（active / unmapped）'],
  ['来源', '人/鼠/斑马鱼心脏图谱原始标签 → 课题组映射（marker 依据逐行记录）'],
], 0.7, 1.82, 11.9, [2.0, 9.9], 0.48, 10.5);
box(s, 0.72, 4.35, 5.8, 1.8, '它影响什么（两条硬联系）',
  '• 影响标签空间：ortholog-PCA 的 coarse/fine 是\n  "映射后词汇"（9 粗类）——其它方法的 coarse\n  是原始标签，两者差异源头就在这里\n• 影响分母：3 行 status=unmapped 的细胞\n  （mouse Prolif 30 / zf mt 30 / zf Prolif 14）\n  不入 mapped 分母，coverage 单列', { fill: C.roseLight, bodySize: 10 });
box(s, 6.78, 4.35, 5.82, 1.8, '为什么需要人工签认',
  '• 按课题纪律：reviewer 签认前不得宣称正式 benchmark\n• 映射表是"评估基准"的一部分，\n  基准的正确性责任在人，不在 AI\n• 本页与附件意见书的作用：\n  把 38 行的复核负担降到"看 4 行 + 局限性"', { fill: C.blueLight, bodySize: 10 });
band(s, '一句话：这张表决定"哪些细胞计分、按什么类别计分"——它是所有方法数字的地基。', 6.35);
notes(s, '开场建立"为什么这张 38 行的表值得老师花十分钟"。');

// 3 复核总览
s = pptx.addSlide(); chrome(s, 'AI 独立复核：九项检查结果总览', 3);
table(s, [
  ['#', '核验项', '结果'],
  ['①', '38 行逐行 marker 文献核查', '通过（附条件）：A 档 22 行 / B 档 11 行 / C 档 2 行 / n/a 3 行（合计 38）'],
  ['②', '物种-基因符号命名规范', '通过：0 真违规（6 处脚本误报经人工排除）'],
  ['③', 'TSV ↔ 冻结报告双向核对', '通过（2 个文档级小缺口，非表缺陷）'],
  ['④', '排除规则对账', '通过：mouse 30 / zf 44 / human 0 四方闭环 + SAMap 差 3 待核验（见下页）'],
  ['⑤', 'hash 链内容等价', '通过：内嵌映射 38 行三元组逐行等价'],
  ['⑥', '数据侧证据盘点', '26 行直接证据 + 1 行间接；8 行仅文献级（全部 canonical 或已披露低置信）'],
  ['⑦', '三个争议点文献级判断', '全部支持保留当前归类（candidate）'],
  ['⑧', '局限性声明', '见意见书 §八（6 条）'],
  ['⑨', '证据等级标定', '程序化验证 = confirmed；文献级判断 = candidate'],
], 0.7, 1.82, 11.9, [0.7, 3.6, 7.6], 0.40, 9.5);
band(s, '结论：无阻塞项；复核意见书已随邮件附件提供（供导师终签参考，不构成签认）。', 6.35);
notes(s, '九项里重点是 ①④⑦：逐行核查、五方对账、争议判断。');

// 4 五方对账
s = pptx.addSlide(); chrome(s, '排除规则对账（30 / 44 / 0；SAMap 差 3 待核验）', 4);
table(s, [
  ['对账方', 'mouse', 'zebrafish', 'human'],
  ['映射表 TSV（status=unmapped）', '30（Proliferating）', '44（mt 30 + Prolif 14）', '0'],
  ['v99 metrics（n_excluded_q）', '30', '44', '0'],
  ['ortholog-PCA（coverage_q 反推）', '30', '44', '0'],
  ['SAMap（n_excluded_q）', '30', '47*', '0'],
  ['证据矩阵 §六（排除普查）', '30', '44', '0'],
], 0.7, 1.82, 11.9, [4.4, 2.6, 3.4, 1.5], 0.44, 10.5);
box(s, 0.72, 4.62, 11.9, 1.5, 'SAMap 的 3 细胞差额（待核验）',
  '* SAMap 鱼方向 n_q=1,496（n_excluded_q=47），与映射表 44 相差 3 个细胞——差额为事实；具体根因待核验（此前归因于运行脚本混合口径，尚无独立证据）。\n'
  + '结论：TSV / v99 / ortholog-PCA / 证据矩阵四方对账一致；SAMap 的 3 细胞差额单独标注，引用其鱼方向数字时随带说明。', { fill: C.goldLight, bodySize: 10 });
band(s, '对账的价值：排除规则不是"清洗"，而是协议——四方一致 + SAMap 差 3 待核验，逐项标注。', 6.35);
notes(s, '对账页：四方闭环 + 一处待核验差额，不宣布"全部一致"。');

// 5 四个低置信映射
s = pptx.addSlide(); chrome(s, '请导师重点审阅的 5 个议题（涉及 6 条源映射）', 5);
table(s, [
  ['#', '映射', '置信', '文献级判断', '数据侧'],
  ['1', 'mouse Valve + 斑马鱼 Valve → fibroblast', 'low', '瓣膜间质为间叶来源、静止态表达成纤维程序；图谱文献常归入成纤维大类；fine 层保留 VIC 独立', '无直接数据'],
  ['2', '斑马鱼 "Orthers"（原始拼写）→ neural', 'low', '证据偏弱：电压门控通道基因在心肌亦表达；为全表最弱一行，解读须注明', 'rank 10/14（最弱）'],
  ['3', '人 Mesothelial → epicardial', 'medium', '心外膜由 proepicardial 间皮发生，谱系同源成立；fine 层保留 mesothelial 独立', '—'],
  ['4', '斑马鱼 Perivascular → smooth muscle', 'medium', 'rgs5a/pdgfrb/notch3 为 mural 公认程序；coarse 合并为常规做法', 'h→z ρ=0.421，rank 8/14'],
  ['5', '行 25 cmlc1 / vmhc（C 档命名疑点）', 'high（另有命名疑点）', 'cmlc1 与 myl7 疑为同源命名（别名），心室行与心房行分别引用存在内部一致性风险；建议 v2 前用数据表达核实', 'h→z 心室 CM rank-1（反向支持）'],
], 0.7, 1.82, 11.9, [0.5, 3.5, 1.1, 5.2, 1.6], 0.65, 9.5);
band(s, '导师无需逐行审表：认可请回复"确认"，或对任何一行提出修改意见（v1 原件不覆盖）。', 6.35);
notes(s, '这页是邮件的核心请求页：把人工负担压缩到 5 行（4 个低置信 + 1 个命名疑点）+ 局限性声明。');

// 6 证据责任
s = pptx.addSlide(); chrome(s, '证据责任：AI 复核能做什么、不能做什么', 6);
box(s, 0.72, 1.82, 5.8, 4.3, 'AI 复核已做（可复算）',
  '• 程序化核验：逐行比对、计数、覆盖率重算、\n  混淆矩阵拆分（本地 .venv39 可复跑）\n• 文献级核验：依心脏图谱 marker 体系逐行判断\n• hash 链内容等价核验（不止 hash 相同）\n• 对账核验（5 方数据、4 方一致 + SAMap 差 3 待核验）\n• 局限性声明 6 条（见意见书 §八）\n\n证据等级：程序化验证 = confirmed；\n文献级判断 = candidate', { fill: C.blueLight, bodySize: 10.5 });
box(s, 6.78, 1.82, 5.82, 4.3, 'AI 复核不能做（责任边界）',
  '✗ 不能替代人工签认\n✗ 不能替代湿实验验证\n✗ 未做逐簇 DEG 定量复核\n  （仓库无 rank_genes_groups 类产物）\n✗ 未对 Litviňuková 2020 / Hu 2022 原文\n  做实时检索核对\n\n→ 意见书为"降低审阅负担的辅助证据"，\n  表的责任由课题组承担\n→ 签认前 mapping 状态保持 needs-reviewer', { fill: C.roseLight, bodySize: 10.5 });
band(s, '把"AI 复核"与"导师签认"两件事分开写清楚，是本页的全部目的。', 6.35);
notes(s, '责任边界页是 Claude 审阅要求："AI 初审、导师终签"必须写明白。');

// 7 结论与请求
s = pptx.addSlide(); chrome(s, '结论与请求事项', 7);
box(s, 0.72, 1.82, 6.3, 4.3, '当前状态（未签认前）',
  '• mapping v1 状态：needs-reviewer\n• 所有基于映射的结果（coarse/fine 层、\n  排除规则、coverage）标注为\n  "候选基准（pending reviewer）"\n• 正式 benchmark 结论不得发布\n• 修订通道：导师意见 → v2（保留 v1 原件，\n  不覆盖）→ 重新走 hash 链与对账', { fill: C.goldLight, bodySize: 10.5 });
box(s, 7.28, 1.82, 5.32, 4.3, '请求导师的三件事',
  '① 回复"确认"或对 4 个低置信映射与行 25 命名疑点提出修改\n\n② 如有意见：指定行号 + 修改方向即可，\n   课题组负责落表与重跑验证\n\n③ 若需要直接审阅原表：\n   38 行 TSV 随邮件附上\n\n（锚点两枚 SHA 已写入邮件附件清单，\n  签认对象与版本可追溯）', { fill: C.blueLight, bodySize: 10.5 });
band(s, '下一阶段（汇报 9）：最小 inductive 方案——签认与通道恢复后的泛化实验设计。', 6.35);
notes(s, '收尾页给出明确的三项请求，降低导师回复成本。');

pptx.writeFile({ fileName: out }).then(() => console.log('PPTX_DONE ' + out));
