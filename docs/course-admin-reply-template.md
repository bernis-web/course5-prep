# 课题5课程确认回填模板

这份模板用于把课程管理员的回复直接回填到 `config/startup-preflight.json`。它不是数据授权书，也不要求复制、上传或下载原始数据；请只填写课程允许公开给本组的路径、字段和版本信息。

## 请管理员确认

| 编号 | 请填写的内容 | 回填字段 |
|---|---|---|
| 1 | HEART 16 物种的只读挂载路径、文件格式（`h5ad`/`rds`/矩阵目录） | `heart_data_path`, `heart_file_format` |
| 2 | 物种、细胞类型、批次、论文金标准标签的字段名 | `heart_metadata_fields.species/cell_type/batch/gold_label` |
| 3 | 已准备的 3/8/16 物种子集，或允许本组从 16 物种对象抽取的规则 | `heart_allowed_subsets` |
| 4 | 七鳃鳗与小鼠 snRNA 的只读路径；空间数据是否纳入第一轮 | `lbspa_snRNA_path`, `lbspa_spatial_policy` |
| 5 | 推荐镜像名称，以及 SATURN、SAMap、scVI 的锁定版本 | `image_recommendation`, `image_versions` |
| 6 | 正式 kBET 实现和版本；是否允许 scANVI、Harmony、LIGER 作为扩展对照 | `kbet_implementation`, `kbet_version` |

## 还需记录的同源基因信息

请注明 HEART 和 LBSPA 各自允许使用的一对一同源基因表来源、版本或发布日期，以及是否有课程指定的基因数量上限。该信息写入数据说明和 `ortholog_manifest.json`，不直接填入启动门字段。

## 最小只读示例

请同时提供一个不修改数据的示例命令，只打印以下信息：对象类型、细胞数、基因数、元数据字段名和可用物种/批次值。示例命令回填到 `readonly_sample_command`；不要在命令或回复中包含密码、cookie、token 或密钥。

## 记录规则

- 只有收到课程管理员明确回复后，才能把 `approval_status` 改为 `confirmed`。
- 原始回复建议保存为组内受控文档，`evidence.course_admin_reply` 只记录不含凭据的文件名或编号。
- 若某项尚未确定，保留 `null` 并在 `docs/teacher-data-request.md` 中标记待确认，不要用猜测填充。
- 三个人共同复核回填内容后，运行 `python scripts/local_readiness.py`；预检通过不等于已经获得云端运行授权。
