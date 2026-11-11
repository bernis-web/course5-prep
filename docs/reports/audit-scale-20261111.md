# 全量数据规模核算：子集 4,606 vs DCS 全量 140,471

- 生成时间：2026-11-11
- 核算范围：HEART 课程数据三物种（人 / 鼠 / 斑马鱼）心脏单细胞
- 复核脚本：`tmp/audit_subset_inspect.py`、`tmp/audit_class_table.py`、`tmp/audit_scale_calc.py`（本报告所有算术都由这三个脚本产出，不手算）
- 一句话结论：**规模差 30.5 倍（每物种 19.6–39.4 倍），全量重跑单 seed 约 ¥180–320，其中 GPU（SATURN）占 85% 以上；结论方向不会翻转，但所有绝对数值不能沿用，CI 也不会像 √30 那样收窄。**

---

## 摘要（12 行内可引用）

| # | 事实 | 值 | 性质 |
|---|---|---|---|
| 1 | 子集细胞数（实测读 h5ad） | 1,528 / 1,535 / 1,543 = **4,606** | 实测 |
| 2 | 全量细胞数（平台文件 n_obs） | 30,000 / 60,471 / 50,000 = **140,471** | 实测（2026-09-20 anndata 读取） |
| 3 | 差距 | 19.6× / 39.4× / 32.4×，合计 **30.5×**（1.3–1.6 个数量级） | 计算 |
| 4 | 标签空间 | 12 / 12 / 14 类，**子集与全量完全一致** | 实测 |
| 5 | 稀有类被过采样 | 3.56–5.00 倍（子集稀有类占比 8.7–9.8%，全量 1.7–2.8%） | 计算 |
| 6 | oPCA 全量 | 7.3 h，内存峰值 **≈39 GB**（必须 32c128g），¥22–87 | 外推（线性） |
| 7 | scVI 全量 | 6.5 h @2c8g，内存 **≈5.7 GB**，¥4.8（32c 档 ¥19） | 外推（幂率 0.95，有 5.6 万细胞实测锚） |
| 8 | SAMap 全量 | 3.0 h @1c4g，¥2.0（线性上限） | 外推 |
| 9 | SATURN 全量 | 5–6 h GPU（3080Ti×1），**¥154–185** | 外推（1c4g 实测 + GPU 加速比） |
| 10 | 单 seed 全量总费用 | **¥180–320** | 外推合计 |
| 11 | 3 seed 总费用 | **¥550–960** | 外推 |
| 12 | 结论会不会变 | 方向不变、数值全废、CI 收窄幅度远小于 √30.5 | 判断 |

---

## ① 全量数据事实核查（出处 + 可信度）

### 1.1 逐条出处

