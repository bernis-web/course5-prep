# 课题5周一课堂汇报稿

> 定位：这是初步方案汇报，不是结果汇报。当前已通过本地基线检查；HEART/LBSPA 的 DCS 路径、字段、实例内版本和正式 kBET 仍处于只读核验阶段。所有 `pending` 均表示尚未取得页面或实例证据，不得用经验值填充。

## 1. 一页结论

课题5要比较 SATURN、SAMap 和 scVI 系方法在跨物种单细胞整合中的表现。我们的初步方案是：先用 HEART 的 2-3 个物种打通流程，再扩展到近缘、远缘和不同类别混合场景；LBSPA 七鳃鳗-小鼠单核数据只作为单细胞主结论后的后置补充，空间数据不进入主实验。

当前已经完成：

1. 课程网页、HEART 论文、LBSPA 论文的版本核验；
2. 本地 47 个单元测试与合成 smoke test 通过；
3. 输入、同源基因、预算、环境、结果 artifact 和启动门脚本已经落地；
4. 候选镜像与数据查询边界已经整理，当前不消耗 DCS 资源；
5. （2026-09-12）DCS 华北2/华南1 两区域只读排查完成：项目、共享项目、公共数据、公共项目全部检索词 0 条，镜像名单已刷新（SATURN--21 与 SATURN--22 页面同栈；平台无预置 kBET 镜像）；
6. （2026-09-13）给老师的提问消息已定稿发出，等待课程数据入口回复；正式实验在回复前不启动。

当前仍未通过启动门：课程数据入口待老师回复；HEART/LBSPA 的具体路径、字段、物种清单、镜像实例内入口和版本、正式 kBET 实现均待只读核验。因此方案可执行，但真实运行必须等证据补齐并经三人批准。

## 2. 课题理解

课程要求不是简单复现论文，而是做一个可审计的基准评测。核心问题拆成四层：

| 层次 | 问题 | 当前设计 |
| --- | --- | --- |
| 数据 | 用哪些物种、细胞和标签？ | HEART 2-3 物种先跑通；后续覆盖近缘、远缘、不同类别混合；LBSPA snRNA 后置 |
| 方法 | 三个工具如何公平比较？ | 相同细胞、同源基因规则、训练/留出拆分、随机种子和资源记录 |
| 评价 | 什么算好？ | macro-F1、正式 kBET、iLISI、silhouette、时间、峰值内存、文档与 Agent 友好度 |
| 复现 | 其他人能否接手？ | Git 分支、manifest、参数、版本、日志、指标、资源文件和 AI 使用日志 |

关键风险是把“论文作者结果”误当成“我们实验结果”。论文数值只能作为背景和外部参考，小组结论必须来自自己的真实运行 artifact。

## 3. 文献精读陈述

### 3.1 HEART 论文

论文：*Spatially resolved single-cell atlas reveals the macroevolutionary trajectory of animal hearts*，DOI `10.1126/science.adw0855`。

可用于课堂陈述的 60-90 秒版本：

> 这篇论文构建了动物心脏的跨物种单细胞图谱。论文报告 27 个物种的多组学资源，scRNA-seq 部分包含 14 个物种、399,483 个细胞；在细胞保守性分析中，作者用 SATURN 整合 16 个物种、479,483 个细胞，并用 SAMap 做跨物种细胞类型映射。方法上，论文记录了 ESM2B 蛋白嵌入、2,000 个 macrogenes 和 8,000 个 HVGs。对我们课题的直接意义是：HEART 提供了跨物种细胞标签、物种范围和一个论文级参考结果；但它不能直接替代我们的评测，因为我们仍要做留一物种标签转移和统一评分。论文的 CNGB accession 是 `CNP0006537`，处理后数据门户在 `https://db.genomics.cn/stomics/heart/`。这些是公共来源标识，不能当作 DCS 课程挂载路径。

精读时要能回答：

1. 为什么 HEART 适合作为主实验数据：物种跨度大、有论文发布注释、可先选小规模 CM/FB 子集；
2. 为什么不能直接采用作者结果：我们的任务是工具评测，必须统一输入、拆分、种子和指标；
3. 为什么先做 2-3 物种：先证明数据读取、预处理、整合、标签转移、指标导出和资源记录全部闭环；
4. 为什么 accession 不是路径：公共检索键只说明来源，DCS 挂载路径、格式和字段必须另行只读核实。

### 3.2 LBSPA 论文

论文：*Lamprey 3D single-cell transcriptomics reveals ancestral and specialized features of the vertebrate brain*，DOI `10.1126/science.aea2535`。

可用于课堂陈述的 60-90 秒版本：

