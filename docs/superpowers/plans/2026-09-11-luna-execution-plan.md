# Luna 课题5执行计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to execute this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** 让 Luna 在不猜测数据、不泄露凭据、不浪费 DCS 体验金的前提下，完成课题5“跨物种单细胞整合工具评测”的可复现准备、分阶段试跑、正式评测和 Word 报告交付。

**Architecture:** 以 config/benchmark-plan.json 为实验规则真源，以每次运行目录中的 manifest、参数、版本、日志、指标和资源文件为证据链。HEART 单细胞先做 2--3 物种流程试跑，再覆盖近缘、远缘和不同类别组合；LBSPA 七鳃鳗--小鼠单核只在单细胞主结论形成后做小规模补充，空间数据不进入主实验。

**Tech Stack:** DCS Cloud（只在启动门通过后使用）、Python、AnnData/Scanpy、SATURN、SAMap、scVI、正式 kBET、iLISI、silhouette、scikit-learn、仓库现有 Python 脚本、Markdown/JSON 源文件和 DOCX 导出脚本。

## Global Constraints

- 未通过 python scripts/startup_preflight.py 前，不创建实例、不提交任务、不上传数据、不安装 DCS 包、不下载大文件。
- 不把论文公共 accession 当成课程数据路径；未知路径、字段、物种、入口和版本保持 null/pending，不能凭经验填写。
- HEART 首轮只用 2--3 个物种，目标是证明端到端流程能运行，不据此评价远缘整合能力。
- 正式主实验只使用单细胞数据；LBSPA 单核是后置小实验，空间数据暂不纳入。
- 三种方法使用同一批细胞、同一物种拆分、同一同源基因规则、同一随机种子集合和同一评测协议；方法原生参数必须逐项记录。
- 最终结论只能来自真实运行 artifact；合成 smoke test、示例 JSON 和论文作者结果不能写成小组实验结果。
- 四个账号按账号分别记账，不能默认余额合并；延长运行、双卡或充值必须由组内明确批准。
- 任何日志、截图、提交和报告都不得包含密码、cookie、token、账号标识或未经授权的原始数据路径。

## 给 Luna 的首条提示词

下面内容可以直接发送给 Luna：

    你负责执行仓库 D:\projects\course5-prep 中的课题5准备与评测计划。请持续推进，不要只回复两句话就停；每完成一个可验证的小步骤就继续下一步。第一轮目标是完成本地基线、DCS 只读盘点和候选镜像只读核验，形成可审计 checkpoint；在启动门通过前绝不能创建 DCS 实例、上传数据、安装包、提交任务或消费余额。

    先阅读 README.md、CONTRIBUTING.md、config/benchmark-plan.json、config/startup-preflight.json、docs/minimal-verification-runbook.md、docs/teacher-data-request.md、docs/report-delivery.md 和本计划。先运行仓库已有本地检查，再处理 DCS 页面证据。不要猜测 HEART/LBSPA 的路径、字段、物种清单、镜像入口、软件版本或正式 kBET 版本；找不到就保持 pending，并记录查过哪里、得到什么、还缺什么。

    执行顺序固定为：
    1. 本地测试、合成 smoke test、计划/预算/环境契约检查。
    2. DCS 只读核实 HEART 格式、路径、字段、物种、论文标签和 LBSPA snRNA 路径；空间数据不纳入主实验。
    3. 候选镜像内只读核实 SATURN、SAMap、scVI、CUDA/GPU、正式 kBET 的真实导入名和版本。
    4. 启动门全部通过后，HEART 先做 2--3 物种 CM/FB 单细胞 pilot，只验证流程闭环。
    5. pilot 通过后，构造近缘、远缘和不同类别混合场景，使用留一物种标签转移和三个随机种子进行正式比较。
    6. 单细胞主结论形成后，才小规模做 LBSPA 七鳃鳗--小鼠 snRNA 补充。
    7. 所有运行完成 artifact 检查，再把真实结果填入 Markdown 源文件并导出 Word。

    每个阶段结束时写状态：已完成、证据文件、仍阻塞项、下一步。如果没有外部阻塞就继续执行，不等待我重复提醒；只有启动门、预算或数据授权必须由人批准时才暂停。

