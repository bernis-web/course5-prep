# 一致性审计：作废数字残留与唯一权威索引（2026-11-11）

> **用途**：把「作废数字仍在被引用」的地方一次性列清，并把现行数字收敛到唯一权威源。
> 配套文件：`docs/reports/number-index-20261111.md`（**唯一权威数值索引**，以后引用只认它）。
>
> **一句话结论**：清单里的 14 个作废串在 **111 个文件**里还有残留；但真正会误导人的只有
> **6 个现行文件**——最严重的是入门手册与口径陷阱两篇，它们把 `saturn_convention_v2.json`
> （`0.1269/0.1640/0.3658/0.3563`，**已被明令「别混用」的第 2.5 代**）当成了现行六向，
> 而这组数比 v2 终版老了整整一代。

---

## 一、违规清单（三类分开）

### 扫描口径（可复现）

| 项 | 内容 |
|---|---|
| 范围 | 全仓 `.md`（281 个）、`.docx`（19 个）、`.pptx`（46 个）、`deliverables/**` 与 `docs/**` 下 `.json`（5 个）；另加 `.pdf`（32 个）、`.csv/.xlsx`（素材）作为补充命中 |
| 排除 | `node_modules / .venv39 / wheelhouse / tmp / .git / __pycache__ / .tmp-*` |
| 方法 | `.md/.json` 逐行（行号）；`.docx` 段落号 + 表格 `tableN!rXcY`；`.pptx` 幻灯片号 + `notes`；**另做一遍 zip 内原始 XML 扫描**，专门捞 `python-docx/pptx` 抽不到的部分（图表缓存 `ppt/charts/*.xml`、文本框） |
| 脚本 | `scripts/audit_consistency_scan.py`（主）、`scripts/_rawxml_scan.py`（图表）、`scripts/_sup2.py`（PDF/CSV/XLSX）、`scripts/_sup_scan.py`（`0.65` 简写形态） |
| 产物 | `results/audit-consistency-20261111/{hits.json,hits-rawxml.json,hits-pdf-csv.json,supplement-0.65.json}` |
| 命中总量 | **111 个文件**（md 39 / pdf 32 / pptx 22 / docx 14 / json 2 / csv 1 / xlsx 1） |

**为什么必须扫图表 XML**：现行汇报 PPT 的「四方法 macro-F1 对比图」与「原口径 vs 修正口径图」
数值都存在 `ppt/charts/chart*.xml` 的缓存里，`python-pptx` 的 `shape.has_text_frame` 读不到。
不扫这一层会漏掉本报告最重要的一条（见 §1.1 第 12 条）。

---

### 1.1 ① 现行交付物 → **必须改**（9 个文件，18 条命中；另有 3 条"缺件/不同步"）

> 判据：文件是**当前对外/对组员**的版本（2026-11-08 之后仍在维护），且作废值被当成
> **现状陈述**或**结论依据**引用，而非「对照/更正」语境。