| # | 主张 | 值 | 出处（文件:行） | 原文摘录 | 可信度 | 判据 |
|---|---|---|---|---|---|---|
| A1 | 全量 n_obs | 30,000 / 60,471 / 50,000 | `docs/heart-inspect-evidence-20260920.json:9` / `:277` / `:1201` | `"n_obs": 30000,` … `"n_obs": 60471,` … `"n_obs": 50000,` | **A（最硬）** | 直接由 anndata 读 `n_obs`，同文件含 sha256 + size + 逐列 value_counts |
| A2 | 同上（叙述版） | 同上 | `docs/dcs-readonly-audit.md:112` | 「三文件全部可读…关键事实：n_obs=30000/60471/50000，n_var=32732/32379/27661，X 均 float32」 | A | 与 A1 同一批证据的 prose 版 |
| A3 | 同上（日志版） | 同上 | `docs/ai-use-log.tsv:31` | 「n_obs 30000/60471/50000, gold label column celltype shared across files」 | A | 操作日志，同日同脚本 |
| A4 | 全量路径 | `/Files/3/stage3/01_raw_data/heart_omics/scrna/` | `docs/execution/20261104-队友交接总纲.md:255-257` | 「`/Files/3/stage3/…/Homo_sapiens_sc.h5ad`｜人 心脏单细胞（全量）｜223,744,070 B（213.38 MiB）｜**全量原始数据首选路径**」 | **B（路径）/ A（字节数）** | 字节数与 A1 的 `size` 字段逐字节一致；路径本身是 2026-11-08 只读 `ls` 实测（`docs/reports/report-09-corrections-20261108.md:111`） |
| A5 | 旧路径作废 | `/Files/RawData/` 已无人/鼠/鱼 | `docs/reports/report-09-corrections-20261108.md:104`、`docs/execution/20261104-队友交接总纲.md:284-285` | 「2026-11-08 在 DCS 上实测（只读 ls）：`/Files/RawData/` 里没有这三个文件」 | **A（实测）** | 只读 ls，两次独立记录一致 |
| A6 | 差距倍数 | 19.6× / 39.4× / 32.4× | `docs/execution/20261111-mainline-reframe.md:51-53` | 「人 30,000 / 1,528 / 19.6×」 | A（计算） | 与 A1 + 本地实测一致 |
| A7 | 「差 2–3 个数量级」已作废 | 实为 20–40 倍 | `docs/execution/20261111-obsolete-numbers.md:130-136` | 「差距：**20–40 倍（1.3–1.6 个数量级）**」 | A | 同一表格内自证 |
| A8 | 教师版口径 | 同上 | `docs/reports/20261111-memo-for-teacher.md:29` | 「全量数据就在平台上（人 30,000 / 鼠 60,471 / 斑马鱼 50,000 细胞），我们只用了 1,528 / 1,535 / 1,543」 | A | 对外文件，与 A1 一致 |
| A9 | 队友通知口径 | 同上 | `docs/teammate-notice-20260920.md:13` | 「细胞数 30,000（人）/ 60,471（鼠）/ 50,000（鱼）」 | A | 上传当天口径 |
| A10 | 全量单物种 scVI 已跑过 | 30,000 / 60,471 / 50,000 | `docs/heart-pilot-scvi-baseline-20260921.md:31-33` | 「Homo_sapiens（人）｜30,000｜0.9838｜68.4s｜g3-scvi-baseline-v11-cpu」 | **A（运行时实测）** | 三个任务号可查，32c128g CPU |
| A11 | 全量文件 sha256 | `3c56fd16…` / `b5d69235…` / `76bcd7ae…` | `docs/heart-inspect-evidence-20260920.json`（`sha256` 字段） | —— | B | 自记录、无官方校验和（`docs/ai-use-log.tsv:31` 明写「SHA256 self-recorded (no official checksums)」） |
| A12 | 七鳃鳗跨门 55,694 | 41,678 + 14,016 | `results/phase-20261030/resource-ledger.json:43` | `"cells": 55694`（cross-phylum lamprey/mouse，¥2.06，9773s） | A（运行时实测） | 平台 analyseDuration |
| A13 | 基因轴 | 15,869 / 9,311 / 8,160 | `docs/execution/20261104-队友交接总纲.md:261-263` | 「人鼠 1:1 直系同源…15,869 对」「人鱼…9,311 对」「鼠鱼…8,160 对」 | A | 有 md5 与文件大小 |
| A14 | 论文规模（**不是我们的数据**） | 16 物种 / 479,483 细胞 | `docs/handoff-to-glm-5.3-flash.md:78` | 「论文…作者 SATURN 分析使用 16 个物种、约 479,483 个细胞」 | A（引用） | 这是 SATURN 原文，**不能拿来当本项目全量** |

### 1.2 哪条可信、哪条要打折

1. **`n_obs = 30000 / 60471 / 50000` 是 A 级事实**，三个独立载体（JSON 证据、审计叙述、操作日志）同源同值，且被全量 scVI 任务的运行时又验证了一次（A10 三个任务的输入形状）。
2. **但「全量」这个词有水分，必须加引号。** 30,000 和 50,000 是整齐的整数上界，而人心脏图谱原始发布是数十万级、SATURN 论文用 479,483 细胞（A14）。**推断（非实测）**：人/鱼两个文件是发布方或平台做的**降采样/封顶版**，鼠的 60,471 不是整数，可能是原样。所以本报告里「全量」一律指 **「平台文件内的全量」**，不指「图谱全库」。
3. **路径是一条 B 级事实 + 一次 A 级实测。** 路径本身只有只读 `ls` 实测（2026-11-08），能否在**离线任务容器**内挂载读到这条深路径，仓库里没有单独探过（`/Files/RawData` 在容器内可见是 v9 实测，见 `docs/g2-closure-exceptions-20260921.md:54`）。→ 这就是任务清单里的 **T0**。
4. **sha256 是自记录**，不能用来对外主张"与官方一致"；能主张的是"本地下载件与平台落盘件字节数一致"。

### 1.3 仓库里没有全量原始文件

`local_*.h5ad` 三份在仓库根目录（26.2 / 27.7 / 16.9 MB），全量三份在平台（213.38 / 259.71 / 153.93 MiB）。**仓库内不存在全量副本**，所以本报告对全量的所有断言要么来自平台侧证据文件，要么是外推——没有第三种。

---

## ② 子集 vs 全量对照表

### 2.1 物种级（实测，anndata 0.10.9 backed 读取）

| 物种 | 文件 | 子集细胞 | 全量细胞 | 倍数 | 子集基因 | 全量基因 | 类数（子集/全量） |
|---|---|---|---|---|---|---|---|
| 人 | `local_human_s.h5ad` | 1,528 | 30,000 | 19.63× | 32,732 | 32,732 | 12 / 12 |
| 鼠 | `local_mouse_s.h5ad` | 1,535 | 60,471 | 39.39× | 32,379 | 32,379 | 12 / 12 |
| 斑马鱼 | `local_zebrafish_s.h5ad` | 1,543 | 50,000 | 32.40× | 27,661 | 27,661 | 14 / 14 |
| **合计** | — | **4,606** | **140,471** | **30.50×** | — | — | 38 类格 |

