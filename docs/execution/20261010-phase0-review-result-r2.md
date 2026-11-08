# Phase 0 只读审阅 · 第二版（修正后复核，2026-10-10）

对象：第一版审阅（`docs/execution/20261010-phase0-review-result.md`，`verdict: REVISE`）所列 F1–F3 修正落地后的复核。
性质：只读复核 + 文档修正核对。未运行模型、未提交 DCS、未训练、未启动 GPU、未充值、未读取或输出任何凭据。
环境：Windows 10.0.22631 · PowerShell 7.6.6 · git 2.53.0.windows.2 · Python 3.9.6（`.venv39`）· 复核时间 2026-10-10T15:59:49+08:00

**范围限定**：本 verdict 是**本地**只读复核结论，用于放行 Task 1 的隔离 smoke 前置检查，**不替代** Claude/Flash 正式反方审阅。`results/phase-20261010/review-gate-status.json` 的 `status` 仍为 `pending`，正式门未关闭。

---

## 一、修正落地核对

| 编号 | 要求 | 落地位置 | 状态 |
|---|---|---|---|
| F1 | 登记写入 `results/pilot-v1` 的既有脚本路径 + 隔离要求 | `20261010-baseline.md:47-59`（新增"覆盖风险"一节，含 P1/P2/P3 三条 + 三条处理要求） | 已落地 |
| F1b | 让接手方第一眼就看到全量模式覆盖风险（超出原 fix 表的增补，已披露） | `20261010-handoff-to-next-agent.md:62`（"已知问题"内补全量模式警告 + 交叉引用 baseline） | 已落地 |
| F2 | 收窄 label-free 表述 | `20261010-baseline.md:31`、`20261010-handoff-to-next-agent.md:30`、`20261010-quick-handoff.md:44` | 已落地 |
| F3 | Task 1 验收补比较精度说明 | `20261010-task1-preflight.md:24`（补"先按冻结精度取整"及其理由）；`:32` 登记第一版审阅结论 | 已落地 |
| F4（可选） | baseline 注明 git 计数为时点快照 | `20261010-baseline.md:16` | 已落地 |

F2 的措辞与项目既有口径一致（`docs/reports/claude-review-03-to-10-20261009.md:89`、`docs/handoff-to-codex-round2-20261009.md:27` 原本就是"label-free：仅评估用标签"），Phase 0 文档此前丢掉了这个限定词，现已恢复并补上 transductive 投影的说明。

## 二、逐项复核

### 1. Phase 0 是否确实只读 —— 通过
`run_scope.json:7-10` 四项边界全为 `true`；`results/phase-20261010/` 下只有 `run_scope.json`、`baseline/git-status.txt`、`baseline/input-sha256.tsv`、`review-gate-status.json`，无提交/训练/费用/GPU 产物；`results/pilot-v1` 下 mtime 晚于 11:04:48 的文件数为 **0**。

### 2. 输入 SHA 一致性 —— 通过（11/11）
修正后重算：**ok=11 / bad=0**（size + sha256 双匹配）。

### 3. 三个目录与口径描述 —— 通过
修正后重算清点不变：oPCA 40 files / 18,098,994 B；SAMap extracted 21 files / 12,730,056 B；SATURN recovered 34 files / 350,869 B。

### 4. 科研口径 —— 通过
`20261010-baseline.md:31` 现写明"label-free 只适用于表示层、PCA 在 src+tgt 联合矩阵上拟合（`scripts/ortholog_pca_local_v1.py:254,258`）、KNN 用 reference 标签（`:265-266`）、不得写成 inductive"。三份交接文档口径一致。transductive 标签（三处 manifest）、SATURN `labels`/`ref_labels`、SAMap `keys=cell_type`、v97g 日志级限制均维持原判定。

### 5. 覆盖 / 绕过审批门 / 提前训练路径 —— 修正后通过（附前置条件）
写入 `results/pilot-v1` 的三条路径**依然存在**，本次未修改任何脚本（复核：`scripts/` 下 15:30 之后无文件被写入）。但：

- Phase 0 记录已完整登记三条路径及其行号（`20261010-baseline.md:51-53`）；
- Task 1 走隔离输出，不进冻结目录（`:57`）；
- Task 2 被显式前置条件拦住——必须先有 `--out` 或副本 + 目标目录存在时硬停止（`:58`）；
- 冻结目录只读复核确认未被触碰（`:59`）。

在本 gate 的作用域（放行 Task 1 隔离 smoke）内，该风险已受控且有书面前置条件；未发现绕过审批门的自动提交路径或提前训练路径。

## 三、残余风险与前置条件

1. **Task 2 前置条件**：`scripts/ortholog_pca_local_v1.py`（全量模式）与 `scripts/run_samap_compliant_v98.py:249-250` 必须在提供隔离输出后才能运行；未满足前不得进入 Task 2。
2. **SATURN 逐细胞覆盖缺口**：本地只有 6 个 coarse payload（`payloads/p1`–`p6`），`exact`/`fine` 只有 confusion。Task 2 若把 SATURN 纳入逐细胞复算，需先补数据；否则 SATURN 在该阶段只能做 confusion 级核对。
3. **Task 1 比较精度**：验收必须按 `20261010-task1-preflight.md:24` 执行（先取整到冻结精度再比），否则会因 ~1e-5 的表示差误停。
4. **正式门未关闭**：Claude/Flash 通道仍不可用（`20261010-review-channel-check.md`），本 PASS 只是本地结论。

## 四、结论

第 1、2、3、4 项通过；第 5 项在 F1 落地并附前置条件后通过。F1–F4 全部落地，未修改任何脚本、未触碰 `results/pilot-v1`、未产生 DCS/训练产物。

可放行的范围：准备并执行 `results/phase-20261010/A-smoke/` 的隔离 `human→mouse` / `coarse` 零成本 smoke。
不可放行的范围：Task 2 及以后（需满足第三节第 1 条）；任何 DCS 提交、训练、GPU、充值（需各自审批门）。

verdict: PASS
