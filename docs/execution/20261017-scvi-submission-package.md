# scVI 跨物种臂：提交与审阅材料（2026-10-17）

> ⚠️ **本节数字已作废（2026-11-11 标注）**：见 `docs/reports/number-index-20261111.md` 与 `docs/execution/20261108-更正索引.md`。本文件按当时口径保留，不回改。

> 用户已批准（2026-10-17）：scVI 跨物种臂 + 鱼方向口径修正，均批准。
> 本文件是提交 DCS 前的完整材料，供 GenPilot 审阅与执行。

---

## 一、脚本

| 项 | 值 |
|---|---|
| 路径 | `scripts/scvi_cross_species.py` |
| 大小 | 16,548 B / 383 行 |
| SHA-256 | `498afeaa817c057b…`（全值见 `sha256sum`） |
| 语法 | ✅ `ast.parse` 通过 |
| 本地逻辑验证 | ✅ `layer_labels` / `macro_f1` / 基因轴对齐 均已实测 |

---

## 二、设计要点（供审阅）

### 2.1 方法

三物种**联合训练**一个 scVI 模型（`batch_key="species"`），取潜空间后做 6 方向 KNN 标签迁移。

| 项 | 值 | 依据 |
|---|---|---|
| n_latent | 10 | 沿用历史 scVI 协议 |
| max_epochs | 50 | 小数据（4,606 细胞）需更多轮次 |
| early_stopping | True | 防过拟合 |
| batch_key | species | LBSPA 论文同做法 |
| KNN | K=15, cosine, distance-weighted | **与 oPCA 完全一致** |
| 主指标 | macro-F1 | 课程要求 |
| 置换检验 | 200 次, RandomState(0) | 与 oPCA 一致 |

### 2.2 基因轴对齐（关键设计）

三物种投影到**共同的 human 基因轴**：

- human：直接用自身基因名
- mouse：经 `hm`（人-鼠 1:1）映射到 human 基因名
- zebrafish：经 `fh`（人-鱼 1:1，**已修正方向**）映射到 human 基因名
- **共同轴 = 8,852 个基因**（三物种同时可映射）

**实测**：mappable mouse 15,869 / zebrafish 9,131 / 三物种交集 **8,852**。

### 2.3 与 oPCA 的口径一致性

| 项 | oPCA (v3_fixkey) | scVI（本脚本） |
|---|---|---|
| 归一化 | normalize_total(1e4)+log1p（全基因空间） | **同** |
| 基因去重 | 首现去重 | **同** |
| 映射方向 | 已修正（fh 键=人基因） | **同** |
| 标签层 | layer_labels 三档 | **同（逻辑逐行复刻）** |
| KNN | K=15 cosine distance | **同** |
| 置换 | 200 × RandomState(0) | **同** |
| 主指标 | accuracy + macro-F1 | **同** |
| **差异** | 每方向独立 PCA-50 | **一次联合训练 + latent-10** |

**这个差异必须在报告中披露**（与 SATURN 一样是"一次训练多方向评估"，而 oPCA 是"每方向独立"）。

---

## 三、请 GenPilot 审阅的问题

1. **`batch_key="species"` 是否合适**？
   跨物种 scVI 的核心权衡：batch 校正太强会抹掉物种差异（KNN 只能靠噪声），太弱则物种主导（标签迁移失败）。
   历史上有没有在本项目数据上跑过跨物种 scVI 的经验？

2. **n_latent=10 / max_epochs=50 对 4,606 细胞是否合适**？
   历史 scVI 是 3 万/6 万/5 万细胞。现在只有 1,500/物种。

3. **基因轴 8,852 是否够**？
   oPCA 用的两两组合是 15,869 / 9,131 / 8,160。三物种共同轴 8,852 介于中间。
   会不会因为轴变小而系统性压低 scVI 表现？

4. **运行时长预估**？
   4,606 细胞 × 8,852 基因 × 50 epochs，CPU 1c4g 大概多久？

5. **镜像里 scvi-tools 版本**？
   历史是 1.1.6.post2。当前 `SATURN--22` 镜像里还是这个版本吗？

---

## 四、提交规格（待执行）

| 项 | 值 |
|---|---|
| 任务名 | `g5-scvi-cross-species-r1` |
| 镜像 | `SATURN--22` |
| 资源 | **2c8g**（小数据，CPU 足够） |
| 脚本输入 | `/Files/ResultData/Notebook/scvi_cross_species.txt` |
| pylibs | `/Files/ResultData/Notebook/pylibs_full.tar.gz`（若 scVI 不在镜像内） |
| 数据输入 | `/Files/local_{human,mouse,zebrafish}_s.h5ad` + `/Files/wheelhouse/orth-*` + `heart-celltype-map-v1.tsv` |
| 输出 | `./scvi-cross-<UTC>/` |
| 预期产物 | metrics.json（6方向×3层，含 macro_f1）+ latent.npy + 18 predictions + manifest |
| 费用上限 | **≤1 元** |
| 停止条件 | 非0退出 / OOM / 费用超限 → 停止，不重投 |

---

## 五、执行顺序

1. **上传脚本**：`scvi_cross_species.py` → `scvi_cross_species.txt` → `dcs data push` 到 `/Files/ResultData/Notebook/`
2. **确认镜像有 scvi-tools**（`python -c "import scvi; print(scvi.__version__)"`）
3. **提交 WDL 任务**（opca_v2 流程，2c8g）
4. **监督**：每 10 分钟检查，完成即回收产物
5. **核对**：6 方向 × 3 层 macro-F1，与 oPCA/SATURN/SAMap 同表对比

---

## 六、预期结果（供对照）

若 scVI 表现合理，粗估（**仅为预期，不是预测**）：

| 方向 | oPCA macro-F1 | SATURN macro-F1 | scVI 预期区间 |
|---|---|---|---|
| 人 → 鼠 | 0.6435 | 0.4147 | 0.40–0.75 |
| 鼠 → 人 | 0.6729 | 0.4010 | 0.40–0.75 |
| 人 → 斑马鱼 | 0.1682 | 0.2479 | 0.10–0.35 |
| 斑马鱼 → 鼠 | 0.4396 | 0.6510 | 0.30–0.65 |

**注意**：若 scVI 结果异常（全 0 或远高于 oPCA），需先查 batch 校正强度与基因轴对齐，不要直接下结论。

---

## 七、边界

- 未提交任何 DCS 任务
- 未修改任何冻结件
- 未在本地安装 torch/scvi（遵守"运算走 DCS"）
- 费用上限 1 元
