// 第 6/10 次汇报：SAMap 复现与负结果解释
// 数字来源：docs/phase6-closure-20261005.md、results/pilot-v1/samap-v98/wdl-run/extracted/metrics.json
const T = require('./lib/report-template.js');
const { newDeck, cover, chrome, box, band, table, notes, C } = T;

const pptx = newDeck({ title: '课题5第6次汇报：SAMap 复现与负结果' });
const out = 'D:/projects/course5-prep/results/stage-reports-20261009/课题5第06次汇报_SAMap复现与负结果.pptx';

// 1 封面
cover(pptx, {
  title: '课题5 第 6 次汇报：SAMap 复现与负结果解释',
  subtitle: '低分/零分是怎样得到的：哪些是运行限制，哪些是方法学观察',
  meta: '汇报 6 / 10 · 主证据：WDL 任务 W202610050003104 ｜ 口径：transductive / in-sample · label-aware · 2026 年 10 月',
});

// 2 复现路线
let s = pptx.addSlide(); chrome(s, '复现路线：绕开故障通道，WDL 一次成功', 2);
box(s, 0.72, 1.82, 5.8, 4.3, '为什么不在原通道跑',
  '• 离线通道（s 型队列）故障：\n  任务 Pending 停滞 40+ 小时\n• 工单 TK20261003235804338 加急中\n• 根因（后经工单确认）：镜像地址错误\n  导致拉取失败，与排队无关\n\n决策（用户批准）：改走 WDL 流程通道\n• QC_plot 实测调度正常\n• runtime docker_url 复用 SATURN--22 公共镜像', { fill: C.blueLight, bodySize: 10.5 });
box(s, 6.78, 1.82, 5.82, 4.3, 'WDL 排障 14 次（每次都有日志）',
  '① 镜像缺失 → 换公共镜像\n② pip 解释器错绑（系统 vs conda）\n   → python3 -m pip\n③ OpenBLAS 线程爆炸 OOM\n   → 限制线程数\n④ mo/ms 键名不一致（脚本 bug）\n   → 双键前缀映射 {hu,mo,ms,zf} 修复\n\n依赖栈：复用 963bb09e 工作区预建 pylibs\n（809MB → 210MB tar，零编译）', { fill: C.goldLight, bodySize: 10.5 });
band(s, '14 次失败是"诊断—修复"迭代，每次都有归档；不是盲目重试，最终一次成功。', 6.35);
notes(s, '这页讲工程事实：通道选择与排障纪律，为结果的"可信度"提供背景。');

// 3 任务与产物
s = pptx.addSlide(); chrome(s, '任务、脚本与产物（全部可核对）', 3);
table(s, [
  ['项', '值', '说明'],
  ['WDL 任务', 'W202610050003104', '前序 14 次失败有归档，最终版一次成功'],
  ['运行脚本', 'md5 56bb6035（410 行版）', '非 Phase 5 修复版 0a2063d3（见限制页）'],
  ['依赖栈', 'samap 1.0.16 + samalg 1.0.2 + hnswlib shim', '预建 pylibs 复用，非重装'],
  ['产物', 'samap_result.tar.gz（481,920 B）', 'id 0e3741b17b25439e98243f821b1c8cc3'],
  ['本地归档', 'wdl-run/（tar + extracted/ 21 文件）', 'metrics.json SHA 3c719399…954f'],
], 0.7, 1.82, 11.9, [2.2, 5.4, 4.3], 0.62, 10.5);
band(s, '六方向 × 三层 = 18 格结果全部有文件级证据（不再是"待复跑"状态）。', 6.35);
notes(s, '产物链条：任务号 → tar → 解包 21 文件 → metrics SHA。');

// 4 18 格结果
s = pptx.addSlide(); chrome(s, '结果：18 格全部 ≤ 10.5%，三方向为零', 4);
table(s, [
  ['direction', 'exact', 'coarse', 'fine', 'n_q(coarse)', '多数类'],
  ['human→mouse', '0.1029', '0.1050', '0.1050', '1,505', '0.4618'],
  ['human→zebrafish', '0.0331', '0.0341', '0.0341', '1,496', '0.3977'],
  ['mouse→human', '0.0196', '0.0196', '0.0196', '1,528', '0.2526'],
  ['mouse→zebrafish', '0.0000', '0.0000', '0.0000', '1,496', '0.3977'],
  ['zebrafish→human', '0.0000', '0.0000', '0.0000', '1,528', '0.2526'],
  ['zebrafish→mouse', '0.0000', '0.0000', '0.0000', '1,505', '0.4618'],
], 0.7, 1.82, 11.9, [3.0, 1.7, 1.7, 1.7, 2.0, 1.8], 0.44, 10.5);
box(s, 0.72, 5.02, 11.9, 1.15, '读数',
  '• 全部 18 格 ≤ 10.5%；三个方向为 0（鼠→鱼、鱼→人、鱼→鼠），鼠→人 0.0196 接近 0\n'
  + '• 全部远低于对应多数类（0.25–0.46）；其中 human→mouse / human→zebrafish 优于随机（shuffle_p 0.0 / 0.035），其余方向与随机不可区分（shuffle_p 1.0）\n'
  + '• confusion 显示预测大量塌缩到单一类别（h→m：内皮 695 个中 634 个被预测为 Lymphoid）', { fill: C.roseLight, bodySize: 10 });
band(s, '负结果本身是可复现的结论：低分不是运行失败，是方法在当前协议下的真实表现。', 6.35);
notes(s, '这页是全场数字最"低"的一页；先摆事实，再讲读法。');

