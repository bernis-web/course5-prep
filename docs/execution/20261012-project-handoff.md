# 课题5 全项目交接文档（2026-10-12）

> 本文件是**整个项目**的交接入口：覆盖目标、当前进度、全部关键产物与 SHA、硬边界、平台阻塞、待决策事项与恢复步骤。
> 供下一个执行者（人或 agent，如 Codex）在**不读全部历史文档**的前提下接手。
> 生成方式：只读核对（`sha256sum` / `git` / 文件实读），未运行任何模型运算，未提交任何平台任务。
> 配套细节文档见 §12 文档地图；本文件与细节冲突时，以细节文档中的原始记录为准。

---

## 一、一页速览

| 项 | 现状 |
|---|---|
| 项目 | 课题5：跨物种单细胞 RNA-seq 方法比较（SATURN / SAMap / ortholog-PCA），三物种心脏数据 |
| 工作目录 | `D:\projects\course5-prep` |
| 分支 / HEAD | `codex/teacher-reply-report-prep` / `8b597d78…`；工作树 269 条未提交改动（**保留原样，不动**） |
| 阶段 0 基线 | ✅ completed（门状态 `passed`，11/11 输入 SHA 匹配） |
| 阶段 1 单方向 smoke | ✅ completed（A-smoke 13 文件，16/16 校验，与冻结件**逐字节相同**） |
| 阶段 2 第一步 隔离层 | ✅ completed（wrapper A/B + DCS 脚本，6 轮 Claude + 1 轮 GenPilot 审阅，第 6 轮 PASS） |
| 阶段 2 第二步 DCS 全量复算 | ⛔ **blocked**——任务 `W202610110124739` 排队 >12h 容器未启动（平台队列问题，非配置问题） |
| 汇报材料 | 汇报 1 修订版已出；汇报 3–10 共 8 份 PPT 已出（校模板版） |
| 唯一人工治理关口 | **映射表 v1 导师签认**（未完成） |
| 主要外部阻塞 | DCS 离线/WDL 调度通道（两个 waiting 任务，均 0 计费） |
| 累计平台花费 | 1.13 元（历史 WDL 系列，已结算） |
| 下一个动作 | ① 提交平台工单（正文已备，需登录）② 等调度 → 回收产物 → 跑核对脚本 |

---

## 二、项目目标与范围

**目标**：在同一份三物种单细胞心脏数据上，对三种跨物种方法（ortholog-PCA / SATURN / SAMap）做可追溯、可复算的对照，产出 8–10 次阶段汇报材料，最终收敛到"实验与材料已收口，只等老师反馈"。

**三物种数据**（单细胞为主，平台已确认含 `cell_or_nuclei` 字段）：

| 物种 | 细胞数 | 本地文件 | SHA-256 前缀 | 字节数 |
|---|---|---|---|---|
| human | 1,528 | `local_human_s.h5ad` | `af41618b6941d2f1` | 26,233,600 |
| mouse | 1,535 | `local_mouse_s.h5ad` | `7fda583d59d3767e` | 27,745,005 |
| zebrafish | 1,543 | `local_zebrafish_s.h5ad` | `6b1e8798d5f848ac` | 16,931,148 |

三个文件已于 2026-10-11 19:29–19:30 上传到平台 `/Files/` 根，容器侧 SHA 复核**精确命中**（见 §8）。

**评估规模**：6 方向（人鼠鱼两两）× 3 层级（exact / coarse / fine）= 18 格/方法。

---

## 三、三方法现状与关键数字

> 全部为 **transductive / in-sample** 口径，**不得**写成 inductive、泛化能力或临床结论。

### 3.1 ortholog-PCA（label-free 参考方法）

- **状态**：candidate-final（有本地 `metrics.json` + manifest + 18 份 predictions + 18 份 confusion，文件级证据完整）
- **coarse 六方向**：`0.8618 / 0.7369 / 0.1961 / 0.2755 / 0.1813 / 0.5761`
- **冻结 metrics SHA-256**：`b2b3ac6bc37c4108…c725`（`results/pilot-v1/ortholog-pca-v98/metrics.json`）
- **口径限定**：label-free 只适用于**表示层**（PCA 载荷不用标签）；PCA 在 src+tgt 联合矩阵上拟合，是 transductive 投影。

