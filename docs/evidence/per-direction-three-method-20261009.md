# 逐方向三方法完整对照（老师问题专页底表，2026-10-09）

> 数字来源：results/pilot-v1/{ortholog-pca-v98,saturn-v99/raw/recovered-20261001,samap-v98/wdl-run/extracted}/metrics.json（coarse 层）。
> 正确数经 confusion 对角和与 acc×n_q 双重复核（6 方向 × 3 方法全部一致，见附录校验）。
> v97g 为日志级（无逐细胞文件），只给 acc/majority/coverage，不给正确数。

## 一、每方法固定口径（随全部数字引用）

| 项 | ortholog-PCA | SATURN v97g | SATURN v99 | SAMap v98 |
|---|---|---|---|---|
| 数据来源 | local_{human,mouse,zebrafish}_s.h5ad（同一批 pilot 子集） | 同左 | 同左 | 同左 |
| 表示层 | 1:1 直系同源交集 + 联合 PCA-50（seed 0） | ESM2 → 1,000 macrogenes 联合训练 | 同 v97g（同一批嵌入） | 同源基因近邻图 + SAM 潜空间（npcs=100） |
| query/reference | src=reference 拟合；tgt=query 预测 | 同左 | 同左 | 同左 |
| 标签空间 | **映射词汇（9 粗类）** | **mapped-space（映射后粗类）** | **原始标签 + status 过滤** | **原始标签 + status 过滤** |
| 训练时标签可见性 | label-free（不用标签） | label-aware（labels 通道参与 miner；ref_labels 仅评估；运行时版本待核实） | label-aware（同 v97g 机制） | label-aware（keys=cell_type；运行脚本内容待回捞） |
| 排除规则 | status≠active 双向（mouse 30 / zf 44） | 规则合规列（74 细胞双向排除） | coarse/fine 排除；exact 不排除 | status≠active 双向（实际排除数见下表） |
| 评分器 | KNN15 · cosine · 倒距离加权 | v97g 评分器（mapped-space） | v99 统一评分器 | KNN15 · cosine（与 v99 同） |
| 置换检验 | 200 次 RandomState(0) 预测向量洗牌 | 同定义 | 同定义 | 同定义 |
| 证据等级 | candidate-final | confirmed（**日志级**） | provenance confirmed（报告数字 candidate） | candidate-final（探索性复现） |

**引用纪律**：映射标签空间（oPCA / v97g）与原始标签空间（v99 / SAMap）的 coarse 层数值**不可直接排名**；
且 label-free 与 label-aware 不是同一问题。跨方法同表仅作方向性参考。

## 二、哺乳动物对（人↔鼠）

| 方向 | 方法 | n_ref | n_q | 排除数 | 正确数 | accuracy | majority | shuffle_p | 证据等级 |
|---|---|---|---|---|---|---|---|---|---|
| 人→鼠 | ortholog-PCA | 1528 | 1505 | 30 | 1297 | **0.8618** | 0.4817 | 0.0 | candidate-final |
| 人→鼠 | SATURN v97g | —（日志级） | ≈1505 | — | — | 0.6179 | 0.4817 | — | confirmed（日志级） |
| 人→鼠 | SATURN v99 | 1528 | 1505 | 30 | 729 | 0.4844 | 0.4618 | 0.0 | provenance confirmed |
| 人→鼠 | SAMap v98 | 1528 | 1505 | 30 | 158 | 0.1050 | 0.4618 | 0.000 | candidate-final（探索性） |
| 鼠→人 | ortholog-PCA | 1505 | 1528 | 0 | 1126 | **0.7369** | 0.3115 | 0.0 | candidate-final |
| 鼠→人 | SATURN v97g | —（日志级） | ≈1528 | — | — | 0.2539 | 0.3115 | — | confirmed（日志级） |
| 鼠→人 | SATURN v99 | 1505 | 1528 | 0 | 294 | 0.1924 | 0.2526 | 0.0 | provenance confirmed |
| 鼠→人 | SAMap v98 | 1505 | 1528 | 0 | 30 | 0.0196 | 0.2526 | 1.000 | candidate-final（探索性） |

## 三、人/鼠 → 鱼（query = 鱼）

