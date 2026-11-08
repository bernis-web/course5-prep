# 课题 5 审计收口与下一轮计划（2026-09-24）

## 结论先行

当前项目已经证明：三物种心脏单细胞数据的 SATURN 试运行管道可以在 DCS 的 1c4g 约束下完成，并且已经有 v73/v74b 的 mapped-label、ortholog-PCA、ESM2 置换和 seed 稳定性探索结果。当前仍没有证明 v71/v72 数字是独立留出泛化性能，也没有证明 num_macrogenes 单独造成了 v62 到 v71 的提升。

因此，现阶段对外表述只能用“探索性管道结果”和“待审计的跨物种迁移现象”，不能写成正式 benchmark 或生物学定论。

## 已证实

1. docs/saturn-smoke-evidence-20260922.md 记录了 v71 的三物种真实训练：人、鼠、斑马鱼，约 1.5k 细胞/物种，2500 HVG 候选基因宇宙，真实 ESM2 嵌入，1000 macrogenes，2000 HVGs，50 epochs，1c4g CPU。
2. 同一记录给出了 v72 KNN15 距离加权迁移数字，但评估对象来自 v71 Final AnnData；后续 v73/v74b 已有 mapped-label 汇总，且 `docs/celltype-map-validation-v1.md` 记录了 `g5-pseudo-v84e` 的独立 pseudobulk 核验并冻结 v1 映射；仍缺查询/参考 barcode 清单、独立留出清单、逐细胞预测表和人工 reviewer 签名。
3. wheelhouse/saturn-src/train-saturn.py 的 create_output_anndata 把模型输出 train_emb 写入 X，把编码器输入写入 obsm[macrogenes]。因此任何 v72 结果都必须在报告中明确使用的是哪一个表示层。
4. SATURN 默认 unfreeze_macrogenes=False；当前 checked-in 训练 miner 是 cross_species。该分支的 triplet 索引函数实际按普通 `labels` 构造正负样本，不使用传入的 `ref_labels`；因此 Final AnnData 中存在 `ref_labels`，或命令行出现 `--use_ref_labels`，都不能证明它参与了 v71 的实际 triplet 路径。
5. 2026-09-24 续审本地验证：`python -m unittest discover -s tests -v` 为 68 tests、3 skipped、其余通过；评估器和测试文件通过 `py_compile`，`git diff --check` 通过，manifest JSON 可解析。`python scripts/startup_preflight.py` 的 `heart_pilot` 阶段为 ready，七鳃鳗后续阶段仍因路径和 scRNA 结论证据门槛保持阻塞。
6. `saturn-smoke-evidence-20260922.md` 的 2026-09-25 追加记录了候选映射 38 行、coarse/fine 双层结果、majority baseline、置换消融、seed 稳定性和物种内 ceiling；这些是项目本地探索证据，不替代原始 DCS 命令、任务详情或逐细胞输出。
7. ortholog-PCA 对照在当前 1c4g-slim 条件下 6 个方向中 5 个方向高于 SATURN，唯一 SATURN 胜出的是 mouse→zebrafish；这说明首轮应报告“带一对一同源先验的零整合基线”，不能把 SATURN 的单次结果写成方法普遍优越。
8. ESM2 行置换显示 human→mouse 的 coarse 结果由 67.4% 降至 20.4%，支持该方向存在真实蛋白同源信号；但 zebrafish→mouse/human 在 seed0/1/2 间呈双峰或剧烈不稳定，必须报告均值、标准差和单 seed，而不能只报最好一次。
9. 物种内 SATURN ceiling（human 85.5%、mouse 93.5%、zebrafish 74.2%）低于同一记录的 scVI ceiling（98.4%、98.1%、92.5%），提示跨物种掉分既可能来自物种差异，也可能来自 SATURN 潜空间本身，不能只归因于标签命名。

## 必须更正的表述

### v62 到 v71 不是 macrogene 的因果实验

16 到 1000 macrogenes 的对比同时改变了细胞数量、基因宇宙、HVG 数量及实验配置，并且只有两个容量点、单一 seed。人到鼠方向明显变化而鼠到人变化很小，也与“容量是决定性因素”的强断言不一致。当前只能说“容量增加与该次结果变化同时出现”，不能说“容量导致了 17 倍提升”。

### v72 是 transductive/in-sample 探索，不是 held-out benchmark

