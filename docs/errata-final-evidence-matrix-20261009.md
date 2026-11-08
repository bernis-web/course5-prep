# 勘误：final-evidence-matrix-20261005.md（2026-10-09）

> 依据：Codex 只读审计（2026-10-09）发现冻结证据矩阵两处表述错误。
> 处置：**不覆盖原冻结文件**；本勘误为补充说明，引用时以本文件为准。
> 原文件：docs/final-evidence-matrix-20261005.md（保持冻结状态不变）。

## 勘误一：§四.3 鱼方向分母笔误（原第 51 行）

**原文**：
> 3. **跨方法分母不同**：各列 n_q 随各自排除规则（ortholog-PCA coarse 1505/1496；v99 同；SAMap 1505/1496）；每个 acc 必须并列 n_q

**更正**：
- ortholog-PCA coarse：h→m **1,505** / h→z **1,499**（非 1496）
- v99 coarse：h→m **1,505** / h→z **1,499**（非 1496）
- SAMap coarse：h→m **1,505** / h→z **1,496**（此项原文正确）

**依据**（逐格复核，2026-10-09）：
- results/pilot-v1/ortholog-pca-v98/metrics.json：human→zebrafish.coarse.n_q = 1499；coverage_q = 0.9715（1,543 − 44）
- results/pilot-v1/saturn-v99/raw/recovered-20261001/metrics.json：human→zebrafish.coarse.n_q = 1499；n_excluded_q = 44
- results/pilot-v1/samap-v98/wdl-run/extracted/metrics.json：human→zebrafish.coarse.n_q = 1496；n_excluded_q = 47

**影响范围**：任何引用"鱼方向分母"的表述。已同步修正：汇报 3/4/7 各册（本轮）；其余文档如再引用该行，需按本勘误更正。
**注**：SAMap 鱼方向 1,496 与映射表 44（理论 1,499）的 3 细胞差额为事实；根因待核验（此前归因于运行脚本混合口径，尚无独立证据）。

## 勘误二：§四.2 标签空间归类不精确（原第 50 行）

**原文**：
> 2. **跨方法标签空间不同**：ortholog-PCA coarse/fine = 映射词汇（9 粗类）；SATURN/SAMap/v99 = 原始标签+status 过滤（无重映射）

**更正**：
- ortholog-PCA coarse/fine = 映射词汇（9 粗类）✓（原文正确）
- **SATURN v97g 的 coarse/fine = mapped 标签（映射后粗类）**——原文将 SATURN 整体归入"原始标签"，对 v97g 不精确
- SATURN v99 与 SAMap = 原始标签 + status 过滤 ✓

**依据**：docs/v99-score-reconciliation-20261001.md（口径消歧专用文档）：
> "v97g 的 coarse/fine 用 mapped 标签（折叠到粗类/细类空间后评分）；v99 的 coarse/fine 用 exact 标签+排除后评分。因此数字不可直接比较。"

**连带更正——多数类基线必须按标签空间分列**：
- h→m coarse majority：映射空间（ortholog-PCA / v97g）= **0.4817**；原始标签（v99 / SAMap）= **0.4618**
- 因此"单一多数类列"不适用于跨方法同表；汇报 7 已改为两列（多数类·映射空间 / 多数类·原始标签）

## 引用纪律（本勘误生效后）

1. 引用鱼方向分母：ortholog-PCA / v99 用 **1,499**，SAMap 用 **1,496**（并注明 3 细胞差额待核验）。
2. 引用 SATURN 标签空间：v97g = mapped-space；v99 = 原始标签（exact/coarse 双报）。
3. 引用多数类：必须声明其所属标签空间（映射空间 vs 原始标签）。
4. 原冻结文件继续作为主表数字出处；本勘误仅修正上述两处表述与连带的多数类列用法。

## 勘误三：§五 ESM2 消融基线为跨协议混排（2026-10-09 追加）

**原文**：
> - **ESM2 消融**：蛋白嵌入打乱后 61.8%→20.4%，蛋白同源信号为真（v80 置换运行）

**更正**：消融实验本体在 **v72-era 协议**下运行，同协议配对为 **67.4% → 20.4%**；
"61.8%→20.4%" 是跨协议混排（61.8% 系 v97g 口径，20.4% 系 v72-era 消融结果）。

**依据**：
- docs/saturn-smoke-evidence-20260922.md L117：置换消融表 `human→mouse 67.4% → 20.4%`
- docs/handoff-v74-20260928.md L27："ESM2 行置换消融使 h→m 67.4%→20.4%"
- docs/wave0-evidence-matrix-20260930.md L117："61.8%→20.4% 的消融基线是 v72-era 67.4% 对应的实现；
  换用 v97g 协议后消融基线需重跑才能严格对齐"
- docs/v99-score-reconciliation-20261001.md L40：v72-era = 67.4%（historical in-sample; superseded）

**引用规则**：引用消融时必须写"67.4% → 20.4%（v72-era 协议内配对）"，并注明"v97g 协议下消融未重跑"；
不得写"61.8%→20.4%"（跨协议混排）。
