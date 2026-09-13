# DCS Cloud 只读核验记录

核验日期：2026-09-09、2026-09-10。所有操作均为已登录页面的只读浏览，没有创建实例、复制数据、上传文件、提交任务或支付。仓库不记录真实账号、手机号、cookie、token 或私有挂载路径。

## 账户与项目

- 区域：DCS-华北2。
- 可用余额：¥99.00。
- 当前账号只有一个默认项目；项目名中的账号标识不写入仓库。
- 当前项目数据管理页：项目数据为 0 条。
- 项目公共库数据页：根目录显示 25 条、总计约 5TB；2026-09-10 用文件夹/文件名搜索 `HEART` 和 `LBSPA` 均为 0 条。
- 公共项目页列出的 7 个项目均为通用演示项目，没有显示 HEART 或 LBSPA 项目。
- 公共库的“公共数据”和“公共项目”目录用 `HEART` 精确搜索也均为 0 条。这个结果只描述当前账号、区域和可见目录，不证明课程共享目录或 Genpilot 中不存在数据。
- Genpilot 学术搜索使用独立登录态；2026-09-10 用户完成独立登录后，文献搜索分别以两篇论文完整题名精确命中元数据。HEART 为 DOI `10.1126/science.adw0855`，LBSPA 为 DOI `10.1126/science.aea2535`。推荐流没有被当作检索证据。

## 论文数据入口回查

- HEART 论文 Data Availability 给出 CNGB accession `CNP0006537`，并给出处理后数据门户 `https://db.genomics.cn/stomics/heart/`。
- LBSPA 论文 Data Availability 给出 CNGB accession `CNP0007565`。
- 2026-09-10 在当前默认项目的“公共库数据”页分别用 `CNP0006537` 和 `CNP0007565` 搜索，均返回 0 条。
- 因此论文公共数据来源已经定位，但当前账号/区域可见的 DCS 文件目录仍没有暴露课程挂载位置、对象格式或字段。公共 accession 不能填入 `heart_data_path` 或 `lbspa_snRNA_path`，启动门继续保持 `pending`。

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

### BENGAL--SAMap--17

- 名称：`BENGAL--SAMap--17`，大小 2.8 GB，语言为 R、python。
- Python3 清单中同时出现 `samap==1.0.1` 与 `samap==1.0.16`，并列出 `anndata==0.10.2`、`scanpy==1.10.3`、`scikit-learn==1.3.1`。
- 同一页面出现两个 SAMap 版本，可能来自不同环境或重复清单；在候选实例内完成 `import samap`、版本和实际入口核验前，不把任一版本写成正式锁定版本。

### scvi_zt

- 名称：`scvi_zt`，标签为 `scvi`。
- 页面 Bash 指令包含 `pip install scanpy` 和 `pip install scvi-tools`，并指定 CPU 版 PyTorch 安装源。
- 因此它可以作为 CPU/兼容性参考，但不应默认当作 GPU 基准环境。
- 公共镜像搜索 `scVI` 共返回 6 个候选；镜像名和搜索结果数量只能用于发现候选，不能替代实例内版本证据。

## 后续老师回复与证据边界

老师在 2026-09-10 回复：HEART、LBSPA 数据及相关信息可在 DCS 查询，相关工具已经安装。该回复修正了“需要老师另行提供全部内容”的工作方式，但没有给出可直接写入配置的路径、字段、物种清单、导入名或版本。

2026-09-10 已复核公共库目录、默认项目的公共库数据页、镜像详情和 Genpilot 文献元数据。论文题名、DOI 和 CNGB accession 已定位；`HEART`、`LBSPA` 及两个 accession 仍未在当前可见 DCS 文件目录中定位。下一步由组员继续查课程共享项目/目录入口，或请课程方指出入口。未知路径、字段和物种清单继续保持 `pending`。

## 2026-09-12 只读核验（GLM-5.3-Flash 接手首轮）

核验日期：2026-09-12。已登录页面的只读浏览：项目列表、默认项目数据管理、公共库（公共数据 / 公共项目 / 公共镜像）。没有创建实例、复制数据、上传文件、提交任务或支付；页面账号标识与项目编号不写入仓库。

