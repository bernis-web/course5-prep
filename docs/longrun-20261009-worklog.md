# 长时任务工作日志（2026-10-09 起）

> 目的：按阶段记录"实际完成事项、证据路径及 SHA、测试/审阅结果、DCS 任务与费用、未关问题"。
> 纪律：只读核对优先；不覆盖并发改动；不新增付费任务（需单独审批）；不虚构会商结果。

## 阶段 1：批次四成果只读核对（完成）

**实际完成事项**
- 工作树基线：HEAD `8b597d7`；`git status --short` 共 212 项（含既有/并发改动：docs/dcs-readonly-audit.md、docs/source-notes.md、docs/team-task-division.md、scripts/ortholog_pca_dcs_v2.py、wheelhouse/* 等，均未触碰）。
- 核第 3 册 p7 成品 PPT：逐方向列数在位（oPCA h→z 0.1961 ／ m→z 0.2755 ／ z→h 0.1813 ／ z→m 0.5761；SATURN v97g 0.1835 ／ 0.3009 ／ 0.2474 ／ 0.4651；SAMap 0.0341 ／ 0 ／ 0 ／ 0），"仅 oPCA 的 z→m 超过多数类 0.4817"在位；旧含混串（0.18–0.28、query=鱼）不存在。
- 生成脚本 build_report03.js 与成品同源。
- 第 10 册版本保留措辞在位（"交付物清单（版本化；可核实旧件保留）"、"中间修订版曾原地重建、未单独归档"）。
- 三份 Claude 复核记录齐备（03-to-10 主记录 / r2 / r4，共 29.5KB）。
- SHA256SUMS.txt 复算 8/8 一致（03=d04a02e8…、10=105ae7ec…）。

**证据路径与 SHA**
- results/stage-reports-20261009/{课题5第03…pptx, 课题5第10…pptx, SHA256SUMS.txt, build_report03.js}
- results/pilot-v1/ortholog-pca-v98/metrics.json（六方向 coarse 逐格）；samap-v98/wdl-run/extracted/metrics.json
- docs/transductive-formal-v74-evidence-20260928.md（v97g 四方向百分比逐项在位）

**测试/审阅结果**
- 只读复核脚本（python-pptx 抽取 + metrics 逐格 + SHA 复算）：全部通过。
- 未重复修改已修好文件；未覆盖任何并发改动。

**DCS 任务与费用**：无（本轮纯本地只读）。

**未关问题**
- 待 Codex 第 4 轮确认（交接件已备：docs/handoff-to-codex-round4-20261009.md）。
- 历史"未覆盖"声明待逐轮基线累积（本轮已记录 HEAD 与状态摘要）。

## 阶段 2a：GenPilot 第一轮·平台事实（完成）

**实际完成事项**
- 通过 DCS Cloud → Genpilot（会话"我们课程项目"）完成第一轮会商；因首轮深挖 18 分钟未收尾（卡在计价端点探测），人工停止后要求"基于已有证据汇总"，得 6 条结论。
- 关键事实：三份 h5ad 平台 file id 与本地 1528/1535/1543 完全一致（human 6ff9e073…、mouse 2d1e6596…、zf 2092aee8…，人文件含 cell_or_nuclei/modality 字段，可支持"单细胞优先"筛选）；SATURN--22 镜像地址确认；资源档 29 档（含 3080Ti/L4 GPU）；**单价无公开接口→待核实**（实证反推 0.011 元/分钟·1c4Gi）；r1d 已失败（10-09 15:41，日志已清理，原因待核实；推断 s 类队列已尝试调度）；downloadFile 公网端点恢复 200；WDL 累计花费 1.13 元。
- 会商记录归档：docs/evidence/genpilot-consultation-20261009.md（含时间、证据位置、待核实标注）。

**证据路径与 SHA**
- docs/evidence/genpilot-consultation-20261009.md（本轮新建）
- 平台侧证据：/Files/ResultData/Notebook/ + dcs preview info + meta/query + dcs image ls + dcs task ls（记录在会商记录中）

**测试/审阅结果**：平台事实与本地记录交叉一致（数据形状、镜像地址、WDL 任务号与费用）；两处待核实（单价、r1d 失败原因）。

**DCS 任务与费用**：本轮无新任务；已花费为历史 WDL 1.13 元（平台实查）。

**未关问题**：单价表待平台补；r1d 失败原因待平台补；"14 次失败 vs 平台 10 条记录"差异待核实。

## 阶段 3：逐方向三方法解释表（完成）

**实际完成事项**
- 产出 docs/evidence/per-direction-three-method-20261009.md：每方法固定口径（数据来源/表示层/query-reference/标签空间/排除规则/评分器/置换/证据等级）+ 六方向分三组表（哺乳动物对 / 人鼠→鱼 / 鱼→人鼠）+ v97g 日志级限定 + 正确数双重复核附录。
- 正确数三方核对：confusion 对角和 = acc × n_q，18 格全通过。
- v97g 分母按 coverage × query 物种细胞数推断（≈1505/1528/1499），明确标"推断值，非文件级"。
- 明确写入：oPCA 与 v97g = 映射标签空间；v99 与 SAMap = 原始标签空间；label-free vs label-aware 差异；不得单表排冠军。

**证据路径**：docs/evidence/per-direction-three-method-20261009.md；底数 results/stage-reports-20261009/per-direction-numbers.json

**测试/审阅结果**：数字程序化生成（无手抄）；confusion 对角和/acc×n_q 双重复核通过。Claude 审阅安排在阶段 2c 一并送审。

**DCS 任务与费用**：无。

## 阶段 4：候选稿与 Word 定向检查（进行中）

**实际完成事项**
- 8 册阶段 PPT + 汇报 2 校模板版逐页标题检查：各册主题互不重复、均回答新问题 ✓
- Word 草稿（deliverables/course5-final-report.docx）定向修订 4 处：
  ① 摘要"斑马鱼方向含混范围"→ 按 query 分组逐方向值；
  ② 消融基线 61.8%→20.4% → 67.4%→20.4%（v72-era 协议内配对）；
  ③ §5.2 标签空间拆分（oPCA/v97g 映射空间；v99/SAMap 原始标签空间）；
  ④ 新增 §5.10 映射表 needs-reviewer 状态段。
- 备份：deliverables/course5-final-report.bak-20261009.docx（修订前版本保留）。
- 复验：旧串 0 次、新串在位（67.4→20.4 / needs-reviewer / 0.5761）。

**证据路径与 SHA**：deliverables/course5-final-report.docx（修订后 42,069 bytes）；备份见上。

**未关问题**：Word 修订后需再渲染/通读一遍（排版是否受影响）；汇报 1 的候选稿形态（状态矩阵）已确认存在。

## 阶段 2b/2c：GenPilot 第二轮 + Claude 反方审阅（完成）

**实际完成事项**
- 第二轮会商（18:49→18:58，7 步取证）：逐方法给出标签通道证据（含脚本行号）、query 入图证据、投影接口可行性（oPCA ✅ / SATURN ⚠️需自写 / SAMap ❌无原生）、泄漏防护机制、A/B 档资源成本估算、做不到项（4 条）。
- Claude 反方审阅（docs/reports/claude-protocol-review-20261009.md）：结论 **revise**；① 为阻塞项——本地材料"SATURN=ref_labels 参与训练"机制写错（正确为 labels 通道；项目自身 09-24 审计已明确）；另发现 oPCA/SAMap 溯源错配、SAMap 近似投影需声明、泄漏清单不全、成本算术矛盾、档名撞车。
- **阻塞项已全链修正**：method-comparison-matrix / per-direction 底表 / metric-lineage / build_report03.js / build_report05.js / build_final_report.py / Word docx；第 3/5 册重建 + 重渲染（CLEAN）+ SHA 重算（03 c858e731…、05 8c8ecedc…）。
- 会商记录追加"Claude 审阅与更正"节（两处对 GenPilot 结论的更正 + 采纳项清单）。

**证据路径与 SHA**：见上列文件；SHA256SUMS.txt 已更新（8 册）。

**测试/审阅结果**：修正项关键词逐册复核在位；Word 主表 36 格 + 分母表 18 格与冻结 metrics 全一致；Claude 审阅归档。

**DCS 任务与费用**：无新任务；已花费 1.13 元（历史 WDL）。

**未关问题**：SATURN 运行时版本/训练命令（待核实）；SAMap 线上脚本（待回捞）；GPU 单价（待核实）；r1d 失败原因（日志已清理）。

## 阶段 5：三档方案 v2 + 审批单（完成）

- 依据 Claude 审阅重写：档名对齐（会商 B = 本方案 C2）、费用算术改正（27×16min≈4.75 元）、0.011 元/分钟适用边界、泄漏清单扩至 8 项、SAMap-approx 硬闸门、mapping 签认设为 C 档硬前置、seed 预注册、inductive 负控、LOO"跨物种级非跨供体级"标注、v97g 排除、单细胞筛选改 n 警示。
- 三张审批单（B-1/C1-1/C2-1）与费用上限列明；**均未提交**。

## 收尾：四类清单与交接（完成）

- docs/longrun-20261009-final-handoff.md：确认 6 / 候选 4 / 待签认待核实 6 / 未运行 3；GenPilot vs Claude 分歧 7 项裁定；候选材料清单与最新 SHA；审批单 3 张；待答问题（用户 3 + 老师 4）。
- round4 交接件已加批次五 SHA 注记（03/05 变更）。

## 验收修正轮（2026-10-09 晚，用户验收反馈 5 项；全部本地完成，未提交任何平台任务）

| # | 验收意见 | 处理 |
|---|---|---|
| ① | 第 5 册 p2/p6 把 1,000 维 macrogene 误写"50 维级" | 已改为"1,000 维 macrogene 空间（v99 评分读取 obsm[macrogenes]，形状 4,606 × 1,000）"与"不是同一维度量级（1,000 维 vs 50 维）"；依据 scripts/dcs_provenance_v99.py:22 `EXPECTED_EMBEDDING_SHAPE=(4606, 1000)`；重建 + 重渲染 CLEAN |
| ② | Word 生成脚本未同步（重建会冲掉手工修正） | 脚本同步 6 处（鱼方向分组/双多数类列/读数 0.4817/消融 67.4/§5.2 拆分/§5.10 needs-reviewer）+ 新增 `fix_settings_zoom` 后处理（zoom 缺 percent 属性为 python-docx 模板既有问题，两版均有，已修）；重建后逐项复验通过、主表 6×6 值全对、Word 渲染 6 页检查通过（另修掉"1. 1)"双编号排版） |
| ③ | 第 3 册"高分包含真值标签的贡献"因果过强 | 改为"训练机制使用细胞类型标签（SATURN：species 前缀 labels；SAMap：keys=cell_type）；该机制对本次分数的贡献尚未单独量化"；v71 运行时待核实标注保留 |
| ④ | C1 缺 SATURN 未见物种可行性证明 | 补源码级判定并写入方案：**C1-SATURN 阻塞**（species_to_gene_idx 未见物种 KeyError；每物种 HVG 块来自自身表达；物种 one-hot 宽度烧进首层权重形状；无冻结指派路径）；C2 中 SATURN 格一并阻塞，如需参与须"重训方案"单独立项 |
| ⑤ | 81 格实际运行次数与费用 | 重算：每方法 9 次运行（3 折×3 seed；单次表示评三层，依据 v98 单任务产出 18 格）；SAMap ≈1.6 元（9×16min，待澄清估算）；旧"27 次/4.75 元"系按逐层重跑计、证据不支持 |

**新 SHA**：03 `c06f791b…`、05 `4990a046…`（其余 6 册不变）；SHA256SUMS.txt 已重算。
**Word**：deliverables/course5-final-report.docx（重建版；备份 .bak-20261009 / .bak2-20261009 保留）。
**边界**：未启动 B/C1/C2 付费任务；未提交 DCS；未充值；未宣称导师签认。

## 验收修正轮（第二批，2026-10-09 深夜；用户只读验收提 2 项口径问题）

| # | 验收意见 | 处理 |
|---|---|---|
| 1 | 方案 C2 仍写"预期产物 81 格"，但 SATURN 27 格已被 C1 判阻塞 | 已改：设计行注明"SATURN 27 格因 C1 源码级阻塞当前不可行"；预期产物行改为"**当前可行子集最多 54 格**（oPCA 27 + SAMap-approx 27）；完整 81 格须待 SATURN 另立方案并过 C1 闸门；子集可在批准后先行，SATURN 方案未立项前完整 C2 不得启动" |
| 2 | Word 主表图例"粗体＝该方向最高值"（实际未加粗）且跨标签空间不宜暗示排名；"显著领先"无配对检验 | 已改：图例删除，改为"跨列标签空间/协议不同（见 §5），同表仅作方向性参考，不构成排名（表内未加粗、未做方法间显著性检验）"；"显著高于/领先"→"数值高于/领先"（摘要 + 读数两处）；脚本同步后重建，zoom 后处理保留 |

**Word 新 SHA-256**：`593d31e6…788f`（42,256 bytes）；重建后复验：双多数类列在位、多数类两列数值全对、无"显著"主张、渲染 6 页检查通过。
**边界**：仍无 DCS 提交/无付费任务/无充值；B/C1/C2 未启动。

## 验收通过（2026-10-09 深夜，用户第二轮只读验收）

- 用户独立核验：C2 子集/完整区分 ✓；Word 排名暗示删除与"数值"措辞 ✓；Word 文件 SHA-256 `593d31e6…788f`、42,256 bytes、结构校验（zoom=percent 100）、双多数类列、逐格数值、第 3 页渲染 ✓；8 册 PPT SHA 8/8 ✓。
- 用户如实说明：其本轮未重新运行 `build_final_report.py`（脚本重建可复现由执行者实际运行验证 + Claude 一致性复审）。
- **规范状态声明**已写入 docs/longrun-20261009-final-handoff.md 末尾（"第一阶段材料可交老师；B/C1/C2 未批准未启动；mapping 待签认；SATURN inductive 需另立方案；C2 若批先做 54 格子集，不称完整 81 格 benchmark；总体=第一阶段材料进入等老师反馈阶段"）。
