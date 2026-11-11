# SATURN 逐细胞 payload 完整性闸门（2026-11-11）

## 目标

判定 `results/pilot-v1/saturn-v99/raw/recovered-20261001/payloads/` 六个文件能否作为
`results/pairwise-20261111/pairwise_corrected.json` 里 SATURN 侧的逐细胞来源。

## 判据

同一方向、同一约定 B（真值→目标物种词表、预测→源物种词表）、同一 v2 映射，
三条路径必须同时给出相同 macro-F1 与 n：payload / confusion / 权威表。

## 结果

| 方向 | payload mf1 | payload n | confusion mf1 | n | 权威 mf1 | n | payload | confusion |
|---|---|---|---|---|---|---|---|---|
| human->mouse | 0.3522 | 1505 | 0.3522 | 1505 | 0.3522 | 1505 | ✅ | ✅ |
| mouse->human | 0.2147 | 1528 | 0.2566 | 1528 | 0.2566 | 1528 | ❌ | ✅ |
| human->zebrafish | 0.1282 | 1469 | 0.1282 | 1469 | 0.1282 | 1469 | ✅ | ✅ |
| zebrafish->human | 0.1386 | 1528 | 0.1386 | 1528 | 0.1386 | 1528 | ✅ | ✅ |
| mouse->zebrafish | 0.3600 | 1469 | 0.4076 | 1469 | 0.4076 | 1469 | ❌ | ✅ |
| zebrafish->mouse | 0.2959 | 1505 | 0.2961 | 1505 | 0.2961 | 1505 | ✅ | ✅ |

## 结论

confusion 路径 6/6 复现权威值，payload 路径在 2 个方向上失败：mouse->human、mouse->zebrafish。

失败的 payload 在任何「标签位置互换 / 物种对调」的 4 种解释下都无法同时满足
「macro-F1 等于权威值」与「n 等于权威 n」——即它们的标签列不是同一次运行、
同一映射的产物，文件名对应关系被搞混。

**因此：pairwise_corrected.py 的 SATURN 侧不能继续用 payloads/。**
SATURN 侧改用 confusion 还原（计数展开成标签序列），代价是失去与 scVI/oPCA 的
逐 barcode 配对，Δ 的语义从「同批细胞配对」降级为「方向内独立重抽样」。

## 复算命令

```powershell
cd D:\projects\course5-prep
.\.venv39\Scripts\python.exe scripts\pairwise_audit_gate.py
```