跨物种参考集和查询集在物种层面可以天然不相交，所以不能未经检查就断言存在“查询细胞自邻居泄漏”。但 v71 训练与 v72 评估使用同一批 Final AnnData，且训练阶段使用了细胞标签进行 triplet mining；这仍然使结果属于训练数据上的 transductive 迁移，不能与独立留出结果等价。由于 v72 的 query/reference 角色和原始训练输入尚未取证，目标标签是否进入训练仍保持待核验，不能预填为 `false`。

### 精确字符串准确率受标签体系强约束

斑马鱼类型名与人、鼠类型名不完全同构时，接近 0 的方向可能反映命名体系，也可能叠加真实潜空间失败。映射 v1 已有 38 行并通过独立 pseudobulk 核验后冻结，但 TSV 的 reviewer 字段仍为 pending，且 `Orthers`、`Valve`、`Proliferating` 等类别仍有低置信度或 unmapped 处理；因此报告必须保留低置信度披露，并在正式 benchmark 前补人工 reviewer 签名。

### 当前结果已暴露的稳定性与基线问题

ortholog-PCA、ESM2 置换和物种内 ceiling 已经改变下一轮优先级：先补齐 provenance、确认冻结映射的人工 reviewer 状态、重做独立评估和 seed 汇总，再决定是否申请容量消融或加入更多整合方法。新增方法或更大物种规模不能替代这些质量门。

## 下一轮最小验收设计

### A. 同一变量容量消融

固定 v71 的物种、细胞清单、2500-HVG 候选宇宙、2000 HVGs、seed、训练 epochs 和 miner，只改变 num_macrogenes，至少运行 16、128、1000 三点；每点至少 3 个 seed。结果报告均值、标准差和每个方向的 macro-F1，而不是只报 accuracy。

### B. 两种泛化协议并列

1. Transductive 组：目标物种无标签表达可以进入整合，但目标物种 cell-type 标签只用于最终评分；训练用到的监督字段和无监督聚类先验必须写入 manifest。
2. Inductive 组：训练阶段完全不读取目标物种数据，只在参考物种训练；推理时将目标物种映射到固定表示空间。

两组使用同一标签映射、同一指标和同一拒答规则，并报告二者差值作为“目标数据参与整合”的影响，不得只保留优胜组。

### C. 评估防线

- kNN 检索排除同一 barcode、重复 barcode 和任何输入副本；保存参考/查询 barcode 清单。
- 保存逐细胞预测、置信度/邻居一致率、混淆矩阵、每类覆盖率、macro-F1、micro-F1、top-1/top-3 和 abstention 曲线。
- 低置信度细胞允许弃权，但必须同时报告弃权率、弃权后 F1 和每类覆盖率；零覆盖类别单列。
- 明确评估读取 X 还是 obsm[macrogenes]，并检查二者维度与含义。
- label-free 指标（如 species-LISI、kBET）只用无监督分组；按 cell type 计算的 silhouette 属于标签依赖的事后描述，不能作为无标签早停或模型选择依据。

### D. LBSPA 单核后置门槛

LBSPA 的方法证据只用于设计后置补充，不改变 HEART scRNA 主 benchmark 的放行顺序：

- 只有在 HEART scRNA 的 provenance、标签映射、transductive/inductive 结果和主结论完成后，才允许申请七鳃鳗 snRNA 小规模测试；空间数据仍不进入当前主 benchmark。
- snRNA 的 QC 必须按处理阶段记录：初始 nuclei 过滤（检测基因数大于 300 且小于 4,000）与 snRNA–Stereo-seq 联合阶段的 `nFeature_RNA > 800` 不能合并成一个统一门槛；实际数据仍应以 QC 分布和批次为依据。
- snRNA 结果单列报告，不与 HEART scRNA 合并排名；至少记录模态（pre-mRNA 富集）、基因覆盖、捕获率和细胞比例可比性限制。
- 若采用论文中的跨物种比较思路，必须把 6,930 个一对一同源基因、13,172 个保守同源基因和本项目实际使用的同源集合分别记入 manifest；论文参数不能直接充当 SATURN 的固定超参。

## 方法扩展优先级

第一优先级仍是 SATURN、SAMap、scVI/scANVI 的统一协议，因为它们已与课程要求和现有 wheelhouse 对齐。新增方法只选一个可落地候选做方法学增量：

