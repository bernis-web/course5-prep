# 论文与方法证据卡（2026-09-24）

本文件把课程材料、公开一手论文和方法论文分开记录。论文内容是外部资料，不是当前 DCS 项目的运行证据；任何参数、数据路径和运行结果，仍须以本项目 manifest、原始命令和完整日志为准。

## 证据等级

- **A：公开一手来源**：PubMed/期刊正文或正式方法论文，可支持论文的研究对象、方法框架和作者报告的结论。
- **B：课程材料/本地 PDF**：可支持课程要求和论文方法细节，但不自动证明 DCS 已挂载同一数据。
- **C：项目本地证据**：SATURN 源码、smoke evidence、运行日志和 manifest，可支持本项目实际执行边界。
- 未同时满足 A/B/C 的内容，不得写成“本项目已复现”。

## HEART：动物心脏跨物种图谱

**论文**：Lian et al., *Spatially resolved single-cell atlas reveals the macroevolutionary trajectory of animal hearts*, Science (2026), DOI `10.1126/science.adw0855`, PMID `42490418`。

**公开一手证据（A）**

- PubMed 摘要报告 27 个物种，覆盖脊索动物、节肢动物和软体动物；联合分析指出双侧对称动物心脏具有共享核心基因组，并讨论心肌、成纤维、内皮和神经细胞等核心类型及心室演化轨迹。
- 公开摘要支持的是研究范围和生物学结论，不足以单独支持课程材料中列出的每一个 SATURN 参数。

**课程材料/本地 PDF 细节（B）**

- 课程材料记录：scRNA 约 14 个物种、约 399,483 个细胞；SATURN 整合约 16 个物种、约 479,483 个细胞；同时使用 SAMap、ESM2B、2000 个 macrogenes 和 8000 个 HVGs。
- 这些数字应在报告中标注为“课程材料记录”，除非能在论文方法/补充材料中逐项定位，不能用 PubMed 摘要替代。

**对课题 5 的帮助**

1. 提供真实跨物种心脏场景和较丰富的细胞类型背景，适合作为首轮 2–3 物种小试的候选来源。
2. 提供跨物种标签和生物学保守性的外部背景，但作者的 SATURN/SAMap 输出不能当作评测真值；我们仍须冻结 query/reference、同源标签映射和独立评分协议。
3. 论文同时包含近缘和远缘类群，提醒我们把“物种混合”与“生物保守性”分开评价，避免只看一个 accuracy。

**当前边界**

- 本项目 v71 只覆盖人、鼠、斑马鱼的小规模 scRNA 试运行；不能声称复现 HEART 的 16/27 物种规模。
- v71/v72 的输入路径、task ID、原始命令、barcode 角色和 hash 仍待补证；它们必须写入 `config/eval-manifest-v73.json` 后才可进入正式 benchmark。

## LBSPA：七鳃鳗脑的三维单细胞图谱

**论文**：*Lamprey 3D single-cell transcriptomics reveals ancestral and specialized features of the vertebrate brain*, Science (2026), DOI `10.1126/science.aea2535`, PMID `42313957`。

**公开一手证据（A）**

- PubMed 记录确认该研究围绕七鳃鳗脑的三维单细胞转录组图谱，比较祖先保守结构和谱系特异特征。
- 公开记录可支持研究主题；测序平台、脑区数量、细胞数和整合软件等细节需回到本地 PDF/论文方法核验。

**课程材料/本地 PDF 细节（B）**

