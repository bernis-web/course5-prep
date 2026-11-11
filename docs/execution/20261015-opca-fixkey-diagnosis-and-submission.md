# oPCA 口径分歧诊断与修正版提交（2026-10-15）

> ⚠️ **本节数字已作废（2026-11-11 标注）**：见 `docs/reports/number-index-20261111.md` 与 `docs/execution/20261108-更正索引.md`。本文件按当时口径保留，不回改。

> 背景：DCS 全量复算任务 `W202610110124739` 完成后，与冻结件核对 100/127，含斑马鱼方向全部有差异。
> 本文件记录根因诊断（**两个独立 bug**）、修正版脚本构建与提交、以及监督状态。
> 全程只读核对冻结件；新产物写入新目录/新任务，不覆盖任何既有结果。

---

## 一、诊断结论：两个独立的 bug

### Bug 1（权威脚本）：人-鱼/鼠-鱼映射键方向错配

`scripts/ortholog_pca_local_v1.py` 的 `parse_orthologs()`：

```python
fh = one_to_one(zfin(ORTH_DIR / "human_orthos.txt"))   # 键 = 鱼基因符号, 值 = 人基因符号
...
MAPS = {..., ("human", "zebrafish"): fh, ...}          # 却当作 human->zebrafish 用
```

循环里 `su`（鱼符号）去查 **human** 的基因集、`tu`（人符号）去查 **zebrafish** 的基因集。

**后果**：只有"两物种 var 里恰好出现同名符号"的基因对能侥幸入选，而符号不同步的真实直系同源对（如 `PPARD` ↔ `PPARDB`）两端都找不到、被系统性丢弃。

实测（当前输入，权威脚本自身逻辑）：

| 方向 | 权威口径 | 语义正确口径 | 差 |
|---|---|---|---|
| human→zebrafish | 9,131 | 9,311 | +180 |
| mouse→zebrafish | 7,670 | 8,160 | +490 |

- 权威口径 9,131 对中 **9,130 对是"两物种符号同名"**（仅 1 对异名）
- 语义正确口径多出的 181 对全部是**真实异名同源对**（`ABCA3↔ABCA3B`、`ATP1A2↔ATP1A2A`、`BID↔BIDA` …）
- 人-鼠方向不受影响（`hm` 的键值同源符号一致，15,869 对两口径相同）

**GenPilot 独立复核结论（2026-10-15）**：Q1「是真实 bug」——"权威脚本 `fh` 键=鱼符号、值=人符号（fish→human 方向），语义本身没错；错在 MAPS 中 `("human","zebrafish"): fh` 直接使用"。

### Bug 2（平台脚本）：重复基因名取"末次列"而非"首现列"

`ortholog_pca_dcs_v2.txt`（SHA `05aa4a23…`）：

```python
"var_idx": {g: i for i, g in enumerate(var_up)},   # 重复符号保留最后一次出现的列索引
```

权威脚本用的是**首现去重**（注释明确：*Deterministic first-occurrence dedup AFTER full-space normalisation, so per-cell normalisation denominators stay protocol-exact*）。

**斑马鱼有 142 个重复基因名（284 列）**，且重复符号的两列**表达值不同**：

| 基因 | 首现列 | 末次列 |
|---|---|---|
| `RPS17` | 列 4（sum=10,855） | 列 136（sum=18,296） |
| （其余 141 个同理） | — | — |

涉及共享集的重复符号数：human→zebrafish **62 个**、mouse→zebrafish **56 个**、人-鼠方向 **0 个**。

→ 即使基因集相同（都是 9,311 / 8,160），PCA 输入矩阵仍不同 → acc 不同。

### 两个 bug 的独立性（关键）

| | 权威脚本 | 平台脚本 v2 | 平台 v3_fixkey |
|---|---|---|---|
| 键方向 | ❌ 错（鱼当人） | ✅ 对 | ✅ 对 |
| 去重列 | ✅ 首现 | ❌ 末次 | ✅ 首现 |

→ 两者各自错在不同的地方，所以「权威 vs 平台 v2」的差异是**两个 bug 叠加**的结果。

---

## 二、三方数字对照（本地实测）

| 方向 | 层级 | 冻结（权威，双bug） | 平台 v2（仅去重bug） | 本地 FIXKEY（双修正） |
|---|---|---|---|---|
| human→mouse | exact | 0.7824 | 0.7824 | 0.7824 |
| human→mouse | coarse | 0.8618 | 0.8618 | 0.8618 |
| human→mouse | fine | 0.7980 | 0.7980 | 0.7980 |
| mouse→human | exact | 0.4084 | 0.4084 | 0.4084 |
| mouse→human | coarse | 0.7369 | 0.7369 | 0.7369 |
| mouse→human | fine | 0.4103 | 0.4103 | 0.4103 |
| human→zebrafish | exact | 0.1698 | 0.1529 | **0.1504** |
| human→zebrafish | coarse | 0.1961 | 0.1801 | **0.1795** |
| human→zebrafish | fine | 0.1801 | 0.1648 | **0.1608** |
| mouse→zebrafish | exact | 0.1659 | 0.1581 | **0.1640** |
| mouse→zebrafish | coarse | 0.2755 | 0.2608 | **0.2675** |
| mouse→zebrafish | fine | 0.1748 | 0.1661 | **0.1721** |
| zebrafish→human | exact | 0.1453 | 0.1374 | **0.1387** |
| zebrafish→human | coarse | 0.1813 | 0.1728 | **0.1734** |
| zebrafish→human | fine | 0.1695 | 0.1597 | **0.1610** |
| zebrafish→mouse | exact | 0.4769 | 0.4717 | **0.4710** |
| zebrafish→mouse | coarse | 0.5761 | 0.5754 | **0.5814** |
| zebrafish→mouse | fine | 0.5010 | 0.4977 | **0.5003** |

