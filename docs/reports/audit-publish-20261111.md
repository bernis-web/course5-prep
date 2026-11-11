# 发表路线审计：三条路线的最短可行路径与缺项清单

> 日期：2026-11-11 · 项目：`D:\projects\course5-prep` · 状态：**v1.0（已走 Claude 复核，采纳/不采纳见文末）**
> 性质：发表可行性审计。**本文件不新增任何未跑出的数字**；所有数值带文件出处，凡"未做"一律标注。
> 全文只写事实、差距、判断，不写鼓励。

---

## 目标

一句话：在不新增 GPU 预算的前提下，给出三条发表路线各自的最早可投日期、命中概率、已有/缺项，并把"不做就会被一审打死"的动作排序。

---

## 前提核实（含本轮新查到的六处硬矛盾）

| # | 事实 | 出处 | 对发表的影响 |
|---|---|---|---|
| F1 | 统一指标表 42 行：oPCA 12 行 v2、SATURN 12 行 v2、**scVI 12 行 v1**、**SAMap 6 行 v1** → **18 行仍是 v1 口径** | `results/current-20261111/current-table.tsv:14-31` | 主结论踩在 18 行待重跑数据上 |
| F2 | **n_q 跨方法不统一**：同一方向 SAMap 307 / scVI 1,528（鼠→人）；人→鼠 oPCA 1,505 / SAMap 1,368 | `current-table.tsv:26-29` vs `:16` | "strict_cell 对不上算错"在 scVI/SAMap 行上**没有落实**；strict_cell 与 intersection 两种口径目前混用 |
| F3 | **SAMap 只有 3 向**（人→鼠、鼠→人、人→斑马鱼），`斑马鱼→人`/`鼠→斑马鱼`/`斑马鱼→鼠` 三向无数据 —— 是"0 覆盖"还是"未跑"必须在稿中二选一写明 | SAMap 仅 6 行 | 现表"四方法 × 六向"实为"四方法 × 3 向 + 三方法 × 3 向"，这句话不能写 |
| F4 | **4,606 是三物种合计，不是人↔鼠 pair 规模**：1,528 + 1,535 + 1,543 = 4,606；人↔鼠 pair 实为 3,063 | `docs/transductive-formal-v74-evidence-20260928.md:14` | 写 "4,606 cells across human and mouse" 会被当规模虚报 |
| F5 | 同一比较在**三种设置**下三个答案（KNN+逐细胞 / KNN+按个体 / LR+按个体），3 条结论翻转 | `docs/reports/report-15-paper-evidence-v0.1-20261111.md` §2.2b | "近缘打平"不是事实，是特定设置下的读数 |
| F6 | 近缘两向 macro-F1：人→鼠 0.6435(oPCA) vs 0.6683(scVI)；鼠→人 0.6729(oPCA) vs 0.5895(scVI) | `current-table.tsv:2-5,15,17` | 按方向是**各赢一向**；两向平均 oPCA 0.6582 / scVI 0.6289（oPCA 高 0.029）。"打平"只能作"差异不显著"解 |
| F7 | 全部结果均为 **transductive/in-sample**，正式表述已写入 v74 证据末段 | `docs/transductive-formal-v74-evidence-20260928.md` | 最大的一击必杀点；但**已有成文口径**，缺的是对照数字 |
| F8 | inductive pilot **设计完成、未运行**（3 物种 × 3 方法 × 3 seed = 81 格，GPU 需预算审批） | `docs/plans/inductive-pilot-manifest-v1.md` 首行 | 可先跑 CPU 臂（oPCA + SAMap，18 格），不必等 GPU |
| F9 | 跨门负结果：macro-F1 0.0235–0.0267 < 多数类基线 0.0274/0.0360；accuracy 4.6–5.8% < 7.69%（=1/13，13 类）——**但只跑了 oPCA/scVI 两个方法** | 任务给定；`docs/reports/report-05-cross-phylum-20261022.md` | 双指标同时低于基线，方向稳固；但"这一族方法都不行"推不出来，只能写"这两法在此设置下"。且 accuracy 低于随机是**映射错误的典型信号**，审稿人会反推"是不是又一个 bug"（见 F11） |
| F10 | 映射表 v2 的签认范围 = 30 行 canonical 由**项目负责人授权**、复核由**AI 程序化生成**；**未逐行生物学同行复核**，报告明确建议"对外发论文前找同行抽查 20%" | `docs/reports/report-11-mapping-signoff-20261109.md` §一 | 真值映射是全文地基，签认层级必须写进 Methods，否则等于把责任边界藏起来 |
| F11 | 已自曝过一次评测代码 bug（词表反转，抬高 0.0625–0.3549） | `docs/execution/20261111-obsolete-numbers.md` 作废 1 | 审稿人默认"你还会犯第二次" → 负结果必须配**正对照**才能自证评测没坏 |

