# v71/v72 DCS 只读取证清单（2026-09-24）

本清单供组员在已获授权的 DCS 页面、任务详情和日志查看器中使用。它只要求读取元数据和运行记录，不要求新建任务、上传数据、下载原始矩阵或修改云端对象。

## 先记住的边界

- 不把浏览器地址栏、项目首页或“已登录”状态当作运行证据。
- 不在截图、命令、日志或仓库中记录密码、cookie、token、API key 或完整登录链接。
- 未找到的内容写 `pending`，不要根据任务名称、文件夹名或论文结果猜填。
- 只读查询完成后，把脱敏后的字段、文件名、task ID 和 hash 回填到 manifest；原始表达矩阵不进入 Git。

## A. v71 SATURN 训练任务

| 要查的项目 | 最小证据 | 回填位置 |
|---|---|---|
| DCS task ID、状态、开始/结束时间 | 任务详情页或日志头部的脱敏标识 | `config/eval-manifest-v73.json:run.dcs_task_id` 及 provenance 记录 |
| 原始命令和配置 | 命令行、参数面板或可复制的任务配置；至少包含物种清单、`num_macrogenes`、HVG、epochs、seed、miner、`use_ref_labels`、`unfreeze_macrogenes` | `run.original_command`、`training_parameters` |
| 源码版本/补丁 | SATURN 源码 commit、镜像内源码目录 hash，或提交前后的补丁摘要 | provenance 记录；用于确认 `miner_type` 是否仍为当前 checked-in 分支 |
| 输入对象 | 每个物种的只读路径/文件名、对象格式、细胞数、基因数、标签列、批次列 | `datasets[]` |
| Final AnnData | 产物文件名/路径、对象大小、完成状态 | `datasets[].final_anndata_path` 和 run artifact 记录 |
| hash | 输入清单、Final AnnData、barcode 清单的 SHA-256 | 对应 `*_sha256` 字段 |
| 训练产物 | Final AnnData、epoch scores、triplets、celltype id 等文件名及成功/失败原因 | run artifact 记录；不上传原始内容 |

## B. v72 评估任务

| 要查的项目 | 最小证据 | 回填位置 |
|---|---|---|
| v72 task ID 和原始命令 | 评估任务详情/日志中能看到的命令和参数 | run 记录及 manifest provenance |
| reference/query 角色 | 每个物种的角色、barcode 清单文件名和 hash | `config/barcode-roles-v73.tsv`、`datasets[].query_or_reference` |
| 表示层 | 明确是 `X` 还是 `obsm["macrogenes"]`，并记录维度 | `representation.evaluation_layer` |
| 评估协议 | 是否训练阶段看过目标表达、目标标签是否进入训练、是否为同一 Final AnnData | `evaluation_protocol.transductive/inductive` |
| 逐细胞输出 | 预测标签、真值、邻居 barcode、置信度、弃权字段是否存在 | `metrics.prediction_table_path` |
| 评分规则 | exact/mapped 标签、k、距离、未知标签和弃权阈值 | `metrics` 及标签映射表 |

## C. 只读验收规则

拿到记录后，先做以下检查，再更新状态：

1. v71 和 v72 的 task ID 不为空，且日志时间顺序合理；
2. 输入对象、Final AnnData 和 barcode 清单都有文件名或路径及 hash；
3. reference/query barcode 交集为 0，重复 barcode 有明确排除记录；
4. 评估层与维度和训练产物含义一致；
5. 若目标表达进入同一整合过程，只能标记为 transductive，不能写成 held-out benchmark；
6. 标签映射每一行都有来源、置信度和 reviewer，未知/歧义类别不强行映射；
7. 只有当这些检查通过，`evidence_status` 才能从 `pending` 改为 `confirmed`。

## D. 发给老师或管理员的最小问题

如果 DCS 页面没有显示上述信息，只集中询问以下 9 项；只需要元数据和配置，不需要下载原始表达矩阵：

1. v71/v72 对应的课程任务 ID 或可访问的任务详情入口；
2. v71/v72 实际提交的原始命令或任务配置导出（至少含物种、HVG、macrogenes、epochs、seed、miner、`use_ref_labels` 和 `unfreeze_macrogenes`）；
3. 运行时 SATURN 源码 commit/补丁摘要，或分析镜像名称与 digest；
4. Final AnnData、epoch scores、triplets 和评估输出的只读路径/文件名，以及可提供的 SHA-256；
5. v72 reference/query 的物种和 barcode 角色，及 barcode 清单文件名/哈希；
6. v72 实际使用的表示层（`X` 或 `obsm["macrogenes"]`）和维度；
7. v72 是否排除 self barcode、重复 barcode，是否与训练阶段共享目标表达或标签；
8. 允许使用的 cell-type 标签列、同源映射依据和 reviewer；
9. 是否有留一物种或独立 query 的正式评估记录；若没有，请明确回复“无”。

不要在问题中附带密码、cookie、token、API key 或完整原始数据。

## E. 证据到齐后的本地动作

1. 只把脱敏 provenance 写入 `config/eval-manifest-v73.json` 和两个 TSV 模板；
2. 由显式提取步骤生成 NPZ bundle，并记录提取命令和 hash；
3. 用 `scripts/evaluate_cross_species_transfer.py` 分别运行 exact/mapped、transductive/inductive；
4. 测试、preflight 和人工抽样通过后，再讨论是否申请容量消融；
5. 在 scRNA 主结论前，不启动 LBSPA snRNA 或空间流程。
