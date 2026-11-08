我已完成独立复核。以下是审阅结论。

---

# 课题 5 Phase 0 只读基线 · 对抗性独立审阅

**审阅者立场**：未参考既有两份本地审阅的结论作为前提；下文每条均为我自己重算/重读源码后得出。凡与既有审阅不同处已标注。

**只读声明**：全程未修改、创建、删除、移动任何文件；未执行 `git commit/push/reset/checkout/clean`；未提交 DCS、未调用 GenPilot、未训练、未启动 GPU、未充值；未读取或输出任何凭据。

---

## 一、逐项判定

### 第 1 项 · Phase 0 是否确实只读 —— **通过**

`results/phase-20261010/run_scope.json:7-10` 四项边界（`no_training` / `no_platform_submission` / `no_gpu` / `no_recharge`）均为 `true`。但我没有只依赖这份自述，而是做了两次独立取证：

- **冻结目录**：`results/pilot-v1` 递归 196 个文件，`LastWriteTime` 晚于 `2026-10-10T11:04:48+08:00` 的**数量为 0**；最大 mtime 为 `2026-10-05T01:12:04`（`samap-v98/wdl-run/extracted/exact_zf--hu.json`），早于快照 5 天。
- **全仓扫描**（3290 个文件，排除 `.git` / `node_modules` / `.venv`）：快照后仅 **16 个文件**被写入，构成全部是 Phase 0 记录与审阅通道产物 —— `docs/` 8 个、`results/phase-20261010/` 4 个、`scripts/ortholog_pca_task1_isolated.py` 及其 `__pycache__` 编译缓存、`.tmp-claude-phase0-review-*` 2 个。**没有** DCS payload、模型输出、训练产物、费用或 GPU 记录。

`results/phase-20261010/` 下只有 `run_scope.json`、`review-gate-status.json`、`baseline/`；`A-smoke/` 不存在。**未发现任何训练 / DCS 提交 / GPU / 充值的痕迹。**

> 唯一瑕疵（非实质）：`20261010-task1-preflight.md:38` 称 `--dry-run` "writes nothing"，实际留下了 `scripts/__pycache__/ortholog_pca_task1_isolated.cpython-39.pyc`（16:03）。应读作"不写任何输出产物"。

### 第 2 项 · 11/11 输入 SHA 是否一致 —— **通过**

对 `input-sha256.tsv` 的 11 个文件行逐行重算 `Get-FileHash -Algorithm SHA256`，并同时比对 `size_bytes`：

```
ROWS_PARSED=11
---- MATCH=11  MISMATCH_OR_MISSING=0 ----
```

11/11 的 size 与 sha256 **双匹配**，无一例外。表头行未被计入文件行（解析得 11 行，与 `20261010-task1-preflight.md:9` 一致）。

### 第 3 项 · 三个目录与口径描述 —— **通过（附 2 条注记）**

目录清点**逐字节吻合**：

| 目录 | 声明 | 实测 |
|---|---|---|
| `ortholog-pca-v98` | 40 files / 18,098,994 B | 40 / 18,098,994 ✓ |
| `samap-v98/wdl-run/extracted` | 21 files / 12,730,056 B | 21 / 12,730,056 ✓ |
| `saturn-v99/raw/recovered-20261001` | 34 files / 350,869 B | 34 / 350,869 ✓ |

`20261010-baseline.md:22-25` 的构成描述准确，含"部分 payload"（实测 `payloads/` 仅 6 个 coarse `.gz`，`exact`/`fine` 只有 confusion）与"哈希清单"。**未发现 candidate 被写成 confirmed**：`saturn-v99/.../manifest.json:27` 用的是 `candidate_hashes` 字段名。

**注记 A（既有审阅未提，我新发现）**：`recovered-20261001/sha256.tsv` 的**自条目不自洽**。该文件第 45 行把自己列为 `c84dd378…`，而该文件在磁盘上的实际哈希是 `26fc554a…`（即 `input-sha256.tsv:11` 冻结的那个值）。`_extraction-report.json` 已诚实记录为 `"content_only_sha_mismatch"`，但它同时记录 `best_local_sha256 = 06be567b…`，**又与当前磁盘值 `26fc554a…` 不符** —— 说明该报告在本地文件之后被重新生成过，报告本身已陈旧。

我进一步验证了实质部分：把清单里的 `->` 映射到本地 `_to_` 命名后，**本地存在的 24 个条目中 23 个哈希吻合**（18 份 confusion + manifest + command + environment + metrics + v99_mapping_embedded），唯一不符的就是 `sha256.tsv` 自条目；另 22 条（18 份 predictions、`candidate_hashes.json`、readout.ipynb、src tree tsv）本地不存在。**结论：SATURN 的实质 provenance 成立，18 份 confusion 与容器侧逐字节一致；只是这份哈希清单是对容器文件的"本地重发版"，不应被当作容器原件的字节级复制品。** baseline 应加一句限定。

