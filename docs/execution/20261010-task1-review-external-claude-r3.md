I have completed all checks. Here is my independent verification.

## 1. D3 correction + §更正 D1/D2/D3

**D3 — 改对了。** `docs/execution/20261010-task1-a-smoke-report.md:84` 现读作"**1535 条**逐细胞预测（含 `neighbor_barcodes`；其中 1505 条被计分，30 条因 `mapping_status:unmapped` 排除）"，并把"完全一致"收紧为"**与该格**在六方向全量运行中的产出**逐字节一致**"。实测 `predictions.json`：数组长度 **1535**，`included:true` **1505**、`false` **30**，唯一 `exclusion_reason = mapping_status:unmapped`，全部记录都带非空 `neighbor_barcodes`。

**D1 — 与实测相符。** 四个文件 `confusion.json` / `confusion/coarse_human_to_mouse.json` / `predictions.json` / `predictions/coarse_human_to_mouse.json` 全部 **CR=0、LF=0**，SHA 两两相同（`167da767…`、`dc729820…`）。

**D2 — 与实测相符。** `A-smoke/` 磁盘 **13** 个文件；`sha256.tsv` = 1 表头 + **12** 数据行。

**D3 — 与实测相符**（见上），且与 `docs/evidence/metric-calculation-examples-20261008.md:17`（"1535 个预测"）、`:20-22`（n_q=1505、coverage=1505/1535）既定口径一致。

## 2. 逐数字重算（全部与磁盘/冻结登记一致）

| 断言 | 实测 |
|---|---|
| A-smoke 文件数 | 13（`find` 全树） |
| 被哈希 / `sha256.tsv` 数据行 | 12 / 12 |
| §产物 13 行字节数 | 14502/92/262/660/2414/1217/809/1283386/1118/2718/7231/809/1283386 — 逐行相符 |
| 混淆矩阵条目 / 总和 / 对角和 | 28 / 1505 / 1297 |
| `acc,majority,shuffle_p` | 0.8618 / 0.4817 / 0.0（= frozen 同格） |
| `n_ref,n_q,n_q_total,coverage_q` | 1528 / 1505 / 1535 / 0.9805 |
| `n_perm,shared_genes` | 200 / 15869 |
| 独立校验 | round(1297/1505,4)=0.8618；acc·n_q=1297.009，差 0.009；frozen 同 |
| 16 项检查 | `verification.json` 16 项全 `ok:true`、`failed_checks:[]` |
| 四处协议哈希同值 | `c56d3ee7…` 出现在 `manifest.script_sha256`、`sha256.tsv` 的 `_patched_source.py` 行、`environment.txt`、`wrapper-provenance.json` |
| 权威源码 / 冻结 manifest `script_sha256` | `scripts/ortholog_pca_local_v1.py` = `6582d873…` = frozen manifest 记录值 |
| 两个冻结 SHA | `confusion/coarse_human_to_mouse.json`=`167da767…`、`predictions/coarse_human_to_mouse.json`=`dc729820…`，且 = `baseline/input-sha256.tsv:4-5` |
| A-smoke vs frozen metrics SHA | `e13a2bdb…` ≠ `b2b3ac6b…`（frozen 18 格，A-smoke 1 格） |
| 预检 | `wrapper-provenance.json` 15 项全 ok（15/15） |
| 补丁 | `patch_count:6`，P1–P6 名称相符 |
| 日志交叉 | `human 1528×32732`、`mouse 1535×32379`、`mapping rows=38`（TSV 1 表头+38 行）、`files_hashed=12`、`acc=0.8618`、`elapsed=9.8s` 全部吻合 |
| 代码事实 | `ortholog_pca_local_v1.py:254,258,265-266` 确在方向循环内（`vstack`→`PCA().fit_transform`→`knn.fit`），支撑"按方向单独拟合/训练" |

## 3. 新错误扫描 — 未发现

全文逐句核对：无与磁盘、与冻结登记值、或与报告内部其他句子相矛盾的陈述。唯一无法由产物独立复现的是 `:17` "**10.5 s（端到端）**"（artifacts 只记录脚本内 9.8 s、wrapper 9.9 s、manifest 起止 33→43 s）；这是外部计时值，与其它数值不矛盾，**不构成缺陷**，仅记录为不可复算项。

## 4. 越界表述 — 干净

全文命中"显著/泛化/inductive/跨方法"仅 4 处，全是否定式免责（`:98-100`、`:108`）。`:106` 只给 `confirmed-for-recompute` 复算级标签。无一处把该单格 transductive 结果说成 inductive / 泛化 / 跨方法，也无无检验支撑的"显著"。

## 5. pilot-v1 冻结 — 零触碰

- `find results/pilot-v1 -newermt "2026-10-10 11:04:48"` → **0 个文件**（全树最大 mtime = `samap-v98/.../exact_zf--hu.json`，2026-10-05T01:12:04）。
- `ortholog-pca-v98/metrics.json` sha256 = `b2b3ac6bc37c410841bdcbbd968159246e1990db47d02b8fa11844527d66c725` — **未变**。

（全程只读：仅 `sha256sum`/`find`/`grep`/`tr`/`wc`/`cat`/`head`/`sed` 与纯内存 JSON 解析；未创建、修改、删除、移动任何文件，未 commit/push，未触碰 DCS/GPU/训练。）

verdict: PASS
