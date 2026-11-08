# 课题5 三档后续实验方案 v2（提交审批用，2026-10-09）

> 状态：**方案稿，未运行**。B/C 档涉及付费资源，须经用户明确批准后另行提交；A 档为本地/免费。
> 纪律：不自动重试、不反复轮询；任一档出现 Pending/502/OOM 反复即停止该分支并记录。
> 老师口径：**单细胞优先**（平台数据已确认含 `cell_or_nuclei` 字段，可精确筛选）；单核等主要结论出来后做小规模测试；**空间数据不进主评估**。
> v2 修订（依据 Claude 反方审阅，2026-10-09）：档名与 GenPilot 对齐（GenPilot 的"A/B"= 本方案的 A/C2）；费用算术改正；泄漏清单扩至 8 项；SAMap 增"近似 inductive"闸门；补 seed 预注册与 inductive 负控。

## 档名对照（两套材料统一）

| 本方案 | GenPilot 会商用名 | 内容 |
|---|---|---|
| 档 A | A 档 | 本地复算/负控/证据整理（零训练、零费用） |
| 档 B | （会商未单列） | 现有三物种单细胞子集小规模同批对照（transductive） |
| 档 C1 | （会商含在 B 的前置） | 投影接口与隔离证明（先证明再花钱） |
| 档 C2 | B 档（81 格） | 留一物种 × 3 方法 × 3 seed × 三层 = 81 格（inductive/近似） |

---

## 档 A：本地复算、负控与证据整理（无新增训练，**0 元**）

| 项 | 内容 |
|---|---|
| 输入 | 已有冻结产物：ortholog-pca-v98/metrics.json + predictions/ + confusion/；saturn-v99 恢复载荷；samap-v98 WDL 产物；config/heart-celltype-map-v1.tsv |
| 协议标签 | `local-recompute; transductive; no-training; no-platform-cost` |
| 预期产物 | ① 逐方向三方法完整对照表（已产出：docs/evidence/per-direction-three-method-20261009.md）；② 负控矩阵：多数类基线 / 置换零分布（E[null]）/ 标签打乱 / 特征打乱；③ 分母敏感性表；④ 逐细胞预测一致性核对（**显式排除 v97g**——其无逐细胞/confusion，只有日志级） |
| smoke | 每项复算先跑 1 个方向验证与 metrics 一致（exit 0），再全量 |
| 资源/费用 | 本地 CPU，**0 元**（不占用平台容器） |
| 失败停止条件 | 任何复算与冻结 metrics 不一致 → 停止并报差异（不覆盖原结果） |
| 能支持的结论 | 数字可复核性、分母/协议敏感性；**不能**支持泛化；复算数字不得混入"新实验"叙述 |

## 档 B：现有三物种单细胞子集小规模同批对照（transductive；本地为主，≤1 元）

| 项 | 内容 |
|---|---|
| 输入 | 平台三份 h5ad（human id=6ff9e0733a2b4b409afa49b29daad0fa；mouse id=2d1e6596a67344878ae7f4e5ecd65d8a；zebrafish id=2092aee8750247cf8389a4233734d5c3）；筛选 `cell_or_nuclei == 'cell'` |
| 协议标签 | `same-batch comparability; transductive; single-cell-only`（标签可见性按各方法实际机制声明：oPCA label-free；SATURN label-aware 经 labels 通道、**运行时版本待核实**；SAMap label-aware 经 keys=cell_type、**线上脚本内容待回捞**） |
| 设计要点 | ① 三方法在同一次筛选后的同批细胞上重跑评分；② 显式声明训练期标签通道；③ 统一报告 n_q、coverage、majority、shuffle_p |
| 预期产物 | 单细胞子集六方向三方法表 + 与全量（cell+nuclei 混合）对照的差异表 |
| smoke | 1 方向 × 1 方法跑通（与本地一致）后再扩全量 |
| 资源/费用 | 本地 CPU（oPCA/v99 复算）；SAMap 如需平台重跑：1 次 WDL（1c4g，约 16 分钟）≈ 0.18 元（实证值，非官方单价） |
| 费用上限 | **≤1 元**（WDL 单次；失败不自动重投） |
| 失败停止条件 | WDL 连续 2 次失败 → 停止该通道分支，保留本地部分 |
| 警示 | 单细胞筛选会改变 n（1528/1535/1543 为混合口径）→ 同时改变 majority 与 acc，**不得解读为方法性能升降**；须并列 n_q/coverage/majority |
| 能支持的结论 | "主要结论是否由单核/混合组成驱动"；**不能**支持泛化（仍 transductive） |
| 依赖 | 档 A 完成；用户批准 WDL 单次费用 |

