# DCS 离线任务历史索引（只读，2026-09-26）

本索引只记录当前账号在 DCS 项目 `P20260920085640327` 页面上直接看到的非敏感字段，以及对应任务的只读运行日志摘要。没有启动、重试、删除、提交或上传任务；没有保存 cookie、token、密码或其他访问凭据。

## v71/v72 任务定位

入口：`任务管理 → 个性分析 → 离线任务`。页面显示共 122 条任务；第 5 页显示：

| 版本 | 批次任务编号 | 页面任务名称 | 批次状态 | 创建时间 |
|---|---|---|---|---|
| v72 | `2102886857148305410` | `g5-eval-v72` | 完成 | 2026-09-24 06:24:31 |
| v71 | `2102857229143199745` | `g5-saturn-3s-hvg-v71` | 完成 | 2026-09-24 04:26:47 |

## 子任务元数据

| 版本 | 子任务编号 | 子任务名称 | 状态 | 项目编号 | 创建时间 | 更新时间 | 计算资源 | 费用 | 分析镜像 | 代码名称 |
|---|---|---|---|---|---|---|---|---|---|---|
| v72 | `2102886857156694017` | `g5-eval-v72-1` | 完成 | `P20260920085640327` | 2026-09-24 06:24:31 | 2026-09-24 06:28:38 | `1c 4g` | ￥0.00 | `SATURN--22` | `-` |
| v71 | `2102857229180948482` | `g5-saturn-3s-hvg-v71-1` | 完成 | `P20260920085640327` | 2026-09-24 04:26:47 | 2026-09-24 06:21:33 | `1c 4g` | ￥0.47 | `SATURN--22` | `-` |

## 启动日志

两项子任务的启动日志都显示：

- 调度到 `stereonote` 容器；
- 从 DCS Harbor 的公开镜像路径拉取镜像；
- 容器成功创建并启动。

启动日志没有原始提交命令、参数清单、输入/输出 hash 或 barcode 角色表。

## v71 运行日志摘要

页面运行日志直接显示：

- 输入规模：human `[1528, 2500]`、mouse `[1535, 2500]`、zebrafish `[1543, 2500]`；
- `RC=0`；
- Epoch 34–50 的 triplet loss 与 mined-triplet 计数；
- 保存 Final AnnData、Final Triplets CSV 和 Final Epoch scores CSV 的路径；
- 末尾出现 `Saving Final AnnData` 完成信息。

这些信息证明 v71 子任务完成了 SATURN 训练阶段并产生了运行日志中的输出路径，但不证明路径对应文件仍可读取，也不包含文件 SHA-256。

## v72 运行日志摘要

页面运行日志直接显示：

```json
{
  "shape": [4606, 256],
  "obsm_keys": ["macrogenes"],
  "lat_shape": [4606, 1000],
  "species_counts": {"zebrafish": 1543, "mouse": 1535, "human": 1528},
  "truth_na": 0,
  "knn_transfer_k15": {
    "human>mouse": 0.5668,
    "human>zebrafish": 0.1154,
    "mouse>human": 0.1846,
    "mouse>zebrafish": 0.2093,
    "zebrafish>human": 0.0007,
    "zebrafish>mouse": 0.0671
  }
}
```

日志前部还出现 observation names 非唯一的 `anndata` 警告。该警告需要在后续评估中作为数据质量风险处理，不能静默忽略。

## 能证明什么、不能证明什么

### 与项目级 SATURN 记录的交叉核对

`docs/saturn-smoke-evidence-20260922.md` 对 v71/v72 的项目级记录补充了参数和规模背景：三物种每物种 2500 个 HVG 候选、内部 2000 HVG、1000 macrogenes、50 epochs、真实 ESM2 嵌入，以及 `saturn_out_real3_h/saturn_results/` 等输出目录。它可以作为“日志摘要与项目计划相互一致”的旁证，但不是 DCS 表单保存的原始命令或文件 provenance；因此不填充 manifest 中仍为 `pending` 的 command、hash、barcode 和 reviewer 字段。

### 本地文件可得性检查（2026-09-26）

对 `D:\projects\course5-prep` 和 `D:\projects\course5-data` 做了只读文件名/元数据检索：当前工作区没有 v71/v72 的 h5ad、Final AnnData、NPZ bundle、barcode 清单或 DCS 输出目录；仅有结构检查报告和审计文档。这个结果解释了为什么不能从本地直接生成 `barcode-roles-v73.tsv`，也确认下一步若要补齐角色表，必须从 DCS 只读文件元数据/工作区内容或老师保留的原始清单取得，而不是凭细胞数推造。

### 已直接证明

- DCS 当前可见项目中确实存在名为 v71/v72 的已完成离线批次；
- 两项任务均使用 `SATURN--22`、`1c 4g`，且具有可读的启动日志；
- v71 日志出现训练迭代和 Final AnnData 输出路径；
- v72 日志出现 `macrogenes`、1000 维 latent 和 KNN-15 迁移结果。

### 仍未证明

- v71 使用的原始命令、checked-in 源码版本、镜像 digest 或补丁；
- v72 是否使用了独立 query/reference barcode、独立留出数据或独立标签；
- v71/v72 输入与输出文件的 SHA-256；
- `ref_labels`、`use_ref_labels`、`unfreeze_macrogenes`、seed 等原始参数；
- v72 评估究竟读取 `X` 还是 `obsm/macrogenes`，以及是否排除了 self/重复 barcode；
- v72 的 exact label 与同源映射 label 评估是否分开。

因此，`config/eval-manifest-v73.json` 必须继续保持 `evidence_status=pending`，v72 只能标记为 transductive/in-sample exploratory evaluation，不能写成 held-out benchmark 或 independent generalization。

## 下一步交接

1. 继续找回原始命令、输入/输出文件 hash、表示层提取记录和 barcode 角色表；
2. 若 DCS 页面无法提供这些字段，向老师/平台只索取上述最小 provenance，不要求重跑；
3. provenance 齐全前只做本地标签映射、评估器测试、日志解析和质量门审计；
4. 用户明确启动下一轮实验且 manifest 通过校验后，才讨论 DCS 任务提交。
