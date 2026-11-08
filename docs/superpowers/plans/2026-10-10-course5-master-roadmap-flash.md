# 课题5总体执行路线图（Flash 主执行，Claude 阶段复审）

> **For agentic workers:** 按阶段执行；每阶段完成后写一份短报告并停止，等待下一阶段条件或用户批准。不得自动轮询、自动重试、自动充值或跨批准门提交任务。

**目标：** 在保护既有冻结结果的前提下，完成零成本复算、单细胞优先的小规模验证、必要的 DCS 实验和 8–10 次阶段汇报材料，最后收敛到“实验与材料已收口，只等待老师反馈”。

**执行角色：** Flash/zcode 负责实际文件检查、脚本运行、GenPilot/DCS 操作和材料更新；Flash 每个阶段自行邀请 Claude 做一次反方审阅；Codex 不作为每阶段必经审批人，只在出现重大协议分歧、费用异常、数据泄漏风险或老师新意见时复核。Claude 调用方式以 `docs/execution/20261010-review-channel-check.md` 的“更正”一节为准：`claude -p "<prompt>" --allowedTools "Read,Glob,Grep,Bash,PowerShell" --disallowedTools "Edit,Write,NotebookEdit"`，stdout/stderr 分开保存，不加 `--model` 覆盖。

**计划层级：** 本文件是总纲；`docs/superpowers/plans/2026-10-10-course5-genpilot-dcs-longrun.md` 是阶段细则。两者冲突时以本文件为准，细则只能收紧边界，不能放宽冻结、费用或停止条件。

## 当前阶段状态

| 阶段 | 当前状态 | 说明 |
|---|---|---|
| 0 基线 | completed | 已冻结并通过外部复审 |
| 1 单方向 smoke | completed | `results/phase-20261010/A-smoke/` 已通过，标签为 `confirmed-for-recompute` |
| 2 A 档全量复算 | next | 只能在隔离输出和覆盖风险闸门通过后准备 |
| 3–4 平台核对/单细胞预检 | not-started | 不自动越过阶段 2 |
| 5–8 DCS/C1/C2/SATURN | gated | 需各自批准，不得因登录而启动 |
| 9 材料收口 | pending | 以老师反馈为最终收口条件 |

## 全局边界

- 工作目录固定为 `D:\projects\course5-prep`；保留现有未提交和未跟踪改动，不 reset、不清理、不覆盖冻结结果。
- 新结果写入新的日期/阶段目录；旧的 `results/pilot-v1`、历史 PPT/Word 和已有证据只读引用。
- 所有结果必须标明 `confirmed`、`confirmed-for-recompute`、`candidate`、`blocked` 或 `design-not-run`；没有逐细胞文件时不得伪造 predictions/confusion。
- 既有跨物种结果只能称 `transductive/in-sample`；不得写成 inductive、泛化能力或临床结论。
- 单细胞优先：只筛 `cell_or_nuclei == "cell"`；单核只在主结论稳定后做小规模对照；空间数据不进入主评估。
- oPCA 为 label-free 表示层方法；SATURN 的默认训练标签通道写作 `labels`，`ref_labels` 主要用于输出/评估，除非原始命令有直接证据，不得反写机制。
- SAMap 当前只能按 `SAMap-approx` 记录；C2 最多执行 oPCA 27 格 + SAMap-approx 27 格，共 54 格，不宣称完整 81 格。
- 没有正式统计检验时只能说“数值更高/方向性差异”；不得使用“显著优于”。
- DCS 只在明确批准后提交最小任务；Pending、502、OOM、RC 非 0、费用异常或队列饥饿时停止该分支，不取消重提、不加资源、不充值。

## 阶段路线（对应约 8–10 次汇报）

### 阶段 0：基线冻结与执行准备（汇报 1）

**目的：** 确认本轮从同一个证据基线出发。

**Flash 执行：**