## 档 C1：投影接口与隔离证明（先证明，再花钱；本地+容器验证，费用 ≤5 元）

| 项 | 内容 |
|---|---|
| 目的 | 在花 GPU 钱之前，逐方法证明"冻结表示后仅投影"可执行且无泄漏 |
| 逐方法要求 | **oPCA**：✅ 固定 PCA 载荷 `transform`（可本地验证）；**SATURN**：❌ **源码级判定为阻塞**（见下）；**SAMap**：❌ 无原生冻结图投影，只能"冻结同源图 + ref 锚点 KNN"**近似**——产物必须命名 **SAMap-approx（近似 inductive）**，并附**硬闸门**：证明冻结图由 ref-only 构建、held-out 物种表达未进入图的任何构建步骤（附 membership 清单） |

### SATURN 未见物种可行性（源码级，2026-10-09 补；结论：**阻塞**）

依据（wheelhouse/saturn-src 源码实读）：
1. **每物种基因块**：`species_to_gene_idx_hv[species] = (ct, ct+n)`，块按物种拼接（train-saturn.py:520-533）；`forward` 里 `filler_idx = self.species_to_gene_idx[species]`（model/saturn_model.py:106）→ **未见物种直接 KeyError**。
2. **基因块的基因集来自该物种自身表达**：`sc.pp.highly_variable_genes(adata, ...)` 逐物种在自己的 adata 上选 HVG（train-saturn.py:527-531）→ 若照搬此路径给 held-out 物种建块，即**用其表达定义特征空间（泄漏）**；替代方案（用冻结词典/训练物种基因空间映射）在现有代码中**未实现**。
3. **物种 one-hot 宽度烧进权重形状**：`num_species = len(species_to_gene_idx)` 用于 `torch.zeros(batch_size, self.num_species)`（L135/L458）与首层输入维 `embed_dim + num_species + num_batch_labels`（L75）→ 新增物种会改变权重形状，**冻结权重不兼容**；代码中未见预留物种槽机制。
4. `p_weights`（基因→macrogene 权重）按 `num_genes = max(v[1])` 定形状（L48-50）→ 新物种块需配套 macrogene 指派，现有代码无冻结指派路径。

**判定**：`model.eval() + no_grad()` **不足以**证明未见第三物种可直接投影；当前代码不支持"冻结 SATURN + 新物种"的合法投影。
→ **C1-SATURN 阻塞**；C2 中 SATURN 格一并阻塞。若需 SATURN 参与 inductive，必须重训或改模型定义（= 新训练，不再是"冻结投影"，需单独立项与预算）。
→ **可先行子集**：oPCA（真投影）+ SAMap-approx（带闸门）的 LOO；SATURN 列为"待重训方案"。
| 硬闸门（任一不过 → 不得进入 C2） | ① oPCA 载荷冻结证明；② **SATURN：源码级已判阻塞**（除非证明存在预留物种槽/冻结指派路径，或接受"重训方案"立项）；③ SAMap-approx 的 ref-only 图 membership 证明；④ 泄漏清单 8 项逐项核验（见下） |
| 泄漏防护清单（8 项，逐项写"平台机制 / 自保证 + 可核查产物"） | 1. **基因集选择**：不得用 held-out 物种的基因存在性（当前 local_v1 用了 query 基因存在性 → inductive 版须改为 ref+词典）；2. **HVG 选择范围**：须 ref-only（SATURN hv_genes=8000 的选取范围无留档 → 不可查）；3. **归一化/PCA 统计量**：仅 ref 统计量（当前 local_v1 在 ref+query 联合矩阵上拟合 → 转导本质，inductive 版须 ref-only）；4. **batch/供体/模态列**：硬断言不使用（当前脚本未用，但无 profile 断言）；5. **供体级隔离**（非仅条码前缀）：防同一供体细胞跨 ref/query；6. **held-out 标签物理剥离**：投影前从 anndata 移除 held-out 物种标签（SATURN 产物把 query ref_labels 与嵌入同文件并列）；7. **嵌入不可跨折复用、seed 不得择优**：预注册"逐 seed 全报 + mean±sd"；8. **inductive 负控**：每折至少"标签打乱零分布"与"特征打乱"对照 |
| 资源/费用 | 本地 CPU + 容器只读验证；如产生容器时长 ≤5 元（待批准） |
| 失败停止条件 | 任一硬闸门不过 → 停止 C2 设计，输出"近似不可行/需另立方法"结论 |

