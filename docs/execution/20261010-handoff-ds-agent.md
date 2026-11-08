# 课题 5｜DS/Claude 接手交接（2026-10-10）

## 交接目的

请下一位 agent 在不破坏现有证据和未提交改动的前提下，继续推进课题 5。当前优先目标不是马上训练，而是先完成审阅门，再按阶段执行零成本复算；最终推进到“只剩每次汇报后的老师反馈”。

## 工作区与基线

- 工作目录：`D:\projects\course5-prep`
- 分支：`codex/teacher-reply-report-prep`
- 交接时 HEAD：`8b597d788352009609688e28c7f2ed23a0358f17`
- 工作树有大量既有未提交改动，必须保留；不得 `reset`、`clean`、`checkout`、删除、覆盖或批量整理。
- 尤其不要覆盖 `results/pilot-v1/` 中已有冻结结果。

## 当前状态（以证据为准）

- 第一阶段汇报材料已进入“待老师反馈”状态；现有 PPT、Word、证据矩阵和阶段报告不要擅自重建。
- 尚未启动本轮 Task 1 smoke；没有新的 DCS 提交、GPU 训练、充值或大规模任务。
- 审阅门状态文件：`results/phase-20261010/review-gate-status.json`，当前应保持 `pending`，除非获得明确且可记录的正式 PASS。
- 主计划：`docs/superpowers/plans/2026-10-10-course5-genpilot-dcs-longrun.md`
- 快速执行说明：`docs/execution/20261010-quick-handoff.md`
- 基线：`docs/execution/20261010-baseline.md`
- Task 1 预检：`docs/execution/20261010-task1-preflight.md`
- Phase 0 审阅请求/结果：
  - `docs/execution/20261010-phase0-review-request.md`
  - `docs/execution/20261010-phase0-review-result.md`
  - `docs/execution/20261010-phase0-review-result-r2.md`

## 模型约束（必须遵守）

1. Claude 只能使用 DS 系列模型（以当前环境实际可用的 DS 模型名为准）。
2. 不得尝试 Sonnet、其他模型，不得修改模型配置或读取/打印任何 key、token、cookie、密码。
3. 发起审阅前先验证 DS 路由是否可用；若路由不可用，记录为阻塞，不要用别的模型替代，也不要反复重试。
4. 审阅是只读的：不改代码/文档、不提交、不推送、不调用 DCS、不训练。

## 已知审阅问题（先处理这些）

Phase 0 反方审阅已指出以下事项，在关闭前不得运行 smoke：

1. 计划中“允许在 DCS 做小规模任务”必须理解为原则性允许；每一个具体 DCS 任务仍需用户单独明确批准。
2. `SAMap keys=cell_type` 目前是本地脚本声明/支持的设置，不等于已确认 DCS 容器内实际脚本事实；平台事实必须标为待核实，除非有容器日志或源码证据。
3. 两份映射 SHA 不同，不能直接视为同一映射：
   - `scripts/v99_mapping_embedded.json`：`D92E32AA788672492FEBE8CD428BEAC71BA69FD99DF68C7F362CBA2E553EEA4A`
   - `config/heart-celltype-map-v1.tsv`：`BE9857354778535B76D1884D004C54691DC5FF2DAA7B098D71DC719DAF583165`
   需只读比较内容并查明 v99 实际使用来源。
4. v99 本地仅有 6 份 coarse 逐细胞 payload；exact/fine 没有逐细胞 payload，不能要求对 exact/fine 做逐细胞重算。
5. “27 格”必须定义计算维度；当前可执行集合最多为 `oPCA 27 + SAMap-approx 27 = 54`，SATURN 的 27 格不属于当前可执行集合。
6. Task 1/Task 2 必须使用隔离输出目录；目标目录已存在时硬停止，不得覆盖。
7. Task 1 与冻结文件比较时注意冻结 metrics 以 4 位小数保存；不能用全精度值直接套 `1e-12` 做错误的假失败判断，应按冻结精度或逐字段容差比较。

