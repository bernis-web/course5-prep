# 汇报 2/10：数字来源链（2026-10-08）

> 主题：一个百分比是怎样得到的——从原始细胞到表格单元格的完整可复核路径。
> 本稿数字以三份冻结 metrics.json 为主源（0.6179 为日志级、E[null] 为推导值，均已逐处标注），并经本地独立复算验证。
> 口径：全部为 transductive/in-sample 重评估；单 seed（0）；K=15 cosine 倒距离加权。

---

## 第 1 节：为什么不能只报一个百分比

一个准确率不是方法的固有属性，而是下面六个因素共同作用的结果：

```
方法 + 表示层 + 标签空间 + query/reference 角色 + 排除规则 + 分母
```

同一个嵌入、同一批细胞，只要换掉其中任何一项，数字就会变。本阶段的目标不是再报一个更高的分数，而是让听众能沿着文件、公式和 SHA 把每个数字复核一遍。

**通用来源链**：

```
原始 h5ad
  ↓ normalize_total(1e4) + log1p（等价 log1p(CPM/100)，全基因空间）
  ↓ 表示层：ortholog 交集+PCA50 / ESM2+macrogenes / SAMap 同源图
  ↓ query / reference 角色划分（src=reference 拟合，tgt=query 预测）
  ↓ KNN15 cosine 倒距离加权
  ↓ 逐细胞预测（含 confidence 与 exclusion_reason）
  ↓ mapping_status 排除（coarse/fine 层）
  ↓ correct / eligible（n_q）
  ↓ metrics.json
  ↓ SHA-256 锚定
  ↓ 汇报表格
```

**四个必须并列报告的量**：

| 量 | 定义 | 为什么必须报 |
|---|---|---|
| accuracy | correct / n_q | 主指标 |
| n_q / coverage | 进入分母的细胞数 / n_q ÷ query 总数 | 排除规则改变了分母 |
| majority | 最大真值类占比 | 无信息基线 |
| shuffle_p | 预测向量置换检验 | 仅回答"是否优于随机预测"，不是多数类检验 |

---

## 第 2 节：ortholog-PCA 人→鼠 coarse = 86.18%

**完整算式链**（每一步可复算）：

| 步骤 | 内容 | 值 |
|---|---|---|
| 输入 | reference = 人；query = 鼠 | 1,528 / 1,535 细胞 |
| 归一化 | normalize_total(1e4) + log1p，全基因空间 | 等价 log1p(CPM/100) |
| 同源基因 | 人鼠 1:1 直系同源交集 | **15,869** 基因 |
| 表示层 | 人+鼠联合 PCA-50（seed 0，transductive） | 3,063 × 50 |
| 评分 | KNN15，cosine，倒距离加权 | k=15 |
| 排除 | 鼠侧 status≠active（Proliferating cell） | 剔 30 |
| eligible query | 1,535 − 30 | **n_q = 1,505** |
| 正确数 | 逐细胞预测 == 真值 | **1,297** |
| **accuracy** | 1,297 ÷ 1,505 | **0.8618** |
| coverage | 1,505 ÷ 1,535 | 0.9805 |
| majority | 鼠 coarse 最大真值类占比 | 0.4817 |
| shuffle_p | 200 次 RandomState(0) 洗牌 | 0.0 |
| 输出 | results/pilot-v1/ortholog-pca-v98/metrics.json | SHA b2b3ac6b…c725 |

**要强调的一句话**：86.18% = 正确预测数 ÷ 排除后仍有资格进入分母的 query 细胞数。不是从表里抄出来的。

**逐类分解（confusion 摘录）**：内皮 720/725 正确、成纤维 255/360、免疫 197/202、心肌 19/47 —— 主要类别命中率高；跨类错误集中在成纤维→平滑肌（82）与心肌→内皮（27）。

---

## 第 3 节：SATURN 的三个数字必须分开报告

SATURN 在不同协议下有三个数字，**任何一个单独出现都是不完整的**：

| 数字 | 口径 | 标签空间 | 分母 | 证据等级 |
|---|---|---|---|---|
| **0.6179** | v97g 评分器 | mapped-space（映射后粗类） | coverage_q 0.9805 → n_q ≈ 1,505（日志级） | confirmed（日志级） |
| **0.4749** | v99 统一评分器 | exact（原始标签） | n_q = 1,535 | candidate（provenance confirmed） |
| **0.4844** | v99 统一评分器 | coarse（原始标签+status 过滤） | n_q = 1,505 | candidate（provenance confirmed） |

**为什么 0.4749 和 0.4844 不同——分母效应的实证**：

