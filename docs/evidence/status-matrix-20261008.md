# 证据状态矩阵（2026-10-08，汇报 1/10：证据状态冻结）

> 逐项状态分类：confirmed（独立审计/双通道互证）/ candidate-final（Gate 复核通过，待 Codex/导师）/ exploratory（初步运行）/ pending（等外部）/ blocked（通道故障）。
> 存在层级区分：**[本地]** 本地文件已存在并校验 / **[容器/日志]** 容器或日志中确认存在 / **[数字级]** 已有数字但无逐细胞文件 / **[已复算]** 已独立复算。状态列中 **待导师人工签认** 属治理状态（非存在层级），出现于 B1。

## A. 评估结果类

| # | 文件或结果 | 证据路径 | SHA-256 | 存在层级 | 状态 | 当前缺口 | 下一步动作 |
|---|---|---|---|---|---|---|---|
| A1 | ortholog-PCA 六方向×三层 metrics | results/pilot-v1/ortholog-pca-v98/metrics.json | b2b3ac6b…c725 | [本地][已复算] | candidate-final | 无（Phase 4 Claude pass） | 汇报 4 基线闭环 |
| A2 | ortholog-PCA manifest（39 文件 SHA 表） | results/pilot-v1/ortholog-pca-v98/manifest.json | 546772c5…608 | [本地] | candidate-final | 无 | 同上 |
| A3 | SAMap v98 六方向×三层 metrics（含 per_cell） | results/pilot-v1/samap-v98/wdl-run/extracted/metrics.json | 3c719399…54f | [本地][容器确认][已复算]（06/06 coarse 层已从本地 per_cell 全行重算，acc 与 metrics 逐向一致） | candidate-final | 脚本 md5 56bb6035 混合口径（旗标 1398≠n_q 1505，已披露）；per_cell included 旗标与 acc 分母语义混合 | 汇报 6 负结果解释 |
| A4 | SAMap WDL manifest | results/pilot-v1/samap-v98/wdl-run/extracted/manifest.json | dc9679f5…e4 | [本地] | candidate-final | 无 | 同上 |
| A5 | v99 统一评分器 metrics（六方向） | results/pilot-v1/saturn-v99/raw/recovered-20261001/metrics.json | **d1081cfd…261**（引用锚点） | [本地][容器确认][已复算] | provenance confirmed / 数字 candidate | v99-vs-v97g 双口径双报不合并 | 汇报 5 SATURN 双口径 |
| A6 | SATURN v97g 六方向数字 | docs/transductive-formal-v74-evidence-20260928.md（EVAL3G 日志引用） | 无独立 SHA（日志级） | [数字级][日志确认] | confirmed（日志级） | 无逐细胞文件；provenance 为日志级 | 汇报 5 引用时并列 v99 |
| A7 | ESM2 消融（67.4→20.4，v72-era 同协议历史配对；v97g 对应消融未重跑） | docs/saturn-smoke-evidence-20260922.md:117 + docs/wave0-evidence-matrix-20260930.md:117 + 勘误三 | 无独立 SHA（日志级） | [数字级][日志确认] | confirmed（方向性） | 原"61.8%→20.4%"为跨协议混排，已按勘误三更正 | 报告引用时带"v72-era 同协议配对 + v97g 未重跑"标注 |
| A8 | 物种内 ceiling（85.5/93.5/74.2） | docs/saturn-smoke-evidence-20260922.md:111 + docs/course5-longrun-state-20260930.md:27 + 证据矩阵 §五 | 无独立 SHA（日志级） | [数字级] | confirmed（成对引用限制；wave0 09-30 曾评 candidate，后被 10-05 冻结版覆盖） | 无 | 报告引用 |
| A9 | seed 稳定性（67.1±3.8；鱼方向双峰） | docs/saturn-smoke-evidence-20260922.md:125 + docs/teammate-notice-20260921.md:49 + 证据矩阵 §五 | 无独立 SHA（日志级） | [数字级] | confirmed（方向性） | 单 seed 限制已在口径警示 | 报告引用 |

## B. 冻结输入与映射

