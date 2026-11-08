# scVI 跨物种臂：运行结果与核对（2026-10-19）

> 任务 `W202610190042919`（流程 `scvi_cross2` v1.0.0）已完成并成功回收全部产物。
> 本文所有数字来自平台产物与本地独立重算，不采信任何转述。

---

## 一、任务与环境

| 项 | 值 |
|---|---|
| 任务号 | `W202610190042919` |
| 实体 ID | `scvi-run-20261019` |
| 流程 | `scvi_cross2` v1.0.0（本次新建；未修改 `opca_v2`） |
| 终态 | **完成**（`STAGE_DONE`） |
| 总时长 | 28m 40s（含排队） |
| 实际计算 | CPU 0.142 h ≈ 8.5 min，峰值内存 2.37 GB，IO 2.21 GB |
| 费用 | ¥0.0x（1 元上限内） |

**运行环境（脚本自记）**

| 包 | 版本 |
|---|---|
| python | 3.9 |
| torch | **2.6.0+cu124**（镜像自带） |
| scvi-tools | **1.1.6.post2**（镜像自带） |
| anndata | **0.10.8**（镜像自带，已排除 pylibs 的旧版） |
| scanpy | 1.9.3（pylibs） |
| numpy | 1.23.5（pylibs） |
| scikit-learn | 1.6.1 |

**数据规模**：human 1,528 / mouse 1,535 / zebrafish 1,543 = 4,606 细胞；共同 human 基因轴 **9,018**。

**协议**：`transductive_formal_reassessment`，seed=0，K=15，cosine，200 次置换，n_latent=10，max_epochs=50，early_stopping。

---

## 二、核对结果

### 2.1 准确率：18/18 完全一致

从 18 个 `predictions/*.json` 逐细胞重算 accuracy，与 `metrics.json` 的 `acc` **逐格完全相等**（差 < 1e-4）。

### 2.2 macro-F1：口径差异（重要）

| 口径 | 定义 | 使用者 |
|---|---|---|
| **truth-only** | `sorted(set(y_true))` | 平台 scVI 脚本（`metrics.json` 里的 `macro_f1`） |
| **union** | `sorted(set(y_true) \| set(y_pred))` | `scripts/unified_coarse_macro_f1.py`（此前给 oPCA / SATURN / SAMap 重算时用的） |

两者在「预测中出现、真实标签中不存在的类」上不同：truth-only 忽略这些类，union 给它们记 F1=0。

**因此 `metrics.json` 的 `macro_f1` 不能直接与另外三个方法的统一重算值并列。**
本文所有跨方法对比一律使用 **union 口径**（从 18 个预测文件独立重算，结果见 `recomputed_union.json`）。

---

## 三、18 格完整结果

下表 `acc` 与 `mf1_union` 均为**本地从逐细胞预测独立重算**；`mf1_truth` 为平台 `metrics.json` 原值（仅供追溯）。

| 方向 | 层级 | acc | macro-F1 (union) | macro-F1 (truth-only) | n | 多数类基线 | 置换 p |
|---|---|---|---|---|---|---|---|
| human→mouse | exact | 0.8241 | 0.3421 | 0.4276 | 1528 | 0.4528 | 0.0000 |
| human→mouse | coarse | 0.9189 | **0.6683** | 0.6683 | 1505 | 0.4817 | 0.0000 |
| human→mouse | fine | 0.8405 | 0.3688 | 0.4694 | 1505 | 0.4618 | 0.0000 |
| mouse→human | exact | 0.5419 | 0.2777 | 0.3703 | 1528 | 0.2526 | 0.0000 |
| mouse→human | coarse | 0.7781 | **0.5895** | 0.5895 | 1528 | 0.3115 | 0.0000 |
| mouse→human | fine | 0.5438 | 0.2966 | 0.3708 | 1528 | 0.2526 | 0.0000 |
| human→zebrafish | exact | 0.5133 | 0.2033 | 0.2759 | 1499 | 0.3863 | 0.0000 |
| human→zebrafish | coarse | 0.6217 | **0.4014** | 0.4516 | 1499 | 0.3976 | 0.0000 |
| human→zebrafish | fine | 0.5457 | 0.2735 | 0.3730 | 1499 | 0.3976 | 0.0000 |
| zebrafish→human | exact | 0.4581 | 0.2120 | 0.3356 | 1528 | 0.2526 | 0.0000 |
| zebrafish→human | coarse | 0.6479 | **0.4290** | 0.4826 | 1528 | 0.3115 | 0.0000 |
| zebrafish→human | fine | 0.4980 | 0.2875 | 0.3593 | 1528 | 0.2526 | 0.0000 |
| mouse→zebrafish | exact | 0.4971 | 0.1980 | 0.2546 | 1499 | 0.3863 | 0.0000 |
| mouse→zebrafish | coarse | 0.6338 | **0.4248** | 0.4779 | 1499 | 0.3976 | 0.0000 |
| mouse→zebrafish | fine | 0.5504 | 0.2742 | 0.3490 | 1499 | 0.3976 | 0.0000 |
| zebrafish→mouse | exact | 0.6717 | 0.2193 | 0.3290 | 1505 | 0.4528 | 0.0000 |
| zebrafish→mouse | coarse | 0.8020 | **0.4786** | 0.5384 | 1505 | 0.4817 | 0.0000 |
| zebrafish→mouse | fine | 0.7056 | 0.3125 | 0.3978 | 1505 | 0.4618 | 0.0000 |

