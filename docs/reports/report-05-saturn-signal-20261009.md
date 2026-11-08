# 报告 5/10：SATURN 结果与容量/协议效应（2026-10-09）

本次汇报：第 5/10 次，主题：SATURN 信号来源与协议效应

实际做了什么：
- 汇总 v97g（日志级）与 v99（文件级）双口径，明确三个数字（0.6179 / 0.4749 / 0.4844）不可合并
- 整理信号来源证据：ESM2 消融（67.4→20.4，v72-era 协议内配对；v97g 协议下未重跑；confirmed 方向性）
- 整理容量/稳定性/上限三项：macrogenes=1000、seed（h→m 67.1±3.8；鱼方向 11.3/48.8/8.3 双峰）、物种内 ceiling（85.5/93.5/74.2）
- 产出汇报 PPT：results/stage-reports-20261009/课题5第05次汇报_SATURN信号与协议效应.pptx（7 页）

证据文件：
- docs/transductive-formal-v74-evidence-20260928.md（v97g 六方向表）
- results/pilot-v1/saturn-v99/raw/recovered-20261001/metrics.json（SHA d1081cfd…dc261）
- docs/final-evidence-matrix-20261005.md §三/§四/§五

命令与退出码：
- python json.load（v99 metrics 逐向核对）：exit 0（无新计算）

数字口径：
- v97g：mapped-space · 日志级 · coverage_q 0.9805/1.0/0.9715
- v99：原始标签 · exact/coarse 双报 · provenance confirmed（file-level）
- 全部 transductive / in-sample · 单 seed（0）

Claude 审阅：待审（随阶段 PPT 批量送审）

未完成与原因：
- macrogene 容量消融（1000 vs 其它档）无现成数据，PPT 已标注为缺口
- v97g 逐细胞文件仍缺失（日志级）

下一阶段：汇报 6（SAMap 复现与负结果）

是否需要用户批准 DCS/GPU：否
