# 报告 14：映射换代（v1→v2）对 coarse 指标的影响与影响面盘点（2026-11-11）

> 起因：`docs/reports/report-12-full-recap-20261110.md` §7 留了一条待办——
> 「镜像内 6 值复现的口径标注：镜像里嵌的是 **v1** 映射；换 v2 需重跑或标注」。
> 本文把这条待办做到可闭环：**量出影响、给出现行数值、并发现影响面比原以为的更大**。

---

## 一、一句话结论

1. 镜像内嵌映射**就是 v1**（与 `config/heart-celltype-map-v1.tsv` 内容差异 0 条）；
   镜像里 6/6 复现的那 6 个 accuracy，**是 v1 口径的数**。
2. **本地重跑已复现 v1 的 6 个冻结值（6/6 逐位一致）**，复算链成立。
3. **v2 签认表下，四个斑马鱼方向数值全部变化**，其中 `斑马鱼→人` 由 0.1734 → **0.2788**（+0.1054）。
4. **换代影响的不是只有镜像那条证据**：scVI 的 `人→斑马鱼` / `鼠→斑马鱼` 两向分母也仍是 v1 的 1499，
   而 scVI **无法事后换算**（见 §五），需要重跑原流程。
5. SATURN 已有 v2 版（`saturn_convention_mapv2.json`），不受此待办影响。

---

## 二、镜像嵌的映射 = v1（证据）

| 项 | 值 |
|---|---|
| 文件 | `scripts/v99_mapping_embedded.json`（3,160 B） |
| sha256 | `d92e32aa788672492febe8cd428beac71ba69fd99df68c7f362cba2e553eea4a` |
| 与产物 manifest 对拍 | ✅ 等于 `results/phase-20261010/opca-fixkey-recovered-20261015/manifest.json` 的 `mapping_sha256` |
| 内容 vs `config/heart-celltype-map-v1.tsv` | **差异 0 条**（38 行逐行同值） |
| 内容 vs `config/heart-celltype-map-v2.tsv` | **差异 1 条**：`zebrafish|Orthers` → `(neural, active)` 改为 `(unresolved)` |

复算命令：`python scripts/opca_mapping_convention_audit.py`

---

## 三、镜像内那 6 个值的口径（说清楚，别含糊）

冻结值 = 产物 `included=True` 子集上的 accuracy：

| 方向 | 冻结 acc | 分母 | 总细胞 | 剔除 |
|---|---|---|---|---|
| 人→鼠 | 0.8618 | 1505 | 1535 | 30 |
| 鼠→人 | 0.7369 | 1528 | 1528 | 0 |
| 人→斑马鱼 | 0.1795 | 1499 | 1543 | 44 |
| 斑马鱼→人 | 0.1734 | 1528 | 1528 | 0 |
| 鼠→斑马鱼 | 0.2675 | 1499 | 1543 | 44 |
| 斑马鱼→鼠 | 0.5814 | 1505 | 1535 | 30 |

被剔除的细胞统一是 `exclusion_reason == "inactive"` 且 `truth == "other"`，
即**真值侧**不在粗类空间（`Proliferating cell` / `mt` 这类 `mapping_status != active` 的行）。

**性质判定（重要）**：这是**真值侧**剔除。与 SATURN 当年「不可映射的**预测**被丢弃、
细胞同时退出分母」那种「按预测结果筛样本」**不是同一回事**，属合理剔除。

---

## 四、v1 → v2：oPCA 的实测影响（已重跑，非推算）

**重跑环境**：`.venv39`（python 3.9.6 / numpy 1.23.5 / sklearn 1.6.1 / anndata 0.10.9），
7 个输入与 manifest **逐位一致**（三份 h5ad + 三份同源文件 + 映射表），各跑 30.8 s。

| 方向 | 冻结（v1） | **v2 实测** | Δacc | 分母 v1→v2（评估侧） |
|---|---|---|---|---|
| 人→鼠 | 0.8618 | 0.8618 | 0 | 1505 → 1505 |
| 鼠→人 | 0.7369 | 0.7369 | 0 | 1528 → 1528 |
| 人→斑马鱼 | 0.1795 | **0.1811** | +0.0016 | 1499 → **1469** |
| 斑马鱼→人 | 0.1734 | **0.2788** | **+0.1054** | 1528 → 1528 |
| 鼠→斑马鱼 | 0.2675 | **0.2730** | +0.0055 | 1499 → **1469** |
| 斑马鱼→鼠 | 0.5814 | **0.5967** | +0.0153 | 1505 → 1505 |

产物：`results/mapping-v2-20261111/rerun-v1/`（`be985735…` 映射，**6/6 命中冻结值**）
与 `rerun-v2/`（`01a43952…` 映射）。

### `斑马鱼→人` 为什么涨这么多（机制，已查到格级）

对比两版混淆矩阵：

| 格子 | v1 | v2 |
|---|---|---|
| `cardiomyocyte=>neural` | 456 | **0** |
| `fibroblast=>neural` | 252 | **0** |
| `smooth_muscle=>neural` | 161 | **0** |
| `immune=>neural` | 113 | **0** |
| `endothelial=>neural` | 106 | **0** |
| `adipocyte=>neural` | 29 | **0** |
| `epicardial=>neural` | 20 | **0** |
| `neural=>neural` | 27 | **0** |