本地独立复算（从 v99 恢复的逐细胞载荷，1535 行）：

```
exact 层：  1,535 个 query 全部计分，正确 729  →  729 / 1535 = 0.4749
排除的 30 个增殖细胞：正确 0 / 30（全部预测错误）
coarse 层：剔 30 后 1,505 个 query 计分，正确仍 729  →  729 / 1505 = 0.4844
```

**正确数完全相同（729）**，accuracy 却升高了——因为被排除的 30 个细胞全部是错的。这说明：

> 排除规则本身就会改变准确率。引用任何 acc 必须并列 n_q 与 coverage，否则两个数字无法比较。

**v97g 的 0.6179 与 v99 的关系**：两者是同一批 SATURN 嵌入（obsm/macrogenes）在**不同评分器+不同标签空间**下的结果，不是"同一个指标的两次测量"。不能写成"SATURN 从 61.79% 降到 48.44%"。v97g 无逐细胞文件，为日志级证据；v99 有完整 46 文件树 provenance。

---

## 第 4 节：SAMap WDL 人→鼠 coarse = 10.50%

| 步骤 | 内容 | 值 |
|---|---|---|
| 运行通道 | WDL 流程任务 | W202610050003104 |
| 实际运行脚本 | 410 行版（**非** Phase 5 修复版） | script_sha256 c0f05b89…3807 |
| 依赖栈 | 预建 pylibs（samap 1.0.16 + samalg 1.0.2 + hnswlib shim） | 复用，非重装 |
| 预处理 | cell_median 归一化 + log + StandardScaler(npcs=100) | k=20 |
| 联合对齐 | SAMAP(keys=cell_type) 同源基因图，NUMITERS=3 | label-aware |
| 评分 | KNN15 cosine 倒距离加权（与 v99 同评分器） | — |
| reference / query | 人 1,528 / 鼠 1,535 | — |
| 排除 | 鼠侧 status≠active | 剔 30 → n_q = 1,505 |
| 正确数 | 逐细胞预测 == 真值 | **158** |
| **accuracy** | 158 ÷ 1,505 | **0.1050** |
| majority | 鼠 coarse 最大类 | 0.4618 |
| 输出 | results/pilot-v1/samap-v98/wdl-run/extracted/metrics.json | SHA 3c719399…954f |

**两个必须声明的限制**：

1. **label-aware**：`keys=cell_type` 使真值标签参与联合图构建——这是 SAMap 的原生工作流，但意味着它不是 label-free 方法，与 ortholog-PCA 不可直接互比；
2. **脚本版本**：本次成功复现使用的是 WDL 实际运行脚本（410 行版），Phase 5 修复版（0a2063d3）在 WDL 环境下未运行——不能把两者说成同一次运行。

**读数**：0.1050 远低于多数类 0.4618，且 confusion 显示预测大量塌缩到单一类别（内皮 695 个中 634 个被预测为 Lymphoid，占 91.2%）——不是"接近随机"，而是"系统性错位"。

**per_cell 旗标口径警示**：SAMap per_cell 的 `included` 旗标用的是"truth∈参考标签集"定义（1,398），与 n_q（1,505）口径不同且不参与 acc 计算——复算请按全部 query 行的 correct/n_q，若误用 included 旗标会得到 158/1398 = 0.113 而非 0.1050（脚本 md5 56bb6035 混合口径，见 Phase 6 关账 §四）。

---

## 第 5 节：斑马鱼方向为什么低于多数类

以 ortholog-PCA 人→斑马鱼 coarse 为例：

| 量 | 值 |
|---|---|
| query / reference | 鱼 1,543 / 人 1,528 |
| 同源基因 | 人鱼 1:1 = 9,131 |
| 排除 | 鱼侧 status≠active（mt 30 + Proliferating 14）= 44 |
| n_q | 1,543 − 44 = **1,499** |
| coverage | 1,499 ÷ 1,543 = 0.9715 |
| 正确数 | **294** |
| accuracy | 294 ÷ 1,499 = **0.1961** |
| majority | **0.3976** |
| shuffle_p | 0.0 |

**两个数字的正确读法**：

- `accuracy 0.1961 < majority 0.3976` → 该方向**没有可靠的类别迁移优势**（低于"全猜最大类"）；
- `shuffle_p = 0.0` → 只说明它**优于"随机洗牌预测向量"的零分布**（E[null]≈0.10；200 次置换 0.089–0.117），**不能**读成"优于多数类"。

**confusion 证据**：鱼红细胞 287/332 被预测为 immune、内皮 509/596 预测为 immune、平滑肌 68/166 预测为 immune——跨物种错误是系统性的，不是噪声。

