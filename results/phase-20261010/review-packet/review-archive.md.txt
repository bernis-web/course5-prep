# 阶段 2 隔离层 · 外部审阅全链归档（2026-10-11）

> 共 6 轮 Claude 审阅 + 1 轮 GenPilot 替代审阅；17 项 must_fix 全部闭环；**第 6 轮判 PASS（must_fix: []）**。
> 通道说明：第 1 轮后 `otokapi.com` 代理与模型目录不匹配导致 `claude -p` exit=1（已记录），
> 按用户指示改由 GenPilot 作替代审阅；随后通道恢复（`--model deepseek-v4.1-flash`）继续至第 6 轮。

## 轮 1（Claude）

```text
All checks complete. Here is my adversarial review.

---

# 阶段 2 第一步「A 档全量复算输出隔离层」反方审阅

**审阅方式**：只读。所有结论基于我自己重算的 SHA、自己重跑的命令与退出码，不采信报告自述。执行时间 2026-10-11，cwd=`D:\projects\course5-prep`，HEAD=`8b597d7`。

---

## 1. 两个权威脚本字节未变 + 新 wrapper 未进冻结目录 — **PASS**

| 证据 | 命令 | 结果 |
|---|---|---|
| oPCA 权威脚本 SHA | `sha256sum scripts/ortholog_pca_local_v1.py` | `6582d8736c3570f3de23ed36cb57c9cf58f6190c4730c3d39e29928415fd0c44` = 要求值 ✓ |
| SAMap 权威脚本 vs HEAD | `git diff --stat -- scripts/run_samap_compliant_v98.py` | **空** ✓（`git rev-parse HEAD:…` blob = `b0d02ff7…`，磁盘同） |
| 磁盘 SHA | `sha256sum` | `8da8c8e7221aeac5e3915cc233931aced86f83ba60fd4bb0ac289d5ccbe8e4a7`（前缀 `8da8c8e7` 与报告 §2 一致） |
| 权威脚本 mtime | `find scripts -newermt "2026-10-11"` | 只有两个新 wrapper，两个权威脚本**不在列表** ✓ |
| 冻结目录定义 | `results/phase-20261010/run_scope.json` | `"frozen_results_root": "results/pilot-v1"` —— 只有它；`scripts/` 非冻结 ✓ |
| wrapper 落点 | `git status -- scripts/` | 两个 wrapper 在 `scripts/`（`??`），不在 `results/pilot-v1` ✓ |
| 全仓 A-full* | `find . -name 'A-full*'` | 0 个 ✓ |

wrapper SHA 也与报告 §2 逐字节一致：A=`b63f66a9ea30357e439ea779cafb8662c32c0d52d57f8b2f8c23522224b17e37`，B=`9aa471bbad4a62a47c119b09da0dbb42f6178a050a10dd13a1c0b4a7f8913e24`。

## 2. 隔离层真的拒绝非空目录 — **PASS**

我自己跑的（`.venv39/Scripts/python.exe`，cwd=仓库根）：

```
A --dry-run --out results/phase-20261010/A-smoke
  → ERROR: output dir already exists: results\phase-20261010\A-smoke (refusing to overwrite)   EXIT=3
B --dry-run --out results/phase-20261010/A-smoke
  → ERROR: output dir already exists: …                                                        EXIT=3
```
A-smoke 未被触碰：文件数仍 **13**；`predictions/coarse_human_to_mouse.json` = `dc729820…f10847`、`confusion/…` = `167da767…33580d`（与报告 §1 一致）；A-smoke 目录 mtime 仍为 `Oct 10 16:39`，今日修改文件数 = 0。附带测了 `--out results/phase-20261010/A-SMOKE`（大小写变体）→ 同样 exit 3（`out.exists()` 在 Windows 上大小写不敏感）。

## 3. 拒绝写进 results/pilot-v1 — **PASS**

```
A --dry-run --out results/pilot-v1/A-full-test → ERROR: output resolves inside results/pilot-v1: …A-full-test (refusing)  EXIT=3
B --dry-run --out results/pilot-v1/A-full-test → 同上                                                        EXIT=3
```
额外对抗：`--out results/PILOT-V1/A-full-test`（大小写）→ exit 3（`resolve()` 归一化回 `pilot-v1`）；`--out "results/pilot-v1/../pilot-v1/A-full-test"`（`..` 穿越）→ exit 3。

pilot-v1 零触碰：`find results/pilot-v1 -newermt "2026-10-10 11:04:48" -type f | wc -l` = **0**；冻结 metrics `sha256sum results/pilot-v1/ortholog-pca-v98/metrics.json` = `b2b3ac6bc37c410841bdcbbd968159246e1990db47d02b8fa11844527d66c725` = `b2b3ac6b…c725` ✓（196 个文件全树复核）。

## 4. 预检覆盖全部输入路径 + 预检先于 mkdir — **REVISE**

**顺序正确**（两 wrapper 相同）：`main()` 先 `preflight()`（A:251 / B:243）→ dry-run 提前返回 → `guard_output()`（A:262 / B:254）→ `run()` → `mkdir`（A:206 / B:194）。预检内部也在建目录前先 `guard_output()`（A:183 / B:171）。且 `build_namespace` 的模块级 exec 无副作用：oPCA 源码模块级（:1-60）无 mkdir（mkdir 在 main 内 :161-162），末尾有 `if __name__ == "__main__"` 守卫；SAMap 源码模块级无 mkdir、`samalg` 只在 main 内 import。**PASS**。

**覆盖度：wrapper A 全，wrapper B 缺** — `scripts/ortholog_pca_full_isolated.py:166-181` 覆盖 BASE / ortholog 目录 / 3 个直系同源文件 / 映射表 / 3 份 h5ad，齐全。但 `scripts/run_samap_full_isolated.py:159-169` **只查 BASE、映射表、3 份 h5ad**，未查 ortholog 目录与任何直系同源文件 —— 而 SAMap 源码实际读取全部三个：`:280` `BASE/"ortholog"/"MGI_HOM_MouseHumanSequence.rpt"`、`:306` `human_orthos.txt`、`:312` `mouse_orthos.txt`。缺任一个，wrapper B 的 dry-run 仍会 16/16 PASS，故障推迟到（付费的）阶段 5 正式运行才暴露。→ **REVISE**

## 5. dry-run 不执行模型、不建目录 — **PASS**

我自己跑的默认 dry-run：A = `PREFLIGHT|18/18|… DRY-RUN|no model executed…` **EXIT=0**；B = `PREFLIGHT|16/16|… DRY-RUN…` **EXIT=0**。跑完 `find results/phase-20261010 -maxdepth 1 -name 'A-full*'` = **0**，A-smoke 仍 13 文件、两 SHA 未变。18/16 项数与报告 §3 自述吻合（我逐条数过 A=18、B=16）。

## 6. 产物清单完整性 — **REVISE**（§4 契约对 B 不成立）

- wrapper 追加四件：`_patched_source.py`(A:209/B:197)、`wrapper-provenance.json`(A:229/B:221)、`environment.txt`(A:227/B:219)、`sha256.tsv`(A:237/B:229) —— **4/4 齐全** ✓
- 但报告 §4 把「脚本原生」写成两 wrapper 通用六件（manifest/metrics/**command.txt**/**environment.json**/predictions/confusion）。实测**只有 oPCA 源码**写这六件（`ortholog_pca_local_v1.py:310,312,324,325,330,352`）；**SAMap 源码只写四件**（`run_samap_compliant_v98.py:405,408,414,430` = predictions/confusion/metrics/manifest），**不产 `command.txt`、不产 `environment.json`**。故 wrapper B 的 `command.txt` 实为 wrapper 自己写（B:201），`environment.json` 根本不会出现。§4 对 B 的表述失真。→ **REVISE**
- 另注：新 wrapper **不写** `verification.json`，也不写 A-smoke 里那两个顶层 `predictions.json`/`confusion.json`（Task-1 wrapper 才有）。§4 未声称，故不算违约，但意味着 **Task 2 全量跑没有内建的「是否复现冻结数字」校验**——建议补。
- 小疵：wrapper A 自己写的 `command.txt`(A:213) 会被源码 `:330` 覆盖（内容等价，属死代码）。

## 7. 补丁安全性 — **PASS**（一处文档小疵）

- **A**：PA/PB 各恰好匹配 1 次（`apply_patches` 强制，实测 `patches_applied PA main-header,PB base-scope`）。PA 只改 main 头部（去 argparse/--smoke，`out=OUT_DIR`，并把 smoke 守卫换成「目录须已由 wrapper 预建」断言）；PB 只改 `BASE` 作用域。**未触碰** `normalize_total(1e4)+log1p`、基因首现去重、`NPCS=50`、`K=15`、`NPERM_FULL=200`、标签/排除逻辑 —— 这些常量与代码段均在补丁区之外（源码 `:40-53`、`:210-230`）。补丁后 `smoke=False` 硬编码，全量分支不会误触 `:221` 的抽样子采样 ✓
- **B**：PB/PC 各恰好 1 次（实测 `PB base-scope,PC main-root`）。只改 `BASE` 与 `root`/`output_dir`。**未触碰** `npcs=100,k=20,n_genes=3000,seed=SEED,preprocessing="StandardScaler"`、`DIRECTIONS`（6）、`LEVELS`（3）、`TRUTH_COLUMN`、`NPERM` ✓ 6 方向/3 层级未改。
- 疵：wrapper B docstring `:12-15` 的补丁清单写了 **PB/PC/PD 三个**名字，实际 `PATCHES` 只有 **PB、PC 两个**（root 与 output_dir 合并为一个 patch）。文档与代码不一致（低危）。

## 8. 会商记录与本地实现一致性 — **REVISE**

- 「平台硬拒绝语义可行」「无自动清理/重投约定，cromwell MaxRetries=0」「回收 `→ /Files/ResultData/Notebook/`」「410 行权威版（`56bb6035`）+两处 sed = `c0f05b89`」—— 报告 §5 与会商记录 §①②③ **逐条一致** ✓
- wrapper B 在 `environment.txt` 记录 `source_variant_note`：**是**（`run_samap_full_isolated.py:210-213`）✓
- **不一致点**：会商记录 §③ 把本地 checked-in 版记为 **`71dd08a3`**（"应位于本地 git 仓库"），而磁盘实为 `8da8c8e7`（sha256）/ `b0d02ff7`（git sha1），且 `git rev-list --all --objects` 中**不存在** `71dd08a3` 任何修订。报告 §5 通篇用 `8da8c8e7`，**从未提及或调和 `71dd08a3`**。阶段 5 的版本决策正建立在这条链上，必须先对账。→ **REVISE**
- 行数口径：报告/会商/wrapper 均称本地「438 行」，`wc -l` 实为 **437**（文件以 `\n` 结尾，`split` 计数 438 含尾空串）。差 1，属口径差，非阻断，但既然要做版本对账就应统一。

## 9. 越界检查 — **PASS**

- `review-gate-status.json`：`dcs_submission/training/gpu/recharge` 全 `false`，`task2=not_started` ✓
- 无 A-full* 目录；A-smoke、pilot-v1 在本阶段（含我的复跑）零改动 ✓
- 本阶段产物只有 `docs/execution/` 与 `results/phase-20261010/`（均 untracked，未提交）✓
- 未发现任何会覆盖 A-smoke 或 pilot-v1 的动作（**前提是**按文档从仓库根调用；见第 10 项）。

## 10. 我独立发现的问题 — **REVISE（含 1 个实质缺口）**

**(a) 实质缺口：`guard_output` 与 `run()` 的路径基准不一致，冻结守卫可被 CWD 绕过。**
`guard_output` 校验的是 `(BASE / out).resolve()`（A:135 / B:129），而 `run()` 的 `mkdir` 与全部落盘用的是**未解析的 CWD 相对路径**（A:206、B:194）。我实测（只读 dry-run）：

```
cwd = D:\projects\course5-prep\results
  A --dry-run --out pilot-v1/A-full-test → PREFLIGHT|18/18 … output_not_in_frozen_root D:\projects\course5-prep\pilot-v1\A-full-test → EXIT=0
  B --dry-run --out pilot-v1/A-full-test → PREFLIGHT|16/16 … 同上 → EXIT=0
