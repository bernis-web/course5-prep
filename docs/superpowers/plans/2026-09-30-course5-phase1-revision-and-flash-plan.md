# 课题5第一阶段修订与后续执行计划

日期：2026-09-30  
目标：把老师指出的“表格数字含金量高但解释不够”转化为一套可汇报、可复核、可继续执行的方案，并交给 Flash 分波次推进。

## 0. 当前判定

### 已确认

- 三物种心脏单细胞规模：人 1,528、鼠 1,535、斑马鱼 1,543。
- SATURN v97g coarse 六方向结果可作为 transductive / in-sample formal reassessment candidate：人→鼠 61.79%、鼠→人 25.39%、人→斑马鱼 18.35%、鼠→斑马鱼 30.09%、斑马鱼→人 24.74%、斑马鱼→鼠 46.51%。
- SATURN 结果使用 KNN15 + cosine + 倒距离加权，coarse/fine 对 unmapped 细胞双向排除并单列 coverage；不能称 held-out 或 inductive 泛化。
- SATURN v72-era 的 67.4% 只作旧实现对照，不进入正式主表。
- mapping v1 有 38 行 coarse/fine 标签，SHA-256 为 BE9857354778535B76D1884D004C54691DC5FF2DAA7B098D71DC719DAF583165；4 个低置信映射仍待 reviewer/导师确认。
- SAMap 合规探索结果 18 格均不超过随机或等于 majority，shuffle_p ≥ 0.98；这只能支持“当前规模/协议下未观察到稳定对齐信号”，不能写成工具普遍无效。

### 候选或待验收

- ortholog-PCA 六方向数字仍是阶段草表；统一评分器复算前不要写成正式排名。
- SAMap v98 DCS 复现因 UMAP 阶段 OOM（RC=137）停止；修复方向是 sm.run(NUMITERS=3, ncpus=1, umap=False)、统一物种前缀和重复条码规则。
- v99 远程任务声称已落盘 manifest、command、environment、sha256、18 组预测与混淆矩阵，但在完整本地回收、哈希和抽样复核前，不把 provenance 写成 complete。

## 1. 全局边界

1. 不覆盖原始 PPT，不删除旧结果，不使用 git add .，不 commit/push。
2. 不读取或保存 token、cookie、密码；DCS 页面只作用户已登录环境下的正常操作。
3. 每个 DCS 任务必须有明确任务 ID、一次性检查和退出条件；禁止对已结束任务死循环轮询。
4. 未经用户明确批准，不启动 inductive 重训、扩大物种、空间组学或大规模 GPU 任务。
5. 训练和评估协议在 manifest 中预注册：transductive 或 inductive，跑完不得事后升级。
6. 任何数字必须同时给出方法、方向、层级、分母、coverage、majority 和证据等级。
7. “已验证/已完成”只在本次运行存在文件、哈希、日志或测试证据时使用。

## 2. Wave 0：只读证据矩阵（Flash 立即执行）

### 输入

- docs/transductive-formal-v74-evidence-20260928.md
- docs/local-samap3-readonly-audit-20260927.md
- docs/method-to-evaluation-matrix-20260926.md
- docs/paper-method-evidence-20260924.md
- config/eval-manifest-v73.json
- config/heart-celltype-map-v1.tsv

### 动作

1. 建立 confirmed / candidate / blocked / needs-reviewer 四列矩阵。
2. 对每个数字记录：来源文件、任务/运行 ID、表示层、query/reference 角色、分母、coverage、置换定义。
3. 明确哪些内容可进 PPT 主表、哪些只能进脚注或后续计划。
4. 只读完成后停止，不提交新 DCS 任务。

### 验收门

- SATURN v97g 六方向数字和 coverage 与证据文档逐项一致。
- SAMap 18 格全部标 exploratory/candidate，不得标 formal benchmark。
- PCA 六方向标“阶段草表，待统一复算”。
- 显式列出 reviewer 签名、v99 本地回收、inductive 留出的阻塞关系。

## 3. Wave 1：v99 provenance 只读回收

### 目标

把远程声称存在的产物变成本地可核验的证据包，零训练成本。

### DCS 动作

只读读取 /data/work/course5_v99/ 下的：

- manifest.json
- metrics.json
- predictions/ 18 组逐细胞 JSON
- confusion/ 18 组混淆矩阵
- sha256.tsv
- environment.txt
- command.txt
- saturn_src_tree_sha256.tsv
- course5_v99_readout.ipynb

### 本地验收

1. 下载到新目录，不覆盖已有 v97f/v97g。
2. 按 sha256.tsv 重算全部文件哈希。
3. 抽查人→鼠 coarse：逐细胞记录、分母、coverage、混淆矩阵三者一致。
4. 检查 manifest 中协议标签、表示层、mapping SHA、query/reference 角色是否齐全。
5. 记录 v99 与 v97g 的数字差异及差异来源；不得把语义差异抹平。

### 停止条件