- scSpecies：2025 年提出的跨物种条件 VAE/架构对齐思路，适合做“同源基因近邻初始化 + 潜空间对齐”的轻量对照；需先确认许可证、依赖和是否能在 1c4g 运行。
- CAMEX：2026 年的异构图神经网络，显式利用 many-to-many 同源关系，适合检验 one-to-one ortholog 与 many-to-many homology 的差异；预计算力和依赖负担较高，先只做文献方法卡，不直接承诺纳入首轮。
- TACMAN：2026 年 transformer + 异构图方法，适合作为近期方法综述对象；当前不列为首轮可执行方法，除非能获得可复现代码和离线依赖。

最可行的一周增量不是再堆方法，而是做“DCS provenance 收口 + 映射审阅冻结 + ortholog-PCA/SATURN/scVI 同协议独立评估 + 3 seeds + 逐细胞审计表”。容量三点消融放在这些证据通过后，并且必须单独固定所有其它变量。

## DCS 与工具状态

- 本轮没有创建 DCS 任务、上传文件、付费或修改云端数据。当前会话没有可用的网页控制资源，不能把已登录浏览器的地址栏状态当作云端日志证据。
- Claude glm-5.3-flash 已完成一次有效只读审查；其结论已由本地源码和文档复核。
- ZCode --help 可用，但只读模型调用仍返回 Model creation failed；本轮停止重试，不把失败调用记为完成。
- 仓库已有用户改动和未跟踪 wheelhouse/探针文件，均未触碰、未清理、未提交、未推送。

## 交给 Claude/ZCode 的下一轮短任务

1. Claude：只读生成 v71/v72 评估 manifest 模板，字段包括 run id、输入文件 hash、barcode 集合、表示层、标签映射、seed、查询/参考角色和评分指标；不改代码。
2. Claude：只读检查 train-saturn.py 与 loss_and_miner_utils.py，列出 use_ref_labels、miner_type 和 unfreeze_macrogenes 的实际分支，给出精确文件行号。
3. ZCode：待模型恢复后再做一次短只读任务，仅检查是否存在 v71/v72 原始命令、DCS task ID 和逐细胞预测表；失败即停止，不循环重试。

## 当前阻塞

1. v71/v72 的真实 DCS 命令、任务号和完整日志尚未落库。
2. 同源 cell-type mapping v1 已有 38 行并完成 pseudobulk 独立核验，冻结报告已落库；仍缺 TSV reviewer 字段的人工签名，且低置信度/unknown 类别不能被解释成高置信真值。
3. SAMap 正式跑数仍受 hnswlib/GCC 兼容性阻塞。
4. 七鳃鳗 snRNA 小规模补充仍等待路径和 scRNA 主结论。
5. 1c4g 内存约束使全基因无偏离重跑暂不适合启动；现有 seed 结果已经显示鱼-兽方向不稳定，不能用增加一次单 seed 运行代替正式重复。

LBSPA 后置阶段另有两个有意保留的阻塞：`lbspa_snRNA_path` 尚未取得可核验的 DCS 路径，且 `evidence.scrna_conclusion` 尚未达到主实验结论门槛；这不是需要绕过的配置错误。

在这些证据补齐前，继续扩充物种或充值算力的收益低于先完成评估协议和审计表。

## 2026-09-24 本地源码复核补充

本轮用当前 `wheelhouse/saturn-src` 源码逐行核对了三个开关：

- `train-saturn.py:56` 的 `train()` 默认参数是 `use_ref_labels=False`；`train-saturn.py:100-103` 只有在该值为真时才把 `ref_labels` 作为命名参数传给 `mining_func`。
- `train-saturn.py:780-782` 实际构造的 miner 是 `TripletMarginMiner(..., miner_type="cross_species")`；`miners/triplet_margin_miner.py:19-39` 再按 `random`、`cross_species`、`cross_species_coarse` 分支选择 triplet 索引函数。当前命令行没有独立的 `miner_type` 参数，因此若 v71 使用了不同 miner，只能来自不同源码版本或源码补丁，不能仅凭命令行推断。
- `train-saturn.py:792-795` 将 `args.use_ref_labels` 传入训练；命令行参数在 `train-saturn.py:968-969` 声明，默认配置在 `train-saturn.py:1025` 为 `False`。
- `train-saturn.py:712-730` 显示 `unfreeze_macrogenes=False` 时，metric-learning 数据集被替换为预训练产生的 macrogene 输入；`train-saturn.py:712-713` 仅在真值时打印解冻提示。命令行声明位于 `train-saturn.py:964-965`，默认配置位于 `train-saturn.py:1034`。
- `train-saturn.py:373-393` 无条件把 `train_ref` 写入 `adata.obs['ref_labels']`。因此 Final AnnData 含有 `ref_labels` 只能证明该字段被输出，不能证明它曾参与 miner；必须回到原始命令、配置和训练日志核验。
- `miners/base_miner.py:28-40` 表明未提供独立 `ref_emb` 时，miner 会把 `ref_labels` 回退为普通 `labels`；这进一步说明“字段存在”和“实际走了哪条监督路径”是两个不同问题。
- 更细的分支核验：`utils/loss_and_miner_utils.py:283-425` 的 `get_species_triplet_indices` 在 `cross_species` 路径中用 `labels` 构造正负样本、近邻和负样本标签；该函数没有用传入的 `ref_labels`。因此在当前 checked-in 源码下，即使命令行显式打开 `use_ref_labels`，也不能把它解释为 `cross_species` triplet 已使用 `ref_labels`；`ref_labels` 的实际作用需要在 `random`、`cross_species_coarse` 或其它源码版本中单独核实。

