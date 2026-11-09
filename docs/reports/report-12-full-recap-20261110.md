# 报告 12：课题5 全流程复盘 —— 从题目到产物（2026-11-10）

> 本文回答三件事：**题目是什么**、**一步步怎么做到的**、**现在做到了哪一步**。
> 全部数字都有文件与命令出处；凡未完成或未验证的，文中直接标出。

---

## 第 0 部分：一句话总览

课题要求在 **DCS 平台上**把三种跨物种整合方法（SATURN / SAMap / scVI，加上我们自建的 ortholog-PCA 基线）跑成一套**可复现的基准测试**，产出**基准测试报告**与**场景化选型指南**，并覆盖近缘、跨门、无 GPU 三个场景。

**现在状态**：12 项课程要求 **11 项完成、1 项部分**；四项方法的六方向数字全部落地并带置信区间；两处会改变结论的错误已自查并更正；全部产物已推送到公开仓库。

---

## 第 1 部分：题目原文与拆解

### 1.1 课程页面的硬要求（`docs/course-requirements-audit.md` 记录原网页 HTML 558-564）

| 要求 | 我们的落地 |
|---|---|
| 比较 HEART 16 物种 CM/FB（论文发表注释当金标准） | 取其中三个物种心脏 scRNA（人 1,528 / 鼠 1,535 / 斑马鱼 1,543 细胞） |
| 七鳃鳗脑 vs 小鼠脑的跨门类场景 | LBSPA 数据，55,694 细胞（七鳃鳗 41,678 + 小鼠 14,016），共同基因轴 6,222 |
| 评测标签转移 macro-F1 | 统一 union 口径，六方向 |
| 批次混合与生物保守性（kBET / iLISI / silhouette） | 三项指标，三方法并表（SATURN 缺席，理由是重训会造出假对照） |
| 时间与内存 | 平台台账 + 本地白盒测量（进程内 `PeakWorkingSetSize`） |
| 文档与易用性、Agent 友好度 | 六维评分（oPCA 26/30、scVI 次之、SATURN 14/30） |
| 交付报告 + 选型指南，至少覆盖近缘/跨门/无 GPU | 选型指南 v8；三个场景全实验 |
| 因依赖差异大，最终实验需容器化 | `container/` 配方 + 平台镜像 `g5-opca-container` |
| 每组维护 AI 使用日志 | `docs/ai-use-log.tsv` |
| 最终结题报告为 Word | `deliverables/` 下多份 docx |

### 1.2 老师补充的口径（`docs/teacher-data-request.md`）

首轮 2–3 个物种、后期覆盖近缘/远缘/不同类别、空间数据暂不做、单核后置。→ 我们据此定下「三门内物种 + 一组跨门数据」的范围。

---

## 第 2 部分：一步步怎么做到的

### 阶段 1：把数据弄上平台（2026-09-20 前后）

1. 从 STDS0000406 官方 FTP 下载三物种心脏 scRNA，本地校验（大小精确一致 + `anndata` 可读 + 金标准列 `celltype` 存在）；
2. 用**镭速 Raysync 客户端**上传——网页上传有 **100 MB 单文件上限**，而三个文件 153.93 / 259.71 / 213.38 MB 全超；
3. 落盘核对：`/Files/RawData/` 下三条记录，大小与本地逐一精确一致。

> ⚠️ **2026-11-08 实测发现**：`/Files/RawData/` 现在**已不含人/鼠/鱼**，只有 10 个其他物种（平台账户 9-26 写入）。
> 现行全量路径是 `/Files/3/stage3/01_raw_data/heart_omics/scrna/`（人 223,744,070 / 鼠 272,322,064 / 鱼 161,403,920 B）。
> 派生文件 `local_{human,mouse,zebrafish}_s.h5ad` 在 `/Files/` 根目录（26,233,600 / 27,745,005 / 16,931,148 B，sha256 `af41618b…` / `7fda583d…` / `6b1e8798…`）——**这三个才是我们分析实际用的子集。**

### 阶段 2：把方法跑起来（2026-09 至 10）

**平台任务台账（`results/phase-20261030/resource-ledger.json`，数据来自 `getUserTaskById` 的 `analyseDuration` / `analysisAmount`）**