```
守卫报的是 **BASE 锚定**的 `…\course5-prep\pilot-v1\A-full-test`（不在冻结区，故放行）；但正式运行时 `mkdir` 用的是 **CWD 锚定**的 `…\course5-prep\results\pilot-v1\A-full-test` —— **正落在 `frozen_results_root` 之内**。即：偏离文档 CWD 时，"输出落在 results/pilot-v1 内 → 退出码 3" 这条硬边界**不成立**。本次是 dry-run，未落任何字节（已核 pilot-v1 零触碰），但这是隔离层唯一的实质漏洞。修法一行：入口处 `out_dir = (BASE / args.out).resolve()` 后再校验与 mkdir（或 `os.chdir(BASE)`），并补一个 cwd≠仓库根 的负例测试。

**(b) wrapper B 的权威脚本校验只比前缀 16 位十六进制。** `EXPECTED_SOURCE_SHA = "8da8c8e7221aeac5"`（B:48）+ `src_sha.startswith(...)`（B:144）；`EXPECTED_SOURCE_SHA_FULL`/`RECORDED_SOURCE_SHA256`（B:49-50）**是死变量，从未使用**。docstring `:25` 却写「权威脚本 SHA 不等于期望值 → 退出码 2」，属**过度声明**。wrapper A 是完整 64 位比较（A:48,150），B 应看齐。

**(c) `sha256.tsv` 不会漏收子目录文件** —— 非缺陷：`write_sha256_tsv` 用 `Path(out_dir).rglob("*")`（A:193 / B:181），`rglob` 递归，`p.is_file()` 收全部嵌套文件（A-smoke 的清单确实含 `confusion/…` 与 `predictions/…`）。唯一排除项是任何位置名为 `sha256.tsv` 的文件，可忽略。

**(d) `is_absolute()` 分支无 Windows 特有漏洞（CWD 之外）** —— 我实测：驱动器相对 `C:evil` → `resolves outside repo root: C:\evil` exit 3；UNC `//server/share/x` → exit 3；绝对外部 `D:/tmp/x` → exit 3；`--out` 指向既有**文件** → `already exists` exit 3。`..` 穿越与大小写变体亦被拒（见第 3 项）。

**(e) 低危**：wrapper A 的 `command.txt` 自写被源码覆盖（死代码）；wrapper B docstring 补丁名 PB/PC/PD ≠ 实际 PB/PC；本地 SAMap 行数 437 vs 声称 438。

---

## 结论

隔离层在**文档规定的调用方式**（cwd=仓库根）下完全成立：4 个负例 + 2 个 dry-run 全部按自述复现，两个权威脚本字节未变，冻结目录与 A-smoke 零触碰，本阶段未越界。**无 BLOCK 级问题**——没有数据被破坏、没有边界被真实跨越、全部缺陷都是小改动可修。但存在 1 个实质缺口（CWD 绕过冻结守卫）与 4 处必须修正的准确性问题，**在 Task 2 全量复算放行前必须闭合**，故判 **REVISE**。

```json
{"stage2_isolation_review": "REVISE", "must_fix": ["guard_output 校验 (BASE/out).resolve() 而 run()/mkdir 用 CWD 相对路径：从 cwd=results 传 --out pilot-v1/A-full-test 时 18/18、16/16 全 PASS 且 exit 0，正式运行会 mkdir 进 results/pilot-v1（冻结区）。入口统一 resolve 到 BASE 后再校验与建目录，并补 cwd≠仓库根 的负例测试", "wrapper B 权威脚本校验只比 16 位十六进制前缀（run_samap_full_isolated.py:48,144，且 :49-50 的 *_FULL/RECORDED 为死变量），docstring:25 却称' SHA 不等于期望值 → exit 2'；改为完整 64 位比较并修正文档", "wrapper B preflight 未覆盖 ortholog 目录与 3 个直系同源文件（run_samap_full_isolated.py:159-169），而源码 :280/:306/:312 三个都读；缺失时 dry-run 仍 16/16 PASS，故障推迟到阶段 5 正式运行", "报告 §4 的'脚本原生六件'只对 oPCA 成立：SAMap 源码不产 command.txt/environment.json（仅 manifest/metrics/predictions/confusion），B 的 command.txt 由 wrapper 补写；§4 需按脚本分别列契约", "版本链未对账：会商记录 §③ 记本地 checked-in SAMap 为 71dd08a3，磁盘实为 sha256 8da8c8e7 / git sha1 b0d02ff7，全仓无 71dd08a3 修订；报告 §5 未提及该分歧（另：本地行数 wc -l=437，声称 438）"], "checked": 10}
```
```

## 轮 1′（GenPilot 替代审阅）

见 `20261011-genpilot-review-stage2.md`（BLOCK 因本地对象在容器不可达；纠正 MD5/SHA256 口径；平台侧越界实测 PASS）

## 轮 2（Claude）

```text
## 阶段 2 隔离层 · 第二轮独立复审（只读，未创建/修改任何文件）

复核方式：全部结论由我自己在本机重跑/重算得出，未采信任何自述。共执行 8 次 wrapper dry-run + 4 次哈希/行数实测 + 2 次内存内 diff 打印。

---

### 1. CWD 绕过缺口 — **PASS（已实质修复）**