本轮生成了两个只读审计模板：

- `config/eval-manifest-v73.json`：把 v71/v72 的运行来源、输入哈希、角色、表示层、同源映射和指标全部列出；未知字段保持 `null` 或 `pending`。
- `config/barcode-roles-v73.tsv`：条码角色表的空模板，尚未填入任何未经核验的条码。

Claude 的后续只读复核已返回有效文本，但只确认了“未找到”项：v71/v72 原始 task ID、原始命令、完整日志、绝对路径/hash、barcode 清单和逐细胞预测表仍未落库；它没有新增 DCS 运行证据，也没有修改文件。下一步仍是从 DCS 页面只读提取这些字段后填充模板，而不是据此启动重跑。

## 2026-09-24 续审新增

- 新增 `docs/paper-method-evidence-20260924.md`：将 HEART、LBSPA、BENGAL、scSpecies 和 CAMEX 的公开论文/课程材料/本地证据分层，并把它们转化为下一轮评估约束；其中未把论文作者的结果当作本项目真值。
- 2026-09-24 复核并补充了上述方法论文的一手 DOI/期刊入口：HEART `10.1126/science.adw0855`、LBSPA `10.1126/science.aea2535`、BENGAL `10.1038/s41467-023-41855-w`、scSpecies `10.1186/s13059-025-03866-2`、CAMEX `10.1038/s41467-026-69696-3`。这些入口只用于论文方法证据，不替代本项目的 DCS 运行证据。
- 新增 `docs/audit-coverage-matrix-20260924.md`：按“要求—证据—缺口—放行条件”逐项覆盖 SATURN 路径、v72 独立性、标签映射、论文证据、下一轮实验和 Word 报告边界，作为组员交接和质量门索引。
- 新增 `docs/dcs-v71-v72-evidence-request-20260924.md`：把缺失的 DCS provenance、barcode、表示层和独立评估证据拆成可直接执行的只读查询项，并指定回填文件与验收规则。
- 新增 `docs/source-evidence-index-20260924.tsv`：集中索引 HEART、LBSPA、BENGAL、scSpecies、CAMEX、课程材料和项目本地证据的入口、等级、可支持结论及边界；它是导航索引，不替代原始论文、课程文件或 DCS provenance。
- 新增 `scripts/evaluate_cross_species_transfer.py` 及 `tests/test_cross_species_evaluator.py`：纯本地、显式表示层的 kNN 迁移评估器，排除查询/参考重叠条码和重复条码，输出 exact/mapped 双评分、逐细胞预测、置信度、弃权、coverage、F1 和混淆矩阵；仅支持显式 NPZ 输入，不读取或上传 DCS 数据。
- 评估器的最小调用契约是：先由外部、显式且可审计的提取步骤生成 NPZ，再指定表示层和协议。例如：
  `python scripts/evaluate_cross_species_transfer.py --input-npz <explicit-bundle.npz> --output <summary.json> --representation obsm/macrogenes --protocol inductive --k 15`。
  评估器不会自动打开 h5ad，也不会在 `X` 与 `obsm/macrogenes` 之间回退；`<explicit-bundle.npz>` 和其提取命令必须在正式 benchmark 前补入 manifest。
- `config/heart-celltype-map-v1.tsv` 已形成 38 行映射，并通过 `g5-pseudo-v84e` 的 pseudobulk 独立核验后冻结；人工 reviewer 签名仍待完成，低置信度和 unmapped 标签不得强行归类，因此当前仍不能视为已完成专家签字的最终真值。
- 以上新增物只完善审计与评估接口，不改变 v71/v72 研究结果，也不构成 DCS 启动许可。

