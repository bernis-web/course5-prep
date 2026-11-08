# 四人小组协作分工

这不是固定排班，而是三条可以轮换的主线。四人团队中，三名成员（A/B/C）各先主责一条线，另一名成员（D）机动复核、协调轮换和阻塞；每名成员同时至少复核另一条主线的一个交付物。不要因为分工而绕过共同的启动门和预算规则。姓名不写死在仓库里，组内可以把 A/B/C/D 替换成实际姓名，也可以在下一阶段轮换主线。

## 打开仓库后的 5 分钟

1. 依次阅读 README.md、CONTRIBUTING.md、本文件、docs/minimal-verification-runbook.md、config/benchmark-plan.json 和 docs/teacher-data-request.md。
2. 在下面的认领表填入姓名、当前小交付和复核人；只认领一项近期可完成的交付，不需要一次包办整条主线。
3. 先完成本地或文档工作，再讨论 DCS。任何真实运行都要等四人共同确认启动门、数据授权、版本和预算。

### 当前认领表（可直接复制到 Issue 或 PR 描述）

| 成员 | 初始主线 | 本轮小交付 | 复核人 | 状态 |
| --- | --- | --- | --- | --- |
| 组员 A：____ | 数据与生物学 | ____ | 组员 C：____ | pending |
| 组员 B：____ | 环境与算力 | ____ | 组员 A：____ | pending |
| 组员 C：____ | 评测与报告 | ____ | 组员 B：____ | pending |
| 组员 D：____ | 机动复核/协调 | ____ | 组内轮换 | pending |

“主线”只表示当前推进人，不是文件所有权；任何人都可以修复另一条主线的问题，但提交前要通知主责并留下验证证据。

### 当前看板（2026-09-17）

A/B/C/D 四线的当前快照；证据只指向具体文档，不复制结论。状态变化时先改本表再改认领表；未知项保持空白或 `pending`，不预填。

| 线 | 负责人角色 | 状态 | 证据 | 阻塞 | 下一动作 |
| --- | --- | --- | --- | --- | --- |
| A 数据与生物学 | 组员 A 主责；C 交叉复核 | 进行中（仅账号1 完成） | `docs/dcs-readonly-audit.md`：账号1 两轮只读排查，两区域按 HEART/LBSPA/CNP 检索均 0 命中 | 账号2–4 待查；课程共享项目/数据入口未知 | 账号2–4 按该文件的空白槽位各自补只读记录；见到入口即记录脱敏标识、格式与字段 |
| B 环境与算力 | 组员 B 主责；A 交叉复核 | 页面级候选已记录；实例内未开始 | 镜像候选 `SATURN--22/--21`、`samap_all`、`BENGAL--SAMap--17`、`scvi_zt` 见 `docs/dcs-readonly-audit.md` | 镜像网页清单版本 ≠ 实例内真实版本；GPU 与正式 kBET 实现/版本全部 `pending`；受控启动未获批 | 做页面级复核并起草启动/停止检查清单；获批后才在实例内消解 SAMap 双版本歧义并取证 |
| C 评测与报告 | 组员 C 主责；B 交叉复核 | 仓库层复跑通过；组员复核待认领 | 2026-09-17 已复跑 50 个测试、synthetic smoke、plan/result/artifact contract，并重建 Word 模板；见 `docs/next-round-handoff.md` 第 0 节 | 尚无真实工具或真实数据结果；smoke 与 fixture 只能证明结构，不能用于排名或结论 | C/B 按 `docs/minimal-verification-runbook.md` 各自复核并记录当次证据；真实运行后再替换占位结果 |
| D 机动复核 | 组员 D | 待分派 | — | 首轮不绑主线 | 至少交叉复核一条线的一项交付物，并维护本看板与轮换安排 |

## 打开仓库后的轻量认领

先把自己的名字写进分支名或 Pull Request 标题，再从下面选一条主线。表里的“第一件事”是为了让大家马上能开始，不代表以后只能做这一类工作。