| 方向 | 方法 | n_ref | n_q | 排除数 | 正确数 | accuracy | majority | shuffle_p | 证据等级 |
|---|---|---|---|---|---|---|---|---|---|
| 人→鱼 | ortholog-PCA | 1528 | 1499 | 44 | 294 | **0.1961** | 0.3976 | 0.0 | candidate-final |
| 人→鱼 | SATURN v97g | —（日志级） | ≈1499 | — | — | 0.1835 | 0.3976 | — | confirmed（日志级） |
| 人→鱼 | SATURN v99 | 1528 | 1499 | 44 | 169 | 0.1127 | 0.3976 | 0.0 | provenance confirmed |
| 人→鱼 | SAMap v98 | 1528 | 1496 | 47 | 51 | 0.0341 | 0.3977 | 0.035 | candidate-final（探索性） |
| 鼠→鱼 | ortholog-PCA | 1505 | 1499 | 44 | 413 | **0.2755** | 0.3976 | 0.0 | candidate-final |
| 鼠→鱼 | SATURN v97g | —（日志级） | ≈1499 | — | — | 0.3009 | 0.3976 | — | confirmed（日志级） |
| 鼠→鱼 | SATURN v99 | 1505 | 1499 | 44 | 292 | 0.1948 | 0.3976 | 0.0 | provenance confirmed |
| 鼠→鱼 | SAMap v98 | 1505 | 1496 | 47 | 0 | 0.0000 | 0.3977 | 1.000 | candidate-final（探索性） |

## 四、鱼 → 人/鼠（query = 人/鼠）

| 方向 | 方法 | n_ref | n_q | 排除数 | 正确数 | accuracy | majority | shuffle_p | 证据等级 |
|---|---|---|---|---|---|---|---|---|---|
| 鱼→人 | ortholog-PCA | 1499 | 1528 | 0 | 277 | **0.1813** | 0.3115 | 0.0 | candidate-final |
| 鱼→人 | SATURN v97g | —（日志级） | ≈1528 | — | — | 0.2474 | 0.3115 | — | confirmed（日志级） |
| 鱼→人 | SATURN v99 | 1499 | 1528 | 0 | 286 | 0.1872 | 0.2526 | 0.0 | provenance confirmed |
| 鱼→人 | SAMap v98 | 1496 | 1528 | 0 | 0 | 0.0000 | 0.2526 | 1.000 | candidate-final（探索性） |
| 鱼→鼠 | ortholog-PCA | 1499 | 1505 | 30 | 867 | **0.5761** | 0.4817 | 0.0 | candidate-final |
| 鱼→鼠 | SATURN v97g | —（日志级） | ≈1505 | — | — | 0.4651 | 0.4817 | — | confirmed（日志级） |
| 鱼→鼠 | SATURN v99 | 1499 | 1505 | 30 | 508 | 0.3375 | 0.4618 | 0.0 | provenance confirmed |
| 鱼→鼠 | SAMap v98 | 1496 | 1505 | 30 | 0 | 0.0000 | 0.4618 | 1.000 | candidate-final（探索性） |

## 五、读数（分组，不含混范围）

- **哺乳动物对**：oPCA 双向强（0.8618 / 0.7369，均大幅超多数类）；SATURN 仅人→鼠超多数类；SAMap 双向 ≤ 0.0196。
- **人/鼠→鱼（query=鱼）**：三方法全部低于多数类（0.3976）——oPCA 0.1961 / 0.2755，SATURN v97g 0.1835 / 0.3009，SAMap 0.0341 / 0.0000。
- **鱼→人/鼠（query=人/鼠）**：oPCA 0.1813（<0.3115）、0.5761（>0.4817，全表唯一鱼侧正信号）；SATURN v97g 0.2474 / 0.4651（均低于多数类）；SAMap 均为 0。
- 结论口径：**鱼作 query 与鱼作目标必须分开报告**；唯一例外是 oPCA 的鱼→鼠（0.5761 > 多数类 0.4817）。

## 六、v97g 的日志级限定（不可升级）

- v97g 无逐细胞预测文件，只有日志级 acc/majority/coverage_q；正确数、confusion 均不可得。
- 其分母按 coverage_q × query 物种细胞数推断（人→鼠 0.9805×1535≈1505；鼠→人 1.0×1528≈1528；人→鱼 0.9715×1543≈1499；鼠→鱼 ≈1499；鱼→人 ≈1528；鱼→鼠 ≈1505），属**推断值**，非文件级确认。
- 引用 v97g 时必须标注「日志级」；不得与 v99 合并。

## 附录：正确数双重复核（confusion 对角和 = acc × n_q）

| 方向 | oPCA | SATURN v99 | SAMap |
|---|---|---|---|
| 人→鼠 | 1297 | 729 | 158 |
| 鼠→人 | 1126 | 294 | 30 |
| 人→鱼 | 294 | 169 | 51 |
| 鼠→鱼 | 413 | 292 | 0 |
| 鱼→人 | 277 | 286 | 0 |
| 鱼→鼠 | 867 | 508 | 0 |

（6 方向 × 3 方法 = 18 格全部通过；exact 层正确数同法可复核。）
