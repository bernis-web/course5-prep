# 阶段 2 第一步报告：A 档全量复算输出隔离层（2026-10-11）

> 范围：**只做隔离与预检，不跑全量复算**。不提交 DCS、不调用 GenPilot 提交、不训练、不启动 GPU、不充值。
> 前置：阶段 0/1 已 PASS（`results/phase-20261010/review-gate-status.json`：status=passed / task1=completed / task2=not_started）。

## 1. 阶段 1 只读复核（未重跑、未新建 A-smoke）

| 项 | 结果 |
|---|---|
| gate 状态 | `status=passed`、`task1=completed`、`task2=not_started`、dcs/training/gpu/recharge 全 false ✓ |
| A-smoke 文件数 | **13**（与阶段 1 报告一致）✓ |
| verification.json | **16/16 ok=true**、`failed_checks: []`、status=PASS ✓ |
| predictions/confusion 与冻结逐字节相同 | `dc729820…`（1535 行预测表）与 `167da767…`（28 条混淆）✓ |
| 冻结 metrics SHA | `b2b3ac6b…c725` 未变 ✓ |
| `results/pilot-v1` 零触碰 | mtime 晚于 `2026-10-10T11:04:48` 的文件数 = **0** ✓ |

## 2. 隔离层实现（两个 wrapper，权威脚本字节不变）

| 项 | wrapper A | wrapper B |
|---|---|---|
| 目标脚本 | `scripts/ortholog_pca_local_v1.py` | `scripts/run_samap_compliant_v98.py` |
| 权威脚本 SHA-256 | `6582d873…0c44`（= 冻结 manifest 的 script_sha256）✓ 未变 | `8da8c8e7…`（本地 437 行变体）✓ 未变 |
| 新增文件 | `scripts/ortholog_pca_full_isolated.py` | `scripts/run_samap_full_isolated.py` |
| 新文件 SHA-256 | `48d79ad1c41d85ac3a68d806ec771e3dca7c8d927f4a27dc608ec8bb81bee83c` | `6f1385cd12d464fc43d392d8fc04a7efaeb5b5854e0d14854773c6963cfe26fa` |
| 补丁 | PA main-header（out→OUT_DIR）、PB base-scope（BASE 钉仓库根） | PB base-scope、PC main-root+output-dir（→OUT_DIR + 断言预建） |
| 隔离机制 | 读源码→补丁（每锚点恰好匹配 1 次）→补丁源码落盘输出目录→执行（Task 1 同模式） | 同左 |
| 输出目录 | `results/phase-20261010/A-full-<UTC时间戳>/`（或 `--out`） | `results/phase-20261010/A-full-samap-<UTC时间戳>/`（或 `--out`） |

### 安全边界（已实测）

| 负例 | 命令 | 结果 |
|---|---|---|
| 目标目录已存在（非空 A-smoke） | `--dry-run --out results/phase-20261010/A-smoke`（A/B 两 wrapper） | **exit 3**，`refusing to overwrite` ✓ |
| 目标解析落在 `results/pilot-v1` 内 | `--dry-run --out results/pilot-v1/A-full-test`（A/B 两 wrapper） | **exit 3**，`resolves inside results/pilot-v1` ✓ |

其他边界：权威脚本 SHA 不符 → exit 2；锚点匹配 ≠1 次 → exit 2；预检失败 → exit 2 且不建目录；输出落在仓库外 → exit 3。

## 3. dry-run 预检（不执行模型、不创建输出目录）

| wrapper | 检查项 | 结果 | 退出码 |
|---|---|---|---|
| A（oPCA 全量） | 18 项：源码 SHA / 补丁 / 补丁源码 exec / BASE=仓库根 / ortholog 目录+3 文件 / 映射表 / 3 份 h5ad / LEVELS=(exact,coarse,fine) / NPERM_FULL=200 / 六方向 MAPS 块完整 / 输出目录不存在 / 不在 pilot-v1 / 在仓库内 | **18/18 PASS** | 0 |
| B（SAMap 全量） | 20 项：源码 SHA（**完整 64 位比较**）/ 补丁 / exec / BASE / ortholog 目录 + 3 个直系同源文件 / 3 物种 h5ad / TRUTH_COLUMN=cell_type / LEVELS / NPERM=200 / DIRECTIONS=6 / 映射表 / 输出路径三项 | **20/20 PASS** | 0 |

dry-run 后复核：`results/phase-20261010/` 下**无 A-full\* 目录**（`A-full*: []`）✓；A-smoke 仍 13 文件、两个关键 SHA 未变 ✓。

## 4. 产物契约（正式运行时会写入输出目录）

**按脚本分别列（外部审阅第 1 轮指出：两脚本原生产物不同，不可合并写）**：

