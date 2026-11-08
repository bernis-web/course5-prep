# 长任务收尾交接（2026-10-09）

> 范围：批次四成果核对 → GenPilot 两轮会商 → 逐方向解释底表 → 候选稿/Word 定向修订 → 三档方案与审批单。
> 纪律声明：本轮**未提交任何 DCS/WDL/GPU 任务**；未充值；未推送敏感数据；未宣称导师签认；未覆盖任何并发改动；未 commit/push。

## 一、四类清单

### 确认（file-level / 平台实查）
1. ortholog-PCA 六方向 × 三层（candidate-final；predictions 18 + confusion 18 本地逐细胞复算；SHA b2b3ac6b…）
2. SAMap v98 WDL 18 格（candidate-final 探索性；per_cell 复算；SHA 3c719399…；任务 W202610050003104）
3. v99 三层（provenance confirmed file-level；恢复载荷逐细胞复算；SHA d1081cfd…）
4. 排除规则四方对账（TSV/v99/oPCA/矩阵：mouse 30 / zf 44 / human 0；SAMap 差 3 待核验）
5. 平台事实（GenPilot 实查）：三份 h5ad file id 与形状（1528×19302 / 1535×18703 / 1543×24007，含 cell_or_nuclei 字段）；SATURN--22 镜像 = public-library/zhongliyuan_57362367597d49499e5bc388096a17f1_public:latest；downloadFile 公网端点 200；WDL 累计花费 **1.13 元**
6. 逐方向三方法底表 18 格正确数（confusion 对角和 = acc×n_q 双重复核）

### 候选（candidate / 探索性 / transductive）
1. 全部汇报数字（transductive/in-sample；单 seed 0）
2. ESM2 消融 67.4%→20.4%（v72-era 协议内配对；v97g 协议下未重跑）
3. 鱼方向 seed 双峰（11.3/48.8/8.3）；h→m 67.1±3.8
4. 物种内 ceiling 85.5/93.5/74.2（SATURN 侧、不同方法/协议，仅作辅助参照）

### 待签认 / 待核实
1. **mapping v1 人工签认**（导师；5 个议题、6 条源映射；needs-reviewer）
2. **SATURN 运行时源码版本 + 训练命令行**（v71/v99 vs checked-in 未闭合；训练命令无留档）→ 材料已标"待核实"
3. **SAMap 线上运行脚本内容**（samap_script.py c0f05b89 ≠ checked-in 71dd08a3，待回捞）
4. 平台 **GPU 单价**（无公开计价接口）
5. **r1d 失败原因**（日志已清理；任务已从"待分析"转"失败"，说明 s 类队列已恢复调度）
6. v97g 逐细胞文件（不存在 → 日志级，不可升级）

### 未运行（designed-not-run）
1. 三档实验方案 A/B/C **全部未运行**（A 档可立即本地执行、0 元）
2. inductive 81 格设计（manifest v1；未提交）
3. 任何新的 DCS/WDL/GPU 任务（无）

## 二、GenPilot 与 Claude 的分歧（及本地裁定）

| 议题 | GenPilot 主张 | Claude 反方 | 本地裁定 |
|---|---|---|---|
| SATURN 标签可见性 | "不可考"（--use_ref_labels 默认 False、命令未留档） | **源码层面可考**：cross_species miner 用 `labels` 通道；ref_labels 仅输出/评估真值（项目 2026-09-24 审计已明确） | **采纳 Claude**：机制 = labels 通道；仅"运行时版本 + 训练命令"标待核实。全链已修正（6 文件 + Word + 2 册 PPT） |
| oPCA label-free 证据 | 引 ortholog_pca_v98_final.py L118 | 权威脚本是 scripts/ortholog_pca_local_v1.py（manifest 6582d873…）；v98_final.py 自身不自洽 | 采纳 Claude；会商记录已加更正注 |
| SAMap label-aware 证据 | 引 checked-in 脚本 L28/335 | 线上运行脚本 ≠ checked-in → 需"待回捞"标注 | 采纳 Claude（已标注） |
| SAMap 投影接口 | ❌ 无原生冻结图投影，只能近似 | 同意；且须显式"近似 inductive"+硬闸门+改名 SAMap-approx | 一致（方案 v2 已落） |
| 成本估算 | A 档含 SAMap 0.55 元、SATURN GPU 5-6h；B 档 oPCA 1.4 / SAMap 1.6 元 | 算术矛盾（27×16min≈4.75 元）；A 档应 0 元；0.011 元/分钟仅适用 1c4Gi 档 | 采纳 Claude（方案 v2 已改正） |
| 泄漏防护清单 | 3 条（条码前缀/标签/不回流） | 需扩至 8 项（基因集、HVG、统计量范围、batch/供体、供体级隔离、标签物理剥离、seed 预注册、inductive 负控） | 采纳 Claude（方案 v2 已落） |
| 档名口径 | A/B（B=81 格） | 与本地 A/B/C 撞名 | 已统一：会商 B = 本方案 C2（对照表见方案 v2） |

