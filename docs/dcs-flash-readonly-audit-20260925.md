# DCS provenance 辅助只读审计（Flash，2026-09-25）

## 证据边界

本记录来自 `glm-5.3-flash` 对当前工作区的只读复核。复核过程中没有获得可用的 DCS 页面快照或浏览器导航授权，因此**没有新增 DCS 页面证据**。它只能作为本地审计辅助记录，不能替代任务详情、原始命令、完整日志、云端路径或 hash。

全程没有修改项目文件、启动 DCS 任务、上传/下载数据、提交或推送。

## 已由本地文件支持的结论

- `config/eval-manifest-v73.json` 仍为 `evidence_status=pending`，`run.dcs_task_id`、`run.original_command`、`run.complete_log_path` 和 `run.input_manifest_path` 均为空。
- `config/barcode-roles-v73.tsv` 只有表头，没有 query/reference barcode 记录。
- `docs/saturn-smoke-evidence-20260922.md` 记录了 v71 的三物种试运行和 v72 的 KNN15 数字，但对应 DCS 原始页面、完整日志和原始命令没有落库。
- 本地 checked-in SATURN 源码审计已经确认 `cross_species` miner、`ref_labels` 未参与当前索引函数的正负样本选择，以及 `obsm["macrogenes"]` 输出；这仍不能证明 v71 DCS runtime 使用了同一源码或同一补丁。

## 当前不能推断的内容

以下字段禁止从历史转述、任务名称或论文信息猜填：

1. 当前 DCS 登录态是否有效；
2. v71/v72 task ID、状态和起止时间；
3. v71 原始命令中的 `use_ref_labels`、`unfreeze_macrogenes`、`seed` 等参数；
4. v71 runtime 源码 commit、镜像层 hash 或补丁；
5. v72 实际使用 `X` 还是 `obsm["macrogenes"]`；
6. query/reference barcode 清单、hash、交集排除记录；
7. 逐细胞预测、邻居、置信度和弃权输出。

## 登录态恢复后的最小查询顺序

1. 先取 v71/v72 task ID、状态和时间；
2. 再取 v71/v72 原始命令和完整日志入口；
3. 取 Final AnnData、epoch scores、triplets 的只读路径与 SHA-256；
4. 取 v72 表示层和 query/reference barcode 清单；
5. 取运行时源码 commit、镜像层 hash 或补丁；
6. 将脱敏字段回填 manifest 和 barcode 表；
7. 运行 `python scripts/validate_eval_manifest.py`，只有条码角色、hash、reviewer 和 provenance 全部通过后，才讨论升级 `evidence_status`。

在此之前，v71/v72 只能表述为“transductive/in-sample 探索性结果”，不能表述为 held-out benchmark 或独立泛化性能。

## 证据等级

`C（项目本地审计/辅助模型复核）`。本记录不提升 DCS provenance 的证据等级。
