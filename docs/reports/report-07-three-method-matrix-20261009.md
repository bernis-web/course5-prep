# 报告 7/10：三方法总矩阵与老师问题专页（2026-10-09）

本次汇报：第 7/10 次，主题：用最终证据重做老师指出的那张表

实际做了什么：
- 总矩阵（六方向 × ortholog-PCA / SATURN v97g / SAMap v98 / v99 / 多数类）全部取自冻结证据矩阵，逐格核对
- 旧→新替换表：草表 80.9/38.3/40.5/22.4/11.9/79.5 → 86.18/73.69/19.61/27.55/18.13/57.61；SAMap 探索列 → WDL 结果；删除"v98 尚需修正复跑"
- 新增"从原始数据到表格单元格"算式页（86.18% = 1,297 ÷ 1,505）与"为什么方法数字不同"六项对照页
- 产出汇报 PPT：results/stage-reports-20261009/课题5第07次汇报_三方法总矩阵与老师问题.pptx（7 页）

证据文件：
- docs/final-evidence-matrix-20261005.md（唯一数字出处）
- results/pilot-v1/ortholog-pca-v98/metrics.json（SHA b2b3ac6b…c725）

命令与退出码：
- python 三份 metrics 逐格对照（PPT 数字 vs 冻结值）：exit 0

数字口径：
- 每列协议标签随表出现；跨方法不排名；SATURN 双口径不合并；全部 transductive / 单 seed

Claude 审阅：待审（随阶段 PPT 批量送审）

未完成与原因：无（本页为汇报材料，正式 Word 终版在汇报 10 后）

下一阶段：汇报 8（mapping reviewer 与证据责任）

是否需要用户批准 DCS/GPU：否
