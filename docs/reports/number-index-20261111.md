# 唯一权威数值索引（2026-11-11）

> **本文件是仓库内全部对外数字的唯一权威源。** 任何文档、PPT、讲稿引用本项目数字，
> 必须引用本文件的 `值 + 源文件 + 字段路径` 三元组，不得从别处二次转述。
>
> - 生成方式：`results/current-20261111/current-table.json`（42 行，机器生成）+
>   本索引复核脚本 `scripts/_opca_recheck2.py` / `scripts/_crossphylum_recheck.py`（独立重算）。
> - 复核结论：oPCA 六向 macro-F1 与 accuracy **逐个复算一致**；跨门 macro-F1 **逐个复算一致**。
> - 维护规则：数字变了只改本文件；本文件不改，别处不许改数字。

---

## 0. 引用四纪律（违反其中任一条，数字即作废）

1. **禁止跨方法比不同指标**：accuracy ≠ macro-F1。
2. macro-F1 必须带三件套：**union 口径 + 分母 n_q + mapping 版本**。
3. 跨方法比较必须声明**拟合方式**：`transductive` / `inductive`。
4. 跨门负结果在拿到正对照前**不得当生物学结论**。

---

## 1. 四方法六向 macro-F1（union 口径）

源：`results/current-20261111/current-table.json` → `rows[].{method,direction,metric,value,n_q,mapping_version,source_json}`
oPCA 与跨门两处经独立重算复核一致；scVI 四项为 v1 映射（待重跑）；SAMap 仅 3 向可评估。

| 方向 | oPCA | scVI | SATURN | SAMap |
|---|---|---|---|---|
| 人→鼠 | 0.6435 | 0.6683 | **0.3522** | 0.1127 |
| 鼠→人 | 0.6729 | 0.5895 | **0.2566** | 0.0401 |
| 人→斑马鱼 | 0.1506 | 0.4014 ⚠ | **0.1282** | 0.0477 ⚠ |
| 斑马鱼→人 | 0.2131 | 0.4290 ⚠ | **0.1386** | n/a（n_q=0） |
| 鼠→斑马鱼 | 0.2816 | 0.4248 ⚠ | **0.4076** | n/a（n_q=1） |
| 斑马鱼→鼠 | 0.4186 | 0.4786 ⚠ | **0.2961** | n/a（n_q=0） |

- ⚠ = scVI 四个斑马鱼相关方向仍挂在 **v1 映射**（分母 1499，应为 1469），**引用必须标注「v1 分母，待重跑」**。
- SATURN 列字段路径：`results/bootstrap-20261030/saturn_convention_mapv2.json` →
  `directions.<方向>.strict_cell.mf1`（**不是** `published.mf1`；`published` 会把斑马鱼→人抬到 0.2501）。
- oPCA 列字段路径：由 `results/mapping-v2-20261111/rerun-v2/confusion/coarse_*.json` 混淆矩阵现算（union）。
- 全套 42 行机器表：`results/current-20261111/current-table.{md,tsv,json}`。

---

## 2. SATURN 六向 accuracy

源：`results/bootstrap-20261030/saturn_convention_mapv2.json` → `directions.<方向>.strict_cell.acc`

| 方向 | accuracy | 对应 macro-F1 | 分母 n_strict |
|---|---|---|---|
| 人→鼠 | 0.5887 | 0.3522 | 1505 |
| 鼠→人 | 0.2271 | 0.2566 | 1528 |
| 人→斑马鱼 | 0.1811 | 0.1282 | 1469 |
| 斑马鱼→人 | 0.2147 | 0.1386 | 1528 |
| 鼠→斑马鱼 | 0.3036 | 0.4076 | 1469 |
| 斑马鱼→鼠 | 0.4565 | 0.2961 | 1505 |

**一句话纪律**：这六个数**是 macro-F1，不是 accuracy**。曾在 `_claude/q1-*.md` 里被当成 accuracy 列，已纠正。

**覆盖率（可评估细胞占比）**：人→鼠 100%、鼠→人 100%、人→斑马鱼 100%（真值侧 30 个 `Orthers` 退出）、
斑马鱼→人 **43.4%（663/1528）**、鼠→斑马鱼 100%、斑马鱼→鼠 **93.4%（1405/1505）**。
→ 凡写「SATURN 覆盖率 97–100%」的句子均已失效。

---

## 3. 跨门（七鳃鳗 ↔ 小鼠）四值

源：`results/phase-20261022/crossphylum/metrics.json` → `<method>.directions.<dir>.acc` / `.macro_f1_union`
**注意**：该文件存的 `macro_f1_union` 字段是污染值（0.0711/0.0732/0.0652/0.0802）。
下表 macro-F1 为**从同文件混淆矩阵 union 口径重算**的结果，acc 与重算逐位一致（本索引已复核）。

