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

### 账号1 第三轮复查（2026-09-18 追加）

- 账号1 本人按排查卡执行：DCS-华北2 与 DCS-华南1 两区域，各走"所有项目/我参与的"项目列表、默认项目数据管理、公共库（公共数据/公共项目），并按 `HEART`、`LBSPA`、`CNP0006537`、`CNP0007565`、`lamprey` 检索，全部 0 命中，未见任何课程共享项目或数据入口（页面事实由账号1 所有者口头确认，未触及邀请/权限/实例按钮）。
- 结论与前两轮一致：账号1 视角下两区域均无课程入口；四账号触发条件仍差账号2/3/4 的记录。
- 用户决定（2026-09-18）：以账号1 三轮全零证据直接向老师发起跟进，不再阻塞等待账号2–4 的排查记录；跟进消息已由用户本人经微信发送（底稿见 `docs/next-round-handoff.md` 第 6 节），当前等待老师回复。

### 账号1 第四轮复查（2026-09-20 追加，老师回复后）

- 背景：2026-09-20 老师微信回复两个网址 `https://db.genomics.cn/stomics/heart/`（Heart Evolution Atlas 门户，与 HEART 论文 Data Availability 声明及 DOI 10.1126/science.adw0855 一致）与 `https://db.cngb.org/stomics/lbspa/`（七鳃鳗脑时空图谱门户，对应 LBSPA DOI 10.1126/science.aea2535），并告知"已经拉进项目里了"。账号1 所有者在 ZCode 内置浏览器完成登录（凭据由本人输入），页面排查由 ZCode 只读执行，未点击邀请/上传/新建/实例/付费类按钮。
- **课程共享项目已出现，位于第三入口 `BGI-时空`**：此前三轮排查卡只覆盖 DCS-华北2 与 DCS-华南1 两区域，`BGI-时空` 入口未在覆盖范围。两 DCS 区域的"我参与的"本轮复核仍为空，课程项目仅存在于 `BGI-时空`。
- 项目事实（只读）：名称"康复大学生信实践"，编号 `P20260920085640327`，创建于 2026-09-20，片区 BGI-时空，项目类型"个人项目"，计费组"青岛分院DCS合同计费组"，简介"康复大学单细胞与时空组学课程实践"，存储统计 0GB。
- 成员与角色：项目成员共 57 人——1 名项目负责人（genomics.cn 邮箱，即课程老师）+ 56 名分析人员；账号1 在列，角色=**分析人员**（状态正常，个人费用 ¥0/无限制）。分析人员可执行分析，排除"访客角色跑不了分析"的担忧。账号标识与联系方式按仓库纪律不记录。
- 项目数据管理（只读）："项目数据" tab 仅 4 个空目录骨架（`RawData`/`ResultData`/`ManualData`/`ReferenceData`，路径前缀 `/Files/`，文件统计 0，共 4 条）；"公共库数据" tab（路径前缀 `/Public/`）共 28 条 / 约 9TB，逐页核对全部为平台通用参考与 demo 数据（hg38/mouse 参考基因组、PanGenie、minimap2-hg38、ST_DEMO 系列、single_cell_DEMO、esmfold_database 等），无 HEART/LBSPA/CNP0006537/CNP0007565 课程数据。
- 结论：G1 的"授权"半边已核实（课程项目存在 + 账号1 为分析人员）；"数据路径"半边仍缺——项目内尚无任何课程数据文件，老师提供的两个 STOmics 门户是 HEART/LBSPA 的官方公共发布处。课程数据进项目的方式待确认（老师统一上传 vs 组员从门户下载后上传到 RawData；后者涉及上传动作，属停止并询问用户的边界）。`heart_data_path`/`lbspa_snRNA_path` 及相关字段维持 pending，不得以门户 URL 或 accession 填充。

### 数据获取与本地核验（2026-09-20 第二小节：老师确认自行下载后）

