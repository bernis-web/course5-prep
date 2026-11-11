# 报告 10：mapping 表 v2 提案与分谱系签字包（2026-11-08）

> ⚠️ **本节数字已作废（2026-11-11 标注）**：见 `docs/reports/number-index-20261111.md` 与 `docs/execution/20261108-更正索引.md`。本文件按当时口径保留，不回改。

> 目的：把「一个人签 38 行」改成「按谱系分签 + 每行带真披露」，并先把改动的代价算清楚。
> 结论：**v2 建议改 1 行（R37 `Orthers` 退出评估），保留 2 行但补全披露（R22 `Valve`、R31 `Perivascular cells`）。**
> 采纳 v2 会让 SATURN 的部分数字再动一次，幅度见 §3；**动完之后仍不影响任何推荐结论**。

---

## 一、v1 的问题（不是错，是不完整）

`config/heart-celltype-map-v1.tsv` 38 行，`reviewer` 全为 `pending`。三行的归类值得逐条说清：

| v1 行号 | 物种 | 原始标签 | v1 粗类 | 置信度 | 争议点 |
|---|---|---|---|---|---|
| 37 | zebrafish | `Orthers` | `neural` | low | 源标签是 `Others` 的拼写错误，**整表只有 30 个细胞**，本质是「无法归类」的残差桶 |
| 22 | mouse | `Valve` | `fibroblast` | low | 瓣膜间质细胞（VIC）并入成纤维，可辩护但是**建模选择** |
| 31 | zebrafish | `Perivascular cells` | `smooth_muscle` | medium | 周细胞（rgs5a/pdgfrb/notch3）并入平滑肌（myh11/acta2/cnn1） |

> 顺带更正一处旧表述：`docs/reports/report-08-teacher-reply-20261030.md` §3.4 里写的「865 个细胞的错误归属」
> 不准确。865 是**预测侧**被判成 `Orthers` 的细胞数（可从 `coarse_zebrafish_to_human.json` 逐对求和复现），
> 不是这一行误映射的真值细胞数。该行真值侧只有 30 个细胞。

---

## 二、v2 提案（`config/heart-celltype-map-v2-proposal.tsv`）

| 行 | v1 | v2 提案 | 理由 |
|---|---|---|---|
| R37 `zebrafish\|Orthers` | `neural` / active | **`other` / `unresolved`** | 残差桶不带细胞类型身份，整桶记 neural 会让神经类的精确率失去解释力。不建议为单物种单行新建专属粗类（会让类集合随物种变化，比污染更难处理；若要保留，应拆成 neural 子集 + unmapped，需要逐细胞 marker 证据） |
| R22 `mouse\|Valve` | `fibroblast` / active | **维持**，补全披露 | VIC 间充质来源成立（Hu 2022 把瓣膜间充质并入 fibroblast-like）；但 human 无 Valve 行，**物种间类别不对称**，必须在 notes 里标出 |
| R31 `zebrafish\|Perivascular cells` | `smooth_muscle` / active | **维持**，补全披露 | mural 程序共享成立，但会抬高平滑肌召回 |

**schema 不变**（列与 v1 完全一致），只在 `notes` 里按「披露四项」写全：
① 依据与文献 ② 备选归类 ③ 预期偏差方向与受影响指标 ④ 敏感性结果。

---

## 三、敏感性：改这一行会动多少（修正口径下重算）

`scripts/mapping_v2_sensitivity.py` → `results/bootstrap-20261030/mapping_v2_sensitivity.json`
基线 = v1 + 2026-11-08 词表方向修正后的 SATURN。

### R37 `Orthers` 退出评估

| 方向 | 基线 mf1 | 改后 | Δ | 分母 |
|---|---|---|---|---|
| 人→斑马鱼 | 0.1269 | 0.1282 | **+0.0013** | 1499 → 1469 |
| 斑马鱼→人 | 0.1640 | 0.1386 | **−0.0254** | 1528（不改） |
| 鼠→斑马鱼 | 0.3658 | 0.4076 | **+0.0418** | 1499 → 1469 |
| 斑马鱼→鼠 | 0.3563 | 0.2961 | **−0.0602** | 1505（不改） |