| 方法 | 方向 | accuracy | macro-F1（重算） | majority 基线 | shuffle p | n_q |
|---|---|---|---|---|---|---|
| oPCA | 七鳃鳗→鼠 | 0.0575 | **0.0235** | 0.2168 | 0.345 | 14016 |
| oPCA | 鼠→七鳃鳗 | 0.0516 | **0.0257** | 0.3059 | 0.86 | 41678 |
| scVI | 七鳃鳗→鼠 | 0.0582 | **0.0241** | 0.2168 | 0.04 | 14016 |
| scVI | 鼠→七鳃鳗 | 0.0457 | **0.0267** | 0.3059 | 0.145 | 41678 |

规模：55,694 细胞 × 6,222 基因，13 类。

---

## 4. 批次混合三指标（仅 scVI 有）

源：`docs/reports/report-04-scvi-and-batch-20261023.md` §第 5 页（L87–L89）

| 指标 | 值 | 判读 |
|---|---|---|
| silhouette（细胞类型，cosine） | 0.181 | 结构存在但不清晰 |
| iLISI（物种，k=30） | **1.125** | 理论 1–3；接近 1 = 邻居几乎全同物种 |
| kBET 接受率（α=0.05） | **0.0039** | 几乎全部邻域被拒绝 |

**纪律**：低 iLISI 不等于方法失败；两项（混合度 / 生物保守性）必须并列报告，不能只引一个。
其余三方法当时未保存嵌入 → **无批次指标，不得补造**。

---

## 5. 时间与内存（单次记录，非受控 benchmark）

源：`docs/reports/time-memory-benchmark-20261023.md` §一（DCS 任务号逐条可回溯）

| 方法 | 场景/任务 | 规模 | 墙钟 | 实际计算 | CPU | 峰值内存 | 费用 |
|---|---|---|---|---|---|---|---|
| ortholog-PCA | 本地 | 4,606 × 15,869 | 30 秒 | 30 秒 | — | 未测 | 0 |
| ortholog-PCA | DCS `W202610150090794`（2c8g） | 同上 | 47m50s（含排队 ~21min） | **14m26s** | 0.064 h | **1.19 GB** | ¥0.19 |
| scVI（门内） | DCS `W202610190042919`（2c8g） | 4,606 × 9,018 | 28m40s | **8.5 min** | 0.142 h | **2.37 GB** | ¥0.20 |
| scVI（跨门） | DCS `W202610220063725`（2c8g） | 55,694 × 6,222 | **3h29m** | — | — | **3.63 GB** | ¥2.06 |
| SAMap v98 | DCS（1c4g） | 4,606 | **16m24s** | — | — | 未测 | ¥0.18 |
| SATURN v99 | GPU 任务 | 4,606 | 未系统测量 | — | — | 未测 | — |

**纪律**：本表只回答「大概多久 / 大概多少内存」，**不做性能排名**（排队混入、资源档不同、单次无重复）。

---

## 6. 平台费用与预算

源：`config/dcs-budget-plan.json`、`config/team-budget-plan.json`

| 项 | 值 | 字段路径 |
|---|---|---|
| DCS 账户余额 | ¥99.0 | `dcs-budget-plan.json` → `account_balance_cny` |
| 试用上限 / 预留 | 25 min / 30 min，单次 ≤¥10 | `.trial_policy.{max_trial_minutes,reserved_minutes,max_trial_cost_cny}` |
| 4090×1 单价 | ¥17.4 / 小时 | `.profiles.4090x1.hourly_rate_cny` |
| 4090×2 单价 | ¥44.3 / 小时 | `.profiles.4090x2.hourly_rate_cny` |
| 团队名义预算 | ¥400（4 账户 × ¥100） | `team-budget-plan.json` → `total_nominal_budget_cny` |
| 储备金 | ¥80 | `.reserve_cny` |
| 可花上限 | **¥320** | `.operational_spend_cap_cny` |

---

## 7. 映射表 38 行状态

源：`config/heart-celltype-map-v2.tsv`（签认版）、`config/heart-celltype-map-v1.tsv`

| 统计 | v1 | **v2（现行）** |
|---|---|---|
| 行数 | 38 | **38** |
| active | 35 | **34** |
| unmapped | 3 | **3** |
| unresolved | 0 | **1** |
| 物种分布 | — | human 12 / mouse 12 / zebrafish 14 |
| 与 v1 差异行 | — | **仅 1 行**：`zebrafish \| Orthers`，`neural`+`active` → `other`+`unresolved` |

连带影响：`neural` 在斑马鱼预测空间消失 → 斑马鱼→人 accuracy 由 0.1734（v1）升到 0.2788（v2）。
另两行（小鼠 `Valve`→fibroblast、斑马鱼 `Perivascular cells`→smooth_muscle）**保留但须标注**依据/备选/预期偏差/敏感性。

---

