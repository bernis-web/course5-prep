# 课题5下一轮执行交接

面向对象：zcode / Claude / GLM 等接手 agent，以及四名团队成员。本文件只写“下一轮怎么干”，背景长文不重复：证据见 `docs/dcs-readonly-audit.md`，分工原则见 `docs/team-task-division.md`，本地命令见 `docs/minimal-verification-runbook.md`，协作与计费规则见 `docs/dcs-team-collaboration.md`。

## 0. 当前 checkpoint（2026-09-18）

| 阶段门 | 状态 | 缺口 |
| --- | --- | --- |
| G0 本地基线 | 核心通过 / 材料已补齐 | 2026-09-17 本轮 50 个测试及 smoke、计划契约、结果契约、artifact contract、Word 模板重建通过；2026-09-18 找回缺失的 `course-web(1).html` 与心脏论文 PDF（回收站原件与微信目录均未破坏），`source_manifest_check.py` 三份大小/SHA-256 全部匹配（3/3，退出码 0）；材料存放于仓库外目录，路径不入库，原件不提交 Git |
| G1 DCS 数据路径/字段/物种/授权 | 部分通过 | **2026-09-20 老师回复后突破**：课程共享项目已找到——`BGI-时空` 入口下"康复大学生信实践"（P20260920085640327，09-20 建，57 人，账号1=分析人员），授权半边核实完成；但项目数据区为空（仅 4 目录骨架），公共库数据 28 条均为平台通用资源，**课程数据尚未挂载**；老师另给 HEART/LBSPA 两个 STOmics 门户 URL（官方公共发布处）。数据进项目方式（老师上传 vs 组员从门户下载上传）待确认，`heart_data_path` 等字段维持 pending |
| G2 候选镜像 | 部分完成 | `SATURN--22`/`SATURN--21`、`samap_all`、`BENGAL--SAMap--17`、`scvi_zt` 等页面已发现；实例内入口、真实版本、GPU、正式 kBET 全部 `pending` |
| G3 启动许可 | 未通过 | `config/startup-preflight.json` 的 `approval_status` 仍为 `pending`，HEART 数据字段全空；预检已按阶段校验（默认 `heart_pilot` 不要求 `lbspa_snRNA_path`；`lbspa_followup` 另要求该路径与 `evidence.scrna_conclusion`），阶段化门本身不再阻塞 HEART |
| HEART pilot | 未开始 | 等 G1+G2+G3 |
| 正式评测 | 未开始 | 等 HEART pilot 闭环 |
| LBSPA 单核补充 | 未开始 | 等单细胞基本结论（`config/benchmark-plan.json` 的 activation_gate） |

### 2026-09-18 本地复核记录

- `python -m unittest discover -s tests -v`：54/54 通过（2026-09-18 测试加固新增 4 项后接手 agent 当次复跑；同日早间基线为 50/50）。
- `python scripts/smoke_test.py --outdir smoke-output`：合成 smoke 产物已生成；仅用于验证产物契约，不代表真实工具结果。
- `python scripts/plan_contract.py`、`python scripts/team_budget_check.py`：通过；仍保持 preflight-only 和分账号预算假设。
- `python scripts/startup_preflight.py --phase heart_pilot`：报告 `ready_for_execution: false`，阻塞项仍是课程数据路径/字段、镜像实际版本与入口、正式 kBET、审批等外部证据。
- 本次没有创建 DCS 实例、启动云任务、上传/下载数据、安装 DCS 包或写入凭据；`smoke-output/` 为本地忽略目录，不纳入 Git。
- 课程材料找回（2026-09-18 接手 agent 复核）：`course-web(1).html` 与心脏论文 PDF 此前被误删入 E 盘回收站（SHA-256 与 `docs/source-file-manifest.tsv` 完全一致后从回收站复制恢复，回收站原件未动）；七鳃鳗论文在微信文件目录原样可用。三份已集中复制到仓库外材料目录并重新核验 3/3 通过。

### 2026-09-18 晚间复核与清单草稿（18:04 非高峰自主推进）