- 读取 `docs/longrun-20261009-final-handoff.md`、`docs/plans/three-tier-followup-20261009.md`、GenPilot 会商记录、最新 Word/PPT 和 `results/phase-20261010/review-gate-status.json`。
- 记录 HEAD、工作树摘要、输入文件 SHA、现有阻塞和本轮范围；建立新的阶段目录，不改旧结果。
- 明确本轮 `no_training`、`no_platform_submission`，直到后续批准门单独开启。

**Claude 复审：** 只检查基线文件、协议标签、冻结数字与当前计划是否一致。

**产物：** 一页状态报告、输入 SHA 清单、执行范围记录。

**停止条件：** 输入缺失、SHA 不一致、路径会覆盖冻结结果或协议标签不清楚。

### 阶段 1：单方向零成本 smoke（汇报 2，已完成）

**目的：** 复用并验收已经完成的权威方向 smoke；不得因为本路线图重新执行而重跑。

**Flash 执行：**

- 读取 `results/phase-20261010/review-gate-status.json`、`results/phase-20261010/A-smoke/` 和 `docs/execution/20261010-task1-a-smoke-report.md`；确认 `task1=completed`、`status=passed`、验证 16/16。
- 只读核对 human→mouse/coarse 的 mapped/exact 标签空间、`n_q`、coverage、majority、排除规则，以及 predictions/confusion 与冻结产物的 SHA；不得新建第二个默认 `A-smoke/`。
- 若确需重跑，必须使用已验证的 `scripts/ortholog_pca_task1_isolated.py`（SHA-256 `71ab5642ad8e8a964717ad738c7f60524f9d1372fcc5bbc534cf63c64d7002ed`）并改用全新、非空即拒绝覆盖的时间戳目录；禁止删除或覆盖现有 `A-smoke/`。

**Claude 复审：** 只检查数字、分母、标签空间和证据链。

**停止条件：** 状态文件与报告不一致、任一数字/SHA 不一致、发现伪造逐细胞证据，或任何动作会覆盖现有 smoke 目录。

### 阶段 2：A 档全量本地复算与负控（汇报 3）

**目的：** 在零成本条件下完成 6 个方向 × exact/coarse/fine 的统一复算和方法学负控。

**Flash 执行：**

- 仅使用真实存在的 predictions/confusion；v97g 只有日志级数字，继续保持 candidate/日志级，不补造文件。
- 运行前必须先读 `docs/execution/20261010-baseline.md` 的“覆盖风险”一节。`scripts/ortholog_pca_local_v1.py` 全量模式和 `scripts/run_samap_compliant_v98.py` 当前会写入 `results/pilot-v1` 且无充分存在性守卫；在风险未关闭前不得运行全量模式。
- 必须**先实现** `--out` 参数或建立等价隔离副本（当前 `scripts/ortholog_pca_local_v1.py` 只有 `--smoke`，`scripts/run_samap_compliant_v98.py` 无 argparse 且硬编码输出路径，两个全量脚本均无此参数），把全部输出重定向到新的 `results/phase-20261010/A-full-<timestamp>/`（或对应独立 SAMap 目录），并在脚本第一步硬拒绝已存在/非空目标目录；不得修改、删除或覆盖 `results/pilot-v1`。
- 运行前先生成隔离 manifest，记录实际命令、脚本 SHA、输入 SHA 和目标目录；若无法证明输出路径隔离，阶段 2 直接停止。
- 计算多数类、shuffle/置换零分布、coverage、excluded 和逐方向分母。
- SATURN 当前只有 6 个 coarse 逐细胞 payload；exact/fine 没有逐细胞数据，只能引用日志级/汇总级数字，不得把它们纳入逐细胞复算。
- 完成 ortholog-PCA 对照、seed/ceiling 等已有本地项目的统一汇总。

**Claude 复审：** 检查是否混用了 mapped/exact 标签空间、是否把方向性差异写成显著性、负控定义是否可复核。

**产物：** A 档总表、负控报告、18 格数字来源表。

### 阶段 3：GenPilot/DCS 平台事实核对（汇报 4）