- 任何哈希不匹配、文件缺失、协议标签缺失：停止，不重跑训练，反馈阻塞证据。
- 仅在本地回收和验收全绿后，才把 provenance 从 candidate 改为 confirmed。

## 4. Wave 2：SAMap v98 单次修复重跑（需用户/Flash 明确执行）

### 预注册修复

- sm.run(NUMITERS=3, ncpus=1, umap=False)。
- 所有 barcode 使用 hu|、mo|、zf| 前缀；禁止拼接器自动生成的 -1 作为身份规则。
- mouse 前缀只允许一个命名空间，修复 mo/ms 冲突。
- coarse/fine 分别记录 unmapped、truth_na、excluded 和 coverage。
- 输出逐细胞预测、混淆矩阵、运行命令、版本、输入输出 SHA-256。

### 资源与停止门

- 首选 DCS 1c4g、ncpus=1；不启用 UMAP。
- 只提交一次修复任务；RC=137、导入错误、输出缺失或 truth_na>0 任一发生，停止并反馈，不自动重试。
- 通过门：6 个方向 × 3 层均有预测、混淆矩阵和 coverage，truth_na=0，条码无重复，协议标注完整。

## 5. Wave 3：ortholog-PCA 统一评分器复算

### 固定协议

- 只使用 1:1 直系同源基因；明确基因集合版本和缺失值规则。
- PCA50、固定 seed、相同 KNN15/cosine/倒距离加权评分器。
- 复用同一 mapping v1、同一 query/reference 角色、同一 majority 和置换检验。

### 验收门

- 六方向都有逐细胞预测、混淆矩阵、coverage 和 SHA。
- 早期草表数字与复算数字的差异有解释；若差异无法解释，草表保持 candidate。
- 通过后才可把 PCA 列从“阶段草表”改成 confirmed baseline。

## 6. Wave 4：mapping reviewer 签认

1. 把 docs/reviewer-signoff-request-mapping-v1.md 发给导师或组内 reviewer。
2. 请求对 4 个低置信映射逐项回复“确认/修改/暂缓”。
3. 任何修改都生成新版本和新 SHA，不覆盖 v1。
4. 没有人工签名时，mapping 只能标 needs-reviewer，不得升级为正式 benchmark 依据。

## 7. Wave 5：inductive 最小试验（必须用户批准）

### 目的

真正回答“未见过目标细胞/物种时能否泛化”，与前面的 transductive 结果分开。

### 最小设计

- 留一物种或分层留出；先做 3 物种 × 1 个留出策略的最小试验。
- 训练阶段禁止读取目标物种标签；评估阶段只在预注册的 query 上运行。
- 先写 manifest：预算、镜像、seed、输入 SHA、停止条件、输出清单，再提交 DCS。

### 通过门

- query/reference 角色表完整；无 self/重复条码；目标标签未进入训练路径。
- 逐细胞预测、混淆矩阵、majority、置换检验和 provenance 全部落盘。
- 只有通过门后才允许使用“inductive benchmark”或“泛化性能”措辞。

## 8. Wave 6：统一比较矩阵与 Word 报告

最终矩阵至少包含：方法、表示层、训练协议、方向、层级、accuracy、coverage、majority、shuffle_p、seed、资源、证据等级、局限性。

报告结构建议：

1. 研究问题与老师意见转化；
2. 数据、mapping 和角色表；
3. 统一评分公式；
4. 三种方法和论文方法的适用边界；
5. transductive 结果；
6. SAMap/PCA 对照；
7. sensitivity、消融和失败分析；
8. inductive 结果（若通过门）；
9. 局限、算力和可复现性；
10. 附录：manifest、命令、哈希、混淆矩阵。

## 9. Flash 第一条执行指令（可直接复制）

~~~text
请在 D:\\projects\\course5-prep 阅读：
- docs/superpowers/plans/2026-09-30-course5-phase1-revision-and-flash-plan.md
- docs/transductive-formal-v74-evidence-20260928.md
- docs/local-samap3-readonly-audit-20260927.md
- docs/method-to-evaluation-matrix-20260926.md

本轮只执行 Wave 0：
1. 读取并核对证据；
2. 输出 confirmed / candidate / blocked / needs-reviewer 矩阵；
3. 不提交新 DCS；
4. 不训练、不启动 GPU；
5. 不修改旧结果；
6. 不 commit/push；
7. 按“做了什么—证据—测试—未完成—下一步请求”反馈并停止。
~~~

## 10. Flash 每轮反馈模板

~~~text
本轮波次：Wave X
做了什么：
证据文件/任务 ID：
关键数字及口径：
测试与验收门：
失败/阻塞：
是否产生新 DCS 任务：是/否
是否修改旧结果：是/否
下一步请求：
~~~

## 11. 当前交接结论

本阶段 PPT 已按老师要求加入“数字来源、含金量、方法比较和边界”四类解释；后续工作按 Wave 0→6 推进。Codex 负责审查、口径和验收，Flash/Claude/zcode 负责重活。除用户明确批准的 Wave 外，不扩大计算范围。