- 子集细胞占比：人 **5.09%**、鼠 **2.54%**、鱼 **3.09%**，合计 **3.28%**。
- **基因轴没缩**（`n_vars` 与全量完全相同）——子集只砍了细胞，这是好消息：基因维度的结论不受规模影响。
- 类数完全相同（`celltype` 列，三文件共有）→ **标签空间不随规模变化**，全量重跑不会引入新类，也不会让某类消失。

### 2.2 子集生成法决定了它「不是随机 1/30 抽样」

`local_regen_subset.py:7-26`：

```python
k = min(len(grp), max(floor, int(N * len(grp) / a.n_obs)))   # 每类至少 floor 个
# stage1: N=3000, floor=50 → stage2: N=1500, floor=30, seed=0
```

两级分层 + 每类下限 30 → **大类的抽样率被压到 4.7% / 2.35% / 2.83%，稀有类被抽走 10%–65%**。

### 2.3 逐类覆盖表（实测：子集行数 vs 全量 value_counts）

**人（12 类）**

| 细胞类型 | 子集 | 全量 | 覆盖率 |
|---|---|---|---|
| Ventricular Cardiomyocyte | 386 | 8,173 | 4.72% |
| Fibroblast | 276 | 5,859 | 4.71% |
| Endothelial cell | 262 | 5,547 | 4.72% |
| Smooth muscle cell | 211 | 4,466 | 4.72% |
| Myeloid | 104 | 2,211 | 4.70% |
| Atrial Cardiomyocyte | 90 | 1,923 | 4.68% |
| Lymphoid | 49 | 1,045 | 4.69% |
| Adipocyte | 30 | 290 | 10.34% |
| Neural cell | 30 | 274 | 10.95% |
| Mast cell | 30 | 85 | **35.29%** |
| Lymphatic Endothelial cell | 30 | 69 | **43.48%** |
| Mesothelial cell | 30 | 58 | **51.72%** |

**鼠（12 类）**

| 细胞类型 | 子集 | 全量 | 覆盖率 |
|---|---|---|---|
| Endothelial cell | 695 | 29,610 | 2.35% |
| Fibroblast | 330 | 14,083 | 2.34% |
| Lymphoid | 128 | 5,447 | 2.35% |
| Smooth muscle cell | 81 | 3,461 | 2.34% |
| Myeloid | 74 | 3,176 | 2.33% |
| Cardiomyocyte | 47 | 2,017 | 2.33% |
| Valve | 30 | 1,016 | 2.95% |
| Neural cell | 30 | 579 | 5.18% |
| Lymphatic Endothelial cell | 30 | 409 | 7.33% |
| Epicardium | 30 | 292 | 10.27% |
| Proliferating cell | 30 | 218 | 13.76% |
| Adipocyte | 30 | 163 | 18.40% |

**斑马鱼（14 类）**

| 细胞类型 | 子集 | 全量 | 覆盖率 |
|---|---|---|---|
| Endothelial cell | 596 | 21,017 | 2.84% |
| Red blood cell | 332 | 11,717 | 2.83% |
| Smooth muscle cell | 136 | 4,804 | 2.83% |
| Ventricular Cardiomyocyte | 89 | 3,174 | 2.80% |
| Fibroblast | 76 | 2,692 | 2.82% |
| Myeloid | 75 | 2,674 | 2.80% |
| Lymphoid | 45 | 1,619 | 2.78% |
| Valve | 30 | 826 | 3.63% |
| Atrial Cardiomyocyte | 30 | 608 | 4.93% |
| Epicardium | 30 | 436 | 6.88% |
| mt | 30 | 208 | 14.42% |
| Orthers | 30 | 165 | 18.18% |
| Perivascular cells | 30 | 46 | **65.22%** |
| Proliferating cell | 14 | 14 | **100.00%** |

### 2.4 三条从表里直接读出来的结论

1. **稀有类被严重过采样**：按「全量 ≤600 细胞」界定稀有类，人 2.59%→子集 9.82%（**3.80×**）、鼠 2.75%→9.77%（**3.56×**）、鱼 1.74%→8.68%（**5.00×**）。
2. **有一个类的样本被抽空**：斑马鱼 `Proliferating cell` 全量只有 14 个，子集拿走 **14/14**。该类在全量下不会有任何"额外样本"，全量重跑对它**一点信息增益都没有**（只有 14 个细胞，F1 的方差照样巨大）。
3. **类别先验会被拉回真实值**：max class share 人 25.3%→27.2%、鼠 45.3%→49.0%、鱼 38.6%→42.0%。→ 全量的多数类基线会**变高**（更多大类样本 → 更容易猜对），而 macro-F1 会因稀有类 F1 下降而**整体下移**。

---

## ③ 算力 / 内存 / 费用估算表