| # | 文件或结果 | 证据路径 | SHA-256 | 存在层级 | 状态 | 当前缺口 | 下一步动作 |
|---|---|---|---|---|---|---|---|
| B1 | 冻结映射表 v1（38 行 TSV） | config/heart-celltype-map-v1.tsv | **be985735…3165** | [本地] | **待导师人工签认**（AI 意见书已出） | 导师终签（AI 意见书已降维其负担至重点 3 处） | 邮件发送 → 导师回复 |
| B2 | v99 内嵌映射（语义等价已验证） | results/pilot-v1/saturn-v99/raw/recovered-20261001/v99_mapping_embedded.json | **d92e32aa…e4a** | [本地][已复算] | confirmed（与 B1 语义等价） | 无 | 随 B1 一并签认 |
| B3 | 三物种 h5ad（人 1528/鼠 1535/鱼 1543） | /Files/ResultData/Notebook/*.h5ad（平台）+ 本地 pilot 子集 | 容器 md5 3458dcb9/8a0c9f53/acea9d74 为 Genpilot 会话内实测（其容器 /data/work 与 /Files 推送副本全等；两值不可本地复算，本地 pilot 子集 md5 不同属预期——平台侧重存过） | [容器确认][本地子集] | confirmed（输入层；本地等价性以细胞数/金标准标签/任务读取成功间接佐证） | 容器 md5 无本地在库锚点（已如实标注为会话内证据） | 无 |

## C. 审计与治理文件

| # | 文件或结果 | 证据路径 | SHA-256 | 状态 | 当前缺口 | 下一步动作 |
|---|---|---|---|---|---|---|
| C1 | AI 复核意见书（映射表 v1） | docs/mapping-v1-ai-review-opinion-20261005.md | 4932804f…3db | [本地] | 2 个 C 档行（cmlc1 命名、Orthers 通道基因）需数据核实；AI 非独立第三方局限已声明 | 导师终签时随附 |
| C2 | Phase 1 关账报告 | docs/phase1-closure-20261004.md | b0bf1ec3…26d | [本地] | 无 | 已归档 |
| C3 | Phase 6 关账报告 | docs/phase6-closure-20261005.md | 685a99dd…245 | [本地] | 无 | 已归档 |
| C4 | ortholog-PCA 证据矩阵 | docs/final-evidence-matrix-ortholog-pca-20261003.md | 11b57747…6c8 | [本地] | 无 | 已归档 |
| C5 | 过程 checkpoint（§1–22） | docs/checkpoint-flash-20261002-evening.md | d1cf4d16…b1d | [本地] | 无 | 随本矩阵更新 |
| C6a | Phase 7 邮件定稿（B1 签认流程核心载体） | docs/phase7-email-final-20261005.md | e025e7de…c12（全值见 .tmp-status-shas.json） | [本地] | 定稿 v3（AI 初审+导师终签模式，Claude 复核 pass 可发送） | 待用户发送导师 |
| C6b | 工单追评文案（E1/E5 待执行件） | docs/ticket-followup-text-20261005.md | （见 git 4ee4847） | [本地] | 待用户粘贴到工单详情页 | 用户操作 |
| C6c | v99/v97g 双口径依据 | docs/v99-score-reconciliation-20261001.md | （见 git） | [本地] | 支撑 A5 双报不合并 | 汇报 5 引用 |
| C6d | 旧草表作废依据 | docs/stale-numbers-audit-20261003.md | （见 git） | [本地] | 支撑 D3 旧数字作废说明 | 汇报 4 引用 |
| C6 | AI 使用日志 | docs/ai-usage-log-20261003.md | b44450944ccf3ea8…（全值见 git） | [本地] | 10-05 后（汇报周期）段待补 | 终稿时更新 |

## D. 交付物

| # | 文件 | 证据路径 | SHA-256 | 状态 | 当前缺口 | 下一步动作 |
|---|---|---|---|---|---|---|
| D1 | Word 终版报告 | deliverables/course5-final-report.docx | 548f0a74…495 | [本地] | 表格数字由脚本从 metrics.json 直接读入（无手工数字）；待导师/Codex 审阅 | 随汇报周期更新 |
| D2 | 终版 PPT（12 页） | deliverables/course5-final-presentation.pptx | 51d9eb1d…4ec | [本地] | 同上 | 随汇报周期更新 |
| D3a | 旧版 Monday PPT（10-05 02:01，13 页，比 D2 更新的中间产物） | deliverables/course5-monday-presentation.pptx | （未本轮计算） | [本地] | 中间迭代产物，非对外终稿；终稿为 D2 | 无（保留存档） |
| D3 | 旧版 PPT（老师批语版） | results/phase1-revised/课题5第一阶段成果汇报_老师批语修订版.pptx | （未本轮计算） | **blocked** | **核心表仍用作废草表 80.9/38.3/40.5/22.4/11.9/79.5；SAMap 表述过时（"v98 尚需修正复跑"）** | 汇报周期后以冻结数字重建为新文件（results/phase1-revised-v2/），不覆盖旧件 |

## E. 平台与任务状态

| # | 项 | 证据 | 状态 | 当前缺口 | 下一步动作 |
|---|---|---|---|---|---|
| E1 | 离线任务调度通道（个性分析 s 类） | 工单 TK20261003235804338 + 三档复现记录（1c4g/2c8g/4c16g 全 Pending）+ 全平台用户任务 0 启动 | **blocked** | 平台侧未响应；工单已加急+追评文案已备（docs/ticket-followup-text-20261005.md，用户待粘贴） | 等平台回复 / 用户粘贴追评 / 导师协助催办 |
| E2 | WDL 流程通道 | QC_plot（实测正常调度）+ runsamap（W202610050003104 成功，运行约 16 分钟） | confirmed（可用） | 无 | Phase 6 已用此通道关账 |
| E3 | R1d（g5-v99-rec-r1d-1，2106401728586420226，4c16g） | subTask/get 多轮探查 | **pending**（10-03 23:11 提交¹〔checkpoint §12 记 23:16，以 subTask/get 为准〕至今，停滞 80+ 小时） | 调度停滞非重试可解 | 留队作活样本；通道恢复自动运行 |
| E4 | R1b/R1c | checkpoint §12 | cancelled | — | — |
| E5 | ITSM 工单 | TK20261003235804338，加急+SLA 已超时，处理人未分配 | **blocked**（等响应） | 追评文案已备未粘贴 | 用户粘贴追评 |
| E6 | Genpilot NFS 只读挂载（/work/Analysis → 离线 /data/work 真身） | Genpilot 实测 + r1_out.txt 84,752B 成功产出 | confirmed（可用） | 无 | Phase 1 已用此通道关账 |

## F. 停止条件核查（本矩阵生成时）

- 数字来源唯一性：coarse 六方向主表数字以各方法 metrics.json 为唯一源，汇报 1 无新数字 ✅
- 文件路径冲突：ortholog-pca-v98 新旧目录已分离（stub-20261001 保留旧件）✅
- 状态可复现：本地持有物的状态可由上表路径+SHA 重新计算验证 ✅（容器级证据与日志级数字除外——已逐项标注存在层级）