### 分母规则已查明（本轮复核修正）

先前记录写"30 个细胞丢失原因未记录"，实际规则是存在的、只是没写进指标表：

- 人→鼠 分母 **1,505 = 鼠 1,535 − 30**（`mapping_status ≠ active`：鼠 30 / 鱼 44 / 人 0，见 `scripts/build_final_report.py:106`）。
- 鱼相关方向 **v1 = 1,543 − 44 = 1,499**；**v2 = 1,543 − 74 = 1,469**——再减的 30 行是 v2 里 R37 `Orthers`（`unresolved`）退出评估（`report-11` §一）。
- 结论：**1,505 / 1,499 / 1,469 三个分母都是"映射版本 × 排除规则"的产物，不是评测 bug**。但它们必须进表、进脚注，否则读者没法复算。

### 由此得到的唯一可辩护主 claim

```
不可辩护：scVI 是六向中五向最优的方法。
可辩护　：跨物种标签迁移的"哪个方法更好"不是方法的属性，是
          (口径 × 映射版本 × 重抽样单位 × 评估器 × 标签粒度) 的函数；
          统一口径后远缘四向 scVI 稳定领先，近缘两向各赢一次；
          跨门迁移在 oPCA/scVI 两法、transductive 这个最有利设置下
          仍低于多数类基线 —— 是上界性质的失败，不是信息不足。
```

**这条变更决定三条路线的选题**：不写"方法排名"，写"排名如何被口径决定 + 跨门失败边界"。前者一重跑就可能翻，后者不会。

---

## ① 三条路线对照表

| 维度 | ① workshop 短文 | ② methods note | ③ 完整 benchmark |
|---|---|---|---|
| 定位一句话 | 负结果 + 评测口径如何改写结论 | "物种词表反转"这一类评测陷阱 + 可复用 harness | 跨物种迁移的系统 benchmark 与选型边界 |
| 典型 venue | ICLR/NeurIPS workshop（LMRL、单细胞基础模型类）、MLCB、NeurIPS **Datasets & Benchmarks**（截稿约 2027-05）、Bioinformatics 短报 | Bioinformatics Applications Note（2 页）、Bioinformatics Advances、GigaScience Technical Note、PLOS Comp Biol Software | Genome Biology（首选）、Briefings in Bioinformatics（次选）、Nature Methods（上限） |
| 典型篇幅 | 4–6 页 + 附录 | 2–4 页 + 代码仓库 | 10–14 页 + 补充材料 |
| 审稿关注点（按命中率排序） | ① 有没有"新东西"（纯 benchmark 易判 engineering）② 负结果是否只是子集/实现问题 ③ 统计强度（n=4 donors 的方向）④ 与 scIB/OpenProblems 的差异 | ① "你们自己写错"还是"一类通用错误" ② 软件可用性 ③ 影响面量化 ④ 复现门槛 | ① 规模 ② 公平性（预算/seed/输入对齐）③ 统计单位 ④ 外部验证 ⑤ 结论可操作性 ⑥ 数据代码可用性 |
| 已有 | 六向主表（oPCA/SATURN 为 v2）、bootstrap ±SE 4,000 次、配对检验、词表反转判定实验（四种查表只有错的那种复现旧数字）、映射 38 行签认、容器复现 6/6 | 同左 + 42 行指标表 + 判定实验 + 容器 6/6 + 作废清单（`obsolete-numbers` 三类作废原因 M/V/D） | 同左 + 批次三指标 + 跨门 55,694 负结果（两方法）+ 时间/内存部分数据 |
| 缺 | 分母规则进表、scVI 12 行 + SAMap 6 行 v2 重跑、Δ(transductive−inductive) 表、正对照 oracle | CLI + 文档 + CI + license + DOI；**≥2 个公开流程的同构反转实验**（把"我们的 bug"升级为"一类 bug"） | 全量重跑、SATURN 3 seeds + 预算表、外部验证集、SAMap 三向、BH/FDR、正对照 |
| 最快投稿（稳健） | **2027-02 底**（NeurIPS 2027 workshop / D&B 截稿约 5 月，取更近者） | **2027-03 中** | **2027-10**（Genome Biology）；Briefings 可 2027-09 |
| 最快投稿（激进） | 2027-01 下旬（须 12/04 关 gate，见⑤） | 2027-02 中 | 2027-07（须全量与外部验证同时到位） |
| 命中概率 | **中**（激进档下）→ **高**（gate 关闭 + 正对照齐后） | **中** | **低**（现状）→ **中**（补齐 P0 + 全量 + 外部验证后） |
| 一句话风险 | 被判"没有新方法"；负结果被判"又一个 bug" | 被判"case report，通用性不足" | 被判"子集 + 未调优 + 残缺矩阵，撑不起排名结论" |
| 与其余两条关系 | 与②③**不互斥、可串行**：同一套重跑产物喂三条线 | 复用①的 protocol 与 harness | 复用①②的 protocol、图、release |