```
PS D:\projects\course5-prep\results> & ..\.venv39\Scripts\python.exe ..\scripts\ortholog_pca_full_isolated.py --dry-run --out pilot-v1/A-full-test
ERROR: must be invoked from the repo root: cwd=D:\projects\course5-prep\results expected=D:\projects\course5-prep
EXIT=2
PS ...> & ..\.venv39\Scripts\python.exe ..\scripts\run_samap_full_isolated.py --dry-run --out pilot-v1/A-full-test
ERROR: must be invoked from the repo root: cwd=D:\projects\course5-prep\results expected=D:\projects\course5-prep
EXIT=2
```
仓库根 + 冻结路径仍硬拒绝（A/B 同）：
```
ERROR: output resolves inside results/pilot-v1: D:\projects\course5-prep\results\pilot-v1\A-full-test (refusing)
EXIT=3
```
我另加两个未在报告中的负例，均被拦：路径穿越 `--out results/phase-20261010/../pilot-v1/A-full-test` → **exit 3**（A/B）；越界 `--out E:\tmp\A-full-test` → **exit 3**（A/B），且 `E:\tmp\A-full-test` 未生成。
仓库根正常 dry-run：**A 18/18 PASS / exit 0**，**B 20/20 PASS / exit 0**（`PREFLIGHT|18/18` / `PREFLIGHT|20/20`）。

> 残留未测边（非缺陷）：`--out` 指向 junction/symlink 进入 pilot-v1。Python 3.9 的 `Path.resolve()` 会解析 junction，按设计应被拦，但只读审阅下我未建 junction 实测。

### 2. wrapper B 完整 SHA — **PASS（代码）／REVISE（报告引述值错）**

- `EXPECTED_SOURCE_SHA = "8da8c8e7221aeac5e3915cc233931aced86f83ba60fd4bb0ac289d5ccbe8e4a7"` — 逐段点数 = **64 位**；比较语句 `src_sha == EXPECTED_SOURCE_SHA`（`scripts/run_samap_full_isolated.py:144`），**已非前缀比较**。
- 与磁盘实测一致：`Get-FileHash scripts\run_samap_compliant_v98.py` = `8DA8C8E7…5CCBE8E4A7` ✓。
- 死变量已删：`Select-String -CaseSensitive "_FULL|RECORDED_"` 命中 **0 行**。
- ✗ **但报告 §7.1 第 2 行把该完整值写成 `8da8c8e7…e6f7081`** —— 真实尾部是 `…cbe8e4a7`；全仓库检索 `e6f7081` 仅命中该处（及 review-packet 副本）。这一行恰恰是"已改为完整 64 位比较"的证据行，值却是错的。

### 3. wrapper B 预检覆盖 ortholog — **PASS（代码）／REVISE（§3 表未同步）**

实测 B 预检 20 行中新增的正是这 4 项，且全 PASS：
```
PASS ortholog_dir_exists D:\projects\course5-prep\ortholog
PASS ortholog_file:MGI_HOM_MouseHumanSequence.rpt …
PASS ortholog_file:human_orthos.txt …
PASS ortholog_file:mouse_orthos.txt …
```
16 + 4 = 20，**属实**。源码确在 main() 内读取这三件（我核到 SAMap 源 `:427` 用 `SPECIES_FILES`、并另有 ortholog 读取路径），dry-run 不再"全 PASS 而故障推迟到正式运行"。
✗ **报告 §3 表 B 行仍写"16 项：源码 SHA（记录前缀 `8da8c8e7`）…16/16 PASS"**，与 §7.1"B 从 16/16 升为 20/20"及"完整 64 位"两处自相矛盾；§4 是就地改的、§3 没改，同一文档内口径不一。

### 4. 报告 §4 契约表 — **PASS**

按脚本分列已落实。我按行号逐条对照源码，**全部命中**：
- oPCA 六件：`:310` predictions/ · `:312` confusion/ · `:324` metrics.json · `:325` environment.json · `:330` command.txt · `:352` manifest.json ✓
- SAMap 四件：`:403`/`:404` predictions|confusion mkdir · `:405` predictions 写入 · `:408` confusion 写入 · `:414` metrics.json · `:430` manifest.json ✓
- 反向验证"SAMap 源码不产 command.txt/environment.json"：`Select-String "command\.txt|environment\.json|environment\.txt|sha256\.tsv"` 在 SAMap 源中 **0 命中** ✓，故表中"✗（源码不产）"成立；wrapper B 确在 `run()` 补写 command.txt（:207）✓。

### 5. 版本链对账 — **PASS（归属）／REVISE（行数）**

- `71dd08a3` 归属已更正为 `scripts/run_samap_compliant_v98_dcs.py`：磁盘实测 `71DD08A34E16B8797EF6C50D197BD80832BD8EB9F4EF032232AB21187BC14D53` **完全一致** ✓；`run_samap_compliant_v98.py` = `8DA8C8E7…` ✓。
- `run_samap_compliant_v98.py` = **437 行**（换行符计数 437、`Get-Content` 数组长 437）✓，与会商记录一致。
- ✗ **`run_samap_compliant_v98_dcs.py` 实际 450 行，不是 451 行**：换行符数 = 450、`Get-Content` 数组长 = 450、文件以换行结尾、无 BOM（首 3 字节 `34,34,34`）。"451 行"出现在 **3 份文档 5 处**：会商记录 §③（:29,:32,:38）、阶段报告 §5(:72) 与 §7.1(:110)、`20261011-genpilot-review-stage2.md`(:29,:46)。
- 报告已记录该分歧 ✓（§5 与 §7.1 第 5 行均写明"71dd08a3 是另一个文件、非本 wrapper 的源"）。

### 6. 回归：冻结区与权威脚本 — **PASS**

| 项 | 实测 |
|---|---|
| `ortholog_pca_local_v1.py` | `6582D873…15FD0C44` ✓ 未变（与 gate 文件 `authoritative_source_sha256` 一致） |
| `run_samap_compliant_v98.py` | `8DA8C8E7…CBE8E4A7` ✓ 未变 |
| `results/pilot-v1` | 晚于 `2026-10-10T11:04:48` 的文件数 = **0**；总 196 文件 |
| A-smoke | **13** 文件 ✓ |
| `A-full*` 目录 | 全 `results` 递归检索：**无**；`results/pilot-v1/A-full-test` 不存在 |
| `results/phase-20261010/` | 仅 `A-smoke / baseline / review-packet / review-gate-status.json / run_scope.json` —— 8 次 dry-run 后**零新增** |
| DCS/训练/充值 | 本地无任何新产物；平台侧由 `20261011-genpilot-review-stage2.md` §三 独立实查确认"10-05 `W202610050003104` 之后无新 DCS/WDL 提交"。注意本地 `review-gate-status.json` 是 10-10 快照，不是本阶段的新自证 |

（`M scripts/ortholog_pca_dcs_v2.py`、`M scripts/build_final_report.py` 在会话开始时就已是修改态，与本轮无关。）

### 7. 第一轮 PASS 项是否回退 — **PASS（无回退）**

- 拒绝语义：已存在非空目录 → `output dir already exists: …A-smoke (refusing to overwrite)` **exit 3**（A/B）；冻结路径 → exit 3；越界 → exit 3；cwd≠根 → exit 2。
- 补丁安全性（内存内打印 diff，未落盘）：A 仅 2 处 hunk（`BASE = Path(SOURCE_BASE)`；main() 头段去 argparse/`--smoke`、`out = OUT_DIR`），B 仅 2 处（BASE 行；`root/output_dir/mkdir` → `SOURCE_BASE/OUT_DIR` + 断言预建）。**除输出路径与 BASE 作用域外无任何字节改动**；锚点各命中恰好 1 次（`PASS patches_applied`）；A 另断言六方向 MAPS 块恰好出现 1 次（`PASS directions_block_intact`）。
- dry-run 不建目录：8 次调用后目录树不变 ✓。
- 附带：review-packet 内两份 wrapper 副本与现盘文件 **SHA 逐一相同**（`48D79AD1…` / `6603C71B…`），即包内是修订后版本 ✓。

---

## 结论

**代码层：第一轮 5 项 must_fix 我已独立复跑验证，全部真实闭环，且无回归 —— 隔离层本身技术上可判 PASS。** 剩余问题**全部是文档层的可核实错值**，无需改代码，但按本项目"逐字节对账"的口径，报告作为受审交付物不能带这些错值放行：

1. `docs/execution/20261011-stage2-isolation-report.md:107`：`8da8c8e7…e6f7081` → 应为 `8da8c8e7…cbe8e4a7`。
2. 同报告 §3（:43）B 行仍写"16 项 / 记录前缀"，与 §7.1（20/20、完整 64 位）矛盾 → 改为 20/20 或显式标注该行为修订前快照。
3. "451 行"（`run_samap_compliant_v98_dcs.py`）→ 实测 **450 行**，涉及会商记录 §③ 三处、阶段报告 §5/§7.1 两处、`20261011-genpilot-review-stage2.md` 两处。