**机制**：`zebrafish|Orthers` 是斑马鱼词表里**唯一**映射到 `neural` 的行。
v1 下它在训练集里造出一个 `neural` 类，KNN 于是把人的大量细胞预测成 `neural`
（合计约 1137 格，几乎全错）；v2 把它判为 `unresolved` 后，斑马鱼参考集**不再有 neural 训练样本**，
`neural` 从预测空间消失，那一片错误预测被重新分配 → 准确率上升。

**一句话**：v1 里 `斑马鱼→人` 的低分，很大程度是被一个拼写错误的类别（`Orthers` ← `Others`）拖出来的。

---

## 五、影响面比原待办更大：scVI 也有两个方向挂在 v1 分母上

### 5.1 scVI 的分母现状

数据源 `results/bootstrap-20261030/bootstrap.json` / `scvi-cross-species/recomputed_union.json`：

| 方向 | scVI acc（现行） | n_q |
|---|---|---|
| 人→斑马鱼 | 0.6217 | **1499** |
| 鼠→斑马鱼 | 0.6338 | **1499** |

`1499` 正是 v1 口径（含 30 个 `Orthers` 真值细胞）。v2 下应为 **1469**。
→ **scVI 这两向的 accuracy / macro-F1 都是 v1 口径，尚未重算。**

### 5.2 但 scVI 不能事后换算（已验证）

我试过「用 v2 表把 scVI 的 exact 层预测重新映射」，**前提不成立**：

| 方向 | `coarse预测 == map(exact预测)` 吻合率 |
|---|---|
| 人→鼠 | 1497/1505 |
| 鼠→人 | 1504/1528 |
| 人→斑马鱼 | 1441/1499 |
| 斑马鱼→人 | 1406/1528 |
| 鼠→斑马鱼 | 1417/1499 |
| 斑马鱼→鼠 | 1429/1505 |

用这套重算出来的 v1 值只能对上冻结值 **1/6** →
**scVI 的 coarse 层与 oPCA 一样，是独立于 exact 层产出的**，不能由逐细胞预测反推。

复算命令：`python scripts/scvi_mapping_v1_v2_audit.py`

### 5.3 对 oPCA 的同类判据

`scripts/ortholog_pca_dcs_v3_fixkey.py:285-291` 显示，coarse 层是**在粗类标签空间里另跑一次 KNN**
（`knn.fit(Z[m_s][keep_r], ytr[keep_r])`），不是把 exact 预测映射一遍。
所以换代**只能整条重跑**——这正是原文「需重跑或标注」的技术原因。

---

## 六、结论会不会变（已核对，未翻转）

拿**同口径**比（不能拿 oPCA 的 acc 去比 scVI 的 macro-F1，我先前差点犯这个错）：

| 方向 | oPCA v2 acc | scVI acc | 胜者 |
|---|---|---|---|
| 人→斑马鱼 | 0.1811 | 0.6217 | scVI |
| 斑马鱼→人 | 0.2788 | 0.6479 | scVI |
| 鼠→斑马鱼 | 0.2730 | 0.6338 | scVI |
| 斑马鱼→鼠 | 0.5967 | 0.8020 | scVI |

**「远缘（鱼四向）统一选 scVI」不变。**
但要注意 scVI 两向仍是 v1 分母，**等 scVI 按 v2 重算后才能出最终版对照表**；
按本次 oPCA 的观察（v2 让 oPCA 的斑马鱼向普遍+0.002…+0.105），scVI 也可能小幅移动，
不过 `0.62–0.80` 对 `0.18–0.60` 的差距远大于任何 SE，**预期不翻转**（此句为预期，非结论）。

---

## 七、这次改了什么 / 还差什么

### 已产出

| 文件 | 内容 |
|---|---|
| `scripts/opca_mapping_convention_audit.py` | v99/v1/v2 三表对比 + oPCA 口径判定 |
| `scripts/scvi_mapping_v1_v2_audit.py` | scVI 前提检验 + v1/v2 对照（并证明不能换算） |
| `results/mapping-v2-20261111/rerun-v1/` | **v1 重跑产物，6/6 命中冻结值（验证件）** |
| `results/mapping-v2-20261111/rerun-v2/` | **v2 重跑产物（要的新数）** |
| `results/mapping-v2-20261111/opca_mapping_convention_audit.json` | 口径判定与差异清单 |
| `results/mapping-v2-20261111/scvi_v1_vs_v2.json` | scVI 前提检验记录 |

### 还差（下一步，可执行）

1. **scVI 按 v2 重跑**：需要原 scVI 流程（`scripts/scvi_cross_species.py`）与对应输入；
   跑完把 `人→斑马鱼` / `鼠→斑马鱼` 两向换成 v2 值，并重出对照表与选型指南。
2. **把本文结论写进现行文档**：`docs/execution/20261028-master-handoff.md` §9.4b 加口径标注；
   `docs/execution/20261108-更正索引.md` 增一节；`report-12` §7 那条待办标为已闭环。
3. 镜像内复现那条证据**保留 v1 口径不改**——因为镜像里嵌的就是 v1，
   改数会导致「证据与镜像不符」；正确做法是**在镜像里补跑一次 v2**，
   或明确标注「本条证据对应 v1 映射」。

---

## 八、钉住的三条纪律（沿用）

1. 不把 transductive 写成 held-out / inductive；
2. 不按总分排冠军，只做「场景 → 方法」；
3. 任何 macro-F1 引用必须带「union 口径 + 分母 + strict_cell」。

另加一条本题专属：**跨方法比数必须同口径同指标**——
本次差点用 oPCA 的 accuracy 去比 scVI 的 macro-F1 得出「oPCA 反超」的错误结论。
