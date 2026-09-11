# 课题5组员交接单

这份交接单可以直接发到小组群。当前仓库是“准备与预检”仓库，不包含 HEART/LBSPA 原始表达矩阵，也不会自动创建或启动 DCS 任务。

## 先发给组员的消息

```text
我们课题5的 GitHub 仓库是：
https://github.com/bernis-web/course5-prep

请先接受仓库所有者的 Collaborator 邀请，再执行：
git clone https://github.com/bernis-web/course5-prep.git
Set-Location course5-prep

第一次只看这 5 个文件：
README.md
CONTRIBUTING.md
docs/team-task-division.md
docs/minimal-verification-runbook.md
config/benchmark-plan.json

请在 docs/team-task-division.md 的认领表中写下姓名和本轮小交付。
目前可以做本地测试、评测设计、课程问题整理和只读环境核验；暂时不要创建 DCS 实例、上传数据、安装包或提交云任务。
```

## 加入仓库后的共同步骤

```powershell
Set-Location <your-local-course5-prep>
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python scripts/smoke_test.py --outdir smoke-output
python scripts/plan_contract.py
```

测试数量以本次命令输出为准；2026-09-10 落实老师回复、公共 accession 边界和 Word 报告契约后应有 47 个测试通过。smoke test 只输出合成指标，这些结果只说明准备代码可用，不是三种真实工具的比较结果。

## 三人第一轮认领

| 角色 | 现在先做什么 | 交付/记录 | 复核人 |
|---|---|---|---|
| A 数据与生物学 | 按 `docs/teacher-data-request.md` 在 DCS 做只读查询；整理 HEART/LBSPA 的字段、格式、可用物种和同源基因来源 | DCS 查询记录、`config/startup-preflight.json` 的待确认项；未知保持 `null`/`pending` | C |
| B 环境与算力 | 运行本地环境、预算和只读探针；核对 `SATURN--22` 页面声明与实际入口的差异 | `config/environment-compatibility-plan.json`、预算记录、探针报告；不启动实例 | A |
| C 评测与报告 | 运行 smoke test，按 `config/benchmark-plan.json` 建立留一物种指标表和运行记录模板 | 指标表、报告骨架、artifact 检查记录；不把代理 kBET 当最终结果 | B |

这三条线可以轮换。主责是当前推进人，不是审批人；每次提交都要有另一位成员复核。

## 多轮推进节奏

第一轮不要追求把课题做完。R0-R4 都不创建 DCS 实例、不上传数据、不安装包、不提交云任务；R5 必须等启动门通过并获得三人明确批准。

| 轮次 | 建议时长 | 本轮目标 | 轮次出口 |
| --- | ---: | --- | --- |
| R0 认领与通读 | 2-4 小时 | 三人认领 A/B/C 主线，各自标记本线仍缺的证据 | 认领表填完，每人承诺一个小交付 |
| R1 本地基线 | 24 小时 | A 整理数据问题；B 跑本地预算/环境/只读探针；C 跑测试和 smoke test 并搭指标表 | 每人提交一个 draft PR，未知项保持 pending |
| R2 只读证据 | 24-36 小时 | A 查 HEART/LBSPA 页面证据；B 查镜像入口和版本；C 固化运行表格 | G1/G2 通过，或形成明确阻塞清单 |
| R3 交叉复核 | 24 小时 | A 复核 B，B 复核 C，C 复核 A，并收敛剩余问题 | 复核意见处理完，必要问题整理给老师/管理员 |
| R4 启动门审查 | 12-24 小时 | 补齐 manifest、版本、预算、停止条件和运行契约 | `startup_preflight` 通过并获三人批准 |
| R5 HEART pilot | 单次 25 分钟硬停止 | 只做 2-3 物种流程闭环，监控输入、资源和失败 | 三工具闭环或完整失败证据，不做排名 |
| R6 正式实验与报告 | 2-3 天 | 依次做近缘、远缘、混合场景，再汇总报告 | 每个结论都有 artifact、版本和资源记录 |

R1 到 24 小时就必须提交 draft PR；部分进展加阻塞原因也算有效交付。被外部信息卡住时，先换到另一条线的复核任务，不要等待整条主线解锁。

## 现在可以开始的事情