- 本地 PDF 记录：Stereo-seq 空间转录组约 465,778 个空间细胞，约 41,678 个高质量单核转录组，覆盖 14 个脑区和 209 个细胞簇；使用 10x Multiome、NovaSeq 6000、约 20,000 paired-end 100 bp reads/nucleus。
- 七鳃鳗—小鼠比较记录了 6,930 个一对一同源基因、13,172 个保守同源基因，并使用 scVI、Harmony 和 Louvain。
- 2026-09-25 对 SHA-256 为 `B83B66F9362CE84E31931DA590BC1FA2B378A002E9D9BA958E633860FFB4E745` 的本地 PDF 重新抽取方法段后确认：单核按 10x Genomics CG000366 Protocol 2 分离，每反应目标 8,000 nuclei；文库使用 Chromium Single Cell Multiome ATAC + Gene Expression Kit，NovaSeq 6000 目标深度为每核 20,000 条 paired-end 100-bp reads。
- snRNA 处理使用 Cell Ranger ARC 2.0.1、Scrublet 0.1 和 Seurat 4.4.0；初始 QC 保留检测基因数大于 300 且小于 4,000 的 nuclei，CCA/Seurat 整合使用 2,000 HVGs。论文后续 snRNA–Stereo-seq 联合分析又使用了更严格的 `nFeature_RNA > 800` 条件，因此这两个阈值对应不同处理阶段，不能合并成一个统一 QC 门槛。
- 七鳃鳗 snRNA 与 Stereo-seq 联合分析将两个 snRNA 生物样本和一个 Stereo-seq 数据集作为 Harmony 1.0 的三个 covariates，使用前 30 个 Harmony dimensions、Louvain resolution 0.5。七鳃鳗—小鼠空间比较用 6,930 个一对一同源基因、`scVI(..., batch_key="species", max_epochs=200)` 和 30D latent embedding；八物种比较则选择至少出现在两个物种中的基因，得到 13,172 个保守同源基因。
- 作者明确区分两类模态偏差：单核富集 pre-mRNA 的表达偏差，以及不同细胞类型在 scRNA/snRNA 中捕获比例不同的偏差。作者只把细胞比例的定量比较限制在 snRNA 数据之间；这直接支持本项目把 LBSPA snRNA 作为独立后置实验，而不是与 HEART scRNA 混在同一个排行榜中。

**对课题 5 的帮助**

1. 适合作为跨门类、跨器官的后置小规模 snRNA 补充，而不是首轮主 benchmark。
2. 能测试单细胞结论在单核模态下是否保持，但模态差异必须单独标记，不能与 scRNA 物种效应混在一个分数里。
3. 由于老师已明确空间组先不使用，Stereo-seq 只作论文背景；当前不把空间细胞数据接入主评测。
4. 论文提供的 QC、HVG、Harmony/scVI 参数是该脑图谱的处理实例，不应直接成为课题 5 的固定超参；可借鉴的是“逐阶段记录 QC”和“species 与 modality 分开建模/报告”的方法设计。

**启动门槛**

- `python scripts/startup_preflight.py --phase lbspa_followup` 仍要求 `lbspa_snRNA_path` 和 `evidence.scrna_conclusion`，这是有意设置的后置门槛，不是需要绕过的错误。

## 方法学对照

### BENGAL（Nature Communications, 2023）

BENGAL 对 28 种“同源基因映射 × 整合算法”组合进行评测，分别考察物种混合、生物保守性和标签转移，并提出 ALCS 量化整合后细胞类型可区分性的损失。论文还强调：同源关系选择会影响结果，远缘物种可能需要保留更多同源关系。

**对课题 5 的新增约束**：BENGAL 的心脏任务逐步加入 5 个物种，并把物种混合、biology conservation 和 cell-type distinguishability 分开看；随着演化距离和物种数量增加，biology conservation/ALCS 可能下降。因此本项目不能只报告一个跨物种 accuracy，应至少保留“标签迁移 + 生物结构保留 + 过度校正风险”三类结果，并把近缘/远缘物种分层报告。

**对本项目的直接启发**：最终报告至少分开报告 macro-F1/标签转移、species mixing、biology conservation 和资源消耗；同时记录同源映射版本，不能只给一个 accuracy。

来源：Song et al., *BENGAL*, DOI `10.1038/s41467-023-41855-w`；期刊页面：`https://www.nature.com/articles/s41467-023-41855-w`。

### scSpecies（Genome Biology, 2025）

scSpecies 以 context species 的有标签数据为参考，target species 可以无标签；流程需要同源基因索引和 batch indicator，先在 context 上预训练 scVI，再通过中间特征空间和近邻约束对齐 target。它适合做“参考物种 -> 目标物种”的轻量对照，但对 target 特有/稀有细胞类型和参考覆盖不足存在风险。

期刊全文还明确说明：target 标签不是必需输入，但 context 必须尽可能覆盖 target 可能存在的细胞类型；对 context 中缺失的 target 类型，模型可能无法正确对齐。因而如果后续加入 scSpecies，必须把“context 覆盖率”和“target-only cell type”作为单独审计字段，不能只看总体 label-transfer accuracy。

