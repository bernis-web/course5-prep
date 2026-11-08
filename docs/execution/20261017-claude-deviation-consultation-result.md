# Claude 咨询结果：课题5 汇报偏题诊断（2026-10-17）

> 咨询对象：Claude Code（deepseek-v4.1-flash）
> 输入材料：`docs/execution/20261015-claude-consultation-deviation.md`
> 原始输出：`/tmp/claude-dev.txt`（18,385 字节）
> 结论性质：独立判断，**纠正了执行者两处错误**（见 §四）

---

## 一、核心判断（与执行者的分歧）

Claude 的总判断：

> **老师说的"偏"，最可能不是六条里的任何一条，而是交付物的类型错了。**
> 课程要的是"场景 → 方法 → 指标 → 选型建议"的基准报告；你们交的是"数字如何可信"的审计报告。
> 六条偏差是症状，根因是：**项目把"防止过度结论"的治理规则，做成了"不产生结论"的默认状态。**

---

## 二、真偏差排序（Claude 判定）

### 不算偏的（是资产，不是负担）

- 证据分级、SHA、manifest、负控、双口径
- 拒绝把 transductive 写成 inductive
- 拒绝按总分排冠军
- **3 物种 pilot**（老师 2026-09-10 明确批准首轮 2–3 物种）
- bug 修复（采纳修正版即可）

### 真偏的（按严重度）

| 排序 | 偏差 | 严重度 | 说明 |
|---|---|---|---|
| 1 | **交付物类型错了** | 最重 | 10/10 汇报没有一页回答"近缘/跨门/无 GPU 该选谁" |
| 2 | **课程点名的 scVI 臂缺失**（执行者漏列） | 高 | 课程标题是"SATURN vs SAMap vs **scVI 系**"；最终矩阵换成了自建 oPCA |
| 3 | **指标 + 标签空间不可比** | 高 | accuracy→macro-F1 是真问题；三方法不在同一标签空间 |
| 4 | **五维评测缺三维** | 高 | kBET/iLISI/silhouette、文档易用性、Agent 友好度全缺 |
| 5 | **跨门场景缺失** | 高 | 七鳃鳗数据未用；且被自设 `activation_gate` 锁死 |
| 6 | **transductive 但计划书写的是 LOO**（执行者漏列） | 中高 | 已披露，但计划与实做不符 |
| 7 | 物种规模 | 中 | 3 物种是老师批准的；偏在"把 pilot 当终局" |
| 8 | **容器化**（执行者漏列） | 轻 | 有方案无交付物 |
| 9 | **CM/FB 任务定义**（待验证） | 可能更根本 | 若 CM/FB 是二类任务，做 8–9 类多分类就是另一个任务 |

### 关键洞见 1：跨门被自己的 gate 锁死

`benchmark-plan.json:56-64` 的 `lbspa_cross_phylum.activation_gate` = `scRNA_benchmark_conclusion_recorded`。
但项目又坚持"不能下结论" → **因为拒绝下结论，跨门场景永远不启动**。
这个 gate 是自设的，不是课程要求。

### 关键洞见 2："不可比"是待修的 bug，不是结论

三方法在不同标签空间（oPCA/SATURN v97g 用映射粗类空间；SATURN v99/SAMap 用原始标签空间），
主表把不同分母、不同标签空间的数字并列，然后说"不可直接排名"。

Claude 的判定：**基准测试的工作就是把不可比变成可比。** 手里有 `config/heart-celltype-map-v1.tsv`，
把它同时应用到 SAMap/v99 的预测上，重算同一 coarse 空间的 macro-F1 —— **零算力**。

---

## 三、纠偏序列（Claude 给出，按优先级）

**总原则：先做零算力的"重新切分"，再做少量付费的"补格"。不要先跑实验。**

| 优先级 | 动作 | 费用 | 重跑 | 时间 |
|---|---|---|---|---|
| **P-1** | bug 决策：采纳 v3_fixkey，旧 12 格标 `superseded`，归档不删 | 0 | 否 | 0.5 天 |
| **P0** | 找回课程 HTML + HEART PDF，核 SHA；做"课程要求→现有证据→缺口→动作"合规矩阵 | 0 | 否 | 1 天 |
| **P1** | **统一 coarse 标签空间，重算 macro-F1**（三方法全部用现有 confusion/per_cell） | 0 | **否** | 0.5–1 天 |
| **P2** | **写选型指南 v1**（行=近缘/远缘/跨门/无GPU，列=方法，格=推荐/条件推荐/证据不足） | 0 | 否 | 2–3 天 |
| P3 | 时间/内存表 + 文档易用性评分 + Agent CLI/API 评分 | 0 | 内存可能需小跑 | 1–2 天 |
| P4 | **scVI 跨物种臂**（同 ortholog 矩阵，species=batch） | 0–0.3 元 | 是，一次 | 1–2 天 |
| P5 | kBET/iLISI/silhouette（只对共享 latent 的方法） | 0–0.3 元 | oPCA 本地；SATURN 先查 payload | 1–2 天 |
| P6 | **跨门最小跑**（lamprey brain vs mouse brain） | 0.2–0.5 元 | 是，一次（最高风险） | 2–4 天 |
| P7 | 容器化交付物（pin 版本 + 可复现 smoke） | 0–0.2 元 | 可能一次 | 1 天 |
| P8 | 重写 Word/PPT 叙事（10 册审计压成 3–5 页附录） | 0 | 否 | 2–3 天 |