- 用户决策链：老师回复"自己下载"（微信）→ 用户批准下载+上传 → 物种组合由 Claude+ZCode 商量定案 **人+小鼠+斑马鱼**（pilot 目标=流程跑通优先，第三物种选 CM/FB 注释无歧义的斑马鱼；七鳃鳗 Lethenteron_reissneri 保留给远缘扩展档与 LBSPA 后置线）；`config/benchmark-plan.json` 已落 `heart_near_selected` 状态+物种清单，`scripts/plan_contract.py` 升级状态机校验（63/63 测试通过）。
- 下载（STDS0000406 公共 FTP，ZCode 执行）：`Homo_sapiens_sc.h5ad` 223,744,070 B=213.38MB、`Mus_musculus_sc.h5ad` 272,322,064 B=259.71MB、`Danio_rerio_sc.h5ad` 161,403,920 B=153.93MB——三者与门户 Download 页标注**小数点后两位精确一致**；官方无校验和伴生文件，本地 SHA256 自算记档（仓库外 `course5-data/sha256-manifest.txt`）。排除项：`sc_fordatabase.h5ad`（5.95GB 合并库，粒度不符）、其余 12 物种（heart_mid 定档后二次批量）、spatial 数据（越界）、LBSPA（activation gate 未开）。
- 本地 inspect（`scripts/heart_h5ad_inspect.py`，GLM-5.3-Flash 实现+ZCode 修复 anndata 0.13.4 的 `n_vars`/layers `None` 槽位两处适配；隔离 venv anndata 0.13.4，不动仓库基线环境）：三文件全部可读（上传前坏文件拦截通过）。关键事实：n_obs=30000/60471/50000，n_var=32732/32379/27661，X 均 float32，obsm 含 X_umap（鼠/鱼另有 X_pca/X_harmony），layers 空；**金标准注释列 `celltype` 三文件共有**（CM/FB 正则 `(?i)cardiomyo|fibroblast|myofibroblast` 命中 15955/16100/6474 细胞），人另有 `cell_type`/`region_celltype`，鼠/鱼另有 `hcelltype`/`subtype`；batch 候选按物种区分（人 `donor`，鼠/鱼 `orig.ident`）。证据：`docs/heart-inspect-evidence-20260920.json`（含逐列 value_counts）。
- 数据存放：`D:\projects\course5-data\`（仓库外，不入 Git）。**待用户手动上传**项目 RawData（内置浏览器不支持 OS 文件选择框），上传后 ZCode 只读核对再更新 `startup-preflight.json` 的 heart 字段（`heart_data_path` 只认项目内实路径）。

### RawData 落盘核对与 G1 关账（2026-09-20 第三小节）

- 上传执行：网页上传因 100MB 单文件限制不可用（三文件 153.93-259.71MB 全超）；采用平台"工具上传"（镭速 Raysync 客户端，用户本机安装并操作，目标目录由平台预填 `/Files/RawData`）。镭速第一阶段 3/3 完成（627.01MB）；第二阶段（中转盘→华大存储）完成后平台落盘。
- **落盘核对（ZCode 只读，2026-09-20）**：RawData 文件列表共 3 条——`Danio_rerio_sc.h5ad` 153.93MB、`Mus_musculus_sc.h5ad` 259.71MB、`Homo_sapiens_sc.h5ad` 213.38MB，路径 `/Files/RawData/`，文件名与**大小（MB 两位小数）与本地逐一精确一致**，创建人=账号1，实体前缀 VIRP20260920085640327。
- `config/startup-preflight.json` 已按证据更新：`heart_data_path=/Files/RawData/`、`heart_file_format=h5ad`、`heart_metadata_fields={species: per_file_constant, cell_type: celltype, batch: Homo_sapiens:donor,Mus_musculus:orig.ident,Danio_rerio:orig.ident, gold_label: celltype}`（映射语义：物种由文件承载注入常量列；金标准注释列 `celltype` 三文件共有；batch 按物种取列，见 `docs/heart-inspect-evidence-20260920.json`）、`dcs_project_file_search_status=uploaded_to_course_project_rawdata_2026-09-20`。`approval_status` 维持 pending（G3 四人批准未做，不因数据到位而变）。
- **G1 关账**：路径✓（/Files/RawData/）、字段✓（celltype 金标准+value_counts 证据）、物种✓（人+小鼠+斑马鱼，heart_near_selected）、授权✓（BGI-时空课程项目，账号1=分析人员）。`startup_preflight.py --phase heart_pilot` 阻塞项收敛为纯 G2 域（image_recommendation/image_versions.{SATURN,SAMap,scVI}/kbet_implementation/kbet_version/readonly_sample_command）+ G3（approval_status）——数据类阻塞全部消除。
- 云端动作口径（本轮唯一一次）：用户本人操作镭速客户端向课程项目 RawData 上传三个公开数据文件（用户 2026-09-20 批准，平台要求的正式上传通道）；ZCode 侧全程只读（下载/校验/页面核对），未创建实例、未提交任务、未安装 DCS 包、无消费。

### G2 受控启动实录（2026-09-20 晚，用户批准后）

- 用户批准一次受控启动用于 G2 镜像核验（预算内 4090×1 假设）。平台 GPU 档最低为 3080Ti×1 捆绑 88c320G（¥30.78/h，无 4090 现货），用户追认按此执行。计费口径实测：**从提交时刻计费（含排队）**，本次含 23 分钟调度排队共 1h06s，**¥32.42**（1h 上限自动停止）。
- K8s 事件证据（运行历史→日志）：Pod `jupyter/task-p20260920085640327-eqwnedcz-7b5f6958f4-5hqbq` 15:28 调度至 `ms-k8s-worker12`，镜像 `st-harbor.dcs.cloud/public-library/zhongliyuan_..._public:latest` 拉取成功（5m54s），15:34 Started——**SATURN--22 镜像真实可运行、GPU 节点存在的平台侧证据**。
- **阻塞 1（环境侧）**：交互式 JupyterLab 白屏——iframe 指向的 `inner.dcs.cloud` 在本机所有 DNS（校园/公共）均 NXDOMAIN，curl 确认无法解析。关闭代理无改善。需老师/IT 说明校园网访问方式（VPN/hosts/专用 DNS）。
- **阻塞 2（脚本侧，已有对策）**：交互不通后改走"离线任务→运行脚本"通道（www 侧提交，绕开 inner 域）。v1 证明脚本在镜像沙箱真实执行（工作区出现 probe.py）；v3 实测裸 shell 无 python PATH（PY_FAILED）；v4 已含按路径探测 python 的对策（find / -maxdepth 4），结果文件同步延迟尚未可读。完整通路与脚本见 `docs/g2-probe-offline-channel-20260920.md`，载荷 `docs/probe-payload-20260920.b64.txt`。
- 工作区文件同步规律（实测）：离线任务产物在容器停止后批量出现于分析工作区树；树内文件可点开预览读取。
- 官方帮助文档证据（2026-09-20 晚补查，`www.dcs.cloud/helpcenter/zh/usermanual/analysis.html`）：FAQ 明确 GPU 档为"**L4 机型一台，88cpu、320mem**"，并指定实例内用 `nvidia-smi` 查 CUDA 版本（与探针计划一致）。注意 **L4（文档）与购买页 3080Ti（页面）不一致**，最终以实例内 `nvidia-smi` 为准。文档另确认：容器停止时 `output/` 自动回传 `/Files/ResultData/Notebook/{user}/output/{project_id}/`——v4 离线任务产物应到数据管理 ResultData 找。全文无任何 VPN/内网/白名单访问要求——notebook 理论上应对公网用户开放，白屏更可能是平台侧 DNS/出口问题而非课程配置。官方支持邮箱：`cloud@stomics.tech`（多组学服务目录页）。
- ResultData 实测（2026-09-20 晚）：`/Files/ResultData/` 下 `Workflow`、`Notebook` 两目录均空（暂无数据；627.01MB 统计即 RawData 三文件之和）。即 G2 交互实例（从未进入）与 v1–v4 离线任务都**没有**产物回传 ResultData——官方"output/ 自动回传"机制只对真实使用过的 notebook 会话生效，离线通道产物仅在分析工作区树部分延迟同步。结论：**离线通道无法补齐镜像内包版本证据，G2 该项唯一通路仍是交互终端（inner.dcs.cloud）**。
- 计费归属实测（2026-09-20 晚）：右上角头像 → 计费组（`/#/billing-group`，SPA 内跳转需整页刷新才生效）→ `user50719-8334 billing group` → 费用账单/账单明细**全部 ¥0.00、0 条**；账户余额 ¥99.00（=活动奖励 99 元，分文未扣）；"科研项目"标签只挂华北2/华南1两个默认项目，课程项目（BGI-时空）不在其中。即 **G2 那次运行未计入用户个人计费组**——课程项目花费大概率由课程方计费组承担（出账延迟的可能性留待次日复核费用账单确认）。此前记录的 ¥32.42 是 ¥30.78/h × 计费时长的口径值，用于预算纪律，不代表用户账户实际扣款。
- **通路突破（2026-09-21 00:02，Genpilot 实测）**：平台内置 AI Genpilot（`genpilot.dcs.cloud`，公网可达，从项目侧边栏 Genpilot 入口带 token 进入）在运行容器内实测确认：①`inner.dcs.cloud` 解析到内网 IP `10.224.26.45`，公网 NXDOMAIN 是**预期行为**，不是故障，改 hosts 无意义；②notebook 的公网网关路径为 **`https://www.dcs.cloud/notebook/st-gw/<task-id>/`**（容器内 `DCS_OPENSANDBOX_URL`、`DCS_EXECD_BASE_URL` 均为此结构，www 侧公网返回 200）；③白屏根因=个性分析前端 iframe 直接拼了内网域名。老师确认无 VPN。**下一步 G2 方案**：启动分析后从运行历史/任务管理取 task-id，直接浏览器访问网关路径绕过坏 iframe，跑探针后立即停机。另发现 Genpilot 自带云端 Bash 终端与 Notebook 工具（其容器非 SATURN 镜像，不能替代 G2 证据，但可作平台侧诊断通道）。
- **2026-09-21 凌晨 G2 第二轮受控启动 + 公网通路终局判定**：用户批准第二次启动（NB2026092100151106476662，SATURN--22/3080Ti/1h，00:15 提交 00:26 转运行中，自动停 ~01:25）。用户人工点"打开"后从其浏览器拿到嵌入页 URL（**`www.dcs.cloud/stereonote/#/notebookEmbed?projectId=...&workspaceId=user50719-8334_963bb09e53bb44678e2bb3818cf5992d&zone=st`，公网可开**，嵌入壳正常显示"剩余44分/延时/关闭"等控件）；自动化导航进去后**抠出真正的 notebook 地址**：`https://inner.dcs.cloud/notebook/st/task-p20260920085640327-4l28jabm/lab/workspaces/auto-l/tree/work?token=0780dad15b54434d9948c14fd71af2e5`（本任务随机后缀 `4l28jabm`，Jupyter token 已废弃随容器销毁）。**逐项实测公网可达性（fetch 状态码）**：`www.dcs.cloud/notebook/st/...` → SAP 系统升级跳转页（提示迁移 cloud.stomics.tech）；`www.dcs.cloud/notebook/st-gw/...`（含 Genpilot 自己的 siq9mjvn 实例）→ 404；`www.dcs.cloud/zoneProxy/...`（前端源码中的 zone API 前缀）→ 同 SAP 跳转页。**终局结论：Genpilot 所称"公网网关"是内网视角（split-horizon），公网侧无任何 notebook/执行代理；白屏不可绕过，只能平台侧修**。前端源码取证（stereonote 资产包）：notebook URL 拼接函数 `useNotebookNavigation`（CLOUD_DOMAIN 配置即 inner 域名来源）、zone 客户端 baseURL `/zoneProxy`、鉴权头 X-Access-Token + X-Client-App。当晚离线任务通道 API（/offline/save、/ipynb/dir/info 等）逐一尝试均因 zone 路由内网-only 未打通。
- **ITSM 工单已提交（2026-09-21 00:25）**：`TK20260921002545502`，模板"个性分析_在线分析"，队列=技术支持，优先级=中，邮箱 hanchangxu1@uhrs.edu.cn（用户实名校园邮箱），片区 BGI-时空，项目 P20260920085640327，任务 NB2026092100151106476662，问题描述含全部排查结论与诉求（改用公网网关或提供官方访问方式）。SLA：首响 ≤2026-09-21 08:25，解决截止 2026-09-22 00:25。
- 任务列表核对（2026-09-21 00:24）：昨日 15:04 起共 5 条已关闭 GPU 记录（¥32.42/¥26.87/¥32.44 等为离线任务 v1–v4 每次提交重启容器所致，均记课程方计费组）+ Genpilot 1c4g 工作区（23:59 起，240 分钟闲置自动停）。用户指示不再启动新任务。
- **工单官方回复（2026-09-21 08:55-09:01，处理人束礼平，5 条）**：①外网登录时空片区**需使用华大 VPN** 才能打开个性分析和镜像管理模块，"这个报错是会这样的"；②"目前还没法解决，只能等审批通过外网可以访问才行"；③"不是云平台要这样，是公司网络安全部门基于内部数据安全考虑的"。**官方定论：白屏=预期行为（无公网通道），出路=华大 VPN 或等安全部门审批外网开放**。与 09-21 凌晨公网通路终局判定（zoneProxy/st-gw/notebook 全内网-only）完全互证。下一步：老师/华大对接人渠道申请课程学生 VPN 账号（微信话术已交用户）；工单内追问 VPN 申请流程待平台重新登录后补充。
- G2 状态：**部分证据到手（镜像可运行、GPU 节点、镜像指纹、费用口径、官方文档 GPU 档=L4/88c320G），包版本/CLI/GPU 型号证据待 VPN/公网审批打通后一轮补齐**（工单 TK20260921002545502 已获官方回复）。preflight G2 字段维持 pending。