非阻塞建议：§2 表内两个 wrapper SHA（`b63f66a9…`/`9aa471bb…`）已被 §7.0 取代、且 §2 仍写"438 行"（§7.1 已统一 437），建议加"修订前"标注；文档修完后需**重新生成** `results/phase-20261010/review-packet/report-stage2-isolation.md.txt` 等快照副本，否则包内文本仍带旧值。

```json
{"stage2_isolation_r2": "REVISE", "must_fix": ["report §7.1:107 full SHA suffix wrong: '8da8c8e7…e6f7081' should be '8da8c8e7…cbe8e4a7' (actual EXPECTED_SOURCE_SHA tail)", "report §3:43 wrapper B row still states 16 checks / 'prefix comparison', contradicting §7.1 (verified live: 20/20, full 64-bit ==)", "'451 行' for scripts/run_samap_compliant_v98_dcs.py is wrong: measured 450 lines (newline count 450, Get-Content length 450); fix in consultation §③ x3, report §5/§7.1, genpilot-review §二 x2"], "checked": 7}
```
```

## 轮 3（Claude）

```text
All checks executed. Here are the results.

---

# 阶段 2 隔离层 · 第三轮复审（收口确认）— 独立只读核验

核验时间：2026-10-11 17:12–17:20 (+0800)｜方式：`sha256sum` / `wc -l` / `awk` / `diff` / 实跑 dry-run（两个 wrapper）｜未写入任何被测文件

## (a) review-packet 快照同步 — **PASS（内容）/ REVISE（清单）**

内容层面**已同步**：7 个快照副本与源文件逐字节相同。

```
diff docs/execution/20261011-stage2-isolation-report.md      packet/report-stage2-isolation.md.txt   → IDENTICAL
diff docs/execution/20261011-genpilot-consultation-...md     packet/consultation-...md.txt           → IDENTICAL
diff docs/execution/20261011-genpilot-review-stage2.md       packet/genpilot-review-stage2.md.txt    → IDENTICAL
diff docs/execution/20261010-baseline.md                     packet/baseline-20261010.md.txt         → IDENTICAL
diff scripts/ortholog_pca_full_isolated.py                   packet/wrapper-A-....py.txt             → IDENTICAL
diff scripts/run_samap_full_isolated.py                      packet/wrapper-B-....py.txt             → IDENTICAL
diff results/phase-20261010/review-gate-status.json          packet/review-gate-status.json.txt      → IDENTICAL
```

但**清单（INDEX.md）不完整**，且包在本次复审期间被重建过：

- 我第一次读到时 INDEX.md = 2371 B / mtime 16:37（含 `report-stage2-isolation.md.txt` 行）；现在 = 2234 B / mtime **17:09:29**，该行**已被删掉**，换成了 `genpilot-review-stage2.md.txt` 行。
- 结果：`report-stage2-isolation.md.txt`（9718 B，**就在包里、且已同步**）**在 INDEX 中无行、其哈希在包内任何地方都未公布**。平台审阅人按 INDEX 走，会看不到阶段 2 主报告、也无法校验其完整性。
- INDEX 现列 7 行的哈希**全部实测吻合**（baseline `3f658648…`、consultation `615985a6…`、dry-run `11ece0d6…`、genpilot-review `a660ff26…`、review-gate `561654b9…`、wrapper-A `48d79ad1…`、wrapper-B `6603c71b…`）✓

## (b) 残留字符串 — **PASS**

| 目标串 | docs/execution/20261011-*.md | 说明 |
|---|---|---|
| `e6f7081` | **0 命中** | ✓ 已清除 |
| `记录前缀` | **0 命中** | ✓ 已清除 |
| `451 行` | 仅 `20261011-genpilot-review-stage2.md:29` | 该行在 GenPilot 结论 JSON 的 `must_fix` 原文引用块内，属**照录原话**，按你的口径不算残留 ✓ |

全仓（排除 `.git`/`wheelhouse`/`.venv39`/`pilot-v1`）复扫：`e6f7081`、`记录前缀` 仅剩于 `.tmp-claude-stage2-r2-out.md`（我第二轮审阅草稿）与 `.tmp-claude-stage2-r3.md`（本轮提示词）两个未跟踪的审阅工作文件，非交付文档，不计缺陷。

## (c) 脚本行数与 SHA-256 复算 — **PASS**

```
wc -l  scripts/run_samap_compliant_v98_dcs.py = 450     sha256 71dd08a34e16b8797ef6c50d197bd80832bd8eb9f4ef032232ab21187bc14d53
wc -l  scripts/run_samap_compliant_v98.py     = 437     sha256 8da8c8e7221aeac5e3915cc233931aced86f83ba60fd4bb0ac289d5ccbe8e4a7
awk NR scripts/run_samap_compliant_v98.py     = 437     （文件以 \n 结尾，两种计法一致）
```

报告数字逐项对账：

| 报告位置 | 报告值 | 实测 | 判定 |
|---|---|---|---|
| §7.1:107 完整 64 位 SHA | `8da8c8e7221aeac5e3915cc233931aced86f83ba60fd4bb0ac289d5ccbe8e4a7` | 逐字符相同 | **✓ 修正到位** |
| §5:71 / §7.1:110 行数 | 437 行 | 437 | ✓ |
| §5:72 / §7.1:110 DCS 变体 | 450 行 / `71dd08a3…` | 450 / `71dd08a3…` | **✓ 修正到位** |
| §2:22 / §7.0:95 权威 oPCA | `6582d873…0c44` | `6582d8736c35…15fd0c44` | ✓ |

## (d) 回归 — **PASS**

```
权威脚本（未变）：ortholog_pca_local_v1.py 6582d873…0c44
                  run_samap_compliant_v98.py 8da8c8e7…cbe8e4a7
results/pilot-v1  晚于 2026-10-10T11:04:48 的文件数 = 0            ✓ 零触碰
A-smoke 文件数 = 13；predictions.json dc729820… / confusion.json 167da767… / verification.json 16/16 ok、failed_checks[]  ✓ 未变
find -name "A-full*" → 空（我实跑 2 次 dry-run 后复查仍为空）      ✓ 无 A-full*
gate：dcs_submission/training/gpu/recharge 全 false；run_scope.json 四项 no_* 全 true  ✓
未提交 DCS：另有 GenPilot 平台侧实测「10-05 之后无任何新 DCS/WDL 提交」作为第三方佐证  ✓
```

我自己实跑的隔离语义（**本轮新证据**）：

```
A --dry-run            → PREFLIGHT|18/18  exit=0
B --dry-run            → PREFLIGHT|20/20  exit=0
A/B --out A-smoke      → exit=3  "output dir already exists … refusing to overwrite"
A/B --out pilot-v1/x   → exit=3  "resolves inside results/pilot-v1 … refusing"
A cwd=results --out pilot-v1/x → exit=2 "must be invoked from the repo root"
```
→ 报告 §3 的 `18 项 / 20 项`、§7.1 #3 的「B 从 16/16 升为 20/20」**独立复现成立**；64 位比较亦在源码中确认（`src_sha == EXPECTED_SOURCE_SHA` 全 64 hex 比较，`[:16]` 仅用于打印）。

## (e) 本轮是否引入新不一致 — **PASS（无新增）**，但暴露 2 处**既存**不一致

本轮 3 项修改自身**自洽**：§3（20 项/完整 64 位）与 §7.1 #2/#3 一致；§7.1:107 完整 SHA 与 §2:22 前缀 `8da8c8e7` 一致；450 行与会商/审阅记录一致。

**但两处既存残留（非本轮引入，前两轮未捕获）：**

1. **报告 §2:24「新文件 SHA-256」整行过期**——发布的是两个**审阅对象**的错误哈希，且与同一文档 §7.0:93-94 和包内 INDEX 自相矛盾：

| | §2:24 写的 | §7.0:93-94 / INDEX / 磁盘实测 |
|---|---|---|
| wrapper A | `b63f66a9ea30…b17e37` | `48d79ad1c41d85ac3a68d806ec771e3dca7c8d927f4a27dc608ec8bb81bee83c` |
| wrapper B | `9aa471bbad4a…13e24` | `6603c71b394282f53c8dec253cc900a7e1cc8ab166b8e20b0a145279bb967111` |

`b63f66a9`/`9aa471bb` 全仓仅出现在该行（及其包内副本），应为第 1 轮改 wrapper 前的旧值。

