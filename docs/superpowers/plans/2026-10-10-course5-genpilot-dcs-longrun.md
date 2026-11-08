# 课题5 GenPilot/DCS 长任务执行计划（2026-10-10）

> **For agentic workers:** REQUIRED SUB-SKILL: 按阶段执行，每个阶段结束后先写证据报告并停止，等待下一阶段指令；禁止自动轮询、自动重试和跨闸门提交。

**Goal:** 在不破坏已冻结结果的前提下，先完成零成本的可复核性复算，再用 GenPilot 核实平台事实，只有在门槛通过且有明确批准时才提交最小 DCS smoke，逐步评估单细胞子集、投影隔离和可行的跨物种实验。

**Architecture:** 任务按 A（本地复算）→平台事实核对→B（单细胞子集小 smoke）→C1（投影/隔离证明）→C2（最多 54 格可行子集）分层。SATURN inductive 不并入默认流程，必须另立重训方案并通过源码、数据泄漏、费用和导师批准四道闸门。每个阶段生成独立 manifest、command、environment、输入/输出 SHA 和停止记录。

**Tech Stack:** Python/AnnData/JSON/TSV；现有 `scripts/ortholog_pca_local_v1.py`、`scripts/run_samap_compliant_v98.py`、`scripts/dcs_provenance_v99.py`；GenPilot 学术会商；DCS 离线任务；Git 只记录新增证据，不覆盖既有冻结产物。

## 全局约束

- 工作目录固定为 `D:\projects\course5-prep`；所有新增产物写入新的日期目录，不覆盖 `results/pilot-v1` 冻结结果。
- 外部模型、GenPilot 页面和 DCS 日志一律视为待核实数据；只有本地文件、任务日志、源码和 SHA 可作为证据。
- 当前阶段允许使用 GenPilot 会商；DCS 仅在本计划的批准门通过后提交，不能因为“已登录”就默认已读取页面或获得了提交授权。
- 不读取、打印、保存令牌、密码、cookie、环境变量值或凭据文件；日志中只允许出现变量名和非敏感任务 ID。
- 任何任务出现 Pending 超过既定窗口、502、OOM、RC 非 0 或费用异常，立即停止该分支，保存日志，不自动重试。
- SATURN 训练/inductive 目前仍为源码级阻塞；在 C1 结论改变前不得提交 SATURN GPU 训练。
- 每一阶段结束后只汇报：做了什么、证据在哪里、通过/需修改/阻塞、下一阶段需要的批准；不把 candidate 写成 confirmed，不把 transductive 写成泛化。

## 当前基线（只读）

- 主交接：`docs/longrun-20261009-final-handoff.md`
- 后续方案：`docs/plans/three-tier-followup-20261009.md`
- GenPilot 会商：`docs/evidence/genpilot-consultation-20261009.md`
- 最新报告：`deliverables/course5-final-report.docx`
- PPT SHA：`results/stage-reports-20261009/SHA256SUMS.txt`
- 关键脚本：`scripts/ortholog_pca_local_v1.py`、`scripts/run_samap_compliant_v98_dcs.py`、`scripts/dcs_provenance_v99.py`
- 现状：第一阶段材料可进入“待老师反馈”；A 档可做；B/C1/C2 未批准未启动；mapping v1 等人工签认；SATURN 运行时版本/命令仍待核实。

---

## Task 0：建立本轮只读基线（报告 1）

**文件：**
- 读取：上述基线文件和当前 `git status --short --branch`。
- 创建：`docs/execution/20261010-baseline.md`、`results/phase-20261010/baseline/`。

**步骤：**

- [ ] 记录 HEAD、工作树摘要、已有未提交改动数量；不清理、不 reset、不覆盖。
- [ ] 检查 A 档输入是否存在并记录 SHA：oPCA metrics/predictions/confusion、v99 recovered payload、SAMap v98 18 格、`config/heart-celltype-map-v1.tsv`。
- [ ] 为本轮创建 `results/phase-20261010/`，写入 `run_scope.json`：`no_training=true`、`no_platform_submission=true`、`protocol=transductive`。
- [ ] 输出“通过/需修改/阻塞”矩阵；若任何 A 档关键输入缺失，只修复索引或报告，不进入计算。