### 项目与共享入口（G1）

- 项目页"所有项目"仅 1 个默认项目；"我负责的 / 我管理的 / 我参与的"中"我参与的"为空（页面提示"您目前没有项目"）。
- 默认项目数据管理 > 项目数据：仅 RawData、ResultData、ManualData 三个系统默认文件夹；进入 RawData 内部无任何文件。
- 结论：当前账号（DCS-华北2）可见范围内不存在课程共享项目，项目内也没有挂载课程数据。课程数据"存在性已知、路径未证实"。

### 公共库数据与公共项目（G1）

- 公共数据栏目共 60 条。搜索 `HEART`、`heart`、`LBSPA`、`lamprey`、`heart atlas`、`cross-species`、`CNP0006537`、`CNP0007565` 均为 0 条。
- 公共项目栏目共 7 条，仍全部为通用 demo 项目（Stereo-seq_FFPE_demo、single_cell_RNA-seq_demo、Bulk_RNA-seq _demo、WGS_VariantCalling_demo、Stereo_seq_H&E_Demo、Single_Cell_ATAC-seq_Demo、Stereo-seq_ssDNA_Demo），没有课程项目。
- 与 2026-09-09/10 结论一致：公共目录不暴露课程挂载位置。老师所说"可在 DCS 查询"更可能指向尚未加入的课程共享项目，或需授权后才可见的私有挂载。

### 公共镜像（G2 页面级）

- 镜像库共 990 个。
- `SATURN` 命中 2 个：`SATURN--22`（已知默认候选）与 `SATURN--21`（33.6 G，更新 2026-07-27，本轮新记录）。`SATURN--21` 页面 Python3 清单与 `SATURN--22` 页面版本一致：`anndata==0.10.8`、`scanpy==1.10.3`、`scvi-tools==1.1.6.post2`、`torch==2.6.0`、`fair-esm==2.0.0`、`faiss-gpu==1.7.2`、`scikit-learn==1.6.1`；两个镜像页面均未列出名为 `saturn` 的包或命令。
- `SAMap` 命中 3 个：`samap_all`、`BENGAL--SAMap--17`（页面双版本冲突维持原判）、`samap_zhangzijian4`（2025-09-05，新候选，页面未展开核验）。
- `scVI` 命中 6 个：`scvi_zt`（CPU 参考）、`integration_scvi_07`、`integration_scvi_06`、`scvi`（python3.9+scvi）、`docker-scvi`、`BENGAL--integration--noscvi--01`；后 5 个仅记录名称，未展开核验。
- `kBET` 命中 0 个：平台无预置 kBET 专用镜像。正式 kBET 只能在候选镜像实例内确认实现与版本，G2 该项继续阻塞。
- 页面声明仍不能替代实例内 import / `--version` / GPU 证据；`config/startup-preflight.json` 全部字段维持 pending。

### 区域排查（2026-09-12 追加）

- 平台仅有两个区域：`DCS-华北2`（默认）与 `DCS-华南1`。
- 已切换到 `DCS-华南1` 只读检查：项目"所有项目"仅显示一个首次访问时自动开通的空默认项目，"我参与的"仍为空；公共数据搜索 `HEART`、`LBSPA`、`CNP0006537`、`CNP0007565`、`lamprey` 均 0 条。检查后已切回 `DCS-华北2`。
- 结论：两个区域都不存在课程共享项目或课程数据。区域差异假设已排除，剩余唯一解释是"账号尚未被加入课程共享项目，或课程数据入口需要课程方指路"。

## 结论

平台有可复用的 SATURN、SAMap、scVI 镜像候选，老师也确认数据可查；当前缺口收敛为一个具体问题：课程共享项目的入口（把当前账号加入课程项目），或课程方给出数据所在的项目/目录名称；之后才能在候选实例内确认真实导入名和版本。首轮实验范围已收窄为 HEART 2–3 个物种的单细胞流程试跑，只有路径、字段、物种选择、运行时入口和正式 kBET 都核实后，才讨论 4090×1 的受控试运行。
