# Codex 评审交接：课题5 创新性与方法扩展（v2，2026-09-24）

> 致 Codex：请评审课题5 当前方案的创新性不足之处，并推荐应纳入的其他跨物种整合比对方法。本文档自包含今晚全部关键结果与设计决策；更细的执行证据见 `docs/saturn-smoke-evidence-20260922.md`、`docs/heart-pilot-scvi-baseline-20260921.md`。仅输出分析，不改文件。

## 一、当前方案与最新结果

**设计**：三方法（SATURN / SAMap / scVI）× 三物种（人/小鼠/斑马鱼心脏 sc 数据）跨物种细胞类型注释 benchmark。

**已有数字**：

1. scVI 物种内基线（KNN15，20% 留出，n_latent=10，2000 HVG）：human 98.38 / mouse 98.12 / zebrafish 92.51。
2. SATURN 跨物种标签迁移（2026-09-24 首轮正式数字；KNN15 距离加权，1000 macrogenes 潜空间，真实 ESM2 5120 维基因嵌入，50 epochs 收敛）：

| 方向 | 准确率 |
|---|---|
| human → mouse | 56.68% |
| mouse → human | 18.46% |
| mouse → zebrafish | 20.93% |
| human → zebrafish | 11.54% |
| zebrafish → mouse | 6.71% |
| zebrafish → human | 0.07% |

3. 16-macrogene 试点（同数据）：human→mouse 3.38% → 1000 macrogenes 后 56.68%，说明宏基因容量是决定性超参。

**已知混淆因素**：评估用精确字符串匹配。人/鼠标签命名同源故 human→mouse 高；斑马鱼 14 类型名（atrium/ventricle CM 等）与人/鼠 12 类几乎无字符串重合，故 zebrafish→human 近 0。**同源类型映射后重算是下一步**，预计大幅改变数字。

**记录在案的方案性偏离**（平台约束所致，见下）：1500 细胞/物种（分层下采样 seed=0）；基因宇宙 = 每物种 2500 HVG 候选集（SATURN 内部再选 2000 HVG）。

## 二、平台/工程约束（影响可行方案的范围）

- BGI DCS 离线任务通道：当前**仅 1c4g 档可调度**（8c32g 与 32c128g 实测长时间不调度）。容器无外网，依赖 wheelhouse 离线安装 + 分片上传。
- 内存实测教训：SATURN prep 把全基因嵌入堆成 n_genes×5120 矩阵，三物种全基因（~19k/23k/26k）在 4GB 下必 OOM（RC=137），因此做了 HVG 预切。全基因×3000 细胞的"无偏离"重跑需等大规格恢复。
- SAMap 1.0.16 已装通（hnswlib 用 sklearn 精确 NN shim 替代），尚未跑正式比对（缺 ortholog 映射文件下载通路）。

## 三、需要评审的方面

1. **评估框架**：仅 KNN 精确匹配准确率是否足够？是否应加入（a）同源类型映射后准确率，（b）label-free 指标（LISI/kBET/Silhouette），（c）top-k 迁移准确率与混淆矩阵分析，（d）斑马鱼外群对 mammal 基准影响的消融？我们是否应把"跨物种标签映射表"本身做成可复用贡献？
2. **方法池扩展**：除 SATURN(2023)/SAMap(2021)/scVI(2018) 外，以下哪些值得纳入 2024-2026 的新方法？metaboliSense、SATURN 后续版本、COSG/MOJITOO/Mowgli、ESM2/Geneformer/plant 等 PLM 原生跨物种方案、Harmony/Symphony/CellTypist 跨物种适配、其他（请给近两年被引用最多的 2-3 个）。
3. **创新点**：在"跑工具比准确率"之外，可加分的方法学贡献候选：
   - 统一的跨物种评估协议（同源映射 + label-free + 迁移率的三角评估）
   - 蛋白语言模型嵌入 vs 序列比对正交组的系统对比
   - 低算力可复现的 benchmark 流程（本项目的 wheelhouse 离线管道是否可写成 artifact）
   - 宏基因容量/嵌入维度对跨物种迁移的 scaling 规律（16 vs 1000 已有 17× 证据点）
   请评估哪些最可行、最能回应"创新性不足"。
4. **斑马鱼方向不对称性**（zebrafish→human 0.07% vs human→zebrafish 11.5%）：是否可深挖为独立发现（标签体系差异 vs 潜空间方向性差异）？需要补哪些对照实验？

## 四、输出要求

- 对上述 4 个方面各给具体建议（每项 1-2 段）
- 推荐优先纳入的 2-3 个新方法（附理由 + 论文引用）
- 指出当前方案最可能被审稿人质疑的 3 个薄弱点及补救方案
- 评估：以现有三物种数据 + 已跑通的管道，最快能做出哪一个"有方法学含量"的增量贡献（一周内可完成的优先）
