# oPCA 映射 bug 影响范围分析（2026-10-15）

> ⚠️ **本节数字已作废（2026-11-11 标注）**：见 `docs/reports/number-index-20261111.md` 与 `docs/execution/20261108-更正索引.md`。本文件按当时口径保留，不回改。

> 目的：判定 `ortholog_pca_local_v1.py` 的键方向 bug 影响了哪些已发布结论、哪些不受影响。
> 方法：只读核对 + 本地复现，不修改任何冻结件。

---

## 一、影响范围（逐脚本排查）

排查了仓库中全部读取直系同源文件的脚本：

| 脚本 | 映射构造方式 | 方向 | 是否受影响 |
|---|---|---|---|
| `scripts/ortholog_pca_local_v1.py` | `one_to_one()` → 键=**鱼**基因 | ❌ **错** | **受影响**（冻结数字来源） |
| `scripts/ortholog_pca_v98_final.py` | `h2f` → 键=**人**基因 | ✅ 对 | 不受影响 |
| `scripts/run_samap_compliant_v98.py` | `h2f` → 键=人基因 | ✅ 对 | 不受影响 |
| `scripts/run_samap_compliant_v98_dcs.py` | `h2f` | ✅ 对 | 不受影响 |
| `scripts/ortholog_pca_dcs_v2.py`（平台） | `h2f` | ✅ 对 | 不受影响 |
| `scripts/ortholog_pca_full_isolated.py` / `task1_isolated.py` | 隔离 wrapper，继承源脚本逻辑 | — | 见下 |

**结论：只有 `ortholog_pca_local_v1.py` 一个脚本有键方向 bug。**

### 冻结数字的来源确认

`results/pilot-v1/ortholog-pca-v98/manifest.json` 记录 `script_sha256 = 6582d873…0c44`，
与磁盘 `scripts/ortholog_pca_local_v1.py` **逐字符匹配** → **冻结的 18 格数字全部来自有 bug 的脚本**。

### SAMap 不受影响（重要）

`run_samap_compliant_v98.py:306-317` 用的是：

```python
fh_raw = zfin(BASE / "ortholog" / "human_orthos.txt")
h2f = {}; f2h = {}
for fish, hs in fh_raw.items():
    if len(hs) == 1:
        hh = next(iter(hs)); h2f.setdefault(hh, []).append(fish); f2h[fish] = hh
fh = {h: fl[0] for h, fl in h2f.items() if len(fl) == 1}   # 键 = 人基因 ✅
```

→ **方向正确**，与平台脚本一致。**SAMap 的 0.1050 等数字不受此 bug 影响。**

---

## 二、对结论的实质影响（关键判定）

### 2.1 数值变化

| 方向 | 层 | 冻结 | 修正 | 绝对差 | 相对差 |
|---|---|---|---|---|---|
| human→mouse | 全部 | 0.7824/0.8618/0.7980 | 同 | **0** | **0.0%** |
| mouse→human | 全部 | 0.4084/0.7369/0.4103 | 同 | **0** | **0.0%** |
| human→zebrafish | exact | 0.1698 | 0.1504 | −0.0194 | −11.4% |
| human→zebrafish | coarse | 0.1961 | 0.1795 | −0.0166 | −8.5% |
| human→zebrafish | fine | 0.1801 | 0.1608 | −0.0193 | −10.7% |
| mouse→zebrafish | exact | 0.1659 | 0.1640 | −0.0019 | −1.1% |
| mouse→zebrafish | coarse | 0.2755 | 0.2675 | −0.0080 | −2.9% |
| mouse→zebrafish | fine | 0.1748 | 0.1721 | −0.0027 | −1.5% |
| zebrafish→human | exact | 0.1453 | 0.1387 | −0.0066 | −4.5% |
| zebrafish→human | coarse | 0.1813 | 0.1734 | −0.0079 | −4.4% |
| zebrafish→human | fine | 0.1695 | 0.1610 | −0.0085 | −5.0% |
| zebrafish→mouse | exact | 0.4769 | 0.4710 | −0.0059 | −1.2% |
| zebrafish→mouse | coarse | 0.5761 | **0.5814** | **+0.0053** | **+0.9%** |
| zebrafish→mouse | fine | 0.5010 | 0.5003 | −0.0007 | −0.1% |

### 2.2 定性结论是否翻转 —— **全部未翻转**

对每一格，检查"acc 是否高于多数类基线（majority）"这一核心定性判断：

| 方向 | 冻结 | 修正 | 判定是否翻转 |
|---|---|---|---|
| human→mouse | 三格均远高于 majority | 同 | **未翻转** |
| mouse→human | 三格均远高于 majority | 同 | **未翻转** |
| human→zebrafish | 三格均低于 majority | 同 | **未翻转** |
| mouse→zebrafish | 三格均低于 majority | 同 | **未翻转** |
| zebrafish→human | 三格均低于 majority | 同 | **未翻转** |
| zebrafish→mouse | 三格均高于 majority | 同 | **未翻转** |

**核心结论：bug 修正后，数值变化但所有定性结论保持不变。**

具体来说：

- "ortholog-PCA 在人-鼠方向表现良好（0.86/0.74 coarse）"——**不变**
- "含斑马鱼方向普遍低于多数类基线"——**不变**（修正后更低，判定更强）
- "鱼→鼠方向是唯一接近/超过基线的鱼方向"——**不变**（修正后 coarse 还略升）

### 2.3 受影响的具体材料

| 材料 | 影响 | 说明 |
|---|---|---|
| 汇报 4（ortholog-PCA 基线闭环） | ⚠️ 数字需更新 | 含鱼方向数字 |
| 汇报 7（三方法总矩阵） | ⚠️ 数字需更新 | 含鱼方向数字 |
| 汇报 3/5/6 | 视是否引用鱼方向数字 | 需逐页核对 |
| Word 终版报告 | ⚠️ 数字需更新 | 同上 |
| **SAMap 相关全部材料** | ✅ **不受影响** | SAMap 脚本方向正确 |
| **人-鼠方向全部数字** | ✅ **不受影响** | 两口径完全一致 |

---

## 三、建议处置（待项目负责人/导师裁定）

| 选项 | 说明 | 影响 |
|---|---|---|
| **A. 更新为修正口径** | 用 v3_fixkey 数字替换冻结的 4 个鱼方向 | 更正确；需改汇报 4/7、Word；人-鼠与 SAMap 不动 |
| B. 保留冻结口径 + 加勘误说明 | 在材料中注明鱼方向数字存在已知映射缺陷 | 改动最小；但对外数字已知有误 |
| C. 双口径并列 | 主表用修正值，附注列冻结值 | 最透明；但表格变复杂 |

**执行者建议**：选 **A**。理由：
1. 修正后的口径**语义正确**（已由 GenPilot 独立复核确认）；
2. 所有定性结论**不受影响**，因此材料的主体论述无需重写，只需替换数字；
3. 人-鼠方向与 SAMap 完全不动，改动面可控（4 个方向的 12 格）；
4. 保留已知错误的数字对外发布，风险高于改表成本。

**注意**：无论选哪个选项，都必须**另存新版本**，不覆盖既有 PPT/Word（遵守"不覆盖旧件"约束）。

---

## 四、边界声明

- 本分析全程**只读**：未修改任何冻结件（`results/pilot-v1` 零触碰）
- 未运行任何模型运算（仅本地复现基因集构造逻辑，CPU 秒级）
- 未提交任何 DCS 任务
- 数字来源：冻结 `metrics.json`（SHA `b2b3ac6b…c725`）与 v3_fixkey 产物（SHA `b97e808a…`）
