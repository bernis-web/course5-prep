# ⚠️ 本文件已作废（SUPERSEDED）

**别引用 `saturn_convention_v2.json` 里的数字当现行值。**

## 为什么

`saturn_convention_v2.json` 是「v1 映射 + 方向更正后」的产物，文件名里的 `v2` 指的是
**约定版本（A/B/C/D 四约定里的更正约定）**，不是**映射版本（v1/v2）**。
这个命名撞车，导致多份文档把它当成「v2 映射的现行结果」引用，于是 0.1269 / 0.1640 /
0.3658 / 0.3563 这组「第 2.5 代」值流进了汇报、选型指南和交接文档。

## 现行在哪

| 用途 | 文件 |
|---|---|
| **现行 SATURN 六向（v2 签认映射 + 约定 B）** | `results/bootstrap-20261030/saturn_convention_mapv2.json` |
| 六值 | 0.3522 / 0.2566 / 0.1282 / 0.1386 / 0.4076 / 0.2961（**strict_cell 口径**） |
| 分母 | 1505 / 1528 / 1469 / 1528 / 1469 / 1505 |
| published 口径（不可映射预测被丢弃） | 鱼→人 0.2501、鱼→鼠 0.3358；其余四向与 strict_cell 同值（丢弃数 = 0） |
| 唯一权威索引（含 oPCA / scVI / SAMap 全部） | `docs/reports/number-index-20261111.md` |
| 本文件的来历与判定过程 | `docs/reports/audit-stats-20261111.md`、`docs/reports/audit-saturn-payload-gate-20261111.md` |

## 保留它干嘛

它是**证据**，不是结论：`scripts/saturn_convention_audit_v2.py` 能复现它，
`scripts/convention_variants.py` 能证明「只有约定 A 能复现 0.6500 那组错值」。
删了就没法解释我们是怎么发现查表方向反了的。所以留档，但只许当历史件读。

## 一句话

**v2 在这个文件名里指约定，不指映射。要映射 v2 的现行数，看 `saturn_convention_mapv2.json`。**