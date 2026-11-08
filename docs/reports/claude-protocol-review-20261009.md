# Claude 反方审阅：会商记录 + 三档方案（2026-10-09）

> 审阅人：Claude（只读，未修改任何文件）｜对象：docs/evidence/genpilot-consultation-20261009.md、docs/plans/three-tier-followup-20261009.md｜结论：**revise**（① 为发布前必须就地修正的阻塞项）
> 执行者处理：① 全链修正（6 文件 + Word + 2 册 PPT 重建）；②③④⑤⑥ 逐项落入三档方案 v2 与记录更正。

---

# 课题5 三档后续方案 — 反方方法学审阅（独立复核，只读）

审阅人：Claude（独立方法学）｜日期：2026-10-09｜范围：会商记录 + 三档方案 + 三份参照底表/产物

> 总判断：三档方案的**框架方向正确**（转导与泛化严格分列、A 档零费用先行、C1 先证明再花钱），但存在 **1 处已被项目自身审计否证、却在正式汇报链中仍被当作事实的过度结论**（①），以及 **近似投影 = 泛化的措辞风险**（②）、**对两个关键产物的溯源错配**（③/⑥）。以下逐条。

---

## ① SATURN 标签可见性冲突 —— **阻塞**（针对"ref_labels 参与训练"这一具体断言）

**结论：现有本地证据（输出 h5ad 含 `ref_labels` 列、v99 评估脚本读 `ref_labels`）不能支持"训练时标签参与"，且项目自己的审计文件早在 2026-09-24 就已否证该路径。但被审材料把它当成事实写入对外报告链。**

依据（三条独立证据链）：

1. **该字段是无条件写出的，存在≠使用。** `wheelhouse/saturn-src/train-saturn.py:373-393` 的 `create_output_anndata()` 无条件把 `train_ref` 写入 `adata.obs['ref_labels']`；`train()` 默认 `use_ref_labels=False`（`train-saturn.py:56`），仅在其为真时才把 `ref_labels` 传入 miner（`train-saturn.py:100-103`），默认配置在 `train-saturn.py:1025` 亦为 `False`。因此"输出里有 `ref_labels`"不能推出"训练用了它"。
2. **v99 脚本把 `ref_labels` 当评估真值，不是训练输入。** `scripts/dcs_provenance_v99.py:358-362` 只读取 `obsm["macrogenes"]`（冻结嵌入）并把 `obs["ref_labels"]` 作为 KNN 评分的**真值标签源**（`knn_eval(..., labels, ...)`）。它是**重评分、无重训练**，与"训练期标签参与"无关。
3. **项目早前审计已给出明确结论。** `docs/audit-and-next-round-20260924.md:108-114` 指出：当前 checked-in 源码下 `get_species_triplet_indices()`（`utils/loss_and_miner_utils.py:283-441`）用 **`labels`** 构造正/负样本，`ref_labels` 除默认初始化行外未被读取；`:199`、`:214-215` 再次确认，并明确写"Final AnnData 含有 `ref_labels` 只能证明该字段被输出，不能证明它曾参与 miner"。这与会商结论一致，但**比会商更早**。

**我的独立增量（会商与本地材料都漏的一点）**：`cross_species` miner 虽然不用 `ref_labels`，却用 **`labels`（细胞类型整数 id）** 判定正/负样本（`loss_and_miner_utils.py:283-441`：`torch.where(labels == label)` 取正、`labels != label` 取负）。因此 **"SATURN = label-aware" 在本仓库源码层面是可成立的**，只是**标签通道是 `labels`、不是 `ref_labels`**。所以：
- 会商"SATURN 是否 label-aware 不可考" **过强**（源码层面可考）；
- 本地材料"**ref_labels 参与训练**" **机制写错**（应为"`labels` 参与 cross_species triplet 构造；`ref_labels` 仅为输出/评估真值"）；
- 真正不可核的是 **v71/v99 运行时源码/镜像是否等于 checked-in 版本**（长期未闭合项，见 `docs/audit-completion-matrix-20260926.md`、`docs/dcs-flash-readonly-audit-20260925.md:14`），以及**训练命令行整体缺失**（`results/pilot-v1/saturn-v99/raw/recovered-20261001/manifest.json` 的 `candidate_hashes` 只含 `prep_real_v60.py`/`eval_v72.py`，**无训练命令**）。