## 阶段门

| 门 | 允许做的事 | 必须具备的证据 | 未通过时 |
|---|---|---|---|
| G0 本地基线 | 仓库脚本和合成数据 | 测试、smoke、契约报告 | 修复本地问题，不能进 DCS |
| G1 数据只读 | 查询 DCS 目录和元数据 | 路径、格式、字段、物种、授权边界 | 记录 pending，必要时问老师 |
| G2 环境只读 | 查看候选镜像和运行时 | 导入名、版本、GPU、kBET | 只生成方案，不安装 |
| G3 启动许可 | 一次小规模试跑 | startup_preflight ready、预算通过、组内批准 | 不创建实例 |
| G4 pilot 通过 | 扩展正式场景 | 三工具闭环或完整失败证据 | 保留失败原因，先修复 |
| G5 主实验结论 | snRNA 补充和报告 | 指标、资源、限制已复核 | 不提前使用空间数据 |

## Task 0：本地基线

**读取：** README.md、CONTRIBUTING.md、config/benchmark-plan.json、config/startup-preflight.json、docs/minimal-verification-runbook.md。

**本地证据命令：**

    Set-Location D:\projects\course5-prep
    git status --short --branch
    git log --oneline -5
    python -m unittest discover -s tests -v
    python scripts/smoke_test.py --outdir smoke-output
    python scripts/plan_contract.py
    python scripts/environment_check.py --output smoke-output/environment-report.json
    python scripts/dcs_readonly_probe.py --output smoke-output/dcs-readonly-probe.json
    python scripts/environment_contract.py smoke-output/dcs-readonly-probe.json --profile SATURN--22
    python scripts/budget_check.py --profile 4090x1
    python scripts/team_budget_check.py --profile 4090x1 --reserved-minutes 60 --runs 1
    python scripts/startup_preflight.py

记录日期、退出码、测试数和输出路径；不提交被 Git 忽略的运行输出。测试和 smoke/plan 检查应为 0；外部信息未补齐时 startup_preflight/readiness 返回 2 是安全阻塞，不是脚本崩溃。

**验收：** G0 证据新鲜；没有创建 DCS 任务，没有安装包。

## Task 1：DCS 只读数据盘点

**修改范围：** 只有在证据出现后才更新 config/startup-preflight.json、docs/dcs-readonly-audit.md、docs/source-notes.md。

1. 检查当前项目数据、课程/共享项目、公共数据和数据集搜索。搜索论文题名以及 CNP0006537、CNP0007565，记录页面位置和结果数；一次目录 0 条不能证明不存在。
2. HEART 只记录有证据的路径或数据集 ID、对象格式、物种字段、细胞类型字段、批次字段、论文标签字段、可用物种及 CM/FB 是否存在。
3. LBSPA 只记录七鳃鳗/小鼠 snRNA 路径和结构字段；空间数据写明 out_of_primary_scope。
4. 已知路径后运行只读对象检查，只打印对象类型、n_obs、n_vars 和元数据列名，不打印行、基因名、表达值或凭据。
5. 不获授权时不把私有挂载路径写入 Git，使用脱敏数据集键。

**验收：** HEART 和 LBSPA 结构信息都有独立页面或对象证据才通过 G1；否则保持 approval_status pending，并写出给老师的最小问题清单。

## Task 2：候选镜像和运行时只读核验

候选优先级：SATURN--22 作为默认 GPU 候选；BENGAL--SAMap--17 与 samap_all 作为 SAMap 候选；scvi_zt 仅作 CPU 兼容参考。页面声明不是实例证据，BENGAL 页面同时出现两个 SAMap 版本必须视为冲突。