### 3.1 单价口径（先定死，否则费用没法比）

| 档位 | 单价 | 出处 | 性质 |
|---|---|---|---|
| `1c 4g` | ¥0.66/h（¥0.011/分钟） | `docs/evidence/genpilot-consultation-20261009.md:31`「0.18 元 ÷ 16.4 min = 0.011 元/分钟·1c4Gi」 | **外推价**（非官方，已标 provisional） |
| `2c 8g` | **¥0.739/h**（¥0.19 / 926 s） | `results/phase-20261030/resource-ledger.json:18-19` | **实测**（平台 analyseDuration + analysisAmount） |
| `32c 128g` | ¥11.8/h | 按核数线性 ×16 从 2c8g 外推 | **外推**（平台无公开计价接口，`docs/reports/batch-mixing-and-crossphylum-feasibility-20261019.md:535`） |
| `3080Ti×1`（捆绑 88c/320G） | **¥30.78/h** | `docs/dcs-readonly-audit.md:125`「3080Ti×1 捆绑 88c320G（¥30.78/h）」 | **实测口径**（一次 1h 会话 ¥32.42，含 23 分钟排队；平台无公开价） |

> 计费口径提醒：**从提交时刻计费，含排队**（`docs/g2-probe-offline-channel-20260920.md:33`）。GPU 任务排队久，费用会显著高于纯计算时间。

### 3.2 实测锚点（这些是「实测」，不是外推）

| 锚点 | 细胞 × 基因 | 档位 | 时间 | 费用 | 出处 |
|---|---|---|---|---|---|
| oPCA（opca_v2，6 方向，200 置换） | 4,606 × 15,869 | 2c8g | analyse 866 s / billing 926 s | ¥0.19 | `resource-ledger.json:9-22` |
| 同上，本地单进程白盒 | 4,606 × 15,869 | 笔记本 | 26.68 s（中位），峰值 1,307.9 MB | — | `results/resource-20261030/resource_summary.json:4-9` |
| scVI（scvi_cross2） | 4,606 × 9,018 | 2c8g | 916 s / 976 s | ¥0.20 | `resource-ledger.json:23-37`，内存 2.37 GB |
| scVI（跨门） | **55,694** × 6,222 | 2c8g | **9,773 s** / 9,833 s | **¥2.06** | `resource-ledger.json:38-52`，内存 3.63 GB |
| SAMap（runsamap WDL） | 4,606（150 维联合嵌入） | 1c4g | 354 s / 414 s | ¥0.02 | `resource-ledger.json:53-67`，内存**未测** |
| SATURN v71（HVG 2500，1000 macrogenes，50 epoch） | 4,606 | 1c4g | wall **6,886 s**（04:26:47→06:21:33） | ¥0.47 | `docs/dcs-offline-task-history-20260926.md:19` |
| scVI 全量**单物种**（5 epoch，32c128g） | 30,000×32,732 / 60,471 / 50,000 | 32c128g | 68.4 s / 128.9 s / 275.2 s | 未单独计 | `docs/heart-pilot-scvi-baseline-20260921.md:31-33,16` |
| SATURN 全基因 prep OOM | 三物种全基因 × 5120 维嵌入 | 4 GB | RC=137 | — | `docs/codex-review-handoff-20260923.md:32` |

### 3.3 全量估算（外推全在这张表）

> 统一口径：全量 = 三物种并集 **140,471 细胞**；R = 140,471 / 4,606 = **30.50**。

