# 课题5 阶段汇报总索引（10 阶段划分与产物，2026-10-09）

> 本目录存放汇报 3–10 的 PPT（校模板版）。汇报 1–2 的产物在各自目录（见下表）。
> 全部数字取自冻结证据矩阵（docs/final-evidence-matrix-20261005.md，勘误见 docs/errata-final-evidence-matrix-20261009.md）与三份冻结 metrics.json；
> 生成脚本可重跑：`node build_reportNN.js && python lib/postprocess_bars.py <pptx>`。
> **阅读顺序建议：先看"当前有效状态"，再看"历史批次记录"（后者含已被取代的中间结论）。**

## 当前有效状态（截至 2026-10-12）

> **汇报 3–10 的状态仍按下方各批次 SHA 绑定记录；汇报 1 已于 2026-10-12 另存修订版并完成本地渲染检查（本轮未作 Claude 复审，不覆盖历史稿）。导师签认未完成；历史"未覆盖"声明待基线核验。**

- 产物绑定：`SHA256SUMS.txt`（8 份 pptx 的 SHA-256，LF 行尾，可直接 `sha256sum -c`）
- 定向复核记录：docs/reports/claude-review-03-to-10-r2-20261009.md（对象=最终版 8 册，SHA 复算 8/8）
- 待闭环：Codex 第三轮确认；导师对汇报 7/8 的反馈；历史版本保留需逐轮 SHA 基线累积
- 汇报 1 最新交付（**实质内容版，当前推荐**）：`results/stage-reports-20261012/课题5第01次汇报_实做进度与关键问题_实质版.pptx`（11 页），SHA-256 见 `results/stage-reports-20261012/SHA256SUMS-v3.txt`
- 汇报 1 内容稿（实质内容版）：`docs/reports/report-01-substantive-v3-20261012.md`
- 汇报 1 历史交付（保留，不覆盖）：`results/stage-reports-20261012/课题5第01次汇报_现状与问题定稿_修订版.pptx`（7 页）与 `results/stage-reports-20261009/课题5第01次汇报_现状与问题定稿.pptx`；原内容稿 `docs/reports/report-01-evidence-status-freeze-20261012.md`
- 说明：实质内容版以"我们解决了什么问题"为主线重做，数字仍逐格取自冻结 metrics（30/30 在位校验通过）；本轮未作 Claude 复审

## 阶段划分（按 docs/superpowers/plans/2026-10-08-course5-report-cycle-and-ppt-audit.md）

| # | 主题 | 要回答的新问题 | 内容稿 | PPT | 状态 |
|---|---|---|---|---|---|
| 1 | 现状与问题定稿 | 哪些完成/候选/阻塞？ | docs/reports/report-01-evidence-status-freeze-20261012.md | results/stage-reports-20261012/课题5第01次汇报_现状与问题定稿_修订版.pptx（7 页） | 修订版已生成并本地渲染检查；本轮未作 Claude 复审；历史稿保留 |
| 2 | 数字来源链 | 一个百分比怎么来的？ | docs/reports/report-02-metric-lineage-20261008.md | results/report-02-metric-lineage-20261008/课题5第二阶段汇报_数字来源链_校模板版.pptx | 完成（Claude 复审 pass） |
| 3 | 三方法公平比较边界 | 为什么不能排冠军？ | docs/reports/report-03-method-comparison-20261008.md | 课题5第03次汇报_三方法公平比较边界.pptx（7 页） | 初稿；批次一 Claude pass；追加修订定向复核通过 |
| 4 | ortholog-PCA 基线闭环 | 为什么简单基线有时赢？ | docs/reports/report-04-evidence-closure-20261008.md | 课题5第04次汇报_ortholog-PCA基线闭环.pptx（7 页） | 初稿；批次一 Claude pass；内容稿分母已更正 |
| 5 | SATURN 信号与协议效应 | 信号从哪来？能不能当泛化？ | docs/reports/report-05-saturn-signal-20261009.md | 课题5第05次汇报_SATURN信号与协议效应.pptx（7 页） | 初稿；批次一 Claude pass；消融基线已按勘误三更正 |
| 6 | SAMap 复现与负结果 | 低分/零分怎么得到的？ | docs/reports/report-06-samap-negative-result-20261009.md | 课题5第06次汇报_SAMap复现与负结果.pptx（7 页） | 初稿；批次一 Claude pass；分母表述定向复核通过 |
| 7 | 三方法总矩阵（老师问题专页） | 老师指出的表怎么改？ | docs/reports/report-07-three-method-matrix-20261009.md | 课题5第07次汇报_三方法总矩阵与老师问题.pptx（7 页） | 初稿；批次一 Claude pass；逐方向分母定向复核通过 |
| 8 | mapping 签认与证据责任 | AI 复核 ≠ 导师签认 | docs/reports/report-08-mapping-signoff-20261009.md | 课题5第08次汇报_映射签认与证据责任.pptx（7 页） | 初稿；批次一 Claude pass；议题计数定向复核通过 |
| 9 | 最小 inductive 方案 | 泛化要新增什么证据？ | docs/reports/report-09-inductive-design-20261008.md | 课题5第09次汇报_最小inductive方案.pptx（6 页） | 初稿；批次一 Claude pass；仅设计不运行 |
| 10 | 阶段收口与下一阶段 | 还剩什么要决定？ | docs/reports/report-10-closure-and-next-phase-20261008.md | 课题5第10次汇报_收口与下一阶段.pptx（7 页） | 初稿；批次一 Claude pass；完成声明已降级 |