**两处 GenPilot 待核实项处理正确**（单价、r1d 原因），Claude 确认 ✓。

## 三、候选材料（PPT / Word / 底表）

| 材料 | 路径 | 状态 |
|---|---|---|
| 汇报 2 校模板版 PPT | results/report-02-metric-lineage-20261008/课题5第二阶段汇报_数字来源链_校模板版.pptx | 已过批次一 Claude 审阅 |
| 汇报 3–10（8 册 55 页） | results/stage-reports-20261009/ | 批次五重建 03/05（SATURN 机制更正）；SHA 见 SHA256SUMS.txt |
| **最新 SHA（关键变化）** | 03 = `c06f791b…`（经两轮重建：d04a02e8→c858e731→c06f791b）；05 = `4990a046…`（9b9dbf96→8c8ecedc→4990a046）；其余 6 册不变 | 复审以最新清单为准 |
| Word 报告（候选） | deliverables/course5-final-report.docx（备份 .bak-20261009.docx） | 本轮定向修订 6 处（鱼方向分组/消融 67.4/标签空间拆分/多数类拆两列/§5.10 needs-reviewer/SATURN 机制） |
| 逐方向解释底表 | docs/evidence/per-direction-three-method-20261009.md | 新建；数字程序化生成 |
| 会商记录 | docs/evidence/genpilot-consultation-20261009.md | 两轮 + Claude 更正注 |
| Claude 反方审阅 | docs/reports/claude-protocol-review-20261009.md | revise；阻塞项已修 |

## 四、三档实验审批单（**待批准；均未提交**）

| 单号 | 内容 | 费用上限 | 前置 |
|---|---|---|---|
| B-1 | SAMap WDL 单细胞子集重跑（1c4g） | ≤1 元 | 档 A 完成 |
| C1-1 | 投影接口与隔离证明（容器只读验证） | ≤5 元 | mapping 签认（硬前置）；**SATURN 已判源码级阻塞**，C1 实际只剩 oPCA（真投影）+ SAMap-approx（带闸门） |
| C2-1 | inductive 81 格（SATURN GPU ≤9 次 + CPU SAMap ≈4.75 元） | 总额申请时列明；单次 GPU ≤¥50 保险丝 | C1 硬闸门全过 + 预算批准 |

（完整输入/协议标签/产物/smoke/停止条件见 docs/plans/three-tier-followup-20261009.md v2）

## 五、需要回答的具体问题

**给用户（3 项）**
1. 三档审批单是否批准？其中 C1-1（≤5 元容器验证）是"先证明再花钱"的关键前置。
2. SATURN 运行时版本/训练命令的"待核实"标注是否按当前方式保留在对外材料中（已如此处理）？
3. 导师邮件是否附本轮更正说明（SATURN 机制更正 + Word 修订 6 处）？

**给老师（4 项）**
1. 映射表 v1 签认（5 个议题、6 条源映射；意见书已备）。
2. "单细胞优先"确认；单核对照是否需要（当前方案把它排在主结论之后）。
3. inductive 实验是否批准（含 GPU 预算与总额上限）。
4. 空间数据不进主评估的口径确认。

## 六、本轮边界声明

- 未提交任何 DCS/WDL/GPU 任务；未充值；未推送敏感数据；未宣称导师签认。
- GenPilot 建议不替代本地 metrics/日志/源码/逐细胞预测/导师签认；两处"待核实"如实标注。
- 未覆盖任何并发改动（工作树 212 项既有改动未触碰）；未 commit/push。
- 汇报候选稿状态为"初稿齐备 + 逐册评审/外部确认待闭环"，**未写成"已向老师汇报 8–10 次"**。

