# Wave 3 ortholog-PCA 本地预检 manifest（2026-09-30）

## 目的

统一评分器复算 ortholog-PCA 基线，取代早期阶段草表。当前状态：等待执行（需用户批准本地运行）。

## 固定协议

| 参数 | 值 |
|---|---|
| ortholog 集合 | MGI 1:1 (17611 对) + ZFIN fish-human (10398) + fish-mouse (9058) |
| 基因过滤 | 仅保留 var_names 中存在的 ortholog 基因 |
| PCA 维度 | 50 |
| 归一化 | log1p(CPM/100) |
| KNN | K=15, cosine, inverse-distance weighting |
| 置换检验 | 200 次 RandomState(0) 洗牌 query 预测，单侧 p |
| 映射表 | config/heart-celltype-map-v1.tsv (SHA-256 be98…3165) |
| seed | 0 |

## 输入

| 文件 | SHA-256 | 说明 |
|---|---|---|
| local_human_s.h5ad | (待计算) | 1528 细胞 |
| local_mouse_s.h5ad | (待计算) | 1535 细胞 |
| local_zebrafish_s.h5ad | (待计算) | 1543 细胞 |
| config/heart-celltype-map-v1.tsv | be98…3165 | 冻结映射 |
| ortholog/MGI_HOM_MouseHumanSequence.rpt | (待计算) | 人鼠 1:1 |
| ortholog/human_orthos.txt | (待计算) | 人鱼 1:1 |
| ortholog/mouse_orthos.txt | (待计算) | 鼠鱼 1:1 |

## 预期输出

- results/pilot-v1/ortholog-pca-v98/metrics.json（六方向×三层）
- results/pilot-v1/ortholog-pca-v98/predictions/（逐细胞预测 JSON）
- results/pilot-v1/ortholog-pca-v98/environment.json

## 停止条件

- 任一输入文件缺失
- 任一方向共享基因数 < 1000
- 任一方向 KNN 训练失败
- OOM

## Gate-2 修订（2026-10-02，ortholog_pca_local_v1.py 重写后）

- 归一化协议口径统一：manifest 写 log1p(CPM/100)，实现为 `normalize_total(target_sum=1e4)+log1p`——两者逐 cell 等价（CPM/100 ≡ counts/total×1e4），在**全基因空间**归一化之后再取共享 ortholog 子矩阵；与 v98 DCS 版（ortholog_pca_dcs_v2.py L84-85）一致。
- mapping 仅用冻结表 `species|cell_type` **字符串键**；coarse/fine 双向排除 `mapping_status != active`（v99 协议），exact 保留全部有效真值。
- 共享 1:1 ortholog < 1000 → 打印 HARDSTOP 并 **exit(2)**（非跳过）。
- 角色命名：`src->tgt` 中 src=reference（KNN 拟合），tgt=query。
- 输出（full 模式）：manifest.json（输入/输出全量 SHA-256）、environment.json、command.txt、metrics.json、predictions/ 18 份、confusion/ 18 份；prediction 行 schema：prefixed_barcode / direction / level / truth / prediction / included / exclusion_reason / confidence / neighbor_barcodes（K=15 cosine 近邻，reference 侧 barcode）。
- --smoke：每物种固定 RandomState(0) 抽 120 细胞、nperm=20，仅写 results/pilot-v1/ortholog-pca-smoke/，目录已存在则拒绝运行；smoke 数字不进主表。

## shuffle_p 的零分布口径（Claude Phase 4 复审补记，2026-10-03）

置换检验 = 200 次 RandomState(0) **洗牌 query 预测向量**后重算 accuracy。其零分布期望
E[null] = Σ_k (预测边际_k/n) × (真值边际_k/n)（对角积），**不是多数类率**。
因此"acc < 多数类却 p≈0"是预期行为（预测高度集中于单一标签时 E[null] 远低于多数类），
报告中不得把 shuffle_p 表述为"优于多数类"的显著性；与多数类的比较只写 acc vs majority
两个并列数字，p 值仅用于"优于随机预测向量"的推断。唯一非零格（m→z exact 0.02=4/200）
恰为 acc−E[null] 裕度最小的格子（0.1659 vs 0.1491），全部 18 格 acc > E[null] 自洽。
