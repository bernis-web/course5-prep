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
```

运行输出在 `smoke-output/` 下，已被 `.gitignore` 排除。每次使用 Agent 时，将摘要和验证方式追加到 `docs/ai-use-log.tsv`，不要记录凭据或原始数据内容。
