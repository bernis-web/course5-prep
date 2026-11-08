# 课题5阶段汇报与PPT证据审计计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在不追求快速结题的前提下，用 8–10 次有证据、有评审回合的阶段汇报，把三方法比较、数字来源、协议差异和后续泛化实验逐步讲清楚，最终形成可供导师审阅的 Word 报告和修订版 PPT。

**Architecture:** ZCode/Flash 负责本地重活、脚本执行、DCS/WDL 机械操作和材料整理；Claude 在每一阶段结束后做独立方法学审阅；GenPilot 只用于平台状态、任务产物或方法咨询，不代替本地文件验收；Codex 负责阶段计划、证据审计和最终收口。每次汇报都必须有一个小的、可回退的产物和一份评审意见记录。

**Tech Stack:** `D:\projects\course5-prep`、Python/.venv39、现有 ortholog-PCA/SATURN/SAMap 评估器、DCS/GenPilot WDL 证据、Markdown、DOCX、PPTX。

## Global Constraints

- 不删除、覆盖或回退现有结果；新版本写入独立目录或带版本号的文件。
- 不把容器级存在、日志级数字或 AI 口头汇报写成本地文件级 confirmed。
- 所有结果明确标注 `confirmed`、`candidate-final`、`exploratory`、`pending` 或 `blocked`。
- 现有结果均为 transductive/in-sample，除非新 manifest 明确写出留出协议，不得称为 inductive 或 held-out benchmark。
- 三方法的标签空间和分母不完全相同：ortholog-PCA 为映射词汇空间；SATURN/SAMap 为原始标签加 status 过滤；SAMap 当前为 label-aware (`keys=cell_type`)。比较时必须并列协议、coverage、n_q 和证据等级。
- 每次 DCS/WDL 操作必须先写任务定义、资源档、预算风险、预期产物和停止条件；不自动重试、不循环轮询。
- 每次阶段结束必须让 Claude 写逐项审阅；没有审阅结论不得进入下一阶段。
- 不因“预计要汇报 8–10 次”而制造重复工作；每次汇报都要回答一个新的可验收问题。
- 任何 PPT/Word 数字必须从冻结 metrics/evidence matrix 生成或逐格核对，禁止手工凭记忆改表。

## 当前审查结论（执行入口）

1. [results/phase1-revised/课题5第一阶段成果汇报_老师批语修订版.pptx](D:/projects/course5-prep/results/phase1-revised/课题5第一阶段成果汇报_老师批语修订版.pptx) 已新增“数字如何得到”“方法核心信号/限制”“防误读门”等内容，**方向正确但尚未最终解决老师意见**。
2. 该 PPT 核心表仍使用早期 ortholog-PCA 草表 `80.9/38.3/40.5/22.4/11.9/79.5`，而统一评分器 candidate-final 已是 `86.18/73.69/19.61/27.55/18.13/57.61`；SAMap 表也仍是旧探索数字，且后页仍写“v98 尚需修正复跑”，与 2026-10-05 WDL 关账报告不一致。
3. [docs/final-evidence-matrix-ortholog-pca-20261003.md](D:/projects/course5-prep/docs/final-evidence-matrix-ortholog-pca-20261003.md) 和 [docs/phase6-closure-20261005.md](D:/projects/course5-prep/docs/phase6-closure-20261005.md) 是当前数字审计的主要依据；PPT 修订前必须先完成一张新的三方法总矩阵。
4. [docs/phase7-email-final-20261005.md](D:/projects/course5-prep/docs/phase7-email-final-20261005.md) 已通过 Claude/GenPilot 复核，但“通过”不等于导师已签认；mapping v1 的人工终签仍是独立事项。
5. 本轮不需要先登录 GenPilot。只有在核对平台任务/WDL 产物、提交经批准的新任务或让 GenPilot 审阅平台流程时才请求用户登录。

## 文件责任边界

- `docs/reports/`: 每次汇报正文、评审意见、用户反馈摘要。
- `docs/evidence/`: 阶段证据矩阵、数字来源表、协议差异表、SHA 清单。
- `results/phase1-revised/`: 保留旧 PPT；新 PPT 另存为 `results/phase1-revised-v2/`，不得覆盖旧文件。
- `scripts/`: 只修改现有生成脚本或新增专用审计脚本；每次修改配套测试/运行记录。
- `deliverables/`: 只有数字冻结和 Claude Gate 通过后才更新最终 Word/PPT；更新前保留旧交付物。

## 8–10 次汇报安排

### 汇报 1：现状与问题定稿

**目标：** 把“哪些已经完成、哪些只是候选、哪些被阻塞”讲成一页可审计状态图。

- [ ] ZCode 对当前 Git 状态、最近提交、三个主证据矩阵和 Phase 6/7 文件做只读核对。
- [ ] 建立 `docs/evidence/status-matrix-20261008.md`，逐项列证据路径、SHA、状态、缺口和下一动作。
- [ ] Claude 审阅状态分类，不得只复述交接文本。
- [ ] 交付一次短汇报：不讲新数字，只讲证据等级和需要导师决定的事项。