- 克隆仓库、认领任务、运行本地测试和合成 smoke test。
- 阅读两篇论文和课程网页，整理标签、物种、同源基因和评测指标问题。
- 根据老师回复先在 DCS 学术搜索、数据或镜像页面查找；只有只读查询仍找不到时，再用 `docs/course-admin-reply-template.md` 汇总剩余问题。
- 已知检索键：HEART `CNP0006537` / `10.1126/science.adw0855`，LBSPA `CNP0007565` / `10.1126/science.aea2535`。当前账号的项目公共库未命中，下一位组员应查课程共享项目或向老师确认入口，不要把 accession 填成 DCS 路径。
- 在不读取表达矩阵的前提下做本机或已授权运行时的环境探针。
- 设计真实运行的参数表、资源表和报告结构。

## 现在不能开始的事情

- 不要因为有 DCS 体验金就创建实例或提交任务。
- 不要上传原始数据，不要把数据路径、cookie、token 或密码写进仓库。
- 不要在本地 smoke-test 环境安装 SATURN、SAMap、scVI。
- 不要把论文作者的结果当作工具评测真值。
- 不要把本机 RTX 4060 或 DCS 镜像页面清单当成候选实例的实际版本证据。

## 真正开始实验前的启动清单

三人共同确认下面每一项后，才讨论第一次单卡试运行：

- HEART/LBSPA 的只读路径、文件格式、字段名、允许物种子集和数据授权已记录。
- 首轮只选 2–3 个物种打通流程；后续近缘、远缘和不同类别混合组合分别记录，不能用首轮结果代替整合效果结论。
- 主实验只使用单细胞；空间数据排除，单核实验等单细胞评测形成基本结论后再小规模启动。
- 推荐镜像已确定；在候选实例内用 `dcs_readonly_probe.py` 确认 SATURN、SAMap、scVI、Python、CUDA、GPU 和依赖版本/入口。
- 正式 kBET 实现与版本已确认；smoke test 的卡方代理不能用于最终结论。
- `python scripts/startup_preflight.py` 返回 `ready_for_execution: true`。
- `python scripts/budget_check.py --profile 4090x1` 通过；单次硬停止为 25 分钟、75 GB 峰值内存或 ¥10，任一达到就停机。
- 如果组内确认四个账号各有 ¥100，可用 `python scripts/team_budget_check.py --profile 4090x1 --reserved-minutes 60 --runs 1` 做团队预算估算；它会显示可分摊的最大运行次数。这不代表余额已合并，也不改变启动门。
- 三人明确批准，并指定一名非主责成员复核运行 artifact。

当前仓库中的启动门仍是 `approval_status: pending`，因此目前的正确动作是完成上面的确认和本地准备，而不是启动云资源。

最终结题报告交付 Word；组员先共同维护 `docs/report-template.md` 与机器可读运行结果，真实结果齐全后再按 `docs/report-delivery.md` 导出并检查 `.docx`。
当前通用 Word 骨架位于 `templates/course5-final-report-template.docx`；修改 Markdown 后运行 `python scripts/build_report_template.py` 重建，不要在两个文件中分别维护不同内容。

## 体验金如何记账

仓库把“四个账号各 ¥100”记录为规划假设，不记录账号、密码或登录态。默认预留 ¥80（每个账号 ¥20，这是暂定的规划选择，不是平台规则），团队可操作上限按 ¥320 估算；每次实际运行必须指定一个账号、记录运行前后余额和成本，并保留充值/合并规则的截图或管理员确认在组内受控位置。没有确认前，不把四个余额当成一个 ¥400 账户。

实际分配时复制 `docs/team-budget-ledger-template.tsv` 到组内受控位置填写；仓库只保留模板，不提交真实账号标识、余额截图或登录态。建议先按每个账号 4 次 60 分钟单卡运行预分配，再根据实际耗时和内存调整。

## 每次 PR 写四句话

1. 改了什么？
2. 用了哪份输入？
3. 如何验证？
4. 是否触碰 DCS？

分支从最新 `main` 创建，例如：

```powershell
git pull origin main
git switch -c codex/<short-task-name>
git add <changed-files>
git commit -m "docs: describe benchmark handoff"
git push -u origin codex/<short-task-name>
```

然后在 GitHub 上创建 Pull Request，等待另一位组员复核和 CI 通过。
