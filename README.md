# 课题5准备包

课题：跨物种细胞类型整合工具评测（SATURN vs SAMap vs scVI 系）。

这个目录目前只包含评测设计和合成数据 smoke test，不包含真实论文数据，也不会自动启动云实例或安装软件。

## GitHub 协作

仓库地址：<https://github.com/bernis-web/course5-prep>（私有仓库）。组员先由仓库所有者在 GitHub 的 Settings → Collaborators 中邀请，再执行：

```powershell
git clone https://github.com/bernis-web/course5-prep.git
Set-Location course5-prep
```

日常修改请从 `main` 创建短分支，提交后发 Pull Request；不要直接提交真实数据、凭据或 DCS 运行输出。完整约定见 `CONTRIBUTING.md`。

三人建议先按“数据与生物学、环境与算力、评测与报告”三条可轮换主线认领一个小交付物，再互相复核；不绑定姓名，也不设硬边界。打开仓库后的认领表、第一步和交付位置见 `docs/team-task-division.md`。向老师确认信息时使用 `docs/course-admin-reply-template.md`；镜像实际版本核验边界见 `docs/dcs-image-probe-plan.md`；最终容器化冻结规则见 `docs/containerization-plan.md`。

## 当前证据

- 课程网页要求比较：标签转移 macro-F1、批次混合与生物保守性（kBET/iLISI/silhouette）、时间/内存、文档易用性和 Agent 友好度。
- HEART 论文用 SATURN 整合 16 个物种的 479,483 个细胞，并用 SAMap 做跨物种细胞类型关系分析；SATURN 设置包含 ESM2B 蛋白嵌入、2000 个 macrogenes 和 8000 个 HVGs。
- LBSPA 论文提供七鳃鳗脑 465,778 个空间细胞和 41,678 个高质量单核转录组，并在七鳃鳗-小鼠比较中使用 6,930 个一对一同源基因、scVI（200 epochs）和 Harmony。
- 本次核对所用课程网页与两篇论文的文件版本见 `docs/source-file-manifest.tsv`；仓库不包含原始论文文件。
- 本机检查结果：约 31.3 GB RAM、16 个逻辑 CPU、RTX 4060 Laptop 8 GB；`torch` 和 `scikit-learn` 可用，但 `anndata`、`scanpy`、`scvi`、`harmonypy`、`saturn`、`samap` 当前均未安装。

## 先跑什么

```powershell
Set-Location D:\projects\course5-prep
python -m unittest discover -s tests -v
python scripts/smoke_test.py --outdir smoke-output
python scripts/environment_check.py --output smoke-output/environment-report.json
python scripts/dcs_readonly_probe.py --output smoke-output/dcs-readonly-probe.json
python scripts/source_manifest_check.py <course-material-directory> --output smoke-output/source-material-check.json
python scripts/input_contract.py tests/fixtures/metadata.tsv --output smoke-output/metadata-manifest.json
python scripts/ortholog_contract.py tests/fixtures/orthologs.tsv --output smoke-output/ortholog_manifest.json
python scripts/budget_check.py --profile 4090x1
python scripts/agent_evaluation.py
python scripts/startup_preflight.py
python scripts/environment_contract.py smoke-output/environment-report.json --profile SATURN--22
python scripts/result_contract.py tests/fixtures/final-metrics.json tests/fixtures/final-resources.json --stage final
python scripts/plan_contract.py
python scripts/local_readiness.py --output smoke-output/local-readiness.json
# 有课程材料目录时，把版本核验纳入同一份 readiness 报告
python scripts/local_readiness.py --source-root <course-material-directory> --output smoke-output/local-readiness-with-materials.json
# 真实运行目录准备好后，再检查一次交付物契约
python scripts/run_artifacts.py runtime-output/example-run --status success
```