| 方法 | 任务号 | 规模 | 实际计算 | 资源档 | 费用 |
|---|---|---|---|---|---|
| oPCA (FIXKEY v3) | `W202610150090794` | 4,606 × 15,869 | 866 s | 2c8g | ¥0.19 |
| scVI 门内 | `W202610190042919` | 4,606 × 9,018 | 916 s | 2c8g | ¥0.20 |
| scVI 跨门 | `W202610220063725` | 55,694 × 6,222 | 9,773 s | 2c8g | ¥2.06 |
| SAMap 联合嵌入 | `W202610260103163` | 4,606 细胞 | 354 s | 1c4g | ¥0.02 |
| **合计** | **4 个任务** | — | **11,909 s（3h18m）** | — | **¥2.47** |

> 跨门那一次占了总费用 84%——细胞数涨 12 倍、耗时涨 10.7 倍，**近似线性而非平方**。

**关键坑（都记在 `docs/execution/20261030-pitfalls.md`，33 条）**：
- 平台上的 `ortholog_pca_dcs_v3_fixkey.txt`（421 行、读 JSON）和本地 `.py`（383 行、读 TSV）**是两个文件**，同名函数两种实现，拿错就 `JSONDecodeError`；
- 环境变量名 `OPCA_OUT` ≠ `OPCA_OUT_ROOT`，写错会得到「平台标失败但结果其实是好的」假警报；
- 平台报「上传失败」时文件可能已落盘（延迟入库），要自己去列表核对。

### 阶段 3：抹平口径（2026-10-17 至 10-30）

统一 coarse 标签空间 → 统一 **union 口径**（真实 ∪ 预测一起平均，多预测的类记 F1=0）→ 给每个分数配 **bootstrap SE 与 95% CI**（22 格与冻结值逐格对齐，0 mismatch）。

跨门那一处：`metrics.json` 里存的 `macro_f1_union`（0.0652–0.0802）与同文件混淆矩阵重算值（0.0235–0.0267）差约 3 倍，accuracy 两处一致 → 判定**存值来源不明，改用可复现的重算值**。

### 阶段 4：容器化（2026-10-28 至 10-31）

- `container/`：Dockerfile + 依赖精确锁 + entrypoint + 验收清单；
- 修掉一个真缺陷：entrypoint 与脚本的环境变量契约不匹配，会导致容器内 `FileNotFoundError`；
- 平台镜像 `g5-opca-container`（基于 `SATURN--22` + 7 个 pip 精确版本）**构建成功**；
- 镜像内跑完整评估：**6 个冻结 accuracy 逐位复现 6/6**。

> ⚠️ `docker build` 本机从未执行：Docker Desktop 29.8.2 装了但 **WSL 没有发行版**，daemon 起不来。这是唯一未执行的工程步骤。

### 阶段 5：交付物（2026-10-23 至 11-04）

基准报告 docx、选型指南（迭代到 v8）、组员入门手册（22 页）、踩坑清单、老师意见回应、七次汇报 PPT、AI 使用日志。

### 阶段 6：自查与更正（2026-11-08 至 11-09，本轮）

这是本轮最重要的部分——**发现两处会改变结论的错误**。

---

## 第 3 部分：两处更正（本轮核心）

### 更正一：SATURN 评测把物种词表查反了

**现象**：SATURN 在鼠↔鱼两向报出 0.6500 / 0.6510，比 scVI（0.4248 / 0.4786）高出一大截。

**真相**：跨物种迁移里 **真值用目标物种词表、预测用源物种词表**（SATURN 输出参考书那方的原始类型名）。旧代码把两边对调：

```python
# 错误
ct = to_coarse(source_species, truth_label)
cp = to_coarse(target_species,  pred_label)
```

**两类后果**：
1. 真值查不到 → `continue`，细胞静默消失（小鼠 `Cardiomyocyte`/`Epicardium`/`Valve` 不在人词表 → 人→鼠分母 1535→1309）；
2. 预测查不到 → 记成「不可映射」再丢一次（人的 `Atrial Cardiomyocyte`/`Mast cell` 不在小鼠词表）。

**判定实验**（`scripts/convention_variants.py`）：四种约定重算，**只有错的那种能复现全部旧值（6/6）**；accuracy 交叉验证同样 6/6。

**修正后**（v2 签认映射，`strict_cell` 口径）：

