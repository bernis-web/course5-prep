# scVI 跨物种臂设计方案（2026-10-17）

> 背景：课程标题为「SATURN vs SAMap vs **scVI 系**」，但项目现有矩阵只有
> ortholog-PCA / SATURN / SAMap —— **scVI 臂缺失**（Claude 2026-10-17 指出的最硬偏差之一）。
> 本文件记录 scVI 臂的现状、约束与最小可行方案。**尚未运行。**

---

## 一、现有 scVI 资产盘点

### 1.1 已做过的（物种内，非跨物种）

来源：`docs/heart-pilot-scvi-baseline-20260921.md`

| 物种 | 细胞数 | KNN accuracy | 耗时 | 任务号 |
|---|---|---|---|---|
| 人 | 30,000 | 0.9838 | 68.4s | `g3-scvi-baseline-v11-cpu` |
| 小鼠 | 60,471 | 0.9812 | 128.9s | `g5-scvi-mouse-v16` |
| 斑马鱼 | 50,000 | 0.9251 | 275.2s | `g5-scvi-zebrafish-v17` |

**协议**：scvi-tools 1.1.6.post2，SCVI(n_latent=10, max_epochs=5, early_stopping)，
batch_key=donor/orig.ident，labels_key=celltype，HVG 2000，KNN15，**20% 留出集**。

### 1.2 关键限定：这是「物种内」不是「跨物种」

- 每个物种**单独训练**一个 scVI 模型
- 评估的是同物种内的 80/20 留出集
- **没有跨物种整合**，因此不能与 oPCA/SATURN/SAMap 的跨物种数字并列

→ **scVI 臂仍然缺失**，这是必须补的。

---

## 二、执行环境约束（关键）

### 2.1 本地不可行

| 项 | 状态 |
|---|---|
| 本地 python 3.9.6 | ✅ |
| torch | ❌ **未安装** |
| scvi-tools | ❌ **未安装** |
| wheelhouse 里的 torch/scvi wheel | ❌ 无 |

**结论**：本地无法跑 scVI。且用户明确要求「运算不放在本地，用 DCS」。

### 2.2 DCS 侧可行（历史已证明）

- 历史 scVI 任务跑在 `SATURN--22` 镜像 + **32c128g CPU** 档
- 镜像内已有 scvi-tools 1.1.6.post2（无需自建镜像）
- 历史耗时：人 68s / 鼠 129s / 鱼 275s（**全量数据**）

### 2.3 数据规模问题（必须先解决）

| 项 | 历史 scVI | 我们的跨物种对比 |
|---|---|---|
| 数据 | 全量（3万/6万/5万细胞） | `local_*_s.h5ad`（1,528/1,535/1,543 细胞） |
| 基因 | 32,732 | 32,732 / 32,379 / 27,661 |

→ 跨物种 scVI 需要在**同一份 `local_*_s.h5ad`** 上跑，才能与 oPCA/SATURN/SAMap 同口径。

---

## 三、最小可行方案（设计，未执行）

### 3.1 设计要点

| 项 | 设计 | 理由 |
|---|---|---|
| 数据 | `local_{human,mouse,zebrafish}_s.h5ad` | 与现有三方法同源 |
| 基因集 | 1:1 直系同源（修正方向后，9311/8160/15869） | 与 oPCA 同基因集，保证可比 |
| 拼接方式 | 三物种按同源基因对齐后 `vstack` | 跨物种整合的标准做法 |
| batch_key | `species` | 跨物种批次 = 物种（LBSPA 论文同做法） |
| 模型 | SCVI(n_latent=10 或 30, max_epochs=5~50) | 沿用历史协议 |
| 评估 | 与 oPCA **完全相同的 KNN15 cosine + 标签层** | 保证评分口径一致 |
| 指标 | **macro-F1**（与 P1 统一后一致） | 课程要求指标 |
| 方向 | 6 方向（每方向：一个物种作 ref，其余作 query？） | 见 §3.3 |

### 3.2 必须解决的三个技术问题

**问题 1：跨物种 scVI 的 ref/query 划分**