**停止条件：** 任何数字来源不唯一、文件路径冲突或状态不能复现时，停在该项。

### 汇报 2：数字来源链

**目标：** 让听众能从一张表追到一个百分比的完整生成路径。

- [ ] 对 ortholog-PCA、SATURN、SAMap 各选一个方向，分别列出输入文件、表示层、标签、query/reference、K、距离、权重、排除规则、分母、输出 JSON 和 SHA。
- [ ] 生成 `docs/evidence/number-provenance-trace-20261008.md`。
- [ ] 解释示例：`human→mouse` 的每个方法都给出 `correct / eligible / accuracy / coverage / majority / shuffle_p`，并明确哪些数字不能互相替代。
- [ ] Claude 审阅逐项链路；缺逐细胞文件时降级为日志级证据。
- [ ] 交付一次汇报：只回答“数字怎么来的”。

### 汇报 3：三方法公平比较边界

**目标：** 解释为什么不能把三列直接按一个总分排冠军。

- [ ] 建立 `docs/evidence/method-comparison-protocol-20261008.md`，至少包含：SATURN 的 macrogenes/训练路径、SAMap 的同源图与 `keys=cell_type`、ortholog-PCA 的 1:1 ortholog+PCA50；label-free/label-aware；transductive；标签空间；分母；算力和失败模式。
- [ ] 给每个方法写“回答的问题”和“不能回答的问题”，避免用“谁更好”替代科学问题。
- [ ] Claude 审阅比较是否公平、是否把协议差异误写成方法能力差异。
- [ ] 交付一次汇报：方法设计和适用场景，而非新跑分。

### 汇报 4：ortholog-PCA 基线闭环

**目标：** 把早期草表正式替换为统一评分器 candidate-final，并解释变化来源。

- [ ] ZCode 以 `results/pilot-v1/ortholog-pca-v98/{manifest.json,metrics.json,predictions/,confusion/}` 为唯一数字源。
- [ ] 逐格核对六方向×exact/coarse/fine、coverage、majority、shuffle_p、n_q 和输出 SHA。
- [ ] 对照旧草表，逐项解释排除规则和评分器变化；旧数字只保留为“作废历史草表”。
- [ ] Claude 审阅方向性结论，尤其是“哺乳动物对强、斑马鱼方向弱/阴性、z→m 为例外”以及单 seed 限制。
- [ ] 交付一次汇报：为什么简单基线有时超过复杂模型。

### 汇报 5：SATURN 结果与容量/协议效应

**目标：** 说明 SATURN 的信号来自哪里，以及为什么不能当作泛化性能。

- [ ] 固定引用 v97g 和 v99 双口径，不合并 `61.79%` 与 `48.44%`；用文档说明 mapped/exact 标签空间差异。
- [ ] 展示 macrogene 容量消融、seed 双峰、物种距离和 transductive/in-sample 边界。
- [ ] 生成 `docs/evidence/saturn-signal-and-limitations-20261008.md`。
- [ ] Claude 审阅“有信号”与“可泛化”之间的措辞；不得写成 SOTA 优胜结论。
- [ ] 交付一次汇报：SATURN 的证据等级和局限性。

### 汇报 6：SAMap 复现与负结果解释

**目标：** 说明 SAMap 的低分/零分是怎样得到的，哪些是运行限制，哪些是方法学观察。

- [ ] 以 `docs/phase6-closure-20261005.md` 和 `results/pilot-v1/samap-v98/wdl-run/` 为主证据，核对 WDL 任务、脚本 SHA、输入 SHA、18 格输出和 n_q。
- [ ] 解释旧 Phase 5 预提交脚本与最终 WDL 运行脚本的差异；不要把两者混成同一次运行。
- [ ] 明确当前 WDL 结果是成功复现但脚本口径存在混合旗标限制，必要时标为 candidate/exploratory，而非无条件 confirmed。
- [ ] Claude 审阅“无稳定信号”是否被过度推广为“工具无效”。
- [ ] 交付一次汇报：负结果、OOM/调度问题和方法边界。

### 汇报 7：三方法总矩阵与老师问题专页

**目标：** 用最终证据重做老师指出的那张 PPT 表，使其既有含金量又不误导。

- [ ] 先生成 `docs/evidence/three-method-matrix-20261008.md`，每个单元格带来源文件、协议标签、coverage/n_q、证据等级。
- [ ] 修改 `results/phase1-revised/build_phase1_revised.js`，不直接改 PPT 二进制；新版输出到 `results/phase1-revised-v2/`。
- [ ] 表格替换为最新 ortholog-PCA、SATURN、SAMap 数字；删除“阶段草表”“v98 尚需修正复跑”等过时文字。
- [ ] 增加一页“从原始数据到表格单元格”的具体算式和一个三方法对照示例；保留原有格式和配色。
- [ ] 增加一页“为什么方法数字不同”：表示层、标签空间、label-aware、分母、transductive 协议、算力/失败模式六项对照。
- [ ] 运行 PPT 渲染和逐页文本/版式检查；Claude 做内容审阅，GenPilot 可做一次平台流程审阅但不是数字验收。
- [ ] 交付一次汇报：专门回应老师的 PPT 意见。

