# 协作约定

## 开始前

- 先阅读 `README.md`、`config/benchmark-plan.json` 和 `docs/teacher-data-request.md`。
- 不把 HEART/LBSPA 原始数据、DCS 凭据、cookie、token 或本地绝对路径提交到仓库。
- 所有真实运行前先确认数据授权、镜像版本和预算；默认不启动云实例。

## 提交前

测试依赖固定在 `requirements.txt`；新环境先执行 `python -m pip install -r requirements.txt`，不要把 SATURN、SAMap 或 scVI 装进这个本地 smoke-test 环境。

```powershell
Set-Location D:\projects\course5-prep
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python scripts/smoke_test.py --outdir smoke-output
python scripts/environment_check.py --output smoke-output/environment-report.json
python scripts/input_contract.py tests/fixtures/metadata.tsv --output smoke-output/metadata-manifest.json
python scripts/ortholog_contract.py tests/fixtures/orthologs.tsv --output smoke-output/ortholog_manifest.json
python scripts/startup_preflight.py
python scripts/environment_contract.py smoke-output/environment-report.json --profile SATURN--22
python scripts/result_contract.py tests/fixtures/final-metrics.json tests/fixtures/final-resources.json --stage final
python scripts/plan_contract.py
python scripts/local_readiness.py --output smoke-output/local-readiness.json
```

预算检查命令以退出码表示是否能在单次上限内运行：例如 4090×2 的预留成本超出 ¥10 时会返回退出码 2，即使它仍打印了 JSON 估算。`local_readiness.py` 在当前待确认状态下也会返回退出码 2；这是预检结果，不是启动许可。只有 `startup_preflight.py` 返回 `ready_for_execution: true` 且组内明确批准后，才进入真实运行。真实运行结束后，将运行目录交给 `python scripts/run_artifacts.py <run-dir> --status success`（失败时使用 `--status failed`）检查，再用 `python scripts/result_contract.py <run-dir>/metrics.json <run-dir>/resource_usage.json --stage final` 检查字段和 kBET 规则。运行输出在 `smoke-output/` 下，已被 `.gitignore` 排除。每次使用 Agent 时，将摘要和验证方式追加到 `docs/ai-use-log.tsv`，不要记录凭据或原始数据内容。