**人-鼠 6 格三方完全一致**；含斑马鱼 12 格三方各不相同（三套 bug 组合）。

shared_genes：

| 方向 | 冻结 | 平台 v2 | FIXKEY |
|---|---|---|---|
| human→mouse | 15,869 | 15,869 | 15,869 |
| human→zebrafish | 9,131 | 9,311 | 9,311 |
| mouse→zebrafish | 7,670 | 8,160 | 8,160 |

---

## 三、修正版脚本

### 本地版（我方构建）

- 路径：`scripts/ortholog_pca_dcs_v3_fixkey.py`
- SHA-256：`f9683cf95b3eef61c75f68f4f169118b5deb3c935a6f0e108708a3388d84a9c5`
- 382 行；基线 = 权威脚本 `6582d873…`，12 个补丁（1 个语义修正 + 11 个平台适配）
- 本地实跑验证：基因集 9,311 / 8,160；人-鼠 acc 不变（0.7824/0.8618/0.7980）；耗时 30.3s

### 平台版（GenPilot 构建并提交）

- 平台路径：`/Files/ResultData/Notebook/ortholog_pca_dcs_v3_fixkey.txt`
- SHA-256：`514d931487f80fd7bfd6152c64729a960a0e5d566552087dceaafb6a0f77ee16`（17,382 B）
- 基线 = 平台脚本 `05aa4a23…`，仅 2 处改动：
  1. `var_idx` 末次列 → **首现列**（`_seen`/`_vidx` 显式去重，X 不裁剪、索引直指原始列）
  2. manifest 新增 `"variant": "FIXKEY-equiv: first-occurrence gene dedup + correct zebrafish mapping orientation"`
- 我方独立下载核对：SHA 与 GenPilot 报告一致；diff 仅上述 2 处（`242a243,246` / `245c249` / `394a399`）

> **核实要点**：平台版**未改键方向**——因为平台脚本的键方向本来就是对的（`h2f.setdefault(hh, ...)` 中 `hh` 是人基因）。
> 两个 bug 的独立性在此得到确认。

### 两版实现差异（已评估）

| 项 | 本地 FIXKEY | 平台 v3_fixkey |
|---|---|---|
| 基线 | 权威脚本 | 平台脚本 |
| KNN | `sklearn.KNeighborsClassifier(metric="cosine", weights="distance")` | 自定义 `knn_cosine_vote()`（手写 cosine + 逆距离加权） |
| 基因列裁剪 | `X[:, keep_cols]` 显式裁剪 | X 不裁剪，索引指向首现列 |
| 输出布局 | 18 预测 + 18 混淆（方向×层级） | 6 预测 + 6 混淆（每方向一文件，内含三层） |

**人-鼠方向三方数字完全一致**（0.7824/0.8618/0.7980），说明 KNN 实现等价、裁剪方式等价。
斑马鱼方向的差异（本地 0.1504 vs 平台 v2 0.1529）预期将由首现去重修正收敛。

---

## 四、任务提交与监督

| 项 | 值 |
|---|---|
| 任务号 | **`W202610150090794`** |
| 提交时间 | 2026-10-15 15:47–15:48 |
| 流程 | WDL `opca_v2` v1.0.0 |
| 资源 | 2c8g（CPU） |
| 脚本输入 | `/Files/ResultData/Notebook/ortholog_pca_dcs_v3_fixkey.txt`（`514d9314…`） |
| pylibs | `/Files/ResultData/Notebook/pylibs_full.tar.gz`（不变） |
| 输出 | `./opca-fixkey-20261015T074740Z` |
| cromwell | `Q2-2026-10-15T15-50-03`，1 attempt 登记 |
| 首次检查（15:58） | **waiting**，无 biocStartTime，0 计费 |
| 监督方式 | GenPilot 定时检查（每 10 分钟，最多 2 轮；超窗即停） |

**纪律**：只投一次；失败/Pending 超窗/OOM/非 0 退出 → 停止报告，不重投、不加资源、不充值。

### 验收标准（任务完成后）

1. `metrics.json` 中 human→zebrafish / mouse→zebrafish 的 exact/coarse/fine acc
   应等于本地对照：`0.1504 / 0.1795 / 0.1608` 与 `0.1640 / 0.2675 / 0.1721`
2. `shared_genes` 应为 9,311 / 8,160
3. `manifest.variant` 应含 `FIXKEY-equiv`
4. 人-鼠方向应保持 0.7824 / 0.8618 / 0.7980（不受影响）

---

## 五、边界声明

- 本次**未修改**任何冻结件（`results/pilot-v1` 零触碰）
- 未覆盖任何既有产物；新任务输出写入平台新目录
- 未读取、未记录任何 token/凭据值（下载全程在页面上下文内构造请求）
- 本地实跑仅用于验证（30.3s，CPU 秒级），**未在本地做正式运算**
- 新增文件：`scripts/ortholog_pca_dcs_v3_fixkey.py`（本地 FIXKEY 变体）