**PPT 预期修正重点：**

- 旧表 `80.9/38.3/40.5/22.4/11.9/79.5` → 新表 `86.18/73.69/19.61/27.55/18.13/57.61`。
- 旧 SAMap 探索列 → Phase 6 WDL 结果；同时标明其脚本口径和跨方法不可直接排名的限制。
- “v98 尚需修正复跑” → “WDL 已完成；结果为当前数据/协议下的探索性复现”。
- 不把 `61.79%`、`48.44%`、`0.6179` 等不同标签/评分口径混为同一 SATURN 数字。

### 汇报 8：mapping reviewer 与证据责任

**目标：** 完成人工签认前的透明说明，不让 AI 复核替代导师责任。

- [ ] 发送 [docs/phase7-email-final-20261005.md](D:/projects/course5-prep/docs/phase7-email-final-20261005.md) 前，更新附件清单和当前 PPT/Word 版本号。
- [ ] 重点请导师确认 4 个低置信映射；收到“确认”或修改意见后保存原文，不覆盖 v1。
- [ ] Claude 审阅邮件是否明确“AI 初审、导师终签”。
- [ ] 交付一次汇报：映射表如何影响三种方法的标签和分母。

**停止条件：** 未收到人工签认时，mapping 状态保持 `needs-reviewer`，不得写成正式 benchmark。

### 汇报 9：最小 inductive 方案（仅设计，不自动运行）

**目标：** 把“后续如何证明泛化”设计清楚，但不因进度快就立即烧算力。

- [ ] 设计留一物种或分层 query/reference 方案，冻结训练/评估角色、标签可见性、预算、资源档和失败停止条件。
- [ ] 写 `docs/plans/inductive-pilot-manifest-v1.md`，附功效/样本量和最小可行版本。
- [ ] Claude 和 GenPilot 分别审阅方法学与平台可执行性。
- [ ] 交付一次汇报：从 transductive 到 inductive 需要新增什么证据。

**停止条件：** 未经用户和导师批准，不提交任务、不启动 GPU。

### 汇报 10：阶段收口与下一阶段路线

**目标：** 形成版本化 Word/PPT 和下一阶段决策页。

- [ ] 将三方法矩阵、数字来源、协议差异、mapping 状态、SAMap 运行限制、inductive 设计合并进 `docs/final-evidence-matrix-v2.md`。
- [ ] 由脚本生成修订 Word 和最终 PPT，保留旧版本并写版本说明。
- [ ] Claude 做逐页、逐数字终审；GenPilot 仅核对平台任务证据（若需要）。
- [ ] Codex 做最终只读审计：数字回溯、状态分类、教师意见闭环、是否存在过度结论。
- [ ] 交付阶段汇报和下一阶段批准清单。

## 每次汇报后的固定评审回合

1. ZCode 提交：执行命令、退出码、测试、输出文件数量、SHA、未完成项。
2. Claude 审阅：逐项列“通过/需修改/阻塞”，引用文件和行号，不只给总体评价。
3. 用户反馈：记录老师/组内评语原文或准确摘要，标明哪些是新要求。
4. ZCode 修订：只处理本轮评审要求，保留旧版本和 diff。
5. 下一阶段放行：只有“证据齐全 + Claude 评审通过 + 用户未提出新阻塞”才进入下一轮。

## ZCode/Claude 汇报模板

```text
本次汇报：第 X/10 次，主题：...
本轮目标：...
实际执行：...
证据文件：...
命令与退出码：...
输出数量与 SHA：...
数字口径：标签空间 / query-reference / 分母 / coverage / seed / transductive-inductive
Claude 审阅：逐项通过/需修改/阻塞
老师/组内反馈：...
已修订文件：...
未完成与阻塞：...
下一次汇报目标：...
是否需要用户批准 DCS/WDL/GPU：是/否
```

## 明确回答用户的问题

- **能明白吗？** 明白。后续重点是证据链和方法差异，不是单纯增加跑分。
- **有问题吗？** 没有需要你现在先登录或补充的阻塞。当前唯一需要明确提醒的是：老师指出的 PPT 问题只完成了“结构性补充”，没有完成“用最新结果替换旧数字并逐项解释来源”；应把汇报 7 作为专门修订回合。
- **GenPilot 什么时候用？** 需要平台任务状态、WDL 产物清单、平台方法咨询或新任务执行前审查时再用；本轮本地证据审计不依赖登录。
- **节奏建议：** 每次汇报以一个新问题为中心，汇报之间等待老师评审，不追求连续快速提交。预计 8–10 次完成，若某次评审要求补证，可在该次和下一次之间插入一个“补证小回合”，不打乱编号。
