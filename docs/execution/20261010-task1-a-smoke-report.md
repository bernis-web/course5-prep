# Task 1 隔离 A-smoke 阶段报告（2026-10-10）

## 目标与范围

零成本、纯本地、单方向：**`human → mouse`，`coarse` 层**。

唯一目的：确认本地统一评分器能复现冻结的 transductive 数字。本阶段**不**做三物种全量、**不**做六方向全量、**不**提交 DCS、**不**训练、**不**启动 GPU、**不**充值。

## 执行

| 项 | 值 |
|---|---|
| 命令 | `D:/projects/course5-prep/.venv39/Scripts/python.exe scripts\ortholog_pca_task1_isolated.py` |
| 解释器 | Python 3.9.6（`.venv39`） |
| 依赖 | numpy 1.23.5 · anndata 0.10.9 · scanpy 1.9.3 · sklearn 1.6.1 |
| 平台 | Windows-10-10.0.22631-SP0 |
| 耗时 | 9.8 s（脚本内计）／10.5 s（端到端） |
| 退出码 | 0 |
| 起止 | 2026-10-10T16:39:33 → 16:39:43 |

运行日志：

```text
ortholog pairs: hm=17611 fh=10398 fmm=9058; mapping rows=38
human: 1528 cells x 32732 genes (dropped 0 dup symbols)
mouse: 1535 cells x 32379 genes (dropped 0 dup symbols)
human->mouse done genes=15869 acc(coarse)=0.8618
DONE mode=full elapsed=9.8s
DONE|status=PASS|files_hashed=12|elapsed=9.9s
```

## 产物

`results/phase-20261010/A-smoke/`，**13** 个文件（其中 12 个被 `sha256.tsv` 收录哈希，第 13 个是 `sha256.tsv` 自身）：

```text
_patched_source.py                       14502   补丁后实际执行的源码
command.txt                                 92
environment.json                           262
environment.txt                            660
manifest.json                             2414
metrics.json                              1217   只含 human->mouse / coarse 一格
confusion.json                             809   顶层副本
predictions.json                       1283386   顶层副本
sha256.tsv                                1118   A-smoke 全树哈希（12 条）
verification.json                         2718
wrapper-provenance.json                   7231   含 6 个补丁的完整 unified diff
confusion/coarse_human_to_mouse.json       809
predictions/coarse_human_to_mouse.json 1283386
```

## 验证：16/16 通过，`failed_checks: []`

与 `results/pilot-v1/ortholog-pca-v98/metrics.json` 的 `human->mouse` / `coarse` 逐字段比对（容差 `1e-12`，按冻结精度 4 位小数取整后比较）：

| 检查 | 结果 |
|---|---|
| `acc` | 0.8618 vs 0.8618，abs_diff = **0.0** |
| `majority` | 0.4817 vs 0.4817，abs_diff = **0.0** |
| `shuffle_p` | 0.0 vs 0.0，abs_diff = **0.0** |
| `n_ref` | 1528 vs 1528 |
| `n_q` | 1505 vs 1505 |
| `n_q_total` | 1535 vs 1535 |
| `coverage_q` | 0.9805 vs 0.9805 |
| `n_perm` | 200 vs 200 |
| `shared_genes` | 15869 vs 15869 |
| `confusion:identical` | 28 条 vs 28 条，逐条相同 |
| `confusion_total_eq_n_q` | 1505 == 1505 |
| `round(diag/n_q,4) == acc` | 1297/1505 → 0.8618 == 0.8618 |
| `abs(acc*n_q − diag) < 0.5` | 1297.009 − 1297 = 0.009 |
| `diag_matches_frozen` | 1297 == 1297 |
| `frozen_round(diag/n_q,4) == frozen_acc` | 0.8618 == 0.8618 |
| `n_perm_is_full` | 200（未降级为 smoke 的 20） |

## 最强证据：与冻结产物**逐字节相同**

不只是数值相同：

