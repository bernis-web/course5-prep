# 课题5最小验证流程

本流程用于在不创建云实例、不上传数据、不提交任务的前提下，确认课题5的输入、评测契约、候选环境和预算是否具备进入下一阶段的证据。它只验证“是否准备好”，不替代真实 SATURN、SAMap 或 scVI 运行。

## 运行边界

- 本地 smoke test 只使用仓库 `requirements.txt` 和合成数据，不安装三种真实工具。
- `dcs_readonly_probe.py` 只读取当前解释器/实例的包元数据、入口和 GPU 信息；它不安装、不联网、不读取表达矩阵。
- 课程文件核验只记录文件名、大小和 SHA-256，不复制原文或把原始数据提交到 Git。
- readiness 未通过前，不创建 DCS 实例、不上传数据、不提交任务。

## A. 本地验证

在仓库根目录执行：

```powershell
Set-Location D:\projects\course5-prep
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python scripts/smoke_test.py --outdir smoke-output
python scripts/environment_check.py --output smoke-output/environment-report.json
python scripts/dcs_readonly_probe.py --output smoke-output/dcs-readonly-probe.json
python scripts/environment_contract.py smoke-output/dcs-readonly-probe.json --profile SATURN--22
python scripts/input_contract.py tests/fixtures/metadata.tsv --output smoke-output/metadata-manifest.json
python scripts/ortholog_contract.py tests/fixtures/orthologs.tsv --output smoke-output/ortholog-manifest.json
python scripts/plan_contract.py
```

预期证据：

- 单元测试退出码为 0；当前仓库应有 37 个测试通过。
- `smoke-output/synthetic_metrics.json` 和 `smoke-output/run_manifest.json` 存在且可读。
- `plan_contract.py` 报告 `status: preflight_only`，并列出禁止的云端动作。
- `dcs-readonly-probe.json` 的 `scope` 是 `runtime_probe`；它不能被当成本机以外的镜像证据。
- `environment_contract.py` 会把必需包、GPU 和页面声明版本分开报告；本机缺包时可以得到阻塞项，但不能据此推断 DCS 镜像也缺包。

## B. 材料与 readiness 核验

把课程材料所在目录作为占位参数传入，不要把本地绝对路径写进仓库：

```powershell
python scripts/source_manifest_check.py <course-material-directory> --output smoke-output/source-material-check.json
python scripts/local_readiness.py `
  --environment-report smoke-output/dcs-readonly-probe.json `
  --source-root <course-material-directory> `
  --output smoke-output/local-readiness-with-materials-and-probe.json
```

判定规则：

- `source_manifest_check.py` 退出码为 0，表示三份课程材料与 `docs/source-file-manifest.tsv` 的大小和 SHA-256 一致；不表示已取得实验数据授权。
- `local_readiness.py` 在课程路径、字段、镜像版本或正式 kBET 尚未确认时预期退出码为 2，报告中的 `ready_for_execution` 必须保持 `false`。
- readiness 报告中的 `environment.report_scope` 应为 `runtime_probe`；`scope: local_only` 只表示综合报告由本地生成。

## C. 预算与启动门

```powershell
python scripts/budget_check.py --profile 4090x1
python scripts/budget_check.py --profile 4090x2
python scripts/startup_preflight.py
```

- `4090x1` 是默认单卡候选，25 分钟硬停止、30 分钟预留成本约 ¥8.70，当前单次上限 ¥10，预算检查应通过。
- `4090x2` 预留成本约 ¥22.15，超过单次上限，预期以退出码 2 拒绝；不要因为 JSON 估算已输出就启动双卡。
- `startup_preflight.py` 当前会报告 `approval_status: pending`。只有数据授权、字段、子集、镜像实际版本、正式 kBET 和只读示例命令全部补齐后，才可能变为 `ready_for_execution: true`。

## D. 真实运行前的最小门槛

三人共同确认以下证据后，才讨论第一次单卡试运行：

1. HEART/LBSPA 路径、格式、字段、允许子集和数据授权已记录。
2. 候选镜像内用同一条只读探针确认 Python、CUDA、GPU、SATURN/SAMap/scVI、`anndata`、`scanpy`、`torch` 和正式 kBET 版本。
3. `startup_preflight.py` 返回 `ready_for_execution: true`，`budget_check.py --profile 4090x1` 通过。
4. 组内写明单次硬停止：25 分钟、峰值内存 75 GB 或成本 ¥10 任一达到即停止；任务结束立即关停实例。
5. 运行目录必须包含 `input_manifest.tsv`、`ortholog_manifest.json`、`parameters.json`、`package_versions.txt`、`stdout_stderr.log`、`metrics.json`、`resource_usage.json`，失败时另有 `failure_reason.txt`。

真实运行后的检查顺序是：

```powershell
python scripts/run_artifacts.py <run-directory> --status success
python scripts/result_contract.py <run-directory>/metrics.json <run-directory>/resource_usage.json --stage final
```

最终结果必须使用留一物种评估和正式 kBET；本地 smoke test 的 `chi2_neighborhood_proxy` 只能作为预检指标。

## 当前状态快照

- 课程网页与两篇论文的三份文件已通过大小/SHA-256 核验。
- 当前本机探针可见 RTX 4060 Laptop GPU，但 `saturn`、`samap`、`anndata`、`scanpy` 和 `scvi` 不可用；这不是 DCS 镜像结论。
- DCS 候选仍是 `SATURN--22`，SATURN 实际入口、SAMap 版本和正式 kBET 版本待确认。
- 启动门保持 `pending`，因而本流程到此为止，不进行任何云端动作。