| 建议认领 | 主要关注 | 第一件事（不需要云资源） | 主要交付位置 | 建议复核 |
| --- | --- | --- | --- | --- |
| 组员 A | 数据与生物学 | 根据老师回复先在 DCS 逐项只读查询 `docs/teacher-data-request.md` 的剩余证据，不要猜路径、字段或物种名 | `config/startup-preflight.json`、`input_manifest.tsv`、`ortholog_manifest.json` | 组员 C 复核标签转移和金标准定义 |
| 组员 B | 环境与算力 | 运行本地预算/环境预检，读懂 `docs/dcs-image-probe-plan.md` 的证据边界，先不启动实例 | `config/environment-compatibility-plan.json`、`config/dcs-budget-plan.json`、资源记录 | 组员 A 复核数据挂载与内存假设 |
| 组员 C | 评测与报告 | 运行测试与合成 smoke test，按 `config/benchmark-plan.json` 建立真实数据的指标表骨架 | `tests/`、`config/benchmark-plan.json`、运行报告 | 组员 B 复核版本、时间、内存和公平性记录 |

如果某条主线被课程确认事项卡住，可以先接手另一条主线的复核任务；认领人负责推进和记录，所有人共同决定是否进入真实运行。没有必要为了“分工完整”提前填写未知信息。

## 主线 A：数据与生物学

**建议主责：** 熟悉论文、数据结构和细胞类型定义的同学。

**第一步：** 根据 `docs/teacher-data-request.md` 在 DCS 学术搜索、数据和镜像页面只读查询 HEART/LBSPA 路径、文件格式、物种/细胞类型/批次/金标准字段，以及一对一同源基因表的来源。实在找不到的项目再汇总到 `docs/course-admin-reply-template.md`。

**交付物：**

- 填写 `config/startup-preflight.json` 中的数据字段和子集信息；
- 为每个数据子集准备不含原始表达矩阵的 `input_manifest.tsv`、同源基因源表和 `ortholog_manifest.json`；
- 用 `python scripts/ortholog_contract.py <ortholog-table.tsv> --output <ortholog_manifest.json>` 检查一对一同源基因表，并把 SHA-256 和物种对写入运行记录；
- 在 `docs/source-notes.md` 或新的数据说明中记录标签来源、排除规则和 modality 边界。

**需要协作：** 请环境与算力主线复核路径是否可读、文件是否适合候选镜像；请评测与报告主线复核留一物种标签转移设计。

## 主线 B：环境与算力

**建议主责：** 愿意核对 DCS 页面、镜像和资源成本的同学。

**第一步：** 在获得课程管理员确认后，按 `docs/dcs-image-probe-plan.md` 和 `docs/containerization-plan.md` 做只读核验，再用 `environment_check.py` 和 `environment_contract.py` 检查 `SATURN--22`、`samap_all` 或课程指定镜像；不安装包、不启动实例，除非组内明确批准。

**交付物：**

- 更新 `config/environment-compatibility-plan.json` 的实例内版本和命令级证据；
- 更新 `config/dcs-budget-plan.json` 或运行资源记录，保留价格来源、GPU/内存、耗时和停止原因；
- 为一次单卡 smoke run 写出可复用的启动/停止检查清单。

**需要协作：** 请数据与生物学主线确认挂载路径和内存需求；请评测与报告主线确认同一工具是否在公平的容器和版本条件下比较。

## 主线 C：评测与报告

**建议主责：** 擅长指标、可视化、写作或整理实验记录的同学。

**第一步：** 先在合成数据上运行测试，确认 macro-F1、silhouette、iLISI、kBET 代理和资源记录格式，再设计真实数据的留一物种评估表。

**交付物：**

- 维护 `config/benchmark-plan.json` 的固定随机种子、HVG、邻居数和指标定义；
- 用 `run_artifacts.py` 检查每次运行的参数、版本、日志、指标和资源文件；
- 汇总 `agent_evaluation.py` 所需的命令/API、输出和失败证据，最终形成基准报告和场景化选型指南。

**需要协作：** 请数据与生物学主线复核金标准和生物保守性解释；请环境与算力主线复核时间、峰值内存、GPU 和成本记录。

## 共同工作方式

1. 任何人都可以接手另一条主线；主责只是当前推进人，不是审批人。
2. 每个 Pull Request 说明：改了什么、使用了哪份输入、如何验证、是否触碰 DCS。
3. 真实运行前，四个人共同确认 `startup_preflight.py` 返回 `ready_for_execution: true`，并明确单次预算和停止条件。
4. 真实运行后，至少一名非主责成员复核 manifest、版本、日志、资源和失败原因；AI 使用记录追加到 `docs/ai-use-log.tsv`。
5. 任何路径、版本或指标未确认时，宁可标记 `pending`，不要用猜测填满表格。

### 第一轮建议动作

