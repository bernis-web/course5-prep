# 报告 11：mapping 表 v2 签认与留痕（2026-11-09）

> ⚠️ **本节数字已作废（2026-11-11 标注）**：见 `docs/reports/number-index-20261111.md` 与 `docs/execution/20261108-更正索引.md`。本文件按当时口径保留，不回改。

> 用途：记录 v2 表的**签认范围、依据与责任边界**，以及签认后数字的变化。
> 前置：`docs/reports/report-10-mapping-v2-proposal-20261108.md`（提案与敏感性）

---

## 一、签的是什么，谁负责

| 类别 | 行数 | 判断性质 | 签认方式 |
|---|---|---|---|
| **L1–L6 高置信 canonical 行** | 30 | **生物判断**（心室肌是不是心肌、内皮算不算内皮） | `项目负责人@2026-11-09(canonical)` —— 依据是源注释 + 文献命名（notes 里有出处），**未逐行请生物学同行复核** |
| **L1–L6 争议归类行**（R22 `Valve`、R31 `Perivascular cells`） | 5（含 fine 层关联行） | **建模选择**，非事实判断 | `(disclosed_choice)` —— 归类保留，但已按披露四项写清备选、偏差方向、敏感性 |
| **L7 排除类**（R37 `Orthers`、`mt`、两个 `Proliferating`） | 3 | **方法学判断**，不需要生物学背景 | `(excluded)` —— 残差桶/线粒体基因/增殖标记不作为细胞类型类 |
| **R37 `Orthers` 单独** | 1 | 方法学 + 生物混合 | `unresolved` —— 退出评估（见下） |

**责任边界，必须说清**：
- 本次签认由**项目负责人授权**，复核意见由 AI 程序化生成（脚本可复算）；
- **这不等于生物学同行逐行复核**。若要对外发论文，L1–L6 的 canonical 行建议再找一位做心脏发育/免疫的人抽查 20%；
- `reviewer` 列填的是**授权签认人 + 日期 + 签认类别**，不是「AI 复核通过」的印章。

---

## 二、v2 相对 v1 改了什么

| 行 | v1 | v2 | 性质 |
|---|---|---|---|
| R37 `zebrafish\|Orthers` | `neural` / active | **`other` / unresolved**（退出评估） | 残差桶不作为一类 |
| R22 `mouse\|Valve` | `fibroblast` / active | 不变，但 notes 补四项披露 | 披露完整性 |
| R31 `zebrafish\|Perivascular cells` | `smooth_muscle` / active | 不变，但 notes 补四项披露 | 披露完整性 |
| 全部 | `reviewer = pending` | 签名留痕 | 可追溯 |

产出：`config/heart-celltype-map-v2.tsv`（38 行，schema 与 v1 完全一致，**v1 未覆盖**）

---

## 三、签认后数字的变化（重要）

用 v2 表重算 SATURN（`MAP_TSV=config/heart-celltype-map-v2.tsv python scripts/saturn_convention_audit_v2.py`）：

| 方向 | v1 口径 mf1 | v2 口径 mf1 | v2 分母（strict） | 变化 |
|---|---|---|---|---|
| 人 → 鼠 | 0.3522 | **0.3522** | 1505 | 不变 |
| 鼠 → 人 | 0.2566 | **0.2566** | 1528 | 不变 |
| 人 → 斑马鱼 | 0.1269 | **0.1282** | 1469（−30 真值） | +0.0013 |
| 斑马鱼 → 人 | 0.1640 | **0.1386** | 1528 | −0.0254 |
| 鼠 → 斑马鱼 | 0.3658 | **0.4076** | 1469（−30 真值） | +0.0418 |
| 斑马鱼 → 鼠 | 0.3563 | **0.2961** | 1505 | −0.0602 |

### ⚠️ 一个必须记住的副作用

启用 v2 后，`zebrafish→human` 方向**又出现了「不可映射预测被丢弃」**：

```
zebrafish->human   n_pub= 663  n_strict= 1528   (差 0.1115)
```

原因：`Orthers` 从 `neural`（active）改成 `unmapped` 后，那 865 个原本被判成 `Orthers` 的预测**重新变成不可映射**。若沿用旧的 `published` 口径（丢样本），分数会被抬到 0.2501；用 `strict_cell`（保留细胞、算错）才是 0.1386。

**结论**：`published` 口径**必须彻底弃用**。只要映射表里存在任何 unmapped 类，丢样本的口径就会系统性抬高分数。**对外一律用 `strict_cell`。**

---

## 四、连带影响清单

| 项 | 状态 |
|---|---|
| SATURN 六向数字 | 已按 v2 重算；`场景化选型指南` 需出 **v8** |
| 选型推荐 | **不变**（scVI 四个远缘方向仍全部最优：0.4248 > 0.4076、0.4786 > 0.2961 等） |
| 跨门、批次指标 | 不受影响（不用 esta 映射表的这两处） |
| 锚定 86.18%（人→鼠 accuracy） | **不变**（v2 未改人/鼠任何行） |
| `g5-opca-container` 镜像内 6 值复现 | 需确认：镜像用的是 v1 映射；若换 v2 重跑，鱼相关的值会变 |

---

## 五、还差什么

1. **选型指南 v8**（v2 数字）
2. **镜像内 6 值复现的口径确认**：镜像里嵌的是 v1 映射，需在文档里标注「复现基于 v1」或重跑
3. **生物学同行抽查**（若要投稿）
4. `docs/execution/20261108-更正索引.md` 里的旧文件清单，同样适用于 v2 变更

---

## 六、复算命令

```bash
# v1 口径
python scripts/saturn_convention_audit_v2.py

# v2（签认后）口径
MAP_TSV=config/heart-celltype-map-v2.tsv python scripts/saturn_convention_audit_v2.py

# 三行改动的敏感性
python scripts/mapping_v2_sensitivity.py
```

产物：`results/bootstrap-20261030/saturn_convention_v2.json`（**运行时会按 MAP_TSV 覆盖**，建议跑完自行改名存档）、`mapping_v2_sensitivity.json`