### 路线 ①：workshop 短文（4–6 页）

**篇幅结构建议**（4 页正文 + 1 页参考）：1 页问题与负结果、1.5 页口径三因素（映射版本 / 重抽样单位 / 评估器）、1 页跨门边界、0.5 页结论。图 3 张：主表热图、Δ 表、跨门 vs 基线 + oracle 线。

**常见审稿关注点**

1. 是否只是把已有方法在已有数据上重跑（"no new method"）。→ 用"口径决定结论"的主张挡。
2. 负结果是否由实现错误造成。→ 我们有判定实验（四种查表只有错的那种能复现旧数字 0.0625–0.3549），**但还需要正对照**：同一套 strict_cell 在近缘上能给出正结果，才能证明评测没坏。
3. n=4 donors（人→鼠、斑马鱼→鼠）的方向 SE 不可靠（`report-15` §2.1：逐细胞重抽样低估 1.47–3.88 倍）。
4. 与 scIB / OpenProblems 的增量——答案应是"口径维度"而非"更多方法"。

**已有 vs 缺**

| 已有 | 缺 |
|---|---|
| 六向主表（oPCA/SATURN v2 实测） | scVI 12 行 + SAMap 6 行 → v2（含分母规则） |
| bootstrap 4,000 次 + 配对检验 | donor-level 重抽样作为正文默认口径（现两套并存） |
| 词表反转判定实验（可复现旧数字） | Δ(transductive − inductive) 表 |
| 容器镜像 6/6 复现 | 正对照 oracle（跨门 + 近缘各一） |
| 跨门负结果（双指标 < 基线，两方法） | SAMap 三向（0 覆盖需说明） |

**最快投稿时间**：稳健 2027-02 底（NeurIPS 2027 workshop 或 D&B）；激进 2027-01 下旬（ICLR 2027 workshop，须 12/04 关 gate，截稿以官网为准）。

**命中概率：中（现状）→ 高（gate 关闭后）**，理由：
1. 4–6 页不要求全量、不要求外部验证——现有证据链已过篇幅门槛；但**门槛不是篇幅，是"评测自证"**：自曝过一次 bug 的团队，必须用正对照证明这次没坏，否则负结果 = null result。这一条决定它是"中"还是"高"。
2. 题材稀缺：workshop 投稿多数是"新方法 SOTA"，"我们发现了自己评测代码的错误并证明它如何改写结论"是可复现的方法学故事，PC 缺这类稿。
3. 最大失败模式（"engineering report"）可用一句话挡掉：主张写"评估协议改变跨物种迁移结论"，不写"scVI 最好"。前者不依赖排名，后者依赖。

### 路线 ②：methods note（2–4 页）

**篇幅结构建议**：Problem（1 段）→ 反转机制与最小复现（1 图）→ 影响量化（1 表：抬高 0.0625–0.3549、排名翻转条数）→ 通用性证据（≥2 个公开流程）→ 检查清单（最容易被引用）→ 可用性（安装/测试/DOI）。

**常见审稿关注点**

1. **"这是你们自己写错，不是领域问题"** ← 第一打回理由，本路线成败点。
2. 软件可用性：Applications Note 硬门槛是"tool 可用 + 有人用"，需要 CLI、README、CI、license、Zenodo DOI。
3. 影响面量化：多少已发表结果可能受影响（按"用 SATURN 且做跨物种映射"的论文清单估）。
4. **机制不能混写**：本项目历史上有两个互相冲突的说法——"不可映射预测退出分母（0.04–0.19）"与"物种词表反转（0.0625–0.3549）"。前者已在 `obsolete-numbers.md` 作废 1 明确废止，**稿中只能出现后者**。任何文档里仍写前者的段落一律不能引。

**已有 vs 缺**

