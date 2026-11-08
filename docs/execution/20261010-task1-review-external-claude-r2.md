## 1. D1 / D2 更正核对

**D1 —— 改对了。** `docs/execution/20261010-task1-a-smoke-report.md:102`（§边界与限制 第 5 条）与 `:110-123`（§更正）现在写"逐字节相同"，我实测复核：

| 文件 | 字节 | CR | LF | sha256 |
|---|---|---|---|---|
| `A-smoke/confusion.json` | 809 | 0 | 0 | `167da767…3580d` |
| `A-smoke/confusion/coarse_human_to_mouse.json` | 809 | 0 | 0 | `167da767…3580d` |
| `A-smoke/predictions.json` | 1283386 | 0 | 0 | `dc729820…f10847` |
| `A-smoke/predictions/coarse_human_to_mouse.json` | 1283386 | 0 | 0 | `dc729820…f10847` |

四个文件 CR=0 / LF=0，SHA 两两相同 → "`json.dumps` 不产生换行符、`write_text` 换行翻译为恒等变换"成立。更正表里四个哈希与字节数逐格对得上，无新错。同时 `sha256.tsv` 确实给顶层与子目录各记了同一个哈希（`167da767…` 两行、`dc729820…` 两行），"初版自我矛盾"的说法属实。

**D2 —— 改对了。** `A-smoke/` 磁盘实际 **13** 个文件（`_patched_source.py`、`command.txt`、`confusion.json`、`environment.json`、`environment.txt`、`manifest.json`、`metrics.json`、`predictions.json`、`sha256.tsv`、`verification.json`、`wrapper-provenance.json` + `confusion/`、`predictions/` 各 1）；`sha256.tsv` 共 13 行 = 1 表头 + **12** 数据行。§产物 的 13 行清单文件名与字节数逐行与磁盘一致。

`preflight.md:59` 与 `review-gate-status.json` 的 O2 字符串均已改为"推测已被实测证伪"，与实测相符，未留旧口径。

## 2. 我的独立重算

- 文件计数 13、`sha256.tsv` 数据行 12 —— 见上。
- 协议哈希四处同值复核通过：`manifest.json.script_sha256`、`sha256.tsv` 的 `_patched_source.py` 行、`environment.txt` 的 `patched_source_sha256`、`wrapper-provenance.json` 的 `patched_source_sha256` **全为 `c56d3ee7…6ba55`**，与 `_patched_source.py` 磁盘哈希一致；权威源码 `scripts/ortholog_pca_local_v1.py` = `6582d873…0c44` = 冻结 manifest 的 `script_sha256`。
- `A-smoke/metrics.json` = `e13a2bdb…`（≠ 冻结 `b2b3ac6b…`，报告解释为"只含 1 格"属实）；混淆矩阵 28 条、总和 1505、对角和 1297；`verification.json` 16 项检查全 `ok:true`、`failed_checks: []`。
- 报告引用的 `baseline/input-sha256.tsv:4-5` 两个值确为 `167da767…` / `dc729820…`。

## 3. 越界表述扫描 —— 干净

全文命中"显著/泛化/inductive/跨方法/证明/优于"仅 4 处，全部是**否定式免责**（`:98-100`、`:108`），无一处把该格说成 inductive、泛化或跨方法结论，也无无检验支撑的"显著"。`:106` 只给 `confirmed-for-recompute` 这一复算级标签。

## 4. `results/pilot-v1` 冻结 —— 未触碰

- mtime 晚于 `2026-10-10T11:04:48+08:00` 的文件：**0**（全树 196 个文件；最大 mtime = `samap-v98/wdl-run/extracted/exact_zf--hu.json`，`2026-10-05T01:12:04`）。
- `ortholog-pca-v98/metrics.json` sha256 = `b2b3ac6bc37c410841bdcbbd968159246e1990db47d02b8fa11844527d66c725` ✔ 未变。

## 5. 但发现一处**残留计数错误**（非本次改动引入，但仍在报告正文里）

`20261010-task1-a-smoke-report.md:84`：

> 即：在只看 human+mouse 的隔离运行里，混淆矩阵与 **1505 条**逐细胞预测（含 `neighbor_barcodes`）与六方向全量运行产出完全一致

该句描述的正是上一段表格里那个 `predictions/coarse_human_to_mouse.json`（1,283,386 B）。该文件实际是 **1535** 行逐细胞预测，不是 1505。两种独立方法互证：

- 文本级计数：`"prefixed_barcode"` 出现 **1535** 次、`"neighbor_barcodes"` **1535** 次、`"included": true` **1505**、`"included": false` **30**（30 条 `exclusion_reason: mapping_status:unmapped`，且这 30 条同样带非空 `neighbor_barcodes`）。冻结件同样 1535。
- `ConvertFrom-Json` 数组长度 1535（A-smoke 与冻结件一致）。

所以"1505"与"（含 `neighbor_barcodes`）"两处都站不住：1505 是 `n_q`（被计分数），1535 才是 `n_q_total`（文件行数）——本报告 `:62-63` 自己就把这两个数并列写对了。项目既有文档 `docs/evidence/metric-calculation-examples-20261008.md:17` 也写"`knn.predict(...)` → **1535 个预测**"，即 1535 是本项目对该产物的既定口径。

这与第一轮 D2 属同一类错误（两个计数口径被混用），同样只影响报告文本、不影响任何数字结论。最小修法：把"1505 条逐细胞预测"改为"**1535** 条逐细胞预测（其中 1505 条被计分）"，或在 §更正 里作为 D3 记录一句。

D1/D2 本身改得干净，第 3、4 项也全部通过；但正文仍留有一句与产物和本项目既定口径都不符的计数陈述，故不能判 PASS。

verdict: REVISE
