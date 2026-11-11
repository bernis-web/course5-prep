# 配对检验·inductive oPCA 口径复核

> oPCA 换成 **inductive** 变体（PCA 只用源细胞拟合），scVI / SATURN 不变；
> 重抽样单位仍为**个体**。目的是检查 transductive 下的结论是否成立。

| 方向 | 比较 | 聚类 | transductive Δ | 显著 | **inductive Δ** | **显著** | 是否翻转 |
|---|---|---|---|---|---|---|---|
| 人→鼠 | oPCA vs scVI | 4 | -0.0247 | ns | **-0.1498** | **SIG** | ★翻转 |
| 人→鼠 | oPCA vs saturn | 4 | +0.2914 | SIG | **+0.1663** | **SIG** | — |
| 鼠→人 | oPCA vs scVI | 22 | +0.0833 | ns | **-0.1531** | **SIG** | ★翻转 |
| 鼠→人 | oPCA vs saturn | 22 | +0.4582 | SIG | **+0.2217** | **SIG** | — |
| 人→斑马鱼 | oPCA vs scVI | 15 | -0.2454 | SIG | **-0.3047** | **SIG** | — |
| 人→斑马鱼 | oPCA vs saturn | 15 | +0.0224 | ns | **-0.0370** | **SIG** | ★翻转 |
| 斑马鱼→人 | oPCA vs scVI | 22 | -0.2159 | SIG | **-0.3377** | **SIG** | — |
| 斑马鱼→人 | oPCA vs saturn | 22 | +0.0745 | SIG | **-0.0473** | **SIG** | — |
| 鼠→斑马鱼 | oPCA vs scVI | 15 | -0.1342 | SIG | **-0.2024** | **SIG** | — |
| 鼠→斑马鱼 | oPCA vs saturn | 15 | -0.0785 | SIG | **-0.1468** | **SIG** | — |
| 斑马鱼→鼠 | oPCA vs scVI | 4 | -0.0600 | SIG | **-0.0951** | **SIG** | — |
| 斑马鱼→鼠 | oPCA vs saturn | 4 | +0.1227 | SIG | **+0.0877** | **SIG** | — |

## 结论

**3 条结论在 inductive 口径下翻转：**
- 人→鼠 oPCA vs scVI：transductive 不显著（Δ-0.0247）→ inductive 显著（Δ-0.1498）
- 鼠→人 oPCA vs scVI：transductive 不显著（Δ+0.0833）→ inductive 显著（Δ-0.1531）
- 人→斑马鱼 oPCA vs saturn：transductive 不显著（Δ+0.0224）→ inductive 显著（Δ-0.0370）
