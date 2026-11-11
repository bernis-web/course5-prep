# 报告 9：两处必须更正的硬错误（2026-11-08）

> ⚠️ **本节数字已作废（2026-11-11 标注）**：见 `docs/reports/number-index-20261111.md` 与 `docs/execution/20261108-更正索引.md`。本文件按当时口径保留，不回改。

> 本文不是复盘，是**更正**。两处错误都会改变对外引用的数字，引用旧值的地方必须一起改。
> 证据全部可从仓库内文件复算，脚本留在 `scripts/` 下。

---

## 结论先行

| # | 错误 | 影响 |
|---|---|---|
| 1 | **SATURN 评测把「真值」和「预测」的物种词表用反了** | 六个方向的 SATURN macro-F1 全部偏高；鼠↔鱼两向由 0.65 降到 **0.3658 / 0.3563**；「SATURN 在鼠↔鱼大胜」不成立 |
| 2 | **`/Files/RawData/` 里没有人/鼠/鱼三份全量数据** | 交接文档给的原始数据路径是错的；正确路径是 `/Files/3/stage3/01_raw_data/heart_omics/scrna/` |

好消息：**场景化选型指南的推荐没有翻转**，scVI 在远缘四向仍然最优。翻转的只是「SATURN 曾经赢过」这件事——它从来没赢过。

---

## 一、SATURN 评测的物种词表错误

### 1.1 错在哪

`saturation` 这条链路里（`scripts/saturn_convention_audit.py` 与产生冻结值的平台管线）对混淆矩阵两侧的标签这样映射：

```python
ct = to_coarse(source_species, truth_label)   # 真值按「源物种」查表
cp = to_coarse(target_species, pred_label)    # 预测按「目标物种」查表
```

但混淆矩阵里两侧的词表是反过来的：

| 方向文件 | 真值侧实际词表 | 预测侧实际词表 |
|---|---|---|
| `coarse_human_to_mouse.json` | Adipocyte / **Cardiomyocyte** / **Epicardium** / **Valve** … → **小鼠** | Atrial·Ventricular Cardiomyocyte / **Mast cell** / **Mesothelial cell** → **人** |
| `coarse_zebrafish_to_human.json` | Atrial·Ventricular CM / Mast / Mesothelial → **人** | **Orthers** / Epicardium / Fibroblast → **斑马鱼** |

即：**真值属于目标物种的词表，预测属于源物种的词表**（SATURN 输出的是参考书那一方的原始细胞类型）。正确写法应该是：

```python
ct = to_coarse(target_species, truth_label)
cp = to_coarse(source_species,  pred_label)
```

### 1.2 后果一：真值侧细胞被静默丢掉

`Cardiomyocyte` 是小鼠词，在人词表里查不到 → `continue`，**这批细胞在三种口径里全部消失**。
所以旧表里的 SATURN 分母是 1309 / 857 / 1032 / 642 / 459 / 912，而 oPCA、scVI 是 1499–1528。**跨方法比大小本来就不公平，根因在这里。**

### 1.3 后果二：预测侧被误判成"不可映射"

人的 `Atrial Cardiomyocyte` 在小鼠词表里查不到 → 记为不可映射 → 算进"SATURN 靠丢样本抬高分数"。`Orthers` 同样被丢弃。
**所谓「SATURN 口径偏差」，本质是这个查表 bug 制造出来的。**

### 1.4 判定实验（同一份混淆矩阵，四种约定重算）

`scripts/convention_variants.py` → `results/bootstrap-20261030/convention_variants.json`