| 方向 | 旧值 | 修正值 | 虚高 |
|---|---|---|---|
| 人→鼠 | 0.4147 | **0.3522±0.0127** | +0.0625 |
| 鼠→人 | 0.4010 | **0.2566±0.0140** | +0.1444 |
| 人→斑马鱼 | 0.2479 | **0.1282±0.0091** | +0.1197 |
| 斑马鱼→人 | 0.4021 | **0.1386±0.0060** | +0.2635 |
| 鼠→斑马鱼 | 0.6500 | **0.4076±0.0143** | +0.2424 |
| 斑马鱼→鼠 | 0.6510 | **0.2961±0.0116** | +0.3549 |

**结论影响**：推荐骨架不变（scVI 远缘最优），但「SATURN 曾在大方向上领先」不成立——它**一个方向都不赢**。

### 更正二：mapping 表三行

- `zebrafish|Orthers`（`Others` 的拼写错误，仅 30 个细胞）从 `neural` 改为**退出评估**；
- `mouse|Valve`、`zebrafish|Perivascular cells` 保留归类，但补全「披露四项」（依据/备选/偏差方向/敏感性）；
- 38 行 `reviewer` 从全 `pending` 改为**签认留痕**（30 canonical + 5 disclosed_choice + 3 excluded）。

**副作用（必须记住）**：`Orthers` 退出后，`zebrafish→human` 又出现丢样本现象（`published` 口径 0.2501 vs `strict_cell` 0.1386）。**只要映射表里有 unmapped 类，丢样本口径就会系统性抬高分数 → 对外一律用 `strict_cell`。**

---

## 第 4 部分：最终数字（现行口径）

四方法 × 六方向，coarse macro-F1（union 口径，strict_cell），带 bootstrap SE：

| 方向 | oPCA | scVI | SATURN | SAMap | 最优 |
|---|---|---|---|---|---|
| 人→鼠 | 0.6435±0.0186 | **0.6683±0.0206** | 0.3522±0.0127 | 0.1127±0.0141 | scVI |
| 鼠→人 | **0.6729±0.0215** | 0.5895±0.0140 | 0.2566±0.0140 | 0.0401±0.0051 | oPCA |
| 人→斑马鱼 | 0.1654±0.0152 | **0.4014±0.0117** | 0.1282±0.0091 | 0.0477±0.0042 | scVI |
| 斑马鱼→人 | 0.1512±0.0070 | **0.4290±0.0119** | 0.1386±0.0060 | n=0 | scVI |
| 鼠→斑马鱼 | 0.2177±0.0135 | **0.4248±0.0155** | 0.4076±0.0143 | n=0 | scVI |
| 斑马鱼→鼠 | 0.4405±0.0144 | **0.4786±0.0114** | 0.2961±0.0116 | n=0 | scVI |

**scVI 五向最优，oPCA 一向（鼠→人）领先**；领先幅度（如斑马鱼→人 0.29）远大于两者 SE（0.006–0.012），不受抽样波动影响。

**跨门（七鳃鳗↔小鼠）**：oPCA / scVI 的 accuracy 4.6–5.8%，低于 13 类随机猜 7.7%；macro-F1（0.0235–0.0267）**低于多数类基线**（0.0274 / 0.0360）。负结果，且换用可复现口径后**更强**。

**批次混合**：三方法都没把物种混匀（iLISI 1.006–1.120，满值 3）；scVI 三项相对最好但绝对水平低。

---

## 第 5 部分：算力分布（回答「需要算力的部分是否都在平台上做完」）

**是的，所有重计算都在平台上做完了，共 4 个任务、11,909 秒、¥2.47**（台账见上）。

| 类型 | 在哪做 | 说明 |
|---|---|---|
| 四方法建模/训练/嵌入 | **DCS 平台** | oPCA、scVI（门内+跨门）、SAMap；SATURN 训练更早完成（GPU 任务，平台未记录 CPU/内存字段） |
| 镜像构建与镜像内复现 | **DCS 平台** | `g5-opca-container`，6/6 逐位复现 |
| 口径审计、重算、判定实验 | **本机** | 纯 Python 读混淆矩阵，无重算力需求（`convention_variants.py` 等） |
| bootstrap 置信区间 | **本机** | 1000 次重抽样，秒级 |
| `docker build` | **未执行** | 本机无 WSL 发行版；配方已验，平台镜像已覆盖等价验证 |

**结论**：需要 GPU / 大规模算力的部分**没有一项留在本地**。

---

## 第 6 部分：产物清单（现行版）

### 6.1 核心交付物

