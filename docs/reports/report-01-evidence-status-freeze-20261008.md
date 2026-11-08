# 第 1/10 次阶段汇报：证据状态冻结（2026-10-08）

本次汇报：第 1/10 次，主题：证据状态冻结

实际检查：
- Git 状态：分支 codex/teacher-reply-report-prep，ahead 53；最近提交链完整（c6e5545 ← … ← dce62b1）；脏工作区（4 修改 + wheelhouse 分片 + 未跟踪 tmp）未触碰、未提交
- 证据文件：三方法 metrics + 关账报告 + AI 意见书 + 交付物共 15 项 SHA-256 独立复算，全部与既有记录一致（详见状态矩阵）
- 三份 metrics 关键数字复核：ortholog-PCA coarse 六方向 0.8618/0.7369/0.1961/0.2755/0.1813/0.5761（与冻结值逐一相符）；SAMap coarse h→m 0.105；v99 coarse h→m 0.4844
- 状态矩阵 v1.1：26+6 项逐项登记（A 评估结果 9 项 / B 冻结输入 3 项 / C 审计治理 10 项 / D 交付物 4 项 / E 平台任务 6 项），经 Claude 两轮审阅（v1.0 revise → v1.1 pass）

证据文件：
- docs/evidence/status-matrix-20261008.md（本次核心产物，v1.1）
- **PPT（2026-10-12 补做，校模板版）**：results/stage-reports-20261009/课题5第01次汇报_现状与问题定稿.pptx（7 页）
  SHA-256 `489e830862e06d0e2e531f256aec2afce62ba4860ae3a66b3390430e80676f11`；逐页渲染 render/r01-p01..07.png；碰撞检测 0 处
- results/pilot-v1/ortholog-pca-v98/metrics.json（SHA b2b3ac6b…c725）
- results/pilot-v1/samap-v98/wdl-run/extracted/metrics.json（SHA 3c719399…54f）
- results/pilot-v1/saturn-v99/raw/recovered-20261001/metrics.json（SHA d1081cfd…261，引用锚点）
- config/heart-celltype-map-v1.tsv（SHA be985735…3165，待导师签认）
- docs/mapping-v1-ai-review-opinion-20261005.md（AI 复核意见书，导师终签的降维材料）

命令与退出码：
- git status --short --branch / git log --oneline -12：exit 0
- python hashlib SHA-256 复算 15 项：exit 0
- ortholog-PCA/SAMap/v99 metrics.json 加载与逐向核对：exit 0
- SAMap coarse 六向 per_cell 全行重算（本地 extracted/*.json）：6/6 与 metrics 一致，exit 0

输出文件与 SHA：
- docs/evidence/status-matrix-20261008.md（矩阵 v1.1，git 7782a17）
- 本汇报正文 docs/reports/report-01-evidence-status-freeze-20261008.md

Claude 审阅：逐项通过（v1.0 判 revise 列出 6 类问题——A3 层级虚标、A7-A9 证据错引、B3 无在库锚点、C6 过时、E2 无源时长、图例错位+5 项漏列——全部落实后 v1.1 复核 pass，零剩余修订；A3 补算经审阅人独立复现 6/6 确认）

老师反馈：待收集

本轮未完成：
- PPT 修订（按计划属汇报周期后；旧 PPT 的作废草表与过时 SAMap 表述已在矩阵 D3 登记 blocked）
- R1d 离线任务仍 Pending（平台通道故障，工单加急+追评文案已备，等平台或老师推动）
- 映射表 v1 导师终签（AI 意见书已出，等邮件发送）

下一次汇报主题：数字来源链（human→mouse 一个方向的完整生成路径：输入→表示层→标签→分母→输出 JSON→SHA）

是否需要 DCS/WDL/GPU：否