| 方向 | 冻结值 | A 真值→源/预测→目标 | B 真值→目标/预测→源 | C 全源 | D 全目标 |
|---|---|---|---|---|---|
| 人→鼠 | 0.4147 | **0.4147** | 0.3522 | 0.2980 | 0.3089 |
| 鼠→人 | 0.4010 | **0.4010** | 0.2566 | 0.3130 | 0.2714 |
| 人→斑马鱼 | 0.2479 | **0.2479** | 0.1269 | 0.1798 | 0.1418 |
| 斑马鱼→人 | 0.4021 | **0.4021** | 0.1640 | 0.1834 | 0.2512 |
| 鼠→斑马鱼 | 0.6500 | **0.6500** | 0.3658 | 0.3913 | 0.3718 |
| 斑马鱼→鼠 | 0.6510 | **0.6510** | 0.3563 | 0.3441 | 0.4602 |

**A 复现冻结值 6/6，B/C/D 全部 0/6。** accuracy 交叉验证同样 6/6 命中 A（例如人→鼠 0.6241、鼠→斑马鱼 0.6863），说明冻结值确实是按 A 算出来的，不是巧合。

### 1.5 修正后的 SATURN 数值与可比性

`scripts/saturn_convention_audit_v2.py` → `results/bootstrap-20261030/saturn_convention_v2.json`

| 方向 | 修正后 macro-F1 | 分母 n_q | 旧值 | 虚高 |
|---|---|---|---|---|
| 人→鼠 | **0.3522** | 1505 | 0.4147 | +0.0625 |
| 鼠→人 | **0.2566** | 1528 | 0.4010 | +0.1444 |
| 人→斑马鱼 | **0.1269** | 1499 | 0.2479 | +0.1210 |
| 斑马鱼→人 | **0.1640** | 1528 | 0.4021 | +0.2381 |
| 鼠→斑马鱼 | **0.3658** | 1499 | 0.6500 | +0.2842 |
| 斑马鱼→鼠 | **0.3563** | 1505 | 0.6510 | +0.2947 |

关键变化：
1. **修正后四个方法的分母一致了**（差异只来自真值侧 unmapped 类：小鼠 Proliferating 30、斑马鱼 mt 30 + Proliferating 14）。跨方法比较第一次真正公平。
2. **SATURN 一个方向都不赢**。旧表里鼠↔鱼那两格 0.65 是 bug 造出来的。
3. 之前那套"公平口径 0.4560 / 0.4588"也是错的——它只修了预测侧丢弃，没修真值侧，仍建立在错误分母上。

### 1.6 对结论的影响

| 结论 | 是否成立 |
|---|---|
| scVI 在远缘四向最优 | **仍然成立**（0.4014 / 0.4290 / 0.4248 / 0.4786 全部高于 SATURN 与 oPCA） |
| 近缘人↔鼠 oPCA 与 scVI 基本打平 | **仍然成立**（0.6435/0.6729 vs 0.6683/0.5895），且 SATURN 0.3522 / 0.2566 明显更差 |
| 鼠↔鱼曾出现 SATURN 0.65 大胜 | **不成立**，是 bug |
| 不排总分冠军 | **仍然成立**，理由更强：分母现在一致了，但特征空间/训练方式/统计强度仍不同 |

---

## 二、DCS 平台数据路径错误

### 2.1 错在哪

旧交接文档写「原始数据在 `/Files/RawData/`：Homo_sapiens_sc.h5ad 213.38 MB / Mus_musculus_sc.h5ad 259.71 MB / Danio_rerio_sc.h5ad 153.93 MB」。

**2026-11-08 在 DCS 上实测（只读 `ls`）：`/Files/RawData/` 里没有这三个文件。**
该目录现有 11 个条目：10 个**其他物种**（Branchiostoma / Chiloscyllium / Ciona / Drosophila / Lethenteron / Patinopecten / Protopterus / Taeniopygia / Trachemys / Xenopus）+ 1 个空目录 `3_group`，owner 全是 `dcs_genpilot`，mtime 集中在 9月26日 15:47–16:09。

`/Files/RawData/` 缺了 17 物种集合里的 7 个（人、鼠、斑马鱼、Achatina_fulica、Ambystoma_mexicanum、Amphioctopus BH/SH），**不能当全量数据源**。