## 本目录文件

```
build_report03.js … build_report10.js   生成脚本（node + pptxgenjs）
lib/report-template.js                  校模板版式模块（顶栏/logo/标题/页脚/封面）
lib/postprocess_bars.py                 顶栏后处理（snip2DiagRect 斜切 + 蓝条渐变）
frozen-numbers.json                     冻结数字快照（校验用）
SHA256SUMS.txt                          8 份 pptx 的 SHA-256（LF 行尾，可 sha256sum -c）
课题5第0X次汇报_*.pptx                  成品（8 份，共 55 页）
render/rXX-pYY.png                      逐页渲染（校验用）
```

## 版式（全部 8 份统一）

- 康复大学校模板：蓝渐变斜切条 + 金条 + 右上 logo + 藏青标题（12365A）+ 页脚（左标签/右页码，8.5pt）
- 封面：校园底图 + 藏青带（与第一阶段汇报同款）
- 表格：表头藏青 005BAC 白字；卡片浅蓝/浅金/浅玫三色
- 每册末页均为"结论 + 边界"，口径警示随数字出现

## 校验记录（2026-10-09）

- 生成：8/8 成功；顶栏后处理 8/8（snip2DiagRect + 渐变注入）
- 渲染：55 页全部渲染；程序化碰撞检测（卡片切字/压行）**0 处**（历轮共修正 12 处）
- 数字校验：逐册关键词在位检查通过；旧草表数字仅出现在汇报 4/7 的"作废对照"语境
- SHA 绑定：SHA256SUMS.txt 复算 8/8（批次三复核）
- 未提交、未推送；**可核实的原始旧件**未被覆盖（中间修订版曾原地重建、未单独归档；历史"未覆盖"声明待逐轮基线累积核验）

---

# 历史批次记录（以下为过程记录，含已被后续更正取代的中间结论）

## 批次与审阅编号对照（统一命名）

| 工作批次 | 内容 | 对应 Claude 审阅记录 |
|---|---|---|
| 批次一 | Codex 第 1 轮审计 + 11 项修订 | —（修订后进入批次二审阅） |
| 批次二 | Claude 逐册审阅（8/8 pass） | 审阅① = docs/reports/claude-review-03-to-10-20261009.md（头部已加批次标注；含消融 61.8→67.4 等追加更正的更正注记） |
| 批次三 | Codex 第 2 轮复审 + 6 项收尾 + 追加更正 | 审阅② = docs/reports/claude-review-03-to-10-r2-20261009.md（定向复核；SHA 绑定为批次三时点，已加时效注记） |
| 批次四 | Codex 第 3 轮验收 + 方向表述更正（斑马鱼四方向） | 审阅③ = docs/reports/claude-review-03-to-10-r4-20261009.md（定向复核 **pass**，绑定批次四重建后 SHA） |

（此前"批次一/二/三"在审阅文件与索引中编号口径不同，本表为统一对照；历史小节标题保留原文。）

## 批次一：Codex 只读审计第 1 轮（2026-10-09）与修订记录 —— 历史，已被后续批次取代

**审计结论：revise**（A/B/C/D/G 需修改，E/F 通过，H 历史声明未确认）。逐项修订如下（全部已落实并重建）：

