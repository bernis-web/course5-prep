# 数字计算示例——逐步算式（2026-10-08）

> 每个示例展示从原始计数到一个百分比的完整算式链。
> 所有中间值可从随附 metrics.json 逐格核对。

## 示例 1：ortholog-PCA human→mouse coarse 0.8618

```
输入:   local_human_s.h5ad (1528×32732) + local_mouse_s.h5ad (1535×32379)
归一化:  sc.pp.normalize_total(target_sum=1e4) → sc.pp.log1p()
        等价于 log1p(CPM/100)，在全基因空间执行
基因过滤: 人鼠 1:1 直系同源交集 → 15,869 基因
联合 PCA: sklearn PCA(n_components=50, random_state=0)
         fit_transform( vstack([Xs, Xt]) )  # Xs 1528×15869, Xt 1535×15869
KNN:     KNeighborsClassifier(n_neighbors=15, metric="cosine", weights="distance")
         fit(Z[human_rows], ytr[human_active])  # 仅 active reference 行
预测:    knn.predict(Z[mouse_rows])  →  1535 个预测
排除:    mouse coarse 层 30 个 status≠active 细胞退出分母
correct = 1297  (预测 == 真值，按映射后 coarse 词汇)
n_q     = 1505  (1535 − 30 排除)
acc     = 1297 / 1505 = 0.8618
coverage = 1505 / 1535 = 0.9805
majority = 4817/10000 → mouse coarse 真值最大类占比 = 0.4817
置换     = 200 次 RandomState(0) shuffle(preds)；p = #{null ≥ 0.8618} / 200 = 0
```

## 示例 2：SATURN v97g human→mouse coarse 0.6179

```
训练:   SATURN num_macrogenes=1000, epochs=50, seed=0
        ESM2 嵌入 → macrogene 聚合 → 跨物种联合训练
评估层:  obsm["macrogenes"]
评分:    v97g 评分器（KNN15 cosine；原始标签+映射过滤）
数字来源: EVAL3G 运行日志（无逐细胞文件，provenance 为日志级）
         → 0.6179 为日志级 confirmed 数字
注意:    与 v99 exact-space 0.4749 不同（标签空间/排除/评分器三重差异）
```

## 示例 3：SATURN v99 exact-space human→mouse 0.4749

```
嵌入:    与 v97g 同一 obsm/macrogenes
评分:    v99 统一评分器（KNN15 cosine 倒距离加权 + 200 置换）
标签:    exact 层 = 原始标签（无映射重映射），无 status 过滤
correct / n_q 由 v99 metrics.json 直接读取:
  acc = 0.4749, n_q = 1535（exact 层无排除）
输出:    results/pilot-v1/saturn-v99/raw/recovered-20261001/metrics.json
SHA:     d1081cfd2489bf2afd30af7706fadf2d08b90390c26d38a766ea97b54b3dc261
```

## 示例 4：SAMap WDL human→mouse coarse 0.1050

```
依赖:    预建 pylibs（samap 1.0.16 + samalg 1.0.2 + hnswlib shim）
预处理:  s.load_data() → s.preprocess_data(cell_median, log, 0.96)
         s.run(StandardScaler, npcs=100, weight_PCs=False, k=20)
联合对齐: SAMAP(sams, keys=cell_type, gnnm=同源图) ; sm.run(NUMITERS=3)
预测:    KNN15 cosine 倒距离加权（联合嵌入空间）
排除:    query 侧 status≠active 剔 30
correct = 158
n_q     = 1505
acc     = 158 / 1505 = 0.1050
输出:    results/pilot-v1/samap-v98/wdl-run/extracted/metrics.json
任务:    W202610050003104（WDL 通道）
```

## 示例 5：ortholog-PCA human→zebrafish coarse 0.1961（低于多数类）

```
同源基因: 人鱼 1:1 = 9,131 基因
排除:    query（鱼）侧 status≠active 剔 44（mt 30 + Prolif 14）→ n_q = 1,499
correct = 294  (round(0.1961 × 1499))
acc     = 294 / 1499 = 0.1961
多数类   = 0.3976（鱼 coarse 真值最大类占比）
         acc < majority → 该方向无迁移优势
shuffle_p = 0.0（E[null] ≈ 0.10，200 次置换 0.089–0.117 << acc 0.1961；仍优于随机，但远低于多数类 0.3976）
输出:    results/pilot-v1/ortholog-pca-v98/metrics.json → human->zebrafish.coarse
```

## 通用公式

```
coverage_q = n_q / n_q_total
acc        = correct / n_q
majority   = max(truth_class_count) / n_q
E[null]    = Σ_k (pred_marginal_k × truth_marginal_k) / n_q²
shuffle_p  = #{shuffled_acc ≥ observed_acc} / n_perm
```
