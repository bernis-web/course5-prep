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
