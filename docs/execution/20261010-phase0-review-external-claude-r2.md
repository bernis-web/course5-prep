All checks complete. Here is my second-round independent review.

---

# 第二轮独立反方审阅（Phase 0 门）

## 复核方法

我没有采信项目方陈述，而是自己动手：(a) 以 `__file__` 指向**刻意伪造的不存在路径**独立 exec 补丁源码；(b) 跑 wrapper 自带 `--dry-run`；(c) 逐项重算 C4 的哈希清单统计；(d) 打开 `train-saturn.py` 原文核对 C3 引用的每一行。全程只读，未创建/修改/删除任何文件。

---

## C1（阻塞 Task 1）— **已修复**

**补丁存在且注入路径正确**
- `scripts/ortholog_pca_task1_isolated.py:119-123`：P6 条目在 `PATCHES` 中，锚点 `BASE = Path(__file__).resolve().parents[1]` → 替换为 `BASE = Path(SOURCE_BASE)`。
- `:178`：`"SOURCE_BASE": str(BASE)` 确实被注入 exec 命名空间（与 `__name__`、`__file__`、`OUT_DIR` 并列）。
- `:144-159`：`apply_patches` 要求每个锚点 `count(anchor) == 1`，否则 `die(..., 2)`。

**我自己的独立验证**（`__file__` 指向不存在的 `results/phase-20261010/A-smoke/_patched_source.py`，`__name__` 非 `__main__`）：

```
src_sha256 6582d8736c3570f3de23ed36cb57c9cf58f6190c4730c3d39e29928415fd0c44
P6 anchor count: 1
BASE       = D:\projects\course5-prep | == repo root: True
__file__   = ...\A-smoke\_patched_source.py | exists: False
ORTH_DIR   = D:\projects\course5-prep\ortholog | is_dir: True
MAPPING_TSV= D:\projects\course5-prep\config\heart-celltype-map-v1.tsv | is_file: True
LEVELS     = ('coarse',)
  input human/mouse/zebrafish  exists=True/True/True
  ortholog MGI_HOM_.../human_orthos.txt/mouse_orthos.txt  exists=True
```

关键点：**即使 `__file__` 指向不存在的目录，`BASE` 仍解析到仓库根**，四个输入路径全部真实存在。C1 的根因（BASE 由 `__file__` 推导导致输入落到 `results/phase-20261010/` 下）已被 P6 真正切断。

**wrapper 自身 `--dry-run` 实测**：`patches_applied=6`、`preflight_checks=13 failed=0`、`preflight=PASS`、`EXIT=0`。diff 显示 P1–P6 全部按预期落点。

**边界行为实测**：dry-run 在 `:349-368` 返回，`out.mkdir` 在 `:374-376`（预检之后）。运行后 `results/phase-20261010/A-smoke/` **仍不存在**——预检失败不留目录的承诺成立。

**真跑路径我也静态走了一遍**，未发现会失败的步骤：
- `:376` mkdir → 补丁源码 `main()` 的 `if not out.is_dir()` 通过（`:94-95`）
- 补丁保留了原生 `(out/"predictions").mkdir` / `(out/"confusion").mkdir`（diff 中为未改动上下文行）
- `:385-386` 期望的 `coarse_human_to_mouse.json` 与源码 `:309` 的 `f"{level}_{src}_to_{tgt}.json"` 一致
- 冻结 metrics 结构完整（`human->mouse`/`coarse` 十个字段齐全，`diag=1297`、`round(1297/1505,4)=0.8618=acc`），`verify()` 全部断言可满足

**结论：C1 已修复，真跑不会在 `die("missing input")` 处失败。**

## C2 — **已修复**

`docs/execution/20261010-task1-preflight.md:39` 已写明证明边界：

> `--dry-run` … 实测 **13/13 checks pass**，`A-smoke/` **was not created** … It does **not** run the model, so it proves the wrapper can start — **not that the numbers reproduce**.

措辞准确。我实测同为 13/13，且 `A-smoke` 未创建。`:40` 标 `Task 1 smoke: NOT RUN`。文档不再把预检夸大为"已验证可复现"。

## C3 — **已修复**（四份文档措辞一致，行号全部核对无误）

四份文档均已收窄为"默认配置下"：`baseline.md:32`、`2026-10-10-course5-genpilot-dcs-longrun.md:119/150/187`、`20261010-handoff-to-next-agent.md:31`、`20261010-quick-handoff.md:45`。

我打开 `wheelhouse/saturn-src/train-saturn.py`（1065 行）逐行核对：

| 引用 | 实际内容 | 判定 |
|---|---|---|
| `:70` | `use_ref_labels -- if metric learning should increase supervision by using shared coarse labels…` | ✅ |
| `:100-103` | `if use_ref_labels:` → `mining_func(..., ref_labels=ref_labels)` / `else:` → `mining_func(...)` 无 ref_labels | ✅ 默认通道是 `labels` |
| `:1025` | `use_ref_labels=False,`（配置 dict 内） | ✅ 默认 False |
| `:968`（文档未引，但存在） | `--use_ref_labels, type=bool, nargs='?', const=True`，未设 `default` → None（falsy） | 与"默认关闭"一致 |