---

## 附：验收修正轮（2026-10-09 晚，用户验收反馈 5 项）

用户验收意见与本轮处理（详见 docs/longrun-20261009-worklog.md 验收修正轮）：
① 第 5 册 1,000 维/50 维错误 → 已改（依据 dcs_provenance_v99.py:22）；② Word 生成脚本同步（双多数类列 + 0.4817 + 全部手工修订回写脚本 + zoom 修复入脚本）→ 重建并逐表/渲染检查通过；
③ 第 3 册因果措辞收紧 → 已改；④ C1 补 SATURN 源码级可行性 → **判定阻塞**；⑤ 81 格运行次数与费用重算 → 每方法 9 次、SAMap ≈1.6 元（待澄清估算）。
**新 SHA：03 c06f791b…、05 4990a046…**；Claude 按最终文件复审记录见 docs/reports/claude-final-r2-review-20261009.md（归档后）。
**B/C1/C2 均未启动**（用户口径：暂不批准；A 档零费用复算与材料修订可继续）。

## 附二：验收修正第二批（2026-10-09 深夜，2 项口径问题）

1. **方案 C2**：预期产物改为"**当前可行子集最多 54 格**（oPCA 27 + SAMap-approx 27）；完整 81 格须待 SATURN 另立方案并过 C1 闸门；子集可先行、完整 C2 不得启动"。
2. **Word 主表**：删除"粗体＝该方向最高值"图例（实际未加粗、跨标签空间不宜暗示排名），改为"不构成排名（表内未加粗、未做方法间显著性检验）"；"显著高于/领先"→"数值高于/领先"。脚本同步重建；**Word SHA-256 = `593d31e6…788f`**（42,256 bytes）。

**当前状态（可保持"待老师反馈"）**：材料初稿齐备、逐册评审与两轮验收修正已闭环；A 档（零费用本地复算）可继续；B/C1/C2 未批准未启动；映射签认、SATURN 新方案、付费运行仍是各自独立关口。

---

# 规范状态声明（2026-10-09，用户验收后确认；以此为准）

> 本块为项目**当前状态的标准表述**，后续对外沟通、交接与汇报均引用此处，不再另行改写。

## 可以做的事
- **第一阶段汇报材料：可以交老师**（8 册阶段 PPT + 汇报 2 校模板版 + 最终 Word 报告）。
- **A 档（零费用本地复算与材料修订）：可继续**。

## 已收尾
- Word/PPT 口径修订：已收尾。两批验收修正全部闭环：
  - 第 5 册 1,000 维 macrogene（依据 dcs_provenance_v99.py:22）；
  - 第 3 册标签机制因果措辞（贡献未单独量化）；
  - C2 可行子集 54 格 vs 完整 81 格区分；
  - Word 主表排名暗示删除（未加粗、未做方法间显著性检验）+"显著"→"数值"；
  - Word 结构（zoom=percent 100）、双多数类列、逐格数值、第 3 页渲染均经用户独立核验；
  - 8 册 PPT SHA 清单 8/8 一致（本轮未动 PPT）；Word SHA-256 = `593d31e6…788f`（42,256 bytes）。

## 未启动 / 未批准（各自独立关口）
- **DCS 付费任务：未启动**（无提交、无充值）。
- **B / C1 / C2：未批准、未启动**。
- **mapping v1：仍等待人工签认**（needs-reviewer）。
- **SATURN inductive：仍需另立重训或模型改造方案**（C1 源码级判定为阻塞）。
- **C2 如获批准**：先考虑 **oPCA + SAMap-approx 的最多 54 格子集**；**不把它称为完整三方法 81 格 benchmark**。

## 总体定性
**项目总体不是"所有实验完成"，而是"第一阶段材料已经可以进入等老师反馈阶段"。**

## 验证归属说明（如实标注）
- "脚本重建可复现"：由**执行者在本会话内实际运行** `scripts/build_final_report.py` 重建验证（两批修正各重建一次，逐项复验通过）；
  Claude 复审核验了脚本内容与最终成品的一致性；**用户本轮的独立验证未重新运行脚本**（用户已如实说明）。
- 其余核验归属见 docs/longrun-20261009-worklog.md 各轮记录。
