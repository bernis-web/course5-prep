# DCS Cloud 只读核验记录

核验日期：2026-09-09。所有操作均为已登录页面的只读浏览，没有创建实例、复制数据、上传文件、提交任务或支付。

## 账户与项目

- 区域：DCS-华北2。
- 可用余额：¥99.00。
- 当前默认项目：`user50719-8334's default project_DCS-North2`。
- 当前项目数据管理页：项目数据为 0 条。
- 项目公共库数据页：根目录显示 25 条、总计约 5TB；搜索 `heart` 和 `lamprey` 均为 0 条。
- 公共项目页列出的 7 个项目均为通用演示项目，没有显示 HEART 或 LBSPA 项目。

## 公共镜像

### SATURN--22

- 名称：`SATURN--22`。
- 发布：2025-09-10；更新：2025-09-10。
- 大小：33.6 GB。
- 语言：Python3 清单可见。
- 关键包：`anndata==0.10.8`、`scanpy==1.10.3`、`scvi-tools==1.1.6.post2`、`fair-esm==2.0.0`、`faiss-gpu==1.7.2`、`torch==2.6.0`；同时可见 CUDA 12.4 运行库组件。
- 页面没有明确列出名为 `saturn` 的 Python 包或命令；页面描述为空，没有启动容器验证，因此镜像名称不能替代命令级确认。

### samap_all

- 名称：`samap_all`。
- 发布：2024-07-23；更新：2025-04-23。
- 大小：6.8 GB。
- 语言：R、python。
- 页面显示 Bash 指令会安装 `ipywidgets`、`holoviews-samap` 及 Jupyter 扩展；完整 Python 工具包版本没有在摘要区域列出。
- 页面描述为空；没有启动容器验证。

### scvi_zt

- 名称：`scvi_zt`，标签为 `scvi`。
- 页面 Bash 指令包含 `pip install scanpy` 和 `pip install scvi-tools`，并指定 CPU 版 PyTorch 安装源。
- 因此它可以作为 CPU/兼容性参考，但不应默认当作 GPU 基准环境。

## 结论

平台有可复用的 SATURN、SAMap、scVI 镜像候选，但当前账户看不到课程专用 HEART/LBSPA 数据。真实实验启动前需要老师或课程管理员提供：数据目录、挂载权限、标签字段说明，以及推荐镜像/版本。只要这些信息到位，首轮可在 4090×1、22 核、90 GB 配置下做 0.5 小时 smoke run。