| 文件 | 冻结 `results/pilot-v1/ortholog-pca-v98/` | A-smoke | 判定 |
|---|---|---|---|
| `confusion/coarse_human_to_mouse.json` | `167da767a21c8688b77dfdd210f17d3bdddec2077182c11648b5ed0e3533580d`，809 B | 同左 | **字节相同** |
| `predictions/coarse_human_to_mouse.json` | `dc729820b3a442d676cc17913f2e79e852ce795d4517730eb10807d145f10847`，1,283,386 B | 同左 | **字节相同** |

两个 SHA 也正是 `results/phase-20261010/baseline/input-sha256.tsv:4-5` 冻结的那两个值。即：在只看 human+mouse 的隔离运行里，混淆矩阵与 **1535 条**逐细胞预测（含 `neighbor_barcodes`；其中 1505 条被计分，30 条因 `mapping_status:unmapped` 排除）与该格在六方向全量运行中的产出**逐字节一致**——这与"PCA 按方向单独拟合、KNN 按方向单独训练"的代码事实相符（`scripts/ortholog_pca_local_v1.py:254,258,265-266`）。

`metrics.json` 的 SHA 与冻结件不同（`e13a2bdb…` vs `b2b3ac6b…`）是预期的：A-smoke 只含 1 格，冻结件含 18 格。

## 协议保真链

- 权威源码 `scripts/ortholog_pca_local_v1.py` sha256 = `6582d8736c3570f3de23ed36cb57c9cf58f6190c4730c3d39e29928415fd0c44`，**等于冻结 `ortholog-pca-v98/manifest.json` 记录的 `script_sha256`** —— 打的补丁正是产出冻结数字的那个脚本。
- 补丁后源码 sha256 = `c56d3ee7607cf4a5b20af446ba279390f1cef3ba361e7b76d55ec3871367ba55`，6 个补丁（P1 main-header、P2 species-loop、P3 direction-map、P4 levels、P5 done-print、P6 base-scope），完整 unified diff 存于 `wrapper-provenance.json`。
- `c56d3ee7…` 在 **四处是同一个值**：`manifest.json` 的 `script_sha256`、`sha256.tsv` 的 `_patched_source.py` 行、`environment.txt` 的 `patched_source_sha256`、`wrapper-provenance.json` 的 `patched_source_sha256`。外部审阅第三轮发现的 F1（同一产物里出现两个都自称"补丁源码哈希"的值）已闭合。
- 执行前预检 15/15：`BASE` 指向仓库根、`ORTH_DIR` 与 3 个直系同源文件、`MAPPING_TSV`、3 个 h5ad 全部存在，`LEVELS == ("coarse",)`，`NPERM_FULL == 200`，冻结 metrics 结构完整。
- 补丁范围仅限"物种/方向/层级/输出路径/`BASE` 作用域"，未触碰归一化、基因去重、PCA 参数、KNN 参数、置换次数、标签层级逻辑。

## 边界与限制（不得越界表述）

1. 本结果只覆盖 `human→mouse` / `coarse` **一格**；不构成 18 格结论，也不构成跨方法比较。
2. 结果仍是 **transductive / in-sample**。本次复现**不**把任何结论升级为 inductive 或泛化。
3. 未做正式统计检验，不得写"显著优于"或"泛化能力更强"；`shuffle_p=0.0` 只是该格置换检验的结果。
4. `results/pilot-v1` 全程零触碰：无任何文件 mtime 晚于 `2026-10-10T11:04:48+08:00`，冻结 `metrics.json` sha256 仍为 `b2b3ac6bc37c410841bdcbbd968159246e1990db47d02b8fa11844527d66c725`。本次未删除、未覆盖任何既有结果。
5. 已知项（外部审阅第二/三轮记录，非缺陷）：`manifest.json` 的 `script_sha256` 记的是**补丁后**源码哈希（`c56d3ee7…`），与冻结的 `6582d873…` 不同属正确行为；`inputs` 仍登记从未读取的 `local_zebrafish_s.h5ad`（观感项）。顶层 `predictions.json` / `confusion.json` 与原生文件**逐字节相同**：`json.dumps` 默认不产生换行符，`write_text` 的换行翻译对不含 `\n` 的内容是恒等变换；实测四个文件 CR=0、LF=0，SHA 两两相同。（先前记录的"CRLF 翻译导致非字节相同"是**运行前推测**，已被运行后实测证伪，见下方"更正"。）

