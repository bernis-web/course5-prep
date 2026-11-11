# 配对检验·LR 评估器下复检

> oPCA 换成 logistic regression（官方评估器），scVI/SATURN 不变；
> 重抽样单位仍为**个体**（评估侧 donor / orig.ident）。

| 方向 | 比较 | 聚类 | KNN 下 Δ | KNN 显著 | **LR 下 Δ** | **LR 显著** | 是否翻转 |
|---|---|---|---|---|---|---|---|
| 人→鼠 | oPCA vs scVI | 4 | -0.0247 | ns | **+0.1426** | **SIG** | ★翻转 |
| 人→鼠 | oPCA vs saturn | 4 | +0.2914 | SIG | **+0.4587** | **SIG** | — |
| 鼠→人 | oPCA vs scVI | 22 | +0.0833 | ns | **-0.0783** | **SIG** | ★翻转 |
| 鼠→人 | oPCA vs saturn | 22 | +0.4582 | SIG | **+0.2966** | **SIG** | — |
| 人→斑马鱼 | oPCA vs scVI | 15 | -0.2454 | SIG | **-0.1408** | **SIG** | — |
| 人→斑马鱼 | oPCA vs saturn | 15 | +0.0224 | ns | **+0.1270** | **SIG** | ★翻转 |
| 斑马鱼→人 | oPCA vs scVI | 22 | -0.2159 | SIG | **-0.1684** | **SIG** | — |
| 斑马鱼→人 | oPCA vs saturn | 22 | +0.0745 | SIG | **+0.1220** | **SIG** | — |
| 鼠→斑马鱼 | oPCA vs scVI | 15 | -0.1342 | SIG | **-0.1730** | **SIG** | — |
| 鼠→斑马鱼 | oPCA vs saturn | 15 | -0.0785 | SIG | **-0.1173** | **SIG** | — |
| 斑马鱼→鼠 | oPCA vs scVI | 4 | -0.0600 | SIG | **-0.2259** | **SIG** | — |
| 斑马鱼→鼠 | oPCA vs saturn | 4 | +0.1227 | SIG | **-0.0431** | **SIG** | — |

## 结论

**3 条结论在换评估器后翻转：**
- 人→鼠 oPCA vs scVI：KNN 不显著 → LR 显著
- 鼠→人 oPCA vs scVI：KNN 不显著 → LR 显著
- 人→斑马鱼 oPCA vs saturn：KNN 不显著 → LR 显著