**停止做的一件事**：在选型指南草稿出来之前，不要再写"证据如何可信"的新汇报。

---

## 四、Claude 纠正执行者的两处错误

### 纠正 1：macro-F1 的因果方向说反了

执行者原话："accuracy 被多数类主导，这可能正是斑马鱼方向低于 majority baseline 的来源。"

Claude 纠正：

- 换成 macro-F1，**方法分数会下降**（少数类更难）
- 但 **majority baseline 的 macro-F1 下降得更狠**（多数类分类器在所有少数类上 F1=0）
- 以 h→m 多数类占比 0.4618、8 个 coarse 类估算：多数类 macro-F1 ≈ **0.079**，而其 accuracy 是 0.4618
- oPCA 的 h→z accuracy 是 0.1961；其 macro-F1 只要超过约 0.071 就**高于**多数类基线

→ **现在"低于多数类基线"的斑马鱼方向，换成 macro-F1 后很可能翻转。** 必须逐格重算。

### 纠正 2：HEART 论文的身份

执行者写"HEART 论文（Tabula Sapiens 系）"——**错误**。

Claude：HEART 是 DOI `10.1126/science.adw0855`，2026 Science，
题为 *"Spatially resolved single-cell atlas reveals the macroevolutionary trajectory of animal hearts"*。
另外 HEART 的 scRNA 部分是 **14 物种 / 399,483 细胞**；16 物种 / 479,483 是 SATURN 整合子集。
执行者写的"原数据是 16 物种 479,483"不准确。

---

## 五、Q4 复用/作废清单（Claude 判定）

### 可复用

| 资产 | 用法 |
|---|---|
| `results/pilot-v1/*` 全部 metrics/predictions/confusion/per_cell | P1 的原料 |
| `config/heart-celltype-map-v1.tsv` | 统一标签空间的键，**要应用到所有方法** |
| `scripts/ortholog_pca_dcs_v3_fixkey.py` | 修正后的基线 |
| DCS 的 scVI/SATURN/SAMap 管线 | P4/P5/P6 复用 |
| 证据矩阵、状态矩阵、manifest、SHA 体系 | 压成"可复现性附录"（加分项） |
| scVI 物种内 98.38/98.12/92.51 | 作为物种内 ceiling，**不是**跨物种 scVI 臂 |

### 应作废/降级的"说法"（不是数据）

- "10 册汇报就是课程交付物" → 作废，它们是审计记录
- "三方法矩阵 = 课程的三方法" → 作废，scVI 臂缺失
- "跨方法不可直接排名，所以不能比较" → 降级为"统一标签空间后比较；剩余不可比列 caveat"
- "不能排冠军 = 不能给推荐" → 作废，选型指南本就是条件化的
- "3 物种 = 完整 benchmark" → 改成"3 物种 pilot + 场景切片"
- accuracy-only 的 headline → 降级为附录，主表用 macro-F1
- bug 影响的 12 个鱼方向数字 → 标 `superseded`，归档不删
- `lbspa_cross_phylum.activation_gate` → 移除/覆盖

**没有任何计算结果需要"作废"。** 作废的是"当前材料已满足课程要求"这个判断。

---

## 六、Q5 结论：补齐，不推倒重来

Claude 明确建议：**在现有基础上补齐，不推倒重来。**

五条理由：

1. 贵的不是算力，是叙事。真正沉没成本是 10 册汇报和证据链
2. 缺的大部分零算力可补（统一标签空间 + macro-F1、选型指南、文档/Agent 评分、时间表）
3. 推倒重来会违反冻结约束，也浪费已验证的 12/12 复算
4. 现有证据链是最终报告的**加分项**，问题是它占了 100% 篇幅，应降到 15%
5. "补齐"必须窄定义：**先重切现有证据，再补最少缺失格**。不是"再写 5 册证据汇报"

**改变建议的条件**：若 P0 核原文发现 CM/FB 确实是二类任务，或映射表覆盖不足，
则需重做的是**评分层和标签层**，不是数据层和算力层——仍是"重切"。

---

## 七、下一步（执行者将按此执行）

按 Claude 建议，立即做 **P1（零算力，可能改变结论）**：

1. 把三方法统一到 coarse 标签空间
2. 重算 macro-F1（含 per-class F1、majority macro-F1）
3. 用现有 confusion/per_cell，不跑新模型
4. 检查"低于多数类基线"的结论是否翻转

P0（找回课程原文）需用户提供文件或确认路径——本地 `course-web(1).html` 与 HEART PDF 缺失。