**对课题 5 的新增约束**：scSpecies 先在 context 物种预训练 conditional-VAE，再将编码器中间层迁移到 target，并使用同源基因近邻引导对齐；论文报告的性能还依赖邻居数和共享基因数，且 context 未覆盖的 target-only 类型不能被可靠对齐。若作为后续对照，必须固定 context→target 方向、邻居数、共享基因清单，并记录 target-only/abstention，而不能把它当作完全对称的无监督整合。

**对本项目的直接启发**：把 context/reference 与 target/query 角色写入 manifest，并把 inductive（训练阶段不看目标数据）与 transductive（整合阶段允许目标表达进入）分开，不可混称。

来源：Schächter et al., *scSpecies: enhancement of network architecture alignment in comparative single-cell studies*, Genome Biology (2025), DOI `10.1186/s13059-025-03866-2`；期刊页面：`https://genomebiology.biomedcentral.com/articles/10.1186/s13059-025-03866-2`。

### CAMEX（Nature Communications, 2026）

CAMEX 将不同物种的细胞—基因关系构造成异质图，用 many-to-many 同源关系连接图；无监督整合使用图自编码器，半监督注释使用有标签参考集和图注意力分类器。该思路对极端物种差异和多对多同源关系有启发，但初始特征、图采样、许可证和运行资源仍需单独核验。

论文方法显示图中包含 cell-expression、gene-expression、cell kNN、gene orthology 及 cell/gene self-loop 六类边；预处理后的 top 2,000 HVGs 用于初始化 cell 特征。虽然图结构纳入 many-to-many 同源关系，作者也明确指出 cell node 的初始特征仍依赖 one-to-one homologs。这意味着它不能被简单宣传为“完全摆脱一对一同源基因限制”。

**对本项目的直接启发**：可作为后续方法卡，不进入当前 1c4g 首轮主 benchmark；先保留论文级方法摘要，不把候选实现视为已安装或可运行。

来源：*CAMEX*, Nature Communications (2026), DOI `10.1038/s41467-026-69696-3`；期刊页面：`https://www.nature.com/articles/s41467-026-69696-3`。

## 2026-09-25 一手来源复核记录

- HEART 与 LBSPA 的 DOI/PMID 入口已按论文题名重新核对：HEART 为 Science DOI `10.1126/science.adw0855`、PMID `42490418`；LBSPA 为 Science DOI `10.1126/science.aea2535`、PMID `42313957`。公开摘要只用于确认研究对象、物种/脑区图谱范围和作者层面的生物学结论；课程材料中的参数仍按 B 级证据处理。
- BENGAL、scSpecies、CAMEX 的期刊入口和 DOI 已与方法卡逐项对照。它们分别支持多维跨物种评测、context/reference→target/query 的角色拆分，以及 many-to-many 同源关系的图模型思路；均不构成本项目 DCS 运行证据，也不自动证明软件在当前环境可运行。
- 因此本项目报告应把“外部论文方法证据”和“本地 SATURN/DCS 实测证据”分成两栏；论文来源可决定评估协议和方法对照，但不能填充 `eval-manifest-v73.json` 中的 task、命令、hash、barcode 或独立留出字段。

## 2026-09-26 方法证据补充复核

- BENGAL 正文的直接方法边界是：4 种同源映射方式、10 个整合算法、16 个任务；输出评估分为物种混合、biology conservation 和 annotation transfer，并额外报告 ALCS。它还包含 5 物种心脏/主动脉任务，说明“物种数”和“演化距离”应作为实验因素，而不是只把所有物种混成一个总分。
- scSpecies 正文明确要求 context 数据集具有足够的细胞类型覆盖，并以 context 标签、同源基因索引和 batch indicator 为输入；target 标签不是必需输入。该方法的设计更接近有方向性的 context→target transfer，而不是对称的两侧标签迁移。
- HEART 和 LBSPA 仍按现有 A/B 分层保存：公开论文入口支持研究范围和方法框架，本地 PDF/课程材料支持测序与分阶段处理细节；它们都不构成当前 DCS 任务的 provenance。