| 已有 | 缺 |
|---|---|
| 判定实验：四种查表方式只有错的那种复现全部旧数字 | **通用性证据**：SATURN 官方 tutorial、SAMap mapping 输出、scVI label-transfer 教程上各构造一次同构反转 |
| 作废清单（三类作废原因 M/V/D） | 可安装 CLI（现为 `scripts/` 下 130+ 个 py，无统一入口） |
| 容器 6/6、映射 38 行签认、抬升 0.0625–0.3549 | 文档站 / CI / license / DOI |
| — | 影响面统计（哪些论文/流程用了同一约定） |

**最快投稿时间**：2027-03 中。核心增量（通用性实验 + CLI 化）约 3–4 周，与路线①写作并行。

**命中概率：中**，理由：
1. 卖点具体、可复现、有教学价值（"四种查表只有一种能复现旧数字"是很硬的判定实验），编辑会认题材。
2. 但 Applications Note 要"软件被使用"，而 harness 是内部脚本集合，CLI/文档/CI 缺一项都可能被退回。
3. 最可能的打回理由是"case report，通用性不足"——除非补上 ≥2 个公开流程的同构反转，否则只能算"我们踩了个坑"。

### 路线 ③：完整 benchmark（10–14 页）

**常见审稿关注点**

1. 规模：为何用 4,606 子集而不是 30,000/60,471/50,000 全量。
2. 公平性：每方法调优预算、seed 数、输入是否对齐（基因集 / ortholog 表 / 标签粒度 / query 集）。
3. 统计单位：细胞级 vs donor 级（细胞级 SE 低估 1.47–3.88 倍）。
4. 外部验证：独立数据集/独立物种。
5. 结论可操作性：能否给出"什么场景选什么方法"。
6. 矩阵完整性：SAMap 只有 3 向、跨门只有 2 方法 → "四方法 × 六向"不成立。

**已有 vs 缺**

| 已有 | 缺 |
|---|---|
| 六向四方法（部分 v2）、批次三指标 | 全量重跑（30,000 / 60,471 / 50,000） |
| bootstrap + 配对 + donor-level 分析 | SATURN 3 seeds + GPU-hours 预算表 |
| 跨门 55,694 负结果（两方法） | 外部验证集 |
| 容器复现、映射签认 | SAMap 三向、BH/FDR、正对照、de novo 基线（仅 sanity） |

**最快投稿时间**：稳健 2027-10（Genome Biology，rolling，一审 2–4 个月）；Briefings 2027-09。

**命中概率：低（现状）**，理由：
1. 子集 + 无外部验证是 GB 一审的标准挂点，编辑很可能直接建议转投；这条不靠"写得好"解决，只能靠跑全量解决。
2. 近缘结论已证依赖评估器与重抽样单位（3 条翻转），写成"方法推荐"会被要求给唯一答案，目前给不出。
3. 跨门负结果 + 55,694 是加分项，但"四方法 × 六向"不成立（SAMap 3 向、n_q 不统一），表必须先补齐。

补齐 P0 三项 + 全量人↔鼠 + 一个外部验证集后 → **中**；Nature Methods 维持**低**（需新方法或全新生物学结论，本项目两者都没有）。

---

## ② 必做三件事（不做就会被一击必杀）

| 优先级 | 动作 | 为什么是它 | 工时 | 阻塞 |
|---|---|---|---|---|
| **P0-1** | **主表作废与重建**：分母规则进表 + v1→v2 重跑 + 口径二选一 + BH/FDR + 第二实现复算 | 主结论踩在 18 行 v1 上，且 n_q 跨方法不等（SAMap 307 vs scVI 1,528） | 5–7 天（SAMap 补三向 +2–3 天 CPU） | ①②③ 全部 |
| **P0-2** | **in-sample 判定**：inductive 的 CPU 臂 + 三档协议落盘 | 全部数字是 transductive，这是唯一能整篇否掉的质疑；且 GPU 卡预算，CPU 臂可立即解锁 | 4–6 天 | ③、①（"是否 in-sample"一问） |
| **P0-3** | **数字可信性**：正对照 oracle（1 天）+ SATURN best-seed（5–8 天，GPU） | 自曝过 bug 后，审稿人默认负结果也是 bug；SATURN 三重不利使任何"它更差"不可辩护 | 6–9 天 | ③、①（"公平吗""负结果真吗"两问） |

> 排序依据：**"评测是否可信" > "排名是否公平" > "规模是否够大"**。前者能让整篇归零，中者能让结论翻转，后者只影响上限。

