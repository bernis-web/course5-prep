# 课题 5 审计覆盖矩阵（2026-09-24）

本表把课题 5 当前目标拆成可核验的要求，区分“已由本地证据证明”“仅有探索性证据”和“仍缺原始证据”。
它是交接和质量门文件，不是实验结果，也不授权启动 DCS。

## 判定规则

- **已核实**：有本地源码、测试输出或可追溯论文来源直接支持，且结论范围不超过证据范围。
- **探索性**：有运行汇总或同一批数据上的结果，但缺少独立留出、完整 provenance 或统一标签映射。
- **待补证据**：manifest 中保持 `pending`/`null`；不得用推测填充，也不得据此宣称正式 benchmark。

## 覆盖矩阵

| 要求 | 当前判定 | 现有证据 | 仍缺什么 | 放行条件 |
|---|---|---|---|---|
| 核实 SATURN 的 miner 路径 | 已核实（当前源码） | `train-saturn.py` 和 `miners/triplet_margin_miner.py` 的源码审计：当前构造的 miner 为 `cross_species`，对应 cross-species triplet 分支；命令行没有独立 `miner_type` 参数 | v71 是否使用同一源码版本/补丁；不同 miner 只能来自源码变化或其它入口 | 记录源码 commit/补丁 hash，并与 v71 运行目录或镜像中的源码核对 |
| 核实 `use_ref_labels` 是否参与训练 | 部分核实（当前源码） | 默认值为 `False`；`train()` 只有显式开启时才把 `ref_labels` 传入 miner，但当前 `cross_species` triplet 索引函数随后按普通 `labels` 取正负样本，未使用 `ref_labels` | v71 原始命令、完整日志、源码版本/补丁 hash | 明确记录 flag、源码版本、训练日志分支和实际 miner 输入 |
| 核实 macrogene 是否冻结 | 部分核实 | 源码默认 `unfreeze_macrogenes=False`；冻结时使用预训练 macrogene 输入 | v71 原始命令/日志 | manifest 填入实际 flag 和输入表示 |
| 核实 v71 训练规模和产物 | 探索性 | `docs/saturn-smoke-evidence-20260922.md` 记录三物种、细胞数、HVG 候选、1000 macrogenes、50 epochs 及产物描述 | DCS task ID、完整日志、输入/输出 hash、实际路径 | provenance 字段全部从原始日志补齐 |
| 核实 v72 是否为独立 benchmark | 未达到 | v72 汇总来自 v71 Final AnnData；当前只能归类为 transductive/in-sample 探索 | query/reference barcode、留出规则、逐细胞预测、独立训练记录 | 有明确 inductive 留出或正式声明为 transductive 并不作泛化结论 |
| 核实 v72 使用的表示层 | 部分达到（本地运行汇总） | `saturn-smoke-evidence-20260922.md` 将 v72 记为 1000 维 macrogene latent；源码同时确认 `X` 与 `obsm["macrogenes"]` 含义不同 | v72 原始命令或显式提取记录、表示层 hash | 在 manifest 中将“本地汇报层”与“原始命令确认层”分开，最终固定 `X` 或 `obsm/macrogenes` |
| 统一 exact/mapped 标签评分 | v1 已冻结，人工 reviewer 签名仍待补 | `heart-celltype-map-v1.tsv` 有 38 行；`docs/celltype-map-validation-v1.md` 记录 g5-pseudo-v84e 的 ortholog-pseudobulk 独立核验（8/8 人鼠映射进入前 5，5 对 rank-1）；v73/v74b 已给出 coarse/fine、majority baseline、coverage 方向的汇总；评估器输出 exact/mapped、F1、top-k、coverage 和混淆矩阵 | TSV reviewer 字段签名、原始标签列和 barcode 清单；低置信度/unknown 的正式拒答规则 | 固定 sha256 的 v1 映射进入 manifest；人工 reviewer 完成签名；低置信度/unknown 不强行归类 |
| 防止 barcode 泄漏 | 接口已就绪，数据未就绪 | 评估器排除重复 barcode、query/reference 交集并输出排除清单 | 实际 barcode 清单及来源文件 | 清单 hash 落入 manifest，交集为 0 |
| 评估 transductive 与 inductive | 计划已形成 | `eval-manifest-v73.json` 和下一轮计划并列定义两种协议 | inductive 实际运行尚未完成 | 两种协议使用同一标签映射、指标和拒答规则 |
| 复现 macrogene 容量差异 | 计划已形成 | 已识别 v62→v71 同时改变多项变量；计划固定其它变量，比较 16/128/1000、每点 3 seeds | 消融输入和结果 | 只有在本地接口验收、证据完整且用户明确启动后才运行 DCS |
| ortholog-PCA 零整合基线 | 已有探索性结果 | v75c/v78b 汇总了 6 个方向的 1:1 ortholog-PCA 对照；5 个方向高于 SATURN，1 个方向 SATURN 胜出 | 原始输入/ortholog hash、逐细胞输出、同协议独立评估 | 与 SATURN/scVI 使用相同 barcode 角色、标签映射、k 和拒答规则后再进入正式比较 |
| ESM2 蛋白信号与 seed 稳定性 | 已有探索性结果 | v79-v83 记录了 ESM2 行置换和 seed0/1/2；人鼠方向有信号，鱼方向出现双峰/剧烈不稳定 | 原始任务 provenance、完整 seed 输出和资源记录 | 报告每个 seed、均值/标准差和失败/异常 seed，不以单次最佳结果代表方法 |
| 物种内 ceiling | 已有探索性结果 | SATURN 1000d 物种内 50/50 split 低于 scVI 对照 | split 清单、逐细胞输出和版本 provenance | 将潜空间上限作为独立诊断，不与跨物种泛化分数混合排名 |
| 纳入 HEART 论文方法证据 | 已核实为论文级证据 | `paper-method-evidence-20260924.md` 和 `source-notes.md` 记录 27 物种背景及方法边界 | 不能把论文作者结果当本项目真值；DCS 挂载路径仍缺 | 报告中单列“外部论文背景”和“本项目实测” |
| 纳入 LBSPA 论文方法证据 | 已核实为论文级证据 | 记录 10x Multiome/CG000366、8,000 nuclei/反应、20,000 paired-end 100-bp reads/nucleus、分阶段 QC、Harmony/scVI 和同源基因集合；方法证据卡注明 PDF SHA-256 | snRNA 数据路径、实际批次/QC 分布和 scRNA 主结论仍缺 | scRNA 主评估完成后再小规模启动；空间数据不进主 benchmark；snRNA 单列报告，不能把论文 QC 或同源集合直接当本项目固定超参 |
| 近期方法对照 | 已形成方法卡 | BENGAL、scSpecies、CAMEX 的 DOI/期刊入口与适用边界已记录 | 软件许可证、依赖、离线可运行性未核验 | 首轮不默认加入；若纳入需单独完成环境和资源 preflight |
| 最终 Word 报告边界 | 已确定 | Markdown/JSON 作为审计源文件，最终交付为 Word | 正式 benchmark 结果和质量门尚未完成 | 先通过 provenance、协议和指标质量门，再生成 Word 素材 |