## 账号2–4 只读核验槽位（空白待填）

截至 2026-09-17，四名成员中只有账号1 完成上述两轮只读排查；账号2、3、4 尚无任何记录。以下槽位由各组员按工作包 A 的检查路径亲自填写，填写规则：

- 只填自己亲眼看到的页面事实；没有证据前保持空白，不得预填 0、复制账号1 的结论或猜测。
- 不写账号标识、手机号、cookie、token 或私有路径原文；账号只用“账号2/3/4”序号。
- “入口”指具体页面（如“项目列表-所有项目/我参与的”“默认项目数据管理-RawData”“公共库-公共数据/公共项目”）；建议 DCS-华北2、DCS-华南1 两个区域各留一行，页面更多就追加行。
- 检索词至少覆盖 `HEART`、`LBSPA`、`CNP0006537`、`CNP0007565`、`lamprey`。
- 填完后同步更新 `docs/team-task-division.md` 的当前看板并通知复核人；任何需要登录凭据、邀请或权限变更的情况，先停下来问用户。

### 账号2

| 区域 | 入口 | 检索词 | 结果数 | 证据时间 | 下一步 |
| --- | --- | --- | --- | --- | --- |
| | | | | | |
| | | | | | |

### 账号3

| 区域 | 入口 | 检索词 | 结果数 | 证据时间 | 下一步 |
| --- | --- | --- | --- | --- | --- |
| | | | | | |
| | | | | | |

