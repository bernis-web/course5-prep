# 课题 5 长任务交接：阶段一证据、方法比较与汇报材料一次准备包

> 交给：ZCode/Flash 执行；Claude 做每阶段独立审阅；Codex 最后做只读审计。  
> 目标：在老师下一轮反馈前，把本地可完成的证据整理、方法学解释、Word/PPT 草稿和下一阶段计划全部准备好；收到老师意见后只做定向修订，不重新搭建流程。

## 0. 先读文件，再动手

工作目录：`D:\projects\course5-prep`

必须先读：

1. `docs/superpowers/plans/2026-10-08-course5-report-cycle-and-ppt-audit.md`
2. `docs/final-evidence-matrix-ortholog-pca-20261003.md`
3. `docs/phase6-closure-20261005.md`
4. `docs/stale-numbers-audit-20261003.md`
5. `docs/handoff-to-claude-codex-20261002.md`
6. 老师批语版 PPT 及其生成脚本：
   - `results/phase1-revised/课题5第一阶段成果汇报_老师批语修订版.pptx`
   - `results/phase1-revised/build_phase1_revised.js`
7. `results/pilot-v1/ortholog-pca-v98/metrics.json`
8. `results/pilot-v1/samap-v98/wdl-run/` 与相关 SAMap 证据。

开始前记录 `git status --short`。不要清理、回退、覆盖或批量暂存用户已有改动。

## 1. 硬边界

- 不把 AI 评审当作导师签字；`mapping v1` 仍标为 `needs-reviewer`，直到真人明确确认。
- 当前结果全部是 `transductive/in-sample`；除非新 manifest 明确留出 query/reference，否则不得写 `held-out` 或 `inductive benchmark`。
- 不把容器/日志中“存在”的文件写成“本地已回收”；状态必须区分 `confirmed-local`、`container-only`、`candidate-final`、`exploratory`、`pending`、`blocked`。
- 不混合 SATURN v97g mapped-space 的 `61.79%` 和 v99 exact-space 的 `48.44%`；两者必须双报并说明标签空间不同。
- 不把三个方法按单一总分排冠军。比较必须同时列表示层、标签空间、分母、coverage、n_q、label-aware/label-free、协议和算力成本。
- 不自动启动新的高成本 GPU、inductive 留出或不可逆 DCS 任务。可以完成本地复算、审计、脚本/manifest、报告和任务 payload 预构建；真正提交新任务前写明资源、费用、预期产物和停止条件，并等待用户批准。
- 旧 PPT 保留。新 PPT 必须另存为 `results/phase1-revised-v2/` 或带版本号的文件。
- 所有数字从 metrics/evidence matrix 逐格回溯，禁止凭记忆手改。

## 2. 长任务目标与交付物

完成以下工作包；每个工作包都要有文件、命令/退出码、测试或只读核对结果、SHA/文件数量和 Claude 审阅结论。

### Work Package A：证据状态冻结

建立或更新：

- `docs/evidence/status-matrix-20261008.md`
- `docs/reports/report-01-evidence-status-20261008.md`

逐项列出 SATURN v97g/v99、ortholog-PCA v98、SAMap v98 WDL、mapping v1、PPT/Word 产物的：来源路径、文件级证据、SHA、数字是否可独立复算、当前状态、缺口、下一动作。明确容器级存在不等于本地回收。

让 Claude 对矩阵逐项给出 `通过/需修改/阻塞`，引用文件和行号。不要只写总体评价。

### Work Package B：把每个数字讲清楚

建立：

- `docs/evidence/metric-lineage-20261008.md`
- `docs/evidence/metric-calculation-examples-20261008.md`

至少完整追踪以下示例：

1. ortholog-PCA human→mouse coarse `86.18%`；
2. SATURN v97g human→mouse coarse `61.79%`；
3. SATURN v99 exact-space human→mouse `48.44%`；
4. SAMap WDL human→mouse coarse `10.50%`；
5. 一个斑马鱼方向低于 majority 的例子。

每个示例必须写出：输入数据、表示层、query/reference 角色、标签空间、排除规则、`n_q`、coverage、正确数、分母、公式、majority、shuffle/null 定义、输出文件和 SHA。若某个分子或逐细胞文件不能本地独立核对，标为 candidate/container-only，不得补猜。

### Work Package C：三方法公平比较

建立：

- `docs/evidence/method-comparison-matrix-20261008.md`
- `docs/reports/report-02-metric-lineage-20261008.md`
- `docs/reports/report-03-method-comparison-20261008.md`

用并列表解释：

- ortholog-PCA：1:1 ortholog、联合 PCA-50、KNN15/cosine、label-free 基线；
- SATURN：蛋白语言模型/ESM2、macrogenes、训练与评估协议、容量和 seed 效应；
- SAMap：同源基因图/联合流形、`keys=cell_type` 的 label-aware 影响、WDL 脚本口径和探索性限制。