| 方法 | 内存峰值估算 | 内存外推假设 | CPU/GPU 时间估算 | 时间外推依据（模型） | 建议档 | 费用估算 | 性质 |
|---|---|---|---|---|---|---|---|
| **oPCA** | **≈39 GB**（并集 140,471×15,869 float32 稠密 + 置换副本）；逐对（人+鼠 90,471×15,869）**≈25.7 GB** | 峰值 ∝ n_cells×n_genes，以 4,606×15,869→1,307.9 MB 实测为锚（≈17.9 B/元素）**线性外推** | **7.3 h**（26,411 s） | **O(n·d) 线性**：866 s × 30.50；置换次数 200 不变，故只随细胞数线性 | **32c 128g**（2c8g 的 8 GB 必 OOM） | **¥87**（32c 同 wall）；若 32c 相对 2c 提速 4× → **¥22** | 时间=外推；内存=外推；单价=2c8g 实测 / 32c 外推 |
| **scVI** | **≈5.7 GB** | 两锚（4,606→2.37 GB，55,694→3.63 GB）插值；**mini-batch 训练，内存不随 n 线性**，这是它与 oPCA 的本质差别 | **6.5 h**（23,531 s）@2c8g；若按 5-epoch 全量锚口径则 **≈8–10 min** | **幂率 O(n^0.95)**：log(9773/916)/log(55694/4606)=**0.950**，两实测锚拟合；另一锚（全量单物种 5 epoch）说明**贵的是预处理/评估不是训练** | 2c8g 可跑；建议 **8c32g** 更快 | **¥4.8**（2c8g）/ **¥19**（32c 同 wall） | 时间=幂率外推（双实测锚）；内存=双实测锚插值 |
| **SATURN** | **≈8–12 GB**（HVG 2500 预切后）；若不预切 HVG，三物种全基因×5120 嵌入约 3.6 GB 仅嵌入本身，加图与优化器状态会顶到 4–8 GB | 以「4 GB OOM（RC=137）」为下界实测，按基因数×5120×4 B 估嵌入，加 2–3× 运行时副本 | **5–6 h GPU**（含 200 epoch / 2000 macrogene / 8000 HVG 的官方配置） | **两步外推**：① 1c4g CPU 6,886 s（实测）→ GPU 同数据约 1/20–1/50（经验加速比）→ 2–6 min；② ×30.5 → 1–3 h；③ 官方配置相对当前配置（50→200 epoch、1000→2000 macrogene、2500→8000 HVG）再 ×2–3 → **5–6 h**，与 `docs/evidence/genpilot-consultation-20261009.md:107` 的独立估计一致 | **3080Ti×1 / 88c320G**（平台 GPU 仅 3080Ti×1 与 L4×1 两档） | **¥154–185**（5–6 h × 30.78）；3 seed → **¥462–555** | 全部为**外推**（GPU 侧无任何实测训练时长） |
| **SAMap** | **≈8–16 GB** | SAMap 主体是稀疏图 + 每物种 1000 细胞采样的密集子图；按 cells×genes 稀疏 + 1000² 密集估 | **3.0 h**（10,796 s）@1c4g | **O(n) 线性上限**：354 s × 30.50。**注意**：若保持默认 1000 细胞/物种采样，建图步不随 n 增长，实际会**低于**此上限 | 1c4g 勉强；建议 **16c64g** | **¥2.0**（1c4g）/ ¥10–25（16c64g 外推） | 时间=线性上限外推；内存=无实测锚，纯结构外推 |

### 3.4 汇总

| 场景 | 组成 | 费用 | 性质 |
|---|---|---|---|
| 只跑 CPU 三方法（oPCA+scVI+SAMap），全量、单 seed | 32c 档口径 | **¥22–110** | 外推 |
| 加 SATURN 全量训练、单 seed | + GPU 5–6 h | **¥180–320** | 外推（GPU 占 **85%+**） |
| 3 seed 全套 | ×3（拟合要重跑，评分可复用） | **¥550–960** | 外推 |
| 对照：跨门 scVI 5.5 万细胞**已花** | 单任务 | ¥2.06 | **实测** |

**一句话**：规模实验**便宜**（不到 ¥1000 就能 3 seed 全量），**真正贵的是 SATURN 的 GPU 和它的 provenance 债**——花钱之前得先把「训练命令 + 源码 hash」补齐，否则等于把不可审计的数字放大 30 倍。

---

## ④ 全量重跑会不会改变结论

### 4.1 当前要保护的结论（引用前先看 `docs/execution/20261111-obsolete-numbers.md` §三）

| # | 结论 | 当前值（v2 口径） |
|---|---|---|
| C1 | 哺乳类对：**零整合 oPCA ≥ SATURN ≥ SAMap** | 人→鼠 acc 0.8618 / 0.5887 / 0.1689 |
| C2 | 人→鼠 oPCA(0.8618) 大幅高于多数类(0.4817) | `results/bootstrap-20261030/bootstrap.json` |
| C3 | 斑马鱼四方向：三方法均无正信号（唯一例外 z→m oPCA 0.5967） | `docs/execution/20261111-obsolete-numbers.md:116-125` |
| C4 | 跨门（七鳃鳗）负结果，未拿到正对照前不得当生物学结论 | `obsolete-numbers.md:187` |
| C5 | **配置 > 数据规模**：oPCA/scVI 在 1,500 细胞上已到 0.86/0.92 | `docs/reports/20261111-memo-for-teacher.md:31-32` |

### 4.2 三条可能的影响（按影响力度排序）

**理由 1 —— 样本量上升只抬高「每个供体内的细胞数」，不抬高「供体数」，所以 CI 收窄远小于 √30.5。**
全量的细胞是**已有供体**的更多细胞，不是新供体：人 22 个 donor、鼠 4 个 `orig.ident`、鱼 15 个 `orig.ident`（`docs/heart-pilot-scvi-baseline-20260921.md:11`；`docs/heart-inspect-evidence-20260920.json` 的 `donor`/`orig.ident` 段）。而项目已经实测出：**细胞级 bootstrap 的 SE 是供体级 SE 的 1/1.47–1/3.88**（`docs/reports/20261111-memo-for-teacher.md:56`），也就是说细胞级 CI 天生偏窄。全量后：
- 细胞级 CI 半宽会从 ±0.0365（oPCA 人→鼠 macro-F1）收到 **±0.008** 量级（÷√19.6 的理想值）；
- **但供体级 CI 主要由 cluster 数决定（22/4/15），几乎不动**，乐观估计只收到 **±0.015–0.025**。
→ **「样本量上升 → macro-F1 更稳」成立，但幅度被高估 3–5 倍；「两条原本显著、修正后不显著」的结论（memo:56-57）在全量下大概率仍然不显著。**