- **组员 A：** 用 docs/teacher-data-request.md 整理 DCS 只读查询结果；老师已确认数据在平台上，但具体路径、字段和可用物种仍要用页面证据落库，找不到时再提问。
- **组员 B：** 运行本地预算、环境和只读探针，重点看 smoke-output/dcs-readonly-probe.json 与 config/dcs-budget-plan.json；不要安装包、启动实例或把凭据写进日志。
- **组员 C：** 运行单元测试和合成 smoke test，阅读 config/benchmark-plan.json，先搭出真实运行的指标/资源记录表，不把合成代理指标写成最终结果。
- **组员 D：** 机动复核/协调；优先复核被外部确认卡住的主线，并维护认领表与轮换安排。

第一轮完成后，A 复核 B 的数据挂载与内存假设，B 复核 C 的版本/资源记录，C 复核 A 的标签和金标准定义。若某条线被外部确认事项卡住，直接交换小交付，不必等待整条主线解锁。

### 多轮推进节奏

时间从四人完成认领时起算；如果课程时间冲突，可以整体平移，但每轮仍要有明确出口。R0-R4 只做本地、文档和只读核验，不创建实例、不上传数据、不安装包、不提交云任务；R5 必须等启动门和组内批准完成后才开始。

| 轮次 | 建议时长 | A：数据与生物学 | B：环境与算力 | C：评测与报告 | 轮次出口 |
| --- | ---: | --- | --- | --- | --- |
| R0 认领与通读 | 2-4 小时 | 标记 teacher-data-request 中仍缺的证据项 | 标记预算、镜像和启动门中仍缺的证据项 | 标记 benchmark plan 中待落地的表格和 artifact | A/B/C 主责与 D 机动复核均已登记，每人只承诺一个小交付 |
| R1 本地基线 | 24 小时 | 整理数据问题清单，未知项保持 pending | 运行本地环境、预算和只读探针 | 运行单元测试与合成 smoke test，搭指标表骨架 | 每人提交一个 draft PR，写四句话说明 |
| R2 只读证据 | 24-36 小时 | 在 DCS 页面只读查 HEART/LBSPA 路径、格式、物种和字段 | 查候选镜像入口、版本和 GPU 证据，不启动实例 | 固化真实运行指标表、留一物种折和资源记录格式 | G1/G2 通过，或形成明确阻塞清单 |
| R3 交叉复核 | 24 小时 | 复核 B 的路径、内存和数据挂载假设 | 复核 C 的版本、资源记录和公平性 | 复核 A 的标签、金标准和生物学解释 | 交叉复核完成，剩余问题收敛成最小询问清单 |
| R4 启动门审查 | 12-24 小时 | 提交数据 manifest、同源基因表和标签来源 | 提交镜像版本、预算、停止条件和启动/停止清单 | 提交运行契约、随机种子、报告骨架和 artifact 检查 | startup_preflight 通过并获四人明确批准 |
| R5 HEART pilot | 单次 25 分钟硬停止 | 监控物种、标签和输入子集是否符合 manifest | 监控时长、内存、费用和停止原因 | 收集日志、指标和资源文件，写流程小结 | 三工具闭环或留下完整失败证据，不做排名 |
| R6 正式实验与报告 | 2-3 天 | 解释近缘、远缘和混合场景的生物学合理性 | 管理多轮运行预算、资源和失败重试 | 汇总正式指标、图表、局限和 Word 报告 | 每个结论都能追溯到运行 artifact 并经复核 |

轮次纪律：

1. R1 到时间就提交 draft PR；部分进展、pending 和阻塞原因也是有效交付，不许为了“完整”拖延整轮。
2. 任何人被外部确认卡住时，先换到另一条线的复核或小交付，不让整条主线停摆。
3. R2 的页面声明不能替代实例证据；如果查不到入口或版本，保持 pending 并记录查询位置。
4. R4 未通过前不讨论“先试一下云环境”；R5 只做 2-3 物种流程验证，不扩大到正式结论。
5. 每轮结束时在 PR 或群消息中写：已完成、证据文件、仍阻塞、下一步。

### 每次提交只回答四件事

Pull Request 或工作记录尽量写清楚：改了什么、使用了哪份输入、如何验证、是否触碰 DCS。四名成员可以共同修改任何一条主线，但每次提交最好只推进一个小问题，方便互相复核和回退。

## 推荐的第一周顺序

1. A 在 DCS 核实数据、字段和候选物种；B 复核仓库中的预算/镜像约束；C 运行本地测试套件并熟悉运行产物（测试数量以当前仓库输出为准）。
2. A 拿到字段后更新启动门；B 根据只读环境报告更新镜像证据；C 准备真实运行的指标表和报告骨架。
3. 四人共同审查启动门和预算，确认后再决定是否申请第一次单卡试运行。

