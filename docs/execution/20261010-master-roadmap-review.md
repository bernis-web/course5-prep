# 总路线图审阅（2026-10-10）

审阅对象：`docs/superpowers/plans/2026-10-10-course5-master-roadmap-flash.md`（189 行）
审阅性质：只读核对，逐条与仓库现状、已完成证据、冻结口径比对。未修改任何文件。

---

## 结论摘要

路线图的结构、边界和口径**方向正确**，可直接作为 Flash 的总纲。但它是在阶段 0/1 完成**之前**写的，**当前状态已过期**，且漏掉了一条会造成不可逆破坏的前置条件。

`verdict: REVISE` —— 两条阻塞级问题 + 七条需修改，改完即可交 Flash。全部为文本改动，不涉及任何实验。

---

## 阻塞级问题

### A1 · "当前交接点"过期，会驱动 Flash 重跑已完成的阶段 1

`master-roadmap-flash.md:188`：

> 当前仍处于阶段 0 已基本冻结、阶段 1 smoke 尚未正式运行的状态。下一步交给 Flash：先执行阶段 1 的单方向零成本 smoke

事实：

- `results/phase-20261010/review-gate-status.json` 现为 `status=passed`、`task1=completed`、`observed_at=2026-10-10T16:58:03+08:00`。
- 阶段 1 已执行完毕：`results/phase-20261010/A-smoke/` 13 个文件，`verification.json` 16/16 通过，混淆矩阵与逐细胞预测表与冻结产物**逐字节相同**，报告 `docs/execution/20261010-task1-a-smoke-report.md` 已过外部审阅 3 轮（最终 PASS）。
- 同一份路线图 `:29` 又要求 Flash 先读 `review-gate-status.json` —— 于是路线图**自相矛盾**：文件说阶段 1 完成，`:188` 说要先做阶段 1。

按现文执行的后果：Flash 会重跑 smoke，并因 `:46` 指定的目录名与现有目录不同，产出**第二个分叉的 A-smoke 目录**，污染证据链；若 Flash 改用已验证的 wrapper，则会撞上"输出目录非空即退 3"的守卫，可能触发对已审阅产物的删除。

**要求**：把 `:188` 的交接点改为"阶段 0、阶段 1 均已完成并通过外部审阅；下一步从阶段 2 开始，且需先满足 A2 的前置条件"，并在路线图开头加一张阶段状态表（已完成 / 进行中 / 未开始）。

### A2 · 阶段 2 缺"覆盖冻结目录"的前置条件（最高危）

`:59-61` 要求阶段 2 做"6 个方向 × exact/coarse/fine 的统一复算"，但**没有**写出本项目已确认的覆盖风险：

- `scripts/ortholog_pca_local_v1.py:158` —— 全量模式 `out = results/pilot-v1/ortholog-pca-v98`，**只有 `--smoke` 分支带存在性守卫（`:159-160`）**。不带参数直接运行会静默覆盖冻结的 `manifest.json`、`metrics.json`、18 份 predictions 和 18 份 confusion。
- `scripts/run_samap_compliant_v98.py:249-250` —— `output_dir = results/pilot-v1/samap-v98` + `mkdir(parents=True, exist_ok=True)`，无守卫。

这条已写入 `docs/execution/20261010-baseline.md` 的"覆盖风险"一节，但**没有进入总路线图**。Flash 只读路线图，会在阶段 2 直接跑全量模式，**一次误跑就摧毁整条证据链所依赖的冻结基线**，且不可逆。

**要求**：在阶段 2 的 Flash 执行清单里加一条硬前置：*"运行全量复算前，必须先用 `--out` 参数或等价隔离副本把输出重定向到新目录，并要求目标目录已存在时硬停止；在满足该条件前不得运行上述脚本的全量模式。"* 并指向 `20261010-baseline.md` 的"覆盖风险"一节。

---

## 需修改