**影响面（广）**——以下材料均以"ref_labels 参与训练"为事实，需统一改为上述精确表述并把**运行时源码版本**降级"待核实"：
- `docs/evidence/method-comparison-matrix-20261008.md:19,21,41`
- `docs/evidence/per-direction-three-method-20261009.md:15`
- `results/stage-reports-20261009/build_report03.js:24,45,47,80`（对应 PPTX 汇报 3）
- `results/stage-reports-20261009/build_report05.js:14,24`（汇报 5，标题页 meta 即写 `label-aware`）
- `scripts/build_final_report.py:114,122`（**Word 正式报告**："ref_labels 参与训练（label-aware）"）
- 另波及 `docs/evidence/metric-lineage-20261008.md:57`、`docs/reports/report-05/06`、`results/report-02-.../render-report.md:30`（"label-aware"检索项）。

**判定 = 阻塞**：该断言已进入 Word 与两场汇报 PPT，且与项目自身审计边界冲突，不可按现文发布。修正后可放行（因 headline 结论"label-free vs label-aware 不可互比"仍成立）。

---

## ② SAMap 无原生 inductive 投影 —— **需修改**

**结论：近似与真正 out-of-sample 的差距没有被显式声明；方案 C1 对 SAMap 的措辞（"固定联合图"）含歧义，可能把"用含 query 的 v98 联合图"误当"冻结投影"。**

依据：

- 会商已如实记录："SAMap ❌ 无原生冻结图投影，只能'冻结同源图 + ref 锚点 KNN'近似，**需如实声明为近似**"（`genpilot-consultation-20261009.md:94`）。
- 但方案 C1 写作"**SAMap：固定联合图，禁止目标物种进入建图（需确认 keys 行为）**"（`three-tier-followup-20261009.md:44`），未点名"近似"。而现网 v98 的联合图是**含全部三物种、迭代对齐**的：`scripts/run_samap_compliant_v98_dcs.py:351` `SAMAP(keys=cell_type)…run(NUMITERS=3)`，评估直接用联合空间 `X_samap_pca`（`:356`）。若"冻结图"沿用这张图，query 表达早已入图，**根本不是 out-of-sample**。

**仍然可能泄漏的点（近似路线即便只冻结 ref 图也难以完全排除）**：
1. **基因集/HVG**：SAMap 每物种独立选基因（`:271-274` `thresh_high=0.96, min_expression=1`），held-out 物种的 HVG 由其自身表达分布决定；若最终锚点映射用的基因集包含按 query 分布筛出的基因，则 query 影响了特征空间。
2. **定位 query 的预处理**：把 query 放进冻结空间，仍要用 query 表达算它自己的 SAM/PCA；若这一步用了 ref 统计量（如 ref 的均值/方差标准化）属**允许**，若用 ref+query 联合统计量则**泄漏**——方案未区分。
3. **迭代对齐的算法偏离**：原 SAMap 靠所有物种相互迭代；"ref-only 图"改变了算法，结果已不是同名 SAMap，而是一个新方法，必须换名。
4. **标签双通道**：SAMap 本身 `keys=cell_type` 即 label-aware（`:435` `label_aware: "keys=cell_type declared"`），叠加近似投影后，"泛化"结论是**双重有条件**的。

**建议**：C1 产物须显式标注 **"SAMap-approx / 近似 inductive"**，并在方案里增设一条 C1 硬闸门——**必须证明冻结图是用 ref-only 构建、且 held-out 物种表达未进入图的任何构建步骤（附 membership 清单）**；C2 的 SAMap 格子不得命名为"held-out SAMap"。

---

## ③ 泄漏防护清单 —— **需修改**（清单不完整，且多数新增项在当前产物中"部分可查、SATURN 项不可查"）