## 当前不可越过的硬门槛

1. v71/v72 原始 DCS 命令、任务 ID 和完整日志；
2. Final AnnData 及输入/输出 SHA-256；
3. reference/query barcode 及标签列；
4. 固定 sha256 的 mapped cell-type v1、其 pseudobulk 验证报告和人工 reviewer 签名；
5. 明确 `X` 或 `obsm["macrogenes"]` 的评估层；
6. 至少一个真正的 inductive 留出协议，或在报告中明确将现有结果限定为 transductive 探索。

## 下一位执行者的最短路径

1. 先只读导出 DCS provenance，不新建任务；
2. 先用 DCS 只读取证补齐 task、命令、日志、Final AnnData 和 barcode provenance；
3. 以已冻结的 `config/heart-celltype-map-v1.tsv` 和 `docs/celltype-map-validation-v1.md` 为基线，补人工 reviewer 签名后，再用显式 NPZ bundle 重跑 exact/mapped 双评分；
4. 用同一协议复核 ortholog-PCA、SATURN、scVI 和 seed 汇总，再决定是否申请小规模容量消融；
5. scRNA 主结论形成前，不启动 LBSPA snRNA 或空间数据流程。

## 2026-09-25 目标级收口检查

| 目标要求 | 当前判定 | 证据 | 未闭合原因 |
|---|---|---|---|
| SATURN v71 标签/Triplet 路径 | 当前 checked-in 源码已核实 | `docs/local-saturn-source-fingerprint-20260924.tsv`、`wheelhouse/saturn-src/train-saturn.py`、`miners/triplet_margin_miner.py`、`utils/loss_and_miner_utils.py` | 尚未取得 v71 DCS 运行时源码/镜像 hash，不能把本地源码等同于 v71 运行时 |
| v72 是否独立评估 | 已完成边界判定：只能称 transductive/in-sample 探索 | `docs/saturn-smoke-evidence-20260922.md`、`config/eval-manifest-v73.json`、`docs/dcs-v71-v72-evidence-request-20260924.md` | 缺 query/reference barcode、留出清单、逐细胞预测和原始命令，无法升级为 held-out benchmark |
| 老师推荐论文与近期方法证据 | 论文级证据已分层 | `docs/paper-method-evidence-20260924.md`、`docs/source-evidence-index-20260924.tsv`、`docs/source-notes.md` | HEART 原 PDF 当前不可从原始 E 盘路径读取；其课程参数继续按 B 级历史材料处理 |
| 下一轮计划与证据缺口 | 已形成可执行清单 | `docs/superpowers/plans/2026-09-24-course5-next-round.md`、本表及 `docs/audit-and-next-round-20260924.md` | 只有 DCS 只读 provenance、人工 reviewer 签名和真实 barcode 角色补齐后才能进入正式 benchmark |

因此本轮审计阶段的正确结论是“本地方法路径、论文边界和下一轮协议已收口；DCS 运行 provenance 仍是正式 benchmark 的硬阻塞”，而不是把当前材料误报为实验已经完成。