### 3.2 SAMap v98（label-aware，`keys=cell_type`）

- **状态**：candidate-final（探索性；per_cell 已复算）
- **coarse human→mouse**：`0.1050`；当前结论是本规模下**没有超过随机/多数类基线的跨物种对齐信号**
- **冻结 metrics SHA-256**：`3c719399…54f`（`results/pilot-v1/samap-v98/wdl-run/extracted/metrics.json`）
- **版本链（重要）**：线上权威 = 410 行版（md5 `56bb6035` / sha256 `f7f21ff4…`）+ 两处 sed → 部署版 `c0f05b89…`；本地 checked-in `run_samap_compliant_v98.py`（437 行，sha256 `8da8c8e7…`）**不是**线上权威。另有一个 450 行的 DCS 变体 `run_samap_compliant_v98_dcs.py`（`71dd08a3…`）。
- **无原生冻结图投影**：后续任何 inductive 尝试只能命名 `SAMap-approx`。

### 3.3 SATURN

- **v99 统一评分器**：human→mouse coarse `0.4844`；有容器级 provenance 与回收锚点；metrics SHA `d1081cfd…261`
- **v97g**：human→mouse coarse `0.6179`，**日志级数字**——无逐细胞文件，不得升级为文件级
- **v99 与 v97g 标签空间不同**，不能合并成排名；必须双口径双报
- **标签机制（已收窄的正确表述）**：默认配置下训练使用 `labels` 通道（`wheelhouse/saturn-src/train-saturn.py:100-103`）；`ref_labels` 主要用于输出/评估（`scripts/dcs_provenance_v99.py:362`）。源码另有默认关闭的 `--use_ref_labels` 开关（`:70`、`:100-101`、`:1025`）。原始训练命令未留档 → 运行时版本与命令列"待核实"。
- **inductive 源码级 blocked**：未见物种会 KeyError（`species_to_gene_idx` 按物种拼接，无预留槽）；物种 one-hot 宽度烧进权重形状；每物种 HVG 用自身表达选取（若照搬即泄漏）。→ SATURN 不能参与"冻结投影"，需另立重训方案。

### 3.4 辅助证据（方向性，非冠军证据）

| 项 | 数字 | 限定 |
|---|---|---|
| ESM2 消融 | 67.4% → 20.4% | v72-era 同协议配对；v97g 对应消融未重跑 |
| 物种内 ceiling | 85.5 / 93.5 / 74.2 | 成对引用；不作为跨方法冠军证据 |
| seed 稳定性 | 67.1±3.8；鱼方向双峰 | 单 seed 限制；只支持方向性判断 |

---

## 四、证据等级体系（必须沿用）

**五档状态（互斥）**：`confirmed`（独立审计/双通道互证）/ `candidate-final`（过 Gate 待外部确认）/ `exploratory`（初步，口径未冻结）/ `pending`（等外部条件）/ `blocked`（已知阻塞，非重试可解）。

**非互斥标签**：`confirmed-for-recompute`——隔离复算已通过，可作为后续复算的可信起点；**不等于**全量 benchmark 已完成。

**四个存在层级**：`[本地]` 文件存在并校验 / `[容器/日志]` 只在容器或日志确认 / `[数字级]` 有数字无逐细胞文件 / `[已复算]` 已独立重算核对。

> 容器级存在 ≠ 本地已回收；日志级数字 ≠ 文件级 provenance。二者都不许混写。

---

## 五、已完成工作（可独立成立）

### 5.1 阶段 0：基线冻结（2026-10-10）

- 产物：`docs/execution/20261010-baseline.md`、`results/phase-20261010/run_scope.json`、`results/phase-20261010/review-gate-status.json`
- 门状态：`status=passed`、`task1=completed`、`task2=not_started`；`dcs_submission/training/gpu/recharge` 全 `false`
- 输入核对：`results/phase-20261010/baseline/input-sha256.tsv` 11/11 匹配
- 关键记录：**覆盖风险清单**（§7 详列）

### 5.2 阶段 1：单方向零成本 smoke（A-smoke）

