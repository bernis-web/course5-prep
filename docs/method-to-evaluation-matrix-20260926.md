# 论文方法到课题 5 评估字段矩阵（2026-09-26）

本文件把老师要求“看看新论文如何测序、采用什么新颖思路”转成可执行的评估字段。它是协议设计和报告写作依据，不是 DCS 运行结果，也不授权创建或提交云任务。

## 使用规则

- 外部论文只决定“应该记录什么、如何分层比较”；不能填充本项目的 task ID、命令、hash、barcode 或真值。
- 每个指标都要同时记录适用协议（transductive 或 inductive）、表示层（`X` 或显式 `obsm` 键）和证据来源。
- 首轮仍以 scRNA 为主；snRNA 单列，空间数据不进入主排行榜。

## 核心方法映射

| 来源/方法 | 论文方法启发 | 本项目必须落库的字段 | 最低输出 | 当前状态/边界 |
| --- | --- | --- | --- | --- |
| BENGAL | 把跨物种整合拆成 species mixing、biology conservation、annotation transfer，并按物种数和演化距离组织任务 | 物种对与演化距离分层、batch/species 标签、细胞类型标签、邻居图/latent 版本、评估协议 | mixing 指标、biology conservation 指标、exact/mapped annotation transfer、ALCS（若实现并记录版本） | 适合作为主评估框架；不能只报一个 accuracy |
| scSpecies | context→target 是有方向的迁移；context 覆盖不足时不能强行给 target-only 类型贴标签 | `context_species`、`target_species`、context 覆盖率、target-only 类型、abstention 规则、共享同源基因版本 | 每个方向的 coverage、abstention、exact/mapped F1、target-only 清单 | 适合 inductive 留一物种；不应写成对称混合分数 |
| HEART | 用近缘与远缘动物心脏共同检验保守结构和宏演化差异 | 类群/演化距离层、心脏细胞类型字典、物种内样本平衡、同源标签映射来源 | 分层 transfer、混淆矩阵、每类 coverage；外部论文只作背景 | 论文级证据，不是本项目真值；当前三物种只能算 pilot |
| LBSPA | scRNA、snRNA、空间转录组分开处理，并记录测序/核捕获/QC 阶段差异 | `modality`、样本/批次、捕获比例、阶段性 QC 版本、同源基因集合、空间/单核是否进入主榜 | scRNA 主榜；snRNA 单列的 coverage/F1；空间只做后置说明 | 先完成 scRNA；snRNA 不能直接混入 HEART scRNA 总排名 |
| CAMEX | many-to-many 同源关系可用异构图表达，但细胞节点初始化仍可能依赖一对一输入 | ortholog relation type、one-to-one/many-to-many 版本、边类型、初始化特征来源、许可证/依赖 | 映射版本对照、资源记录、失败/不可运行原因 | 当前只做方法卡和依赖 preflight，不纳入 1c4g 首轮主 benchmark |
| SATURN（本项目） | Triplet、macrogene 表示和跨物种训练路径必须与运行时 provenance 分开核实 | miner 类型、`use_ref_labels`、`unfreeze_macrogenes`、seed、源码/镜像 hash、输入/输出 hash、表示层 | 训练日志、逐细胞预测、exact/mapped 指标、容量/seed 摘要 | 当前 checked-in 源码已静态审计；v71 运行时仍缺完整 provenance |

## 统一结果表字段

每个“方法 × 物种方向 × 协议 × seed”至少保留：

1. `method`, `run_id`, `protocol`, `query_species`, `reference_species`；
2. `representation`, `representation_key`, `representation_sha256`；
3. `label_mapping_version`, `label_mode`（exact/mapped）、`ortholog_manifest_sha256`；
4. `n_query`, `n_reference`, `n_excluded_duplicate`, `n_excluded_overlap`；
5. `accuracy`, `macro_f1`, `micro_f1`, `top_k`, `coverage`, `abstention`；
6. 每类支持数、每类 coverage、混淆矩阵，以及失败/异常说明；
7. 对 BENGAL 类指标：species mixing、biology conservation 和 annotation transfer 分列；
8. 对 scSpecies 类指标：context coverage、target-only 类型、方向性和拒答率分列；
9. 对 LBSPA：`modality`、QC 阶段和捕获比例必须进入分组键，禁止与 scRNA 静默合并。

## 对 v73 的直接约束

- `config/eval-manifest-v73.json` 在原始命令、barcode 角色、表示层、输入/输出 hash 和 reviewer 签名补齐前继续保持 `evidence_status=pending`。
- v72 现有数字只能写作 transductive/in-sample exploratory evaluation；不能填入 `held_out` 或 `independent_generalization`。
- 下一次真实运行先做 2–3 物种流程验收；正式效果评测再加入近缘、远缘和不同类群组合，并使用同一评分合同。
- 容量消融（16/128/1000 macrogenes）和多 seed 运行必须在 provenance 门通过后单独申请，不能用现有一次性结果替代。

## 证据来源

- 论文分层与 DOI/PMID：`docs/paper-method-evidence-20260924.md`。
- DCS v71/v72 只读页面证据：`docs/dcs-browser-offline-task-audit-20260926.md`、`docs/dcs-offline-task-history-20260926.md`。
- 当前 manifest 质量门：`config/eval-manifest-v73.json`、`scripts/validate_eval_manifest.py`。