结论只写“在当前数据和协议下观察到的方向性差异”，不写普遍工具优劣。

### Work Package D：ortholog-PCA 和 SAMap 证据闭环

只读复核 ortholog-PCA `metrics.json/manifest/predictions/confusion` 的 18 格和输出 SHA；确认旧草表  
`80.9/38.3/40.5/22.4/11.9/79.5` 在所有新材料中被标为作废。

只读复核 SAMap Phase 6 WDL 关账：六方向×三层、21 个归档文件、脚本 md5、n_q/acc 混合口径、Phase 5 修复版与实际运行版的差异。不得把“WDL 已成功”写成“Phase 5 修复版已运行”。

如果需要补跑，只能先生成 manifest 和一次性提交说明；不自行重试排队饥饿的旧任务。

### Work Package E：修订第一阶段 PPT 与 Word 草稿

先复制旧 PPT 到新版本目录，再修改生成脚本/副本。新版本至少完成：

1. 主表 ortholog-PCA 替换为：`86.18 / 73.69 / 19.61 / 27.55 / 18.13 / 57.61`；
2. SAMap 列替换为 Phase 6 WDL 数字，并标注探索性、运行脚本口径和标签/分母限制；
3. 删除“统一评分器复算后再冻结”和“v98 尚需修正复跑”等过时文字；
4. 增加“一个百分比如何得到”的算式页，至少展示正确数、分母、coverage 和过滤；
5. 增加“论文方法 vs 本项目方法”的对照页：回答测了什么、为什么适合本题、哪里不能比较；
6. 增加“不能从当前结果推出什么”的防误读页；
7. 保持原有格式、配色和叙事层次，不把页面塞满；
8. 生成 `docs/reports/report-07-ppt-revision-20261008.md`，逐页列旧问题、修改、证据来源和未决项。

Word 草稿至少包括：摘要、数据与预处理、三方法、评估协议、结果主表、数字来源、方法差异、局限、下一阶段计划、证据等级和 reviewer 状态。Word/PPT 数字必须来自同一矩阵。

完成后做：PPT 渲染、逐页文本抽取、版式/溢出检查、旧数字全文搜索；把命令和结果写入报告。不要覆盖老师批语原稿。

### Work Package F：后续实验设计，不立即烧算力

建立：

- `docs/plans/inductive-pilot-manifest-v1.md`
- `docs/reports/report-09-inductive-design-20261008.md`
- `docs/reports/report-10-closure-and-next-phase-20261008.md`

设计留一物种/分层 query-reference、标签可见性、最小样本量、资源档、预算、失败停止条件和输出验收。明确“设计完成”不等于“已运行”。单核、更多物种、空间数据作为后续候选，不混入第一阶段结论。

## 3. Claude 审阅安排

Claude 至少做四次独立审阅：

1. 证据状态矩阵；
2. 数字来源与三方法比较；
3. PPT/Word 逐页逐数字；
4. 最终交付包与过度结论检查。

每次审阅保存独立文件，例如：
`docs/reports/claude-review-01-20261008.md`，保留原意见，不覆盖旧意见。审阅必须引用路径/行号并区分必须修改、建议修改和可接受限制。

## 4. 每个阶段的固定汇报格式

```text
本次阶段：A/B/C/D/E/F，主题：...
实际做了什么：...
证据文件：...
命令与退出码：...
输出文件数量与 SHA：...
数字口径：标签空间 / query-reference / 分母 / coverage / seed / transductive-inductive
Claude 审阅：通过 / 需修改 / 阻塞（逐项）
未完成与原因：...
老师反馈待修改点：...
下一阶段：...
是否需要用户批准 DCS/GPU：是/否
```

本长任务完成后先停在“待老师反馈”状态，不把草稿升级成最终定稿。老师反馈回来后，按反馈逐条建立变更清单，保留旧版、修改新版，再让 Claude 和 Codex 做一次收口审计。

## 5. 最终停止条件

只有满足以下条件，才能报告“本轮长任务完成”：

- 证据状态矩阵和数字来源链已写完；
- 三方法对照和限制已写完；
- PPT 新版本和 Word 草稿已生成，旧版未被覆盖；
- 全文没有把旧草表当正式数字，没有把 transductive 写成 inductive；
- Claude 四轮审阅已归档，必须修改项已处理或明确标为阻塞；
- 所有未完成项、需要老师决定的事项和需要用户批准的 DCS/GPU 事项列清楚；
- `git status`、测试/渲染结果和文件 SHA 已记录；
- 不因为材料齐全而声称导师已经认可或项目已经完成。

执行重点：把“数据怎么来的”和“方法为什么不同”讲到听众可以沿着文件和公式复核，而不是继续堆一个更高的分数。