### P0-1 主表作废与重建

**为什么最致命**：审稿人第一动作是复算，第二动作是对分母。同一方向 SAMap 307 / scVI 1,528，说明 strict_cell 只在部分行落实——被点出一次，"fair comparison"这个词就没了，而它是全文地基。另外 18 行 v1 里包含 scVI 全部 12 行，即"五向最优"的主体仍待重跑。

**做什么**

1. **口径二选一，全表贯彻，写进文件**：
   - `strict_cell`：未预测 = 错，分母 = 该向 query 总数（1,469 / 1,505 / 1,528，按方向取）。
   - `intersection`：只评共同覆盖，**必须报 n_q + 覆盖率敏感性分析**。
   - 现状是两种混用（F2）。
2. 建 `results/current-*/nq-reconciliation.tsv`：方向 / query 总数 / 每方法预测数 / 采用分母 / 排除行数 / 排除原因（`mapping_status≠active` 与 R37 `unresolved` 分列）。
3. scVI 走 v2 重跑（`scripts/scvi_mapping_v1_v2_audit.py` 已有）；SAMap 补 `斑马鱼→人`、`鼠→斑马鱼`、`斑马鱼→鼠` 三向（CPU）；若判定为"0 覆盖"，必须在表中记 `n/a` 并写明理由，不能留空。
4. **第二实现复算一条链**（复用 v97f 的 numpy 复刻模式）：同一份预测用另一套代码重算指标，逐位对齐才算过。
5. `build_current_table.py` 出 v3.0；`build_paper_evidence.py` 复核无 v1 行；同批做 BH/FDR（13 条配对，α=0.05 下期望 0.65 个假阳性，现在报 SIG 的可能掉 1–2 条）。

**验收标准**：同一方向四方法 `n_q` 严格相等或明确标 `n/a`+理由；`mapping_version` 列无 v1；两套实现指标逐位一致；BH 后的 q 值进表。

### P0-2 in-sample 判定（CPU 臂先跑）

**为什么**：所有数字都是 transductive，这是唯一能整篇否掉的质疑。团队已有完整 inductive 设计（F8），卡点是 GPU 预算——**所以本项的动作不是"设计实验"，是"把不依赖 GPU 的那一半先跑出来"**：oPCA + SAMap，3 物种留一 × 3 seed = 18 格，纯 CPU。

**做什么**

1. 按 `docs/plans/inductive-pilot-manifest-v1.md` 跑 oPCA 与 SAMap（复用 `scripts/_opca_inductive_variant.py`、`scripts/pairwise_inductive.py`）。
2. 出 Δ 表：同方向 `transductive − inductive`（macro-F1 与 accuracy 分开列）。
3. 写 `docs/evaluation-protocol.md`，冻结三档：
   - **T** transductive：query 细胞参与 embedding 训练与 ortholog 映射构建（现状全部属此档）。
   - **I** inductive-heldout：query 物种训练阶段完全不可见。
   - **E** external：独立数据集/独立物种，映射表也不含 query。
4. 若 Δ > 0.10，主表改报 I 档、T 档进附录——这会让论文更硬。

**验收标准**：Δ 表 + `evaluation-protocol.md` 落盘；每张主表标注档位。

### P0-3 数字可信性：正对照 + SATURN 上界

**为什么拆成两半**：两件事回答的是同一个问题——"你的数字能不能信"。正对照证明**评测没坏**，best-seed 证明**方法没被低估**。缺任一，负结果与排名都可被一句意见推翻。

**P0-3A 正对照 oracle（1 天，CPU，先做）**

1. 近缘正对照：同一套 strict_cell + 同一评估器，在 人↔鼠 上跑（已有，macro-F1 0.64/0.67 ≫ 基线 0.48/0.31）→ 证明评测链能给出正结果。
2. 跨门正对照：在 七鳃鳗↔小鼠 上用**目标物种真值训练的监督分类器**（oracle 上界）跑同一指标。
   - oracle 高（≥0.15 macro-F1）而方法只有 0.023–0.027 → 失败来自方法/映射，不是评测坏了 → 负结果成立。
   - oracle 也低 → 任务本身不可迁，必须把结论改写成"标签空间不可对齐"，不能写"方法失败"。
3. 对跨门标签重做一次四种查表判定（和近缘同款），证明这次的负结果不是同一个 bug。

**P0-3B SATURN best-seed（5–8 天，GPU，排队）**

