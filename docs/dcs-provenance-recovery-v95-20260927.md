# v95 DCS 只读取证恢复记录（2026-09-27）

## 结论

v95 只读任务本身已完成，但它生成的 `g5-provenance-v95-out.json` 未能从 DCS 读回。因此，本轮只能确认 v95 的提交命令、脚本指纹、任务元数据和预期输出位置；不能把 v95 视为已完成 v71/v72 provenance 恢复，也不能把 `config/eval-manifest-v73.json` 从 `pending` 升级为 `confirmed`。

这轮结果不改变 v71/v72 的定性：现有结果仍是 **transductive / in-sample exploratory evaluation**，不能单独写成 held-out 或 independent generalization benchmark。

## v95 任务元数据

以下字段来自 2026-09-27 Codex 对 DCS 任务页的直接只读观察；本文件只保存脱敏元数据，不保存登录凭据。

| 字段 | 值 |
| --- | --- |
| 项目 | `P20260920085640327` |
| 批次任务 | `2104141429858734082` |
| 子任务 | `2104141429879705602` |
| 任务名 | `g5-provenance-v95-readonly` |
| 状态 | 完成 |
| 创建/开始 | 2026-09-27 17:29:45 |
| 更新/结束 | 2026-09-27 17:30:44 |
| 计算资源 | `1c4g` |
| 分析镜像 | `SATURN--22` |
| 费用 | ¥0.00 |

## 提交命令与脚本指纹

v95 提交命令的结构如下（省略内嵌 base64 正文）：

```text
printf '%s\n' 'g5-provenance-v95-readonly | payload=base64(dcs_provenance_v95.py) | payload_sha256=89195b9aa21c372cf9c07c698e3e35a285586291eb55b3df19900ed3c9742317 | mode=readonly | no_prior_artifact_modified' > /data/work/g5-provenance-v95-command.txt;
printf '%s' '[BASE64_PAYLOAD_OMITTED]' | base64 -d > /data/work/dcs_provenance_v95.py;
python3 /data/work/dcs_provenance_v95.py > /data/work/g5-provenance-v95-out.json 2> /data/work/g5-provenance-v95-err.log;
rc=$?;
cat /data/work/g5-provenance-v95-out.json;
printf '\n';
if [ -s /data/work/g5-provenance-v95-err.log ]; then cat /data/work/g5-provenance-v95-err.log >&2; fi;
exit $rc
```

本地仓库中的 `scripts/dcs_provenance_v95.py` 复核 SHA-256 为：

```text
89195b9aa21c372cf9c07c698e3e35a285586291eb55b3df19900ed3c9742317
```

该值与提交命令中的 `payload_sha256` 一致。脚本的声明范围是只读扫描 `/data/work`，仅写入 v95 自己的 JSON、错误日志和命令记录，不删除、移动或重写旧产物。

## 输出读回结果

Codex 当时在 DCS 工作区文件树中可见：

- `g5-provenance-v95-command.txt`
- `dcs_provenance_v95.py`

未见以下两个预期输出：

- `g5-provenance-v95-out.json`
- `g5-provenance-v95-err.log`

这个“未见”只能说明当时文件树没有显示，不能等同为容器内文件从未生成；文件树同步和前端渲染均可能延迟。任务日志中出现过 JSON 开头，但可复制内容被截断，不能把截断文本当作完整 JSON 或完整日志。

随后做了一次无凭据只读接口探测：对离线子任务详情、任务日志和文件内容接口的请求均返回应用层 `{"code":401}`。这证明这些接口需要登录态；本轮没有读取、保存或复用 cookie/token。浏览器插件句柄随后变为不可用，因此也无法再通过页面自身的文件读取机制完成读回。

## 对 v71/v72 provenance 的影响

### 本轮可确认

- v95 任务确实存在并完成；
- v95 使用 `SATURN--22`、`1c4g`，费用为 ¥0.00；
- v95 提交命令明确声明只读模式和不修改旧产物；
- 本地脚本与提交载荷的 SHA-256 一致；
- v95 预期会在 `/data/work` 生成完整 JSON，但该 JSON 目前未能读回。

### 本轮不能确认

- v71 原始训练命令的完整文本；
- v71/v72 输入对象、Final AnnData、triplets 和 epoch scores 的 SHA-256；
- v71/v72 的完整条码清单和角色表；
- v72 self/重复条码排除记录；
- v71 运行时 SATURN 源码树或镜像 digest；
- v72 逐细胞预测表和混淆矩阵。

因此，v95 报告不能替代这些字段，`config/eval-manifest-v73.json` 的正式运行字段必须继续留空或 `pending`。

## 与评审结论的关系

2026-09-27 第二评审确认了一个协议级事实：v71 原训练命令显式包含 `--in_label_col cell_type --ref_label_col cell_type`，且 v72 评估与训练使用同一 4,606 细胞集合。该证据来自当时提交记录的直接知情，不是 v95 JSON 读回结果。它支持把 v72 定性为：

```text
transductive / in-sample exploratory evaluation
```

不要只写 `transductive`，因为目标物种标签在训练阶段已被使用，单独“transductive”容易暗示标签曾被隐藏。

## 本地落库验证

2026-09-27 在本地仓库完成以下验证：

- `python -m unittest tests.test_eval_manifest -v`：5 个测试全部通过；
- `python scripts/validate_eval_manifest.py`：`valid: true`，`evidence_status: pending`，`ready_for_confirmation: false`，并列出条码表、正式任务号、原始命令、评估层 provenance 等阻塞项；
- `Get-FileHash scripts/dcs_provenance_v95.py -Algorithm SHA256`：与 v95 提交命令中的 `payload_sha256` 一致；
- `git diff --check`：无空白错误（仅输出既有跟踪文件的 LF/CRLF 提示）。

这些验证只证明本地记录和校验规则自洽，不改变 v95 输出未能读回、v71/v72 正式 provenance 仍为 `pending` 的结论。

## 下一步

1. 若用户重新恢复 DCS 页面插件连接，优先通过页面自身文件读取机制读取 `g5-provenance-v95-out.json`，并核对 JSON 内的 `generated_at_utc`、文件清单和哈希；
2. 若文件树持续不显示输出，可考虑一个更小的 `v96-readout-readonly`，仅读取并打印 v95 的 out/err/command 三个文件及 SHA-256；提交前需用户明确批准；
3. 在 v95 JSON 读回前，不填充 v73 manifest 的正式 provenance 字段；
4. 即使 v95 JSON 读回成功，它也只能恢复文件/命令/哈希类证据；独立 query/reference 留出从未存在于 v72 协议中，仍需按新协议重跑。