> 这篇论文构建了七鳃鳗全脑三维空间转录组图谱，报告 465,778 个空间细胞、约 200 万个估计总细胞、41,678 个高质量单核转录组和 209 个细胞簇。七鳃鳗-小鼠比较保留 6,930 个一对一同源基因，作者在跨物种/模态整合中使用 scVI，并以 Harmony 嵌入做后续聚类和可视化。对我们课题的意义是：它提供了一个跨门类、单核数据的后置补充场景，可以检验单细胞主结论在同源基因更稀疏、测量对象为核转录组时是否稳健。老师已明确空间数据暂不进入主实验，因此我们只把 LBSPA 的 snRNA 数据放在单细胞主结论之后做小规模补充，避免把物种差异和模态差异混在一起。

精读时要能回答：

1. 为什么 LBSPA 后置：跨门类同源基因更稀疏，直接放入首轮会同时改变物种距离、模态和标签体系；
2. 为什么空间数据排除：主实验是单细胞工具评测，空间数据会引入额外模态偏差；
3. 为什么保留 snRNA：它可以作为主结论后的稳健性补充，但仍需单独报告，不与 scRNA 排名混写；
4. 为什么必须核验 6,930 个一对一同源基因的来源和格式：不同工具对物种对顺序和一对多映射的处理不同。

## 4. 可执行初步方案

### 4.1 阶段门

| 阶段 | 允许做的事 | 通过条件 | 禁止事项 |
| --- | --- | --- | --- |
| G0 本地基线 | 本地测试、合成 smoke、契约检查 | 测试与 smoke 通过 | 安装真实工具、触碰云资源 |
| G1 数据只读 | DCS 页面与元数据查询 | 路径、格式、字段、物种、授权边界有证据 | 猜路径、复制原始数据 |
| G2 环境只读 | 查看镜像和运行时入口 | 实例内导入名、版本、GPU、kBET 有证据 | 把页面清单当实例证据 |
| G3 启动许可 | 申请一次最小试运行 | `startup_preflight` 通过且三人批准 | 未过门先创建实例 |
| G4 HEART pilot | 2-3 物种端到端流程 | 三工具闭环或完整失败证据 | 用 pilot 做工具排名 |
| G5 主实验与报告 | 近缘/远缘/混合场景、LBSPA 后置 | 指标、资源、失败原因可复核 | 用合成结果或论文结果替代 |

### 4.2 非本课题同学接手卡

目标：任何人拿到仓库和 DCS 权限后，都能从同一个入口开始，不需要先追问隐藏上下文。

```powershell
git clone https://github.com/bernis-web/course5-prep.git
Set-Location course5-prep
git switch -c codex/<short-task-name>
python -m pip install -r requirements.txt

python -m unittest discover -s tests -v
python scripts/smoke_test.py --outdir smoke-output
python scripts/plan_contract.py
python scripts/budget_check.py --profile 4090x1
python scripts/startup_preflight.py
```

预期：单元测试、smoke test 和计划契约通过；`startup_preflight.py` 在外部证据未补齐时返回退出码 2 是安全阻塞，不是脚本崩溃。此时不能创建实例、上传数据、安装包或提交云任务。

接下来按角色执行：

| 角色 | 只读任务 | 交付 |
| --- | --- | --- |
| A 数据与生物学 | 在 DCS 查 HEART/LBSPA 路径、格式、物种、细胞类型、批次、金标准字段 | `startup-preflight.json` 数据项、`input_manifest.tsv`、同源基因说明 |
| B 环境与算力 | 查镜像入口、实例内导入名、版本、CUDA/GPU、正式 kBET | `environment-compatibility-plan.json`、预算与停止清单 |
| C 评测与报告 | 固化指标表、留一物种折、artifact 检查和报告骨架 | `benchmark-plan.json`、运行表格、报告模板 |

### 4.3 统一实验协议

1. 数据子集：HEART 首轮只用 2-3 个物种、CM/FB 两类细胞；物种名等待 DCS 页面证据，不提前填写。
2. 标签评估：留一物种标签转移，训练时不使用被留出物种标签；报告每折和聚合 macro-F1。
3. 基因空间：需要同源基因的方法统一使用一对一同源基因表；HVG 只在训练折拟合。
4. 随机种子：7、17、27；每个场景报告均值、标准差和全部失败折。
5. 指标：macro-F1、正式 kBET、iLISI、细胞类型 silhouette、物种/批次混合诊断、墙钟时间、峰值内存、GPU/CPU 和成本。
6. 结果解释：kBET rejection 越低、iLISI 和标签 silhouette 越高通常更好；物种过度分离或过度混合都要解释，不能只优化一个指标。
7. Agent 友好度：文档清晰度、CLI/API、参数透明、机器可读输出、失败诊断、环境复现六项；没有本地证据的条目保持 `pending`，不当作 0 分。

### 4.4 每次运行必备文件

`input_manifest.tsv`、`ortholog_manifest.json`、`parameters.json`、`package_versions.txt`、`stdout_stderr.log`、`metrics.json`、`resource_usage.json`；失败运行另加 `failure_reason.txt`。

