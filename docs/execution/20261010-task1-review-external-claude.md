我已完成独立重算。**未创建/修改任何文件**（我自己的只读自检：评审期间仓库内最后一次写入是 16:41:44，全部来自执行者会话；我开工后零写入）。未重跑评分器——重跑会写文件，违反只读边界；取而代之的是"产物字节级等同冻结件 + 补丁链可重建"这一更强证据。

---

## 1. A-smoke 全树 sha256 独立重算

`Get-ChildItem -Recurse -File | Get-FileHash -Algorithm SHA256`，13 个文件全部重算。`sha256.tsv` 的 **12 行逐行全部命中**（path / size / sha256 三元组无一不符）：

`_patched_source.py` c56d3ee7… ✓ · `command.txt` 0e274240… ✓ · `confusion/coarse_human_to_mouse.json` 167da767… ✓ · `confusion.json` 167da767… ✓ · `environment.json` 8553c1c7… ✓ · `environment.txt` ba164078… ✓ · `manifest.json` fd728236… ✓ · `metrics.json` e13a2bdb… ✓ · `predictions/coarse_human_to_mouse.json` dc729820… ✓ · `predictions.json` dc729820… ✓ · `verification.json` 46ab9a2c… ✓ · `wrapper-provenance.json` 17f6bf89… ✓

（`sha256.tsv` 自身不在表内，符合预期。）

## 2. "逐字节相同"独立验证 —— 成立

| 文件 | A-smoke | 冻结 `ortholog-pca-v98/` | baseline `input-sha256.tsv` |
|---|---|---|---|
| `confusion/coarse_human_to_mouse.json` | 809 B / 167da767… | 809 B / 167da767… | 167da767…（`opca-confusion-smoke`）✓ |
| `predictions/coarse_human_to_mouse.json` | 1283386 B / dc729820… | 1283386 B / dc729820… | dc729820…（`opca-predictions-smoke`）✓ |

字节数、哈希、冻结登记值三者一致。**"逐字节相同"属实。**

## 3. 16 项检查独立重算 —— 16/16 复现，0 失败

从 A-smoke `metrics.json` 与冻结 `ortholog-pca-v98/metrics.json` 取 `human->mouse`/`coarse` 自行比对（浮点先 `round(x,4)` 再比，容差 1e-12）：

- 9 个字段 `acc 0.8618` / `majority 0.4817` / `shuffle_p 0.0` / `n_ref 1528` / `n_q 1505` / `n_q_total 1535` / `coverage_q 0.9805` / `n_perm 200` / `shared_genes 15869` —— **abs_diff 全为 0**。
- `confusion:identical`：两侧各 28 条，字典相等 → True。
- 从 A-smoke 混淆矩阵独立重算：条目总和 `1505 == n_q 1505` ✓；`diag 1297`，`round(1297/1505,4)=0.8618 == acc` ✓；`|0.8618*1505 − 1297| = |1297.009 − 1297| = 0.009 < 0.5` ✓；`diag 1297 == 冻结 diag 1297` ✓；冻结侧 `round(1297/1505,4)=0.8618 == 冻结 acc` ✓。
- `n_perm = 200`（manifest/scope 亦记 200），**不是 smoke 的 20** ✓。

## 4. 协议保真 —— 四处同值成立，且补丁链可重建

- `scripts/ortholog_pca_local_v1.py` sha256 = `6582d873…` **== 冻结 `ortholog-pca-v98/manifest.json` 的 `script_sha256`** ✓
- `c56d3ee7…` 在**四处同值**：A-smoke `manifest.json:script_sha256`、`sha256.tsv` 的 `_patched_source.py` 行、`environment.txt:patched_source_sha256`、`wrapper-provenance.json:patched_source_sha256` ✓
- **额外加验**（超出要求）：我把 `wrapper-provenance.json` 里记录的 6 个 unified-diff hunk **纯内存重放到权威源码**上，重建结果 sha256 = `c56d3ee7…`，与磁盘上的 `_patched_source.py` **完全一致**。即补丁后源码确系"权威源码 + 恰好这 6 处改动"，无夹带。
- 6 处改动（BASE 作用域、LEVELS、main() 输出目录/smoke 分支、物种循环、MAPS 方向表、打印语句）**均未触碰**归一化、基因去重、PCA 参数（`PCA(n_components=NPCS, random_state=SEED)`）、KNN 参数（`KNeighborsClassifier(n_neighbors=K, metric="cosine", weights="distance")`）、NPERM 数值。报告 §94 属实。