**理由 2 —— 类不平衡加剧（方向与直觉相反：不是"更平衡"，是"更不平衡"）。**
标签空间不变（12/12/14 类），但稀有类占比从 8.7–9.8% 掉回 1.7–2.8%（②2.4），鼠的内皮一家占 49.0%、鱼 42.0%。macro-F1 对每类等权，于是：
- 大类 recall 上升 → union macro-F1 的"分子"部分改善；
- 稀有类 recall 的估计**更接近真实（更低）**，且斑马鱼 `Proliferating cell` 全量只有 14 个细胞 → 该类 F1 的方差**一点没降**；
- 净效果：**单点 macro-F1 可能整体下移 0.03–0.06**，方向取决于大类增益与稀有类损失谁大。
→ **不能拿全量的 macro-F1 去和现在的数直接相减，必须两套并列双报。**

**理由 3 —— SATURN 的 GPU 时间按细胞线性、按配置超线性，与规模叠加后是 3–30 倍级的墙钟时间。**
当前 SATURN 是「1000 macrogenes / 2500 HVG / 50 epoch / 1c4g / 6,886 s」；官方配置是「2000 macrogenes / 8000 HVG / 200 epoch / GPU」（`docs/reports/20261111-memo-for-teacher.md:19-24`）。两者叠加：5–6 h GPU × 3 seed = 15–18 h GPU ≈ **¥460–555**。→ 规模实验一旦启动 SATURN 支线，**预算和排期都由它决定**，而它的 provenance（训练命令 / 源码 hash）目前仍是 blocked（`docs/execution/20261010-baseline.md:35`、`docs/execution/20261010-handoff-to-next-agent.md:34`）。

### 4.3 判断

| 问题 | 判断 | 依据 |
|---|---|---|
| 全量会翻转方法排名吗 | **不会**（oPCA > SATURN > SAMap 在哺乳类对上是 0.86 vs 0.59 vs 0.17 的量级差，30 倍样本改不动） | C1 的差值远大于任何合理 CI（最大 ±0.04） |
| 全量会让鱼方向"长出信号"吗 | **不会**（三方法在鱼方向低于多数类，是协议/同源覆盖问题，不是样本量问题） | C3；`docs/reports/20261111-memo-for-teacher.md:69-71` 把"复现协议"与"同源覆盖"排在前两位 |
| 全量会让绝对分数变好看吗 | **不一定**（macro-F1 可能下移，accuracy 可能上移：多数类更容易猜） | ②2.4 + 4.2 理由 2 |
| 全量能替代"按原文配置重跑"吗 | **不能**（配置差距是 4×/2×/0.3 vs 1.0，比规模差距更致命） | C5、memo:19-26 |
| 全量值不值得做 | **值得，但不是为了提分**：把 C5「规模不是主因」从推断变成可检验，并给出 CI 收窄的真实幅度 | 本报告 §3 费用 < ¥1000 |

---

## ⑤ 可执行的全量重跑任务清单

### 5.0 平台提交的硬约束（先看这段，否则任务必挂）

| 项 | 事实 | 出处 |
|---|---|---|
| 提交端点 | `POST /stereonote/api/offline/save`（表单路由 404，直连是唯一通路） | `docs/handoff-v74-20260928.md:43`、`docs/course5-longrun-state-20260930.md:94-100` |
| shell 加密 | `CryptoJS.AES.encrypt(content,"stereonote")`（OpenSSL `Salted__` 格式） | `docs/dcs-readonly-audit.md:178` |
| 必需 header | `X-Access-Token` / `X-Zone: st` / `X-Domain-Code` / `X-Domain-Type: 21` / `projectId` | 同上 |
| **多行脚本会被压成单行** | runner 每行尾插 `2>&1 \| tee -a /data/work/offline-task-logs/<subid>.log` 再 `&&` 连接 → **Python 多行语法必毁** | `docs/dcs-readonly-audit.md:179` |
| 正确姿势 | `printf` 写出 `.py` 文件，再 `python3 xxx.py` | 同上 |
| payload 中文会炸 | `projectName` 等字段含中文 → 服务端 `json.loads` 以 latin-1 崩，**用 ASCII** | `docs/handoff-v74-20260928.md:43` |
| `/Files/` | 容器内**只读可见**；持久工作区 `/data/work` | `docs/execution/20261104-队友交接总纲.md:294` |
| 产物 | 落 `/work/{user}/<任务目录>/`，打包后 `dcs data push` 回 `/Files/ResultData/Notebook/` | 同上 :295 |
| resource_id | **1c4g = 259**（实测）；其它档需 `GET /stereonote/api/workspace/get/resource/cfg?task_type=offline&search_type=2` 现查 | `docs/handoff-v74-20260928.md:45` |
| 依赖 | 平台任务都要 `/Files/ResultData/Notebook/pylibs_full.tar.gz`（200.80 MB） | 同上总纲 :271 |
| 环境变量名 | oPCA 平台脚本读 **`OPCA_OUT_ROOT`**（不是 `OPCA_OUT`），写错会得到"平台标失败但结果其实是好的"假警报 | 同上总纲 :296 |