## 不可改变的科研口径

- 既有跨物种结果是 `transductive/in-sample`，不是泛化或 inductive。
- oPCA 表示层是 label-free；联合 PCA 在 source+target 上拟合，因此属于 transductive 投影；标签只用于评估。
- SATURN 默认训练标签通道是 `labels`；`ref_labels` 主要是输出/评估字段。不要写成“ref_labels 参与训练”。源码存在默认关闭的 `--use_ref_labels` 开关，原始训练命令仍待核实。
- SAMap 当前口径是 `keys=cell_type` 的 label-aware；没有原生冻结图投影，只能称 `SAMap-approx` 或近似隔离方案。
- v97g 只有日志级数字，不能伪造逐细胞 predictions/confusion，也不能把 candidate 写成 confirmed。
- SATURN inductive 当前仍是源码级 blocked；不得直接启动 SATURN GPU 训练。
- 单细胞优先，只筛 `cell_or_nuclei == "cell"`；单核仅作为后置小规模对照；空间数据不进主评估。
- 没有正式统计检验时只能写“数值更高/方向性差异”，不能写“显著优于”或“泛化能力更强”。

## 接手后的严格顺序

### 0. 只读审阅

先读：

1. `docs/execution/20261010-phase0-review-request.md`
2. `docs/execution/20261010-baseline.md`
3. `docs/execution/20261010-task1-preflight.md`
4. `docs/superpowers/plans/2026-10-10-course5-genpilot-dcs-longrun.md`
5. `results/phase-20261010/run_scope.json`
6. `results/phase-20261010/baseline/input-sha256.tsv`

使用 DS/Claude 做正式只读反方审阅。输出必须逐项列出通过/需修改/阻塞，并在最后单独写：

```text
verdict: PASS
```

没有明确 PASS 就停止；不得运行 smoke、DCS、训练或 GPU。

### 1. PASS 后才做本地 Task 1 smoke

只做 `human → mouse / coarse`，零成本，输出到新目录：

`results/phase-20261010/A-smoke/`

必须落盘 `manifest.json`、`command.txt`、`environment.txt`、输入/输出 SHA、`metrics.json`、`confusion.json` 和逐细胞预测表。使用隔离 wrapper，不能直接调用会写入旧目录的脚本。对角线求和与 `accuracy × n_q` 双重复核；按冻结文件精度比较。任何不一致立即停止。

### 2. 每一阶段都要停下来复审

Task 1 完成后再次交 DS/Claude 审阅；通过后才进入 A 档全量本地复算、负控/稳定性、三方法对照。每一阶段写独立证据报告并停止，等待用户继续指令。

### 3. DCS/GenPilot 只在批准门之后

GenPilot 只用于核实 file id、资源档、费用、队列、镜像和回收端点；未知项标为待核实，生成卡住 10 分钟就停止并汇总。任何具体 DCS smoke 都要先有审批单、预算、停止条件和用户明确批准；不自动重试、不擅自加资源、不充值。

## 禁止事项

- 不把 transductive 写成 inductive。
- 不把 candidate 写成 confirmed。
- 不将容器级“文件存在”写成本地文件已回收。
- 不把不同标签空间的数字直接排名或合并。
- 不因队列 Pending 而死循环轮询、取消重提或扩大任务。
- 不读取、保存或打印凭据。

## 阶段汇报格式

```text
阶段：
实际执行：
产物路径：
证据/哈希：
测试：
DS/Claude 结论：
DCS/GenPilot 状态：
阻塞：
是否进入下一阶段：是/否
```

## 一句话交接

当前不是“直接开训”，而是“先用 DS/Claude 完成只读审阅并拿到明确 PASS，再做隔离的本地 human→mouse/coarse smoke”；任何实验、DCS、GPU、充值都必须逐闸门、逐批准执行。