历史 scVI 是「同物种 80/20 留出」。跨物种场景需要：
- 方案 A：三物种一起训练 scVI → 取潜空间 → 按方向做 KNN 标签迁移
  （与 oPCA 的 transductive 性质一致，可比）
- 方案 B：只用 ref 物种训练 → query 物种投影（真 inductive，但 scVI 需 `load_query_data`）

**建议方案 A**：与现有三方法的 transductive 口径一致，且技术风险低。
方案 B 需额外验证 scVI 的 query 投影接口，风险高、时间长。

**问题 2：基因集对齐**

- oPCA 用的是「1:1 同源对」（修正方向后 9311/8160/15869）
- scVI 需要**单一基因矩阵**，所以要把三物种投影到共同的同源基因轴上
- 每个物种取 `shared_genes` 对应的列，按同源对顺序排列

**问题 3：数据规模 vs 历史协议**

历史 scVI 用 HVG 2000 + 全量细胞。我们现在只有 1,500 细胞/物种：
- 细胞数少 → scVI 训练可能欠拟合
- 建议：`n_latent=10`（历史值）、`max_epochs=50`（小数据需更多轮次）、`early_stopping`

### 3.3 六方向怎么跑

跨物种 scVI 有两种跑法：

| 跑法 | 说明 | 任务数 | 成本 |
|---|---|---|---|
| **A. 一次训练 + 六方向评估** | 三物种一起训练一个模型 → 取潜空间 → 6 方向各自 KNN | **1 次** | ~0.1–0.3 元 |
| B. 每方向单独训练 | 每方向只训练 ref+query 两个物种 | 6 次 | ~0.6–1.8 元 |

**建议跑法 A**：成本低、与 oPCA 的「每方向独立 PCA」略有差异但可接受
（需在报告中说明：scVI 是联合训练，oPCA 是每方向独立）。

---

## 四、任务规格（待提交）

| 项 | 值 |
|---|---|
| 任务名 | `g5-scvi-cross-species-r1` |
| 镜像 | `SATURN--22`（含 scvi-tools 1.1.6.post2） |
| 资源 | 1c4g 或 2c8g（小数据，CPU 足够） |
| 输入 | `/Files/local_{human,mouse,zebrafish}_s.h5ad` + ortholog 三件 + 映射表 |
| 输出 | `./scvi-cross-<UTC>/`：metrics.json（6方向×3层 macro-F1）+ latent.npy + manifest |
| 预期时长 | 5–15 分钟（1,500 细胞/物种，max_epochs=50） |
| 费用上限 | **≤1 元** |
| 停止条件 | 非0退出 / OOM / 费用超限 → 停止，不重投 |

---

## 五、与现有方法的口径对齐（关键）

| 项 | oPCA | SATURN v99 | SAMap | **scVI（待做）** |
|---|---|---|---|---|
| 标签空间 | coarse（映射表） | 原始→coarse | 原始→coarse | **coarse（同 oPCA）** |
| 基因集 | 1:1 同源（修正后） | 全部（macrogene） | 全部（图对齐） | **1:1 同源（同 oPCA）** |
| 表示 | PCA-50 | 1000-dim macrogene | 图嵌入 | **scVI latent-10** |
| 训练 | 每方向独立 PCA | 一次训练（transductive） | 一次建图 | **一次训练（transductive）** |
| 评估 | KNN15 cosine | KNN15 cosine | 同 | **KNN15 cosine（同）** |
| 指标 | accuracy + **macro-F1** | 同 | 同 | **macro-F1（主）** |

**限定**：scVI 与 SATURN 都是「一次训练、多方向评估」，而 oPCA 是「每方向独立 PCA」。
这个差异必须在报告中披露，不能直接排名。

---

## 六、待决策

| # | 事项 | 需要谁 |
|---|---|---|
| 1 | 是否批准提交 scVI 任务（≤1 元） | 用户 |
| 2 | 跑法 A（1 次）还是 B（6 次） | 用户/执行者建议 A |
| 3 | 是否同时补 kBET/iLISI（可在同一次任务里算） | 用户 |

---

## 七、边界

- 本文件为**设计文档**，未运行任何 scVI 代码
- 未安装 torch/scvi 到本地（遵守「运算走 DCS」）
- 未提交任何 DCS 任务