smoke test 只验证指标和审计输出，不执行 SATURN、SAMap 或 scVI。其标签转移使用合成数据上的 kNN 留一物种折叠，`kbet_rejection_rate` 当前是卡方邻域代理，不是正式 kBET；接入真实数据前必须换成真实工具流程和正式 kBET 实现，并在报告中标注版本。
`input_contract.py` 只读取元数据并生成带 SHA-256 的 manifest；它不会修改输入表，也不会连接或提交 DCS 任务。
`ortholog_contract.py` 要求共享的 `species_a/gene_a/species_b/gene_b` 四列，规范化物种对顺序并拒绝一对多映射；它生成 SHA-256 manifest，供 SATURN、SAMap 和 scVI 使用同一基因空间。
`budget_check.py` 从 `config/dcs-budget-plan.json` 读取已核验价格，只计算成本，不创建实例；默认单卡 25 分钟硬停止、30 分钟预算预留。双卡方案若超出单次 ¥10 上限，命令会保留 JSON 结果但以退出码 2 结束，必须先复核再运行。
`run_artifacts.py` 只检查单次运行目录中的 `input_manifest.tsv`、`ortholog_manifest.json`、`parameters.json`、`package_versions.txt`、`stdout_stderr.log`、`metrics.json` 和 `resource_usage.json` 是否齐全且非空；失败运行还必须有非空 `failure_reason.txt`。它不会上传、下载、启动任务或修改这些文件。
`agent_evaluation.py` 检查文档清晰度、CLI/API、参数透明度、机器可读输出、失败诊断和环境复现性六个维度。评分范围为 0–3，但没有本地证据路径和验证说明的条目必须保持 `pending`，不能把 pending 当作 0 分。
`startup_preflight.py` 检查课程管理员确认是否已补齐数据路径、字段、镜像版本、正式 kBET 规则和只读示例命令；默认配置会阻止启动，且脚本不会检查远端路径或调用 DCS。
`environment_contract.py` 只读取 `environment_check.py` 生成的 JSON，按候选镜像检查必需包、版本记录和 GPU 可见性；报告中的 `scope: local_runtime` 只代表当前本机解释器，不能替代 DCS 实例证据。页面声明的版本与实例内实际版本分开记录，不能互相替代。
`dcs_readonly_probe.py` 只读取当前运行时的包元数据、`--version` 输出和 `nvidia-smi` 查询，并写出 `scope: runtime_probe` 报告；它不安装包、不联网、不读取表达矩阵、不上传数据，也不会启动或提交 DCS 任务。探针报告的包键与 `environment_contract.py` 对齐，可直接做候选环境预检；进入候选镜像后应使用同一命令保存实例内证据，不能把本机报告当成镜像证据。
`source_manifest_check.py` 只读取课程材料目录中的文件大小和 SHA-256，并与 `docs/source-file-manifest.tsv` 比对；报告不包含原文内容，缺失或哈希不一致时退出码为 2。它只能证明文件版本一致，不能证明课程已授权提供真实数据集。
`result_contract.py` 校验最终指标和资源字段；所有结果都必须声明 `leave_one_species_out` 和折数，最终阶段还拒绝 `chi2_neighborhood_proxy`，必须记录正式 kBET 的实现名称和版本。`tests/fixtures/final-metrics.json` 中的 `example-*` 仅是契约占位，不能当作真实版本。smoke 阶段可使用代理，但不能把该结果当作最终结论。
`plan_contract.py` 校验方法集合、留一物种策略、指标、停止线和禁止的云端动作；它通过前，不能把计划状态改为可执行。
`local_readiness.py` 汇总计划、预算、课程确认和本机候选环境四项检查；传入 `--source-root` 后还会把课程材料大小/哈希核验纳入报告。它只读本地配置与运行时信息并写出一份 JSON；在课程数据和镜像版本尚未确认时，预期返回退出码 2，不能把它当作失败修复或启动许可。

## 接入真实数据的最小顺序

