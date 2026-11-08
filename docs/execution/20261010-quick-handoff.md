# 课题5快速交接（2026-10-10）

工作目录：`D:\projects\course5-prep`  
分支：`codex/teacher-reply-report-prep`  
当前 HEAD：`8b597d788352009609688e28c7f2ed23a0358f17`

## 现在停在哪里

当前处于 **Phase 0 基线冻结，等待 Claude/Flash 只读反方审阅**。目前没有启动新实验、DCS、GPU、训练或充值。

审阅门状态：

- `results/phase-20261010/review-gate-status.json`
- `status = pending`
- 基线输入 SHA：`11/11 matched`
- `task1 = not_started`
- `dcs_submission = false`
- `training = false`
- `gpu = false`
- `recharge = false`

## 接手后第一件事（必须先做）

只读审阅以下文件：

1. `docs/execution/20261010-phase0-review-request.md`
2. `docs/execution/20261010-baseline.md`
3. `docs/execution/20261010-task1-preflight.md`
4. `docs/superpowers/plans/2026-10-10-course5-genpilot-dcs-longrun.md`
5. `results/phase-20261010/run_scope.json`
6. `results/phase-20261010/baseline/input-sha256.tsv`

审阅输出必须逐项判断，并在最后一行明确写：

```text
verdict: PASS
```

如果是 `REVISE` 或 `BLOCK`，不要运行任何 smoke、DCS 或训练，先列出需要修正的文件和行号。

## 关键科研口径（不可改写）

- 既有跨物种结果：`transductive/in-sample`，不是泛化或 inductive。
- oPCA：label-free 参考方法，但只限于表示层（标签只在评估阶段使用）；v98 的 PCA 在 src+tgt 联合矩阵上拟合，是 transductive 投影，不得写成 inductive。
- SATURN：默认配置下训练使用 `labels`；`ref_labels` 主要是输出/评估字段。源码有默认关闭的 `--use_ref_labels` 开关，原始训练命令待核实，别笼统写成"ref_labels 参与训练"。
- SAMap：当前是 `keys=cell_type` 的 label-aware 口径；无原生冻结图投影，只能称 `SAMap-approx` 或近似 inductive。
- v97g：只有日志级数字，不能伪造逐细胞 predictions/confusion，也不能把 candidate 写成 confirmed。
- SATURN inductive：源码级 blocked。
- C2 当前最多 54 格：oPCA 27 + SAMap-approx 27；SATURN 27 格暂不执行。
- 单细胞优先，只筛 `cell_or_nuclei == "cell"`；单核后置小规模对照；空间数据不进主评估。
- 无正式统计检验时只能写“数值更高/方向性差异”，不能写“显著优于”或“泛化能力更强”。

## PASS 后的执行顺序

### Task 1：隔离的零成本 smoke

只运行 `human → mouse / coarse`，输出到：

`results/phase-20261010/A-smoke/`

不得删除、覆盖或修改 `results/pilot-v1/ortholog-pca-smoke/`。旧脚本 `scripts/ortholog_pca_local_v1.py --smoke` 会写入旧目录且会跑三物种六方向，不能直接使用；应创建 wrapper 或等价副本，限制为单方向、单层、隔离输出。

必须落盘：

- `manifest.json`
- `command.txt`
- `environment.txt`
- 输入/输出 SHA-256
- `metrics.json`
- `confusion.json`
- 逐细胞预测表

验收时同时核对：混淆矩阵对角线之和、`accuracy × n_q`，并与冻结数字比较，要求 `abs_diff <= 1e-12`。任何差异立即停止。

### Task 2 及以后

Task 1 完成后必须再次交 Claude/Flash 复审；复审通过后才进入 A 档全量本地复算，再进入负控/稳定性和三方法对照。DCS/GenPilot 小规模测试只有在本地证据链和审批门通过、且用户确认资源后才能提交；不自动重试、不擅自加资源、不充值。

## 禁止事项

- 不 `reset`、`checkout`、`clean`、删除或覆盖用户既有改动。
- 不覆盖 `results/pilot-v1`。
- 不把 transductive 写成 inductive。
- 不把日志级 candidate 写成 confirmed。
- 不自动提交、取消重提或扩大 DCS 任务。
- 不读取、保存或打印 token、密码、cookie、API key 或凭据。
- Pending/失败只检查一次，随后汇报，禁止死循环轮询。

## 回报格式

```text
阶段：
实际执行：
产物路径：
证据/哈希：
测试：
Claude/Flash 结论：
DCS/GenPilot 状态：
阻塞：
是否进入下一阶段：是/否
```

## 当前交接点

**先完成 Phase 0 只读反方审阅并拿到 `verdict: PASS`。在此之前不要运行 Task 1，也不要提交 DCS 或启动训练。**