## 5. 边界 —— 零触碰成立

- `results/pilot-v1` 共 196 个文件，**mtime 晚于 `2026-10-10T11:04:48+08:00` 的文件数 = 0** ✓
- 冻结 `ortholog-pca-v98/metrics.json` sha256 仍为 `b2b3ac6bc37c410841bdcbbd968159246e1990db47d02b8fa11844527d66c725` ✓（与 baseline 登记值一致）
- 三个冻结目录清单与 baseline 声明**逐一相符**：ortholog-pca-v98 40 文件/18098994 B、samap 21/12730056、saturn 34/350869 —— 无增无减。

## 6. 报告越界表述审查 —— 无越界

`显著 / inductive / 泛化 / 跨方法 / 优于` 等词**仅出现在 §边界与限制 与 §结论 的否定句里**（第 98–100、108 行），全部是"不构成/不升级"的免责表述。§84 关于"PCA 按方向拟合、KNN 按方向训练"的说法我核对了 `scripts/ortholog_pca_local_v1.py:254,258,265-266`，属实。§106 结论限定在"该格可标记为 confirmed-for-recompute"。**未发现任何把单格 transductive 结果说成 inductive/泛化/跨方法的表述，也未发现无检验支撑的"显著"。**

---

## 与报告不符之处（2 处，均为报告写错，非算法差异）

**D1 — 实质性：报告 §边界与限制 第 5 条末句为事实错误。**
报告称顶层 `predictions.json` / `confusion.json` 是 `write_text` 副本、"Windows 下 LF→CRLF"、"与原生文件**非字节相同**"。实测（直接字节比较 + 原始 CR/LF 计数）：

```
confusion.json                       809 B  CR=0 LF=0   sha 167da767…
confusion/coarse_human_to_mouse.json 809 B  CR=0 LF=0   sha 167da767…   equal_bytes=True
predictions.json                 1283386 B CR=0 LF=0   sha dc729820…
predictions/coarse_..._mouse.json 1283386 B CR=0 LF=0  sha dc729820…   equal_bytes=True
```

**四个文件零 CR、零 LF，逐字节相同。** 原因是这两个 JSON 由 `json.dumps` 默认分隔符产出，**整文件不含任何换行符**，`write_text` 的 newline 翻译对无 `\n` 的内容是恒等变换——"LF→CRLF"从前提上就不成立。更直接的是：报告同一句话里引用的 `sha256.tsv` **本身**给顶层与子目录两行记的就是**同一个哈希**，报告自我矛盾。

溯源：该说法来自 `results/phase-20261010/review-gate-status.json` 的 `O2`，而 O2 是在 Phase 0 写下的——同文件 `task1_wrapper.output_dir_exists: false`，即**运行时该文件尚不存在**，O2 是运行前的推测，报告把它当作"外部审阅第二/三轮记录"的既成观测照抄，未做运行后复核。**报告错，我的测量成立。**

**D2 — 计数小错：** 报告 §产物 写"`A-smoke/`，12 个文件"，其下列了 **13** 行；磁盘实际 **13** 个文件（12 个被哈希 + `sha256.tsv` 自身）。日志 `files_hashed=12` 说的是被哈希数，报告混用了两个口径。

---

**结论：Task 1 的实质结果我独立复现，全部成立**（12/12 哈希、逐字节等同、16/16 检查、四处协议哈希同值、pilot-v1 零触碰、报告无越界）。**但报告文本含 1 处可被其自身证据直接证伪的字节级陈述（D1）**——按本项目既定门槛（F1 的哈希标注不一致、C4 的自条目不一致均判 REVISE），且该错误会向下游传播，需一行更正后重审。修复不影响任何数字结论。

verdict: REVISE