注：斑马鱼作真值的方向分母 −30（那 30 个细胞退出）；斑马鱼→人/鼠 两向另有 865 / 100 个**预测**原本落到
`Orthers` 并映射成 neural，改后变成不可映射 → 记错。**所以不是「只减 30 个细胞」那么简单。**

### R22 `Valve` 退出评估

| 方向 | 基线 | 改后 | Δ |
|---|---|---|---|
| 人→鼠 | 0.3522 | 0.3500 | −0.0022 |
| 鼠→人 | 0.2566 | 0.2271 | **−0.0295** |
| 鼠→斑马鱼 | 0.3658 | 0.3264 | **−0.0394** |
| 斑马鱼→鼠 | 0.3563 | 0.3567 | +0.0004 |

### R31 `Perivascular cells` 退出评估

| 方向 | 基线 | 改后 | Δ |
|---|---|---|---|
| 人→斑马鱼 | 0.1269 | 0.1235 | −0.0034 |
| 鼠→斑马鱼 | 0.3658 | 0.3684 | +0.0026 |
| 其余四向 | — | 不变 | 0 |

**读法**：三行里影响最大的是 R37（最多 ±0.06）。即使全部采纳，scVI 在四个远缘方向仍全部高于 SATURN
（最低差距 scVI 0.4248 vs SATURN 上限 0.4076）。**推荐结论稳。**

---

## 四、签字方式：按谱系分，不按物种分

判断力在谱系，不在物种——同一个「心肌细胞」在人/鼠/鱼三处的判断是同一类知识。

`deliverables/课题5-mapping-签字单-20261108.csv`（38 行，可直接发给对应的人填）

| 谱系 | 行数 | 需要什么背景 | 覆盖的粗类 |
|---|---|---|---|
| **L1 心肌** | 5 | 心脏发育 / 心肌细胞 | cardiomyocyte |
| **L2 免疫** | 7 | 免疫学（髓系/淋系/肥大） | immune |
| **L3 基质-血管** | 11 | 间质、平滑肌、周细胞、脂肪 | fibroblast / smooth_muscle / adipocyte |
| **L4 内皮-被膜** | 8 | 血管与淋巴内皮、心外膜/间皮 | endothelial / epicardial |
| **L5 神经** | 2 | 神经 / 神经嵴 | neural |
| **L6 红系** | 1 | 红细胞 | erythroid |
| **L7 排除类（方法学）** | 4 | 不需要生物学判断，需要方法学确认 | other（含 `Orthers`、`mt`、两个 Proliferating） |
| **合计** | **38** | — | — |

**签字约定**：
1. 每行填 `签字人`（姓名）+ `日期` + `意见`（同意 / 改判 / 存疑）；
2. `改判` 或 `存疑` 的行**不阻塞**其他行——把该行在 v2 里标 `unresolved` 即可，评估时退出；
3. 全表签完后，把 `reviewer` 列从 `pending` 改成对应签字人，`mapping_status` 保持 `active`/`unmapped`/`unresolved` 三值之一；
4. 任何后续改动进 changelog 重签，**不覆盖旧签**（签名是留痕，不是状态位）；
5. **不要**把 `reviewer` 填成「AI」或模型名——AI 复核是另一件事，混填会让这列的语义失效。

---

## 五、采纳顺序

1. 先把本报告 + 签字单发给对应谱系的人（L7 那 4 行可以找我这种做方法学的确认）；
2. 收齐后：改 `reviewer` 列 → 存为 `heart-celltype-map-v2.tsv`（**不要覆盖 v1**）；
3. 用 v2 重跑 `scripts/saturn_convention_audit_v2.py`（把 `MAP_TSV` 指到 v2）与
   `scripts/compute_batch_metrics.py`，出「v1 vs v2」对照；
4. 数字若变化，同步 `deliverables/场景化选型指南-v7-20261108.md` → 出 v8。

---

## 六、复算命令

```bash
python scripts/mapping_v2_sensitivity.py     # 三行候选改法的敏感性
python scripts/convention_variants.py        # 词表归属判定（上一轮那处 bug）
python scripts/saturn_convention_audit_v2.py # 修正口径后的 SATURN 三口径
```

产物：`results/bootstrap-20261030/mapping_v2_sensitivity.json`、
`convention_variants.json`、`saturn_convention_v2.json`。
