# LBSPA 论文精读与跨门场景可行性（2026-10-17）

> 论文：*Lamprey 3D single-cell transcriptomics reveals ancestral and specialized features of the vertebrate brain*
> Science, 18 June 2026 | DOI `10.1126/science.aea2535`
> 本地 PDF：`E:\xwechat_files\wxid_2gvkgptwgs8b22_6b72\msg\file\2026-09\Lamprey 3D single-cell transcriptomics ... .pdf`
> 文件校验：13,463,395 bytes｜SHA-256 `b83b66f9362ce84e31931da590bc1fa2b378a002e9d9ba958e633860ffb4e745`
> **与 `docs/source-file-manifest.tsv` 记录一致** ✅

---

## 一、论文核心内容

### 1.1 科学问题

- 七鳃鳗（lamprey）是**无颌类**脊椎动物，约 4.5 亿年前与有颌类分化，是最基础的现存脊椎动物之一
- 用 **snRNA-seq + 高分辨率空间转录组** 构建成体七鳃鳗脑的完整 3D 分子图谱
- 与斑马鱼（新生成）、小鼠、猕猴、斑胸草雀、鸽子、龟、蜥蜴做跨物种比较

### 1.2 关键数据规模

| 项 | 数值 |
|---|---|
| 七鳃鳗细胞群体 | **209 个 distinct cell populations** |
| 脑区 | **14 个主要脑区**（图中标注 13 个，meninges 被排除） |
| 斑马鱼 snRNA-seq | **56,787 个细胞核**（新生成） |
| 跨物种同源基因 | **13,172 个 conserved gene orthologs** |
| 模态 | snRNA-seq（单核）+ Stereo-seq（空间） |

### 1.3 方法学（**关键**）

论文的跨物种整合**用的正是 scVI**：

> "cross-species integration and batch effect removal were executed across the whole brain
> and distinct anatomical regions using the **scVI algorithm** via `stereoAlign.alg.scvi_alignment(adata, batch_key="species", max_epochs=200)`"

**这直接印证了 Claude 的判断**：课程标题"SATURN vs SAMap vs **scVI 系**"里的 scVI，
正是 LBSPA 论文用的方法。我们的项目矩阵里**没有 scVI 臂**，这是实打实的缺口。

### 1.4 数据可用性

| 项 | 地址 |
|---|---|
| 七鳃鳗原始/处理后数据 | CNGB `CNP0007565`（https://db.cngb.org/） |
| 代码 | GitHub `https://github.com/Dee-chen/lbspa_code` |
| 交互网站 | https://db.cngb.org/stomics/lbspa/ |
| 补充材料 | Data S1–S10、Figs S1–S31 |

---

## 二、跨门场景的可行性评估

### 2.1 课程要求 vs 我们现状

| 项 | 课程要求 | 我们现状 |
|---|---|---|
| 跨门场景 | 七鳃鳗脑 vs 小鼠脑 | ❌ **完全未做** |
| 数据 | LBSPA（snRNA） | DCS 项目里有 `lamprey` 目录，**但内容未核实** |
| 方法 | — | 论文用 scVI；我们连 scVI 臂都没有 |

### 2.2 历史核查记录（重要）

`docs/dcs-readonly-audit.md:74,90,95` 记录了 2026-09 期间的只读检查：

> 公共数据栏目共 60 条。搜索 `HEART`、`heart`、`LBSPA`、`lamprey`、`heart atlas`、
> `cross-species`、`CNP0006537`、`CNP0007565` 均为 **0 条**。

→ 当时 DCS **公共库**里没有 LBSPA 数据。

但现在项目数据管理页里能看到 `lamprey` 目录（`/Files/lamprey`）——**需要核实其内容**。

### 2.3 可行性判定