// 5 负结果怎么读
s = pptx.addSlide(); chrome(s, '负结果的三层读法', 5);
box(s, 0.72, 1.82, 3.9, 4.3, '第一层：不能读成',
  '✗ "SAMap 无效"\n✗ "工具坏了"\n✗ "跨物种对齐不可能"\n\n理由：\n• 结果为可复现的运行产物\n• 同批次 ortholog-PCA 在同数据上\n  有强信号（86.18%）\n• 说明数据本身可对齐；\n  更可能是 SAMap 当前配置未提取到信号（待检验）', { fill: C.roseLight, bodySize: 10.5 });
box(s, 4.72, 1.82, 3.9, 4.3, '第二层：可以读成',
  '✓ "在 label-aware 协议下，当前配置\n   （NUMITERS=3、keys=cell_type）\n   未产生有迁移能力的联合表示"\n\n？ "未产生可分联合流形"是待检验解释\n   （需表示层可分性分析，本轮未做）\n\n？ "图对齐在小样本/远缘物种不稳定"\n   同为待检验解释\n\n→ 可确认的是结果本身；\n   机制解释留待后续', { fill: C.blueLight, bodySize: 10.5 });
box(s, 8.72, 1.82, 3.88, 4.3, '第三层：待回答',
  '？ 换 keys / 提高 NUMITERS 是否有改善\n  （属新实验，需批准）\n\n？ 零分方向的预测是否全部塌缩\n  到单一类别（confusion 已显示 h→m 如此）\n\n？ 负结果与物种距离的关系\n  （三个零分方向均含鱼；但人→鼠 0.1050、\n   人→鱼 0.0341 高于鼠→人 0.0196，\n   格局并非按物种距离单调）\n\n→ 留给后续讨论，不在本轮下结论', { fill: C.goldLight, bodySize: 10.5 });
band(s, '负结果的价值在于边界清晰：它约束了"跨物种对齐有多难"，而不是宣布"做不到"。', 6.35);
notes(s, '三层读法是审阅重点：防止过度推广为"工具无效"。');

// 6 两个口径限制
s = pptx.addSlide(); chrome(s, '两个必须声明的限制', 6);
box(s, 0.72, 1.82, 5.8, 2.05, '限制一：label-aware',
  '• keys=cell_type 使真值标签参与联合图构建\n• 这是 SAMap 的原生工作流，但它意味着\n  它不是 label-free 方法\n• 与 ortholog-PCA（label-free）不可直接互比', { fill: C.roseLight, bodySize: 11 });
box(s, 6.78, 1.82, 5.82, 2.05, '限制二：脚本版本混合口径',
  '• 本次运行 = WDL 实际脚本（410 行版 md5 56bb6035）\n• Phase 5 修复版（0a2063d3）在 WDL 环境未运行\n• per_cell 的 included 旗标（1,398）与 n_q（1,505）\n  口径不同且不参与 acc——引用以 n_q/acc 为准', { fill: C.roseLight, bodySize: 11 });
box(s, 0.72, 4.05, 11.9, 2.1, '这些限制怎么影响结论',
  '① 影响"可比性"：与 label-free 方法的对比必须声明协议差异（汇报 3 已建立规则）\n'
  + '② 影响"精确复算"：复算 acc 必须按全部 query 行（158 ÷ 1,505 = 0.1050），误用 included 旗标会得到 158 ÷ 1,398 = 0.113\n'
  + '③ 不影响方向性结论：18 格各按各自分母计算（n_q 1,496–1,528），全部 ≤ 10.5%；158 ÷ 1,505 仅为 h→m coarse 示例；included 旗标（1,398）不是另一种合法计分口径', { fill: C.blueLight, bodySize: 11 });
band(s, '限制讲清楚之后，负结果依然成立——这才是"可复核的负结果"。', 6.35);
notes(s, '限制页是 Claude 审阅要求的核心：脚本版本 + per_cell 旗标必须随数字出现。');

// 7 排障记录的价值 + 结论
s = pptx.addSlide(); chrome(s, '排障记录的方法学价值与结论', 7);
table(s, [
  ['根因类别', '具体问题', '修复方式'],
  ['镜像/环境', '镜像缺失、拉取失败', '换公共镜像 SATURN--22'],
  ['依赖', 'pip 解释器错绑、BLAS 线程 OOM', 'python3 -m pip；限制线程数'],
  ['脚本', 'mo/ms 键名不一致', '双键前缀映射 {hu,mo,ms,zf}'],
  ['通道', '离线队列停滞', 'WDL 通道（经批准）'],
], 0.7, 1.82, 11.9, [2.4, 5.0, 4.5], 0.5, 10.5);
box(s, 0.72, 4.35, 5.8, 1.8, '结论（可复述）',
  '• SAMap v98 在 WDL 通道成功复现，18 格产物齐全\n• 负结果与本地审计方向一致，可复现、可复核\n• 证据等级：candidate-final（探索性复现）', { fill: C.blueLight, bodySize: 10.5 });
box(s, 6.78, 4.35, 5.82, 1.8, '下一步（待批准）',
  '• 如需精确对齐 Gate-5 口径：用 Phase 5 修复版\n  脚本在同一 WDL 重投（属新任务）\n• 换 keys / NUMITERS 的敏感性实验\n• 全部留待 inductive 设计（汇报 9）统一安排', { fill: C.goldLight, bodySize: 10.5 });
band(s, '下一阶段（汇报 7）：三方法总矩阵——把六方向 × 三方法放在一张可审计的表里。', 6.35);
notes(s, '排障四类根因也是"平台使用经验"的沉淀，对后续任务有价值。');

pptx.writeFile({ fileName: out }).then(() => console.log('PPTX_DONE ' + out));
