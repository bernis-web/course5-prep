# 报告 8/10：mapping reviewer 与证据责任（2026-10-09）

本次汇报：第 8/10 次，主题：人工签认前的透明说明

实际做了什么：
- 汇总 AI 独立复核九项结果（A 档 22 行 / B 档 11 行 / C 档 2 行；排除规则五方对账 30/44/0 闭环）
- 整理 5 个审阅议题（涉及 6 条源映射：3 low + 2 medium + 1 high 命名疑点）与三个争议点文献级判断
- 明确责任边界：AI 复核（程序化 + 文献级）≠ 导师签认；签认前 mapping 保持 needs-reviewer
- 产出汇报 PPT：results/stage-reports-20261009/课题5第08次汇报_映射签认与证据责任.pptx（7 页）

证据文件：
- docs/mapping-v1-ai-review-opinion-20261005.md（复核意见书）
- docs/phase7-email-final-20261005.md（签认请求邮件定稿）
- config/heart-celltype-map-v1.tsv（SHA be985735…3165，38 行）

命令与退出码：
- python 逐行比对/计数/覆盖率重算（复核期已执行）：exit 0（本轮为材料整理，无新计算）

数字口径：
- 排除规则：mouse 30 / zf 44（mt 30 + Prolif 14）/ human 0；SAMap 鱼方向 1,496 差额已披露
- 映射表 v1 在签认前不得用于正式 benchmark 表述

Claude 审阅：待审（随阶段 PPT 批量送审）

未完成与原因：
- 导师签认未完成（外部依赖）
- 行 25 cmlc1 命名疑点建议 v2 前数据核实

下一阶段：汇报 9（最小 inductive 方案）

是否需要用户批准 DCS/GPU：否