### 2.2 正确路径（实测字节数）

**首选**：`/Files/3/stage3/01_raw_data/heart_omics/scrna/`（owner `dcs_genpilot`，mtime 10月19日，17 物种完整）

| 文件 | 字节 | 折合 MiB |
|---|---|---|
| `Homo_sapiens_sc.h5ad` | 223,744,070 | 213.38 |
| `Mus_musculus_sc.h5ad` | 272,322,064 | 259.71 |
| `Danio_rerio_sc.h5ad` | 161,403,920 | 153.93 |

**备选**：`/Files/lamprey/Heart/Singlecell/`（owner `supp-1501539`，9月27日，同名三个文件字节数**分毫不差**，另含 6.38 GB 合并库 `sc_fordatabase.h5ad`）。

### 2.3 本项目实际用的子集（复核通过）

`/Files/` 根目录（**注意不是 RawData，也不是 Notebook 子目录**）：

| 文件 | 字节 | sha256 | 结论 |
|---|---|---|---|
| `local_human_s.h5ad` | 26,233,600 | `af41618b6941d2f1…` | 与文档一致 ✅ |
| `local_mouse_s.h5ad` | 27,745,005 | `7fda583d59d3767e…` | 一致 ✅ |
| `local_zebrafish_s.h5ad` | 16,931,148 | `6b1e8798d5f848ac…` | 一致 ✅ |

三者均由 `supp-1501539` 于 10月11日上传，是**子集**（全量的 2MB 级 vs 200MB 级），不是全量。

### 2.4 为什么会漂移

9月20日仓库记录里确实在 RawData 见过这三份（大小一致）。9月26日平台账户往 RawData 批量写入 10 个其他物种，此后该目录不再包含人/鼠/鱼。文件系统不保留删除日志，**「被移走」还是「原本就在别处」无法 100% 判定**，但可以确定：

- 现在 RawData 里没有；
- 全量文件在 `3/stage3/scrna` 与 `lamprey/Heart/Singlecell` 两处完好；
- 交接文档必须改路径，否则新人第一步就卡死。

---

## 三、复算命令（任何人可复核）

```bash
# 1) 词表归属判定实验：看哪种约定能复现冻结值
python scripts/convention_variants.py

# 2) 修正方向后重算三口径
python scripts/saturn_convention_audit_v2.py

# 3) 旧脚本（保留作对照，勿再引用其结论）
python scripts/saturn_convention_audit.py
```

产物：
- `results/bootstrap-20261030/convention_variants.json`
- `results/bootstrap-20261030/saturn_convention_v2.json`
- `results/bootstrap-20261030/saturn_convention.json`（v1，**已作废**）

---

## 四、还要跟着改的地方（清单）

| 文件 | 要改什么 |
|---|---|
| `deliverables/场景化选型指南-v6-20261027.md` | 不改推荐，但「SATURN 在鼠↔鱼曾领先」的表述必须删；需出 v7 |
| `docs/execution/20261028-master-handoff.md` §2 表下的 † 注 | 换成修正值，指向本报告 |
| `docs/reports/report-08-teacher-reply-20261030.md` §3.4 | 865 这个数来源已查清（见下），连同词表错误一起更正 |
| `docs/execution/20261104-队友交接总纲.md` | §3 表、§5、§7.5 数据路径，全部改 |
| 所有 PPT / docx 交付物 | 凡引用 SATURN 0.65 / 0.4560 的页面 |

> 关于旧文档里那个 `865`：它确实是 `coarse_zebrafish_to_human.json` 里**预测为 `Orthers` 的细胞数**（逐对求和可复现），不是"被误映射的细胞数"，也不是"跨门"的数字。它和 v1 报的 `n_dropped=736` 差 131，原因就是真值侧另有 131 个细胞先被丢掉了。修正后 `Orthers` 预测 → `neural`（斑马鱼词表里是 active），**不再被丢弃**。