**单 seed 提示**：斑马鱼方向全部为单 seed（0）点估计，且鱼方向 seed 双峰已证实——本页数字不应读作该方向的稳定值。

---

## 第 6 节：数字来源追踪图（一页图）

```
local_*.h5ad（1528 / 1535 / 1543）
        ↓  normalize_total(1e4) + log1p
        ↓  三种表示层
   ┌────────────┬──────────────────┬─────────────────┐
   │ ortholog   │ SATURN           │ SAMap           │
   │ 1:1 ortho  │ ESM2 → macrogene │ 同源基因图       │
   │ +PCA50     │ 联合训练          │ +keys=cell_type │
   └────────────┴──────────────────┴─────────────────┘
        ↓  KNN15 / cosine / 倒距离加权
        ↓  mapping_status 排除（coarse/fine）
        ↓  prediction table + confusion matrix
        ↓  metrics.json
        ↓  SHA-256
        ↓  汇报表格
```

**四个 SHA 锚点**：

| 产物 | SHA-256 |
|---|---|
| ortholog-PCA metrics | `b2b3ac6bc37c410841bdcbbd968159246e1990db47d02b8fa11844527d66c725` |
| SAMap WDL metrics | `3c7193999f489017e4227bff2dc83667b63a564a97a373373f6239328ae4954f` |
| v99 metrics | `d1081cfd2489bf2afd30af7706fadf2d08b90390c26d38a766ea97b54b3dc261` |
| 冻结映射表 v1 | `be9857354778535b76d1884d004c54691dc5ff2daa7b098d71dc719daf583165` |

---

## 第 7 节：复核清单——听众可以自己验

| 想验什么 | 怎么做 |
|---|---|
| ortholog-PCA 某方向数字 | 读 metrics.json → 对照 predictions/ 与 confusion/（18 份全在本地） |
| SAMap 某方向数字 | 读 extracted/metrics.json 的 per_cell → 按**全部 query 行**重算 correct/n_q（勿用 included 旗标，见 §4 警示） |
| v99 数字 | 用 SHA d1081cfd 定位 metrics.json；逐细胞载荷在 payloads/（6 份） |
| 排除规则 | config/heart-celltype-map-v1.tsv（38 行，SHA be985735）的 mapping_status 列 |
| 评分器定义 | scripts/ortholog_pca_local_v1.py（K=15、cosine、倒距离、200 置换） |

---

## 第 8 节：本阶段结论与边界

**结论**：

1. 每个百分比都能沿"输入 → 表示层 → 角色 → 评分 → 排除 → 分母 → SHA"完整回溯；
2. 分母效应真实存在且可量化（v99 exact 0.4749 → coarse 0.4844，正确数不变）；
3. 三个方法的数字**不可直接互比**：标签空间（映射词汇 vs 原始标签）、label-free vs label-aware、评分器（v97g vs v99）三重差异；
4. 所有结果仍为 **transductive/in-sample**，不支持 inductive 泛化结论。

**边界（不能从本阶段推出什么）**：

- 不能推出"哪个方法普遍更好"——协议不同；
- 不能把 61.79% 与 48.44% 合并成一个 SATURN 成绩；
- 不能把 shuffle_p 当作多数类显著性；
- 不能把 v97g 的日志级数字当作文件级证据。

**本阶段未完成**：

- SATURN v97g 的逐细胞文件仍缺失（日志级）；如需文件级，需重跑 v97g 评分器（属新任务，需批准）；
- mapping v1 仍待导师人工签认（needs-reviewer）。

**下一阶段**：汇报 3——三方法公平比较边界（协议差异表、能回答/不能回答的问题清单）。

---

## 附：本稿数字来源

| 数字 | 来源文件 | 验证方式 |
|---|---|---|
| 0.8618 / 1297 / 1505 | ortholog-pca-v98/metrics.json + predictions/ | 本地逐细胞重算 ✓ |
| 0.1961 / 294 / 1499 | 同上（human->zebrafish.coarse） | 本地逐细胞重算 ✓ |
| 0.6179 | v74 证据文档（EVAL3G 日志） | 日志级，无逐细胞文件 |
| 0.4749 / 729 / 1535 | v99 metrics.json + 恢复载荷 p6 | 本地逐细胞重算 ✓ |
| 0.4844 / 729 / 1505 | 同上（排除 30 后） | 本地逐细胞重算 ✓（30 个被排除细胞正确数 0/30） |
| 0.1050 / 158 / 1505 | samap-v98/extracted/metrics.json | 本地 per_cell 重算 ✓ |
