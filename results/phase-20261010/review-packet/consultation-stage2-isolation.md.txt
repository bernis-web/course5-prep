# GenPilot 会商记录 · 阶段 2 隔离层（2026-10-11）

> 方式：DCS Cloud → Genpilot（项目 P20260920085640327），会话"我们课程项目"。提问 12:3x，答复 12:40（约 7 分钟，8 步平台实查）。
> 纪律：原答复要点照录；平台侧证据标注位置；**不替代本地 metrics/日志/源码**。

## 提问（要点）

阶段 2 隔离层需要平台侧确认四点：①WDL command 段能否实现"目标目录已存在即失败"的硬拒绝、平台有无冲突约定；②后续 DCS 跑 SAMap 的输出回收位置；③本地冻结 SAMap 数字来自 WDL 部署脚本（c0f05b89），与仓库 checked-in 版（71dd08a3）不同——同协议复算应以哪个为权威、能否回捞；④隔离层产物在平台侧的路径/权限注意事项。

## 答复（照录要点）

### ① 硬拒绝语义：**可行**，平台无冲突约定
- `[ -e dir ] && exit 1` 是普通 bash 语句，WDL command 段就是 shell 脚本，直接写。
- 平台侧**无"自动清理旧输出/自动重试同目录"约定**。证据：本轮 SAMap 连续 10 次失败（W202610040066785 → W202610050003104），每次回传提示"系统将自动排查失败原因并尝试重新投递"，但**实际重投均由 Agent 手动 fill+submit**；每次 `cromwell_id`/`shadow_work_dir` 全新（Q3-…/Q2-… 递增）；cromwell 默认 `MaxRetries=0`（我们 WDL runtime 未设置该属性）。
- 即：WDL 每次 attempt 都在干净工作目录执行，输入靠 cp 注入；"目标目录已存在即失败"不会因重试误触发。唯一要防的是脚本内部 `mkdir(exist_ok=True)` 覆盖旧输出——**隔离层必须在 mkdir 之前做 `[ -e "$OUT" ] && exit 1`，预检先于建目录**。

### ② 输出回收位置：`/Files/ResultData/Notebook/` 是已验证约定目录
- 证据：`samap_result.tar.gz`（id `0e3741b17b25439e98243f821b1c8cc3`）等多次 push 均成功到该目录；/Files 下另有 RawData/ResultData/ManualData/ReferenceData 顶层，ResultData 下 Workflow（空）与 Notebook（实际使用区）。
- 约束：`dcs data push` 只接受 `/work/{user}/` 下源文件、**目标目录必须已存在**、**不支持 .py 扩展名**（需 .txt）、**文件名含 `>` 会被跳过**（历史踩坑：`coarse_mouse->human.json` 曾因此失败）。
- 建议：WDL `output_path` 落在 `/work/{user}/<任务目录>/`，跑完打包 tar.gz 再 push 到 `/Files/ResultData/Notebook/`。

### ③ 同协议复算的权威脚本：**410 行权威版（56bb6035…）为权威，线上可完整回捞**
证据链（GenPilot 已实测验证）：
- `/Files/ResultData/Notebook/run_samap_compliant_v98_dcs.txt` 与 online 树 `run_samap_compliant_v98_dcs.py` 为同一文件；
  其 **md5 = `56bb6035e2…`**（注意：**不是 sha256**——既有记录 `docs/phase6-closure-20261005.md:19,38`、`docs/final-evidence-matrix-20261005.md:52,56` 均写"脚本 md5 56bb6035"）；
- WDL 部署版 `samap_script.py`（manifest 记录 `c0f05b89653e…`）= 上述文件经两处 sed（`/data/work→.`、`mo→ms`）后的结果——**在容器里复现了这条 sed 链并精确命中**。
  **算法口径更正（GenPilot 独立审阅第 1 轮指出，2026-10-11）**：`56bb6035` 是 **MD5**（32 hex），`c0f05b89` 是 **SHA-256**（64 hex）；线上 410 行版的 **SHA-256 = `f7f21ff4…`**。两者是不同算法，**不得混用或互相替代**（本记录初版曾把 md5 前缀当 sha256 写，已更正）；