- 目录：`results/phase-20261010/A-smoke/`（13 文件）
- 范围：**仅** human→mouse / coarse 一格
- 结果：`acc=0.8618`、`majority=0.4817`、`n_q=1505`、`n_q_total=1535`、`coverage=0.9805`
- 验收：`verification.json` **16/16 通过**，`failed_checks: []`
- **混淆矩阵与逐细胞预测与冻结件逐字节相同**
- `results/pilot-v1` 零触碰
- 标签：`confirmed-for-recompute`
- 审阅：外部 Claude 3 轮（revise → revise → PASS）

### 5.3 阶段 2 第一步：输出隔离层

- 产物（3 个新脚本 + 报告）：
  - `scripts/ortholog_pca_full_isolated.py`（wrapper A，oPCA 全量隔离）SHA `48d79ad1c41d85ac…e83c`
  - `scripts/run_samap_full_isolated.py`（wrapper B，SAMap 全量隔离）SHA `6f1385cd12d464fc…26fa`
  - `scripts/ortholog_pca_dcs_v2.py`（DCS 版，路径适配平台）SHA `e802ffe198a0d819…dae8`
  - 报告：`docs/execution/20261011-stage2-isolation-report.md`
  - 审阅归档：`docs/execution/20261011-stage2-review-archive.md`（6 轮 Claude + 1 轮 GenPilot 原文）
  - 自包含审阅包：`results/phase-20261010/review-packet/`（8 个 `.txt` + INDEX）
- 隔离语义（已实测）：
  - dry-run 预检 **A 18/18、B 20/20**，exit 0
  - 目标目录已存在 → exit 3；输出落在 `results/pilot-v1` 内 → exit 3；cwd 非仓库根 → exit 2
  - 12 项拒绝负例全部正确
- 审阅结论：**第 6 轮 PASS，must_fix 空**；两轮 REVISE 的实质缺陷（CWD 绕过冻结守卫、wrapper B 只比 16 位前缀、preflight 漏查 ortholog 文件、契约按脚本分列、版本链对账）**全部已修**

### 5.4 阶段 2 第二步：DCS 全量复算（准备完毕，执行被阻塞）

- 准备产物：`docs/execution/20261011-stage2-dcs-recompute-prep.md`（21 节，含平台核对、脚本投递、任务提交、队列诊断全过程）
- 核对脚本已就绪：`scripts/verify_dcs_recompute.py` SHA `ea3d7c32fa0c940f…462b`
  - 功能：6 方向×3 层 `acc/majority/shuffle_p/n_q/coverage_q` 与冻结 metrics 逐格比对（tol=1e-12）+ 独立复算（对角和 == round(acc×n_q)）+ 36 份文件逐字节 SHA
  - **双向自测通过**：假数据 → `VERIFY|7/27`；真实冻结件 → **`VERIFY|127/127|byte_identical=36/36`**
  - 全通过返回 0，否则返回 4

---

## 六、关键文件与 SHA-256 总表（2026-10-12 实测）

### 6.1 权威脚本（**禁止修改**）

| 文件 | SHA-256 前缀…后缀 | 说明 |
|---|---|---|
| `scripts/ortholog_pca_local_v1.py` | `6582d873…0c44` | oPCA 权威版（= 冻结 manifest 的 script_sha256） |
| `scripts/run_samap_compliant_v98.py` | `8da8c8e7…e4a7` | 本地 437 行变体（**非线上权威**，见 §3.2） |

### 6.2 新增隔离与工具脚本

| 文件 | SHA-256 前缀…后缀 |
|---|---|
| `scripts/ortholog_pca_full_isolated.py` | `48d79ad1…e83c` |
| `scripts/run_samap_full_isolated.py` | `6f1385cd…26fa` |
| `scripts/ortholog_pca_dcs_v2.py` | `e802ffe1…dae8` |
| `scripts/verify_dcs_recompute.py` | `ea3d7c32…462b` |

### 6.3 冻结输入与结果

| 文件 | SHA-256 前缀…后缀 |
|---|---|
| `config/heart-celltype-map-v1.tsv` | `be985735…3165`（**待导师签认**） |
| `results/pilot-v1/ortholog-pca-v98/metrics.json` | `b2b3ac6b…c725` |
| `results/pilot-v1/samap-v98/wdl-run/extracted/metrics.json` | `3c719399…54f` |
| `results/pilot-v1/saturn-v99/raw/recovered-20261001/metrics.json` | `d1081cfd…261` |

### 6.4 交付物

