# 过时数字审计（Phase 8 修订 PPT/报告前必读，2026-10-03）

> ortholog-PCA 六方向草表已作废（docs/final-evidence-matrix-ortholog-pca-20261003.md 末节）。
> 本清单列出仓库中所有携带旧数字的位置，修订时逐一替换；**修订版 PPT 完成前不得再引用旧表**。

## 载点 1：docs/phase1-results-briefing-20260929.md L22-27（六方向对比表）

| direction | 旧草表（作废） | 新全量 coarse（candidate-final） | majority(coarse) |
|---|---|---|---|
| 人→鼠 | 80.9% | **86.18%** | 48.17% |
| 鼠→人 | 38.3% | **73.69%** | 31.15% |
| 人→斑马鱼 | 40.5% | 19.61% | 39.76% |
| 鼠→斑马鱼 | 22.4% | 27.55% | 39.76% |
| 斑马鱼→人 | 11.9% | 18.13% | 31.15% |
| 斑马鱼→鼠 | 79.5% | **57.61%** | 48.17% |

配套口径修订：
- 表头"ortholog-PCA"列脚注须改为"零整合基线（1:1 ortholog → PCA-50 → KNN15 cosine，映射表 v1 排除）"
- "≈2%/≈39%(=基线)"等 SAMap 草表数字同样待 SAMap v98 冻结后替换
- PPT 若引用"h→m 80.9% > SATURN 61.8%"：新表述为"h→m coarse 86.2% vs SATURN 61.8%"（ SATURN 数字不变，v97g confirmed）
- 斑马鱼向叙事从"全面失败"改为"低于多数类的阴性/弱结果（z→m 例外）"，且 seed=0 单种子点估计

## 载点 2：docs/teammate-notice-20260921.md（同表）

同上替换；该文档发出时间为 09-21，若已发出无法撤回，在正式报告中注明"9-21 通知中的 ortholog-PCA 数字系早期草表，已被统一复算取代"。

## 载点 3：deliverables/course5-monday-presentation.pptx 与 course5-progress-presentation.pptx

构建脚本（scripts/build_monday_presentation.py / build_progress_presentation.py）源码中未 grep 到旧 ortholog 数字；修订 PPT 时以 pptx 内容逐页核对为准（Phase 8 执行项）。

## 不受影响（已核对）

- SATURN v97g 六方向 coarse（61.79/25.39/18.35/30.09/24.74/46.51）：confirmed，不动
- 物种细胞数、ESM2 消融、seed 双峰、物种内 ceiling：confirmed，不动