- 模式说明：用户指示非高峰时段自主继续；Codex 编排当次不可用（CC Switch 本地代理 502，上游 127.0.0.1:15721 连接失败，校园网时段），复审改由 Claude 子代理独立审查 + 本人 diff 复读执行。
- `python -m unittest discover -s tests -v`：54/54 通过（当次输出为准）。
- runbook A/B/C 段当次全量重跑：smoke_test、environment_check、dcs_readonly_probe（`scope: runtime_probe`）、environment_contract `--profile SATURN--22`（唯一 unresolved 仍为 SATURN 页面未列入口，属已知 G2 缺口）、input/ortholog 契约、plan_contract、team_budget_check（4090x1/60min/1 run）均通过；budget_check 4090x1 退出码 0、4090x2 按预期以退出码 2 拒绝。
- `startup_preflight.py` 两阶段均 `ready_for_execution: false`：heart_pilot 阻塞项不含 `lbspa_snRNA_path`；lbspa_followup 含 `lbspa_snRNA_path` 与 `evidence.scrna_conclusion`；阻塞项全部为 G1/G2/G3 外部证据字段，无脚本故障。
- `source_manifest_check.py`（材料目录路径按规矩不入库）：3/3 大小/SHA-256 匹配，退出码 0。
- `build_report_template.py` 默认参数重建 Word 模板成功；占位符检查由测试回归覆盖。
- 新增 `docs/startup-shutdown-checklist.md`（工作包 B"启动/停止检查清单"草稿 v0.1）：无标注条目来自 handoff／镜像计划／runbook 既有规则，（建议）标注条目为新增流程建议。v0.1 已按子代理独立复审意见修订：补 handoff §5 第 1–2 项与 runbook D-1 的物种/范围门、补齐（建议）标注（四角色表、批准记录、运行目录骨架、紧急停止细则等）、明确数据仅经已核实共享路径只读访问且探针不读课程数据、证据清单扩至 Python/CUDA/GPU 与 anndata/scanpy/torch、花费按整会话口径、换卡数按新一轮启动处理、异常上报统一为"停下来问用户"。复审结论：零高危（无事实错误、无边界放宽），可作待评审交付物。待四人评审后转正。
- 本轮无云端动作、无登录、无付费、无包安装。

## 1. 现在能做 vs 必须等

现在就能做（不碰云资源、不装包、不付费）：

- 工作包 C 全部（本地评测材料，见下）。
- 找回或重新导出缺失的课程 HTML 与心脏论文 PDF 后，只在本地重跑材料哈希核验；大文件不提交 Git。
- 工作包 A 的四账号只读排查：各组员用自己的已有登录态检查自己的账号；agent 不得代替登录。
- 工作包 B 的页面级复核与"启动/停止检查清单"草稿（清单草稿 v0.1 已于 2026-09-18 晚落至 `docs/startup-shutdown-checklist.md`，经子代理独立复审修订，待四人评审）。
- 团队预算账本核对（`python scripts/team_budget_check.py`，只算账不连 DCS）。

必须等 DCS/老师信息才能做：

- 实例内运行时核验（B 的核心）：等组内批准一次受控启动，或课程方提供免自建实例的安全核验方式。
- HEART pilot 与一切正式评测：等 G1、G2、G3 全过。
- LBSPA 单核补充：等单细胞评测结论落库。

## 2. 三个工作包

### 工作包 A：DCS 成员与数据发现（对应 G1）

- **输入**：`docs/dcs-readonly-audit.md`（单账号两轮排查先例）、`docs/teacher-data-request.md`（第 0–6 项清单）、`docs/dcs-team-collaboration.md`（成员/计费规则）、四名成员各自的 DCS 账号。
- **可执行动作**：
  1. 四个账号依次只读检查：区域（DCS-华北2、DCS-华南1）→ 项目列表（"所有项目/我参与的"）→ 默认项目数据管理（RawData 等文件夹）→ 公共库（公共数据/公共项目）→ 按 `HEART`、`LBSPA`、`CNP0006537`、`CNP0007565`、`lamprey` 检索。
  2. 任何账号看到课程共享项目或数据入口时，只读打开并记录：脱敏项目/数据集标识、文件格式（`.h5ad`/`.rds`/矩阵目录）、物种/细胞类型/批次/金标准标签字段名、可用物种清单、CM/FB 子集可行性、本账号角色（访客跑不了分析）。
  3. 结果按日期追加到 `docs/dcs-readonly-audit.md`；不写账号标识、手机号、cookie、token 或私有路径原文。
  4. DOI 和 CNGB accession 只是公共检索键，绝不能填进 `heart_data_path` 或 `lbspa_snRNA_path`。