**payload 模板**（直连 `/offline/save`）：

```json
{
  "taskName": "g5-opca-full-v1",
  "taskType": "2",
  "shells": ["<AES(stereonote) 加密后的 shell 字符串>"],
  "fileParams": [],
  "seting": "0",
  "csFileNmme": "",
  "workspaceId": "<从 workspace/get 取>",
  "resource_type": 2,
  "resource_id": "259",
  "projectId": "P20260920085640327",
  "projectName": "bgicourse",
  "imageId": "<images/select/list 取>",
  "imageUuid": "57362367597d49499e5bc388096a17f1",
  "imageName": "SATURN--22",
  "computingNameTemp": "1c 4g",
  "cpu": "1",
  "memory": "4"
}
```

> `cpu`/`memory`/`computingNameTemp`/`resource_id` 必须与所选档**一致**，否则提交成功但调度按错档跑（历史踩过）。

### 5.1 任务表

| ID | 任务 | 档位 | 输入 | 输出 | 验收标准（跑完看这些数字） |
|---|---|---|---|---|---|
| **T0** | 挂载探测 + 全量文件校验（**必须先做，2 分钟，¥0.02**） | 1c4g（259） | `/Files/3/stage3/01_raw_data/heart_omics/scrna/{Homo_sapiens,Mus_musculus,Danio_rerio}_sc.h5ad` | `/data/work/probe_full/` 下 `ls.txt` + `sha256.txt` + `shape.json` | ① 三文件 `ls -l` 字节数 = **223,744,070 / 272,322,064 / 161,403,920**；② sha256 = **3c56fd16… / b5d69235… / 76bcd7ae…**；③ `n_obs` = **30000 / 60471 / 50000**、`n_vars` = 32732/32379/27661。缺任一项 → 停，换 `/Files/lamprey/Heart/Singlecell/` 同名三件 |
| **T1** | oPCA 全量六方向 | **32c 128g**（2c8g 必 OOM，内存峰值 ≈39 GB） | T0 三文件 + `/Files/wheelhouse/orth-MGI-HOM.rpt`、`orth-human-orthos.txt`、`orth-mouse-orthos.txt`、`v99_mapping_embedded.json`（**JSON 版，不是 TSV**） | `/data/work/opca_full/` → `metrics.json` + `predictions/`18 份 + `confusion/`18 份 + `manifest.json` + `environment.txt` | ① `n_cells` = 140,471（或按逐对 90,471/80,000/110,471）；② 人→鼠 acc 落在 **0.82–0.90**（当前 0.8618 ±0.0173），鼠→人 **0.68–0.79**；③ coverage ≥ 0.98；④ 六方向 CI（**供体整群** bootstrap，1000 次）半宽 ≤ 0.025 |
| **T2** | scVI 全量（union 140k） | 8c 32g 起步（2c8g 也能跑，只是慢；内存 ≈5.7 GB） | T0 三文件（HVG 9000，`batch_key=donor`/`orig.ident`，`labels_key=celltype`） | `/data/work/scvi_full/` → `latent.h5ad`（[140471,10]）+ `metrics.json` + 18 份 prediction | ① latent shape = **140471×10**；② 人→鼠 acc ≈ **0.92**（当前 0.9189 ±0.0133，容许 0.89–0.94）；③ 鱼→人 / 鱼→鼠 两向 `n_q` 用 **v2 分母**（1469），不得再用 1499；④ 训练 loss 收敛曲线留档 |
| **T3** | SAMap 全量 | 16c 64g（1c4g 也能跑，3 h 起） | T0 三文件 + `/Files/ResultData/Notebook/run_samap_compliant_v98_dcs.txt`（权威版，md5 `56bb6035`） | `/data/work/samap_full/` → 联合嵌入（n×150）+ `metrics.json` + `manifest.json` | ① 六方向 **n_q 全部 > 300**（当前 SAMap 鼠→人 n_q=307、人→鱼=986、鱼→人=**0 不可评估**）；② 人→鼠 acc 报出点估计 + CI；③ 判据：若全量下仍 ≤ 多数类 → 支持 C3「无信号」而非"样本不够" |
| **T4** | SATURN 全量训练（**前置门：provenance**） | **3080Ti×1 / 88c320G**，¥30.78/h，**封顶 8 h** | ① 官方配置（hv_genes 8000 / macrogenes 2000 / hv_span 0.3 / pretrain 200 epoch）；② `saturn-src.tar.gz.txt`；③ 三件 `*_saturn_input_s.h5ad`（现成的 4,606 版不够，**需按全量重做**） | `/data/work/saturn_full/` → `Final AnnData` + `macrogenes` obsm + command.txt + environment.txt + 源码树 sha256 | ① **前置**：训练命令全文 + 源码 commit/补丁 hash 落盘（这是当前 blocked 项，`docs/execution/20261010-baseline.md:35`），没有就先别提交；② loss 收敛到 ≤0.08（CPU 版实测 0.07–0.08，`docs/execution/20261111-mainline-reframe.md:73`）；③ 人→鼠 coarse acc ≥ 0.5887（当前 v2 实测）；④ 3 seed 必须都跑，**单 seed 不出结论**（鱼方向 seed 双峰已证） |
| **T5** | 统一评分 + 供体整群 bootstrap | 2c8g | T1–T4 的 `predictions/` | `/Files/ResultData/Notebook/scale-20261111/` → `current-table-full.{tsv,json,md}`（与现有 `results/current-20261111/current-table.*` 同 schema，42 行） | ① 42 行齐全，每行带 `method/direction/metric/value/n_q/ci_low/ci_high/mapping_version/source_json/notes`；② CI 一律**供体整群**重抽样（1000 次），禁止再用细胞级；③ 新旧值并列双报，禁止相减当"规模效应" |

