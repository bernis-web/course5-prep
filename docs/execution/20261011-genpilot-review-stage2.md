# GenPilot 独立审阅（阶段 2 隔离层，2026-10-11）

> 背景：本机 Claude 通道当时不可用（`otokapi.com` 中转 + 模型目录不匹配），按用户指示改用 GenPilot 作为**替代独立审阅人**。
> 性质：**替代通道审阅**，不等同于 Claude 复审；结论如实标注来源。
> 时间：提问 16:2x，结论 16:34（处理 3m4s）。

## 一、GenPilot 结论：BLOCK（理由是可达性，非发现缺陷）

原话要点：

> **可达性边界声明（必须先说明）**：审阅对象位于本地 `D:\projects\course5-prep`，容器 `/work`、`/work/Analysis`、`/Files` 中**均无任何副本**（已全量查找：无 `course5-prep` / `pilot-v1` / `A-smoke` / `review-gate-status` / `ortholog_pca_full_isolated.py` / `run_samap_full_isolated.py`，无 `6582d873` / `8da8c8e7` / `71dd08a3` 命中的 .py）。因此涉及本地文件的操作项无法"自己跑"，只能对平台侧可实查项给出实测证据；对不可达项按"不得采信自述"原则**不给 PASS**。

| # | 审阅项 | GenPilot 判定 | 理由 |
|---|---|---|---|
| 1 | 权威脚本字节未变 | BLOCK | 本地对象不可达；仅能实查线上 SAMap |
| 2 | 拒绝语义 dry-run | BLOCK（不可验证） | wrapper 不在容器，三个用例无法实跑 |
| 3 | 预检覆盖 / 先于 mkdir | BLOCK（不可验证） | 同上 |
| 4 | 补丁安全性 | BLOCK（不可验证） | 补丁 diff 不可达 |
| 5 | 产物契约 | REVISE | 线上 SAMap 四件成立；oPCA 六件的行号在线上版不存在 |
| 6 | 版本链对账 | **REVISE（发现真实错误）** | 见下 §二 |
| 7 | 越界检查 | 平台侧 PASS | 见下 §三 |

**结论 JSON（原文）**：
```json
{"stage2_isolation_review": "BLOCK", "must_fix": [
 "提供审阅对象可访问副本（上传 wrapper A/B、两份 docs/execution 报告、20261010-baseline.md、review-gate-status.json、pilot-v1 与 A-smoke 的 sha256 清单到 /Files 或容器 /work，否则 1/2/3/4 项不可验证）",
 "更正版本链哈希口径：线上权威 SHA256=f7f21ff4…（410行），56bb6035 是 MD5 非 SHA256；并说明本地 6582d873（≥352行）与线上 oPCA 156 行（56480c06）的版本分支关系",
 "补交 wrapper dry-run 三个拒绝用例的独立运行记录（非零退出码+stderr）与 A/B 预检项清单",
 "确认并记录本地 437 行 8da8c8e7 / 451 行 71dd08a3 与线上 f7f21ff4/c0f05b89 的版本拓扑，报告中不得混用 MD5/SHA256 前缀"]}
```

## 二、它纠正的**真实错误**（已修正）

**`56bb6035` 是 MD5，不是 SHA-256。**

- 我在 `20261011-genpilot-consultation-stage2-isolation.md` 初版写成"sha256 = 56bb6035e2…"——**错**。
- 既有记录本就用 MD5：`docs/phase6-closure-20261005.md:19,38`（"脚本 md5 56bb6035"）、`docs/final-evidence-matrix-20261005.md:52,56`（"脚本 md5 56bb6035 版"）。
- GenPilot 实测：线上 410 行版 **SHA-256 = `f7f21ff4…`**；sed 链后部署版 **SHA-256 = `c0f05b89…`**（= `W202610050003104` manifest 的 script_sha256）。
- **已修正**：会商记录与阶段报告均改为"md5 `56bb6035` / sha256 `f7f21ff4…`（410 行）→ sed → sha256 `c0f05b89…`"，并显式加注"两者是不同算法，不得混用或互相替代"。

**三方版本拓扑（已写入报告）**：
```
线上权威  410 行  md5 56bb6035 / sha256 f7f21ff4  ← 可从 /Files/ResultData/Notebook/run_samap_compliant_v98_dcs.txt 回捞
   └─ sed(/data/work→. , mo→ms) → 部署版 sha256 c0f05b89（= W202610050003104 manifest 记录值）
本地变体A 437 行  sha256 8da8c8e7  ← wrapper B 的源（本阶段隔离对象）
本地变体B 450 行  sha256 71dd08a3  ← run_samap_compliant_v98_dcs.py（DCS 变体）
```

它另指出一条**待澄清项**（未作为 must_fix，但值得记录）：线上 oPCA 脚本 `ortholog_pca_v98_final.py` 仅 **156 行**（sha256 `56480c06…`），而本地权威 `ortholog_pca_local_v1.py` 为更长版本（≥352 行，sha256 `6582d873…`）——**两者是不同的脚本**，不是同一文件的两个版本；本地冻结数字由后者产出（manifest 的 `script_sha256` 指向它），此关系已在基线文档与本次报告中冻结，但两者的"分支关系"未在早期文档说明。

## 三、它完成的**平台侧独立核查（PASS，有实证价值）**

- `dcs task ls`：本用户最近任务为 **`W202610050003104`（10-05 完成）**；**10-05 之后无任何新 DCS/WDL 提交** ✓
- 10-10/10-11 的 8 个 offline-task-logs 全部属于**另一用户** `user73591-6547` 的 OrthoFinder 任务（pair01–pair09），与本课题无关 ✓
- 容器内**无**新建 `A-full*` / `pilot-v1` 目录、无新镜像构建 ✓
- 不可实查：本地 Windows 是否跑过全量/GPU/充值（本地盘不可达，如实标注）

→ 这条是**独立第三方对"本阶段未提交任何平台任务"的实测确认**，价值独立于本地自述。

## 四、未闭环项与下一步

| 项 | 状态 |
|---|---|
| 本地对象审阅（1/2/3/4 项） | **未完成**——需把审阅包推送到平台（已备 `results/phase-20261010/review-packet/`，8 个 `.txt` 审阅对象 + 索引（共 10 个文件），无凭据/无冻结数据），**待用户批准推送** |
| 哈希口径错误 | **已修正**（会商记录 + 阶段报告） |
| 版本拓扑 | **已锁定并写入报告** |
| 本地 dry-run 证据 | 已生成 `dry-run-evidence.txt`（2 正例 exit 0；10 负例 exit 2/3，真实退出码） |
| Claude 通道 | 用户已恢复；`deepseek-v4.1-flash` 实测可用，第二轮复审正在运行 |

**边界声明**：GenPilot 的建议**不替代**本地 metrics/日志/源码证据与导师签认；本记录不改变任何实验口径、不启动任何任务。