- **证据字段**：账号序号（脱敏"账号1–4"）、区域、检查页面、检索词、命中数、命中项目/数据集脱敏标识、格式、字段名、物种、权限角色、检查时间。
- **产物路径**：`docs/dcs-readonly-audit.md`（追加小节）；拿到真实路径证据后才更新 `config/startup-preflight.json`。
- **完成定义**：四个账号都有可复核的检查记录；或课程入口已找到且字段/物种/权限记录完整。
- **停止条件**：需要登录/验证码；需要接受邀请或变更权限；页面要求创建实例/提交任务/复制或上传数据才能看数据；要写入账号标识或敏感路径——停下来问用户。

### 工作包 B：运行时只读核验（对应 G2）

- **输入**：`docs/dcs-image-probe-plan.md`、`config/startup-preflight.json` 的 `page_level_image_candidates`、`scripts/dcs_readonly_probe.py`。
- **前提**：只在两种情况之一满足后记录实例内证据：(a) 组内明确批准一次受控启动用于核验；(b) 课程方提供无需自建实例的安全核验方式。两者都没有时，本包只做页面级复核，不启动任何实例。
- **可执行动作**：进入候选镜像实例后，用与本机同一条命令保存实例内证据：`python scripts/dcs_readonly_probe.py --output <运行目录>/dcs-readonly-probe.json`；本地再用 `python scripts/environment_contract.py <报告.json> --profile SATURN--22` 对齐检查。记录：Python 版本、CUDA/GPU（`nvidia-smi`）、SATURN 的 import/CLI 入口、SAMap 版本（`BENGAL--SAMap--17` 页面双版本歧义必须在实例内消解）、scvi-tools、`anndata`/`scanpy`/`torch`、正式 kBET 的实现名和版本。
- **证据字段**：镜像名、实例内 Python/CUDA/GPU 型号、每个工具的 import 结果+版本+入口命令、kBET 实现名+版本、采集时间、`scope: runtime_probe`。页面软件清单不能代替实例内证据。
- **产物路径**：`config/startup-preflight.json` 的 `image_recommendation`、`image_versions`、`kbet_implementation`、`kbet_version`、`readonly_sample_command`；探针 JSON 存运行目录。
- **完成定义**：SATURN/SAMap/scVI 三者的实例内版本与入口都有非页面证据；正式 kBET 实现与版本落库。
- **停止条件**：需要付费或超出既定预算；需要安装 DCS 包；需要上传/复制数据；实例内环境与页面声明不符且需要改环境——停下来问用户。

### 工作包 C：本地评测材料（不需要真实数据）

- **输入**：`config/benchmark-plan.json`、`tests/`、`scripts/`、`docs/report-delivery.md`。
- **可执行动作**：按 `docs/minimal-verification-runbook.md` A 段复现本地检查；复核输入契约（`input_contract.py`）与同源基因契约（`ortholog_contract.py`，一对一同源、物种对顺序规范化）；确认留一物种标签转移、seeds 7/17/27、macro-F1、kBET/iLISI/silhouette 定义；核对运行时间/内存/GPU/成本记录字段与 artifact 命名（`run_artifacts.py` 检查项）；用 `build_report_template.py` 重建 Word 模板并检查占位符未被填入合成结果。课程材料恢复后运行 `source_manifest_check.py`，只记录 3/3 哈希结果，不提交论文或 HTML 原件。
- **证据字段**：命令退出码、输出 JSON 路径、复核人、日期；测试数量以当次输出为准，不沿用历史数字。
- **产物路径**：`smoke-output/` 下各报告、`config/benchmark-plan.json` 维护记录、`templates/course5-final-report-template.docx`。
- **完成定义**：A/B/C 三名主责成员各自本地复现 A 段全部通过，D 至少抽查一份输出；课程材料哈希核验恢复为 3/3；真实数据的指标/资源记录表骨架就绪。
- **停止条件**：本包无云端风险；若复核中发现字段或物种选择会改变实验设计，停下来问用户。

