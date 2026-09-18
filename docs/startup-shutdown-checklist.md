# DCS 受控启动/停止检查清单（草稿）

状态：**草稿 v0.1（2026-09-18），待四人评审，不是启动授权。** 在 G1（数据路径/字段/物种/授权）、G2（实例内运行时与正式 kBET）、G3（审批）全部通过且四名成员明确批准之前，仓库保持不创建实例、不提交任务、不上传数据、不安装包、不付费。启动门定义见 `docs/next-round-handoff.md` 第 5 节；镜像证据要求见 `docs/dcs-image-probe-plan.md`；命令与预算口径见 `docs/minimal-verification-runbook.md`；停止并询问用户的条件见 handoff 第 4 节。

标注约定：无标注条目直接来自上述文档的既有规则；标 **（建议）** 的条目是本草稿新增的流程建议，需四人评审时逐条确认或删除。本清单与 handoff 第 5 节冲突时，以 handoff 为准。

## 0. 角色指名（启动前必须填好）**（建议）**

**（建议）** 以下四角色拆分为本草稿新增：源文档只要求"指名一名负责监控并手动停机的人"，拆分是为了把监控、停机、验证分给不同的人。评审不认可时可合并回单角色。

| 角色 | 职责 | 本轮成员 |
|---|---|---|
| 运行负责人 | 发起任务、掌握进度、到达停止线时执行手动停机 | 待指名 |
| 监控人 | 盯内存/GPU/计时/花费，到达任一停止线立即叫停运行负责人 | 待指名 |
| 记录人 | 保全运行目录证据、更新预算账本与 `docs/ai-use-log.tsv` | 待指名 |
| 停机验证人 | 停止后在平台页面确认实例状态为"已停止"并记录 | 待指名 |

一人可兼多角色（角色可轮换，每轮启动前重新指名）；至少"指名停机负责人"这一项是 handoff §5 的硬要求。**（建议）** 停机验证人不与运行负责人为同一人：自己停自己验等于没验。

## 1. T-1 启动前门（全部勾选才能进 T0）

来源：handoff 第 5 节全部 8 项 + runbook C/D 段。T-1 通过不豁免 handoff 第 5 节的逐项核对。

- [ ] 首轮物种 2–3 个、scRNA、优先 CM/FB 子集，论文标注为金标准（handoff §5 第 1 项）；首轮 2–3 物种及后续近缘/远缘/混合类别组合已记录（runbook D-1）
- [ ] 空间数据排除在外；LBSPA 单核后置，不在本轮启动范围（handoff §5 第 2 项）
- [ ] G1：HEART 数据路径、格式、字段（`species`/`cell_type`/`batch`/`gold_label`）、可用物种清单、授权全部核实并落 `config/startup-preflight.json`
- [ ] G2：候选镜像实例内探针证据齐备（SATURN/SAMap/scVI 版本与入口、正式 kBET 实现名+版本；`BENGAL--SAMap--17` 双版本歧义已消解）
- [ ] G3：`approval_status` 脱离 `pending`（**（建议）** 批准人与日期一并记录；当前配置仅有 `approval_status` 与 `evidence.recorded_at` 字段）
- [ ] `python scripts/startup_preflight.py`（默认 `heart_pilot`）返回 `ready_for_execution: true`
- [ ] `python scripts/budget_check.py --profile 4090x1` 退出码 0（默认口径：25 分钟硬停止、30 分钟预留约 ¥8.70、单次上限 ¥10）
- [ ] 采用团队预算扩展的运行：批准的时长/金额（如 60 分钟单次估算约 ¥17.40）单独写明，不沿用默认线
- [ ] 本轮绑定账号、预算上限、硬停止时长写入运行目录 `parameters.json`
- [ ] 四名成员明确批准本轮启动（**（建议）** 记录批准时间与成员）
- [ ] 停机负责人已指名且在场；**（建议）** 已确认平台手动停机入口位置
- [ ] **（建议）** 运行目录骨架就绪：`input_manifest.tsv`、`ortholog_manifest.json`、`parameters.json` 占位

## 2. T0 启动与"先探针后任务"

顺序强制：**先只读探针，确认环境，再放真实任务**。环境与落库证据不符时停在本节，不进 2.3。

### 2.1 启动实例

- [ ] 使用预检通过的镜像（默认候选 `SATURN--22`）与 4090×1 单卡配置
- [ ] 记录实例启动时间、脱敏实例标识、所属账号
- [ ] 不上传任何自带文件；课程数据只通过 G1 已核实的共享项目路径只读访问，探针段（2.2）不读取课程数据

### 2.2 只读探针（真实任务前必做）

```powershell
python scripts/dcs_readonly_probe.py --output <运行目录>/dcs-readonly-probe.json
python scripts/environment_contract.py <运行目录>/dcs-readonly-probe.json --profile SATURN--22
```