| 产物 | oPCA 源码原生 | SAMap 源码原生 | wrapper 追加 |
|---|---|---|---|
| `manifest.json` | ✓ | ✓ | — |
| `metrics.json` | ✓ | ✓ | — |
| `predictions/`（逐细胞） | ✓（18 格） | ✓（18 格） | — |
| `confusion/` | ✓（18 格） | ✓（18 格） | — |
| `command.txt` | ✓ | ✗（源码不产） | **B 由 wrapper 补写** |
| `environment.json` | ✓ | ✗（源码不产） | — |
| `environment.txt` | ✗ | ✗ | ✓（A/B 都写） |
| `sha256.tsv` | ✗ | ✗ | ✓（A/B 都写，rglob 递归含子目录） |
| `_patched_source.py` | ✗ | ✗ | ✓ |
| `wrapper-provenance.json` | ✗ | ✗ | ✓ |

依据：`scripts/ortholog_pca_local_v1.py:310,312,324,325,330,352`（六件）；`scripts/run_samap_compliant_v98.py:403,404,405,408,414,430`（四件）。
隔离 provenance 四要素：**脚本 SHA**（权威 + 补丁后）/ **补丁**（完整 diff）/ **输入 SHA**（脚本原生 manifest 记录）/ **输出 SHA**（sha256.tsv）。

## 5. 与 GenPilot 会商的接口结论（详见 20261011-genpilot-consultation-stage2-isolation.md）

- WDL command 段可做 `[ -e ] && exit 1` 硬拒绝；平台无"自动清理/自动重投同目录"约定（cromwell MaxRetries=0）→ 本地隔离语义与平台一致；
- 平台回收约定：`/work/{user}/<任务目录>/` → tar.gz → `dcs data push` → `/Files/ResultData/Notebook/`；
- **版本口径（含算法口径更正）**：本地 `run_samap_compliant_v98.py`（437 行，sha256 `8da8c8e7…`）**不是**线上权威；线上权威 = 410 行版（**md5 `56bb6035` / sha256 `f7f21ff4…`**）+ 两处 sed → 部署版 sha256 `c0f05b89…`，可从 `/Files/ResultData/Notebook/run_samap_compliant_v98_dcs.txt` 回捞。
  另：本地还有 450 行变体 `run_samap_compliant_v98_dcs.py`（sha256 `71dd08a3…`）。**算法口径**：`56bb6035` 是 MD5、`c0f05b89`/`f7f21ff4` 是 SHA-256，两者不可混用（本报告初版误标，已更正，见会商记录）。
  wrapper B 的 environment.txt 已记录该差异（`source_variant_note`）。阶段 5 若做同协议复算应以 410 行版为源。

## 6. 边界与未做项

- **未跑全量复算**（不执行 6 方向 × 3 层级；不执行 SAMap 任何计算）。
- 未修改/删除/覆盖 `results/pilot-v1` 任何文件；未修改两个权威脚本（SHA 实测未变）。
- 未新建第二个 `A-smoke/`；未提交 DCS；未训练；未启动 GPU；未充值；未读取任何凭据。
- wrapper B 的正式运行需要 samap/samalg 依赖栈（阶段 5 范畴），本阶段只做 dry-run。

## 7. 通过 / 需修改 / 阻塞

- 阶段 1 只读复核：**通过**。
- 隔离层（A/B 两 wrapper + 4 个拒绝负例 + 2 个 dry-run）：**通过**（本阶段范围内）。
- 阻塞项：无。
- 待外部审阅（Claude 反方）确认后方可标记"隔离层 PASS"。

## 7.0 本轮修订后的 SHA 与状态

| 文件 | 修订后 SHA-256 |
|---|---|
| `scripts/ortholog_pca_full_isolated.py` (wrapper A) | `48d79ad1c41d85ac3a68d806ec771e3dca7c8d927f4a27dc608ec8bb81bee83c` |
| `scripts/run_samap_full_isolated.py` (wrapper B) | `6f1385cd12d464fc43d392d8fc04a7efaeb5b5854e0d14854773c6963cfe26fa` |
| 权威 `scripts/ortholog_pca_local_v1.py` | `6582d873…0c44`（**未变**） |
| 权威 `scripts/run_samap_compliant_v98.py` | `8da8c8e7…`（**未变**） |

> 上表两个 wrapper SHA 由 `sha256sum` 实测写入。

## 7.1 外部审阅第 1 轮（Claude 反方，2026-10-11）

`verdict: REVISE`（无 BLOCK）。审阅人独立重算/复跑并发现 5 项，全部已修：