**目的：** 只核实平台事实，不因登录状态自动启动训练。

**Flash 执行：**

- 核对离线任务入口、镜像完整地址、可用资源档、队列状态、费用显示、文件 ID、downloadFile 回收链路和单细胞字段。
- GenPilot 卡住 10 分钟就停止生成并要求基于已有证据汇总；未知项标为待核实。
- 不提交任务、不充值、不把平台口头答复当作本地确认事实。

**Claude 复审：** 检查平台证据是否足够支持后续预算和任务选择，特别是价格、失败原因和队列状态。

**停止条件：** 费用口径不明、队列不可用、下载链路不稳定或平台证据互相矛盾。

### 阶段 4：单细胞优先子集预检（汇报 5）

**目的：** 在本地确认正式实验的数据选择和角色表，不提交 DCS。

**Flash 执行：**

- 从三份数据中筛 `cell_or_nuclei == "cell"`，记录物种、细胞数、标签覆盖率、重复条码和 NA。
- 生成 query/reference 角色表、物种前缀化条码和单细胞 manifest；单核只登记为后续对照。
- 对 2–3 个物种做最小 smoke 设计，同时保留远近关系不同的正式候选组合。

**Claude 复审：** 检查物种组合、角色表、条码命名空间、self/重复条码排除和数据泄漏边界。

**停止条件：** 角色表不完整、条码碰撞、标签 NA、单细胞筛选无法复现或 query/reference 未留出。

### 阶段 5：B 档最小 DCS smoke（汇报 6，必须用户批准）

**目的：** 用最低成本验证平台容器、脚本、镜像和结果回收链路。

**启动前必须具备：** 阶段 0–4 通过；审批单写明任务名、镜像、资源档、预计费用上限（原则上 ≤1 元）、输入 SHA、输出文件和停止条件；用户明确回复批准。

**Flash 执行：**

- 只跑 2–3 个物种、单细胞子集、单 seed、最小方向；先跑 oPCA 或 SAMap 单次 smoke，不做 9 次扩展。
- 任务首步记录完整命令、参数、环境、输入 SHA；结束后保存 metrics、predictions、confusion、coverage、excluded 和输出 SHA。
- 只做一次绑定状态检查；失败或 Pending 超窗立即收口。

**Claude 复审：** 检查任务是否按批准范围执行、结果是否可回收、是否有标签/条码泄漏和费用越界。

**停止条件：** 费用超过上限、OOM、RC 非 0、队列饥饿、输出缺失或协议偏离。

### 阶段 6：C1 投影/隔离闸门（汇报 7）

**目的：** 在扩大实验前裁决哪些方法可以做真正的 query/reference 或投影评估。

**Flash 执行：**

- oPCA：验证训练矩阵、投影矩阵、query-only 变换和标签未进入拟合。
- SAMap：只能提出并验证 `SAMap-approx`，明确其不是原生 inductive；记录近似步骤和泄漏风险。
- SATURN：不直接训练。先依据源码确认物种槽、每物种 HVG、首层维度、冻结权重兼容性和 `labels/ref_labels` 通道。

**Claude 复审：** 作为反方审阅，重点查“inductive”命名是否过度、C1 源码判断是否有证据、是否遗漏数据泄漏。

**停止条件：** 任一方法无法形成可审计的 query/reference 协议，或 SATURN 源码级阻塞未解除。

### 阶段 7：C2 可行子集（汇报 8，必须用户批准）

**目的：** 在闸门通过后，完成可行范围内的跨物种方法学比较。

**Flash 执行：**

- 先做 oPCA 1 折 × 1 seed smoke；通过后扩展为 3 折 × 3 seed = 9 次本地运行。
- SAMap 仅按 `SAMap-approx` 运行，预算以平台实际价格为准，最多 9 次；未批准不得提交。
- 汇总最多 54 格，逐 seed 报三层指标、分母、coverage、majority、shuffle_p、mean±SD；不择优 seed。
- 结果标题注明“跨物种级、非跨供体级”；不要把 SAMap-approx 写成正式 inductive。