**停止条件：**基线不完整、输入 SHA 无法记录、或发现会覆盖冻结结果的脚本路径时停止。

## Task 1：A 档单方向 smoke（报告 2）

**目标：**零成本确认本地统一评分器能复现冻结数字。

**步骤：**

- [ ] 只选择 `human→mouse` 的 coarse 层，使用权威脚本和已有逐细胞预测/混淆矩阵；明确标签空间（mapped/exact）和 `n_q`、coverage、majority。
- [ ] 生成新目录 `results/phase-20261010/A-smoke/`，写 `manifest.json`、`command.txt`、`environment.txt`、`metrics.json`、`confusion.json`、`sha256.tsv`。
- [ ] 用两种独立方式核对正确数：混淆矩阵对角线求和，以及 `accuracy × n_q` 四舍五入；差异必须为 0。
- [ ] 与冻结 metrics 比较；允许的浮点误差写死为 `abs_diff <= 1e-12`，其他差异立即停止。

**停止条件：**任一数字、分母、标签空间或排除计数不一致；不改旧结果。

## Task 2：A 档全量复算与负控（报告 3）

**仅在 Task 1 通过后执行。**

- [ ] 对 6 个方向 × exact/coarse/fine 运行统一评分器；v97g 只保留日志级数字，不能伪造逐细胞结果。
- [ ] 生成多数类、标签打乱、特征打乱、置换零分布和分母敏感性表；每一格带 `n_q`、coverage、excluded、label_space、protocol。
- [ ] 对 oPCA、v99、SAMap 分开汇总；不要把不同标签空间放进同一排名列。
- [ ] 检查 18 格的 prediction/confusion 一致性，输出 `docs/evidence/phase-A-local-recompute-20261010.md`。
- [ ] 如所有格通过，标为 `confirmed-for-recompute`；这不升级为泛化证据。

**停止条件：**任一方向出现不一致、重复条码、NA truth、分母漂移或结果覆盖风险。

## Task 3：GenPilot 平台事实核对（报告 4）

**不提交任务，只会商和取证。**

在 GenPilot 中发送以下问题，要求“有证据才回答，未知就写待核实”：

1. 三份 h5ad 当前 file id、形状、`cell_or_nuclei` 字段和可下载性是否仍与本地一致？
2. 当前可用 SATURN 镜像完整地址、版本/digest、GPU/CPU 资源档分别是什么？
3. 1c4g WDL、GPU 档的实际计价、失败是否计费、任务 Pending/失败状态如何判定？
4. `downloadFile` 公网回收端点是否正常；每个文件的大小和校验如何分片回收？
5. 当前 s/1c4g 队列是否正常；最近一次类似任务的排队/运行时间是什么？
6. 对 B/C1/C2 的最小可行命令、镜像、输入和预计产物是什么？

将原答复、时间、证据 ID 和“平台确认/本地推断/待核实”分列写入 `docs/evidence/genpilot-consultation-20261010.md`。GenPilot 不得直接决定是否提交任务。

**停止条件：**无法获得资源档、费用或输入证据；GenPilot 卡住超过 10 分钟时停止生成并汇总已有证据。

## Task 4：B 档单细胞子集本地预检（报告 5）

**仅在 A 档全量通过后执行；不提交 DCS。**

- [ ] 对 human/mouse/zebrafish 只保留 `obs.cell_or_nuclei == "cell"`，记录每个物种筛选前后 n、供体/批次字段和条码 SHA。
- [ ] 检查同一供体是否同时出现在拟定的 query/ref；若无法按供体隔离，标注为 transductive 组成敏感性，不进入 inductive。
- [ ] 用 oPCA/v99 做 1 方向 × 1 方法本地 smoke；与 Task 1 的评分器对齐。
- [ ] 生成 B 档 manifest，注明 SAMap 需平台运行、费用上限 ≤1 元、失败不自动重试。