| 编号 | 位置 | 问题 | 要求 |
|---|---|---|---|
| B1 | `:46` | 产物目录写作 `results/phase-20261010/A-smoke-<timestamp>/`，与实际 `results/phase-20261010/A-smoke/` 不符 | 改为实际目录名；若确需支持重跑，写明"已存在且非空则拒绝覆盖，改用新的 `<timestamp>` 目录"，并禁止删除既有 A-smoke |
| B2 | `:43-47` | 阶段 1 未引用已验证的隔离 wrapper | 指向 `scripts/ortholog_pca_task1_isolated.py`（sha256 `71ab5642…`）与 `docs/execution/20261010-task1-preflight.md`，避免 Flash 从零重写并重踩 C1/F1 两类缺陷 |
| B3 | `:7` | "Flash 每个阶段自行邀请 Claude 做反方审阅"未给调用方式；项目自己曾把 Claude 误判为不可用 | 指向 `docs/execution/20261010-review-channel-check.md` 的"更正"一节：`claude -p "<prompt>" --allowedTools "Read,Glob,Grep,Bash,PowerShell" --disallowedTools "Edit,Write,NotebookEdit"`，stdout/stderr 分开重定向，**不加** `--model` 覆盖 |
| B4 | `:1`、`:29` | 与 `2026-10-10-course5-genpilot-dcs-longrun.md` 并存两套编号（Task 0–9 vs 阶段 0–9），未说明谁优先 | 加一句"本路线图为总纲，`2026-10-10-course5-genpilot-dcs-longrun.md` 为阶段细则；冲突时以本文件为准" |
| B5 | `:13` | 标签集合只列 `confirmed`/`candidate`/`blocked`/`design-not-run` | 补 `confirmed-for-recompute`（阶段 1 的结论用的就是这个复算级标签，且它是"不升级为泛化"的关键限定） |
| B6 | `:59` | 只说"仅使用真实存在的 predictions/confusion"，未提示 SATURN 的实际缺口 | 补：SATURN v99 recovered 本地只有 6 个 coarse payload（`exact`/`fine` 只有 confusion），**无法**做 exact/fine 逐细胞复算；若阶段 2 要纳入 SATURN，需先补数据 |
| B7 | `:160` | 要求把老师反馈归档到 `docs/teacher-feedback/`，但该目录**不存在** | 补"若不存在则创建" |

另有一条建议（非必须）：`:16` 的 oPCA 口径可补上项目已冻结的措辞——"label-free 只适用于表示层；v98 的 PCA 在 src+tgt 联合矩阵上拟合，是 transductive 投影，不得写成 inductive"（见 `20261010-baseline.md:31`）。

---

## 核对通过的部分

- `:11-19` 全局边界与 `20261010-baseline.md` 的冻结口径一致，包括 `:16` 已正确写成"SATURN 的**默认**训练标签通道写作 `labels`"（这正是外部审阅 C3 要求收窄后的表述）、`:17` 的 54 格上限。
- `:5` 目标、`:13` 禁止伪造逐细胞证据、`:14` transductive 限定、`:18` 禁用"显著优于"——均与既有口径一致。
- `:99` 阶段 5 的启动前必须具备项（审批单、≤1 元上限、用户明确批准）完整。
- `:105` "只做一次绑定状态检查"、`:19` 的失败即停不重试，与交接单一致。
- `:131-134` 阶段 7 的 1 折×1 seed → 3 折×3 seed、最多 54 格、逐 seed 全报不择优、标题注明"跨物种级、非跨供体级"——与既有计划一致。
- `:163-170` "只等老师反馈"的 6 条条件可核查。
- `:172-184` 每阶段固定模板可用。
- 路线图引用的 13 个文件路径全部存在（仅 `docs/teacher-feedback/` 例外，见 B7）。

---

## 结论（针对修订前的初版）

`verdict: REVISE`

改掉 A1、A2 两条阻塞项，再按 B1–B7 补齐，即可交 Flash。**A1 是"防止重跑已完成阶段"，A2 是"防止摧毁冻结基线"——这两条不改，不建议交付执行。**

> 注：本节及以上引用的行号针对**修订前**的初版（189 行）。以下复审小节的行号针对修订版（207 行）。

---

## 复审（2026-10-11，修订后核验）

修订版共 207 行。逐项核验：