## 档 C2：留一物种泛化（81 格；需 GPU 预算，单独审批）

| 项 | 内容 |
|---|---|
| 输入 | 同档 B 的单细胞子集；冻结映射表 v1（或签认后的 v2） |
| 协议标签 | `out-of-sample projection; leave-one-species-out; 跨物种级（非跨供体级）`；SAMap 格命名 **SAMap-approx** |
| 设计 | 留一物种 × 3 方法 × 3 seed × 三层 = 81 格；**其中 SATURN 27 格因 C1 源码级阻塞当前不可行**（见 C1 判定）；seed 聚合规则**预注册**（全报 + mean±sd，禁最大择优） |
| 预期产物 | **当前可行子集最多 54 格**（oPCA 27 + SAMap-approx 27）；**完整 81 格须待 SATURN 另立方案并过 C1 闸门**。子集可在批准后先行；**SATURN 方案未立项前，完整 C2 不得启动**。附与 transductive 成对差值表（差值须同时标注协议差异与引擎近似差异，不得写成纯泛化能力度量） |
| smoke | C1 硬闸门未过 → 不得进入 |
| 资源/费用（次数重算，2026-10-09 二次修正） | 81 评分格 = 3 折 × 3 方法 × 3 seed × 3 层；**运行次数 = 每方法 9 次**（3 折 × 3 seed；单次表示可评三层——v98 SAMap 单任务即产出 exact/coarse/fine 18 格，v99/oPCA 同理）：<br>• oPCA：9 次拟合，本地 CPU，**0 元**<br>• SAMap：**9 次建图** × ~16 分钟 ≈ 148 分钟 ≈ **1.6 元**（按 1c4Gi 0.011 元/分钟实证值；**待澄清估算**，LOO 单次时长未实测）<br>• SATURN：9 次训练，GPU（**C1 已判阻塞**；若走重训方案，单次时长与单价均待澄清）<br>（此前"27 次 × 16 min ≈ 4.75 元"系按"每层重跑"计；现有证据不支持逐层重跑——v98 单次任务产出三层 → 以 9 次为准） |
| 费用上限 | 单次 GPU ≤ ¥50 保险丝（**在单价未核实前不构成有效保险丝**）；**总额上限须在运行申请单中列明并经批准** |
| 失败停止条件 | 任一次失败 → 停止 → 分析 → 批准后重试；泄漏核验任一不过 → 停止 |
| 能支持的结论 | 跨物种级 LOO 泛化（若通过）；**须注明"跨物种级，非跨供体级"**（物种为留出单位会高估现实泛化）；SAMap 为近似口径 |
| 硬前置 | ① 档 A/B 完成；② **mapping v1 人工签认**（不是"依赖"，是硬前置）；③ 通道可用；④ **用户与导师批准预算** |

---

## 费用与审批

- 已花费（平台实查，2026-10-09）：WDL 系列 **1.13 元**（完成 1 条 0.18 + 失败 9 条 0.95；此前材料写"约 1.3 元"系估算，以 1.13 为准）。
- 0.011 元/分钟·1c4Gi 反推的**适用边界**：仅 1c4Gi WDL/w-类在线任务、单数据点（16m24s=0.18 元）、含计费取整误差；跨 CPU 档、GPU 档、交互容器时长、存储/idle 计费**均不可线性外推**。
- 待审批付费项（各一单，须用户明确批准）：
  1. **审批单 B-1**：SAMap WDL 单细胞子集重跑（1c4g，≤1 元）。
  2. **审批单 C1-1**：投影接口验证容器时长（≤5 元）。
  3. **审批单 C2-1**：inductive 81 格（oPCA 9 次本地 0 元 + SAMap 9 次 ≈1.6 元 + SATURN 9 次 GPU——**SATURN 因 C1 源码级阻塞，须先决定"重训方案"是否立项**；总额上限待申请时列明）。
- 未列入审批：空间数据实验（不进主评估）；扩物种（无当前需求）。

## 与老师口径的对应

- "单细胞优先"：档 B 显式筛选 `cell_or_nuclei == 'cell'`；单核仅作后续小规模对照。
- "主要结论出来后小规模测试"：档 B 排在档 A 之后、档 C 之前。
- "空间数据不进主评估"：本方案不含空间数据。