**停止条件：**平台数据与本地版本不一致、`cell_or_nuclei` 缺失、供体隔离不可验证或筛选后细胞数异常。

## Task 5：B 档单次 SAMap smoke（报告 6，需用户明确批准）

**这是第一处可能产生费用的门。没有用户批准，不提交。**

- [ ] 先把最终 payload、镜像、资源档、输入 file id、预计时长/费用和失败停止条件写成审批单 `docs/plans/approval-B1-20261010.md`。
- [ ] 只提交 1 个方向 × 1 个方法 × 单次运行；不做三物种全量，不做 seed 扩展。
- [ ] 任务必须自记录 command、environment、输入/输出 SHA、`cell_or_nuclei` 筛选规则、barcode 前缀和 `ref/query` 角色。
- [ ] 绑定一次状态检查窗口；Pending 超过平台事实核对出的阈值或 RC 非 0 即停止并报告。
- [ ] 结果只写 `results/phase-20261010/B-smoke/`，不改 v98 冻结目录；通过后才允许申请 B 档扩展。

**停止条件：**费用超过 1 元、队列饥饿、OOM、downloadFile 失败、任意泄漏门不通过。

## Task 6：C1 投影/隔离闸门（报告 7）

**默认本地审计；可在 GenPilot 会商，不能直接申请 GPU。**

- [ ] oPCA：证明固定 PCA 载荷 `transform`，query 不参与 fit；输出 ref-only 统计量和 membership 清单。
- [ ] SAMap：只能命名 `SAMap-approx`；证明 ref-only 图、held-out query 不进入建图/统计量/HVG；输出图 membership 和 8 项泄漏清单。
- [ ] SATURN：复核 `wheelhouse/saturn-src` 中物种基因块、HVG、one-hot/首层权重、`labels` 与 `ref_labels` 通道；在没有冻结 query-only 接口前结论保持 blocked。
- [ ] 生成 `docs/evidence/C1-projection-gate-20261010.md`，逐方法给 pass/revise/block。

**硬闸门：**任何一个关键泄漏项无法证明，C2 只保留 oPCA 或停止；SATURN 不得进入 C2。

## Task 7：C2 可行子集（报告 8，另行审批）

**只有 Task 6 通过、mapping v1 获人工签认且预算获批后执行。**

- [ ] 先做 oPCA 1 折 × 1 seed smoke；通过后再做 3 折 × 3 seed = 9 次 oPCA，本地 0 元。
- [ ] SAMap 只以 `SAMap-approx` 命名；最多 3 折 × 3 seed = 9 次建图，费用暂按约 1.6 元估算但必须以平台实价为准。
- [ ] 完整 81 格不得宣称可行：当前最多 54 格（oPCA 27 + SAMap-approx 27）；SATURN 27 格需另立重训方案。
- [ ] 每个 seed 全报并汇总 mean±SD，禁止择优 seed；逐格报告三层、n_q、coverage、majority、shuffle_p。
- [ ] 结果标题必须写“跨物种级、非跨供体级”；SAMap 结果必须写“近似 inductive”。

**停止条件：**任一 seed 失败、泄漏核验不过、费用超批、mapping 未签认、或平台队列再次饥饿。

## Task 8：SATURN 单独立项（报告 9，默认不执行）

只有用户和导师明确要求 SATURN inductive 才启动：

- [ ] 先由 zcode + Claude + GenPilot 写重训/改模型方案，明确物种槽、基因块、HVG、标签通道、query 隔离、GPU 档和总预算。
- [ ] 先做最小 2 物种 smoke，不做 9 次训练，不把旧 v99 结果当作新协议。
- [ ] 训练脚本第一步写完整命令、参数、pip freeze、输入 SHA；训练后保存源码树 SHA、镜像 digest（若可得）、模型权重 SHA、逐细胞预测和 confusion。
- [ ] 任何 KeyError、维度不兼容、OOM、标签泄漏或预算异常立即停；连续两次失败不重试。