1. 同输入：同基因集、同 ortholog 表、同标签粒度、同 query 集。
2. 3 seeds × 六向（先 2 向试水；`scripts/stab_campaign.py` 已有稳定性框架）。
3. 报 **mean±sd** 与 **best-seed** 两个数——best-seed 是上界，报出来就把"你没调好"挡死。
4. 记录 GPU-hours；正文只写"在 X GPU-hour 预算内"。
5. 预算允许加 3 组超参 × 2 向小网格；若 best-of-grid 仍低于 scVI，这条质疑即死。

**验收标准**：`positive-control.tsv` + `saturn-seeds.tsv`；正文出现"matched budget, not matched tuning"这句限定。

### 第二梯队（并行、不阻塞投稿）

| 项 | 内容 | 工时 | 服务 |
|---|---|---|---|
| 全量人↔鼠 scaling | 30,000 / 60,471 双向，oPCA + scVI | 3–4 天 | ③、② |
| de novo 聚类基线 | Leiden，**仅 sanity**：它不是标签迁移，指标不可比，不进主表 | 1 天 | ③（对照组完整性） |
| 生物学同行抽查 | L1–L6 canonical 行抽 20%（`report-11` 建议），2 天 | 2 天 | ①②③（投稿前必做） |
| 外部验证集 | 独立人-鼠配对数据或其它组织 | 2–4 周（需数据） | ③ |
| SAMap 三向 | 已并入 P0-1 | — | ①②③ |

---

## ③ 三个最可能被质疑的点与可执行应对

### 质疑 ①：只用子集，规模小

**审稿人原话**：*"4,606 cells out of 30,000/60,471/50,000 — why subsample? Rankings may not survive at scale."*

**杀伤力**：中。workshop 不致命；GB 一审致命。

**补什么**

1. 首选：人↔鼠全量（30,000 / 60,471）双向跑 oPCA + scVI，报 macro-F1 与 n_q。排序不变即可写 "ranking preserved at full scale"。
2. 退路（更便宜且能出图）：25% / 50% / 100% 三档分层抽样，画 scaling 曲线，只需人↔鼠一个 pair。
3. 先把**抽样规则**写成脚本 + 固定 seed，否则"子集"会被读成"挑了对自己有利的细胞"。

**怎么写**：limitation 第一句给数字，第二句给语义（"interpret rankings, not absolute performance"），第三句给证据（曲线或全量结果）。

**不做的代价**：GB 必挂；workshop 可活。

### 质疑 ②：SATURN 未完整调优（公平吗）

**审稿人原话**：*"SATURN's low score may reflect your hyperparameters, not the method."*

**杀伤力**：高。且**双向风险**：调优后若反超，主结论也要改。

**补什么**

1. 预算透明：GPU-hours、搜索空间、seed 数，写进方法或补充材料。
2. **best-seed 上界**：3 seeds 里最好的那个作为天花板。只要 best-seed 仍低于 scVI，"没调好"就站不住。
3. 同输入对照：证明差异不是"喂了不同基因集/ortholog 表"。
4. 小网格（3 组 × 2 向，约 6 GPU-runs）能跑就彻底关掉这条。

**怎么写**：不写 "SATURN underperforms"；写 *"within a fixed budget of X GPU-hours and matched inputs, SATURN reached macro-F1 = A (best seed = B), below scVI's C"*。把结论限定在预算内。

**不做的代价**：一句"SATURN 最差"就能被推翻；且无法回答"那你调了吗"。

### 质疑 ③：transductive / in-sample 评估本身是否合理

**审稿人原话**：*"Query cells were used to build the ortholog map and the embedding — this is in-sample evaluation."*

**杀伤力**：最高（可整篇否掉），但最容易写清——团队已有 v74 的正式表述（F7）。

**补什么**

1. 三档定义（T / I / E）落成 `evaluation-protocol.md`，每张表标注档位。
2. 跑 CPU 臂 inductive（P0-2），给 Δ 表；Δ 大就把主表换成 I 档。
3. **反向用法（重要）**：跨门负结果在 T 档（最有利条件）下仍低于多数类基线 → 这不是"结果不干净"，是**上界论证**：给了最宽松的设置都失败，说明失败不是信息不足造成的。这句应写进 §4 正面段落，不是 limitation 里道歉。

**怎么写**：limitation 明确"本文全部为 T 档，是 inductive 标注的上界"；Discussion 用同一事实支撑负结果稳健性。两处不冲突，是同一件事的两面。

**不做的代价**：一句 in-sample 就能要求重做全部实验；且我们无法回答"掉多少"。