**注记 B**：`20261010-baseline.md:23` 描述 SAMap extracted 时漏记 `environment.txt`（21 = 18 + manifest + metrics + environment.txt）。属"含…"式不完全枚举，非错误。既有审阅 r1 的附注 A 已提过。

### 第 4 项 · 科研口径 —— **通过（1 处措辞需收窄，见 §3-C3）**

- **transductive / in-sample**：三处 manifest 的 `protocol_label` 均为 `transductive_formal_reassessment` —— oPCA（`manifest.json` `protocol` + `mode=full`）、SAMap（`extracted/manifest.json:7` 与 `:11`）、SATURN（`manifest.json:2`）。**未发现任何写成 inductive 或泛化的位置。**
- **oPCA label-free 的适用范围**：`scripts/ortholog_pca_local_v1.py:254` `X_joint = np.vstack([Xs, Xt])`、`:258` `PCA(...).fit_transform(X_joint)` —— PCA 载荷在 **src+tgt 联合矩阵**上拟合；`:265-266` `knn.fit(Z[m_s][keep_r], ytr[keep_r])` —— 分类头**使用 reference 标签**。`20261010-baseline.md:31` 引用的 `:254,258` 与 `:265-266` **行号全部准确**，"label-free 只适用于表示层、v98 是 transductive 投影、不得写成 inductive"成立。
- **SAMap `keys=cell_type` label-aware**：`scripts/run_samap_compliant_v98.py:28` `TRUTH_COLUMN = "cell_type"`，`:350` `SAMAP(sams, keys={s: TRUTH_COLUMN for s in sams}, gnnm=gnnm)`。成立。
- **v97g 只有日志级数字**：`results/pilot-v1/saturn-v97g/` 下**只有一个文件** `raw/task-metadata.json`（1661 B），**没有** predictions / confusion。成立。
- **SATURN `labels` / `ref_labels`**：见 §3-C3，措辞过强，需收窄。
- **独立复算（既有审阅未做全量，我做了）**：对冻结 oPCA 的 **18/18 格**独立核对，`opca_cells=18 failures=0`、`coverage_cells=18 failures=0`。即每格：混淆矩阵条目和 == `n_q`；`round(diag/n_q, 4) == acc`；`|acc×n_q − diag| < 0.5`；`coverage_q == round(n_q/n_q_total, 4)`。**分母 / coverage / 标签空间在冻结侧自洽，未发现不一致。**

### 第 5 项 · 覆盖 / 绕过审批门 / 提前训练路径 —— **需修改**

**(a) 覆盖路径的登记本身：准确且完整。** 我全量 grep 了 `scripts/*.py` 中的 `pilot-v1`，确认写入者**只有**下列三处（`build_final_report.py`、`build_final_presentation.py` 仅读取）：

- `scripts/ortholog_pca_local_v1.py:158` 全量模式 `out = results/pilot-v1/ortholog-pca-v98`，守卫**只在** smoke 分支 `:159-160`。行号准确，风险描述准确。
- `scripts/run_samap_compliant_v98.py:249-250` `output_dir = root/"results"/"pilot-v1"/"samap-v98"` + `mkdir(parents=True, exist_ok=True)`，无守卫。行号准确。
- `scripts/extract_v99_from_logs_v1.py:17`、`scripts/parse_v99_rec_log_v1.py:21` `RAW = …/saturn-v99/raw`。行号准确。

**未发现绕过审批门的自动提交路径，也未发现提前训练路径。**

**(b) 但为 Task 1 准备的隔离机制是坏的 —— 这是本次审阅的主要发现。**

`scripts/ortholog_pca_task1_isolated.py:300-305` 用
```python
namespace = {"__name__": "_ortholog_pca_task1_patched", "__file__": str(patched_path), "OUT_DIR": out}
exec(compile(patched, str(patched_path), "exec"), namespace)
```
执行补丁后的源码。而权威源码的**所有输入路径都由 `BASE` 推导**：`scripts/ortholog_pca_local_v1.py:33` `BASE = Path(__file__).resolve().parents[1]`（全文件仅此 1 处）。**五个补丁没有一个重定义 `BASE`** —— 我验证过 `PATCHES` 块（wrapper `:65-108`）中 `BASE` 只出现 1 次，且位于 P1 的**锚点**里（`out = BASE / "results" / "pilot-v1" / …`），该锚点被替换为 `out = OUT_DIR`。