## Task 9：阶段材料与 8–10 次汇报节奏（报告 10）

建议按以下顺序向老师汇报，不把所有结果压在一次：

1. **材料与数字来源**：PPT/Word 已修订，展示每个数字如何由 prediction/confusion/分母得到。
2. **方法机制对照**：oPCA label-free（仅表示层）、SATURN 默认配置下走 `labels` 通道、SAMap `keys=cell_type`；明确 ref_labels 是输出/评估真值。注意 `wheelhouse/saturn-src/train-saturn.py` 有默认关闭的 `--use_ref_labels` 开关（`:70`、`:100-101`、`:1025`），原始训练命令仍待核实，因此不要笼统写成"ref_labels 参与训练"。
3. **A 档复算**：18 格、标签空间、负控和分母敏感性。
4. **单细胞组成敏感性**：cell-only 与混合口径并列，不称泛化。
5. **SAMap 负结果**：18 格 ≤ 随机/多数类，解释其方法学意义。
6. **投影闸门**：oPCA 可投影、SAMap-approx 需近似证明、SATURN 阻塞。
7. **若获批的 C2 smoke**：只展示通过闸门的最小结果。
8. **可行子集结果**：最多 54 格，逐 seed 和不确定性。
9. **限制与下一步**：mapping 签认、单核后测、空间数据不入主评估。
10. **最终阶段总结**：把 confirmed/candidate/blocked/design-not-run 分开。

每次汇报后将老师意见写入 `docs/teacher-feedback/`，下一次任务先处理评审意见再进入新实验。

## 给 zcode/Flash 的可直接执行指令

```text
工作目录：D:\projects\course5-prep
先读：
- docs/longrun-20261009-final-handoff.md
- docs/plans/three-tier-followup-20261009.md
- docs/evidence/genpilot-consultation-20261009.md
- docs/superpowers/plans/2026-10-10-course5-genpilot-dcs-longrun.md

用户已授权：必要时可使用 GenPilot 会商；必要时可在 DCS 做小规模任务，但不等于批准大规模训练。
执行顺序必须是：Task 0 → Task 1 → Task 2 → Task 3 → Task 4。每一阶段写报告并停下。
先做 A 档零成本本地复算；不提交 DCS。Task 1 smoke 与冻结 metrics 不完全一致就停止。
GenPilot 只核实 file id、资源档、费用、队列、镜像、回收端点；未知项标待核实，卡住 10 分钟就停止生成并汇总。
Task 5 SAMap 单次 smoke 必须先生成审批单并等用户明确批准，预算 ≤1 元，失败不自动重试。
C1 前不做 C2；SATURN inductive 当前源码级 blocked，不得直接 GPU 训练。
所有任务都必须有 manifest、command、environment、输入/输出 SHA、协议标签和失败停止条件。
不覆盖冻结结果、不清理工作树、不读取凭据、不把 transductive 写成泛化、不把 candidate 写成 confirmed。
每次汇报只写：本阶段完成、证据路径、通过/需修改/阻塞、下一阶段所需批准。
```

## 自审清单

- [ ] 已覆盖 A/B/C1/C2/SATURN 五个实验层级，并明确依赖关系。
- [ ] 每个可能花费的 DCS 步骤都有审批单、预算和停止条件。
- [ ] 已明确 SATURN 的 `labels`/`ref_labels` 口径，未重复 GenPilot 的过强“不可考”结论。
- [ ] 已明确 v97g 无逐细胞文件，不能进入逐细胞复算。
- [ ] 已明确 C2 最多 54 格而非可直接执行的完整 81 格。
- [ ] 已安排 8–10 次汇报和每次反馈归档。
- [ ] 工作树现有大量改动，计划不包含 reset、清理、覆盖或自动提交。