会商/方案给出的三条（条码前缀隔离、标签隔离、投影后不回流，`genpilot-consultation-20261009.md:98-99`；方案 `three-tier-followup-20261009.md:51`）只覆盖"字符串唯一性 + 标签不回流"，**缺以下关键项**，并附"现有产物能否核查"：

| 缺项 | 为什么是泄漏/漏洞 | 现有产物可否核查 |
|---|---|---|
| **基因集选择是否用 query** | 共享直系同源基因集要求两侧都存在：`ortholog_pca_local_v1.py:242` `tu in d_t["var_idx"]`，即**用了 query 的基因存在性** | **可查**：脚本已证实用了 query；inductive 版必须改为只用 ref+词典 |
| **HVG 是否在全数据上选** | 方案未规定 HVG 选择范围；SATURN `hv_genes=8000` 的选择范围无留档 | **SATURN 不可查**（训练命令缺失）；SAMap/local_v1 可从脚本判读 |
| **投影是否用 query 的 batch/供体/模态** | 无 batch 列使用的显式断言；`non_species_batch_col` 默认 `None`（saturn-src 默认段），但方案未把它写成硬断言 | **部分可查**：现有脚本未用 batch；但无 profile 断言 |
| **归一化/标准化统计量范围** | 若用 ref+query 联合统计做 scaling/PCA 即泄漏；`local_v1.py:258` **PCA 在 `X_joint`（ref+query, `:254`）上拟合** = 转导本质 | **可查**：脚本证实当前为联合；inductive 版须 ref-only |
| **映射表/标签空间本身是否由 query 标签派生** | mapping v1 的 query 物种行来自 query 标签；included/excluded 掩码由 query 真值决定（`local_v1.py:262-264`、`run_samap_compliant_v98_dcs.py:187-190`） | **可查**：属"评估范围"，非训练泄漏，但须声明 |
| **供体/样本级隔离（非仅条码）** | 前缀只保证字符串唯一，**不防同一供体的细胞同时落入 ref 与 query**；LOO 换物种虽无此问题，但单物种内复现/多批次会中招 | **不可查**（无 barcode-roles 回填，`config/barcode-roles-v73.tsv` 为空模板） |
| **嵌入不可跨折复用 / seed 不得择优** | v99 直接复用 v97g 同一嵌入（`manifest.source_sha256=20cf807f…`）；鱼方向 seed 双峰（11.3/48.8/8.3）→ 有择优风险 | **可查**：方案须预注册"逐 seed 全报 + mean±sd" |
| **显式 profiler/负控** | inductive 每格缺 shuffle-null / 特征打乱对照（A 档有，C 档无） | **不可查**（尚未产出） |
| **held-out 标签物理隔离** | SATURN 产物把 query 的 `ref_labels` 与嵌入**同文件并列**；任何读该 anndata 的流水线都会顺带拿到 query 标签 | **可查**：须在投影前剥离 held-out 物种标签 |

**判定 = 需修改**：清单需扩充到"基因集/HVG 范围、统计量范围、batch/供体、供体级隔离、seed 预注册、标签物理剥离、折间不复用、负控"八项，并逐项写明"平台机制 vs 自保证 + 可核查产物"。

---

## ④ 成本估算 —— **需修改**（0.011 元/分钟 反推的适用边界未写；并与方案自相矛盾）

**反推本身**：0.18 元 ÷ 16.4 min = 0.011 元/分钟·1c4Gi（`genpilot-consultation-20261009.md:31`），且已标"非官方单价"。适用边界必须写明：

1. **只适用于 1c4Gi 这一档的 WDL/w-类在线任务**（唯一数据点=1 次 runsamap）。跨 CPU 档（4c16g/8c31g…）按"每核分钟线性缩放"是**未经验证的假设**——平台常按档位每分钟计价（超线性）。
2. **计费取整误差**：单点仅到分（0.18），短任务受最小计费粒度影响大；外推到 ~4-5 min/次的小任务时误差可达两位数百分比。
3. **GPU 档不可外推**：3080Ti/L4 计价独立且"平台无公开接口"（`:112-113`），材料正确地把 SATURN GPU（5-6h / 18h）标为"单价待核实"（`:107,110`）——此点通过。
4. **交互/容器时长、存储、idle 计费口径不同**，不能按分钟线性推。

