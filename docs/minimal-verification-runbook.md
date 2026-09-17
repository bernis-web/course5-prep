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

- 单元测试退出码为 0；测试数量以本次命令输出为准。2026-09-17 加入阶段化预检回归测试后，本轮应有 50 个测试通过。
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
python scripts/team_budget_check.py --profile 4090x1 --reserved-minutes 60 --runs 1
python scripts/startup_preflight.py
```

- `4090x1` 是默认单卡候选，25 分钟硬停止、30 分钟预留成本约 ¥8.70，当前单次上限 ¥10，预算检查应通过。
- `4090x2` 预留成本约 ¥22.15，超过单次上限，预期以退出码 2 拒绝；不要因为 JSON 估算已输出就启动双卡。
- `team_budget_check.py` 使用四个账号各 ¥100 的“规划总额”估算；当前配置暂定预留 ¥80（每个账号 ¥20），团队可操作上限为 ¥320。账号余额和跨账号合并能力必须由组员分别核实，脚本默认不假设可合并。
- 在团队预算层面，4090×1 的 60 分钟单次估算约 ¥17.40，仍低于单个 ¥100 规划额度；这只是成本估算，不是启动授权。每次运行仍要绑定一个实际账号、记录消耗，并在结束后停止实例。
- 按每账号预留 ¥20 分摊时，4090×1/60 分钟最多先按每账号 4 次、四账号共 16 次估算（约 ¥278.40）；3 个工具 × 3 个随机种子只需 9 次（约 ¥156.60）。超过这些数字先检查实际余额，再决定是否充值。
- 4090×2/30 分钟单次约 ¥22.15，虽然团队预算可以覆盖，但它只作为单卡内存不足后的例外路径，不能因余额变多就默认启用。
- `startup_preflight.py` 按阶段校验：默认 `heart_pilot` 不要求 `lbspa_snRNA_path`；`--phase lbspa_followup` 另要求该路径与 `evidence.scrna_conclusion`（LBSPA 激活门，配置中初始为空）。当前配置会报告 `approval_status: pending`，只有数据授权、字段、子集、镜像实际版本、正式 kBET 和只读示例命令全部补齐后，才可能变为 `ready_for_execution: true`。

## D. 真实运行前的最小门槛

四人共同确认以下证据后，才讨论第一次单卡试运行：

1. 已在 DCS 中只读核实 HEART/LBSPA 路径、格式、字段、可用物种和数据授权；首轮 2–3 个物种及后续近缘/远缘/混合类别组合已记录。
2. 候选镜像内用同一条只读探针确认 Python、CUDA、GPU、SATURN/SAMap/scVI、`anndata`、`scanpy`、`torch` 和正式 kBET 版本。
3. `startup_preflight.py` 返回 `ready_for_execution: true`，`budget_check.py --profile 4090x1` 通过。
4. 组内写明单次硬停止：默认预检仍为 25 分钟；若采用团队预算扩展，则由批准的运行单独写明 60/120 分钟上限，但峰值内存 75 GB 或该次分配的预算上限任一达到即由指名负责人手动停止；不能把平台预算设置当作自动停机保证；任务结束立即关停实例。
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
- 四账号体验金只是用户提供的规划假设；尚未核实四个账号是否能合并、充值规则和实际余额，不能把 ¥400 当成单一账户可直接消费的余额。
- 老师已确认数据和工具可在 DCS 查询，但仓库尚未取得可复核的具体路径、字段、物种清单、工具入口和正式 kBET 版本；这些项目仍是启动阻塞项。
- 主实验只使用单细胞数据；空间数据暂不纳入，LBSPA 单核只在单细胞评测形成基本结论后做小规模补充。
- 启动门保持 `pending`，因而本流程到此为止，不进行任何云端动作。