## 2026-09-24 验证记录

以下结果来自本次工作区运行，不是历史聊天摘要：

```text
python -m unittest discover -s tests -q
Ran 68 tests in 6.647s
OK (skipped=3)

python -m json.tool config/eval-manifest-v73.json
OK

python scripts/startup_preflight.py
valid=true, ready_for_execution=true, target_phase=heart_pilot, blocking_items=[]

python scripts/startup_preflight.py --phase lbspa_followup
valid=true, ready_for_execution=false,
blocking_items=[lbspa_snRNA_path, evidence.scrna_conclusion]

git diff --check
OK
```

`unittest` 输出中个别测试会故意触发 CLI usage 文本，用来验证参数拒绝路径；最终测试进程仍返回成功，3 个跳过项均对应本机未安装 `anndata` 的测试分支。上述验证不证明 DCS provenance 已补齐，也不把 `heart_pilot` preflight 通过误写成已获云端运行授权。

## 2026-09-25 验证刷新

本轮在补入 LBSPA 后置门槛、证据索引重核日期并删除可再生临时抽取文件后重新运行：

```text
python -m unittest discover -s tests -q
Ran 68 tests in 5.820s
OK (skipped=3)

python -m py_compile scripts/evaluate_cross_species_transfer.py scripts/startup_preflight.py
python -m json.tool config/eval-manifest-v73.json
OK

source-evidence-index-20260924.tsv
TSV_OK total_lines=9 data_rows=8 cols=9

python scripts/startup_preflight.py
valid=true, ready_for_execution=true, target_phase=heart_pilot, blocking_items=[]

python scripts/startup_preflight.py --phase lbspa_followup
valid=true, ready_for_execution=false,
blocking_items=[lbspa_snRNA_path, evidence.scrna_conclusion]

git diff --check
OK
```

本次只更新审计/证据文档，没有创建 DCS 任务、上传数据、提交或推送；未填充任何未知 provenance 字段。

## 2026-09-25 原始课程文件可用性复核

对用户最初提供的三个 E 盘路径做只读存在性与哈希检查：七鳃鳗 PDF仍可读取，文件大小为 `13,463,395` bytes，SHA-256 与 `docs/source-file-manifest.tsv` 中的 `B83B66F9362CE84E31931DA590BC1FA2B378A002E9D9BA958E633860FFB4E745` 一致；课程网页和 HEART PDF 的原始路径当前均不存在。由此，LBSPA 的方法细节仍有本地 PDF 可复核，HEART 的已保存方法笔记和来源索引只能作为历史审计记录，不能在本轮声称重新读取了 HEART 原 PDF。该文件可用性差异不改变论文级外部证据的边界，也不填充任何 DCS provenance 字段。

## 2026-09-25 completion audit（当前状态，不等同于项目完成）

| 目标要求 | 当前权威证据 | 判定 | 尚缺什么 | 放行条件 |
| --- | --- | --- | --- | --- |
| 核实 SATURN v71 的标签/Triplet 路径 | `wheelhouse/saturn-src/train-saturn.py:100-103, 782`；`utils/loss_and_miner_utils.py:283-437`；`docs/local-saturn-source-fingerprint-20260924.tsv` | **部分完成**：当前 checked-in 源码已核实 `cross_species` 分支和 `labels` 取样逻辑 | v71 DCS 运行时的源码 commit、镜像层或补丁 hash；原始命令中的 `use_ref_labels` 和 `unfreeze_macrogenes` | 将运行时版本与本地 fingerprint 对齐，或明确记录差异 |
| 判断 v72 是否独立评估 | `docs/saturn-smoke-evidence-20260922.md`；`config/eval-manifest-v73.json`；`docs/dcs-v71-v72-evidence-request-20260924.md` | **边界已完成，事实未完成**：目前只能称 transductive/in-sample 探索 | v72 task ID、query/reference barcode、留出清单、逐细胞预测表、原始评估命令、表示层确认 | barcode 交集为 0 且目标未参与训练，或正式声明为 transductive 并不作泛化结论 |
| 补齐 HEART/LBSPA 和近期方法论文证据 | `docs/paper-method-evidence-20260924.md`；`docs/source-evidence-index-20260924.tsv`；公开 DOI/PMID 入口 | **论文方法证据完成**：已分层 A/B/C 证据并写明边界 | HEART 原 PDF 当前本地路径缺失；论文不能替代 DCS provenance 或本项目真值 | Word 报告中将论文方法启发与本项目实测结果分栏 |
| 形成下一轮可执行计划和证据缺口清单 | `docs/superpowers/plans/2026-09-24-course5-next-round.md`；`docs/dcs-v71-v72-evidence-request-20260924.md`；本文件和 `docs/team-task-division.md` | **完成** | 需要组员在 DCS 页面补回证据 | 回填 manifest、barcode 角色表并通过验收规则 |
| 保持只读审计边界 | 本轮 git 状态、验证记录、manifest 的 `cloud_actions_allowed=false` | **完成** | 无 | 继续不提交、不推送、不启动 DCS、不上传数据 |