**更严重的是内部矛盾（必须修）**：

- **档名撞车**：会商"B 档 = 留一物种×3 方法×3 seed×3 层 = 81 格"（`:108-110`）＝ 方案里的 **档 C2**；而方案"档 B"是同批单细胞小规模（`three-tier-followup-20261009.md:23-36`）。两份材料的 A/B/C **语义不同**，费用表不可直接套用。
- **费用与范围不符**：会商 B 档 oPCA ~1.4 元、SAMap ~1.6 元（`:106-109`）隐含 ~127/145 分钟；但 27 次主运行 × 单次 SAMap ~16 min ≈ 432 min ≈ **4.75 元**，与 1.6 元矛盾。且 oPCA/v99 方案里"可本地"（`three-tier-followup-20261009.md:32`），却计入 1.4 元。
- **A 档自相矛盾**：方案 A 档"零费用"（`:18`），会商 A 档却含 SAMap ~0.55 元、SATURN GPU 5-6h（`:105-107`）——两者 A 档范围不一致。
- **已花费口径不一**：方案写"约 1.3 元"（`:59`），会商写 1.13 元（`:49`）。

---

## ⑤ 三档结论声明 —— **需修改**

- **A 档**：`three-tier-followup-20261009.md:20` "**不能**支持泛化结论"，与"本地复算/无训练"协议相符 —— **通过**（唯一提醒：A 档不得把复算数字混入"新实验"）。
- **B 档**：`:35` "**不能**支持泛化（仍 transductive）" 正确；但 `:28` 协议标签**直接写入"SATURN/SAMap label-aware"**——把①中未定的可见性**固化进新实验的协议标签**，会**传播未核实结论**。须改为按①的精确机制声明或标"pending"。
- **C 档**：`:52` "首次可写 held-out/inductive 泛化结论（若通过）"，并设"C1 未通过→不得进 C2"（`:47`）——方向对，但**存在把近似投影写成泛化结论的风险**：C1 对 SAMap 只能给"近似接口"，却未设"必须按近似命名/另立方法栏"的闸门；C2 "81 格 inductive 结果 + 与 transductive 成对差值表"（`:46`）会**把"方法差异"与"协议差异 + 引擎近似差异"混为一谈**（转导-泛化差值不再是纯泛化能力度量）。
- 另：C 档"单次 GPU ≤ ¥50"（`:49`）在 **GPU 单价未核实**时**构不成有效保险丝**；且无总额上限。

---

## ⑥ 其他协议漏洞 / 需补的实验前检查 —— **需修改**

1. **溯源错配（重要）**：
   - 会商用 `ortholog_pca_v98_final.py L118` 作为 oPCA label-free 证据（`genpilot-consultation-20261009.md:76`），但**冻结数字实际来自 `scripts/ortholog_pca_local_v1.py`**（`results/pilot-v1/ortholog-pca-v98/manifest.json` 的 `script_sha256=6582d873…`＝`local_v1.py` 实测哈希；而 `v98_final.py` 哈希为 `01e7f303…`）。且 `v98_final.py:117` 的 `fit_transform(X)` 中 `X` 是载入循环遗留变量（第 90-91 行），**并非拼接矩阵**——该文件本身不自洽，不应作为行号证据。→ 须澄清"哪个 oPCA 脚本是权威"，并把会商引用改为 `local_v1.py:254,258,265-266`。
   - SAMap 冻结数字来自 WDL 部署脚本 `samap_script.py`（`results/pilot-v1/samap-v98/wdl-run/extracted/manifest.json` `script_sha256=c0f05b89…`），**与 checked-in `run_samap_compliant_v98_dcs.py`（`71dd08a3…`）不是同一文件**；"keys=cell_type→label-aware"的证据来自 checked-in 脚本（`:351`），**不等于线上运行脚本**。同理该 run 的 manifest 里**没有 `label_aware` 字段**。→ "SAMap label-aware"也应附带"运行脚本内容未回捞"待核实。