## 3. 四人柔性认领与交叉复核

A/B/C 只是主责线，不是文件所有权，也不绑定姓名（组内把 A/B/C 对应到实际人员即可，可轮换）：

| 主责线 | 至少交叉复核另一线的一项 |
| --- | --- |
| A 数据与生物学 | 复核 B 的路径可读性与内存假设 |
| B 环境与算力 | 复核 C 的版本/时间/内存/成本记录 |
| C 评测与报告 | 复核 A 的标签转移与金标准定义 |

D 成员首轮不绑主线，至少交叉复核一条线的一项；后续可与 A/B/C 轮换。认领方式沿用 `docs/team-task-division.md` 的认领表；启动前四名成员共同确认（见第 5 节启动门）。

## 4. 停止并询问用户的条件

出现以下任一情况，立即停止当前动作并向用户报告，不得自行继续：

1. 需要登录、输入验证码或以任何方式访问凭据/登录态。
2. 需要接受项目邀请或变更任何权限。
3. 需要创建实例、提交任务、复制或上传数据。
4. 任何付费动作。
5. 需要在 DCS 实例上安装包。
6. 需要超出既定预算（单次默认上限 ¥10；团队扩展须先核算并单独批准）。
7. 发现字段或物种选择会改变实验设计。
8. 需要把账号标识或敏感路径写入仓库或日志。

## 5. HEART pilot 启动门（全部满足才启动）

阶段化预检已于 2026-09-17 落实：`startup_preflight.py` 与 `local_readiness.py` 均支持 `--phase heart_pilot`（默认）与 `--phase lbspa_followup`，未知阶段以 `PreflightError`/退出码 2 拒绝。`heart_pilot` 不再要求 `lbspa_snRNA_path`，但保留 HEART 的审批、数据、字段、镜像、kBET 与证据检查；`lbspa_followup` 在此之上另要求 `lbspa_snRNA_path` 与 `evidence.scrna_conclusion`（配置中该证据初始为空）。`benchmark-plan.json` 的 LBSPA 激活门（`scRNA_benchmark_conclusion_recorded`）保持不变；在真实结论落库前，不得为了让脚本变绿而填写虚假路径或伪造结论。

- [ ] 物种 2–3 个、scRNA、优先 CM/FB，论文标注为金标准。
- [ ] 空间数据排除在外；LBSPA 单核后置。
- [ ] 数据路径、字段、物种清单已核实（G1 通过）。
- [ ] 实例内运行时与正式 kBET 实现已核实（G2 通过）。
- [ ] 预算已确认：默认 25 分钟硬停止、峰值内存 75 GB、单次 ¥10 任一达到即由指名负责人手动停机；采用团队预算扩展的运行单独写明批准的时长/成本。
- [ ] 本次运行负责停止实例的人已指名；不能把平台预算设置当作自动停机保证。
- [ ] `python scripts/startup_preflight.py` 返回 `ready_for_execution: true`。
- [ ] 四名成员明确批准。

## 6. 老师跟进消息（2026-09-18 已发送；**2026-09-20 已收到回复**）

原触发条件为"四个账号都完成工作包 A 检查仍无入口"。2026-09-18 用户决定以账号1 的三轮全零证据直接跟进，不再阻塞等待账号2–4（决定记录见 `docs/dcs-readonly-audit.md` 2026-09-18 小节）。跟进消息已由用户本人通过微信发送，内容如下；此类消息只能由用户本人发送，agent 不得代发。2026-09-13 已发过一条详细消息（见 `docs/teacher-data-request.md`）。

~~~text
老师好！打扰您了，想跟进一下课题5的数据入口：这几天我在 DCS 上翻了好几遍——华北2、华南1 两个区域的项目列表、公共数据、公共项目都看了，HEART、LBSPA 还有论文里的数据编号也都搜了，一直没找到课程共享项目或者数据在哪。想麻烦老师指个路：方便的话把我们几个的账号加进共享项目，或者直接告诉我数据在哪个项目/目录下就行。找到之后我们先只做只读检查（数数细胞数、基因数，看看字段），保证不复制、不上传原始数据。谢谢老师！
~~~

