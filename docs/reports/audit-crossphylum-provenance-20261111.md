# 跨门 `macro_f1_union` 存值溯源（2026-11-11）

## 目标

`results/phase-20261022/crossphylum/metrics.json` 存的 `macro_f1_union` 是
0.0711 / 0.0732 / 0.0652 / 0.0802，用同文件混淆矩阵重算是 0.0235 / 0.0257 / 0.0241 / 0.0267，
差约 3 倍。本报告回答一个问题：**那组存值到底是哪个公式算出来的？**

## 原理

存值与重算值若差在「口径」，一定能被某种标准口径复现；若 16 种口径都复现不出，
那它就不是口径差异，而是**另一段代码的产物**。判定必须靠穷举，不能靠猜。

关键旁证：存值里的 `acc` 与混淆矩阵的 micro-F1 **完全相等**（0.0575 / 0.0516 / 0.0582 / 0.0457），
说明混淆矩阵与存值**是同一次运行的产物**——所以差异只能出在 `macro_f1_union` 这一段计算上。

## 步骤

```powershell
cd D:\projects\course5-prep
.\.venv39\Scripts\python.exe scripts\trace_crossphylum_mf1.py
```

脚本从混淆矩阵还原 `y_true / y_pred`，然后依次试：

| 变体 | 定义 |
|---|---|
| V1 | 13 类并集 · macro · zero_division=0 |
| V2 | 仅真值出现过的类 · macro |
| V3 | 仅预测出现过的类 · macro |
| V4 | 真值∩预测交集类 · macro |
| V5 | micro |
| V6 | weighted |
| V7 | 并集 · macro · zero_division=1 |
| V8 | 交集 · macro · zero_division=1 |
| P1–P4 | 行/列标签用「插入序 vs 排序」的四种错位组合（模拟标签错配 bug）|
| T1–T13 | top-k 支持度子集 macro（k=1..13）|
| S1–S5 | 支持度阈值 macro（≥50 / 100 / 200 / 500 / 1000）|

## 结果：16 类变体全部复现不出

| 方向 | 存值 | V1（我们的重算） | 变体里最高的 | 差 |
|---|---|---|---|---|
| oPCA 七鳃鳗→鼠 | 0.0711 | **0.0235** | 0.0459（top-6） | 3.0× |
| oPCA 鼠→七鳃鳗 | 0.0732 | **0.0257** | 0.0568（top-4） | 2.8× |
| scVI 七鳃鳗→鼠 | 0.0652 | **0.0241** | 0.0457（top-6） | 2.7× |
| scVI 鼠→七鳃鳗 | 0.0802 | **0.0267** | 0.0701（top-1） | 3.0× |

`acc` 侧逐位相等，证明不是「不同运行」。

## 结论

**存值的来历无法从现有证据复原。** 能确定的是：

1. 混淆矩阵与 `acc` 是可信的、自洽的（micro-F1 逐位相等）。
2. `macro_f1_union` 这一段与同一份混淆矩阵不自洽，且不属于任何标准 macro-F1 口径。
3. 因此**现行一律采用重算值**：0.0235 / 0.0257 / 0.0241 / 0.0267（13 类并集、macro、zero_division=0）。

这和统计战线原来的判定一致，但现在是**穷举过的判定**，不再是一句「差约 3 倍、来源不明」。

## 实现：文件侧处置

`results/phase-20261022/crossphylum/_PROVENANCE.md`：就在 `metrics.json` 旁边，
写明哪个字段能用、哪个字段不许引用。改数字会破坏可信性（`acc` 与混淆矩阵对得上），所以**留值 + 标注**。

## 验证

```powershell
.\.venv39\Scripts\python.exe -c "import json;m=json.load(open(r'results/phase-20261022/crossphylum/metrics.json'));print({k:m[k]['directions'][d]['acc'] for k in ('opca','scvi') for d in m[k]['directions']})"
```

## 坑

- 别用 `f1_score(..., average='macro')` 不带 `labels=` 就去比：sklearn 默认只用**真值与预测并集**，
  与「13 类并集」差 1.6 倍（0.0382 vs 0.0235），很容易被当成「存值对了」。
- top-k 变体里出现过 0.0459 / 0.0568 这类接近值，但四个方向**没有一个能同时对上**，
  所以不是「只在几个大类上算 macro」。

## 下一步

- 若将来要复算跨门，用 `scripts/crossphylum_*.py` 重跑并**直接写 `macro_f1_union_strict` 新字段**，
  不要覆盖旧字段——留着它当反例，比删掉更有价值。