全部 18 格 `shuffle_p = 0.0000`（200 次置换均未达到实测精度）。

---

## 四、四方法并列（coarse macro-F1，union 口径）

| 方向 | **scVI** | oPCA | SATURN | SAMap |
|---|---|---|---|---|
| human→mouse | **0.6683** | 0.6435 | 0.4147 | 0.1127 |
| mouse→human | 0.5895 | **0.6729** | 0.4010 | 0.0401 |
| human→zebrafish | **0.4014** | 0.1682 | 0.2479 | 0.0477 |
| zebrafish→human | **0.4290** | 0.1585 | 0.4021 | n/a |
| mouse→zebrafish | 0.4248 | 0.2314 | **0.6500** | n/a |
| zebrafish→mouse | 0.4786 | 0.4396 | **0.6510** | n/a |

**六方向中 scVI 有 4 个方向最高**（h→m、h→z、z→h、z→m），oPCA 在 m→h 最高，SATURN 在 m→z、z→m 最高。
**没有任何方法在所有方向领先——不按单一总分排名。**

---

## 五、必须同时披露的限定

### 5.0 可比性声明（放在方法节，不要只放脚注）

**特征空间按各自方法学约束定义，不是同一数量，不做横向比较。**
可比性只限定在**输出层面**（macro-F1、批混合、结构保持）。

- scVI 的输入是**共享 human 直系同源交集 9,018 个基因**——模型架构要求跨物种基因一一对齐，
  取交集是保守标准做法；
- ortholog-PCA **每个方向独立**使用该方向的物种基因集（h↔m 15,869 / h↔z 9,311 / m↔z 8,160），
  PCA 是各自的 SVD，不需要共享轴，因此保留了物种特异信号。

这两个数字**不应并排出现在同一张"基因数"表里**，否则会被读成"scVI 信息量更少"。

### 5.1 其余限定

1. **transductive，不是 held-out 也不是 inductive**：scVI 在三物种全部细胞上联合训练（`batch_key="species"`），query 细胞参与了表征学习；评估时 KNN 只在 reference 的标签上拟合。这与 SATURN 的做法同类，但**与"留出物种"的设定不同**。
2. **样本量不一致**：scVI 每方向 n≈1,499–1,528；oPCA 1,499–1,528；SATURN 459–1,309；SAMap 0–1,368。scVI 使用了最完整的数据，跨方法比较需带此限定。
3. **基因轴不同**：见 5.0。
4. **macro-F1 口径**：平台 `metrics.json` 用 truth-only（`set(y_true)`），本报告跨方法表统一用 union 口径独立重算；两个口径**不能混用**。这条与 5.0 属于同一段"可比性声明"，应一起交代。
5. **单次运行**：seed=0 单次，未做多种子重复；置换检验 p=0.0000 只说明"优于随机打乱"，不说明多种子稳定性。

---

## 六、产物与文件

| 文件 | 说明 |
|---|---|
| `metrics.json`（40,371 B） | 平台原始指标（含 acc / macro_f1(truth-only) / majority / shuffle_p / confusion） |
| `predictions/*.json`（18 个） | 逐细胞预测，含 truth / prediction / included / 排除原因 |
| `latent.npy`（184,368 B） | 4,606 × 10 scVI 潜空间 |
| `manifest.json` / `environment.txt` | 输入 SHA-256、版本、参数 |
| `run.log`（22,184 B） | 完整运行日志 |
| `sha256.tsv` | 平台产物清单 |
| `recomputed_union.json` | 本地按 union 口径重算的 18 格结果 |
| `verify_recomputed_union.txt` | 重算与平台原值的逐格对照 |
| `platform_script.txt` | 平台实际执行的脚本（SHA `f894119f…`，19,796 B） |

本地产物目录：`results/phase-20261019/scvi-cross-species/`

---

## 七、边界声明

- 未修改 `opca_v2` 流程；`scvi_cross` / `scvi_cross2` 均为新建。
- 未重投失败任务；`W202610180071516`（我自己的 WDL bug）与 `W202610180071475`（误重复提交）已主动取消。
- 未在本地做任何模型运算；本地只做 JSON 读取与指标重算。
- 未读取、未记录任何 token / cookie / 密码值。