在候选运行时只读执行：

    python -c "import sys; print(sys.version)"
    python -c "import importlib.util; names=['saturn','samap','scvi','anndata','scanpy','kbet']; print({n: bool(importlib.util.find_spec(n)) for n in names})"
    python -c "import importlib.metadata as m; names=['saturn','samap','scvi-tools','anndata','scanpy','kbet']; print({n: (m.version(n) if importlib.util.find_spec(n.replace('-','_')) else None) for n in names})"
    nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader

记录每个方法的实际 import、命令/可调用模块、版本、CUDA/GPU 可见性和证据文件。若缺包，只生成安装计划或换镜像建议，不自动安装。

**验收：** 每个 pilot 方法有可复现入口和版本，正式 kBET 的实现与版本已知，才通过 G2；否则继续 preflight-only。

## Task 3：统一输入与 HEART pilot

1. 仅选择 DCS 实际存在且有 CM/FB 标签的 2--3 个 HEART 物种；首轮优先近缘组合。物种名、细胞数、标签数和排除规则写入 manifest，禁止凭空填写。
2. 固定相同 QC、细胞子集、count layer、物种/批次标签和论文注释；限制到一对一同源基因；HVG 只在训练折拟合；pilot 使用邻居数 15、seed 17。
3. 用 input_contract.py 和 ortholog_contract.py 检查 SHA-256、物种对顺序、一对一映射和行数；真实路径只在运行时使用，不提交到 Git。
4. SATURN、SAMap、scVI 分开运行，连续保存日志。OOM/超时只有在 failure_reason.txt 和部分资源记录齐全时才算可审计失败。
5. 每个运行目录必须有 input_manifest.tsv、ortholog_manifest.json、parameters.json、package_versions.txt、stdout_stderr.log、metrics.json、resource_usage.json；失败时再有 failure_reason.txt。

**验收：** 三种方法都完成到嵌入/映射/指标导出，或各自有可复现失败和修复方案，才通过 G4 pilot；单次 pilot 不给工具排名。

## Task 4：正式评测

1. 至少构造一个近缘、一个远缘和一个不同类别混合的 HEART 组合；初期保持 CM/FB。8 物种仅在 3 物种稳定且批准预算后加入，16 物种是可选扩展。
2. 对每个场景做留一物种标签转移：训练/整合不含被留出的物种，再向该物种转移标签；按折和聚合值报告 macro-F1。
3. 使用 seeds 7、17、27；报告均值、标准差和所有失败折，失败不得填 0 或插值。
4. 计算 macro-F1、正式 kBET、iLISI、细胞类型 silhouette、物种/批次混合诊断、墙钟时间、峰值内存、GPU/CPU 和实际成本。kBET rejection 越低、iLISI 和标签 silhouette 越高通常越好；物种分离是过度混合诊断，不能单独优化。
5. 用 run_artifacts.py 和 result_contract.py 验证；最终指标禁止 chi2_neighborhood_proxy，该代理只能用于本地 smoke。

**验收：** 每个结果都能映射到 run 目录、输入 manifest、参数、版本和资源记录；缺少证据的场景报告为 unavailable/failed，不得静默删除。

## Task 5：LBSPA 单核后置补充

HEART 单细胞指标、失败和资源记录经组内复核并形成短结论后，才激活本任务。选择有一对一同源基因和可比标签的七鳃鳗--小鼠 snRNA 小子集，沿用 artifact schema 和留一物种思路，但单独报告 snRNA，明确核/细胞测量差异和跨门类同源基因稀疏性。空间数据仍排除，snRNA 不改写主 scRNA 排名。

## Task 6：算力、预算和失败处理

