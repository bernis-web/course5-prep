# 历史留档作废声明落地（2026-11-11）

## 目标

一致性审计列了 58 行、约 70 个「历史留档」文件：它们定稿于 2026-11-08 之前、已对外讲过/交过，
**改数字等于篡改历史**。正确动作不是改数，而是让每个文件自己声明「这些数已作废，现行看哪」。

## 原理

判据只有一条：**文件是不是现行件**。

- 现行件（v8 选型指南 / part1–4 / 已修的 handoff / 索引 / 审计报告本身）：改数字，不改历史。
- 历史件：加一行声明，数字原样保留。声明里必须给**去哪找现行值**，否则等于没说。

二进制件（docx / pdf / pptx）不能「插一行」——它们的处置靠**版本号 + 文件名日期 + 更正索引**，
见本报告 §四。

## 步骤

```powershell
cd D:\projects\course5-prep
# 先干跑看清要动哪些
.\.venv39\Scripts\python.exe scripts\stamp_historical_docs.py
# 确认后落地
.\.venv39\Scripts\python.exe scripts\stamp_historical_docs.py --apply
```

插入位置：一级标题（`# `）之后一行；已有声明的文件自动跳过（幂等）。

## 实现：已插入 25 个文件

| 组 | 文件 |
|---|---|
| 选型指南旧版（7） | v1-20261017 / v2-20261019 / v3-20261022 / v4-20261023 / v5-20261023 / v6-20261027 / v7-20261108 |
| 执行记录（6） | 20261015-opca-bug-impact-analysis / 20261015-opca-fixkey-diagnosis-and-submission / 20261015-opca-fixkey-verification / 20261017-scvi-submission-package / 20261018-session-state / 20261019-handoff-full / 20261023-resume-point |
| 报告（9） | report-02-metric-lineage / report-03-fairness-boundaries / report-04-scvi-and-batch / report-07-closure / report-08-teacher-reply / report-09-corrections / report-10-mapping-v2-proposal / report-11-mapping-signoff / scvi-cross-species-result / unified-coarse-macro-f1 |
| 交接（1） | `.agent-handoff/20261104-1215-关机断点.md` |

统一声明文本：

```
> ⚠️ **本节数字已作废（2026-11-11 标注）**：见 `docs/reports/number-index-20261111.md`
> 与 `docs/execution/20261108-更正索引.md`。本文件按当时口径保留，不回改。
```

**两个例外**（脚本会自动跳过或人工排除）：

- `docs/team-handbook/part4-汇报说明小白版.md`：它是**现行件**。里面出现的 `0.4147 / 0.6500`
  是「旧值 vs 正确方向」对照表的具体引用，属更正语境，不盖戳；同章 oPCA 四值已改 v2。
- `results/bootstrap-20261030/_SUPERSEDED-saturn_convention_v2.md`：自带专门标牌，无需再盖。

## 验证

```powershell
# 应为 25
(Select-String -Path (Get-ChildItem -Recurse -Filter *.md -File |
  Where-Object {$_.FullName -notmatch '\\tmp\\|node_modules|wheelhouse'}).FullName `
  -Pattern '本节数字已作废（2026-11-11 标注）' | Group-Object Path).Count
```

实测输出：`25`。抽检文件头（`场景化选型指南-v6` / `report-08`）均在第一行标题后出现声明。

## 坑

- `Path.rglob("*.md")` 在本仓会在 `_select_from` 里直接抛（junction / 权限异常目录）。
  改用 `os.walk` + `dirnames` 剪枝。
- part4 一开始被误盖戳：它的作废值出现在**对照表**里，不是当成现值。教训是——判据不能只看
  「文件里有没有旧值」，还要看**旧值在句子里的角色**（是结论，还是被引用的反例）。
- 盖戳是幂等的：跑第二遍只会skip，不会叠两行。

## 二进制件为什么不盖戳（约 45 个 docx/pdf/pptx）

| 类别 | 处置 |
|---|---|
| v3 / v4 汇报 pptx+pdf | 已被 v5 取代；文件名带日期，`更正索引` §一 已列明现行版 |
| 20261017 / 20261019 / 20261023 / 20261102 各次汇报 | 按次存档，是「当时讲了什么」的记录，重命不重改 |
| course5-final-report-v2 / 项目说明-组员版 / 逐页讲解稿 | 历史稿，`更正索引` 已列「待定（可不动）」 |
| 老师七条意见回应 docx | **反例**：它已加修订说明 + 附录 A 对照表（不改正文），是全仓唯一被处理过的历史 docx |
| `tr_render/` `mh_render/` `fr_render/` `td_render/` 下的 PDF | 上述 docx 的渲染件，跟随母件 |

## 下一步

- 跨门 `metrics.json` 存值溯源（0.0711 vs 重算 0.0235）：这是最后一个「数字说不清来历」的点。
- 若将来重出历史件，先跑 `scripts/scan_pptx_chart_cache.py` 与 `scripts/stamp_historical_docs.py`，
  两个扫描器是新文件的准入闸。