2. **`438 行`残留，与「已统一为 437」直接冲突**（磁盘实测 437）：
   - `docs/execution/20261011-stage2-isolation-report.md:22`（§2）
   - `docs/execution/20261011-genpilot-consultation-stage2-isolation.md:54`
   - `scripts/run_samap_full_isolated.py:18`（wrapper B docstring，**审阅对象本体**）
   
   而 `report:110` 自称「行数口径 `wc -l`=437 / `split`=438 **已统一为 437**」——该声明目前不成立。

---

## 判定

- 本轮 3 项修改：**全部真实到位**（逐字符/逐项实测确认），且无回归。
- 隔离层行为：我独立实跑复现 18/18、20/20、4 负例 exit 3、cwd 守卫 exit 2。
- 未通过的是**文本/清单准确性**：§2:24 过期哈希（与 §7.0 冲突）、`438 行`残留（与 §7.1 冲突）、包 INDEX 漏登主报告行。

均非 BLOCK 级（不涉及安全语义、不动冻结数据、不改权威脚本），但都落在**推送给平台审阅的自包含包**里，属"审阅对象自述与自证互相打架"，按你的口径计入 must_fix。

### must_fix

1. `docs/execution/20261011-stage2-isolation-report.md:24`（+ 包内 `report-stage2-isolation.md.txt:24`）：`b63f66a9…`/`9aa471bb…` → 实测 `48d79ad1c41d85ac3a68d806ec771e3dca7c8d927f4a27dc608ec8bb81bee83c` / `6603c71b394282f53c8dec253cc900a7e1cc8ab166b8e20b0a145279bb967111`。
2. `438 行` → `437 行`：`report:22`、`consultation:54`、`scripts/run_samap_full_isolated.py:18`。**注意耦合**：改 wrapper B docstring 会改变 wrapper B 的 SHA-256，须连带更新 §2:24、§7.0:94、`review-packet/INDEX.md`、包内 wrapper-B 快照与 `dry-run-evidence.txt` 中引用的值；否则修一处坏三处。
3. `results/phase-20261010/review-packet/INDEX.md` 补回 `report-stage2-isolation.md.txt` 行（文件已在包内且与源同步，SHA-256 = `f4595277d35a84b9add8a027a5889326be62ce63047b7a958116d426ac233b76`）；并说明包在 17:09 被重建、避免审阅人拿到与 INDEX 不一致的目录状态。

### 附注（非 must_fix）

- 包在本次复审期间被重建（INDEX.md 16:37 → 17:09:29），我上述所有 diff/哈希结论均以 **17:12 之后**的状态为准。
- `genpilot-review-stage2.md` §四称包为「9 个纯文本文件」，实际目录现为 10 个（8×.txt + INDEX.md + INDEX.md.txt），补登第 3 项时一并订正。
- wrapper B dry-run 打印为 `source=8da8c8e7221aeac5 expected=8da8c8e7221aeac5`（仅显示截断 16 位），比较本身是完整 64 位；若怕被误读为"前缀比较"，可把打印改成全值。

```json
{"stage2_isolation_r3": "REVISE", "must_fix": ["report §2:24 (and packet snapshot) publishes wrong SHA-256 for both review objects: b63f66a9…/9aa471bb… must be 48d79ad1c41d85ac3a68d806ec771e3dca7c8d927f4a27dc608ec8bb81bee83c / 6603c71b394282f53c8dec253cc900a7e1cc8ab166b8e20b0a145279bb967111 — contradicts §7.0 and packet INDEX", "'438 行' residual must become '437 行' in report:22, consultation:54, and scripts/run_samap_full_isolated.py:18 (disk wc -l = 437, awk NR = 437); note editing the wrapper docstring changes wrapper B SHA-256, so §2:24, §7.0:94, INDEX.md, the packet wrapper-B snapshot and dry-run-evidence.txt must be re-hashed together", "review-packet/INDEX.md omits the report-stage2-isolation.md.txt row (file is present and byte-synced, SHA-256 f4595277d35a84b9add8a027a5889326be62ce63047b7a958116d426ac233b76); the packet was rebuilt at 17:09:29 and lost that row — restore it and note the rebuild"], "checked": 5}
```
```

## 轮 4（Claude）

```text
核验完毕。以下是第四轮（最终收口）逐项结论。

---

## (a) INDEX 登记与同步 — **REVISE**

**登记完整性 + 哈希逐字节相等：PASS**

```
$ sha256sum results/phase-20261010/review-packet/*.txt
3f658648190ca8145dfe16818f58e423bc085dc87e8af12e963784c3e66cb835 *baseline-20261010.md.txt
8ee91e6d269069f008755f1080f5b2efa2da90724127c7af41f65a041477eb44 *consultation-stage2-isolation.md.txt
9728c3fe16819c5e37c00828c38a87d411a4d3c7d141b7e42fbeb2b8ef7170a2 *dry-run-evidence.txt
a660ff2698c1a3079402285d223d879ad5c873608895810e98f7e8b60ca891c7 *genpilot-review-stage2.md.txt
1081161cfb3fb7c2930ad2d3bb711dcabf66cb5f78aefae30278c6807ec09f1f *report-stage2-isolation.md.txt
561654b9078daa67d63ad275120fd13ad29b94d861486beeb9518c707befd31c *review-gate-status.json.txt
48d79ad1c41d85ac3a68d806ec771e3dca7c8d927f4a27dc608ec8bb81bee83c *wrapper-A-ortholog_pca_full_isolated.py.txt
ec7e2945beeba72b624bcc2d3c15ba561f9322c33070d22cab794fe3bdffe21f *wrapper-B-run_samap_full_isolated.py.txt
```
INDEX 表内 8 行 SHA 与上表**逐一相等**；`cmp INDEX.md INDEX.md.txt` → IDENTICAL；包内共 10 文件（8 内容 .txt + INDEX.md + INDEX.md.txt），与 INDEX 第 8 行"8 个 .txt"自述一致。✓

**与源文件同步：REVISE（7/8 IDENTICAL，1 处 stale）**

```
IDENTICAL  wrapper-A…py.txt      <= scripts/ortholog_pca_full_isolated.py
IDENTICAL  wrapper-B…py.txt      <= scripts/run_samap_full_isolated.py
IDENTICAL  report-stage2-isolation.md.txt        <= docs/execution/20261011-stage2-isolation-report.md
IDENTICAL  consultation-stage2-isolation.md.txt  <= docs/execution/20261011-genpilot-consultation-stage2-isolation.md
IDENTICAL  review-gate-status.json.txt           <= results/phase-20261010/review-gate-status.json
IDENTICAL  baseline-20261010.md.txt              <= docs/execution/20261010-baseline.md
DIFFER     genpilot-review-stage2.md.txt         <= docs/execution/20261011-genpilot-review-stage2.md
```
`dry-run-evidence.txt` 无对应源文件（包内独有），不适用同步检查。

差异内容（`diff` 唯一一行，第 64 行）：
- 源 `docs/execution/20261011-genpilot-review-stage2.md`（mtime **17:20**）：`8 个 .txt 审阅对象 + 索引（共 10 个文件）` ← 已按第三轮意见订正
- 包内副本 `genpilot-review-stage2.md.txt`（mtime **17:09**）：`9 个纯文本文件` ← **未重新拷贝**

时间线证明这是漏拷而非方向问题：包在 17:18–17:19 重建时重拷了 consultation/report/wrapper-B 并重建 INDEX，**唯独跳过了 genpilot 这一份**；源文件随后 17:20 被改。即第三轮"文件计数"意见只修了源、没同步包内副本——而这份副本正是要推送平台的产物，其自述"9 个纯文本文件"与实际 10 文件不符。

附带（同属该项，轻）：`INDEX.md:16` 的说明列仍是占位符 `（未登记）`。

## (b) 过期值残留 — **REVISE**

| 模式 | 结果 |
|---|---|
| `b63f66a9` / `9aa471bb` / `e6f7081` / `记录前缀` | 全仓库 0 命中 ✓ |
| `451 行` | 仅 `genpilot-review-stage2.md:29` 的 GenPilot 原话引用行（豁免）✓ |
| `438 行` | **仍有 2 处残留（含包内副本共 4 处）** ✗ |

残留 1 — 报告 §2 表：
```
docs/execution/20261011-stage2-isolation-report.md:22
| 权威脚本 SHA-256 | `6582d873…0c44`…✓ 未变 | `8da8c8e7…`（本地 438 行变体）✓ 未变 |
```
（包内 `report-stage2-isolation.md.txt:22` 同步残留）

残留 2 — wrapper B 的 `source_variant_note`（**会在正式运行时写进 `environment.txt`**）：
```
scripts/run_samap_full_isolated.py:217
"local 438-line variant; frozen SAMap numbers came from the 410-line …"
```
（包内 `wrapper-B-…py.txt:217` 同步残留）