| 文件 | 说明 |
|---|---|
| `deliverables/场景化选型指南-v8-20261109.md` | **课程核心交付物（现行）** |
| `results/stage-reports-20261102/课题5-三场景结论与可复现闭环-v2-20261109.pptx` | **对外版汇报 PPT（15 页）** |
| `deliverables/课题5-总交接文档-20261028.docx` | 技术总交接（含更正声明） |
| `deliverables/课题5-组员入门手册-20261104.docx/.pdf` | 22 页入门，第 3 章已按新机制重写 |
| `deliverables/课题5-数据更正说明-20261109.pptx` | 4 页更正附页 |
| `deliverables/课题5-踩坑清单-20261030.docx` | 33 条实测坑 |
| `deliverables/课题5-老师七条意见回应-20261030.docx` | 逐条回应 |
| `deliverables/course5-final-report-v2-20261023.docx` | 基准测试报告 |
| `deliverables/课题5-组员交接总纲-20261104.docx/.pdf` | 15 页组员交接 |

### 6.2 数据与证据

| 路径 | 内容 |
|---|---|
| `config/heart-celltype-map-v2.tsv` | **签认版映射表**（38 行） |
| `results/bootstrap-20261030/saturn_convention_v2.json` | v1 口径 SATURN 三口径 |
| `results/bootstrap-20261030/saturn_convention_mapv2.json` | **v2 签认口径** |
| `results/bootstrap-20261030/saturn_bootstrap_fixed*.json` | **修正后 SE 与 95% CI** |
| `results/bootstrap-20261030/convention_variants.json` | 四约定判定实验 |
| `results/bootstrap-20261030/mapping_v2_sensitivity.json` | 三行改动敏感性 |
| `results/phase-20261030/resource-ledger.json` | 平台算力台账 |
| `results/stability-20261030/` | 10 seed + 20 次扰动 |

### 6.3 复盘与索引文档

| 文件 | 说明 |
|---|---|
| `docs/reports/report-09-corrections-20261108.md` | 更正一（词表方向）+ 数据路径 |
| `docs/reports/report-10-mapping-v2-proposal-20261108.md` | mapping v2 提案 |
| `docs/reports/report-11-mapping-signoff-20261109.md` | 签认范围与责任边界 |
| `docs/execution/20261108-更正索引.md` | **哪些文件还能引、哪些作废** |
| `docs/execution/20261028-master-handoff.md` | 技术总交接（540+ 行） |
| **本文** | 从题目到产物的全流程 |

---

## 第 7 部分：还没做的（如实列出）

| 项 | 状态 | 说明 |
|---|---|---|
| `docker build` 实跑 | 未做 | 需 WSL 发行版或有 Docker 的机器；配方已验，平台镜像已给出等价证据 |
| 生物学同行抽查 | 未做 | 签认由项目负责人授权、AI 复核；投稿前建议找心脏发育/免疫方向的人抽查 20% |
| 留出 / inductive 评估 | 明确不做 | 需新协议与预算；现有结论只声称 transductive |
| SATURN 批次指标 | 明确不做 | 重训会产出不同表示，造成假对照 |
| 排总分冠军 | 明确不做 | 分母/特征空间/训练方式/统计强度都不同 |
| 镜像内 6 值复现的口径标注 | 待办 | 镜像里嵌的是 **v1** 映射；换 v2 需重跑或标注 |

---

## 第 8 部分：三条纪律（改任何东西之前先读）

1. **不把 transductive 写成 held-out / inductive**；
2. **不按总分排冠军**，只做「场景 → 方法」；
3. **限定语随数字一起出现**：任何 macro-F1 引用必须带「union 口径 + 分母 + strict_cell」。

另外两条工程纪律：**不覆盖旧文件**（新版本另存）；**数字从文件读，不凭记忆写**。

---

## 附：复算命令

```bash
# 判定实验：哪种词表约定能复现旧值
python scripts/convention_variants.py

# SATURN 修正口径（v1）
python scripts/saturn_convention_audit_v2.py

# SATURN 签认口径（v2）
MAP_TSV=config/heart-celltype-map-v2.tsv python scripts/saturn_convention_audit_v2.py

# 修正后的 SE 与 95% CI
python scripts/bootstrap_saturn_fixed.py
MAP_TSV=config/heart-celltype-map-v2.tsv OUT_NAME=saturn_bootstrap_fixed_mapv2.json \
  python scripts/bootstrap_saturn_fixed.py

# 三行候选改动的敏感性
python scripts/mapping_v2_sensitivity.py
```