| 文件 | SHA-256 前缀…后缀 | 说明 |
|---|---|---|
| `results/stage-reports-20261012/课题5第01次汇报_现状与问题定稿_修订版.pptx` | `c2e15729…8804` | 汇报 1 修订版（7 页，不覆盖历史稿） |
| `docs/reports/report-01-evidence-status-freeze-20261012.md` | `6546b7eb…6d2b` | 汇报 1 修订版内容稿 |
| `results/stage-reports-20261009/`（8 份 PPT + SHA256SUMS.txt） | 见其 `SHA256SUMS.txt` | 汇报 3–10 校模板版 |
| `deliverables/course5-final-report.docx` | `593d31e6…788f` | Word 终版（随汇报周期更新） |
| `results/phase1-revised-v2/课题5第一阶段成果汇报_终版.pptx` | `9ab1e69d…4547` | 老师批语修订终版（2026-10-08） |

---

## 七、硬边界与禁止事项（不可放宽）

### 7.1 科研口径

1. 既有跨物种结果**只能**称 `transductive/in-sample`；不得写成 inductive、泛化能力或临床结论。
2. oPCA 是 label-free **仅限表示层**；v98 的 PCA 在 src+tgt 联合矩阵上拟合 → 不得写成 inductive。
3. SATURN 训练标签通道写 `labels`，`ref_labels` 主要用于输出/评估；**不得**笼统写"ref_labels 参与训练"。
4. SAMap 只能按 `SAMap-approx` 记录；C2 最多 **54 格**（oPCA 27 + SAMap-approx 27），不得宣称完整 81 格。
5. v97g 是**日志级**数字，不得伪造逐细胞 predictions/confusion，不得升级为 confirmed。
6. **不把三个方法按一个总分排"冠军"**；比较时必须并列协议、coverage、n_q 和证据等级。
7. 没有正式统计检验时只写"数值更高/方向性差异"，**不得**写"显著优于"。
8. 单细胞优先：只筛 `cell_or_nuclei == "cell"`；单核后置小规模对照；空间数据不进主评估。

### 7.2 数据与文件

9. **不删除、覆盖或回退现有结果**；新结果写入新目录/新版本。
10. `results/pilot-v1` **保持冻结**：只读引用，任何脚本全量模式在隔离门通过前不得直写。
11. 不 reset / checkout / clean，不删除既有未提交改动（269 条保留原样）。
12. 不修改权威脚本 `ortholog_pca_local_v1.py` / `run_samap_compliant_v98.py`。
13. **任何 PPT/Word 数字必须从冻结 metrics/证据矩阵生成或逐格核对**，禁止手工凭记忆改表。
14. 不覆盖旧 PPT、旧报告或用户已有改动；修订版一律另存新文件。
15. 映射表 v1 在导师签字前保持 `needs-reviewer`。

### 7.3 平台与费用

16. **运算不放在本地，用 DCS**（用户明确要求）。
17. DCS 任务：**只提交一次**；失败 / Pending 超窗 / OOM / 非 0 退出 → 立即停止报告，**不自动重投、不加资源、不充值**。
18. 费用上限 **1 元**（单次 WDL）。
19. **不对已结束任务进行轮询**；反复执行时不得陷入死循环。
20. **不读取、打印、复制或保存 token、密码、cookie、API key、凭据或环境变量值**。

### 7.4 覆盖风险清单（历史高危路径，禁止直接运行）

| 脚本 | 风险 |
|---|---|
| `scripts/ortholog_pca_local_v1.py:158` | 全量模式直写 `results/pilot-v1/ortholog-pca-v98`，**无守卫**（只有 `--smoke` 分支带守卫） |
| `scripts/run_samap_compliant_v98.py:249-250` | `output_dir = results/pilot-v1/samap-v98` + `mkdir(exist_ok=True)`，**无守卫** |
| `scripts/extract_v99_from_logs_v1.py:17`、`scripts/parse_v99_rec_log_v1.py:21` | `RAW = results/pilot-v1/saturn-v99/raw`，重跑会重写 recovered 目录 |

→ 全部须经 §5.3 的隔离 wrapper 调用。

---

## 八、平台状态与阻塞

### 8.1 当前任务