- [ ] 探针 JSON 的 `scope` 为 `runtime_probe`
- [ ] `environment_contract.py` 无新增 unresolved 项（与 G2 基线一致）
- [ ] Python、CUDA、GPU 型号/显存，SATURN 导入名/入口/版本、SAMap 版本、scvi-tools 版本、`anndata`/`scanpy`/`torch` 版本、正式 kBET 实现名+版本全部记入 `package_versions.txt`
- [ ] 任一项与 G2 落库值不一致 → 停止并问用户，不进入 2.3；不在实例内 `pip install` 救环境

### 2.3 放行真实任务

- [ ] 任务命令、参数、seed（按计划的 7/17/27）写入 `parameters.json`
- [ ] 任务开始即重定向保存 `stdout_stderr.log`，不事后补
- [ ] **（建议）** 硬停止计时口径向全员明示：25 分钟从真实任务开始时刻计，探针段单独计时入账，两段都记录
- [ ] **（建议）** 花费口径向全员明示：单次 ¥10 按整个实例会话累计（含探针段），与"30 分钟预留约 ¥8.70"的整会话设计一致

### 2.4 运行目录必备文件（runbook D 段）

`input_manifest.tsv`、`ortholog_manifest.json`、`parameters.json`、`package_versions.txt`、`stdout_stderr.log`、`metrics.json`、`resource_usage.json`；失败运行另加非空 `failure_reason.txt`。

## 3. T1 运行中监控（监控人职责）

| 停止线 | 阈值 | 达到后动作 |
|---|---|---|
| 墙钟时间 | 25 分钟硬停止（计时口径按 2.3 评审确认结果执行；采用扩展上限的运行用批准值） | 运行负责人立即手动停止任务与实例 |
| 峰值内存 | 75 GB | 同上 |
| 单次花费 | ¥10（或批准的扩展金额；会话口径见 2.3） | 同上 |
| 平台异常 | 实例重启、掉卡、OOM 前兆、页面报错 | 停止并按第 5 节记录 `failure_reason.txt` |

- 平台预算设置**不能当作自动停机保证**；到达任一停止线以人手停机为准。
- **（建议）** 每 5 分钟记录一次：时间、任务阶段、GPU 利用率、显存、进程内存、页面可见累计花费。
- **（建议）** 任何时刻无法确认实例状态 → 按已到停止线处理，先停再说。

## 4. T2 停止与确认

### 4.1 正常停止

- [ ] 任务自然结束后**立即**停止实例（先停实例再整理文件）
- [ ] 停机验证人在平台页面确认实例"已停止/已释放"，记录确认时间与方式
- [ ] 实际花费与时长记入 `resource_usage.json` 与团队预算账本（`docs/team-budget-ledger-template.tsv` 口径）

### 4.2 紧急停止（到达任一停止线或异常）

- [ ] **（建议）** 先停任务进程，再停实例；平台无任务级停止入口时直接停实例
- [ ] **（建议）** 保全现场：`stdout_stderr.log` 尾部、脱敏页面截图、非空 `failure_reason.txt`（什么故障、何时、谁停的）
- [ ] 花费与时长照常入账

## 5. 异常处置与上报边界

- 环境与页面/落库记录不符、包缺失、入口不存在：停止并问用户；不安装包、不自行换镜像**或改卡数/配置**——4090×2 只是单卡内存不足后的例外路径（runbook C 末条），换任何配置都按新一轮启动处理，回到第 1 节。
- 数据字段与 G1 记录不符：立即停止（handoff §4 第 7 条：可能改变实验设计）。
- 出现登录、验证码、邀请、权限、付费确认：停止并问用户（handoff §4 第 1–4 条）。
- 超预算、超时长：停止（handoff §4 第 6 条）；续期按新一轮启动处理，回到第 1 节，不在运行中追加。
- 任何不确定性：**先停机，后讨论**。**（建议）** 经验法则：停错机的代价上限是一段机器费；不停机的代价没有上限。

## 6. T3 事后核验

```powershell
python scripts/run_artifacts.py <运行目录> --status success
python scripts/result_contract.py <运行目录>/metrics.json <运行目录>/resource_usage.json --stage final
```

- [ ] 两个契约检查通过（失败运行的 status 与 `failure_reason.txt` 按脚本要求另计）
- [ ] 最终指标使用留一物种评估与正式 kBET；smoke 的 `chi2_neighborhood_proxy` 不得进入 final 指标
- [ ] 预算账本、`docs/ai-use-log.tsv` 各追加一条；handoff 检查点表同步更新

## 7. 变更记录

| 日期 | 变更 | 作者 |
|---|---|---|
| 2026-09-18 | 初稿 v0（工作包 B 本地交付物） | Claude Code (GLM-5.3) |
| 2026-09-18 | v0.1：子代理独立复审后修订——补 handoff §5 第 1–2 项与 runbook D-1 物种/范围门；补齐（建议）标注（角色表、批准记录、骨架、紧急停止细则等）；明确数据访问与探针不读数据、证据清单扩至 Python/CUDA/GPU/anndata/scanpy/torch、花费与会话口径、换卡数按新一轮处理、上报统一为"停下来问用户" | Claude Code (GLM-5.3)，复审：子代理 |