同一文件第 18 行 docstring 已改为 `437 行变体`，与第 217 行**自相矛盾**。实测口径：
```
$ python -c "d=open('scripts/run_samap_compliant_v98.py','rb').read(); print(d.count(b'\n'), len(d.splitlines()), d.endswith(b'\n'))"
437 437 True
```
→ 437 行、结尾有换行。438 为错值。（报告:110 的"`wc -l`=437 / `split`=438"是口径说明，非残留值，不计。）

## (c) 三处 SHA 一致性 — **PASS**

```
live A = 48d79ad1c41d85ac3a68d806ec771e3dca7c8d927f4a27dc608ec8bb81bee83c
live B = ec7e2945beeba72b624bcc2d3c15ba561f9322c33070d22cab794fe3bdffe21f
```
报告 §2（:24）、§7.0（:93/:94）、`INDEX.md`（:18/:19）、以及包内报告副本（:24/:93/:94）**四处全部等于 live 新值**，无旧值残留。wrapper B 本轮改过 docstring 后新值 `ec7e2945…` 已全线贯通。✓

## (d) 实跑复核 — **PASS**

```
$ ./.venv39/Scripts/python.exe scripts/ortholog_pca_full_isolated.py --dry-run
PREFLIGHT|18/18|out=…\A-full-20261011T092108Z        EXITCODE=0
$ ./.venv39/Scripts/python.exe scripts/run_samap_full_isolated.py --dry-run
PREFLIGHT|20/20|out=…\A-full-samap-20261011T092112Z  EXITCODE=0

[ortholog_pca_full_isolated --out results/phase-20261010/A-smoke] exit=3 :: refusing to overwrite
[ortholog_pca_full_isolated --out results/pilot-v1/x]             exit=3 :: resolves inside results/pilot-v1
[run_samap_full_isolated      --out results/phase-20261010/A-smoke] exit=3 :: refusing to overwrite
[run_samap_full_isolated      --out results/pilot-v1/x]             exit=3 :: resolves inside results/pilot-v1

(cwd=results) …ortholog_pca_full_isolated.py --dry-run --out pilot-v1/x  EXITCODE=2 :: must be invoked from the repo root
(cwd=results) …run_samap_full_isolated.py      --dry-run --out pilot-v1/x  EXITCODE=2 :: must be invoked from the repo root
```
18/18、20/20、4×exit 3、2×exit 2 全部符合预期；dry-run 后未产生任何目录。

## (e) 回归 — **PASS**

| 项 | 实测 | 结论 |
|---|---|---|
| `ortholog_pca_local_v1.py` | `6582d873…0c44`，= 冻结 `manifest.json:script_sha256` | 未变 ✓ |
| `run_samap_compliant_v98.py` | `8da8c8e7…cbe8e4a7` | 未变 ✓ |
| 两权威脚本 git 状态 | 均 tracked 且 porcelain 干净（仅两 wrapper 为 `??` 新文件） | ✓ |
| A-smoke | 13 文件，mtime **全部 2026-10-10 16:39**；`dc729820…` / `167da767…` 未变 | 零触碰 ✓ |
| pilot-v1 | 196 文件，晚于 `2026-10-10T11:04:48` 者 = **0** | 零触碰 ✓ |
| 冻结 metrics | `b2b3ac6b…c725` 未变 | ✓ |
| `A-full*` | `ls: cannot access …A-full*: No such file or directory` | 无 ✓ |
| gate 标志 | dcs_submission/training/gpu/recharge 全 `false` | ✓ |
| DCS/训练/充值痕迹 | 无新提交、无新 DCS 产物（`docs/dcs-*` 均为 9 月旧件） | ✓ |

我本轮实跑只读、未落任何文件：包内 10 个文件 mtime 仍为 17:18/17:19，`scripts/__pycache__/*.pyc` 仍为 17:03（早于我 17:21 的运行，且被 `.gitignore` 覆盖）。

---

## 结论

隔离层的**实质行为**（预检、补丁、拒绝语义、越界防护、冻结区零触碰）本轮全部复现通过，无 BLOCK 级问题。但**文本收口未完成**：第三轮第 2 项（438→437）漏改了 2 处，第 3 项（文件计数）漏拷了包内副本。故判 **REVISE**。

**注意耦合（与上轮同一陷阱）**：修 must_fix #2 会再次改变 wrapper B 的 SHA-256，必须连带重算并同步 `report §2(:24)` / `§7.0(:94)` / `INDEX.md:19` / 包内 `wrapper-B-…py.txt` + `report-stage2-isolation.md.txt`，否则重演"改了源、哈希三处不一致"。

```json
{"stage2_isolation_r4": "REVISE", "must_fix": ["报告 §2 (:22) 及包内副本 report-stage2-isolation.md.txt:22 仍为「本地 438 行变体」，实测 run_samap_compliant_v98.py = 437 行（LF=437, splitlines=437），应改为 437 行", "scripts/run_samap_full_isolated.py:217 的 source_variant_note 仍为 'local 438-line variant'（会被写入 environment.txt），与同文件 :18 docstring 的 437 自相矛盾；改为 437-line 后 wrapper B SHA 必变，须连带重算并同步 report §2(:24)/§7.0(:94)、INDEX.md:19、包内 wrapper-B-*.py.txt 与 report 副本", "包内 genpilot-review-stage2.md.txt（17:09）落后于源 docs/execution/20261011-genpilot-review-stage2.md（17:20）：源已订正为「8 个 .txt 审阅对象 + 索引（共 10 个文件）」，副本仍为「9 个纯文本文件」，须重拷并更新 INDEX.md:15 哈希", "INDEX.md:16 的 report-stage2-isolation.md.txt 说明列仍为占位符「（未登记）」，须补实际说明"], "checked": 5}
```
```

## 轮 5（Claude）

```text
核验完毕。全部命令均为我本轮独立执行，未采信自述。

---

## a) `review-packet/INDEX.md` — **PASS**

```
sha256sum results/phase-20261010/review-packet/*.txt *.md   # 与 INDEX 表逐行比对
ls *.txt | wc -l  → 9      ls | wc -l → 10      INDEX 表行数 → 8
grep -n "见文件名\|未登记\|TODO\|TBD" INDEX.md → 无命中 (exit 1)
```

| 项 | 结果 |
|---|---|
| 表内 8 行 SHA 与磁盘逐字节相等 | ✓ 8/8 全部相等（我独立复算） |
| 覆盖包内全部 `.txt` | ✓ 磁盘 9 个 `.txt` = 8 个审阅对象 + `INDEX.md.txt`；INDEX 首行明确写「8 个 `.txt` + 索引 `INDEX.md` / `INDEX.md.txt`」，总数 10 与磁盘一致 |
| 占位符「（见文件名）/（未登记）」 | ✓ 0 命中 |
| `INDEX.md.txt` 是否已登记 | ✓ 与 `INDEX.md` 字节相同（同为 `bb36d98b…d3e0`），按「索引」类别声明 |

## b) 残留扫描 — **PASS**

```
grep -rIn "438|9 个纯文本|b63f66a9|9aa471bb|e6f7081|记录前缀" <docs,scripts,results,deliverables,tests> --exclude tmp
Grep(glob=*.md) / Grep(glob=*.{py,js,json,txt,docx}) 全仓
```

全仓命中仅 4 类，**均非残留**：
- `b63f66a9` / `9aa471bb` / `e6f7081` / `记录前缀` / `9 个纯文本` → **0 命中**（交付文档中彻底清除）
- `438` → 仅 `20261011-stage2-isolation-report.md:110` 的「行数口径 `wc -l`=437 / `split`=438 **已统一为 437**」，属口径说明（第三/四轮已明确不计）；包内副本同址同步
- `wheelhouse/holoviews_samap-1.0.1/CHANGELOG.md` 的 `#438` 是第三方 PR 编号
- `451 行` 仅存于 `genpilot-review-stage2.md:29` 的 GenPilot **原话引用行**内（该行整体为 `"…437 行 8da8c8e7 / 451 行 71dd08a3…"`），按指示保留 ✓；同文档正文已用 437/450

## c) wrapper SHA 三处交叉一致性 — **PASS**

```
sha256sum scripts/ortholog_pca_full_isolated.py scripts/run_samap_full_isolated.py
48d79ad1c41d85ac3a68d806ec771e3dca7c8d927f4a27dc608ec8bb81bee83c  A
6f1385cd12d464fc43d392d8fc04a7efaeb5b5854e0d14854773c6963cfe26fa  B
```

| 位置 | A | B |
|---|---|---|
| 磁盘实测 | `48d79ad1…bee83c` | `6f1385cd…cfe26fa` |
| 报告 §2「新文件 SHA-256」 | 同上 ✓ | 同上 ✓ |
| 报告 §7.0 表 | 同上 ✓ | 同上 ✓ |
| `INDEX.md` | 同上 ✓ | 同上 ✓ |
| 包内快照文件本身 | 同上 ✓ | 同上 ✓ |