| 任务号 | 资源档 | 提交时间 | 状态 | 费用 |
|---|---|---|---|---|
| `W202610110113185` | 1c4Gi | 10-11 20:20 | **已取消**（我方手动，排队 1h40m） | 0.00 |
| `W202610110124739` | **2c8g**（新流程） | 10-11 22:06 | **waiting >12h，容器未启动** | 0 |
| `W202610110124487` | 1c4Gi（旧流程） | 10-11 22:03 | waiting >12h | 0 |

### 8.2 卡点定位（关键证据）

- cromwell **已受理**：`Q4-2026-10-11T22-06-51`（124739）、`Q3-…22-06-50.97`（124487）
- attempt #1 已登记，**资源档已生效**（124739 = 8.00Gi / 124487 = 4.00Gi）
- 但 **attempt 开始时间为空、stdout/stderr 均为空** → **容器从未启动**
- 结论：卡在 **cromwell 向计算后端分配资源**环节；排队位置与原因在 CLI 层无字段可见

### 8.3 已排除的因素（勿重复排查）

1. **镜像**：`SATURN--22` = `public-library/zhongliyuan_00000000000000000000000000000000_public:latest`，10-04/10-05 跑过 13 个任务
2. **输入**：7 个输入全部存在且 SHA 核对通过
3. **流程定义**：`dcs app info` 状态 `checked`
4. **配置合法性**：非法配置会在提交/校验阶段报错，而非卡 waiting
5. **账号欠费/超配额**：历史任务均已结算或取消；三个 waiting 任务 0 计费
6. **资源档太小**：1c4Gi 与 2c8g 两档均 waiting

### 8.4 对照证据

- **10-04 全天**：13 个 WDL 任务全部被调度（失败也是运行后失败，计费 0.01–0.79 元）
- **10-05 00:45**：`W202610050003104`（同一镜像）**16 分 24 秒完成**，0.18 元
- **10-11 20:20 之后**：连续 3 个任务全部卡 waiting

→ 差异在**提交时段**，不在镜像/输入/流程。

### 8.5 重复投递发现（需用户确认）

`W202610110124487`（22:03、1c4Gi、旧流程）**不是本会话投递的**：其 `params_table.csv` mtime 22:02 被重写，`wfId` 为 22:05 流程更新**之前**的旧版本。与 `124739` 输入完全相同，相差 0.2 秒先后被 cromwell 受理。**未取消**（等用户确认来源）。

### 8.6 历史同类问题

2026-10-02 起，**个性分析离线任务（s 类）**曾长期卡 Pending：`2105712313899782145` / `2105967078722850818` / `2106397814268989442` / `2106401728586420226`，三档资源全部试过；工单 `TK20261003235804338` 已加急。本次是 **WDL 通道出现同样症状**。

### 8.7 已备工单

- `docs/execution/20261012-ticket-text-queue-stall.md`（3,928 B，可直接整段粘贴到工单系统）
- 另有一份更长的材料版：`docs/execution/20261011-ticket-material-queue-stall.md`

---

## 九、待决策事项（需用户/导师）

| # | 事项 | 阻塞方 | 处置建议 |
|---|---|---|---|
| 1 | **映射表 v1 导师签认** | 导师 | 唯一人工治理关口；AI 意见书已降维（`docs/mapping-v1-ai-review-opinion-20261005.md`）；邮件定稿 `docs/phase7-email-final-20261005.md` 已过 Claude 复核 |
| 2 | **提交平台工单** | 用户登录 | 正文已备；登录后可直接粘贴，或由执行者经浏览器提交 |
| 3 | `W202610110124487` 来源确认 | 用户 | 若非本组提交，可取消以避免被调度后计费（当前 0 计费） |
| 4 | 阶段 2 第二步通道选择 | 用户 | 选项：A 继续等（0 成本）/ B 换时段重投 / C 走工单。**执行者建议先 A + 提工单** |
| 5 | 是否开展 SATURN 重训（C2 的 SATURN 27 格） | 导师 + 用户 | 需另立方案与预算；当前源码级 blocked |
| 6 | C1/C2 付费审批 | 用户 | 审批单在 `docs/plans/three-tier-followup-20261009.md` |

---

## 十、恢复步骤（命令级）

### 10.1 任务被调度并完成后，回收与核对

