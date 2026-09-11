# 课题5交接文档：给 Luna

更新时间：2026-09-11
仓库：https://github.com/bernis-web/course5-prep
分支：codex/teacher-reply-report-prep
当前交接提交：367de1c docs: add Luna execution plan

这不是一份“从头猜实验”的任务。仓库已经完成了课题范围梳理、预算约束、三人协作约定、运行产物契约和 Word 报告骨架；你要从现有证据继续推进，先完成只读核验，再按阶段解锁真实实验。

## 直接发给 Luna 的消息

~~~text
请接手 GitHub 仓库 https://github.com/bernis-web/course5-prep 的课题5任务，分支为 codex/teacher-reply-report-prep，当前提交为 367de1c。

请先阅读：
1. README.md
2. CONTRIBUTING.md
3. docs/handoff-to-luna.md
4. docs/superpowers/plans/2026-09-11-luna-execution-plan.md
5. docs/handoff-to-teammates.md
6. docs/minimal-verification-runbook.md
7. config/benchmark-plan.json
8. config/startup-preflight.json
9. docs/teacher-data-request.md
10. docs/report-delivery.md

请持续推进，每完成一个可验证的小步骤就继续下一步，不要只回复两句话后停下。第一轮只完成本地基线、DCS 只读数据盘点和候选镜像只读核验，形成 checkpoint。启动门通过前绝不能创建 DCS 实例、提交任务、上传数据、安装包、下载大文件或消费余额。

不要猜测 HEART/LBSPA 的 DCS 路径、文件格式、字段名、物种清单、工具入口、软件版本或正式 kBET 版本。查不到就保持 null/pending，并记录查过的页面、结果和最小待确认问题。论文 DOI/CNGB accession 只能作为检索线索，不能直接当作 DCS 挂载路径。

固定顺序：
1. 运行本地测试、smoke、计划/预算/环境契约检查。
2. 在 DCS 只读确认 HEART 数据、LBSPA snRNA 数据和课程共享入口；空间数据暂不纳入。
3. 在候选运行时只读确认 SATURN、SAMap、scVI、CUDA/GPU 和正式 kBET 的真实入口/版本。
4. 只有 startup_preflight ready、预算通过且组内批准后，才做 HEART 2--3 物种 CM/FB 单细胞 pilot。
5. pilot 通过后，再做近缘、远缘和不同类别混合场景的留一物种评测。
6. 单细胞主结论形成后，才小规模补充 LBSPA 七鳃鳗--小鼠 snRNA。
7. 所有结果先保存 artifact，再写 Markdown/JSON，最后导出 Word。

每个阶段结束都汇报：已完成、证据文件、当前门、仍阻塞、没有做的云端动作、下一步唯一最小动作。只有遇到数据授权、启动门、预算或必须由人批准的操作才暂停。
~~~

## 当前状态

### 已完成并已推送

- 课题5目标明确为跨物种单细胞整合工具评测：SATURN、SAMap、scVI。
- HEART 首轮范围限定为 2--3 个物种，先验证流程闭环。
- 后续再覆盖近缘、远缘和不同类别混合物种。
- 主实验只比较单细胞数据。
- LBSPA 七鳃鳗--小鼠单核只在单细胞结论后做小规模补充。
- 空间数据暂不进入主实验。
- 统一输入、同源基因、HVG、随机种子、留一物种标签转移和运行 artifact 契约已经写入仓库。
- 最终报告格式确定为 Word；Markdown/JSON 作为可审计源文件。
- 四个账号各约 ¥100 的额度已经建模为“分账号规划”，不假定余额可合并。
- 当前候选 GPU 默认是 4090x1；双卡不是默认方案。
- 本地验证证据：47 个单元测试通过，计划契约有效，合成 smoke test 通过。
- 没有创建实例、上传数据、安装云端包、提交任务或消费余额。

### 当前门状态

- G0 本地基线：已通过。
- G1 DCS 数据只读盘点：未通过，课程数据的准确路径、格式、字段和物种还需要页面证据。
- G2 DCS 运行时只读核验：未通过，SATURN/SAMap/scVI 的真实入口、实例版本和正式 kBET 仍需确认。
- G3 启动许可：未通过，config/startup-preflight.json 仍是 approval_status: pending。
- G4 HEART pilot：尚未开始。
- G5 主实验结论和 LBSPA 补充：尚未开始。

## 已确认的论文检索线索

HEART：

- DOI：10.1126/science.adw0855
- CNGB：CNP0006537
- 处理后数据门户：https://db.genomics.cn/stomics/heart/
- 论文涉及 27 个物种；作者 SATURN 分析使用 16 个物种、约 479,483 个细胞。
- 方法线索包括 ESM2B、2,000 个 macrogenes 和 8,000 个 HVGs。

LBSPA：

- DOI：10.1126/science.aea2535
- CNGB：CNP0007565
- 论文包含七鳃鳗脑空间图谱和单核 RNA-seq；高质量单核转录组约 41,678 个。
- 七鳃鳗--小鼠比较涉及约 6,930 个一对一同源基因，并使用 scVI/Harmony 等分析。

注意：这些是论文和公共数据入口线索，不是当前课程 DCS 挂载路径的证明。之前在当前账号可见公共目录中搜索 HEART、LBSPA 及两个 accession 均未命中；下一轮应查课程共享项目/目录，不能重复把 accession 当路径填写。

## 第一轮执行清单

在仓库根目录运行：

~~~powershell
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
~~~

预期：