| 审计项 | 修订内容 |
|---|---|
| 汇报 3 | v97g coarse 标签空间改为 mapped-space；n_q 行拆为 coarse（1,505/0.9805）与 exact（1,535/1.0） |
| 汇报 4 | z→m 归因改为事实性（query 侧排除 30）；删"排除 44 未生效"；"shuffle_p 全 0.0" 收窄为 coarse 六方向（m→z exact 层 0.02）；ceiling 标注为 SATURN 侧辅助参照 |
| 汇报 5 | 删"与 ortholog-PCA 格局一致"；消融改为"对蛋白嵌入置换敏感、支持重要贡献"；~~61.8% 标注 v72-era 口径~~ → **批次二更正为 67.4%→20.4%（v72-era 同协议配对）**；删"接近随机"；ceiling 差值改为描述性 |
| 汇报 6 | "四方向为零"→三方向为零；删"≤随机"（改为 shuffle_p 0.0/0.035 与 1.0 分列）；待检验解释降级；included 旗标明确为非合法计分口径 |
| 汇报 7 | 多数类拆为两列（映射空间 0.4817… / 原始标签 0.4618…）；口径框补 n_q/coverage（批次三再补逐方向）；p6 SATURN 标签空间拆分；删"61.79% 与 0.6179 两种口径"表述 |
| 汇报 8 | SAMap 鱼排除 41→47（=1,543−1,496）；删"混合旗标所致/五方一致"，改为"根因待核验 + 四方一致"；九项表补 n/a 3 行与 ⑧⑨；新增行 25 cmlc1/vmhc 疑点（批次三改为"5 议题涉及 6 条源映射"） |
| 汇报 9 | 可见性按方法拆分（oPCA label-free）；删"乐观上界/现实下界/记忆依赖"；标注候选方案 + 投影接口待验证 |
| 汇报 10 | 撤回"全部逐细胞复算"（v97g 日志级）；"周期完成"→"初稿齐备"；签认范围限定为 mapping 相关；"未覆盖"声明改为待基线核验 |
| 上游 | docs/errata-final-evidence-matrix-20261009.md（鱼分母 1,499/1,496；v97g mapped-space；多数类分列）；render-report 页脚 8.5pt 同步 |

- 重建后：55 页全部重渲染，程序化碰撞检测 **0 处**；修正项关键词逐册复核全部在位。
- 历史"未覆盖"声明：待补轮次基线后确认（不默认通过、不判违规）。

## 批次二（= Claude 审阅①）：逐册审阅（2026-10-09）—— 不直接代表最终版

- 结论：**pass（8/8 册）**；11 项 Codex must_fix 全部在位，未发现修订引入的实质错误。
- 归档：docs/reports/claude-review-03-to-10-20261009.md（头部已加批次标注）
- Claude 发现的上游数据链问题（已处理）：消融基线 61.8%→20.4% 系跨协议混排，同协议配对应为 **67.4%→20.4%（v72-era）**；
  已写入勘误三（docs/errata-final-evidence-matrix-20261009.md）并同步汇报 3/5、method-comparison-matrix §五、report-05。
- 其余 3 项措辞残余（v99 空间表述/第 6 册语气/第 8 册对账表述）已修正并重建。

## 批次三：Codex 第 2 轮复审与 6 项收尾（2026-10-09）—— 当前轮

**Codex 结论：revise（6 项收尾）**，其中 C/E 通过。逐项落实：

| 收尾项 | 落实 |
|---|---|
| ① 标签空间残留 | 汇报 3 p7 + 方法比较矩阵 §六改为"ortholog-PCA、SATURN v97g = 映射标签空间；SATURN v99、SAMap = 原始标签空间"；**定向复核追加发现并修正 §三 表（v97g→mapped-space；v99 n_q/coverage 拆 coarse 1,505/0.9805 与 exact 1,535/1.0）** |
| ② 逐方向分母 | 汇报 7 p3 口径框补 coarse 逐方向 n_q（oPCA/v99 = 1505/1528/1499/1499/1528/1505；SAMap = 1505/1528/1496/1496/1528/1505）；汇报 6 p6 改"各按各自分母计算"；report-04 内容稿分母序列更正 |
| ③ 映射议题计数 | 汇报 8 p5 改"5 个议题（涉及 6 条源映射）"、第 5 行标 high（另有命名疑点）；汇报 10 p5 与 report-08 同步 |
| ④ 状态矩阵消融 | A7 行改为"67.4→20.4（v72-era 同协议历史配对；v97g 对应消融未重跑）" |
| ⑤ Claude 批次与 SHA 绑定 | 批次一记录加批次标注；定向复核归档 claude-review-03-to-10-r2-20261009.md；新增 SHA256SUMS.txt（LF，8/8 复算一致） |
| ⑥ 索引批次区分 | 本文件重写：当前有效状态在前，历史批次在后并标注取代关系 |