1. 先用 HEART 的 3 个物种、CM/FB 两类或三类细胞，使用论文发布标签作为金标准。
2. 再扩大到 HEART 的 8 个物种，最后才跑 16 个物种。
3. LBSPA 先只用 lamprey 与 mouse 的 snRNA 子集；空间数据作为第二阶段验证，避免把 modality 差异误算成物种差异。
4. 每个工具固定输入细胞、基因/同源基因表、HVG 规则、邻居数、随机种子和 CPU/GPU 配置；每次运行保存参数、版本、日志、峰值内存和耗时。

## 推荐比较矩阵

| 场景 | 输入 | 主比较 | 主要结果 |
|---|---|---|---|
| 近缘 | HEART 3-8 物种 CM/FB | SATURN、SAMap、scVI + kNN | macro-F1、silhouette、iLISI、时间/内存 |
| 远缘 | HEART 16 物种 CM/FB | SATURN、SAMap、scVI + kNN | macro-F1、物种混合、保守细胞类型是否被过度合并 |
| 跨门 | lamprey vs mouse snRNA | SATURN、SAMap、scVI + kNN | 同源基因敏感性、标签转移、失败案例 |
| 模态压力 | lamprey snRNA + 空间子集 | 仅在方法支持时比较 | 记录 modality 偏差，不与 snRNA 主结果混合 |

标签转移建议采用留一物种（或留一批次）评估：整合训练物种后向被留出的物种转移标签，避免直接在同一批数据上“整合后再评分”。scANVI 可作为单独的有监督变体报告，不与无监督 scVI 混为一个分数。

## DCS Cloud 镜像核验

已登录 DCS 公共镜像中可搜索到：

- `SATURN--22`：33.6 GB；Python3 清单含 `anndata==0.10.8`、`scanpy==1.10.3`、`scvi-tools==1.1.6.post2`、`fair-esm==2.0.0`、`faiss-gpu==1.7.2`、`torch==2.6.0`，并列出 CUDA 12.4 组件。页面没有明确列出名为 `saturn` 的 Python 包或命令，仍需进入实例后做只读 `import/which` 验证。
- `samap_all`：6.8 GB；语言标为 R、python，描述页未给出完整 Python 版本清单，不能仅凭镜像名认定依赖已固定。
- `scvi_zt`：公共镜像；页面 Bash 指令包含安装 `scanpy`、`scvi-tools`，但同时指定 CPU 版 PyTorch，不适合作为默认 GPU 基准环境。

公平性建议：优先以 `SATURN--22` 为候选基础环境，在同一容器中补齐 SAMap 并锁定版本；若必须分别使用 `samap_all` 和 `scvi_zt`，则把“镜像/依赖差异”作为实验因素，并在报告中分别记录版本、CUDA 可见性和安装命令。

## DCS Cloud 使用边界

已知账户体验金余额为 ¥99，区域为 DCS-华北2。推荐只在真实数据和容器/依赖检查完成后使用：

- 首次：4090×1、22 核、90 GB，约 ¥17.40/小时；先跑 0.5 小时试运行，预算约 ¥8.70。
- 只有确认单卡和内存不足时才考虑双卡；4090×2 约 ¥44.30/小时，不作为默认配置。
- 运行前设置硬停止：单次测试达到 25 分钟、内存超过 75 GB、或余额消耗超过 ¥10 就停止并检查日志。
- 任务结束立即停止实例；存储和下载费用另计，下载约 ¥0.50/GB。
- 默认使用课程挂载数据，避免重复上传和下载；严禁把密码、cookie、token 写入日志或代码。

## 目前待确认

- 课程数据在 DCS 中的准确目录、文件格式（`.h5ad`/`.rds`/矩阵包）和标签字段名。
- HEART 16 物种中课程允许使用的最小子集，以及 LBSPA 对照小鼠数据是否已挂载。
- DCS 预置镜像是否包含 SATURN、SAMap、scVI；若不包含，只先生成安装计划，不自动安装。
- 老师是否要求正式 kBET，还是接受在报告中把正式 kBET 作为附加实验。

课程交付要求和 AI 使用日志另见 `docs/course-requirements-audit.md` 与 `docs/ai-use-log.tsv`。组员协作约定见 `CONTRIBUTING.md`。