**2026-09-20 老师回复**（微信，两句话）：`https://db.genomics.cn/stomics/heart/`、`https://db.cngb.org/stomics/lbspa/` 两个网址 + "已经拉进项目里了"。

**回复处理结果**（2026-09-20 ZCode 只读复查，证据见 `docs/dcs-readonly-audit.md` 账号1 第四轮小节）：
- 课程项目已找到：`BGI-时空` 入口"康复大学生信实践"（P20260920085640327，09-20 创建，57 名成员，账号1 角色=分析人员，费用 ¥0/无限制）。前几轮排查卡未覆盖 `BGI-时空` 第三入口，是三轮 0 命中的原因。
- 项目数据区目前为空（4 目录骨架、存储 0GB）；项目公共库数据 28 条全为平台通用资源。课程数据尚未挂载。
- 两个 STOmics 门户是 HEART（DOI 10.1126/science.adw0855，scRNA 15 物种）与 LBSPA（DOI 10.1126/science.aea2535）的官方公共数据发布处，与两篇论文的 Data Availability 一致。
- **待用户决策**：数据进项目的方式——(a) 问老师是否统一上传到项目 RawData（推荐，57 人共享一份、版本一致）；(b) 组员自行从门户 Download 页下载数据后上传项目（涉及上传边界动作，须用户明示批准并先确认选哪些物种子集）。在此之前 G1 数据字段维持 pending。

## 7. zcode / Claude 下一次接手时的首条任务提示词

2026-09-17 本机核验：`zcode` 尚未在当前 PATH 中找到，不要擅自安装；Claude Code 显式使用 `--model glm-5.3` 可完成小块任务。当前智谱路由下 `--model sonnet` 的返回元数据仍是 `canonicalModel: glm-5.3`，所以文档中不得称其为真正的 Anthropic Sonnet。GLM-5.3-Flash 若长时间无返回，应停止该次调用并把任务拆小后改用 GLM-5.3。

~~~text
你是课题5仓库 D:\projects\course5-prep 的下一轮执行 agent。本轮只做只读检查并报告，不启动任何云资源：
1. 读 README.md、docs/next-round-handoff.md、docs/dcs-readonly-audit.md、config/startup-preflight.json。
2. 运行 python -m unittest discover -s tests -v 和 python scripts/startup_preflight.py（不带参数即读默认 config/startup-preflight.json；blocked/pending 是预期结果，不是脚本故障）。
3. 报告五件事：G0–G3 各门当前状态；startup preflight 的 blocking_items 列表（默认 `heart_pilot` 阶段下 `lbspa_snRNA_path` 不应出现在其中）；`--phase lbspa_followup` 下额外阻塞项（`lbspa_snRNA_path`、`evidence.scrna_conclusion`）是否保持；docs/dcs-readonly-audit.md 中四个账号各自是否已有检查记录；工作包 A/B/C 各自的下一步。
4. 边界：不访问凭据或登录态，不创建/启动 DCS 实例或任务，不安装包，不付费，不提交或推送；遇到登录、邀请、权限、付费、或字段/物种选择会改变实验设计的情况，停下来问用户。
~~~

## 8. 已核验的 startup preflight 命令

2026-09-17 已对照 `scripts/startup_preflight.py` 的 argparse 源码核验：该脚本有两个可选参数——`--preflight`（默认读 `config/startup-preflight.json`）和 `--phase`（默认 `heart_pilot`，可选 `lbspa_followup`；未知阶段会被 `PreflightError` 以退出码 2 拒绝）。

```powershell
Set-Location D:\projects\course5-prep
python scripts/startup_preflight.py                                    # 默认配置 + heart_pilot 阶段
python scripts/startup_preflight.py --preflight config/startup-preflight.json   # 等价显式写法
python scripts/startup_preflight.py --phase lbspa_followup            # LBSPA 后置阶段：另检查 lbspa_snRNA_path 与 evidence.scrna_conclusion
```

当前配置下两个阶段都已于 2026-09-17 实测输出 `ready_for_execution: false`：默认 `heart_pilot` 不含 `lbspa_snRNA_path`，`lbspa_followup` 含 `lbspa_snRNA_path` 与 `evidence.scrna_conclusion`。命令退出码 0 只表示记录格式有效，不构成启动许可；测试状态仍以接手者本次亲自执行为准。
