# 数字溯源核验（2026-11-11）

| 主张 | 期望 | 实测 | 判定 | 强度 | 源文件 |
|---|---|---|---|---|---|
| SATURN human->mouse macro-F1（strict_cell） | 0.3522 | 0.3522 | PASS | RECOMPUTE | `results/bootstrap-20261030/saturn_convention_mapv2.json · directions/human->mouse/strict_cell` |
| SATURN mouse->human macro-F1（strict_cell） | 0.2566 | 0.2566 | PASS | RECOMPUTE | `results/bootstrap-20261030/saturn_convention_mapv2.json · directions/mouse->human/strict_cell` |
| SATURN human->zebrafish macro-F1（strict_cell） | 0.1282 | 0.1282 | PASS | RECOMPUTE | `results/bootstrap-20261030/saturn_convention_mapv2.json · directions/human->zebrafish/strict_cell` |
| SATURN zebrafish->human macro-F1（strict_cell） | 0.1386 | 0.1386 | PASS | RECOMPUTE | `results/bootstrap-20261030/saturn_convention_mapv2.json · directions/zebrafish->human/strict_cell` |
| SATURN mouse->zebrafish macro-F1（strict_cell） | 0.4076 | 0.4076 | PASS | RECOMPUTE | `results/bootstrap-20261030/saturn_convention_mapv2.json · directions/mouse->zebrafish/strict_cell` |
| SATURN zebrafish->mouse macro-F1（strict_cell） | 0.2961 | 0.2961 | PASS | RECOMPUTE | `results/bootstrap-20261030/saturn_convention_mapv2.json · directions/zebrafish->mouse/strict_cell` |
| 分母 human->mouse（n_strict） | 1505 | 1505 | PASS | RECOMPUTE | `results/bootstrap-20261030/saturn_convention_mapv2.json · n_strict` |
| 分母 mouse->human（n_strict） | 1528 | 1528 | PASS | RECOMPUTE | `results/bootstrap-20261030/saturn_convention_mapv2.json · n_strict` |
| 分母 human->zebrafish（n_strict） | 1469 | 1469 | PASS | RECOMPUTE | `results/bootstrap-20261030/saturn_convention_mapv2.json · n_strict` |
| 分母 zebrafish->human（n_strict） | 1528 | 1528 | PASS | RECOMPUTE | `results/bootstrap-20261030/saturn_convention_mapv2.json · n_strict` |
| 分母 mouse->zebrafish（n_strict） | 1469 | 1469 | PASS | RECOMPUTE | `results/bootstrap-20261030/saturn_convention_mapv2.json · n_strict` |
| 分母 zebrafish->mouse（n_strict） | 1505 | 1505 | PASS | RECOMPUTE | `results/bootstrap-20261030/saturn_convention_mapv2.json · n_strict` |
| oPCA 人→鼠 macro-F1（coarse 矩阵重算） | 0.6435 | 0.6435 | PASS | RECOMPUTE | `results/mapping-v2-20261111/rerun-v2/metrics.json · coarse.confusion` |
| oPCA 鼠→人 macro-F1（coarse 矩阵重算） | 0.6729 | 0.6729 | PASS | RECOMPUTE | `results/mapping-v2-20261111/rerun-v2/metrics.json · coarse.confusion` |
| oPCA 人→斑马鱼 macro-F1（coarse 矩阵重算） | 0.1506 | 0.1506 | PASS | RECOMPUTE | `results/mapping-v2-20261111/rerun-v2/metrics.json · coarse.confusion` |
| oPCA 斑马鱼→人 macro-F1（coarse 矩阵重算） | 0.2131 | 0.2131 | PASS | RECOMPUTE | `results/mapping-v2-20261111/rerun-v2/metrics.json · coarse.confusion` |
| oPCA 鼠→斑马鱼 macro-F1（coarse 矩阵重算） | 0.2816 | 0.2816 | PASS | RECOMPUTE | `results/mapping-v2-20261111/rerun-v2/metrics.json · coarse.confusion` |
| oPCA 斑马鱼→鼠 macro-F1（coarse 矩阵重算） | 0.4186 | 0.4186 | PASS | RECOMPUTE | `results/mapping-v2-20261111/rerun-v2/metrics.json · coarse.confusion` |
| scVI 人→鼠 macro-F1（源文件比对） | 0.6683 | 0.6683 | PASS | MATCH | `results/bootstrap-20261030/bootstrap.json` |
| scVI 鼠→人 macro-F1（源文件比对） | 0.5895 | 0.5895 | PASS | MATCH | `results/bootstrap-20261030/bootstrap.json` |
| scVI 人→斑马鱼 macro-F1（源文件比对） | 0.4014 | 0.4014 | PASS | MATCH | `results/bootstrap-20261030/bootstrap.json` |
| scVI 斑马鱼→人 macro-F1（源文件比对） | 0.4290 | 0.4290 | PASS | MATCH | `results/bootstrap-20261030/bootstrap.json` |
| scVI 鼠→斑马鱼 macro-F1（源文件比对） | 0.4248 | 0.4248 | PASS | MATCH | `results/bootstrap-20261030/bootstrap.json` |
| scVI 斑马鱼→鼠 macro-F1（源文件比对） | 0.4786 | 0.4786 | PASS | MATCH | `results/bootstrap-20261030/bootstrap.json` |
| SAMap 人→鼠 macro-F1（源文件比对） | 0.1127 | 0.1127 | PASS | MATCH | `results/bootstrap-20261030/bootstrap.json` |
| SAMap 鼠→人 macro-F1（源文件比对） | 0.0401 | 0.0401 | PASS | MATCH | `results/bootstrap-20261030/bootstrap.json` |
| SAMap 人→斑马鱼 macro-F1（源文件比对） | 0.0477 | 0.0477 | PASS | MATCH | `results/bootstrap-20261030/bootstrap.json` |
| 全量/子集倍数 | 30.5000 | 30.5000 | PASS | RECOMPUTE | `DCS 全量 140,471 / 子集 4,606` |

## 28/28 PASS

- RECOMPUTE：从源数据重算，口径写进报告；
- MATCH：与 current-table 声明的 source_json 逐位对账（证明数字有出处，不证明口径正确）。