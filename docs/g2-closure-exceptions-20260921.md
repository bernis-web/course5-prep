# G2 关账例外记录（2026-09-21）

> 依据：双评审咨询（Codex `codex exec` + Claude Code glm-5.3-flash，2026-09-21 上午，原文摘录见文末）。结论：G2 以**"证据整理完成 + 三项记录例外"**状态关账进入 G3 四人审批；进入审批≠批准运行，`ready_for_execution` 在例外补齐前必须保持 false。

## 例外清单（每项含责任人/验收标准/截止点/停止条件）

### 例外 1：image_versions.SAMap 运行时版本未实测

- **现状**：BENGAL--SAMap--17 镜像不在本项目可选范围（项目目录 22 个镜像无 SAMap 系，`/images/my/pub/page` 实测）；平台页面版本自相矛盾（1.0.1 与 1.0.16 并存，`docs/dcs-image-probe-plan.md`）。
- **处置**：preflight 填证据型状态串（不虚填任一版本号，沿用 image_versions.SATURN 的先例）：`page_ambiguous_1.0.1_or_1.0.16_pending_runtime_verification`。
- **验收标准**：SAMap 环境就绪时（专门工作区或镜像入项），离线探针实测 `import samap` 版本并回填。
- **责任人**：账号1（ZCode 辅助）；**截止点**：SAMap 方法正式纳入评测前；**停止条件**：若实测版本与页面两值均不符，按"页面证据无效"重开 G2 对应项。

### 例外 2：kBET 实现路线待四人裁决（评审分歧点）

- **现状**：平台无 kBET 预置镜像。两评审结论相反：
  - **Codex**：选原版 R 实现（`theislab/kBET` 钉完整 commit SHA）——scIB 的 kBET 是 R 包封装并未绕开安装；scib-metrics 与原实现不一致，替换属方法变更需显式批准，不能静默换。
  - **Claude**：选 scib-metrics（pip 可装、与 scanpy 生态一致）——但 kbet_version 必须保持 null 待实测钉死。
- **处置**：preflight `kbet_implementation` 填证据型状态串：`pending_team_decision_original_R_vs_scib_metrics（见 docs/g2-closure-exceptions-20260921.md 例外2）`；**决定权交 G3 四人批准**（批准材料须含两方案对比）。
- **验收标准**：四人批准记录中明确所选实现；首跑时实测版本号回填 `kbet_version` 并留冒烟测试证据。
- **责任人**：四人小组；**截止点**：HEART pilot 启动批准前；**停止条件**：若所选实现安装失败或冒烟不过，回到本例外重新裁决。

### 例外 3：kbet_version 保持 null

- **处置**：两评审一致——版本号只能实测填（R 包无 CRAN 号则记 commit SHA；scib-metrics 记 pip 版本）。preflight 该项维持阻塞（诚实红灯）。
- **验收标准**：首跑环境内 `pip show scib-metrics` 或 R `packageVersion('kBET')`/commit 记录取证。

## G2 关账声明

- **已完成的 G2 证据**（`docs/g2-offline-probe-evidence-20260921.md`）：SATURN--22 镜像内实测 Python 3.9.12 / scvi-tools 1.1.6.post2 / scanpy 1.10.3 / torch 2.6.0+cu124（三项与页面声明一致）/ anndata 0.10.8 / fair-esm 2.0.0 / faiss-gpu 1.7.2；SATURN 包不存在于镜像（需实例内安装）；离线任务通道公网可用（readonly_sample_command 已回填）；GPU 型号维持 K8s 事件+购买页 3080Ti+官方 FAQ L4 多源证据（GPU 实例内 nvidia-smi 待未来核验）。
- **G2 状态**：证据整理完成，带上述三项记录例外关账，**进入 G3 不等于批准运行**；`startup_preflight.py --phase heart_pilot` 预期阻塞：`approval_status`（G3）+ `kbet_version`（例外 3）。

## 评审原文摘录

**Codex**（条件性评审，未能读文件）：
1. SAMap：选 C——版本留 null/例外记录页面歧义与"待运行时核验"，不把任一值当实测版本；风险=镜像不可选可能是执行路径未落实。
2. kBET：选 A——原版 R 钉 commit；scib 是封装仍需 R；scib-metrics 与原实现不一致，替换须显式批准。
3. G2："有条件进入 G3 四人审批"而非无条件通过；例外须有责任人/截止点/验收标准/停止条件，防例外变永久豁免。

**Claude**（读了仓库文件）：
1. SAMap：选 C——证据型状态串（SATURN 先例）。
2. kBET：选 B 修正版——scib-metrics，kbet_version 保持 null 待实测钉死。
3. G2：可有记录例外关账进 G3，但 ready_for_execution 必须等核验回填后才允许变绿。

## 附：G3 批准后首跑实录（2026-09-21 12:0x）

- **G3 批准**：用户代表四人小组批准（"都同意，按你推荐的来"，2026-09-21）；kBET 裁决=方案 B scib-metrics（方法变更显式记录）。`approval_status=confirmed`（31efade），preflight 阻塞仅剩 kbet_version。
- **v8 冒烟（g3-smoke-install-v8，1c4g/SATURN--22，12:07 完成）结论：离线容器无外网**——`urlopen pypi.org → Errno 101 Network is unreachable`；pip 安装 scib-metrics/saturn 全部失败（无网络+`/home/stereonote/.local` 权限拒绝）；`saturn-scripts` 在索引中不存在。**运行时装包路线不可行**。
- **修正路线**：SATURN 与 scib-metrics（kBET）须经平台"镜像管理→添加镜像"自建镜像烘焙安装（镜像构建是平台官方装包通道）；scVI 已在镜像内，基线不受影响。例外 2/3 的补证路径更新为"自建镜像后实例内版本取证"。
- **v9 挂载探测（g3-mount-probe-v9，1c4g，12:09 提交）**：探 /Files/RawData 等路径在离线容器内的可见性——决定 GPU scVI 基线能否直接读课程数据。

## 附2：v9 挂载实证 + v10 GPU 基线提交（2026-09-21 12:25/13:15）

- **v9（g3-mount-probe-v9，1c4g，12:25 完成）关键结论**：离线任务容器内 `/Files/RawData/` **直接可见三物种 h5ad**（Danio_rerio_sc.h5ad / Mus_musculus_sc.h5ad / Homo_sapiens_sc.h5ad），课程项目数据无需复制即可只读挂载使用；工作区目录在容器内挂载为 `/data/work`（即 /jdfsms1/.../online 的容器内视角）。scVI 基线的数据链路打通。
- **v10（g3-scvi-baseline-v10，3080Ti×1 88c320g，13:15:50 提交）**：GPU 档离线任务——nvidia-smi 取证 GPU 型号 → 人心脏 30k 细胞 HVG2000 → scVI(5 epoch, n_latent=10, donor batch, celltype labels) → KNN15 金标准准确率 + 耗时。结果文件 scvi_v10_out.txt / gpu_v10.txt 落工作区后经公网 API 读取。后台监控中。
- 运维注：GPU 档任务从提交起计费（课程方账户）；脚本无死循环、数据量小（213MB），总时长受控。
