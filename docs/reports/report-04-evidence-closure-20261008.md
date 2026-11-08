# 报告 4/10：ortholog-PCA 与 SAMap 证据闭环复核（2026-10-08）

本次汇报：第 4/10 次，主题：ortholog-PCA 与 SAMap 证据闭环只读复核

实际做了什么：
- ortholog-PCA manifest 39 文件 SHA 逐文件复核：39/39 一致
- 旧草表作废标注：在 3 份文档中检索"作废"标记——ortholog-PCA 证据矩阵 ✓、过时数字审计 ✓、终版证据矩阵 §四 补充说明 ✓
- SAMap WDL 六方向×三层 metrics 全量读入 ✓
- Phase 6 关账报告脚本口径声明（md5 56bb6035 非 Phase 5 修复版 0a2063d3）核实 ✓

证据文件：
- results/pilot-v1/ortholog-pca-v98/（manifest + metrics + 39 files）
- results/pilot-v1/samap-v98/wdl-run/extracted/（21 files）
- docs/phase6-closure-20261005.md

命令与退出码：
- python SHA 复算 39 文件 + JSON 读入 × 3：exit 0

输出文件数量与 SHA：
- 无新文件（纯只读复核）

数字口径：
- ortholog-PCA coarse：映射词汇 9 粗类；n_q 逐方向（h→m / m→h / h→z / m→z / z→h / z→m）= 1505 / 1528 / 1499 / 1499 / 1528 / 1505
- SAMap coarse：原始标签+过滤；n_q = 1505 / 1528 / 1496 / 1496 / 1528 / 1505（鱼方向 1496 与 v99 的 1499 差 3，根因待核验）
- 全部 transductive；单 seed

Claude 审阅：待审（并入 Stage E PPT/Word 审阅一并送审）

未完成与原因：无

下一阶段：Stage E（PPT v2 + Word 草稿）

是否需要用户批准 DCS/GPU：否
