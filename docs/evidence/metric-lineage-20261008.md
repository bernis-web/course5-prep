# 数字来源链（metric lineage）——五个核心示例（2026-10-08）

> 本文件回答一个问题：报告里的每个百分比是怎么从原始 h5ad 一路算出来的。
> 每条链的终点是 SHA 锚定的 metrics.json；中间每步可由随附脚本复算。
> 五个示例覆盖三种方法与"低于多数类"的读数场景。

## 示例 1：ortholog-PCA human→mouse coarse = 0.8618

| 属性 | 值 |
|---|---|
| 输入数据 | local_human_s.h5ad（1528 细胞）+ local_mouse_s.h5ad（1535 细胞）|
| 表示层 | 1:1 直系同源基因交集（15,869 基因）→ 联合 PCA-50 |
| query / reference | query = 鼠 1,535；reference = 人 1,528 |
| 标签空间 | 映射词汇（coarse 9 粗类，经冻结映射表 v1）|
| 排除规则 | query 侧 status≠active 剔 30 → n_q = 1,505 |
| coverage_q | 1505/1535 = 0.9805 |
| 正确数 | round(0.8618 × 1505) = 1,297 |
| 分母 | n_q = 1,505 |
| 公式 | acc = correct / n_q |
| 多数类 | 0.4817（mouse coarse 真值分布）|
| shuffle/null | 200 次 RandomState(0) 洗牌 query 预测；p = P(null ≥ acc) = 0.0 |
| 输出文件 | results/pilot-v1/ortholog-pca-v98/metrics.json |
| SHA-256 | b2b3ac6bc37c410841bdcbbd968159246e1990db47d02b8fa11844527d66c725 |

## 示例 2：SATURN v97g human→mouse coarse = 0.6179

| 属性 | 值 |
|---|---|
| 输入数据 | 同上三物种 pilot（全细胞）|
| 表示层 | ESM2 蛋白嵌入 → macrogene 聚合（256→1000）→ 联合训练（epochs=50, seed=0）|
| 评估层 | obsm/macrogenes |
| 标签空间 | 原始标签 + 映射表 status 过滤（无词汇重映射）|
| 数字出处 | EVAL3G 运行日志（docs/transductive-formal-v74-evidence-20260928.md）|
| 证据等级 | confirmed（日志级；无逐细胞文件，provenance 为日志级）|
| 注意 | 与 v99 exact-space 0.4749 不同口径——**双报不合并** |

## 示例 3：SATURN v99 exact-space human→mouse = 0.4749

| 属性 | 值 |
|---|---|
| 评分器 | v99 统一评分器（KNN15 cosine + 200 置换；与 ortholog-PCA 同评分器）|
| 表示层 | SATURN obsm/macrogenes（与 v97g 同一嵌入，统一评分器重评）|
| 标签空间 | 原始标签（exact 层，无映射重映射；status 过滤仅 coarse/fine）|
| n_q | 1,535（exact 层无排除，全 query 细胞）|
| 输出文件 | results/pilot-v1/saturn-v99/raw/recovered-20261001/metrics.json |
| SHA-256 | d1081cfd2489bf2afd30af7706fadf2d08b90390c26d38a766ea97b54b3dc261 |
| provenance | confirmed（file-level，46 文件树，Gate 1 pass）|
| 与 v97g 关系 | 61.79% = mapped-space（v97g 评分器）；0.4749 = exact-space（v99 统一评分器）——**双报不合并** |

## 示例 4：SAMap WDL human→mouse coarse = 0.1050

| 属性 | 值 |
|---|---|
| 运行通道 | WDL 流程任务 W202610050003104（绕开离线通道故障）|
| 实际运行脚本 | run_samap_compliant_v98_dcs.py md5 56bb6035（410 行版，**非** Phase 5 修复版 0a2063d3）|
| 表示层 | SAM 预处理（cell_median + log + StandardScaler npcs=100）→ SAMap 同源基因图联合对齐（NUMITERS=3）|
| label-aware | keys=cell_type 参与联合图构建（线上运行脚本与 checked-in 版本不一致，内容待回捞） |
| 标签空间 | 原始标签 + status 过滤（与 v99 一致）|
| 排除规则 | query 侧 status≠active 剔 30 → n_q 1,505；reference 侧剔 0 → n_ref 1,528 |
| 正确数 | round(0.1050 × 1505) = 158 |
| 分母 | n_q = 1,505 |
| 输出文件 | results/pilot-v1/samap-v98/wdl-run/extracted/metrics.json |
| SHA-256 | 3c7193999f489017e4227bff2dc83667b63a564a97a373373f6239328ae4954f |
| 证据等级 | candidate-final（探索性复现；脚本口径限制见 §四混合旗标说明）|

## 示例 5：ortholog-PCA human→zebrafish coarse = 0.1961（低于多数类）

| 属性 | 值 |
|---|---|
| 同源基因 | 人鱼 1:1 = 9,131 基因 |
| query / reference | query = 鱼 1,543；reference = 人 1,528 |
| 排除 | query 侧 status≠active 剔 44（mt 30 + Prolif 14）→ n_q = 1,499 |
| coverage_q | 1499/1543 = 0.9715 |
| acc | 0.1961；**多数类 = 0.3976 → acc < majority** |
| shuffle_p | 0.0（E[null] ≈ 0.10，200 次置换 0.089–0.117，远低于 acc；不是多数类检验）|
| 正确解读 | 该方向迁移信号弱——但 shuffle_p 表明仍优于随机预测向量；多数类比较是另一维度 |
| 输出文件 | results/pilot-v1/ortholog-pca-v98/metrics.json → human->zebrafish.coarse |