- 用户消息中的 `71dd08a3` 在容器 `/work` 与 `/work/Analysis` 全量 sha256 扫描**均不存在**，平台侧无法回捞；
  **本地更正（2026-10-11，外部审阅第 1 轮要求对账）**：`71dd08a3` 其实是**另一个本地文件** `scripts/run_samap_compliant_v98_dcs.py`（450 行，DCS 变体）的 SHA-256；本阶段 wrapper B 的源是 `scripts/run_samap_compliant_v98.py`（437 行，sha256 `8da8c8e7…`）。两者均**不是**线上权威版（线上权威 = 410 行 `56bb6035` + 两处 sed = `c0f05b89`）。
- 注意区分：`/work/user50719-8334/samap_script.py`（449 行，sha256 `0a2063d3…` = `/Files/ResultData/Notebook/samap_script.txt` 旧变体）是早期调试版本，`output_dir` 硬编码 `/data/work/course5_samap_v98`，不是部署权威。
- **结论**：若"同协议复算"对标线上产物（W202610050003104），权威 = 410 行版（sha256 `f7f21ff4…`；md5 `56bb6035`）+ 固定 sed 链（→ sha256 `c0f05b89…`）；
  若要对标本地仓库逻辑，本地有两份变体：`run_samap_compliant_v98.py`（437 行，sha256 `8da8c8e7…`）与 `run_samap_compliant_v98_dcs.py`（450 行，sha256 `71dd08a3…`，DCS 变体），均非线上权威。
  **版本拓扑（三方，2026-10-11 锁定）**：
  ```
  线上权威  410 行  md5 56bb6035 / sha256 f7f21ff4  ← 可从 /Files/ResultData/Notebook/run_samap_compliant_v98_dcs.txt 回捞
     └─ sed(/data/work→. , mo→ms) → 部署版 sha256 c0f05b89（= W202610050003104 manifest 记录值）
  本地变体A 437 行  sha256 8da8c8e7  ← wrapper B 的源（本阶段隔离对象）
  本地变体B 450 行  sha256 71dd08a3  ← run_samap_compliant_v98_dcs.py（DCS 变体）
  ```
  依据：GenPilot 容器实测（在线树 + sed 链复现）+ 本地磁盘实测（两变体 sha256）。

### ④ 隔离层产物的平台侧注意事项
- `manifest.json` / `environment.txt` 已在线上 WDL 产物中（`/work/user50719-8334/runsamap/W202610050003104/result/` 下有这两个文件 + 18 个 level JSON + metrics.json）；**`command.txt` 与 `sha256.tsv` 是 449 行变体才写的字段，410 行权威版不生成**——若隔离层契约要求这四件套，需在 wrapper 里补写 command.txt/sha256.tsv。
- 路径权限：`/Files` 对容器是**只读挂载**（fuse ro），只能经 `dcs data push` API 写入；产物目录名建议用不含空格/特殊字符的 ASCII（历史证明 `>` 会阻断上传）；`.py` 扩展名不被接受。
- 预检先行原则（wrapper 先检查目标目录不存在 + 校验输入 sha256，再执行，最后写四件套）与平台"干净工作目录+手动重投"约定**无冲突**。

## 与本地实现的对应（本阶段已落实）

| 会商要点 | 本地隔离层落实 |
|---|---|
| 硬拒绝先于 mkdir | 两个 wrapper 的 `guard_output()` 在创建目录之前检查"已存在/非空即退出 3"（已实测 4 个负例） |
| 预检先行 | `--dry-run` 先 exec 补丁源码并断言输入/常量，再检查输出路径；预检失败不建目录 |
| 四件套补写 | wrapper 在输出目录写 `_patched_source.py` / `wrapper-provenance.json` / `environment.txt` / `sha256.tsv`（脚本原生写 manifest/metrics/command/predictions/confusion） |
| SAMap 版本差异 | wrapper B 的 `environment.txt` 记录 `source_variant_note`（本地 437 行变体 ≠ 线上 410 行权威版，见本记录 §③） |
| 平台回收约定 | 记录于本文件；阶段 5 提交时按"output_path → /work/{user}/<任务目录>/ → tar.gz → push /Files/ResultData/Notebook/"执行（属付费阶段，未启动） |

## 边界声明

- 本会商**未提交任何任务、未启动容器训练、未充值**；GenPilot 的答复不替代本地 metrics/日志/源码/逐细胞证据。
- 会商中出现的任务号/文件 id/哈希均为平台侧只读核对所得。
