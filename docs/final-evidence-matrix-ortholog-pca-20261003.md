# 终版证据矩阵（一）：ortholog-PCA 基线（2026-10-03）

> 状态：candidate-final（Claude phase4_verdict=pass，2026-10-02 复审；SAMap/v99 数值冻结后并入总矩阵）。
> 数值来源唯一：results/pilot-v1/ortholog-pca-v98/{metrics.json,manifest.json,predictions/,confusion/}。
> 禁止手工改数字；引用必须带 manifest SHA。

## 方法一句话

零整合基线：三物种 1:1 直系同源基因取交集 → 全基因空间 log1p(CPM/100) 归一化 → 共享 ortholog 子矩阵上人-鼠 15,869 / 人-鱼 9,131 / 鼠-鱼 7,670 基因 → src+tgt 联合 PCA-50（seed 0，transductive）→ KNN K=15 cosine 倒距离加权 → 三层标签评估（exact 原始标签 / coarse-fine 冻结映射表 v1 be98…3165 双向排除 status≠active）→ 200 次 RandomState(0) 预测向量置换。

## 主表（18 格；coarse 加粗为主结论层）

| direction | exact | coarse | fine | coverage(q) | majority(coarse) |
|---|---|---|---|---|---|
| human→mouse | 0.7824 | **0.8618** | 0.7980 | 0.9805 | 0.4817 |
| mouse→human | 0.4084 | **0.7369** | 0.4103 | 1.0000 | 0.3115 |
| human→zebrafish | 0.1698 | 0.1961 | 0.1801 | 0.9715 | 0.3976 |
| mouse→zebrafish | 0.1659 | 0.2755 | 0.1748 | 0.9715 | 0.3976 |
| zebrafish→human | 0.1453 | 0.1813 | 0.1695 | 1.0000 | 0.3115 |
| zebrafish→mouse | 0.4769 | **0.5761** | 0.5010 | 0.9805 | 0.4817 |

完整逐格（n_q/n_q_total/majority/shuffle_p/confusion）：metrics.json。

## 核心读数（带 §口径 警示）

1. **哺乳动物对强**：h→m coarse 86.18%（majority 48.17%，超出 38 个百分点）；m→h coarse 73.69%（majority 31.15%）。
2. **斑马鱼向弱/阴性**：h→z、m→z、z→h 的三层全部低于对应多数类（z→m 例外，coarse 57.61% > majority 48.17%）。
3. 与 SATURN v97g（transductive reassessment candidate，h→m coarse 61.79%）对比：**同方向上零整合 ortholog-PCA 基线高于 SATURN**——支持"跨物种对齐能力被高估、简单同源基线难超越"的方法学结论（跨方法 coarse 标签空间差异警示见下，正式对比须并列 coverage 与标签空间定义）。
4. SAMap 对比：待 v98 DCS 复现数值冻结后填入。

## 口径警示（引用本表必须随带）

1. **协议**：全部为 transductive/in-sample reassessment（联合 PCA 含 query 表达值），不得写成 held-out/inductive。
2. **shuffle_p 零分布**是预测边际×真值边际对角积 E[null]，不是多数类检验；斑马鱼向 9 格 acc<多数类但 p≈0 属预期；p 值只用于"优于随机预测向量"。
3. **分层分母不同**：exact 含全部真值；coarse/fine 剔除 status≠active（mouse 30 / zf 44）。每个 acc 必须并列 n_q 与 coverage_q；跨层不可直接比。
4. **跨方法 coarse/fine 不可直接同表**：本方法 coarse/fine 是映射后词汇空间；SATURN v97g 与 SAMap v98/v99 的 coarse/fine 是原始标签+status 过滤空间。跨方法比较必须定义共同标签空间或分层并列呈现。
5. **label 属性**：本方法 label-free（评估才用标签）；SAMap（keys=cell_type）为 label-aware——工具公平性表述须带此差异。
6. **seed**：单 seed（0）；SATURN 侧已证鱼方向 seed 双峰，本基线的鱼方向数字同样是单 seed 点估计。
7. **数据边界**：每物种 ~1.5k 细胞 pilot 子集；142 个斑马鱼重复基因符号按首现确定性去重（manifest.params.gene_symbol_dedup_dropped）。

## 溯源链（全部 SHA-256 锚定）

输入：local_{human,mouse,zebrafish}_s.h5ad + config/heart-celltype-map-v1.tsv（be98…3165）+ ortholog/{MGI_HOM_MouseHumanSequence.rpt,human_orthos.txt,mouse_orthos.txt} → manifest.input_sha256（7 项）。
实现：scripts/ortholog_pca_local_v1.py（script_sha256 见 manifest）。
产物：39 文件 SHA 全量在 manifest.output_sha256； predictions/ 18 + confusion/ 18 + metrics.json。
独立验证：Claude 审查代理从原始 h5ad 端到端复现 mouse→human exact+coarse，预测与邻居条码逐行一致（2026-10-02）；18/18 格与逐细胞重算全等。

## 旧草表作废说明

v75c/v78b 阶段草表（h→m 80.9 / m→h 38.3 / h→z 40.5 / m→z 22.4 / z→h 11.9 / z→m 79.5，出处 docs/course5-longrun-state-20260930.md §2）作废：其排除规则失效（coarse_level=='unmapped' 字符串过滤在 TSV 中 0 行命中，TSV 实测；mouse 30 / zf 44 应排除细胞留在分母）且未用统一评分器。正式引用一律以本表为准。