## 2026-09-24 课题五审计交接附录

本附录覆盖 v71/v72 审计阶段，优先级高于上面的历史 R0-R6 快照，但不删除历史记录。
详细的逐项判定见 `docs/audit-coverage-matrix-20260924.md`；DCS 只读取证直接按 `docs/dcs-v71-v72-evidence-request-20260924.md` 执行。

| 角色 | 当前小交付 | 交付物 | 明确不要做的事 |
| --- | --- | --- | --- |
| 数据与生物学 | 只读取得 v71/v72 的输入路径、标签列、物种和 barcode 角色；整理 HEART 同源 cell-type 证据 | `config/eval-manifest-v73.json`、`config/barcode-roles-v73.tsv`、`config/heart-celltype-map-v1.tsv` | 不猜路径、标签映射或 barcode；不把论文作者结果当真值 |
| 环境与算力 | 只读确认原始命令、task ID、完整日志、Final AnnData hash 和 SATURN 源码版本/补丁 hash；核对表示层和资源记录 | provenance 记录及 manifest 中的命令、路径、源码/数据 hash 字段 | 不启动 DCS、不上传数据、不充值、不安装依赖 |
| 评测与报告 | 用显式 NPZ bundle 验收 exact/mapped 双评分、barcode 泄漏排除和 inductive/transductive 两套协议 | `scripts/evaluate_cross_species_transfer.py` 的本地输出、逐细胞预测和审计摘要 | 不把 v72 transductive 数字写成 held-out benchmark |
| 机动复核 | 复核一条主线的证据和文档一致性，维护阻塞清单 | `docs/audit-coverage-matrix-20260924.md` 及复核记录 | 不清理或回退已有用户文件，不修改研究结果 |

### 进入下一阶段的共同门槛

只有当原始 DCS provenance、barcode 角色、标签映射和表示层全部落库后，才讨论容量消融或正式方法排名。当前三物种 HEART pilot 的本地启动门已通过；LBSPA snRNA 仍必须等待 scRNA 主评估结论和数据路径。

## 2026-09-25 续审轮：可直接认领的三个重任务

本轮优先把“已有本地结果”与“尚缺 DCS 原始证据”分开。三名组员各认领一条主线，第四人只做交叉复核；没有证据的字段继续写 `pending`。本轮不创建云任务、不上传数据、不改研究结果。

| 认领线 | 具体动作 | 交付物 | 完成判据 |
| --- | --- | --- | --- |
| A：DCS provenance（适合 Claude/zcode 重查页面） | 只读核对 v71/v72 task ID、原始命令、完整日志、Final AnnData/epoch scores 路径与 hash、query/reference barcode 文件、表示层 | `config/eval-manifest-v73.json`、`config/barcode-roles-v73.tsv` 的脱敏回填；附查询时间和页面位置 | 6 类核心证据均有来源；缺失项明确写 `pending`，没有猜填 |
| B：本地评测与泄漏审计（适合 Claude/zcode 跑脚本） | 生成显式 NPZ bundle（只在获授权的本地副本上），运行 exact/mapped、transductive/inductive 双协议，检查重复 barcode、query/reference 交集和逐细胞输出 | `summary.json`、逐细胞预测表、提取命令与 SHA-256 记录 | 评分器测试通过；输出含 accuracy/F1/top-k/coverage/abstention/混淆矩阵；协议标签清楚 |
| C：论文方法与报告边界（适合熟悉文献的成员） | 将 HEART、LBSPA、BENGAL、scSpecies、CAMEX 的“方法启发”和“不能替代的项目证据”逐项整理，核对 Word 报告中的已证实/探索性/待补证据三栏 | `docs/paper-method-evidence-20260924.md`、`docs/source-evidence-index-20260924.tsv` 的审阅记录；Word 报告提纲 | 每条论文结论都有一手来源；没有把论文结果填入 DCS manifest 或本项目真值 |

### 本轮统一回报格式

每条线只需回报四项：`已完成`、`证据文件/页面位置`、`仍阻塞`、`下一步`。A 若无法从 DCS 页面取得任务详情，应把页面入口、查询时间和“未显示字段”记录下来，而不是反复重试或启动新任务。B 若没有经过授权的 NPZ 提取物，只完成评分器合成测试，不生成正式结果。C 若 HEART 原 PDF 不可重新读取，必须沿用 A/B/C 证据分层并明确说明来源等级。