- 测试、smoke 和计划契约成功。
- DCS 相关 readiness 在外部证据未补齐时可以退出码 2；这表示安全阻塞，不是脚本崩溃。
- 不要为了让本地环境“全绿”而安装 SATURN、SAMap、scVI。
- smoke-output/ 和 runtime-output/ 是本地运行输出，不要提交真实数据或机器特定路径。

## DCS 页面操作边界

DCS 当前需要登录时，由用户在页面完成登录；不要索要、记录或转发密码、验证码、cookie、token。登录完成后再继续只读查询。

只读查询顺序：

1. 当前项目数据和课程/共享项目入口。
2. 数据集/公共数据搜索。
3. HEART 和 LBSPA 的数据记录详情。
4. 候选镜像详情。
5. 镜像内终端或 Jupyter 的只读版本探针。

记录页面位置、查询词、结果数、对象格式、字段名和版本证据；不要复制表达矩阵、打印表达值或把私人挂载路径提交到 Git。若页面显示“有数据”但找不到具体入口，应写成“存在性已知、路径未证实”，然后继续查共享入口或汇总一个具体问题给老师。

候选镜像的当前判断：

- SATURN--22：默认 GPU 候选；页面列出 anndata、scanpy、scvi-tools、fair-esm、faiss-gpu、torch 和 CUDA 组件，但 SATURN 入口仍需实例内确认。
- BENGAL--SAMap--17：页面同时出现两个 SAMap 版本，属于版本冲突，不能任选一个写入结论。
- samap_all：SAMap 候选，但完整版本和入口尚未锁定。
- scvi_zt：更像 CPU 兼容参考，不作为默认 GPU 基准。

## 真实实验解锁条件

在以下证据齐全并获得组内批准前，保持 preflight-only：

- HEART 和 LBSPA 的课程数据入口、格式、字段、授权范围有证据。
- HEART 可用物种清单已知，首轮 2--3 个物种和后续近/远/混合组合可解释。
- 候选运行时已确认 Python、CUDA/GPU、SATURN、SAMap、scVI、依赖和正式 kBET 版本/入口。
- python scripts/startup_preflight.py 返回 ready_for_execution: true。
- python scripts/budget_check.py --profile 4090x1 通过。
- 三人明确批准首轮运行，指定一名非主责成员复核 artifact。

## 实验路线

1. HEART 2--3 物种 pilot：CM/FB 单细胞，只验证读取、预处理、整合/映射、嵌入导出、指标计算和 artifact 写入能否闭环。
2. 正式场景：至少一个近缘、一个远缘、一个不同类别混合组合；初期保持 CM/FB。
3. 评测协议：留一物种标签转移，HVG 只在训练折拟合，固定邻居数 15，正式种子 7/17/27。
4. 指标：macro-F1、正式 kBET、iLISI、细胞类型 silhouette、物种/批次混合诊断、墙钟时间、峰值内存、GPU/CPU 和实际成本。
5. 失败处理：OOM/超时保留日志、失败原因和资源记录，先缩小细胞/物种规模；没有证据时不直接开双卡或延长时长。
6. LBSPA snRNA：HEART 单细胞主结论经复核后才启动，单独报告，不改变主 scRNA 结果表。
7. 报告：真实 artifact -> Markdown/JSON -> Word；smoke 和示例 JSON 不得作为真实结果。

## 预算和停止线

- 默认 4090x1。
- Pilot 预留 30 分钟，硬停止 25 分钟、峰值内存 75 GB 或单次 ¥10，任一达到就停止。
- 正式运行如需 60 分钟，先记录账号分配和成本预算。
- 120 分钟或 4090x2 需要新证据和明确批准。
- 每次运行结束立即停止实例。
- 四个账号各 ¥100 不能直接写成一个 ¥400 账户；实际账本按账号和 run ID 分开记录。

## 三位组员的柔性分工

- A：数据与生物学。查 DCS 数据入口、字段、物种、标签、同源基因和排除规则。
- B：环境与算力。查镜像入口、版本、GPU 可见性、预算、运行时长和停止原因。
- C：评测与报告。维护指标表、artifact 检查、可视化、Agent 友好度和 Word 一致性。
- 分工可轮换；每个人至少复核另一条线的一项交付。主责不是审批人，所有人共同确认启动门。

## 每轮 checkpoint 模板

~~~text
课题5 Luna checkpoint
日期：
当前提交：
当前门：G0 / G1 / G2 / G3 / G4 / G5

已完成：


证据文件：


仍阻塞：


本轮没有做：
- 未创建实例
- 未上传数据
- 未安装 DCS 包
- 未提交任务
- 未记录凭据

下一步唯一动作：

~~~

## 什么时候必须暂停并找人

只在以下情况暂停并明确提问：

- 需要用户在 DCS 页面完成登录或二次验证。
- 数据授权、共享项目入口或私有挂载范围不清。
- 需要创建实例、上传数据、安装包、延长运行、开双卡、充值或改变预算上限。
- 正式 kBET 实现/版本无法确认。
- 发现课程要求与当前计划冲突。
- 结果 artifact 不完整，无法追溯输入、参数、版本、日志、指标或资源。

除此之外，优先继续做本地文档、契约、只读检查、失败诊断和报告骨架，不要等待用户重复发送“继续”。

## 交接完成标准

Luna 接手后，至少应先留下一个 G0/G1/G2 状态 checkpoint。真正完成课题5还必须满足：真实数据入口和授权有证据；三种方法有可追溯 pilot/正式结果；正式 kBET 与版本已记录；近缘/远缘/混合场景按留一物种和三个种子报告；snRNA 与 scRNA 分开；时间、内存、成本和失败原因齐全；Word 报告与机器可读结果一致。

仅复制仓库、跑通 smoke test 或写完计划，不等于课题完成。
