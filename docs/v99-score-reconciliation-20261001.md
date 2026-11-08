# v99 vs v97g 数字口径消歧（2026-10-01）

> 本文档唯一目的：为每个方向×层级的数字指定唯一来源和标签空间，解释差异原因。不选择"更好"的版本。

## 三组数字的协议差异

| 维度 | v97f（全保留） | v97g（映射标签排除） | v99（统一评分器） |
|---|---|---|---|
| 评估脚本 | 容器内 numpy 复刻 | 同 v97f（复用 knn_eval） | dcs_provenance_v99.py（numpy 复刻） |
| 标签空间 | exact 原始标签 | exact 标签 + inactive 排除 | exact 标签 + inactive 排除 |
| unmapped 处理 | 保留（other 类） | **双向排除**（train+分母） | **双向排除**（train+分母） |
| majority 分母 | 全 query | 排除后 query | 排除后 query |
| coverage | 未单列 | ✅ coverage_q 单列 | ✅ coverage_q 单列 |
| per-cell 预测 | ❌ 仅混淆矩阵 | ❌ 仅混淆矩阵 | ✅ 18 组逐细胞 JSON |
| 置换检验 | 200 次洗牌 query 预测 | 同左 | 同左 |
| 任务 ID | 2104537769199724545 | 2104535560372703234 | 2104910134758707202 |

**核心语义差异**：v97g 的 coarse/fine 用 mapped 标签（折叠到粗类/细类空间后评分）；v99 的 coarse/fine 用 exact 标签+排除后评分。因此数字不可直接比较。

## 六方向×三层对照（coarse 层）

| 方向 | v97f acc | v97g acc | v99 acc | v97g majority | 差异原因 |
|---|---|---|---|---|---|
| human→mouse | 60.59% | 61.79% | 48.44% | 48.17%(v97g) / 46.18%(v99) | v99 用 exact 标签训练+投票，v97g 用 mapped 粗类标签。粒度越细，KNN 越难命中。 |
| mouse→human | 23.49% | 25.39% | 19.24% | 31.15%(v97g) / 25.26%(v99) | 同上 |
| human→zebrafish | 17.82% | 18.35% | 11.27% | 39.76%(v97g) / 38.56%(v99) | 鱼方向 v99 低于 v97g——待验证假设：映射 JSON 解析路径差异可能导致部分映射缺失（无直接证据） |
| mouse→zebrafish | 28.90% | 30.09% | 19.48% | 38.63%/39.76% | 同上 |
| zebrafish→human | 24.74% | 18.72% | 18.72% | 31.15%/25.26% | 同上 |
| zebrafish→mouse | 45.60% | 46.51% | 33.75% | 47.23%/46.18% | 同上 |

**注意**：上表中"差异原因"列的解释为**待验证假设**，非已证结论。Phase 1 回收完整 metrics.json 后可逐项验证。

**注意**：上表中 v97f 列来自此前会话记录，v97g 列来自 g5-v97g 日志，v99 列来自 v99-r6 日志。三者均为 transductive/in-sample，不可互相替代。

## 正式引用规则

1. **主表数字**：v97g 列（mapped coarse 标签 + 规则合规排除），引用时标 `transductive_formal_reassessment_of_v71_v72; not_inductive; not_held_out`
2. **v99 列**：标 `transductive per-cell with unified scorer; exact labels; not mapped-space`
3. **v97f 列**：标 `exploratory all-retained; superseded by v97g`
4. **v72-era 67.4%**：标 `historical in-sample; superseded`
5. 三组数字双报或三报均可，**不得合并为单一 benchmark 数字**

## 待消歧项

| 问题 | 当前判定 | 需要的证据 |
|---|---|---|
| v99 的鱼方向数字为何显著低于 v97f/v97g | v99 映射 JSON 解析路径差异（部分映射缺失） | Phase 1 metrics.json 完整回收后逐项对照 |
| v99 与 v97g 的 h→m coarse 差异（61.79% vs 48.44%） | 标签空间不同（mapped vs exact）为已确认主因 | 两套协议的 per-cell 预测对比 |
| v97g 的 z→h coarse 24.74% 低于 v97f 18.72% 的问题 | v97f 排除规则偏向保留 vs v97g 排除——待 Phase 2 逐行对照 | 同上 |