**当前结论：** 本地源码审计、论文证据分层、评估接口和下一轮计划已经形成；DCS 运行 provenance 和 v72 独立性仍未达到 completion gate。因此本目标继续保持 active，不能标记为 complete，也不应把当前数字写成正式 benchmark。

## 2026-09-25 本地 Triplet 静态审计刷新

新增 `scripts/audit_saturn_triplet_path.py` 与 `tests/test_saturn_triplet_audit.py`，审计器只解析 checked-in Python 源码，不导入或执行 SATURN。它同时检查 `train-saturn.py` 和其相邻的 `utils/loss_and_miner_utils.py`，并把源码 SHA-256、行号和证据片段写入 `docs/local-saturn-triplet-audit-20260925.json`。

本次报告的结论是：

- `train-saturn.py:780-782` 确实实例化 `TripletMarginMiner(..., miner_type="cross_species")`；
- `train-saturn.py:100-103` 的 `use_ref_labels` 真分支传入 `ref_labels`，假分支不传入；
- `utils/loss_and_miner_utils.py:283-437` 中 `get_species_triplet_indices()` 的 `ref_labels` 只在默认初始化行读取，没有检测到参与正样本/负样本选择；
- `train-saturn.py:393` 确实输出 `adata.obsm["macrogenes"]`。

该结果进一步支持“当前 checked-in 源码的 Triplet 选择仍按 `labels` 解释；v71 DCS 运行时是否使用同一源码、补丁或镜像仍需 provenance 证据”这一边界。静态审计结果不能替代 DCS task ID、原始命令、运行日志或运行时版本。

## 2026-09-25 manifest 证据门刷新

新增 `scripts/validate_eval_manifest.py` 与 `tests/test_eval_manifest.py`。该校验器只读检查 `config/eval-manifest-v73.json` 和 `config/barcode-roles-v73.tsv`，把“结构合法”和“证据已足以放行”分开：

- 当前 manifest 保持 `evidence_status=pending`，校验结果为 `valid=true` 但 `ready_for_confirmation=false`；
- 当前条码表只有表头，因此明确报告 `barcode_role_table_empty`、`no_query_barcodes` 和 `no_reference_barcodes`；
- 若 pending manifest 被填入看似已核实的 task ID、命令或 hash，校验器会拒绝；
- 若 `provenance.cloud_actions_allowed` 被改为 `true`，校验器会拒绝；
- 只有在 task provenance、输入/输出 hash、表示层、人工 reviewer 和 query/reference 条码表齐全且无交集时，才会返回 `ready_for_confirmation=true`。

本次运行：

```text
python scripts/validate_eval_manifest.py
valid=true, evidence_status=pending, ready_for_confirmation=false
blocking_items=[barcode_role_table_empty, evidence_status_pending, labels.reviewer,
no_query_barcodes, no_reference_barcodes, representation.evaluation_layer,
run.complete_log_path, run.dcs_task_id, run.input_manifest_path,
run.original_command, training_parameters.original_command_flags]
```

该门仍然不启动 DCS；它只是为后续 Flash/组员的只读回填提供机械化验收。

## 2026-09-25 Flash 只读复核

已让 `glm-5.3-flash` 做一次只读复核，结果记录在 `docs/dcs-flash-readonly-audit-20260925.md`。由于当前会话没有获得可核验的浏览器/DCS 页面快照，它没有新增页面级 provenance；它只复核了本地 manifest、空条码表和既有审计文档，并再次确认以下字段不可猜填：task ID、原始命令、完整日志、Final AnnData/hash、v72 表示层、query/reference barcode 及运行时源码版本。

该辅助复核不改变 `evidence_status=pending`，也不改变“v72 只能称 transductive/in-sample 探索性结果”的边界。