- 默认 4090x1；pilot 预留 30 分钟，但硬停止 25 分钟、峰值内存 75 GB、单次 ¥10，任务结束立即停止实例。
- 正式运行预留 60 分钟要记录账号分配和预期负载；120 分钟或 4090x2 必须有新证据和明确批准，不能因为四账号名义 ¥400 就自动启用。
- 每次受控台账记录脱敏账号别名、run ID、profile、预留/实际分钟、实际成本、峰值内存、停止原因和 artifact 路径；真实账号信息留在 Git 外。
- OOM/超时先减少细胞数、物种数或做更小 pilot；只有单卡失败包含峰值内存且确认不能缩小输入时，才讨论双卡例外。

## Task 7：报告与 Word 交付

1. 只把真实 artifact 支持的内容写入 docs/report-template.md；主报告纳入数据范围、方法、公平性、pilot、近/远/混合结果、资源、易用性、局限、选型指南和结论。
2. SATURN、SAMap、scVI 的 Agent 友好度只在有本地证据路径和验证说明时评分；六个维度为文档清晰度、CLI/API、参数透明、机器可读输出、失败诊断和环境复现，pending 不是 0。
3. 运行 python scripts/build_report_template.py 生成 templates/course5-final-report-template.docx，逐页检查表格、图题、分页、字体、图像、参考文献和页码；不要把示例数值当成真实结果。
4. 由未负责汇总的组员逐项核对 Word 与 metrics.json/resource_usage.json，并把复核日期记入 docs/ai-use-log.tsv。

**验收：** 最终交付是 .docx；Markdown/JSON 是可追溯源文件；每个结果都有证据路径。

## Task 8：checkpoint、协作和提交

每个阶段结束写：

    已完成：列出阶段和证据文件
    当前门：G0/G1/G2/G3/G4/G5
    仍阻塞：逐项写缺失证据或审批
    没有做：实例、上传、安装、任务提交等未授权动作
    下一步：一个最小可执行动作

组员可柔性分工为：A 数据与生物学（路径、字段、物种、标签和同源基因）；B 环境与算力（镜像入口、GPU、版本、预算和停止）；C 评测与报告（指标、artifact、可视化和 Word）。主线可轮换，每人至少复核另一条线的一项交付，不要把姓名和硬边界写死。

提交前执行：

    git diff --check
    git status --short
    git diff --stat
    rg -n -i "password|passwd|secret|api[_-]?key|token|cookie|authorization:|bearer " --glob '!smoke-output/**' --glob '!runtime-output/**' .
    python -m unittest discover -s tests -q

扫描命中规则说明时要人工确认没有真实凭据。计划文档使用 docs: add Luna execution plan；证据更新使用 docs: record DCS inventory evidence。每个阶段一个逻辑提交并推送短分支。

## 失败决策表

| 情况 | 应做 | 禁止 |
|---|---|---|
| DCS 搜索 0 条 | 记录范围、查共享入口、汇总具体问题 | 猜路径或把 accession 当路径 |
| 页面有包但无入口 | 实例内只读 import/which/version | 直接安装并称已验证 |
| SAMap 两个版本 | 记录冲突，采用实例实际版本 | 任意挑版本 |
| 本地缺包 | 保持 smoke 环境轻量 | 污染本地环境 |
| pilot OOM/超时 | 保存失败 artifact，缩小输入 | 立刻开双卡或延时 |
| kBET 只有代理 | 只用于 smoke，正式阶段阻塞 | 写入最终结果 |
| 余额/账号规则不清 | 停止云动作，更新问题清单 | 假设余额可合并 |

## 完成定义

只有在真实数据和授权入口有证据、三种方法 pilot/正式场景均有 artifact、正式 kBET 与版本已记录、近缘/远缘/混合结果按留一物种和三个种子报告、snRNA（如执行）与主实验分开、成本/资源/失败原因齐全、Word 逐页校验且与机器可读结果一致时，课题5才可称为完成。仅完成本地 smoke test 或写完计划，不等于完成。