本轮官方页面复核补充了以下可直接引用的边界：HEART 的 PubMed 摘要明确为 27 个物种的动物心脏多组学图谱；LBSPA 的 PubMed 摘要明确使用空间转录组与单核 RNA 测序，并在 14 个脑区识别 209 个细胞簇。BENGAL 期刊正文明确将 28 种“同源映射×整合算法”组合按 species mixing、biology conservation 和 annotation transfer 等维度评估；scSpecies 正文明确区分 context 与 target，并用预训练 conditional-VAE/架构对齐和同源基因近邻引导迁移；CAMEX 正文明确使用细胞—基因异质图、多对多同源边和六类边，同时说明细胞节点初始化仍依赖预处理表达的一对一特征输入。以上只强化论文方法边界，不改变本项目的 DCS provenance 状态。

## 对下一轮评估协议的约束

1. **标签**：冻结 exact label，并建立 `source label -> mapped label` 表；无法可靠映射的类别标记 `unknown/ambiguous`，不强行归类。
2. **表示层**：manifest 必须明确评估读取 `X` 还是 `obsm["macrogenes"]`，禁止隐式回退。
3. **协议**：transductive 和 inductive 并列；前者不能写成 held-out benchmark。
4. **指标**：至少输出 exact/mapped accuracy、macro-F1、micro-F1、top-k、coverage、abstention、混淆矩阵、每类覆盖率，以及物种混合和生物保守性指标。
5. **物种设计**：先用 2–3 个物种验证流程；正式效果评测再覆盖近缘、远缘和不同类群组合，并固定输入后做 macrogene 容量消融。
6. **模态**：scRNA 主评测形成结论后，再小规模加入 snRNA；空间数据暂不进入主 benchmark。
7. **模态偏差**：若做 LBSPA snRNA，结果单列，不与 HEART scRNA 合并计算总排名；记录 pre-mRNA/基因覆盖差异和细胞捕获比例偏差。
8. **参考覆盖**：若加入 scSpecies 或任何 reference-to-target 方法，报告 context 未覆盖的 target-only 类型，并计算这些类型的 abstention/coverage，而不是强制分配到最近类别。
9. **同源关系**：同时记录 one-to-one 与 many-to-many 映射版本；方法声称支持多对多时，也要核查其输入初始化是否仍依赖一对一映射。

## 参考入口与审计提醒

- HEART：Science DOI `10.1126/science.adw0855`；PubMed PMID 42490418。
- LBSPA：Science DOI `10.1126/science.aea2535`；PubMed PMID 42313957。
- BENGAL：Nature Communications DOI `10.1038/s41467-023-41855-w`。
- scSpecies：Genome Biology DOI `10.1186/s13059-025-03866-2`。
- CAMEX：Nature Communications DOI `10.1038/s41467-026-69696-3`。
- 课程及 PDF 细节：`docs/source-notes.md`；原始文件版本以 `docs/source-file-manifest.tsv` 核验。
- 证据入口索引：`docs/source-evidence-index-20260924.tsv`；该索引只用于定位来源和边界，不替代原始来源。
- 项目运行边界：`docs/audit-and-next-round-20260924.md`、`docs/saturn-smoke-evidence-20260922.md`。

**禁止越过的证据缺口**：没有原始 DCS 命令、task ID、完整日志、输入/输出 hash、barcode 角色和标签映射前，不得把 v71/v72 数字升级为正式 benchmark，也不得启动大规模运行。

## 2026-09-26 公开来源复核补记

本轮重新核对公开一手入口后，以下边界得到再次确认：

- HEART 的 PubMed 记录支持“27 个物种的动物心脏多组学图谱”和宏演化研究范围；
- LBSPA 的 PubMed 记录支持“空间转录组 + 单核 RNA 测序、14 个脑区、209 个细胞簇”的研究摘要级事实；
- BENGAL 正文支持 28 种“同源映射 × 整合算法”组合、16 个任务，以及 species mixing、biology conservation 和 annotation transfer 分开评估；
- scSpecies 正文支持 context→target 的有方向迁移、目标标签不是必需输入，以及 context 需要尽量覆盖目标细胞类型。

这些复核只提高外部论文证据的可追溯性，不改变当前项目的 DCS provenance、barcode 角色表或 `evidence_status=pending` 状态。