## 8. 分母与数据规模

| 项 | 值 | 源 |
|---|---|---|
| oPCA / SATURN 分母（六向） | 1505 / 1528 / 1469 / 1528 / 1469 / 1505 | `saturn_convention_mapv2.json` `n_strict`；oPCA 同 |
| scVI 分母（门内两向 + 斑马鱼→鼠） | 1505 / 1528 / 1505 | `bootstrap.json` |
| scVI 分母（人→斑马鱼、鼠→斑马鱼） | **1499（v1，应为 1469，待重跑）** | `bootstrap.json` |
| SAMap 分母 | 1368 / 307 / 986 / **0 / 1 / 0** | `bootstrap.json`（后三向不可评估） |
| 我们用到的规模 | 1,528 / 1,535 / 1,543（每物种）；门内实验 4,606 细胞 | `docs/heart-inspect-evidence-20260920.json` `n_obs` |
| 原文全量 | **30,000 / 60,471 / 50,000** | 同上 |

**纪律**：规模差距是 **20–40 倍（1.3–1.6 个数量级）**，不是「2–3 个数量级」，也不是「300 倍」。

---

## 9. `865` 与 `30` 的语义（必须一起说）

源：`results/bootstrap-20261030/saturn_convention_mapv2.json`

| 数字 | 含义 | 字段路径 |
|---|---|---|
| **865** | 斑马鱼→人方向、**预测侧**被判成 `Orthers` 的细胞数（`n_dropped_unmappable`） | `directions.zebrafish->human.n_dropped_unmappable` |
| **30** | 人→斑马鱼 / 鼠→斑马鱼方向、**真值侧**的 `Orthers` 细胞数 | `directions.{human->zebrafish,mouse->zebrafish}.truth_unmapped_labels.Orthers` |
| 100 | 斑马鱼→鼠方向预测侧丢的 `Orthers` 数 | `directions.zebrafish->mouse.n_dropped_unmappable` |

**禁止写法**：「865 个细胞被错归为神经」——865 是预测侧计数，不是这一行的真值误映射数。

---

## 10. oPCA：transductive vs inductive（12 个数）

源：`results/transductive-20261111/transductive_vs_inductive.json`；`results/mapping-v2-20261111/rerun-v2/`（transductive）

| 方向 | transductive（**主表用这个**） | inductive | Δ |
|---|---|---|---|
| 人→鼠 | 0.8618 | 0.8186 | −0.0432 |
| 鼠→人 | 0.7369 | **0.5144** | **−0.2225** |
| 人→斑马鱼 | 0.1811 | 0.2056 | +0.0245 |
| 斑马鱼→人 | 0.2788 | **0.0949** | **−0.1839** |
| 鼠→斑马鱼 | 0.2730 | 0.2566 | −0.0164 |
| 斑马鱼→鼠 | 0.5967 | 0.6625 | +0.0658 |

**机制**：`scripts/ortholog_pca_dcs_v3_fixkey.py:278-282` 的 `X_joint = np.vstack([Xs, Xt])`
——PCA 在源+目标细胞上联合拟合，**是 transductive 的**（"看到"了目标细胞）。
拿它去和 inductive 方法（scVI / SATURN / SAMap）比，是不公平比较。

---

## 11. 已作废值（只用于更正对照，不得作为结论引用）

| 代际 | 六向 macro-F1 | 出处 | 状态 |
|---|---|---|---|
| 第 1 代（v1 `published`） | 0.4147 / 0.4010 / 0.2479 / 0.4021 / 0.6500 / 0.6510 | `saturn_convention.json` → `directions.*.published.mf1` | ⛔ 作废 |
| 第 1.5 代（v1 `strict_cell`，即旧称"公平口径"） | 0.3402 / 0.3118 / 0.2051 / 0.2139 / **0.4560 / 0.4588** | 同上 → `directions.*.strict_cell.mf1` | ⛔ 整批作废 |
| 第 2 代（v2 映射前的 `saturn_convention_v2.json`） | 0.3522 / 0.2566 / **0.1269 / 0.1640 / 0.3658 / 0.3563** | `saturn_convention_v2.json` | ⛔ 作废（**最容易误用**） |
| **第 3 代（现行）** | **0.3522 / 0.2566 / 0.1282 / 0.1386 / 0.4076 / 0.2961** | `saturn_convention_mapv2.json` `strict_cell` | ✅ 现行 |

另：`pairwise.json` 内 10 条涉及 `saturn_v99` 的比较全部作废（旧分母 + 旧 mf1）。

---

## 12. 变更记录

| 日期 | 变更 |
|---|---|
| 2026-11-11 | 首版；确立「本文件为唯一权威源」，收录四方法六向 / SATURN accuracy / 跨门 / 批次 / 时间内存 / 费用 / 映射 38 行 / 分母 / 865-30 语义 / transductive-inductive |