四/五处**互相一致且等于磁盘值**。另：wrapper B `:18` 与 `:217` 的 `source_variant_note` 已改为 `local 437-line variant`（第 1 项）✓；报告 §2 B 行已改为「（本地 437 行变体）」✓；`genpilot-review-stage2.md:64` 已改为「8 个 `.txt` 审阅对象 + 索引（共 10 个文件）」（第 3 项）✓。

## d) 实跑 — **PASS**（5/5，另补 B 侧 3 例）

| 命令 | 实测 | 期望 |
|---|---|---|
| A `--dry-run` | `PREFLIGHT\|18/18`，exit **0** | ✓ |
| B `--dry-run` | `PREFLIGHT\|20/20`，exit **0** | ✓ |
| A `--out results/phase-20261010/A-smoke` | `refusing to overwrite`，exit **3** | ✓ |
| A `--out results/pilot-v1/x` | `resolves inside results/pilot-v1`，exit **3** | ✓ |
| cwd=`results` | `must be invoked from the repo root: cwd=…\results expected=…\course5-prep`，exit **2** | ✓ |
| （补）B 同上三例 | 3 / 3 / 2 | ✓ |

## e) 回归 — **PASS**

| 项 | 证据 |
|---|---|
| `ortholog_pca_local_v1.py` | `6582d8736c3570f3de23ed36cb57c9cf58f6190c4730c3d39e29928415fd0c44` ✓ |
| `run_samap_compliant_v98.py` | `8da8c8e7221aeac5e3915cc233931aced86f83ba60fd4bb0ac289d5ccbe8e4a7` ✓ |
| `pilot-v1` 零触碰 | 晚于 `2026-10-10T11:04:48` 的文件数 = **0**；`ortholog-pca-v98/metrics.json` = `b2b3ac6b…c725` ✓ |
| `A-smoke` 零触碰 | 今日（≥10-11）修改文件数 = **0**；仍 **13** 文件；`predictions.json`=`dc729820…f10847`、`confusion.json`=`167da767…33580d`、`verification.json` 16/16 ok / `failed_checks: []` / PASS ✓ |
| 无 `A-full*` | `results/phase-20261010/` 目录列表与跑前完全一致，无新目录 ✓ |
| 未提交 DCS / 未训练 / 未充值 | `review-gate-status.json`：`dcs_submission=false, training=false, gpu=false, recharge=false`；`task2=not_started` ✓ |

---

## 附加发现（本轮新提出，非上述 4 项）：**报告 §7 的审阅轮次记录已过期，且 INDEX 对其描述失实**

这是我核验 INDEX 描述与实际内容时发现的，属第四轮同类的「改源后未连带更新」：

1. **`docs/execution/20261011-stage2-isolation-report.md` §7.2（:114-122）** 以现在时写：
   > 「第 2 轮复审无法执行…**第 2 轮独立复审待通道恢复后补做**。通道恢复前，**不进入 Task 2 全量复算**。」

   但该报告最后修改时间为 **17:31:19**，而第 2/3/4 轮复审分别在 **17:06:36 / 17:13:50 / 17:25:08** 完成并各自判 REVISE（共 3+4+4 项，均已修复）。报告 §7 通篇**没有任何第 2/3/4 轮记录**（grep `^## ` 仅得 §7.0/§7.1/§7.2，全文 128 行）。同一文档 §7.0 还写着「**本轮**修订后的 SHA」，说明 §7.0 是刚改的，却未回头修 §7.2。
2. **`review-packet/INDEX.md`（及 `.txt`，:16）** 把该报告描述为「**§7 四轮审阅闭环**」——§7 实际只有第 1 轮 + 一次「未执行」，不存在四轮闭环。包内 INDEX 自称「自包含可审包，供平台侧独立审阅」，此描述会让平台审阅人以为复审链停在第 1 轮，看不到后续 11 项修正。

**性质**：文本/账目一致性问题，非隔离层功能缺陷（隔离层实质行为本轮 8 例实测全绿）。

**非阻塞观察**（不建议改，仅记录）：
- `INDEX.md` 头部写「17:4x 重建」、尾部写「重建时间 17:30:45」，而文件 mtime 为 `17:31:56`（报告源 17:31:19 改后 INDEX 被重写但时间串未更新），差 ~71 s。
- `wrapper-A-….py:8` docstring「经四轮外部审阅验证」——wrapper A 冻结于 16:17，彼时阶段 2 仅第 1 轮已跑（若指阶段 0 的四轮则无误），含义不明；因其 SHA 已登记，不建议为此改动。

---

**判定**：a–e 五项全部 PASS，第四轮 4 项修正经独立复算/复跑确认全部落实且无回归；但包内主报告 §7 的复审记录与 INDEX 的描述均与事实不符，属上一轮同类未收口项，故整体判 **REVISE**（非 BLOCK）。

```json
{"stage2_isolation_r5": "REVISE", "must_fix": ["report §7.2 (docs/execution/20261011-stage2-isolation-report.md:114-122, + packet copy report-stage2-isolation.md.txt) still states in the present tense that the round-2 review was never executed and the phase is blocked on it, while rounds 2/3/4 completed at 17:06:36/17:13:50/17:25:08 (all REVISE, 11 items fixed) — before the report's own last edit at 17:31:19; §7 contains no record of rounds 2-4. Add §7.3-§7.6 (or an explicit review-round ledger) and correct §7.2's status sentence, then re-copy the packet snapshot so its SHA in INDEX is recomputed", "review-packet/INDEX.md:16 (and INDEX.md.txt) describes report-stage2-isolation.md.txt as containing '§7 四轮审阅闭环', but §7 holds only round 1 plus a 'not executed' note; correct the description to match the report's actual §7 content and rebuild INDEX.md/INDEX.md.txt"]}
```
```

## 轮 6（Claude）

```text
核验完毕。以下为第六轮（收口确认）逐项结论，全部命令由我本轮独立执行，未采信任何自述。

---

## a) 报告 §7（含 §7.2 台账）与事实一致性 — **PASS**

**轮次/判定/项数逐条比对**（§7.2 台账 ↔ 各轮审阅记录 mtime 与结论 JSON）：

| 台账行 | 记录文件 | 文件 mtime | 实际 must_fix 项数 | 判定 | 相符 |
|---|---|---|---|---|---|
| 1 Claude REVISE | `.tmp-claude-stage2-out.md` | 10-11 13:00:57 | 5（含 guard_output CWD 实质缺口） | REVISE | ✓ |
| （—）通道中断 exit=1 | `20261011-review-channel-check.md` | — | — | — | ✓ |
| 1′ GenPilot BLOCK | `20261011-genpilot-review-stage2.md` | — | 4（JSON 数组实为 4 条） | BLOCK | ✓ |
| 2 Claude REVISE | `.tmp-claude-stage2-r2-out.md` | 10-11 **17:06:36** | 3 | REVISE | ✓（台账记 17:0x）|
| 3 Claude REVISE | `.tmp-claude-stage2-r3-out.md` | 10-11 **17:13:50** | 3 | REVISE | ✓（台账记 17:12–17:20）|
| 4 Claude REVISE | `.tmp-claude-stage2-r4-out.md` | 10-11 **17:25:08** | 4 | REVISE | ✓（台账记 17:2x）|
| 5 Claude REVISE | `.tmp-claude-stage2-r5-out.md` | 10-11 **17:36:55** | 2 | REVISE（a–e 全 PASS） | ✓（台账记 17:4x）|

**项数算术自洽**：5+3+3+4+2 = **17**，与「5 轮共 17 项全闭环」一致；「1 项实质缺口 + 16 项文本/清单准确性」= 17 ✓（GenPilot 的 4 项单列在 1′ 行，不计入 17，台账行文已如此区分）。
**第 5 轮 a–e PASS 表述**：`.tmp-claude-stage2-r5-out.md:93` 原文「a–e 五项全部 PASS…整体判 REVISE（非 BLOCK）」，与台账「REVISE（a–e 五项 PASS，仅文档记录未收口）」逐字相符 ✓。

**过期状态句**：§7.2（报告 :114–128）已无「未执行」「待通道恢复」字样（`grep -n "未执行\|待通道恢复" docs/execution/20261011-stage2-isolation-report.md` → **0 命中**）；旧句「第 2 轮复审无法执行…阶段被阻塞于此」已删除。台账第 2 行「通道中断 exit=1」属**历史记录行**（非状态声明），保留正确。§7.2 当前状态段（:126–128）为「17 项全闭环 + Task 2 仍未放行」，与事实一致。

---