## 结论

本地统一评分器在 `human→mouse` / `coarse` 上**完全复现**冻结数字：16/16 检查通过，混淆矩阵与逐细胞预测表与冻结产物逐字节相同。该格可标记为 **`confirmed-for-recompute`**。

这不升级为泛化证据，也不改变任何其他格的现有口径。

## 更正（外部审阅 Task 1 结果时提出，2026-10-10）

**D1（实质性，已改）**：本报告初版把顶层 `predictions.json` / `confusion.json` 写成"`write_text` 副本、Windows 下 LF→CRLF、与原生文件非字节相同"。这是**运行前的推测**（源自 Phase 0 阶段的 O2 观察，当时 A-smoke 尚不存在），我把它当成运行后的既成观测照抄，未做复核。

运行后实测：

| 文件 | 字节数 | CR | LF | sha256 |
|---|---|---|---|---|
| `confusion.json` | 809 | 0 | 0 | `167da767…` |
| `confusion/coarse_human_to_mouse.json` | 809 | 0 | 0 | `167da767…` |
| `predictions.json` | 1283386 | 0 | 0 | `dc729820…` |
| `predictions/coarse_human_to_mouse.json` | 1283386 | 0 | 0 | `dc729820…` |

四个文件**逐字节相同**。原因：`json.dumps` 默认不产生换行符，整文件不含 `\n`，因此 `write_text` 的换行翻译是**恒等变换**——"LF→CRLF"从前提上就不成立。本报告初版在同一句话里引用的 `sha256.tsv` 本就给顶层与子目录两行记了同一个哈希，属自我矛盾。

**D2（计数，已改）**：初版写"12 个文件"却列了 13 行。磁盘实际 **13** 个文件 = 12 个被哈希 + `sha256.tsv` 自身；日志里的 `files_hashed=12` 说的是被哈希数，两个口径被混用。

**D3（计数，已改）**：初版 §最强证据 写"混淆矩阵与 **1505** 条逐细胞预测（含 `neighbor_barcodes`）"。预测表实际是 **1535** 行：`"prefixed_barcode"` / `"neighbor_barcodes"` 各出现 1535 次，`"included": true` 1505、`"included": false` 30（30 条 `exclusion_reason: mapping_status:unmapped`）。1505 是 `n_q`（被计分数），1535 是 `n_q_total`（文件行数），本报告 §验证 本就把两者并列写对，属同一类"两个计数口径混用"。冻结件同为 1535 行，与 `docs/evidence/metric-calculation-examples-20261008.md` 的既定口径一致。

三处均属报告文本错误，**不影响任何数字结论**。修正后已对全文所有计数类断言逐一复核：13 个文件、12 个被哈希、`sha256.tsv` 12 数据行、混淆矩阵 28 条、`n_q` 1505、`n_q_total` 1535、对角和 1297、16/16 检查、两个冻结 SHA —— 全部与磁盘和冻结登记值一致。哈希、逐字节等同、16/16 检查、四处协议哈希同值、`pilot-v1` 零触碰均经外部审阅独立重算确认成立。

## 下一步门

本阶段报告需再次交 Claude/Flash 反方复审。通过后才进入 Task 2（A 档全量本地复算）；且按 `20261010-baseline.md` 的"覆盖风险"一节，Task 2 之前必须先给全量模式提供隔离输出（`--out` 参数或等价副本），否则不得运行。