### 顺带必须回答的第四问：负结果本身是不是又一个 bug

这条不单列成"第 4 个质疑"是因为它由 ① 和 ③ 派生，但它是最可能被顺带打死的：

- **信号**：跨门 accuracy 4.6–5.8% 低于随机 7.69%——低于随机的表现，最典型的成因是**标签索引/词表错位**，而我们刚犯过一次（F11）。审稿人不会信"我们这次检查过了"。
- **唯一有效应对**：P0-3A 的 oracle 正对照 + 跨门四种查表判定。两者都进补充材料。
- **表述纪律**：负结果只能写"oPCA/scVI 两法在此设置下低于多数类基线"，不能写"跨物种方法整体失败"；只能写"在该标签空间下不可迁"，不能写"方法无能"。

---

## ④ §4 Discussion 可直接用的 limitation 英文草稿（133 词）

```
Three limitations qualify these results. First, the human-mouse and
zebrafish comparisons use 4,606-cell subsamples of atlases containing
30,000, 60,471 and 50,000 cells, so absolute scores are not comparable to
studies run on complete atlases; the lamprey-mouse comparison (55,694
cells) is affected to a lesser degree. We therefore interpret rankings,
not absolute performance. Second, SATURN was trained within a fixed
compute budget and a single seed, whereas oPCA and scVI are deterministic
or multi-seed; its scores are a lower bound, and every comparison is
conditional on matched budget rather than matched tuning. Third, all
evaluations are transductive: query cells contribute to embedding training
and to ortholog-map construction, so the reported accuracy is an upper
bound for inductive annotation. Held-out controls appear in Supplementary
Note S4; we claim no generalization to unseen samples or species.
```

- 词数 **133**（程序核对）；`Supplementary Note S4` 为占位，落稿替换为实际编号。
- 对应关系：第一句 ← 全量/scaling；第二句 ← P0-3B；第三句 ← P0-2。
- 若 P0-2 的 Δ 很小（< 0.03），第三句可加强为 *"…upper bound; the measured gap to held-out annotation was ≤0.03 macro-F1"*，从 limitation 变成贡献。
- 若跨门结论保留，建议再加一句（不计入上面 133 词）：*"The cross-phylum result is reported for two methods only and should not be read as a statement about the method class."*

---

## ⑤ 建议时间表

| 段 | 稳健档（推荐） | 激进档 | 动作 | 产出 |
|---|---|---|---|---|
| G1 | 11/11–11/30 | 11/11–11/16 | P0-1 主体：分母规则进表 + scVI v2 重跑 | `nq-reconciliation.tsv` |
| G2 | 11/24–12/12 | 11/17–11/23 | P0-2 CPU 臂 inductive + 协议 | Δ 表 + `evaluation-protocol.md` |
| G3 | 12/01–12/20 | 11/24–12/04 | P0-3A 正对照（1 天）+ P0-3B SATURN seeds（排队） | `positive-control.tsv`、`saturn-seeds.tsv` |
| G4 | 12/20–01/10 | 12/05–12/10 | **validity gate 关闭**：v3.0 冻结 + 第二实现复算 + BH | 主表 v3.0 |
| G5 | 01/10–02/10 | 12/10–01/05 | workshop 稿 4–6 页（3 图） | 正文 + 图 |
| G6 | 02/10–02/28 | 01/06–01/20 | 投 workshop（NeurIPS 2027 / ICLR 2027，按截稿择近） | 投稿号 |
| G7 | 02/01–03/15 | 02/10–03/10 | methods note 成稿并投 | 投稿号 |
| G8 | 03–09 | 03–09 | 全量人↔鼠 + 外部验证 + SAMap 三向 | GB 材料 |
| G9 | 10–11 | 07–08 | 投 Genome Biology | 投稿号 |

**关键路径**：`P0-1 → G4 → G5 → G6`。P0-3B 与写作并行（GPU 排队不占人力）；全量只服务③，放在 workshop 投出后。

**六个熔断点（到点不满足就换方案，不硬撑）**

1. **11/30**：若 `n_q` 无法统一 → 降级 intersection 口径并全表标注，**放弃"四方法六向"表述**，改写"三方法六向 + SAMap 三向"。
2. **12/20**：若 P0-3A 的跨门 oracle 也低 → 结论改写为"标签空间不可对齐"，负结果从"方法失败"降级为"任务边界"，路线①的卖点改为口径方法学。
3. **12/20**：若 SATURN best-seed ≥ scVI → 主 claim 立即改为"口径决定排名"，不报冠军。这不是坏消息，它让①的 framing 更稳。
4. **01/10**：若 v3.0 与 v2 排名有翻转 → 标题与摘要按"排名依赖口径"重写，材料 80% 复用，不影响窗口。
5. **02/28**：若 workshop 未中 → 直接转 methods note（材料 80% 复用），不等下一轮。
6. **09/30**：若外部验证集仍无数据 → GB 改投 Briefings，并在 limitation 写明"无外部验证"。

