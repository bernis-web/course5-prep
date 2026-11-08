# 本地三物种 SAMap 只读复核（2026-09-27）

## 结论

`local_samap3.py` 的三物种运行完成了本地管线，六个人 printed 分数也均未超过对应 majority baseline；但它还不能作为正式 mapped benchmark 或 v72 provenance 使用。主要问题不是三份源文件内部 barcode 重复，而是：

1. 三个 raw barcode 跨物种重名，SAMAP 拼接后自动加 `-1`，回连真值失败，生成 3 个 `cell_type=NA`；
2. 评估代码只按 `coarse_level == 'unmapped'` 排除，而映射表把应排除的类型写成 `fine_mapped_label='unmapped'`、`coarse_level='other'`，导致 mouse/zebrafish 的 Proliferating、zebrafish mt 共 74 个细胞未按既定规则排除；
3. `SAMAP(keys=cell_type)` 会使细胞类型信息影响邻域扩张规模，联合嵌入不是纯无监督表示；
4. 目标物种表达全程参与联合嵌入后评分，只能称 transductive/in-sample，不能称 held-out/inductive。

因此，`docs/saturn-smoke-evidence-20260922.md` 附3 中“三方法对比矩阵就此完整”的表述应降级为：本地三物种 SAMap operationalization 已完成初步复核，但 mapped 层分数需修正后重算，不能直接进入正式报告排名。

## 本轮实测证据

解释器：`D:\projects\course5-prep\.venv39\Scripts\python.exe`；`anndata 0.10.9`，`sammap 1.0.16`，`sam-algorithm 1.0.2`。

### 文件结构与 SHA-256

| 文件 | n_obs | n_vars | 重复 obs | SHA-256 |
| --- | ---: | ---: | ---: | --- |
| `local_human_s.h5ad` | 1528 | 32732 | 0 | `AF41618B6941D2F1EACC7535E34A73B08E57CCE78060C9F6D0DF15984E57C633` |
| `local_mouse_s.h5ad` | 1535 | 32379 | 0 | `7FDA583D59D3767EE0D61C741AE2AB89DC0C43F5D587CAF2F768B4D8A12D9D2E` |
| `local_zebrafish_s.h5ad` | 1543 | 27661 | 0 | `6B1E8798D5F848ACD6340486836FF2E3A8393408E282B6B0C50695B13E49A879` |
| `local_samap3_emb.h5ad` | 4606 | 0 | 0 | `179ADA665BBEAC3EB4CA8C775151A7E98A4885FDF51C875431BE991AFA2105EE` |

`local_samap3_emb.h5ad` 的表示层为 `obsm["X_samap_pca"]`，维度 4606×150；源文件基因数与平台 v71/v72 记录的 2500 HVG/256 macrogenes 不同，不能把本地结果解释为 v72 复现。

脚本与输出指纹：

- `local_samap3.py`: `900E17AD10FDA254F3CF527CF997B2FDB125D4FB5FB1AC38282B6838B169ACA1`
- `local_samap3_out.txt`: `3A72D114B06D06D523DE51EF953725BBAB60245B70FCB98D66F470C58D7D52DB`
- `config/heart-celltype-map-v1.tsv`: `BE9857354778535B76D1884D004C54691DC5FF2DAA7B098D71DC719DAF583165`

### Barcode 碰撞

三份源文件各自 obs name 均唯一。以下 3 个名字跨物种重复：

| raw barcode | 受影响联合 obs name | 物种 | 回连真值 |
| --- | --- | --- | --- |
| `CELL10600_N1_4` | `zf|CELL10600_N1_4-1` | zebrafish | `NA` |
| `CELL5262_N1_2` | `zf|CELL5262_N1_2-1` | zebrafish | `NA` |
| `CELL5873_N1_3` | `zf|CELL5873_N1_3-1` | zebrafish | `NA` |

这与 `local_samap3_out.txt` 中三次 `Observation names are not unique` 警告和 `truth NA=3` 对上。

### 排除规则与映射层

映射表中的既定规则：

| source | label | coarse_level | fine_mapped_label | 应否进入 mapped 分母 |
| --- | --- | --- | --- | --- |
| mouse | Proliferating cell | other | unmapped | 否 |
| zebrafish | mt | other | unmapped | 否 |
| zebrafish | Proliferating cell | other | unmapped | 否 |

源数据计数：mouse Proliferating 30、zebrafish mt 30、zebrafish Proliferating 14，共 74。`local_samap3.py` 却按 `coarse_level == 'unmapped'` 过滤，而映射表没有任何 coarse 值等于字符串 `unmapped`，因此这 74 个细胞被保留在 exact/coarse 两个评分空间。代码也没有使用 `fine_mapped_label` 列，所以 printed 的 “coarse” 不能等同于 manifest 定义的 mapped evaluation。

## 对既有 printed 分数的判定

`local_samap3_out.txt` 的 exact 分数仍可作为 exploratory exact-layer KNN 输出引用；但：

- 3 个 `NA` 参与训练标签并可参与分母；
- 74 个应排除细胞未按 v1 映射规则处理；
- `keys=cell_type` 使标签信息影响联合图构建；
- 未保存逐细胞预测表；
- 无多 seed/容量消融。

因此不能把 0.0195/0.1715/0.0/0.3856/0.0/0.0 写成正式 mapped benchmark，也不能据此声称“SAMap 已完整进入三方法/四方法正式排名”。

## 修复门槛

后续如需把 SAMap 保留为方法学对照，先做小修正并本地重跑，仍不启动 DCS：

1. 在进入 SAMAP 前构造物种限定 barcode，或保存原始 barcode 映射，禁止依赖拼接器自动加 `-1`；
2. 训练和真值回连均断言无 `NA`、无重复；
3. 评分使用 `fine_mapped_label`，按 `fine_mapped_label == 'unmapped'` 排除并报告 coverage/abstention；
4. exact 与 mapped 分开输出，另存逐细胞预测和混淆矩阵；
5. 明确标注为 label-aware SAMAP operationalization 与 transductive/in-sample 协议；
6. 记录 seed、包版本、输入/输出 SHA-256 和原始命令。

## v71/v72 provenance 边界

2026-09-27 尝试无凭据访问 `/stereonote/api/offline/subTask/get/2102857229180948482`，GET/POST 均返回 `{"code":401}`。这不是平台故障，而是需要登录会话；本审计不读取、保存或复用 cookie/token。

本地 SAMap 结果不能补齐以下 v72 证据：原始命令、query/reference barcode、self/重复 barcode 排除、表示层读取代码、Final AnnData/hash、训练日志中的参数、runtime 镜像 digest。`config/eval-manifest-v73.json` 必须继续维持 `evidence_status=pending`、`ready_for_confirmation=false`、`cloud_actions_allowed=false`。
