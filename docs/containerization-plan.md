# 课题5容器化与版本冻结计划

本文件是最终实验的环境设计，不是当前的构建或启动授权。课程数据、镜像内实际入口和版本尚未确认前，不创建 Docker/Conda 环境，不安装 SATURN、SAMap、scVI，也不上传数据。

## 推荐基线

- 默认候选基础镜像：`SATURN--22`。页面已声明部分 `anndata`、`scanpy`、`scvi-tools`、`torch` 和 CUDA 组件，但 `saturn` 的实际导入名/入口仍需实例内只读探针确认。
- 公平比较优先在同一容器中锁定 SATURN、SAMap、scVI 的版本、CUDA 可见性和命令入口；不得让某个工具偷偷使用另一套未记录的 Python 环境。
- 若 SAMap 或 scVI 只能在独立镜像运行，报告中必须把镜像/依赖差异作为实验因素，并分别保存探针结果、参数、日志和资源记录；不能把三个分镜像结果直接当成只由算法造成的差异。
- `scvi_zt` 仅作为 CPU/兼容性参考，不作为默认 GPU 基准；双卡也不是默认配置。

## 版本冻结记录

在允许真实运行前，每个候选运行环境至少保存以下机器可读证据：

1. 镜像名称、镜像摘要或平台版本标识；
2. Python、CUDA/驱动、GPU 型号和显存；
3. `saturn`、`samap`、`scvi`、`anndata`、`scanpy`、`torch` 及正式 kBET 的导入名和版本；
4. 每个工具的 `--version`/`--help` 或等价入口输出；
5. `input_manifest.tsv`、`ortholog_manifest.json` 和参数文件的 SHA-256；
6. 墙钟时间、峰值内存、GPU 数量、成本来源和失败原因（如有）。

统一使用 `python scripts/dcs_readonly_probe.py --output runtime-output/dcs-readonly-probe.json` 生成运行时证据，再用 `environment_contract.py` 检查候选环境。页面清单和本机 `scope: local_runtime` 报告只能作为候选信息，不能替代实例内证据。

## 分阶段流程

1. **本地 smoke**：只使用仓库 `requirements.txt`，运行合成指标、输入/同源基因契约和结果契约；不安装三种真实工具。
2. **实例只读核验**：课程管理员确认数据和镜像后，先运行探针，不读取表达矩阵，不安装包，不提交任务。
3. **单卡试运行**：只有 `startup_preflight.py` 为 `ready_for_execution: true`、四人明确批准且 `budget_check.py --profile 4090x1` 在上限内，才做不超过 25 分钟的最小 smoke run；峰值内存超过 75 GB 或成本达到 ¥10 时，由指名负责人立即手动停止（预算/提醒阈值只提醒，不会自动停机）。
4. **最终冻结**：2–3 物种首轮通过后才保存容器配方/锁定文件、探针 JSON 和运行 artifact；扩大到近缘/远缘/不同类别组合或后置 LBSPA 单核补充前重新复核预算和内存。空间数据暂不纳入主实验。

## 不应提交的内容

仓库不提交 HEART/LBSPA 原始表达矩阵、DCS 数据挂载路径、登录凭据、未审计的 pip/conda 安装日志或被 `.gitignore` 排除的运行输出。容器配方可以引用已批准的镜像和锁定版本，但不能把“待确认”字段填成猜测值。

## 通过标准

容器化准备只有在以下条件全部满足后才算完成：课程数据授权和字段已记录、候选镜像实例证据齐全、三种工具入口与版本可复现、正式 kBET 实现与版本已记录、单卡预算和停止规则通过、每次运行 artifact 契约通过。否则保持 `pending`，先补证据，不进入真实数据运行。
