# 报告 6/10：SAMap 复现与负结果解释（2026-10-09）

本次汇报：第 6/10 次，主题：SAMap 复现与负结果解释

实际做了什么：
- 以 Phase 6 关账报告与 WDL 产物为准，核对任务号、脚本 md5、输入 SHA、18 格输出与 n_q
- 明确两个必须声明的限制：label-aware（keys=cell_type）与脚本版本混合口径（md5 56bb6035 非 0a2063d3）
- 整理排障记录（14 次迭代、四类根因）作为工程证据
- 产出汇报 PPT：results/stage-reports-20261009/课题5第06次汇报_SAMap复现与负结果.pptx（7 页）

证据文件：
- docs/phase6-closure-20261005.md
- results/pilot-v1/samap-v98/wdl-run/extracted/metrics.json（SHA 3c719399…954f）
- 任务 W202610050003104；tar 481,920 B（id 0e3741b17b25439e98243f821b1c8cc3）

命令与退出码：
- python json.load + per_cell 全行重算（158÷1505=0.1050；误用 included 得 158÷1398=0.113）：exit 0

数字口径：
- 原始标签+status 过滤；n_q 1505/1496/1528；18 格全 ≤ 10.5%，四方向为 0
- 全部 transductive / in-sample · 单 seed（0）

Claude 审阅：待审（随阶段 PPT 批量送审）

未完成与原因：
- Phase 5 修复版脚本（0a2063d3）未在 WDL 运行（需新任务，待批准）
- 换 keys / NUMITERS 的敏感性实验未做（属新实验）

下一阶段：汇报 7（三方法总矩阵与老师问题专页）

是否需要用户批准 DCS/GPU：否（如需重投 WDL 则需）