**Claude 复审：** 检查 seed 完整性、泄漏审计、费用、统计表达和三种方法是否在同一标签空间/协议下被误排名。

**停止条件：** 任一 seed 失败、费用超批、映射未签认、平台再次饥饿或结果无法逐格回溯。

### 阶段 8：SATURN 独立方案（汇报 9，默认不执行）

**目的：** 只有老师明确要求 SATURN inductive 时，才另立重训项目。

**Flash 执行：**

- 先让 Claude + GenPilot 讨论重训/模型改造方案：物种槽、HVG、标签通道、query 隔离、GPU 档、预算和成功标准。
- 先做 2 物种最小 smoke；不把 v99 或旧 transductive 结果当作新协议结果。
- 每个训练任务自动保存命令、参数、pip freeze、输入/输出 SHA、源码树 SHA、模型权重 SHA 和逐细胞结果。

**审批门：** 用户和老师双重明确同意、预算明确、C1 泄漏问题已解决。任何 KeyError、维度不兼容、OOM、标签泄漏或费用异常立即停止。

### 阶段 9：材料收口与等待老师反馈（汇报 10）

**目的：** 将结果组织成可讲清楚、可追溯、可被老师逐页审阅的最终阶段材料。

**Flash 执行：**

- 更新 Word、PPT、数字来源表和证据索引；主表旁边明确写出数字来自 prediction/confusion、分母、coverage 和排除规则。
- 单独解释 oPCA、SATURN、SAMap 的训练/表示/标签机制差异，区分 confirmed、confirmed-for-recompute、candidate、blocked、design-not-run。
- 每次老师反馈归档到 `docs/teacher-feedback/`，先修反馈再开启下一阶段；不因已有结果多就提前宣称项目全部完成。
- 首次归档老师意见前先创建 `docs/teacher-feedback/`（若不存在）；不得把反馈散落在临时文件或未索引的聊天记录中。
- 形成最终清单：已完成实验、未运行设计、待人工签认、平台待核实、下一步仅待老师决定。

**进入“只等老师反馈”的条件：**

1. 所有已运行结果均有 manifest、命令、环境、输入/输出 SHA 和协议标签；
2. PPT/Word 主表与冻结数字逐格一致；
3. transductive、SAMap-approx、SATURN blocked 等限定语全部保留；
4. 没有未处理的数字冲突、泄漏风险、费用异常或未说明的文件缺口；
5. mapping v1、预算、是否开展 SATURN/单核等人工决策事项已列成清单；
6. 后续工作只剩老师评审意见，不再自动启动实验。

## Flash 每阶段固定执行模板

```text
工作目录：D:\projects\course5-prep
本阶段目标：<阶段编号和一句话目标>
先读：现有总交接、上一阶段报告、当前阶段 manifest 和老师最新反馈。
执行规则：保留既有改动；不 reset、不覆盖冻结结果；新结果写新目录；不读取凭据。
本阶段只做：<明确的本阶段动作>
本阶段不做：<明确禁止动作，例如不提交 DCS/不训练/不扩展物种>
完成后必须输出：做了什么、证据路径、通过/需修改/阻塞、费用/任务状态、下一阶段前置条件。
然后调用 Claude 做反方审阅，要求逐项给 PASS / REVISE / BLOCK，并引用文件和行号/页码。
若 Claude 发现协议、数字、泄漏或费用问题，先修正并复审；若发现跨阶段问题，停止并汇报，不自行越门。
```

## 当前交接点

当前阶段 0 和阶段 1 均已完成并通过外部复审：`results/phase-20261010/A-smoke/` 有 13 个文件，验证 16/16，标签为 `confirmed-for-recompute`。下一步交给 Flash：只读复核阶段 1 后，从阶段 2 开始；阶段 2 必须先关闭全量脚本覆盖 `results/pilot-v1` 的风险并建立隔离输出，未满足前不得运行全量模式。当前不提交 DCS、不启动训练、不充值。