| # | 文件 | 位置 | 命中的作废串 | 应该改成 | 说明 |
|---|---|---|---|---|---|
| 1 | `docs/team-handbook/part1-问题与方法.md` | L193 | `0.1269 / 0.1640 / 0.3658 / 0.3563` | `0.1282 / 0.1386 / 0.4076 / 0.2961` | 原句「修正后 SATURN 六向为 0.3522/0.2566/**0.1269/0.1640/0.3658/0.3563**」——前两个对、后四个是第 2.5 代。**这是全仓最危险的一处**，因为它自称"修正后现行" |
| 2 | 同上 | L187（表格 SATURN 行） | `0.3658 / 0.3563` + `459–1309` | `0.4076 / 0.2961`；分母 `1469–1528` | 「修正后为 0.3658/0.3563」同错；`n_q` 区间是老口径（459–1309），v2 下是 1469–1528 |
| 3 | 同上 | L203（覆盖率表） | `97–100%`（同格引 `29–87%` 作对照） | **`43–100%`** | `29–87%` 在「旧文档写的」语境里，属更正引用、可留；但同行宣称的 **97–100% 不成立**——斑马鱼→人实测 663/1528 = **43.4%**，斑马鱼→鼠 1405/1505 = 93.4% |
| 4 | 同上 | L185、L224、L225 | oPCA `0.1654`；L225 `0.3658/0.3563` | oPCA `0.1506`（v2 现算）；SATURN `0.4076/0.2961` | oPCA 列仍是 v1 冻结值；权威表是 v2 映射重算值 |
| 5 | `docs/team-handbook/part2-口径陷阱与三场景.md` | L26–27 | `0.3658 / 0.3563`（标"修正后"） | `0.4076 / 0.2961` | 两行小表的"修正后"列整列错代 |
| 6 | 同上 | L93–98（现行六向表） | `0.1269 / 0.1640 / 0.3658 / 0.3563` + 分母 `1499` | `0.1282 / 0.1386 / 0.4076 / 0.2961` + 分母 `1469` | 表头写「修正后」、脚注指向 `saturn_convention_v2.json` —— 正是被明令别混用的那个文件 |
| 7 | 同上 | L103 | 「分母第一次全部一致 **1499–1528**」 | `1469–1528` | v2 下鱼两向分母 1469，不是 1499 |
| 8 | 同上 | L151–154（远缘场景表） | SATURN `0.1269/0.1640/0.3658/0.3563`；oPCA `0.1654/0.1512/0.2177/0.4405` | SATURN `0.1282/0.1386/0.4076/0.2961`；oPCA `0.1506/0.2131/0.2816/0.4186` | 同一张表的两个方法列都旧了 |
| 9 | 同上 | L209 | 「**现行**以 `saturn_convention_v2.json` 为准：0.3658 / 0.3563」 | 改为 `saturn_convention_mapv2.json` → `strict_cell.mf1` | 这是一句**权威性错误声明**，危害最大：它把作废文件钉成"现行" |
| 10 | 同上 | L19–20 | `0.6500 / 0.6510`（"最初的表"里 SATURN 大胜） | 保留数字，补「（v1 口径，**已作废**；仅作判定实验的旧值）」 | 有「最初」语义但无作废标注，读者会当成"曾经的真相" |
| 11 | `docs/team-handbook/part3-可复现与FAQ.md` | L73 | `459–1309` | `1469–1528` | SATURN 分母区间 |
| 12 | `docs/team-handbook/part4-汇报说明小白版.md` | L161 | 「SATURN 从 **0.6500** 掉到 0.4076」 | 改成「原口径 0.6500（**已作废**）→ 0.4076」，或直接写 v1 `published` → v2 `strict_cell` 同指标对照 | L156–157 判定实验表（列名「旧值」）**合法**，可留 |
| 13 | `docs/reports/time-memory-benchmark-20261023.md` | L66 | 「有 GPU、鼠↔鱼 → **选 SATURN（0.65，最高）**」 | 「鼠↔鱼 → **选 scVI（0.4248 / 0.4786）**；SATURN 0.4076 / 0.2961 不再领先」 | 这是一条**选型结论**，与现行结论（SATURN 一个方向都不赢）正面冲突 |
| 14 | `deliverables/课题5-汇报-v5-20261111.pptx` | `ppt/charts/chart1.xml` | oPCA 系列 `0.4405 / 0.2177 / 0.1512 / 0.1654` | `0.4186 / 0.2816 / 0.2131 / 0.1506` | 现行主结果图的 oPCA 列仍是 v1 冻结值；`chart3.xml`（原口径 vs 修正口径）**合法**，不动 |
| 15 | `deliverables/课题5-组员汇报说明-小白版-20261110.docx` | para#67 | 「从 **0.6500** 掉到 0.4076」 | 补「原口径（已作废）」 | table6「旧值 / 错的那种（我们用的）」**合法** |
| 16 | `deliverables/课题5-组员汇报说明-小白版-20261110.pdf` | p5、p7 | 同上（孪生件） | docx 改完**重出 PDF** | 现在 PDF 与 docx 同步，但两者都带未标注的 0.6500 |
| 17 | `docs/execution/20261104-队友交接总纲.md` | L386 | 六向 `0.1269/0.1640/0.3658/0.3563` 称为"修正后" | v2 六向 | 该文件是**交接给下一任**的现行口径 Q&A，不是历史记录 |
| 18 | `deliverables/`（缺件） | — | v5 PPT **无 PDF 孪生**（v4 的 PDF 停在 11:01，v5 是 21:13 生成） | 补出 `课题5-汇报-v5-20261111.pdf` | 交出去的 PDF 版本落后于 PPTX |

**合计**：`part1` 5 处、`part2` 8 处、`part3` 1 处、`part4` 1 处、`time-memory` 1 处、
`v5.pptx` 1 处（图表重做）、`小白版.docx` 1 处、`小白版.pdf` 重出、`交接总纲.md` 1 处、出 v5 PDF。

---

### 1.2 ② 历史留档 → **保留，但文件头必须加一句作废声明**

> 判据：2026-11-08 之前定稿、已对外讲过/交过的版本。改数字等于篡改历史。
> **统一动作**：每个文件第一段前插一行
> `> ⚠️ 本节数字已作废，见 docs/reports/number-index-20261111.md 与 docs/execution/20261108-更正索引.md`

| 文件 | 命中 | 位置 | 命中串 |
|---|---|---|---|
| `deliverables/场景化选型指南-v1-20261017.md` | 3 | L26,51,67 | V01–V04 |
| `deliverables/场景化选型指南-v2-20261019.md` | 6 | L28,56–59,176 | V01–V06, V14 |
| `deliverables/场景化选型指南-v3-20261022.md` | 6 | L28,56–59,200 | 同上 |
| `deliverables/场景化选型指南-v4-20261023.md` | 6 | L28,56–59,240 | 同上 |
| `deliverables/场景化选型指南-v5-20261023.md` | 6 | L28,56–59,240 | 同上 |
| `deliverables/场景化选型指南-v6-20261027.md` | 6 | L28,56–59,283 | 同上 |
| `deliverables/course5-final-report-v2-20261023.docx` | 9 | 全文 + 表 | V01–V06, V14 |
| `deliverables/课题5-项目说明文档-组员版-20261023.docx` | 8 | 全文 + 表 | V01–V06, V14 |
| `deliverables/课题5第02次汇报-逐页讲解稿-20261027.docx` | 8 | 全文 + 表 | V01–V06, V14 |
| `deliverables/课题5-组员入门手册-20261104.docx` | 25 | 第二章整章 + 判定表 | V01–V08, V14, X25 |
| `deliverables/课题5-组员入门手册-20261104.pdf` | 35 | p — | 同上（PDF 滞后于 docx） |
| `deliverables/课题5-组员交接总纲-20261104.docx` | 3 | §Q&A + 表 | V05,V07,V08,V12,V14,X25 |
| `deliverables/课题5-组员交接总纲-20261104.pdf` | 13 | p — | 同上 |
| `deliverables/课题5-老师七条意见回应-20261030.docx` | 22 | para#9,70；table2,3,8,11,12 | V01–V12, V14, X25 |
| `deliverables/tr_render/课题5-老师七条意见回应-20261030.pdf` | 17 | p — | 同上 |
| `deliverables/课题5-总交接文档-20261028.docx` | 3（行）/ 9 串 | — | V01–V08, V14, X25 |
| `deliverables/mh_render/课题5-总交接文档-20261028.pdf` | 9 | p — | 同上 |
| `deliverables/fr_render/course5-final-report-v2-20261023.pdf` | 9 | p — | V01–V06, V14 |
| `deliverables/td_render/课题5-项目说明文档-组员版-20261023.pdf` | 8 | p — | V01–V06, V14 |
| `deliverables/课题5-汇报-v3-学校模板-20261110.pptx` | 1 | slide7 notes + `charts/chart3.xml` | V05（notes）；chart3 属更正对照，合法 |
| `deliverables/课题5-汇报-v3-学校模板-20261110.pdf` | 5 | p7 | V01,V03,V04,V05,V06（图表渲染值） |
| `deliverables/课题5-汇报讲稿-20261110.docx` | 1 | para#159 | V05,V12（**更正语境，合法**） |
| `deliverables/课题5-汇报讲稿-20261110.pdf` | 4 | p — | V05,V12 |
| `deliverables/课题5-汇报讲稿-学校模板-20261110.docx` | 1 | — | V05,V12（更正语境） |
| `deliverables/课题5-汇报讲稿-学校模板-20261110.pdf` | 3 | p — | V05,V12 |
| `deliverables/课题5-汇报讲稿-v3-20261110.docx` | 1 | — | V05（更正语境） |
| `deliverables/课题5-汇报讲稿-v3-20261110.pdf` | 1 | p — | V05 |
| `deliverables/课题5-汇报-讲故事版-20261110.pptx` | 2 | slide11 + notes11/12 | V05（讲稿原话"原来 0.65"）；notes12 的 865 是**更正句** |
| `deliverables/课题5-汇报-讲故事版-20261110.pdf` | 1 | p11 | V05 |
| `deliverables/课题5-汇报-讲故事版-学校模板-20261110.pptx` | 2 | 同上 | 同上（notes12 更正是加分项，保留） |
| `deliverables/课题5-汇报-讲故事版-学校模板-20261110.pdf` | 1 | p — | V05 |
| `results/stage-reports-20261017/*.pptx`（3 个）+ `render*/` PDF（3 个） | 7×3 / 7×3 | slide4 | V01–V06 |
| `results/stage-reports-20261019/*.pptx`（4 个）+ PDF（4 个） | 1–2 / 2–3 | slide7/8/9 + `charts/chart1.xml` | V14 + 图表 V01–V06 |
| `results/stage-reports-20261023/课题5第03次汇报_公平比较边界.pptx` + PDF | 2 | slide3,7 | V05,V06,V14 |
| `results/stage-reports-20261023/课题5第04次汇报_scVI与批次混合.pptx` + PDF | 7 | slide3 | V01–V06,V14 |
| `results/stage-reports-20261102/*`（含 `_candidate*`，共 7 组 pptx/pdf） | 17–25 | slide4,5,6,9 | V01–V11（含 **对外发过的版本**） |
| `docs/execution/20261017-scvi-submission-package.md` | 4 | L118–121 | V01,V02,V03,V06 |
| `docs/execution/20261018-session-state.md` | 6 | L362–367 | V01–V06 |
| `docs/execution/20261019-handoff-full.md` | 7 | L207–212,262 | V01–V06,V14 |
| `docs/execution/20261023-resume-point.md` | 6 | L27–32 | V01–V06 |
| `docs/execution/20261028-master-handoff.md` | 4 | L89,90,146,238 | V01–V08,V14（**L89 已有红框声明**，可作模板） |
| `docs/reports/report-02-metric-lineage-20261019.md` | 9 | L150–155,160,176,198 | V01–V06,V14 |
| `docs/reports/report-03-fairness-boundaries-20261023.md` | 4 | L76,143,144,160 | V03,V05,V14 |
| `docs/reports/report-04-scvi-and-batch-20261023.md` | 7 | L68–73,76 | V01–V06 |
| `docs/reports/report-07-closure-20261023.md` | 1 | L69 | V05,V06 |
| `docs/reports/report-08-teacher-reply-20261030.md` | 16 | L28,36,50–53,123,125,188–193,197,209 | V01–V14 |
| `docs/reports/report-10-mapping-v2-proposal-20261108.md` | 3 | L19,20,52 | V12 |
| `docs/reports/report-11-mapping-signoff-20261109.md` | 1 | L58 | V12 |
| `docs/reports/report-12-full-recap-20261110.md` | 7 | L99,119–124 | V01–V06（L119–124 是「旧→现行」对照表，**合法**；L99 "报出 0.6500/0.6510" 补作废标注即可） |
| `docs/reports/scvi-cross-species-result-20261019.md` | 6 | L91–96 | V01–V06 |
| `docs/reports/unified-coarse-macro-f1-20261017.md` | 6 | L37–42 | V01–V06 |
| `docs/reports/report02-walkthrough-content.json` | 8 | — | V01–V06,V14 |
| `docs/reports/team_doc_content.json` | 8 | — | V01–V06,V14 |
| `docs/reports/课题5第02次汇报_数字来源链_内容稿.docx` + `docx_render/*.pdf` | 9 / 9 | — | V01–V06,V14 |
| `_claude/20261111-1248-low-accuracy-publishability.md` | 6 | L114,174,283,403,408,502 | V03,V04,V09,V11 |
| `_claude/q1-low-accuracy-and-publishability.md` | 1 | L104 | V09,V11 |
| `.agent-handoff/20261104-1215-关机断点.md` | 1 | L92 | V07,V08 |
| `.agent-handoff/20261111-1300-mainline-reframe.md` | 2 | L200,1130 | V01,V03,V04,V09,V11（本身在讲作废，属更正语境） |

**特别说明两个文件**：
- `课题5-组员入门手册-20261104`（docx 25 处 / PDF 35 处）：更正索引早已点名「第二章整章用
  `0.04–0.19` 当教学案例，机制已被推翻，**下次重印前必须重写该章**」。它既是历史件，也是**待办**。
- `课题5-老师七条意见回应-20261030`：见 §三 冲突 D2 —— 更正索引声称它「已按新值重出」，
  实际 22 处旧值原封不动。

---

### 1.3 ③ 更正报告 / 更正性引用 → **不算违规**

> 判据：文件本身就在讲"旧值错在哪/旧→新对照"，出现作废值是它的**工作内容**。

| 文件 | 位置 | 命中串 | 为什么允许 |
|---|---|---|---|
| `docs/reports/report-09-corrections-20261108.md` | L60–65,75–80,85,169–173 | V01–V08,V12 | 更正报告本体。**但**：L12 与 L79 把「修正后」写成 `0.3658/0.3563`（第 2.5 代），需补一句「v2 映射后为 0.4076/0.2961」 |
| `docs/execution/20261108-更正索引.md` | L33,34,50 | V01–V08,V12 | 本索引就是作废清单；**但** §二 表格「已更新为现行口径」里 `老师七条意见回应` 一条与事实不符（见 §三 D2） |
| `docs/execution/20261111-obsolete-numbers.md` | L28,64–71 | V01,V03,V04,V09,V11 | 作废清单本体 |
| `docs/execution/20261111-mainline-reframe.md` | L19,21,101,188,196–203 | V01,V03,V04,V09,V11 | 重定主线稿，逐行标「作废」 |
| `deliverables/课题5-数据更正说明-20261108.pptx` | slide3,4 | V01–V08,X25 | 更正说明本体（4 页，对外首页） |
| `deliverables/课题5-数据更正说明-20261109.pptx` | slide3,4 | 同上 | 同上 |
| `deliverables/课题5-汇报-v4-20261111.pptx` / `v5-20261111.pptx` | `charts/chart3.xml`（系列名「原（错）」） | V01,V03–V06 | 图题就是「原口径 vs 修正口径」，系列 2 = v2 终版六值 |
| `deliverables/课题5-汇报-v4/v5.pptx` | `notesSlide7.xml` | V05（"原来 0.65，改完 0.41"） | 讲者提词，先旧后新的叙述 |
| `deliverables/课题5-PPT制作交接包-20261110.docx` | table7 `r2c2,r3c2,r4c2,r5c2,r6c2,r7c2` | V01,V03–V06 | 表头「原口径（**错**）/ 修正后 / 虚高」，标注齐全。建议列名统一成「原口径（**已作废**）」 |
| `deliverables/PPT交接包/03_素材/修正对比.csv` | L2–L7 | V01–V06 | 同上，两列对照；建议表头加「（已作废）」 |
| `deliverables/PPT交接包/03_素材/数据源.xlsx` | `修正对比!r2,r4,r5,r6,r7` | V01,V03–V06 | 同上 |
| `docs/team-handbook/part2-…` | L74–79（四种约定判定实验） | V01–V06 + X25 | 「冻结值（旧）」是实验输入，必须存在。**但** B 列 `0.3522…0.3563` 是 v1 映射下的结果，需标注「v1 映射」 |
| `docs/team-handbook/part2-…` | L156 | V05,V07 | 明写「已作废」 |
| `docs/team-handbook/part1-…` | L195 | V07,V08 | 明写「公平口径 0.4560/0.4588 已作废」 |
| `docs/team-handbook/part4-…` | L156–157, L177 | V01,V05,V12 | 判定实验（列名「旧值」）+ 865 更正句 |
| `deliverables/课题5-组员汇报说明-小白版-20261110.docx` | table6, para#73 | V01,V05,V12 | 表头「旧值 / 错的那种」；865 是更正句 |
| `deliverables/课题5-汇报-讲故事版*.pptx` | notesSlide12 | V12（865） | 「旧文档写 865 不准」的更正句 |
| `docs/reports/report-15-paper-evidence-v0.1-20261111.md` | L283 | V09,V11 | 明写「禁止再引用 0.0428–0.1940」 |
| `results/convention-20261111/drop_unmapped_audit.md` | L18 | V12 | 865 的机制审计 |

---

## 二、唯一权威数值索引

**完整版单独成文：`docs/reports/number-index-20261111.md`**（12 节，含每条数字的
`值 / 源文件 / 字段路径`）。此处只放最常被引错的三块。

### 2.1 SATURN 六向（唯一现行）

源：`results/bootstrap-20261030/saturn_convention_mapv2.json` → `directions.<dir>.strict_cell.{mf1,acc}`

| 方向 | macro-F1 | accuracy | 分母 |
|---|---|---|---|
| 人→鼠 | **0.3522** | 0.5887 | 1505 |
| 鼠→人 | **0.2566** | 0.2271 | 1528 |
| 人→斑马鱼 | **0.1282** | 0.1811 | 1469 |
| 斑马鱼→人 | **0.1386** | 0.2147 | 1528 |
| 鼠→斑马鱼 | **0.4076** | 0.3036 | 1469 |
| 斑马鱼→鼠 | **0.2961** | 0.4565 | 1505 |

### 2.2 四代 SATURN 值（为什么仓库里会有四套）

| 代际 | 六向 | 出处 | 状态 |
|---|---|---|---|
| 第 1 代 v1 `published` | 0.4147 / 0.4010 / 0.2479 / 0.4021 / 0.6500 / 0.6510 | `saturn_convention.json` | ⛔ |
| 第 1.5 代 v1 `strict_cell`（旧称"公平口径"） | 0.3402 / 0.3118 / 0.2051 / 0.2139 / **0.4560 / 0.4588** | 同上 | ⛔ |
| 第 2 代 `saturn_convention_v2.json` | 0.3522 / 0.2566 / **0.1269 / 0.1640 / 0.3658 / 0.3563** | `saturn_convention_v2.json` | ⛔ **最常被误当现行** |
| **第 3 代（现行）** | **0.3522 / 0.2566 / 0.1282 / 0.1386 / 0.4076 / 0.2961** | `saturn_convention_mapv2.json` | ✅ |

### 2.3 `865` 与 `30`

| 数字 | 含义 | 字段 |
|---|---|---|
| **865** | 斑马鱼→人、**预测侧**被判成 `Orthers` 的细胞数 | `directions.zebrafish->human.n_dropped_unmappable` |
| **30** | 人→斑马鱼 / 鼠→斑马鱼、**真值侧** `Orthers` 细胞数 | `directions.*.truth_unmapped_labels.Orthers` |
| 100 | 斑马鱼→鼠、预测侧丢的 `Orthers` 数 | `directions.zebrafish->mouse.n_dropped_unmappable` |

---

## 三、互相矛盾的版本对

| # | 冲突 | 一处 | 另一处 | 影响 | 建议 |
|---|---|---|---|---|---|
| **D1** | **四代 SATURN 六向并存**，且第 2 代被三处当"现行" | `saturn_convention_v2.json`：`0.1269/0.1640/0.3658/0.3563`（被 `part1:193`、`part2:93-98`、`part2:209`、`交接总纲:386` 引用） | `saturn_convention_mapv2.json`：`0.1282/0.1386/0.4076/0.2961`（`current-table.md`、`更正索引`） | 斑马鱼→人 / 鼠→斑马鱼 差 0.04–0.09，**推荐结论可能被算反** | 以 mapv2 为唯一来源；`saturn_convention_v2.json` 文件首行加「⛔ 作废，勿引用」 |
| **D2** | **更正索引谎报了已修状态** | `docs/execution/20261108-更正索引.md` §二：「`课题5-老师七条意见回应-20261030.docx` 已按新值重出（含更正声明）」 | 该 docx 实际仍有 **22 处**旧值（table2/3/8/11），仅 table12 有更正注 | 老师拿到的回应稿仍是旧数；若被问"你们不是说更正了吗"会很难看 | 要么真重出，要么把更正索引那句改成「未重出，仅加声明」 |
| **D3** | **选中结论互斥** | `docs/reports/time-memory-benchmark-20261023.md:66`：「有 GPU、鼠↔鱼 → 选 SATURN（0.65，最高）」 | `part2:102`/`part1:195`：「SATURN 一个方向都不赢，四向全选 scVI」 | 同一仓库给两套选型建议 | 改 time-memory 那格（见 §1.1 第 13 条） |
| **D4** | **现行 PPT 主结果图的 oPCA 列 vs 权威表** | `课题5-汇报-v5-20261111.pptx` `chart1.xml`：oPCA `0.4405/0.2177/0.1512/0.1654` | `current-table.json`：oPCA `0.4186/0.2816/0.2131/0.1506`（我已用 `rerun-v2/confusion/*` 独立重算复核一致） | 图上 oPCA 柱子整体偏移，鼠→斑马鱼差 0.064 | 重做 chart1（取值走 `current-table.json`） |
| **D5** | **三张"权威表"同时存在** | `results/current-20261111/current-table.md`（42 行，声称「以后所有对外数字都从这张表取」） | ① `docs/reports/unified-coarse-macro-f1-20261017.md` ② `docs/team-handbook/part2` 表 ③ `docs/reports/audit-stats-20261111.md` | 谁都能自称权威 | current-table 立为唯一；其余三处表头改为「派生自 current-table」 |
| **D6** | **跨门同文件两套 mf1** | `results/phase-20261022/crossphylum/metrics.json` 存值 `0.0711/0.0732/0.0652/0.0802` | 同文件混淆矩阵重算 `0.0235/0.0257/0.0241/0.0267`（我已复核，acc 逐位吻合） | 差约 3 倍，且方向相反（存值让跨门看起来"还行"） | 只引用重算值；存值字段加 `"status":"contaminated"` |
| **D7** | **scVI 鱼两向分母双版本** | `bootstrap.json`：n_q = **1499**（v1） | v2 应为 **1469** | 分母差 30（`Orthers`），分数与 CI 都要重算 | 引用时强制标注「v1 分母，待重跑」（current-table 已标，但 deck/手册没标） |
| **D8** | **时间/内存两套实测** | `time-memory-benchmark-20261023.md`：oPCA 30s / 1.19GB；scVI 门内 28m40s（墙钟）| `part1:185-186`：oPCA 26.7s / 1.31GB；scVI **8.5 分钟**（实际计算）、平台含 IO 15m16s | 同一数字两种口径混写，读者以为矛盾 | 统一「实际计算」口径，或两列并列（墙钟 / 计算） |
| **D9** | **SATURN 覆盖率声明失真** | `part1:203`：SATURN 覆盖率 **97–100%**（"2026-11-08 更正后"） | `saturn_convention_mapv2.json`：斑马鱼→人 663/1528 = **43.4%**、斑马鱼→鼠 1405/1505 = 93.4% | 「分母已拉齐」这句站不住 | 改 `43–100%`，并注明是"预测侧可映射比例" |
| **D10** | **docx 与 PDF 孪生件不同步** | `组员入门手册-20261104.docx`（mtime **21:16 今天**，仍在改） | 其 PDF 停在 **11/09**（35 处命中） | 发出去的 PDF 与 docx 不一致 | 内容定稿后统一重出；本报告 §1.2 的 PDF 条目以「重出前保留旧件」处理 |

---

## 四、建议的最小改动集合（按文件合并）

> 原则：**只动会改变结论的句子**，不重排、不改写历史。改完每个文件只需 1 次复核。

| 优先级 | 文件 | 处数 | 具体动作 |
|---|---|---|---|
| **P0** | `docs/team-handbook/part1-问题与方法.md` | **5** | L193 六向→ v2；L187 的 `0.3658/0.3563`→`0.4076/0.2961` + 分母 `459–1309`→`1469–1528`；L203 `97–100%`→`43–100%`；L185/L224 oPCA `0.1654`→`0.1506`；L225 同步 |
| **P0** | `docs/team-handbook/part2-口径陷阱与三场景.md` | **8** | L26–27、L93–98（含分母）、L151–154（两列）、L209（改指 mapv2）、L103（`1469–1528`）、L19–20（补"已作废"标注）、L74–79（B 列标"v1 映射"） |
| **P0** | `docs/team-handbook/part3-可复现与FAQ.md` | **1** | L73 `459–1309`→`1469–1528` |
| **P0** | `docs/team-handbook/part4-汇报说明小白版.md` | **1** | L161 补「原口径（已作废）」 |
| **P0** | `docs/reports/time-memory-benchmark-20261023.md` | **1** | L66 选型格改 scVI |
| **P0** | `deliverables/课题5-汇报-v5-20261111.pptx` | **1** | 重做 `chart1.xml` 的 oPCA 系列（4 值），并**补出 v5 的 PDF** |
| **P0** | `docs/execution/20261104-队友交接总纲.md` | **1** | L386 六向→ v2 |
| **P1** | `deliverables/课题5-组员汇报说明-小白版-20261110.docx` | **1** | para#67 补「原口径（已作废）」，然后重出 PDF |
| **P1** | `docs/execution/20261108-更正索引.md` | **1** | §二 里 `老师七条意见回应` 的「已按新值重出」改为事实（见 D2） |
| **P1** | `docs/reports/report-09-corrections-20261108.md` | **1** | L12/L79 的「修正后 0.3658/0.3563」补注「v2 映射后为 0.4076/0.2961」 |
| **P1** | `deliverables/PPT交接包/03_素材/修正对比.csv` + `数据源.xlsx` | **2** | 表头「原口径」→「原口径（已作废）」 |
| **P1** | `deliverables/课题5-PPT制作交接包-20261110.docx` | **1** | table7 列名「原口径（错）」→「原口径（已作废）」 |
| **P2** | `deliverables/课题5-组员入门手册-20261104.docx/.pdf` | **整章** | 第二章重写（把「丢样本」案例换成「物种词表查反」案例），重出 PDF。这是更正索引里挂了 3 天的待办 |
| **P2** | §1.2 表里的历史件（约 70 个文件） | **各 1** | 文件头插一行作废声明（模板见 §1.2） |

**合计**：必改 **12 个文件 / 24 处**（P0 7 个文件 18 处 + P1 5 个文件 6 处）；
再加 §1.2 表里 58 行历史件（含 PPT/PDF 分组，实际约 70 个文件）各 1 行标注。
**不需要动**：`③` 的 22 个文件（更正说明、判定实验、chart3、mainline-reframe 等）。

### 验收方法（改完跑一遍，0 命中即通过）

```powershell
cd D:\projects\course5-prep
python scripts\audit_consistency_scan.py
python scripts\_rawxml_scan.py
# 期望：下列 10 个文件不再出现在结果里
# part1/part2/part3/part4、time-memory、v5.pptx（chart1）、小白版.docx、交接总纲.md、更正索引、report-09
```

```powershell
# 只验 P0 四个 handbook + time-memory：
Select-String -Path docs\team-handbook\*.md -Pattern '0\.1269|0\.1640|0\.3658|0\.3563|0\.4147|0\.6500|0\.6510|459\s*[-–ー~至]\s*1309'
# 期望输出：只有 part1:195 / part2:74-79 / part2:156 / part4:156-157 这类【已标注作废】的对照行
```

---

## 五、待决（本报告不下结论）

1. **`saturn_convention_v2.json` 要不要删/改名？** 它已被明令"别混用"，却仍被 4 处引用。
   建议改名为 `saturn_convention_v2-DEPRECATED.json`，从根上断掉误引。
2. **scVI 鱼两向重跑** 是唯一还挂着的口径债（1499→1469）；`current-table` 已标"待重跑"，
   但 PPT 与手册没有这个标记，评审会被问。
3. **`part1:203` 的语义**：43.4% 是"预测侧可映射比例"，不是"评估覆盖率"——改数字时把口径词一起写准，
   否则下一轮还会被误读。
4. **镜像内 6 值**（`0.8618/0.7369/0.1795/0.1734/0.2675/0.5814`）按更正索引**保留 v1 不改**，
   只加口径标注：本报告未列入违规。

---

## 附：本报告用到的复核脚本

| 脚本 | 作用 | 结论 |
|---|---|---|
| `scripts/_opca_recheck2.py` | 从 `rerun-v2/confusion/coarse_*.json` 重算 oPCA 六向 macro-F1 + acc | **与 current-table 逐位一致**（0.6435/0.1506/0.6729/0.2816/0.2131/0.4186） |
| `scripts/_crossphylum_recheck.py` | 从混淆矩阵重算跨门 mf1 | `0.0235/0.0257/0.0241/0.0267`，acc 与存值吻合 |
| `scripts/_map_diff.py` | v1 vs v2 映射表逐行比对 | 38 行，**仅 1 行变更**（zebrafish `Orthers`） |
| `scripts/_chart_dump.py` | 导出 pptx 图表 series 实际数值 | 抓出 v5 `chart1` 的 oPCA 旧值 |