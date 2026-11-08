# 报告 3/10：三方法公平比较边界（2026-10-08）

本次汇报：第 3/10 次，主题：三方法公平比较边界

实际做了什么：
- 建立 docs/evidence/method-comparison-matrix-20261008.md（六个维度并列表）
- 明确每个方法"能回答的问题"与"不能回答的问题"
- 列出五项不可比项清单

证据文件：
- docs/evidence/method-comparison-matrix-20261008.md
- results/pilot-v1/ortholog-pca-v98/metrics.json
- results/pilot-v1/saturn-v99/raw/recovered-20261001/metrics.json
- results/pilot-v1/samap-v98/wdl-run/extracted/metrics.json

命令与退出码：
- python json.load × 3：exit 0（数字来源核对，无新计算）

输出文件数量与 SHA：
- docs/evidence/method-comparison-matrix-20261008.md

数字口径：
- 全部引用冻结 metrics（无新计算）
- 标签空间差异（映射词汇 vs 原始标签+过滤）为不可比项之首
- label-free vs label-aware 为方法设计差异，非优劣判据

Claude 审阅：待审（与汇报 2 合并送审）

未完成与原因：无

下一阶段：汇报 4（ortholog-PCA 基线闭环）

是否需要用户批准 DCS/GPU：否