于是补丁运行时 `BASE = Path("<out>/_patched_source.py").resolve().parents[1] = results/phase-20261010`，导致：

| 常量 | 补丁运行时的值 | 是否存在 |
|---|---|---|
| `ORTH_DIR` | `results/phase-20261010/ortholog` | **False** |
| `MAPPING_TSV` | `results/phase-20261010/config/heart-celltype-map-v1.tsv` | **False** |
| `SPECIES_FILES` | `results/phase-20261010/local_{human,mouse}_s.h5ad` | **False** |

权威源码自己的输入检查 `ortholog_pca_local_v1.py:173-175` 会立刻 `die("missing input: …")`（退出码 2）。**即：Task 1 按现状执行必然在计算前中止，无法复现冻结数字。**

后果分级：

- **对冻结结果无风险**（fail-safe）：它在写任何 metrics 之前就死；且 wrapper `:267-269` 另有 `--out` 落在 `results/pilot-v1` 内即退 3 的守卫（该守卫我审过，`Path` 在 Windows 上大小写不敏感比较，逻辑正确）。所以这不是"会覆盖冻结结果"的路径。
- **但 Task 1 不可运行**，`20261010-task1-preflight.md:31` 的"protocol-faithful by construction"**未被建立**，`:29` 的"Wrapper prepared"名不副实。
- **`--dry-run` 抓不到这个 bug**：它只校验锚点并打印 diff，**从不 exec 补丁源码**（wrapper `:278-291`）。因此 `preflight:38`"all 5 anchors matched exactly once"**不能作为 wrapper 可用的证据**。
- **副作用**：`ortholog_pca_local_v1.py:161-162` 的 `mkdir` 早于 `:175` 的 `die`，失败运行会留下 `A-smoke/predictions/`、`A-smoke/confusion/`；重试会撞上 wrapper `:293-294` 的非空目录守卫（退 3），需要人工删除 —— 与"不清理"边界冲突。

**其余部分设计是对的**（我逐条核过，仅供修复时保留）：P2–P5 锚点在权威源码中**均恰好匹配 1 次**（实测 count 全为 1），补丁语义正确；`nperm` 保持 `NPERM_FULL=200`，与冻结 `n_perm=200` 一致；docstring `:40-41` 的参考值与冻结 metrics **完全吻合**（`acc=0.8618 majority=0.4817 shuffle_p=0.0 n_ref=1528 n_q=1505 n_q_total=1535 coverage_q=0.9805 n_perm=200 shared_genes=15869 对角线=1297`）；human+mouse 两物种运行不影响 `human->mouse` 的 `shared_genes`/`n_ref`，故这些参考值作为验收靶子是正确的。

---

## 二、我实际运行的验证命令与数字

| 验证 | 命令要点 | 结果 |
|---|---|---|
| 11 文件 SHA | `Import-Csv -Delimiter "\`t"` + `Get-FileHash -Algorithm SHA256` + `Get-Item.Length` | `MATCH=11 MISMATCH_OR_MISSING=0` |
| 三目录清点 | `Get-ChildItem -Recurse -File` + `Measure-Object -Sum Length` | 40/18098994、21/12730056、34/350869 |
| pilot-v1 冻结 | `Where LastWriteTime -gt 2026-10-10T11:04:48+08:00` | `total=196`，`files_after_cutoff=0`，max mtime `2026-10-05T01:12:04` |
| 全仓新增文件 | 递归 3290 文件，排除 `.git`/`node_modules`/`.venv` | 快照后仅 16 个，全为 Phase 0/审阅文档 + wrapper |
| git 现状 | `git rev-parse HEAD` / `--abbrev-ref HEAD` / `status --porcelain=v1` | `8b597d788352009609688e28c7f2ed23a0358f17`、`codex/teacher-reply-report-prep`、232 条（staged 0 / unstaged 29 / untracked 203） |
| oPCA 18 格自洽 | 逐格重算 confusion 和、`round(diag/n_q,4)`、`acc×n_q`、`coverage_q` | `opca_cells=18 failures=0`；`coverage_cells=18 failures=0` |
| SATURN 哈希清单 | 按 `->`→`_to_` 映射逐条 `Get-FileHash` | `match=23 mismatch=1 absent_locally=22`（唯一 mismatch 为 `sha256.tsv` 自条目） |
| 脚本 provenance | `Get-FileHash` 对比 preflight 声明 | `ortholog_pca_local_v1.py` = `6582d873…` **等于**冻结 manifest 的 `script_sha256`；wrapper = `2b585211…` **等于** preflight 声明 |
| wrapper 安全性 | 读源码 + 文本计数 | PATCHES 块内 `BASE` 出现 1 次（在 P1 锚点中）；补丁后 `BASE` 仍由 `__file__` 推导 |
| A-smoke 存在性 | `Test-Path` | `False`（dry-run 确实未创建输出） |

