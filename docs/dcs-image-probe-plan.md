# DCS 镜像只读核验计划

本文件是镜像证据清单，不是启动授权。当前仓库仍禁止创建实例、提交任务、上传数据、安装包和消耗余额。只有课程管理员确认数据与镜像、组内明确批准后，才可以在一个最小单卡试运行中执行这里的只读检查。

## 核验目标

对候选镜像分别记录：

- Python、CUDA、GPU 型号和显存；
- `saturn`、`samap`、`scvi-tools`、`anndata`、`scanpy`、`torch` 的实际导入名与版本；
- 可用的 CLI/入口命令，以及命令是否仅打印帮助或版本；
- 不读取课程数据时的启动耗时、峰值内存和停止原因。

页面清单中的版本只能作为候选证据，不能替代实例内的实际版本。特别是 `SATURN--22` 页面没有明确列出 SATURN 包或命令，必须单独记录“可导入名/入口/版本”三项。

仓库本机运行 `environment_check.py` 产生的报告会标记 `scope: local_runtime`；它只能说明本机解释器和本机 GPU，不是 DCS 实例证据。只有在候选镜像实例内重复探针并保存实际输出后，才可把对应条目标为 `observed`。

## 只读探针边界

探针只能检查运行时和包元数据，不得执行 `pip install`、`conda install`、网络下载、数据复制、数据上传或真实表达矩阵读取。建议把标准输出和错误输出保存为 `stdout_stderr.log`，把版本结果保存为 `package_versions.txt`；不把凭据写进任何文件。

仓库提供统一的只读探针：

```powershell
python scripts/dcs_readonly_probe.py --output runtime-output/dcs-readonly-probe.json
```

探针会记录 `runtime_probe` 范围内的 Python、包导入/版本、`saturn`/`samap`/`python`/`nvidia-smi` 的命令级信息，以及 GPU 查询结果。报告中的包键与 `environment_contract.py` 对齐，可以直接作为候选环境预检输入。它不会安装、联网、复制或读取课程数据；报告只能作为当前运行时证据，不能用页面声明或本机报告替代实例内证据。

| 检查项 | 必须留下的证据 |
|---|---|
| Python 与包版本 | `package_versions.txt`，包含发行版版本和导入成功/失败 |
| 入口命令 | `package_versions.txt`，包含 `which`/等价查找结果和 `--version`/`--help` 结果 |
| GPU/CUDA | `resource_usage.json` 或环境报告，包含 GPU 型号、显存、CUDA 可见性 |
| 资源边界 | `resource_usage.json`，包含墙钟时间、峰值内存、GPU 数量、成本来源 |
| 失败诊断 | 失败运行必须有非空 `failure_reason.txt` |

## 候选记录表

| 镜像 | 角色 | 页面版本 | 实例实际版本 | 入口/导入 | GPU/CUDA | 状态 |
|---|---|---|---|---|---|---|
| `SATURN--22` | 默认 GPU 候选 | `latest`；页面含 `scvi-tools 1.1.6.post2`、`scanpy 1.10.3`、`torch 2.6.0`，未显示 SATURN 包/入口 | pending | pending | 页面列出 CUDA 12.4 组件，实例待核验 | pending |
| `BENGAL--SAMap--17` | SAMap 版本核验候选 | 页面同时列出 `samap 1.0.1` 与 `1.0.16`，存在歧义 | pending | pending | pending | pending |
| `samap_all` | SAMap 交互环境候选 | 页面有 Jupyter/holoviews-samap 安装指令，未锁定 SAMap 版本 | pending | pending | pending | pending |
| `scvi_zt` | CPU 兼容性参考 | 页面安装指令未锁定 scvi-tools 版本，并指定 CPU PyTorch 源 | pending | pending | CPU 参考 | pending |

## 通过条件

只有在候选镜像的实际包版本、入口命令和 GPU/CUDA 证据齐全，并且 `startup_preflight.py` 返回 `ready_for_execution: true` 后，才可以讨论真实数据的首轮试运行。首轮仍使用 4090×1、25 分钟硬停止、75 GB 内存停止线和 ¥10 单次上限；任务结束立即停止实例。