| 维度 | 判定 | 说明 |
|---|---|---|
| 论文方法可参考 | ✅ 高 | 论文给了完整 pipeline（scVI + stereoAlign），13,172 同源基因 |
| 数据可得性 | ⚠️ **待核实** | 需查 DCS `/Files/lamprey` 内容；若无，需从 CNGB `CNP0007565` 下载（可能需申请） |
| 标签空间 | ⚠️ 需建 | 七鳃鳗 209 个细胞群体 vs 小鼠脑区——标签体系完全不同，需新建映射 |
| 模态差异 | ⚠️ 需处理 | 七鳃鳗是 **snRNA（单核）**，我们的心脏数据是 scRNA（单细胞）——**跨模态** |
| 成本 | 0.2–0.5 元（Claude 估） | 但前提是数据在手 |

### 2.4 建议的最小可行路径

**第一步（零成本，必须先做）**：核实 DCS `/Files/lamprey` 里到底有什么
- 若有 snRNA 数据 + 标签 → 可推进
- 若只有空间数据或空目录 → 标 `blocked`，在指南里诚实说明

**第二步（若数据可用）**：最小跨门跑
- 七鳃鳗脑（snRNA）vs 小鼠脑（snRNA）
- 用论文的 13,172 同源基因（或我们自己的直系同源文件，若覆盖足够）
- 只做 coarse 层，单 seed
- **必须用 scVI**（论文方法，也是课程点名的第三臂）

---

## 三、这篇论文对我们纠偏的三个直接价值

### 价值 1：确认 scVI 是课程要求的方法

课程标题"SATURN vs SAMap vs scVI 系"中的 scVI，就是 LBSPA 用的方法。
**我们缺这一臂，必须补。**

### 价值 2：跨门场景有现成的方法学模板

论文的 `stereoAlign.alg.scvi_alignment(adata, batch_key="species", max_epochs=200)` 可直接参考。
13,172 个 conserved orthologs 是现成的基因集参考。

### 价值 3：标签体系可以借鉴

论文用 14 个脑区 + 209 个细胞群体。我们做跨门时，可用"脑区"作为 coarse 层，
细胞群体作为 fine 层——这与我们心脏数据的 coarse/fine 分层思路一致。

---

## 四、与我们现有工作的关系

| 现有资产 | 对跨门场景的可用性 |
|---|---|
| `config/heart-celltype-map-v1.tsv` | ❌ 只覆盖心脏细胞类型，**不适用于脑** |
| ortholog 三件（MGI_HOM / human_orthos / mouse_orthos） | ⚠️ 只覆盖人-鼠-鱼，**不含七鳃鳗** |
| oPCA / SATURN / SAMap 脚本 | ⚠️ 需改造（物种槽、标签体系不同） |
| scVI | ❌ 未实现 |
| 证据链方法论（manifest/SHA/负控） | ✅ **完全可复用** |

**结论**：跨门场景需要**新建**标签映射与同源基因表，不是现有资产的直接延伸。

---

## 五、下一步建议

| 优先级 | 动作 | 成本 | 前置 |
|---|---|---|---|
| 1 | 核实 DCS `/Files/lamprey` 内容（只读） | 0 | 无 |
| 2 | 若数据可用，建七鳃鳗-小鼠同源基因表 | 0（本地） | 步骤 1 |
| 3 | 实现 scVI 臂（先在心脏数据上验证） | 0–0.3 元 | 无（可与跨门并行） |
| 4 | 跨门最小跑（lamprey brain vs mouse brain） | 0.2–0.5 元 | 步骤 1–3 |

**注意**：步骤 3（scVI 臂）优先级应**高于**步骤 4——因为 scVI 是课程点名的三方法之一，
补上它直接解决"方法臂缺失"这个最硬的偏差；而跨门只是"场景覆盖"之一。

---

## 六、边界声明

- 本分析仅**只读**论文 PDF，未修改任何项目文件
- 未访问 CNGB 下载数据（需用户授权与网络确认）
- 未提交任何 DCS 任务
- 论文 SHA-256 与 `docs/source-file-manifest.tsv` 记录一致，可追溯