```bash
# 1) 平台侧：打包 push 到 /Files/ResultData/Notebook/，再经 downloadFile API 拉回本地
#    产物预期落点：/work/user50719-8334/opca_v2/[taskId]/opca-full-<UTC>/

# 2) 本地核对（一条命令，6 方向×3 层 + 36 文件逐字节）
cd /d/projects/course5-prep
.venv39/Scripts/python.exe scripts/verify_dcs_recompute.py <回收目录>

# 3) 预期输出（全通过）
#    VERIFY|127/127|byte_identical=36/36     → exit 0
#    任一差异 → exit 4，并输出失败清单
```

### 10.2 隔离 wrapper 的复现命令（审阅人可自行验证）

```bash
.venv39/Scripts/python.exe scripts/ortholog_pca_full_isolated.py --dry-run   # 期望 PREFLIGHT|18/18 exit=0
.venv39/Scripts/python.exe scripts/run_samap_full_isolated.py --dry-run      # 期望 PREFLIGHT|20/20 exit=0
.venv39/Scripts/python.exe scripts/ortholog_pca_full_isolated.py --dry-run --out results/phase-20261010/A-smoke  # exit=3
.venv39/Scripts/python.exe scripts/ortholog_pca_full_isolated.py --dry-run --out results/pilot-v1/x              # exit=3
(cd results && ../.venv39/Scripts/python.exe ../scripts/ortholog_pca_full_isolated.py --dry-run --out pilot-v1/x) # exit=2
```

### 10.3 每阶段固定执行模板（来自总路线图）

```text
工作目录：D:\projects\course5-prep
本阶段目标：<阶段编号和一句话目标>
先读：现有总交接、上一阶段报告、当前阶段 manifest 和老师最新反馈。
执行规则：保留既有改动；不 reset、不覆盖冻结结果；新结果写新目录；不读取凭据。
本阶段只做：<明确的本阶段动作>
本阶段不做：<明确禁止动作>
完成后必须输出：做了什么、证据路径、通过/需修改/阻塞、费用/任务状态、下一阶段前置条件。
然后调用 Claude 做反方审阅，要求逐项给 PASS / REVISE / BLOCK，并引用文件和行号。
```

**Claude 调用方式**（以 `docs/execution/20261010-review-channel-check.md` 的"更正"一节为准）：

```bash
claude -p "<prompt>" --allowedTools "Read,Glob,Grep,Bash,PowerShell" --disallowedTools "Edit,Write,NotebookEdit"
# stdout/stderr 分开保存；不加 --model 覆盖
# 注意：stderr 的 unrecognized_model 是警告，不是失败；claude -p 退出码 0 即正常
```

---

## 十一、后续阶段路线（阶段 2–9）

| 阶段 | 内容 | 状态 | 关键前置 |
|---|---|---|---|
| 2 | A 档全量复算与负控（6 方向×3 层） | **进行中**（隔离层已完成；DCS 执行被阻塞） | 队列恢复 |
| 3 | GenPilot/DCS 平台事实核对（汇报 4） | not-started | 不越阶段 2 |
| 4 | 单细胞优先子集预检（汇报 5） | not-started | 角色表、条码命名空间、标签 NA 检查 |
| 5 | B 档最小 DCS smoke（汇报 6） | gated | **用户批准**；审批单 + ≤1 元上限 |
| 6 | C1 投影/隔离闸门（汇报 7） | gated | SATURN 源码级 blocked 已知 |
| 7 | C2 可行子集（汇报 8） | gated | **用户批准**；映射签认为硬前置；最多 54 格 |
| 8 | SATURN 独立方案（汇报 9） | **默认不执行** | 老师明确要求 + 双重批准 |
| 9 | 材料收口与等待老师反馈（汇报 10） | pending | 6 条收口条件 |

**进入"只等老师反馈"的 6 条条件**：① 所有已运行结果均有 manifest/命令/环境/输入输出 SHA/协议标签；② PPT/Word 主表与冻结数字逐格一致；③ transductive、SAMap-approx、SATURN blocked 限定语全部保留；④ 无未处理数字冲突/泄漏风险/费用异常/未说明缺口；⑤ 人工决策事项已列清单；⑥ 后续工作只剩老师评审。

---

## 十二、文档地图（读哪些）

### 必读（接手先读这 4 份）