---

## 附：缺项清单（按工时升序，可直接派工）

| # | 缺项 | 现状 | 要做 | 工时 | 阻塞 |
|---|---|---|---|---|---|
| 1 | BH/FDR | 无 | 13 条配对 → q 值 | 0.5 天 | ③ |
| 2 | 正对照 oracle | 无 | 跨门监督上界 + 近缘正对照 + 跨门四种查表判定 | 1 天 | ①③ |
| 3 | de novo 聚类基线 | 无 | Leiden，仅 sanity，不进主表 | 1 天 | ③ |
| 4 | 分母对账表 | 规则存在但未进表 | `nq-reconciliation.tsv` + 口径二选一 | 1 天 | ①②③ |
| 5 | scVI v2 重跑 | 12 行 v1 | 六向重跑，统一分母 | 2–3 天 | ①②③ |
| 6 | SAMap 三向 | 3 向无数据 | 补齐或明确记 `n/a`+理由 | 2–3 天 | ①②③ |
| 7 | 生物学同行抽查 | 仅负责人授权 + AI 复核 | L1–L6 抽 20% | 2 天 | ①②③ |
| 8 | 全量人↔鼠 | 子集 3,063 | 30,000/60,471 双向 2 方法 | 3–4 天 | ③ |
| 9 | Δ(transductive−inductive) 表 | 设计有、未运行（GPU 卡） | 先跑 CPU 臂（18 格） | 4–6 天 | ①③ |
| 10 | SATURN seeds | 单 seed | 3 seeds × 6 向 + best-seed | 5–8 天 | ①③ |
| 11 | 通用性反转实验 | 只有本项目判定实验 | ≥2 个公开流程同构反转 | 2 周 | ② |
| 12 | 软件化 | 130+ 脚本无统一入口 | CLI + README + CI + license + DOI | 2–3 周 | ② |
| 13 | 外部验证集 | 无 | 独立数据/物种 | 2–4 周（需数据） | ③ |

**合计**：到 workshop 可投需 #1–#10（净工时约 4–5 周，含 GPU 排队 5–6 周）；到 methods note 加 #11–#12；到 GB 加 #13。

---

## 复核记录（Claude 咨询，2026-11-11 21:17，`_claude/20261111-2117-publish-routes.md`）

**采纳（5 条）**

1. 跨门只有 oPCA/scVI 两法 → 不能写"这一族方法都不行"，已在 F9、①③、④ 加限定。
2. 缺**正对照 oracle**，且这是比"SATURN 未调优"更靠前的生死项 → 已升级为 P0-3A，并改写了"必做三件事"的排序依据。
3. 时间表偏乐观（gate 需 2–3 个月）→ 改为双档，"稳健"为推荐，GB 推到 2027-10。
4. "重跑"应升级为"**主表作废** + 独立复算" → P0-1 加入第二实现复算与"作废"语义。
5. `1,505` 的 30 个细胞不是丢失而是 `mapping_status≠active`（鼠 30 / 鱼 44 / 人 0）→ 已改前提 F2 并给出三处分母的对应关系。

**不采纳（2 条，各附理由）**

1. Claude 称"交接文档记录的抬升机制是不可映射预测退出分母（0.04–0.19），与词表反转（0.0625–0.3549）不是同一件事"——**该机制已在 `20261111-obsolete-numbers.md` 作废 1 明确废止**，它引的是作废段落。本报告按"机制唯一 = 物种词表反转"写，并在②路线里把"不能混写"列为审稿风险。
2. Claude 称"scVI 完整格 2/3"——与 `current-table.tsv` 实际不符（scVI 六向 12 行俱全，只是全部为 v1）。不采用。

---

## 本轮未做

- 未跑任何新实验，全部判断基于磁盘上的现有产物；工时是净执行估计，不含排队与返工。
- workshop 截稿日期为经验区间（ICLR/NeurIPS workshop 通常在会前 2–3 个月），**以官网为准**；G6 的具体日期需在 12 月复查一次。
- 外部验证集的可行性未评估（取决于能否拿到第二套人-鼠配对数据）。