| 项 | 位置 | 判定 |
|---|---|---|
| A1 交接点 | `:11-20` 新增阶段状态表；`:52` 标题标"已完成"；`:54` 禁止重跑；`:58-60` 改为只读复核 + 受控重跑；`:206` 交接点更新 | **已修** |
| A2 覆盖闸门 | `:73-75` 先读"覆盖风险"、必须重定向到 `A-full-<timestamp>/`、第一步硬拒绝已存在/非空目标、不得改动 `pilot-v1`、无法证明隔离则停止 | **已修**（表述完整） |
| B1 目录名 | `:59` 禁止新建第二个默认 `A-smoke/`；`:74` 改用 `A-full-<timestamp>/` | 已修 |
| B2 wrapper | `:60` 引用 `scripts/ortholog_pca_task1_isolated.py`，SHA-256 与磁盘实测 `71ab5642…7002ed` **逐字符一致** | 已修 |
| B3 Claude 调用 | `:7` 完整写出 `claude -p` 调用、stdout/stderr 分开、不加 `--model` | 已修 |
| B4 计划层级 | `:9` 新增"计划层级"段，明确本文件为总纲 | 已修 |
| B5 标签 | `:26` 补入 `confirmed-for-recompute` | 已修（`:176` 仍只列 4 个，见 N1） |
| B6 SATURN 缺口 | `:77` 明确只有 6 个 coarse payload，exact/fine 不得纳入逐细胞复算 | 已修 |
| B7 teacher-feedback | `:178` 补"首次归档前先创建（若不存在）" | 已修 |

修订未引入实验动作。19 小时后独立复核：HEAD 未变（`8b597d78…`）；`results/pilot-v1` 零触碰；`A-smoke/` 仍 13 个文件；无 `A-smoke-<ts>/`、无 `A-full-<ts>/`；门状态仍 `status=passed / task1=completed / task2=not_started`；冻结 metrics SHA 未变。该时段内唯一被写入的文件是路线图本身（10-10 17:14）。

### N0（阻塞，修订新引入的错误）· `:74` 断言 `--out` "已实现"，与事实和本文件 `:206` 都矛盾

`:74`：

> 必须先用**已实现的** `--out` 参数或等价隔离副本……

实测：

- `scripts/ortholog_pca_local_v1.py` 的 argparse **只有** `--smoke`（`:153-154`），**没有** `--out`。
- `scripts/run_samap_compliant_v98.py` **完全没有 argparse**，`:249` 把 `output_dir` 硬编码为 `root/"results"/"pilot-v1"/"samap-v98"`。
- 全仓 `scripts/*.py` 中唯一实现 `--out` 的是 `scripts/ortholog_pca_task1_isolated.py:377`——那是阶段 1 的 wrapper，不是全量脚本。

且本文件 `:206` 自己写的是"阶段 2 **必须先关闭**……**并建立**隔离输出"，与 `:74` 的"已实现"直接冲突。

危害：Flash 按 `:74` 会以为隔离能力已就绪。试 `python scripts/ortholog_pca_local_v1.py --out …` 会得到 argparse 报错；若它据此误判"该脚本不支持隔离"而直接跑全量模式，就会**覆盖冻结基线**——正是 A2 要关掉的那个风险。

**要求**：`:74` 改为"必须**先实现** `--out` 参数或建立等价隔离副本（当前两个全量脚本均无此参数）"。

### N1（非阻塞）· `:176` 标签集合不完整

`:26` 已补入 `confirmed-for-recompute`，但 `:176` 仍写"区分 confirmed、candidate、blocked、design-not-run"四个。建议同步为五个，避免阶段 9 材料收口漏掉复算级标签。

---

## 复审结论

`verdict: REVISE`（仅剩 N0 一条阻塞）

N0 一处措辞即可修正，但它守的正是 A2 那道闸门，**改掉再交 Flash**。N1 可同期顺手补。

---

## 收口（2026-10-11 12:17）

N0、N1 已按要求修正：

- `:74` 改为"必须**先实现** `--out` 参数或建立等价隔离副本（当前 `scripts/ortholog_pca_local_v1.py` 只有 `--smoke`，`scripts/run_samap_compliant_v98.py` 无 argparse 且硬编码输出路径，两个全量脚本均无此参数）"。全文已无"已实现"类断言。
- `:176` 补入 `confirmed-for-recompute`，与 `:26` 的五个标签一致。

修正后复核：HEAD 未变；`results/pilot-v1` 零触碰；`A-smoke/` 仍 13 个文件；无 `A-smoke-<ts>/` 或 `A-full-<ts>/`；冻结 metrics SHA 未变；门状态 `task1=completed / task2=not_started`。当日仅路线图与本审阅记录被写入，未启动任何实验、DCS、训练或充值。

`verdict: PASS` —— 可交 Flash 执行。首个动作是阶段 2 的前置工作：为两个全量脚本实现 `--out` 或等价隔离副本，并加"目标目录已存在/非空即硬拒绝"守卫；在该前置完成前不得运行全量模式。
