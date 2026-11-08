# 课题 5 审计阶段逐项验收表（2026-09-26）

本表用于判断审计阶段是否达到完成门槛。它不授权创建 DCS 任务，也不把探索性结果升级为正式 benchmark。

| 目标要求 | 当前证据 | 判定 | 完成前还需要 |
| --- | --- | --- | --- |
| 核实 SATURN v71 的 Triplet/miner 路径 | docs/local-saturn-triplet-audit-20260925.json；2026-09-26 静态审计复跑；checked-in SATURN 源码；76 个测试通过 | 已核实当前 checked-in 源码（复跑时源码 SHA-256 与报告一致，`ref_labels` 未参与检测到的 triplet 选择）；未核实 v71 运行时 | v71 原始命令、运行时源码/补丁或镜像 digest、实际 use_ref_labels/unfreeze_macrogenes/seed |
| 判断 ref_labels 是否实际参与 v71 选择逻辑 | 静态审计显示参数可传入，但 get_species_triplet_indices() 的选择仍按普通 labels | 当前源码边界已核实；不能外推到 DCS v71 | 原始命令和运行时日志/源码证据 |
| 核实 v72 是否独立评估 | DCS 页面与日志显示 v72 完成、含 macrogenes 和 KNN 数字；`saturn-smoke-evidence-20260922.md` 另提供参数级交叉核对；无 query/reference 角色表 | 只能称 transductive/in-sample exploratory evaluation | query/reference barcode、留出规则、评估命令、self/重复 barcode 排除记录 |
| 恢复 v71/v72 文件与命令 provenance | `docs/dcs-provenance-recovery-v95-20260927.md`；`docs/dcs-provenance-recovery-v96-20260928.md`（v96 完成，日志恢复 Final AnnData 哈希、4606×256 形状、标签参数与 `obsm/macrogenes` 评估层） | 评估层与关键 Final AnnData 哈希可确认；完整 v95/v96 JSON 与 v71 原始提交命令仍未读回 | 人工 reviewer、完整条码角色表、self/重复条码排除记录、原始 run 字段；不得用 v95/v96 任务号替代 |
| 补齐 HEART 论文证据 | docs/paper-method-evidence-20260924.md；PubMed/论文入口；课程参数单列为 B 级 | 论文级证据已分层 | 不得用论文结果填充本项目 manifest 或真值 |
| 补齐 LBSPA 论文证据 | 同上；本地 PDF SHA-256、Multiome、NovaSeq、分阶段 QC、scRNA/snRNA/空间边界已记录 | 论文/本地材料证据已分层 | snRNA 数据路径和本项目 scRNA 主结论仍待后置阶段 |
| 纳入近期跨物种方法启发 | docs/method-to-evaluation-matrix-20260926.md；BENGAL、scSpecies、CAMEX 字段化 | 方法启发已转成评估字段 | 软件许可证、依赖和资源 preflight；不默认进入首轮 |
| 本地三物种 SAMap operationalization | docs/local-samap3-readonly-audit-20260927.md；源文件/嵌入/脚本哈希、4606×150 表示层、3 个跨物种 barcode 碰撞、74 个未排除 mapped-unmapped 细胞均已复核 | 只能作为 exploratory exact-layer 结果，不能进入正式 mapped 排名 | 先修正 barcode 回连与 fine-mapped 排除规则、输出逐细胞预测，再本地重跑；仍不补 v72 provenance |
| 形成下一轮可执行计划 | docs/superpowers/plans/2026-09-24-course5-next-round.md；docs/audit-coverage-matrix-20260924.md | 已形成，执行仍受门控 | provenance、barcode、reviewer 和 manifest 通过后再启动 |
| 保持安全边界 | cloud_actions_allowed=false；manifest validator；无本轮 DCS 提交/重试/上传 | 已核实 | 后续任何真实运行仍需用户明确启动和共同确认 |

## 当前完成结论

审计阶段的本地方法、论文边界、DCS 历史任务定位和下一轮协议已经具备可交接性；但“v71/v72 可复核运行 provenance”和“v72 独立评估证明”尚未满足完成门槛。因此目标继续保持 active，不标记 complete，也不把现有 v72 数字写成正式泛化结果。

## v74 transductive-formal 工具链状态（2026-09-28）

按 `docs/superpowers/plans/2026-09-28-flash-transductive-formal.md` 完成 Task 1–4：验证器部分闭环识别（91 测试全绿）、映射/条码命名空间契约、方向显式 NPZ bundle 构建器、六方向 runner 与 result-index。Task 5 真实数据执行**BLOCKED**：SHA-256=`20cf807f…` 的 v71 Final AnnData 仅存在于 DCS 工作区，公开只读接口无二进制下载通道（`/offline/subTask/logs` 只覆盖日志文本；文件下载 API 未在公开前端暴露）。按计划，任何 DCS 提取任务（v97）需用户另行明确批准；v73 manifest 保持 `evidence_status=pending`。

## 下一位执行者的最短取证顺序

1. 从 DCS 只读页面或原始提交记录取得 v71/v72 原始命令、完整日志路径和文件元数据。
2. 取得输入/输出 SHA-256、表示层提取记录和 query/reference barcode 文件；无法取得的字段保持 pending。
3. 若保留 SAMap 对照，先按 docs/local-samap3-readonly-audit-20260927.md 修正 barcode 回连、`fine_mapped_label` 排除和逐细胞输出，再本地重跑；不得沿用 printed 聚合分数进入正式排名。
4. 由 reviewer 签名冻结 cell-type mapping v1 后，生成显式 NPZ bundle，先跑 transductive 与 inductive 双协议的本地评分。
5. 只有上述字段和测试门通过后，才讨论 macrogene 容量消融、多 seed、scVI/SATURN/PCA 对照及后置 snRNA。