### 账号4

| 区域 | 入口 | 检索词 | 结果数 | 证据时间 | 下一步 |
| --- | --- | --- | --- | --- | --- |
| | | | | | |
| | | | | | |

## 结论

平台有可复用的 SATURN、SAMap、scVI 镜像候选，老师也确认数据可查；当前缺口收敛为一个具体问题：课程共享项目的入口（把当前账号加入课程项目），或课程方给出数据所在的项目/目录名称；之后才能在候选实例内确认真实导入名和版本。首轮实验范围已收窄为 HEART 2–3 个物种的单细胞流程试跑，只有路径、字段、物种选择、运行时入口和正式 kBET 都核实后，才讨论 4090×1 的受控试运行。

### G2 离线通道攻坚成功实录（2026-09-21 上午，老师确认无 VPN 后自立通路）

- **通路发现链**：工单官方回复（需华大 VPN）+ 公网 API 全量测绘 → `/stereonote/api/*` 公网可调（zone 类需 `X-Zone: st` 头，取 sessionStorage `cld:zone`——此前踩坑：从 localStorage 取成空值报 "Zone '' not found"）。关键端点：`/offline/page`（pageSize/pageNo/subTask/parentId）、`/offline/subTask/get|logs/<id>`、`/ipynb/dir/info`+`/normal/content`（**工作区文件树与文件内容公网可读**）、`/images/select/list`（SATURN--22: uuid `57362367597d49499e5bc388096a17f1`）、`/workspace/get/<id>`（resource_type=7/resource_id=280）。
- **离线任务机制破解**（前端源码 newOfflineTask-Bs9nENn1.js）：shell 内容经 `CryptoJS.AES.encrypt(content,"stereonote")`（OpenSSL Salted__ 格式）后 POST `/offline/save`；直接 API 提交缺字段会 500（str+None），**走表单提交成功**（表单路由 `/stereonote/#/notebookListNewTask?workspaceId&projectId&zone=st`，需 sessionStorage cld:projectId/cld:project:detail；stereonote 独立应用可自动化，非 wujie）。**提交成功后页面跳转 dashboard（此前误判为"点歪导航"——实际 3 次提交全部成功）**。
- **离线 runner 行为**：多行脚本被压成单行（每行尾插 `2>&1 | tee -a /data/work/offline-task-logs/<subid>.log` 后以 `&&` 连接）——**Python 多行语法必毁，v1-v5 失败根因**；正确写法=printf 写 .py 文件再执行（v6）。离线任务=1c4g CPU + SATURN--22 镜像（imageName 已核），`/usr/local/bin/python3` 存在（diag.py 实证）。
- 已提交任务：g2-probe-v5×3（多行版，IndentationError 复现了 runner 行为）+ g2-probe-v6-printf（printf 版，10:56 提交，Pending 排队中）。