2. **SATURN 运行时 provenance 未闭合**：v71/v99 运行时源码/镜像 commit 从未与 checked-in 对齐（`audit-completion-matrix-20260926.md:7`），且**训练命令整体缺失**——这同时**卡住"SATURN label-aware"与任何 inductive SATURN 设计**的复现。
3. **v97g 无逐细胞/无 confusion**（`per-direction-three-method-20261009.md:70-74`）→ A 档"逐细胞预测一致性核对"**必须显式排除 v97g**，否则该 check 无法闭合。
4. **mapping v1 尚未人工签认**（`reviewer-signoff-request-mapping-v1.md`；`inductive-pilot-manifest-v1.md:27`）→ C 档"mapping 签认"应为**硬前置**，不能只列依赖。
5. **单细胞子集筛选会改细胞数**：方案 B 筛 `cell_or_nuclei=='cell'`（`:27`），但冻结矩阵用的 1528/1535/1543 是该子集的**混合**口径；筛后 n 变化会同时改变 majority 与 acc，**不得解读为方法性能升降**，须并列 n_q/coverage/majority（方案已要求全列，但需加"不做跨口径性能比较"警示）。
6. **缺 inductive 负控**：A 档有负控矩阵（`:15`），C 档无——建议 C 每折至少加"标签打乱零分布"与"特征打乱"。
7. **seed 预注册**：鱼方向双峰（`report-05` / `final-evidence-matrix §五`），LOO×3 seed 必须**先注册聚合规则**（全报+mean±sd，禁最大择优），否则 81 格可被事后择优。
8. **"单细胞优先"与"泛化"概念错位**：以 species 为留出单位，其可分性远高于"留出供体/样本"，LOO 结果会**高估**现实泛化；结论须注明"跨物种级 LOO，非跨供体"。
9. **两处"待核实"处理正确**：单价（`:112`）与 r1d 失败原因（`:33,37`）已如实标注，且注明 GenPilot 被人工中断（`:55-56`）——**通过**；但应据此把会商 §③④ 一律视为 provisional。

---

## 汇总

- 框架可用，但**① 是不可发布的过度结论**（已被项目自身审计否证，却写入 Word+两场 PPT）；②⑤ 是"近似/协议差异被写成泛化"的措辞风险；③④⑥ 是清单与溯源缺口。均为**可修正**（无需新增付费运行，除已计划的 C 档外），故总体判 **revise**；① 视为**发布前必须就地修正的阻塞项**。

```json
{"protocol_review": "revise", "must_fix": ["①将' SATURN=ref_labels参与训练'全链（method-comparison-matrix:19,21,41；per-direction:15；build_report03.js:24,45,47,80；build_report05.js:14,24；build_final_report.py:114,122）改为'label-aware来自cross_species miner的labels通道(ref_labels仅为输出/评估真值)'，并把v71/v99运行时源码版本降级'待核实'", "②C1对SAMap增设'近似inductive'显式声明与硬闸门(ref-only图membership证明；冻结图必须不含held-out物种)，C2的SAMap格改名SAMap-approx，禁写'held-out SAMap'", "③泄漏清单扩充：基因集/HVG选择范围、归一化/PCA统计量范围(ref-only)、batch/供体使用断言、供体级(非仅条码)隔离、seed预注册、held-out标签物理剥离、折间嵌入不复用、inductive负控", "④统一两份材料的A/B/C档定义(会商B=方案C)，改正B档oPCA/SAMap费用与单次16min×27run≈4.75元的矛盾，写明0.011元/分钟仅适用于1c4Gi WDL档、GPU与跨档不可线性外推", "⑤B档协议标签不得把未核实的SATURN/SAMap可见性写成既成事实；C档禁止把近似投影/协议差值写成泛化结论，并给GPU总额上限", "⑥修正溯源错配：oPCA权威脚本为ortholog_pca_local_v1.py(manifest script_sha=6582d873)，SAMap线上脚本为samap_script.py(c0f05b89)≠checked-in(71dd08a3)，均需回捞或标待核实", "⑥A档逐细胞核对须显式排除v97g(无逐细胞/confusion)；mapping v1人工签认设为C档硬前置；LOO结论标注'跨物种级，非跨供体级'"], "checked": 6}
```