运行后执行：

```powershell
python scripts/run_artifacts.py <run-directory> --status success
python scripts/result_contract.py <run-directory>/metrics.json <run-directory>/resource_usage.json --stage final
```

## 5. 算力与风险控制

默认配置：4090x1，单次 25 分钟硬停止、75 GB 峰值内存停止线、¥10 成本上限，任务结束立即停止实例。当前 30 分钟预留成本约 ¥8.70，低于单次上限；4090x2 不是默认路径，只能在单卡内存不足且有完整失败证据后申请。

主要风险与应对：

| 风险 | 表现 | 应对 |
| --- | --- | --- |
| 数据入口找不到 | 搜索 0 条或字段缺失 | 记录搜索范围，继续查课程共享项目，最后集中问老师 |
| 镜像版本冲突 | 页面同时出现多个版本或无入口 | 实例内只读 `import/which/version`，不能任意挑选 |
| pilot OOM/超时 | 内存、时间或成本触发停止 | 保存失败 artifact，缩小物种数、细胞数或运行时间 |
| 指标不可比 | 输入、种子或环境不同 | 统一 manifest、拆分、种子、版本和资源记录 |
| 把论文结果当结论 | 报告缺少小组运行目录 | 结论只引用本组 artifact，论文结果只做背景 |

## 6. 小组成员分工

姓名在展示前由组内替换；A/B/C 是可轮换主线，不是固定身份。

| 成员 | 主线 | 当前小交付 | 复核人 |
| --- | --- | --- | --- |
| ____ | A 数据与生物学 | HEART/LBSPA 路径、字段、物种、标签、同源基因来源 | C |
| ____ | B 环境与算力 | 镜像入口、版本、GPU/CUDA、预算、停止规则 | A |
| ____ | C 评测与报告 | 指标表、留一物种设计、artifact 检查、报告骨架 | B |

多轮节奏：

| 轮次 | 时长 | 出口 |
| --- | ---: | --- |
| R0 认领与通读 | 2-4 小时 | 认领表完成，每人承诺一个小交付 |
| R1 本地基线 | 24 小时 | 每人一个 draft PR，未知项保持 pending |
| R2 只读证据 | 24-36 小时 | G1/G2 通过或形成阻塞清单 |
| R3 交叉复核 | 24 小时 | 三人互审，剩余问题收敛 |
| R4 启动门审查 | 12-24 小时 | preflight 通过并获三人批准 |
| R5 HEART pilot | 25 分钟硬停止 | 三工具闭环或完整失败证据 |
| R6 正式实验与报告 | 2-3 天 | 每个结论可追溯到运行 artifact |

## 7. 周一 PPT 页面安排

| 页 | 标题 | 展示重点 |
| ---: | --- | --- |
| 1 | 封面 | 课题、组员、日期 |
| 2 | 一页结论 | 已完成、待核验、当前不启动云资源 |
| 3 | 课题理解 | 数据、方法、评价、复现四层拆解 |
| 4 | HEART 精读 | 数据规模、SATURN/SAMap 用法、 accession 边界 |
| 5 | LBSPA 精读 | 空间与 snRNA 区分、后置理由 |
| 6 | 数据与场景设计 | pilot、近缘、远缘、混合、LBSPA 补充 |
| 7 | 统一评测协议 | 相同输入、留一物种、三种种子、指标集合 |
| 8 | 执行路线 | R0-R6 与阶段门 |
| 9 | 接手操作卡 | 克隆、安装、测试、只读核验、启动门 |
| 10 | 启动门与预算 | 25 分钟/75GB/¥10 硬停止 |
| 11 | 分工与复核 | A/B/C 主线与交叉复核 |
| 12 | 风险与应对 | 数据入口、版本冲突、OOM、指标不可比 |
| 13 | 结论与下一步 | 先补 G1/G2 证据，再申请 pilot |

## 8. 证据文件索引

| 内容 | 文件 |
| --- | --- |
| 课程要求核对 | `docs/course-requirements-audit.md` |
| 论文来源笔记 | `docs/source-notes.md` |
| 数据只读清单 | `docs/teacher-data-request.md` |
| DCS 只读核验记录 | `docs/dcs-readonly-audit.md` |
| 本地验证流程 | `docs/minimal-verification-runbook.md` |
| 实验计划真源 | `config/benchmark-plan.json` |
| 分工与轮次 | `docs/team-task-division.md` |
| 镜像核验计划 | `docs/dcs-image-probe-plan.md` |
| 容器化边界 | `docs/containerization-plan.md` |
| 启动门配置 | `config/startup-preflight.json` |
| 预算配置 | `config/dcs-budget-plan.json` |

重建 PPT：

```powershell
python scripts/build_monday_presentation.py
```

输出：`deliverables/course5-monday-presentation.pptx`。
