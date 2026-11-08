# AI 使用日志（课题5，2026-09-20 至 2026-10-03）

> Phase 8 交付物。按阶段汇总 AI 工具的使用内容、产出与人工把关点；所有结论均有人工/独立复核锚点。

## 工具与分工

| 工具 | 角色 | 阶段 |
|---|---|---|
| ZCode（GLM 系，"Flash"） | 执行：数据下载校验、平台 API 攻坚、脚本实现、评测运行、证据回收、文档 | 全程 |
| Claude（独立审阅代理） | 审阅：状态文件修订意见、Gate 2/3/5 逐项裁决、Phase 4 证据化复审、checkpoint 终审 | 09-29 起 |
| Codex | 规划：长跑计划共同作者；终审：待执行（用户转交 checkpoint 后） | 09-30 起规划 |
| Genpilot（平台内置） | 平台诊断通路发现（inner.dcs.cloud 内网解析、notebook 网关结构） | 09-21 |

## 关键节点与人工把关

1. **数据获取（09-20）**：AI 执行公开 FTP 下载 + 字节级校验 + h5ad 元数据探查；老师微信确认"自己下载"，用户批准上传；物种组合由 AI 建议人鼠鱼、Claude 共同定案。
2. **G2 镜像核验（09-20/21）**：AI 攻坚离线任务通道（AES 表单加密、printf 单行化）；两次 GPU 受控启动均经用户逐次批准（¥32.42/¥26.87 课程计费组承担）；白屏问题经 ITSM 工单 TK20260921002545502 官方定性（需华大 VPN/等审批），AI 的"内网 split-horizon"判定与官方互证。
3. **首轮 SATURN（09-22 前后）**：AI 提交 v71/v72；其后审计发现 v72 证据不足以支持 held-out 表述，全部降级为 transductive/in-sample exploratory——AI 自我纠偏并冻结 v73 manifest（evidence_status=pending 维持至今）。
4. **统一评分器 v99（09-29）**：AI 实现并提交 DCS 只读评估；其与 v97g 口径差异（48.44% vs 61.79%）由消歧文档处理为双报不合并。
5. **长跑计划执行（10-01 起）**：Phase 0-5 按 docs/superpowers/plans/2026-10-01-course5-flash-claude-longrun.md 执行；每个 Gate 由 Claude 独立裁决（Gate 2 pass / Gate 3 conditional→修复解除 / Gate 5 pass / Phase 4 pass / checkpoint pass），全部裁决带 file:line 证据并归档。
6. **AI 抓出的真 bug 清单**（防御性价值的直接证据）：ortholog-PCA 未定义变量 X、mapping 元组键错配、共享基因门跳过→硬停、neighbor_barcodes 索引错位（Claude 实测发现）、解析器 3 处崩溃级缺陷（fixture 干跑发现）。
7. **人工决策点**（AI 未自作主张）：一切 DCS 训练/提交、数据上传、预算、导师沟通、Phase 6 SAMap 提交（待批准）、commit 处置（本轮全部未提交待 Codex）。

## 未使用 AI 做的事

- 未用 AI 生成生物学结论性解释（方法学结论均由数字+统计检验支撑，解释文本由 AI 起草但标 candidate 待人工审）
- 未用 AI 绕过任何平台权限/凭据边界（全程不读取不保存 token/cookie；登录均由用户本人操作）

## 补记（2026-10-04/05：Phase 1 收尾 + Phase 6 WDL + Phase 8 终稿）

- **Phase 1 收官**：经 Genpilot NFS 挂载发现 + dcs data push + downloadFile API 三层通道，v99 全部 46 文件回收并通过四重独立验证（Claude Gate 1 pass，provenance 升 confirmed file-level）。metrics.json SHA d1081cfd 为引用锚点。
- **Phase 6 WDL 通道**：用户批准路线变更后，Genpilot 构建 runsamap WDL（SATURN--22 镜像 + 4Gi）并迭代 14 次排障（hnswlib→pip 解释器→BLAS OOM→mo/ms 键名）后一次跑通。脚本 mo/ms bug 为本项目真 bug（Genpilot 发现），本地脚本待同步修。
- **Phase 8 终稿**：Word 报告（deliverables/course5-final-report.docx，表格数字由脚本从 metrics.json 直接读入）+ 终版 PPT（deliverables/course5-final-presentation.pptx，12 页）+ 最终证据矩阵（docs/final-evidence-matrix-20261005.md，唯一数字出处）。
- **人工把关**：Phase 6 路线变更（离线→WDL）由用户 AskUserQuestion 明确批准；工单加急由用户授权；全部 Gate 由 Claude 独立复核。
