# 统一 coarse 标签空间 macro-F1 重算报告（2026-10-17）

> **零算力重算**：只使用现有冻结的 confusion / per_cell，不跑任何模型。
> 依据 Claude 2026-10-17 咨询结论：三方法原本在不同标签空间与分母上报告 accuracy，
> 主表把不可比的数字并列，然后以"不可直接排名"作为结论——**这是待修的缺陷，不是结论**。
> 脚本：`scripts/unified_coarse_macro_f1.py`
> 产物：`results/phase-20261017/unified-coarse-macro-f1/`

---

## 一、最重要的发现：4 个结论翻转

把三方法统一映射到 `config/heart-celltype-map-v1.tsv` 的 `coarse_level` 后重算，
**有 4 处"是否高于多数类基线"的判定发生翻转**：

| 方向 | 方法 | accuracy 判定 | **macro-F1 判定** | 翻转 |
|---|---|---|---|---|
| human→zebrafish | ortholog-PCA | below | **ABOVE** | ⚠️ **翻转** |
| human→zebrafish | SATURN v99 | below | **ABOVE** | ⚠️ **翻转** |
| zebrafish→human | ortholog-PCA | below | **ABOVE** | ⚠️ **翻转** |
| mouse→zebrafish | ortholog-PCA | below | **ABOVE** | ⚠️ **翻转** |

**为什么翻转**：多数类分类器在 accuracy 下能拿到高分（如 0.4817），但在 macro-F1 下
所有少数类的 F1 都是 0，macro-F1 只有约 0.08。方法只要在少数类上有一点正确率，
macro-F1 就超过基线——即使 accuracy 低于基线。

**这意味着**：此前"含斑马鱼方向普遍低于多数类基线"的负结论，**主要是度量选择造成的假象**。

---

## 二、完整结果（统一 coarse 空间）

### 2.1 macro-F1（主表，课程要求指标）

| 方向 | ortholog-PCA | SATURN v99 | SAMap |
|---|---|---|---|
| human→mouse | **0.6435** | 0.4147 | 0.1127 |
| mouse→human | **0.6729** | 0.4010 | 0.0401 |
| human→zebrafish | 0.1682 | **0.2479** | 0.0477 |
| zebrafish→human | 0.1585 | **0.4021** | n/a (n=0) |
| mouse→zebrafish | 0.2314 | **0.6500** | n/a (n=1) |
| zebrafish→mouse | 0.4396 | **0.6510** | n/a (n=0) |

### 2.2 多数类基线（macro-F1）

| 方向 | majority macro-F1 | majority accuracy |
|---|---|---|
| human→mouse | 0.0813 | 0.4817 |
| mouse→human | 0.0594 | 0.3115 |
| human→zebrafish | 0.0711 | 0.3976 |
| zebrafish→human | 0.0594 | 0.3115 |
| mouse→zebrafish | 0.0711 | 0.3976 |
| zebrafish→mouse | 0.0813 | 0.4817 |

**对照**：majority 的 accuracy 是 0.31–0.48，但 macro-F1 只有 0.06–0.08。
这正是"换指标后结论翻转"的机制。

### 2.3 accuracy（附录用，非主表）

| 方向 | ortholog-PCA | SATURN v99 | SAMap |
|---|---|---|---|
| human→mouse | 0.8618 | 0.6241 | 0.1689 |
| mouse→human | 0.7369 | 0.3734 | 0.1368 |
| human→zebrafish | 0.1961 | 0.2190 | 0.1197 |
| zebrafish→human | 0.1813 | 0.5047 | n/a |
| mouse→zebrafish | 0.2755 | 0.6863 | n/a |
| zebrafish→mouse | 0.5761 | 0.6875 | n/a |

---

## 三、必须同时披露的限定（否则会变成新的过度结论）

### 3.1 样本量差异极大

| 方向 | oPCA n | SATURN n | SAMap n |
|---|---|---|---|
| human→mouse | 1505 | 1309 | 1368 |
| mouse→human | 1528 | **857** | **307** |
| human→zebrafish | 1499 | **1032** | **986** |
| zebrafish→human | 1528 | **642** | **0** |
| mouse→zebrafish | 1499 | **459** | **1** |
| zebrafish→mouse | 1505 | **912** | **0** |

**SAMap 在 3 个方向 n≈0，无法计算**；SATURN 覆盖率只有 oPCA 的 30%–87%。
→ **不能直接按 macro-F1 排序**，因为分母不同。

### 3.2 标签空间统一后的剩余不可比

- oPCA 的 confusion **原生就是 coarse 空间**（来自映射表）
- SATURN v99 / SAMap 的 per_cell 是**原始标签**，经映射表转换到 coarse
- 转换过程中被排除的细胞（无映射行 / status≠active）计入 `n` 的损失
- **这解释了样本量差异的主要来源**——不是方法本身"少预测了"，而是标签映射覆盖不同

### 3.3 仍是 transductive / in-sample

所有数字仍是同批数据上的标签迁移，不是留出评估，不能解释为泛化能力。

---

## 四、对既有结论的影响

| 既有结论 | 新判定 |
|---|---|
| "ortholog-PCA 在人-鼠方向表现良好" | ✅ 保持（macro-F1 0.64/0.67） |
| "含斑马鱼方向普遍低于多数类基线" | ❌ **推翻**（4 格翻转，改用 macro-F1 后高于基线） |
| "SAMap 无跨物种信号" | ✅ 保持（macro-F1 0.04–0.11，低于基线） |
| "鱼→鼠是唯一接近基线的鱼方向" | ❌ **需重述**（改用 macro-F1 后，SATURN 在鱼→鼠达 0.65） |
| "三方法不可直接比较" | ⚠️ **降级**：统一标签空间后可以比较，但需并列 n 与覆盖率 |

---

## 五、边界声明

- **零算力**：未运行任何模型，仅读取冻结的 confusion/per_cell 重算
- 未修改任何冻结件（`results/pilot-v1` 零触碰）
- 产物写入新目录 `results/phase-20261017/unified-coarse-macro-f1/`
- 未提交任何 DCS 任务
- 原始数据来源：`results/pilot-v1/ortholog-pca-v98/confusion/`、
  `results/pilot-v1/saturn-v99/raw/recovered-20261001/`、
  `results/pilot-v1/samap-v98/wdl-run/extracted/`