## b) `review-packet/` 登记与同步 — **PASS**

```
$ sha256sum results/phase-20261010/review-packet/*.txt   # 与 INDEX 表逐行比对
```
| 项 | 结果 |
|---|---|
| INDEX 表行数 | **8** ✓（`baseline` / `consultation` / `dry-run-evidence` / `genpilot-review` / `report` / `review-gate-status` / `wrapper-A` / `wrapper-B`）|
| 8 行 SHA 与磁盘 | **8/8 逐字节相等** ✓（我独立复算，无一处不符）|
| 包内 `.txt` 总数 | 9 = 8 审阅对象 + `INDEX.md.txt`；INDEX :8 自述「8 个 `.txt` + 索引」与实际 10 文件相符 ✓ |
| `INDEX.md` vs `INDEX.md.txt` | `cmp` → **IDENTICAL**（同为 `187fb195…39a6`）✓ |
| report 行描述 | 「§7 审阅轮次台账：5 轮全闭环」与报告 §7.2 标题「审阅轮次台账（最终状态：5 轮，全部闭环）」**相符** ✓（第五轮「四轮审阅闭环」失实描述已消除）|
| 快照 ↔ 源文件 | **6/6 IDENTICAL**：report↔`docs/execution/20261011-stage2-isolation-report.md`、consultation↔`…genpilot-consultation-stage2-isolation.md`、genpilot-review↔`…genpilot-review-stage2.md`、review-gate-status↔`results/phase-20261010/review-gate-status.json`、wrapper-A↔`scripts/ortholog_pca_full_isolated.py`、wrapper-B↔`scripts/run_samap_full_isolated.py`、baseline↔`docs/execution/20261010-baseline.md`（共 7 处，均 IDENTICAL）；`dry-run-evidence.txt` 为包内独有，不适用同步检查 ✓ |

---

## c) 残留串复扫（全仓 + 包内） — **PASS**

| 串 | 交付文档命中 | 说明 |
|---|---|---|
| `9 个纯文本` / `b63f66a9` / `9aa471bb` / `e6f7081` / `记录前缀` | **0** | 仅存于未跟踪的 `.tmp-claude-stage2-r2/r3/r4-out.md`（我自己的历轮审阅草稿），非交付件 |
| `438` | 2 处，**均属口径说明** | 报告 :110「`wc -l`=437 / `split`=438 已统一为 437」、:122 台账记第三轮发现「`438 行`残留」；其余命中为 `heart-inspect-evidence-20260920.json` 数值、A-smoke 十六进制串、`wheelhouse/…CHANGELOG.md` 的第三方 PR `#438` |
| `未执行` | 4 处，**全部合理** | `20261010-baseline.md:50`（「本阶段未执行」＝历史陈述）、`20261010-phase0-review-external-claude.md:9`（未执行 git 写操作）、`superpowers/plans/…:397`、`wave0-evidence-matrix…:100` —— 无一处为阶段 2 的过期状态 |

---

## d) 回归抽验 — **PASS（全部实测）**

```
$ .venv39/Scripts/python.exe scripts/ortholog_pca_full_isolated.py --dry-run
PREFLIGHT|18/18|out=…\A-full-20261011T094815Z          EXIT=0        ✓
$ .venv39/Scripts/python.exe scripts/run_samap_full_isolated.py --dry-run
PREFLIGHT|20/20|out=…\A-full-samap-20261011T094821Z    EXIT=0        ✓
$ …ortholog_pca_full_isolated.py --dry-run --out results/pilot-v1/x
ERROR: output resolves inside results/pilot-v1: …\results\pilot-v1\x (refusing)   EXIT=3   ✓
$ (cd results && ../.venv39/…/python.exe ../scripts/ortholog_pca_full_isolated.py --dry-run --out pilot-v1/x)
ERROR: must be invoked from the repo root: cwd=…\results expected=…\course5-prep    EXIT=2   ✓
```
| 回归项 | 实测 | 结论 |
|---|---|---|
| 权威 `ortholog_pca_local_v1.py` | `6582d873…5fd0c44` | 未变 ✓ |
| 权威 `run_samap_compliant_v98.py` | `8da8c8e7…be8e4a7` | 未变 ✓ |
| `results/pilot-v1` 零触碰 | 196 文件，晚于 `2026-10-10T11:04:48` 者 = **0**；`ortholog-pca-v98/metrics.json` = `b2b3ac6b…66c725` | ✓ |
| `A-smoke` 零触碰 | **13** 文件；10-11 修改数 = **0**；`predictions/coarse…json`=`dc729820…f10847`、`confusion/coarse…json`=`167da767…33580d`（= 冻结 `ortholog-pca-v98` 同名件，逐字节相同）；`verification.json` **16 ok:true / 0 ok:false / failed_checks: [] / status=PASS** | ✓ |
| 无 `A-full*` | `ls results/phase-20261010/A-full*` → No such file；目录列表与跑前一致 | ✓ |
| 报告 §1 数字 | predictions **1535** 条、confusion **28** 条、included **1505** —— 与报告「1535 行 / 28 条混淆」相符 | ✓ |
| 只读证明 | 我全部 4 条命令均为 `--dry-run`/拒绝路径；跑后重算包内 8 文件 + INDEX + 两 wrapper SHA，**与跑前逐字节相同** | ✓ |

---

## 非阻塞观察（记录，不影响本轮判定）

1. **`review-packet/INDEX.md:6` 重建说明归因陈旧**：头部仍写「（第四轮审阅 4 项修正后的重算哈希）」，而文件实于 **17:38:11** 为**第五轮** 2 项修正再次重建；尾部「重建时间：2026-10-11T17:30:45」亦早于实际 mtime 17:38:11（此项第五轮已判为非阻塞）。**不影响任何登记哈希**（8/8 与磁盘相符）。建议下轮顺手改为「第五轮审阅 2 项修正后的重算哈希 / 17:38」。
2. **仓库根存在游离 `INDEX.md`（未跟踪，2865 B，17:37:52）**：与包内 INDEX 仅 :16 一字之差（「5 轮 17 项全闭环」vs「5 轮全闭环」），属重建过程的中间副本残留；两者与报告 §7.2 均不矛盾，但建议清理或使之一致，避免与包内交付件混淆。
3. **`docs/execution/20261011-review-channel-check.md:29`** 仍有「第 2 轮复审待通道恢复」字样，同文件 :36 列 wrapper B 旧值 `6603c71b…`。该文件是**当日事件记录**（标题即「本轮不可用」），其 §三/§四 为当时点陈述，且**不在审阅包内**；报告 §7.2 已将其正确定性为「通道中断」历史行，故不计缺陷。如需绝对干净，可加一行「本记录状态已被报告 §7.2 台账取代」。
4. `docs/execution/20261011-genpilot-review-stage2.md:68`「第二轮复审正在运行」同理，为 16:34 时点的记录，且该文档 §四文件计数已订正为「8 个 `.txt` + 索引（共 10 个文件）」✓。
5. `scripts/ortholog_pca_full_isolated.py:8` docstring「经四轮外部审阅验证」含义不明（第五轮已判非阻塞、且其 SHA 已登记）——**不建议改动**，改动会使 wrapper A SHA 与三处登记失配。

---

**判定**：第五轮 2 项 must_fix **均已落实且经独立复算/复跑确认**（§7.2 台账与各轮记录逐条相符、算术自洽、无过期状态句；INDEX report 行描述与报告实际内容相符且 SHA 重算无误）；包完整性、残留串、SHA 交叉一致、隔离语义实跑、回归六类**全部 PASS**。剩余 5 项均为时间/归因类陈旧说明或游离文件，**不涉及任何哈希、任何隔离行为、任何登记项**，不构成收口阻塞。

```json
{"stage2_isolation_r6": "PASS", "must_fix": [], "checked": 4}
```

后台全仓复扫（排除 `.git`/`wheelhouse`/`.tmp-claude`）已完成，结果与我的 c) 项判定**完全吻合**，无需修正结论：

```
=== [9 个纯文本] ===        （0 命中）
=== [b63f66a9] ===          （0 命中）
=== [9aa471bb] ===          （0 命中）
=== [e6f7081] ===           （0 命中）
=== [记录前缀] ===           （0 命中）
=== [待通道恢复] ===
./docs/execution/20261011-review-channel-check.md:29: …第 2 轮复审待通道恢复…
```

- 5 个交付级残留串在**全仓**（不只是 docs/results 子树）均为 **0 命中**；
- `待通道恢复` 全仓仅 1 处，正是我已列为**非阻塞观察 #3** 的当日事件记录行（该文件不在审阅包内，报告 §7.2 已将其定性为「通道中断」历史行）。

判定不变：

```json
{"stage2_isolation_r6": "PASS", "must_fix": [], "checked": 4}
```
```