`scripts/dcs_provenance_v99.py:362` = `labels = np.array([str(v) for v in adata.obs["ref_labels"]])` ✅，正是"评估真值"的取用行。文档表述与源码相符。

## C4 — **已修复**（我重算了全部统计，逐条吻合）

`docs/execution/20261010-baseline.md:26` 的限定与实测完全一致：

```
manifest rows : 46
match         : 23   (confusion 18 + manifest.json/command.txt/environment.txt/metrics.json/v99_mapping_embedded.json)
mismatch      : 1    ['sha256.tsv']
gz_only       : 6    (6 个 coarse predictions 仅 .gz)
missing       : 16
可比合计 24 = 23 吻合 + 1 不符   ✅ 与文档逐字吻合
```

- 自条目：manifest 第 45 行写 `c84dd3780cb0db09…`，磁盘实际 `26fc554a94becbda…` ✅ 与文档 `c84dd378…`/`26fc554a…` 一致
- 目录规模 34 文件 / 350,869 bytes ✅（与 `:25` 一致）
- `_extraction-report.json` 的 `best_local_sha256 = 06be567bb214a854…` ✅ 与文档 `06be567b…` 一致

（注：清单用 `->` 命名、提取物用 `_to_` 命名，这是"本地可比 24 条"的来源，文档已正确界定范围。）

## C5 — **已修复**

`docs/execution/20261010-baseline.md:24` 已补记 `environment.txt`。实测 `results/pilot-v1/samap-v98/wdl-run/extracted/`：**21 个文件、12,730,056 bytes**，含 18 份方向/层级结果 + `manifest.json` + `metrics.json` + `environment.txt`（内容为合法 JSON，含 `samap 1.0.16`、`script_sha256`）✅ 三项数字与文档逐字一致。

---

## 三项前置事实（独立确认）

| 检查 | 结果 |
|---|---|
| `results/phase-20261010/A-smoke/` 不存在 | ✅ 确认不存在（dry-run 后仍不存在） |
| `ortholog_pca_local_v1.py` 未被修改 | ✅ `6582d873…` = 冻结 manifest `script_sha256` |
| `results/pilot-v1` 零触碰 | ✅ 196 个文件中**无一** mtime 晚于 `2026-10-10 11:04:48`；最新为 `2026-10-05` |

我的全部活动结束后复查：`results/phase-20261010/` 树中只有三个既有条目，无新增文件。

---

## 新发现的问题（均为轻微，不阻塞）

**N1 — A-smoke manifest 的 `script_sha256` 会与冻结 manifest 不同（预期但未说明）**
补丁源码 `:344` 是 `sha256_file(__file__)`，真跑时 `__file__` = `A-smoke/_patched_source.py`，故 A-smoke `manifest.json` 的 `script_sha256` 记录的是**补丁后**源码哈希，与冻结 manifest 的 `6582d873…` 不同。这本身是正确行为（记录实际执行物），且 wrapper 已在 `wrapper-provenance.json` / `environment.txt` 另存 `authoritative_source_sha256`。但字段同名易被误读为协议偏离，建议在 `20261010-task1-preflight.md` 加一句说明。

**N2 — 预检未校验冻结 metrics 的结构**
`:356` 只断言 `frozen_metrics_exists`，未断言 `frozen["human->mouse"]["coarse"]` 含 `verify()` 将要比较的十个字段。若冻结 metrics 形状异常，会在跑完模型、写完产物**之后**才于 `:244` 抛未捕获 `KeyError`（退出码 1，而非文档承诺的写 `verification.json` + 退出码 4）。实测冻结 metrics 结构完整，此风险当前不成立，但预检可顺手加固以省掉一次无效全跑。

**N3 — A-smoke manifest 仍会登记 zebrafish 输入**
P2 只改了数据加载循环（源码 `:191`），`SPECIES_FILES`（`:45`）与 `inputs` 登记（`:171-176`）仍含 zebrafish，故 A-smoke manifest 会列出一次从未被读取的 `local_zebrafish_s.h5ad`。纯属观感问题，不影响数字。

**正面记录**：wrapper 的 `write_sha256_tsv`（`:316`）显式排除 `sha256.tsv` 自身，正是规避 C4 那类陈旧自条目的正确做法。

---

## 判定

C1 是本轮唯一阻塞项，我通过独立 exec 补丁源码（含伪造 `__file__` 的对抗性构造）确认其**已真正修复**：`BASE` 钉死在仓库根，全部输入路径真实存在，`A-smoke` 未创建，冻结目录零触碰，权威源码字节未变。C2–C5 的文档改动逐条落地且措辞与源码/实测相符，C3 的四个行号引用、C4 的全部统计数字均经我重算验证。新发现的 N1–N3 为轻微观感/健壮性问题，不构成进入 Task 1 的障碍；"数字能否复现"这一未被证明的边界，已由 C2 的改写如实标注，且复现需要跑模型，超出 Phase 0 的无算力范围。

verdict: PASS