### 5.2 T1 的 shell 骨架（规避 runner 单行化）

```bash
set -e
mkdir -p /data/work/opca_full
cat > /data/work/opca_full/run.py <<'PYEOF'
import anndata as ad, json, os
src = "/Files/3/stage3/01_raw_data/heart_omics/scrna"
files = {"human": "Homo_sapiens_sc.h5ad", "mouse": "Mus_musculus_sc.h5ad", "zebrafish": "Danio_rerio_sc.h5ad"}
for k, v in files.items():
    a = ad.read_h5ad(os.path.join(src, v), backed="r")
    print(k, a.n_obs, a.n_vars, flush=True)
    a.file.close()
PYEOF
python3 /data/work/opca_full/run.py
```

> 注意：若走"多行被压平"的旧 runner，`cat > ... <<'PYEOF'` 这种 heredoc 也会被压坏。**稳妥写法**：本地用 `printf '%s\n' 'line1' 'line2' ... > run.py` 拼，或者把 `.py` 先 `dcs data push` 到 `/Files/ResultData/Notebook/` 再在任务里 `cp`。历史上能跑通的都是后者（`docs/execution/20261104-队友交接总纲.md:266-272` 的脚本清单就是为此存在）。

### 5.3 执行顺序（依赖关系）

```
T0（2 min，¥0.02）
 ├─ 失败 → 换 /Files/lamprey/Heart/Singlecell/ 重试；仍失败 → 停，找运维
 └─ 通过
     ├─ T1 oPCA 全量（7.3 h，¥22–87）  ─┐
     ├─ T2 scVI 全量（6.5 h，¥5–19）    ├→ T5 统一评分（30 min，¥0.4）
     ├─ T3 SAMap 全量（3.0 h，¥2–25）   ─┘
     └─ T4 SATURN 全量（5–6 h×3 seed，¥462–555）── 前置 provenance 补齐
```

**预算保险丝**：T1–T3 合计 ≤ ¥150；T4 单 seed ≤ ¥200、三 seed ≤ ¥600；任一任务页面预估超上限就停下问，不硬跑（沿用 `docs/superpowers/plans/2026-09-29-course5-final-roadmap-flash-dcs.md:115` 的纪律）。

---

## 附录：复算命令

```powershell
cd D:\projects\course5-prep
.\.venv39\Scripts\python.exe tmp\audit_subset_inspect.py > tmp\audit_subset_inspect.json   # 子集 n_obs/列名/分布
.\.venv39\Scripts\python.exe tmp\audit_class_table.py   > tmp\audit_class_table.json       # 子集 vs 全量逐类覆盖率
.\.venv39\Scripts\python.exe tmp\audit_scale_calc.py                                       # 倍数/时间/内存/费用
```

**已知缺口（本报告没解决的）**

1. `32c 128g` 与 `16c 64g` 的 **resource_id 与真实单价**：平台无公开计价接口，本报告的 ¥11.8/h 是按核数线性外推，**不是报价**。
2. **SATURN GPU 训练时长无任何一次实测**——表格里 5–6 h 是「1c4g 实测 × 经验加速比 × 配置系数」的三段外推。
3. **SAMap 全量是否仍按 1000 细胞/物种采样**未核实；若是，则 3.0 h 是明显高估的上限。
4. 全量三文件在**离线容器**内的可见性只做了推理（`/Files` 只读可见已证），未单独探过这条深路径——这正是 T0 存在的理由。