| # | 问题 | 修正 |
|---|---|---|
| 1 | **实质缺口**：`guard_output` 校验 `(BASE/out).resolve()`，而 `run()/mkdir` 用 cwd 相对路径 → 从 `cwd=results` 传 `--out pilot-v1/x` 时守卫放行、正式运行会写进冻结区 | 入口强制 `cwd == BASE`（否则 exit 2）并把 `--out` 一律 `.resolve()` 后校验与建目录；已实测非仓库根调用 exit 2 |
| 2 | wrapper B 只比 16 位 SHA 前缀，docstring 却称"不等于即 exit 2" | 改为完整 64 位比较（`8da8c8e7221aeac5e3915cc233931aced86f83ba60fd4bb0ac289d5ccbe8e4a7`），死变量已删 |
| 3 | wrapper B preflight 未覆盖 ortholog 目录与 3 个直系同源文件（源码 :280/:306/:312 实际读取） | 已补 4 项检查；B 从 16/16 升为 **20/20** |
| 4 | 报告 §4 把两脚本原生产物合并写成六件（SAMap 只产四件） | 已改为按脚本分别列契约（见 §4 表） |
| 5 | 版本链未对账：会商记本地 checked-in 为 `71dd08a3`，磁盘 `run_samap_compliant_v98.py` 实为 `8da8c8e7` | **已查清**：`71dd08a3` 是**另一个文件** `scripts/run_samap_compliant_v98_dcs.py`（450 行，DCS 变体），非本 wrapper 的源；行数口径 `wc -l`=437 / `split`=438 已统一为 437 |

审阅同时确认（PASS 项）：权威脚本字节未变、A-smoke 与 pilot-v1 零触碰、4 个拒绝负例复现、dry-run 不建目录、补丁只改输出路径与 BASE 作用域、越界检查通过。

## 7.2 审阅轮次台账（最终状态：5 轮，全部闭环）

| 轮 | 审阅人/通道 | 时间 | 判定 | 提出项 | 处置 |
|---|---|---|---|---|---|
| 1 | Claude（`claude -p`，当时通道异常前） | 2026-10-11 | **REVISE** | 5 项（含 1 项**实质缺口**：CWD 可绕过冻结守卫） | 全部修正（见 §7.1） |
| （—） | 通道中断 | 2026-10-11 下午 | exit=1（模型/代理不可用） | — | 如实记录 `20261011-review-channel-check.md`；**未**改 `--model`、**未**伪造结论 |
| 1′ | **GenPilot**（替代审阅人） | 2026-10-11 16:34 | **BLOCK**（因本地对象在容器不可达） | 4 项（含纠正 MD5/SHA256 口径）+ 平台侧越界实测 PASS | 哈希口径已更正；审阅包已备（待批准推送）；见 `20261011-genpilot-review-stage2.md` |
| 2 | Claude（通道恢复，`--model deepseek-v4.1-flash`） | 2026-10-11 17:0x | **REVISE** | 3 项（文本准确性：完整 SHA 后缀、§3 的 16→20 项、`451`→`450` 行） | 全部修正 |
| 3 | Claude | 2026-10-11 17:12–17:20 | **REVISE** | 3 项（§2 过期 SHA、`438 行`残留、INDEX 漏登主报告行） | 全部修正 + 连带重算哈希 |
| 4 | Claude | 2026-10-11 17:2x | **REVISE** | 4 项（同类"改源未连带重算"：`source_variant_note`、§2 行数、genpilot 记录文件计数、INDEX 说明占位） | 全部修正 + 统一重算 |
| 5 | Claude | 2026-10-11 17:4x | **REVISE**（a–e 五项 PASS，仅文档记录未收口） | 2 项（§7.2 状态过期、INDEX 描述不符） | **本表已补，§7.2 已更正** |
| 6 | Claude | 2026-10-11 18:0x | **PASS**（must_fix: []） | 0 项（第 5 轮 2 项已复核确认；a–e 及回归六类全 PASS） | 收口通过；全链归档 `20261011-stage2-review-archive.md` |

**当前状态**：隔离层已建成并通过外部审阅收口；6 轮 Claude + 1 轮 GenPilot 替代审阅共 17 项全部闭环（1 项实质缺口 + 16 项文本/清单准确性）；
最新一次独立复核（第 5 轮）对 **a–e 五项（包完整性、残留串、SHA 三处一致、实跑隔离语义、回归）全部 PASS**。
**Task 2（全量复算）仍未放行**——按本阶段边界，需用户明确放行后才执行。

## 8. 下一阶段前置条件

1. 本报告 + 会商记录经 Claude 反方审阅 PASS；
2. 全量复算（Task 2）另经用户放行后才执行（本阶段未获此放行）；
3. 阶段 5 提交 DCS 前：按审批单（任务名/镜像/资源档/费用上限/输入 SHA/停止条件）+ 用户明确批准；SAMap 以 410 行权威版为源。
