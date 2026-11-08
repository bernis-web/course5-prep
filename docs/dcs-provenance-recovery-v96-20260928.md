# v96 DCS 只读读回记录（2026-09-28）

## 结论

v96 只读任务已完成，平台任务日志成功恢复出 v95 JSON 的一个中段切片。这个切片足以确认 v71/v72 相关 Final AnnData 的路径、SHA-256、形状、物种计数、重复条码计数，以及 SATURN 命令模板中的标签参数。但它不是完整的 v95/v96 JSON，也不能替代原始 v71 提交记录。

因此，本轮只做两项升级：

1. v72 评估表示层可以确认为 `obsm["macrogenes"]`，维度为 1,000；
2. v72 继续定性为 **transductive / in-sample exploratory evaluation**：训练与评估使用同一细胞集合，目标物种标签路径进入训练/整合流程。

manifest 的 `evidence_status` 仍必须保持 `pending`；不得把 v95/v96 任务号、日志切片或文件哈希冒充 v71/v72 原始 run 字段。

## v96 任务元数据

以下字段来自 2026-09-28 通过 DCS 前端只读接口读取的子任务详情；本文件只保存脱敏元数据，不保存 token、cookie 或其他凭据。

| 字段 | 值 |
| --- | --- |
| 项目 | `P20260920085640327` |
| 批次任务 | `2104407677481881602` |
| 子任务 | `2104407677498658818` |
| 任务名 | `g5-provenance-v96-readout-readonly-1` |
| 状态 | `Completed` |
| 创建时间 | 2026-09-28 11:07:43 |
| 开始时间 | 2026-09-28 11:29:09 |
| 结束时间 | 2026-09-28 11:29:09 |
| 计算资源 | `1c4g` |
| 分析镜像 | `SATURN--22` |

本地脚本 `scripts/dcs_provenance_v96_readout.py` 的 SHA-256 为：

```text
31018e53eaeff2fee98ea88f0fa75a6f538c9581c462f5c732fdcbe372dc8ab4
```

该脚本声明并经本地测试复核：只读取 v95 的 out/err/command 三个文件；只写入 v96 自己的 JSON、错误日志和命令记录；不删除、移动或重写旧产物。

## 平台日志恢复到的关键证据

平台子任务日志接口返回的 `message` 长约 39,642 字符。它从 v96 JSON 的 `key_lines` 中段开始，到 `h5ad_rows` 结束，缺少 `schema_version`、`self_record`、`targets`、`v95_json_summary` 的头部和 `compact_file_rows` 等字段。因此它是一个截断日志切片，不是完整 JSON 读回。

### Final AnnData

日志切片确认以下对象：

```text
/data/work/saturn_out_real3_h/saturn_results/test256_data_human_saturn_input_hvg_mouse_saturn_input_hvg_zebrafish_saturn_input_hvg_org_human_seed_0.h5ad
SHA-256: 20cf807fcaa5e8ed9ac65a28d50e781c82c9c48cdac9b7a1820dcf74bdf5143f
shape: 4606 × 256
duplicate_barcode_count: 6
species counts: human=1528, mouse=1535, zebrafish=1543
```

同目录相关输出还包括：

| 文件 | SHA-256 |
| --- | --- |
| `..._seed_0_ep_25.h5ad` | `686fdf433f7d564322be068600cf1f5137bb1864c4d3252d61606f0de99569ed` |
| `..._seed_0_ep_50.h5ad` | `20cf807fcaa5e8ed9ac65a28d50e781c82c9c48cdac9b7a1820dcf74bdf5143f` |
| `..._seed_0_pretrain.h5ad` | `4526d5bd93c0a0e770c7e09560701ddecb2c273e3b332c7e52f8eb00a43c609d` |

其中 `ep_50` 与无 epoch 后缀的 Final AnnData 哈希一致，支持其为最终评估对象的既有判断。

### 标签参数与表示层

日志切片中的 SATURN 源码命令模板显式包含：

```text
--in_label_col={args.in_label_col}
--ref_label_col={args.ref_label_col}
--num_macrogenes={args.macrogenes}
--seed=
```

可见源码片段同时显示：

```text
in_label_col="cell_type"
ref_label_col="cell_type"
```

这与既有 v72 评估代码和日志中的 `obsm_keys=["macrogenes"]` 相互印证：v72 使用的是 `obsm["macrogenes"]` 表示层，而不是原始表达矩阵 `X`。该结论只解决评估层 provenance，不证明评估独立，也不补出 query/reference 留出。

## 文件树与任务目录限制

通过 DCS 前端文件树接口确认：

- 持久工作区 `online/` 有 144 个条目；
- 可见 `dcs_provenance_v96_readout.py`、`g5-provenance-v96-command.txt`、`g5-provenance-v95-command.txt`、`dcs_provenance_v95.py`、`eval_v72.py`、`eval_v72_out.txt`、`prep_real_v60.py` 和 `saturn-src/`；
- 不可见 `g5-provenance-v96-out.json`、`g5-provenance-v96-err.log`、`g5-provenance-v95-out.json`、`g5-provenance-v95-err.log`；
- v96 任务目录 `.../task/2104407677481881602/2104407677498658818` 存在但为空。

文件内容接口对 `.ipynb` 可返回内容，但对 `.json` 和 `.txt` 的多次尝试均返回 `data: null`。因此不能通过该接口直接读取 v95/v96 输出或命令文本。

上述“不可见/为空”只能说明页面可见的持久文件树和任务目录没有同步这些容器内 `/data/work` 产物，不能证明容器内文件未生成。

## 对 manifest 的影响

本轮允许的低风险更新：

- `representation.evaluation_layer`: `pending` → `obsm/macrogenes`；
- `provenance.source_evidence`: 加入本文件。

以下字段必须继续 pending 或为空：

- v71/v72 原始 DCS 任务号与完整提交命令；
- v71 输入/输出完整清单和正式 run 字段；
- 条码角色表、self/重复条码排除记录；
- 人工 reviewer 签名；
- transductive/inductive 新协议运行结果。

特别地，v95/v96 的任务号只能证明“取证任务”的来源，不能填入 `run.dcs_task_id`；Final AnnData 哈希可以进入证据文档，但在完整上下文核验前不直接把 manifest 升级为 confirmed。

## 仍不可恢复的协议缺口

v96 只能恢复文件、命令片段和哈希类 provenance。以下缺口不是证据丢失，而是 v72 原协议中从未存在：

- 独立 query/reference 留出；
- v72 self/重复条码排除记录；
- 完整条码角色表。

这些只能通过按 v73 冻结协议重跑或重新评估来产生，不能靠后续取证补造。

## 下一步

1. 由人工 reviewer 冻结并签名 cell-type mapping v1；
2. 生成带物种前缀的完整条码角色表，并在评分器中断言无 NA、无跨物种重复；
3. 对现有 Final AnnData 执行 `transductive-formal` 重评：逐细胞预测、双层标签准确率、macro/micro F1、top-k、coverage、混淆矩阵；
4. 通过 manifest 门后再单独申请用户批准 inductive 重跑。