git 计数漂移（228→232）是 Phase 0 自身新增文档所致，`20261010-baseline.md:16` 已作时点快照说明，属预期，**不是**既有改动被动过。

---

## 三、文档与文件不一致清单（要求停止并修正）

| 编号 | 位置 | 不一致内容 | 要求 |
|---|---|---|---|
| **C1（阻塞 Task 1）** | `scripts/ortholog_pca_task1_isolated.py:300-305` vs `20261010-task1-preflight.md:29-31` | wrapper 注入 `__file__=patched_path`，使补丁源码的 `BASE` 变为 `results/phase-20261010`，三处输入路径全部不存在 → 必然 `die("missing input")`。preflight 却称"prepared"且"protocol-faithful by construction"。 | **修**：把 `__file__` 指回权威源码路径（补丁路径另用变量传），或新增第 6 个锚点把 `BASE = Path(__file__).resolve().parents[1]` 钉成绝对原路径；**并**加一个真正 exec 补丁源码的自检（或至少断言推导出的输入路径存在），否则不得声称 wrapper 就绪。修完后需重新复核。 |
| **C2** | `20261010-task1-preflight.md:38` | "`--dry-run` … writes nothing" 与实际留下的 `scripts/__pycache__/ortholog_pca_task1_isolated.cpython-39.pyc` 不符；且 dry-run 不 exec 补丁源码，**不能**作为 wrapper 可用的证据。 | 改措辞为"不写任何输出产物"，并明确 dry-run 的证明边界。 |
| **C3** | `20261010-baseline.md:31`、`docs/superpowers/plans/2026-10-10-course5-genpilot-dcs-longrun.md:150` | "不能写成 `ref_labels` 参与训练" / "`ref_labels` 只是输出/评估真值"过强。`wheelhouse/saturn-src/train-saturn.py:70,100-101,968` 存在一等公民开关 `--use_ref_labels`，会把 `ref_labels` 送进 miner。默认 `use_ref_labels=False`（`:1025`）时结论成立，v99 实际配置即默认。 | 收窄为："默认配置下训练标签通道是 `labels`；`ref_labels` 用于输出列与评估真值（`:388`、`:466-469`）；源码存在 `--use_ref_labels` 可将其引入 miner，本阶段未启用。" **不影响任何数字。** |
| **C4** | `20261010-baseline.md:25` | 未提示 `recovered-20261001/sha256.tsv` 的自条目不自洽（自列 `c84dd378…`，实为 `26fc554a…`），也未提示 `_extraction-report.json` 的 `best_local_sha256=06be567b…` 已陈旧。 | 加一句限定：该清单是本地重发版，自条目与 4 条本地缺失项不可用于字节级验证；实质 provenance 由 18 份 confusion + 5 个 provenance 文件（23/24 吻合）支撑。 |
| **C5（非阻塞）** | `20261010-baseline.md:23` | 漏记 SAMap extracted 的 `environment.txt`。 | 补齐枚举。 |

**按审阅请求的要求：发现上述文档与文件不一致，停止推进；在 C1–C2 落地并复核前，不得运行 Task 1 smoke。**

---

## 四、结论

第 1、2、3、4 项**通过** —— 这些正是 Phase 0 自身的核心主张，我用独立重算全部证实：冻结目录零触碰、11/11 SHA 双匹配、三目录字节级吻合、18/18 格分母与 coverage 自洽、口径除一处措辞外全部写对。**Phase 0 没有把 candidate 写成 confirmed，没有把 transductive 写成泛化，没有训练/DCS/GPU/充值。**

第 5 项**需修改**：覆盖路径的登记准确且完整，未发现绕过审批门或提前训练的通路；但为 Task 1 准备的隔离 wrapper 因 `BASE` 作用域缺陷**无法运行**，而 preflight 断言其已就绪 —— 这是文件与文档的实质不一致，且现有 dry-run 证据覆盖不到它。该缺陷 fail-safe（不会覆盖冻结结果），修复面小且明确，故不构成 BLOCK。

**可放行范围**：无。**待 C1–C2 修复并复核后**，方可准备 `results/phase-20261010/A-smoke/` 的隔离 `human→mouse` / `coarse` 零成本 smoke。C3–C5 应同期落地，但非放行前置。

verdict: REVISE