**批次三复核（Claude 定向复核）**：①②③④⑤ 通过（SHA 复算 8/8；5 页渲染抽核无遮挡）；复核中发现的 §三/§五 残留与 SHA 清单 CRLF 已当场修正。定向复核记录归档：docs/reports/claude-review-03-to-10-r2-20261009.md。

## 批次四：Codex 第三轮验收与方向表述更正（2026-10-09）—— 当前轮

**Codex 结论：revise**（D/E 通过；A/B/C/F 需改）。核心问题：第 3 册 p7 与方法矩阵 §五把"斑马鱼方向"写成含混范围，且把 query/目标方向讲反（鱼作 query 为 z→h 0.1813 / z→m 0.5761；0.1961 / 0.2755 是鱼作目标）。逐项落实：

| 项 | 落实 |
|---|---|
| 方向表述 | 第 3 册 p7 与矩阵 §五 改为**逐方向列数**：oPCA h→z 0.1961 / m→z 0.2755 / z→h 0.1813 / z→m 0.5761；SATURN v97g 0.1835 / 0.3009 / 0.2474 / 0.4651；SAMap 0.0341 / 0 / 0 / 0（与三份 metrics 逐格核对） |
| 读数 | 改为"仅 oPCA 的 z→m（0.5761）超过其多数类 0.4817；其余方向均弱或无信号" |
| 版本保留措辞 | 第 10 册 p4 标题改"交付物清单（版本化；可核实旧件保留）"、band 与 index 校验记录行明确"中间修订版曾原地重建、未单独归档" |
| 历史记录 | 批次一/批次二审阅记录加**更正注记**（不改写原文），标明范围写法错误已按批次四更正 |
| 重建与复核 | 第 3/10 册重建 + 后处理 + 重渲染（两册各 7 页，碰撞检测 CLEAN）；SHA256SUMS.txt 重算（8/8，`sha256sum -c` 通过） |

- 批次四定向复核：docs/reports/claude-review-03-to-10-r4-20261009.md（SHA 绑定，见该文件）

## 待办

- Codex 第三轮确认（本轮 6 项 + 定向复核追加修正）
- 老师对汇报 7 表格与汇报 8 签认请求的反馈（5 个议题，涉及 6 条源映射）
- 历史"未覆盖"声明：逐轮记录 HEAD 与产物 SHA，累积基线后闭环

## 批次五：长任务（平台会商 + SATURN 标签机制更正，2026-10-09 晚）

**触发**：长任务第 2 步平台会商发现 SATURN 标签可见性表述问题；Claude 反方审阅判定为**阻塞项**（本地材料把机制写错）。

**更正内容**：本地材料原写 "SATURN = ref_labels 参与训练" 属机制错误。正确表述：
- SATURN = label-aware，但标签通道是 **`labels`（细胞类型整数 id）**（cross_species miner 构造正负样本）；
- `ref_labels` 仅为**输出列/评估真值**，不参与 miner（输出 h5ad 含该列 ≠ 训练使用了它；项目 2026-09-24 审计已明确）；
- 运行时源码版本（v71/v99 vs checked-in）与训练命令行**未闭合 → 待核实**。

**受影响文件（已全部修正）**：docs/evidence/method-comparison-matrix-20261008.md、docs/evidence/per-direction-three-method-20261009.md、
docs/evidence/metric-lineage-20261008.md（SAMap 行加"运行脚本待回捞"）、results/stage-reports-20261009/build_report03.js、
build_report05.js、scripts/build_final_report.py、deliverables/course5-final-report.docx（§3.2 与 §3.3）。

**重建与绑定**：第 3/5 册重建 + 重渲染（各 7 页，碰撞 CLEAN）；
**SHA 变化（经两轮重建）**：03 d04a02e8→c858e731→**c06f791b…**；05 9b9dbf96→8c8ecedc→**4990a046…**（第一轮为 SATURN 机制更正；第二轮为验收修正：第 5 册 1,000 维、第 3 册因果措辞）；其余 6 册不变；SHA256SUMS.txt 已重算。

**另**：SAMap 侧补充"线上运行脚本（samap_script.py c0f05b89）≠ checked-in（71dd08a3），内容待回捞"。