| 文件 | 内容 |
|---|---|
| 本文件 | 全项目交接总览 |
| `docs/superpowers/plans/2026-10-10-course5-master-roadmap-flash.md` | 总路线图（阶段 0–9 细则 + 全局边界 + 每阶段模板） |
| `docs/execution/20261010-baseline.md` | 阶段 0 基线 + **覆盖风险清单** |
| `docs/execution/20261011-stage2-dcs-recompute-prep.md` | 阶段 2 全过程（21 节，含平台核对/任务提交/队列诊断） |

### 证据与状态

| 文件 | 内容 |
|---|---|
| `docs/evidence/status-matrix-20261008.md` | 状态矩阵 v1.1（26+6 项，A–E 分类） |
| `results/phase-20261010/review-gate-status.json` | 门状态（机器可读） |
| `results/phase-20261010/run_scope.json` | 本轮范围与停止条件 |
| `docs/final-evidence-matrix-20261005.md` | 三方法总证据矩阵 |
| `docs/errata-final-evidence-matrix-20261009.md` | 勘误（消融数字更正等） |

### 汇报材料

| 文件 | 内容 |
|---|---|
| `docs/reports/report-01..10-*.md` | 10 次汇报内容稿 |
| `results/stage-reports-20261009/index.md` | 阶段汇报总索引（含版式说明与校验记录） |
| `docs/reports/claude-review-03-to-10-r2-20261009.md` | 汇报 3–10 定向复核记录 |

### 方案与审批

| 文件 | 内容 |
|---|---|
| `docs/plans/three-tier-followup-20261009.md` | 三档方案 v2（含 C1 SATURN 源码级阻塞判定） |
| `docs/plans/inductive-pilot-manifest-v1.md` | inductive 81 格设计（未提交） |
| `docs/superpowers/plans/2026-10-08-course5-report-cycle-and-ppt-audit.md` | 汇报周期与 PPT 审计计划 |

### 审阅归档

| 文件 | 内容 |
|---|---|
| `docs/execution/20261011-stage2-review-archive.md` | 阶段 2 六轮 Claude + 一轮 GenPilot 审阅原文 |
| `docs/execution/20261010-master-roadmap-review.md` | 路线图审阅（含 A1/A2 阻塞项闭环） |
| `docs/execution/20261010-review-channel-check.md` | Claude 调用方式更正 |

---

## 十三、已知残留（不影响结论，但接手需知情）

| # | 项 | 说明 | 处置建议 |
|---|---|---|---|
| R1 | 审阅包 INDEX 计数与实际不符 | `results/phase-20261010/review-packet/INDEX.md` 声称"8 个 `.txt`"，实际目录为 **11 个 `.txt`**；其中 `ortholog_pca_dcs_v2.py.txt`（19:39 加入）与 `script-segments-meta.json`（19:42 加入）**未登记**。INDEX 已列的 9 行哈希**全部实测吻合** | **不改**（包已推送平台，改动会使本地与平台副本分叉）；下次重建包时一并补登 |
| R2 | 本文件与 §12 细节文档的时序 | 本文件为 2026-10-12 汇总；若后续任务完成或状态变化，以 `docs/execution/20261011-stage2-dcs-recompute-prep.md` §21 及后续新增记录为准 | 后续每次状态变化追加到该 prep 文档，不覆盖本文件 |
| R3 | `results/stage-reports-20261012/` 含两个渲染目录 | `render/` 与 `render-final-20261012/` 并存（前者为中间迭代） | 保留存档；以 `render-final-20261012/` 为准 |
| R4 | Word 交付物存在两个备份 | `deliverables/course5-final-report.bak-20261009.docx` / `.bak2-20261009.docx` | 保留；当前有效版为 `course5-final-report.docx`（`593d31e6…788f`） |

---

## 十四、边界声明

本文件生成于 2026-10-12，**全程只读**：

- 未运行任何模型运算（本地零计算）
- 未提交、未取消任何 DCS 任务；未加资源、未充值
- 未修改、删除或覆盖任何现有文件（本文件为**新增**）
- `results/pilot-v1` 与 `A-smoke` 零触碰
- 未读取、打印或保存任何凭据

**本文件中的数字来源**：§3/§6 全部取自冻结 `metrics.json`、`review-gate-status.json` 或本轮 `sha256sum` 实测；
§8 取自平台侧只读实查记录。若与细节文档冲突，以细节文档的原始记录为准。
