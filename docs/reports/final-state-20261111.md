# 终态汇总：课题5 / XenoTransfer 六条战线验收（2026-11-11）

> 本文件是**总账**。六条战线的结论、证据、复核命令都在这里；
> 逐项细节看各自的审计报告，数字引用一律以 `docs/reports/number-index-20261111.md` 为准。

## 目标

把「课程交付物」推到「可发表 + 可复现 + 设计合格」的终态：六条战线并行推进并逐条验收，
每条结论都必须能落到文件路径或命令回显上。

## 原理

这条项目走过一次**结论翻转**（SATURN 从「0.65 大胜」变成「0.4076 一个方向都不赢」），
根因是评测实现把真值查目标物种词表、预测查源物种词表——方向反了，制造两类静默丢弃。
翻转之后，唯一站得住的做法是：**每个数字都必须能从混淆矩阵重算出来**，否则不许进交付物。
所以六条战线的验收标准统一成一条：**能不能复算，能不能逐字指到文件**。

## 步骤与验收（六条战线）

### ① 设计战线 —— PASS

| 指标 | 目标 | 实测 | 判据出处 |
|---|---|---|---|
| 留白 | ≥25% | **44.4%–78.4%**（10 页全部） | `audit-design-v5-20261111.md` |
| 对齐误差 | ≤0.1" | **簇内极差最大 0.040"**，PAD 违例 0 | 同上 |
| 图优于字 | 定量信息在图里 | 第 4/5/7 页承载六向与「原/修正」对照，均为图表 | 同上 |
| 正文对比 | ≥4.5:1 | 无违例 | 同上 |

关键改动：`PAD=0.36` / `COL2=4.60` 全篇统一（18 处常量替换），第 7 页内文 0.30 偏移修正。
**坑**：体检脚本第一版自己报了 10/10 不达标，全是口径错（白底阈值把封面深蓝算成 1.6% 墨）。

复核：`.\.venv39\Scripts\python.exe scripts\check_design_v5.py`

### ② 统计战线 —— PASS（含一处无法复原的存值，已隔离）

- SATURN 六向权威值（v2 映射 + 约定 B，strict_cell）：`0.3522 / 0.2566 / 0.1282 / 0.1386 / 0.4076 / 0.2961`
- 分母：`1505 / 1528 / 1469 / 1528 / 1469 / 1505`（鱼向 1469 = 1543 − 74）
- 旧配对 Δ 用错分母 → 改为独立重抽样：人→鼠 −0.3161、鼠→人 −0.3330、人→鱼 −0.2732、
  鱼→人 −0.2904、鼠→鱼 −0.0172 **ns**、鱼→鼠 −0.1825
- 跨门 `macro_f1_union` 存值 0.0711/0.0732/0.0652/0.0802 **16 类口径全复现不出**，
  而 `acc` 与混淆矩阵 micro-F1 逐位相等 → 该字段标记不可引用，`_PROVENANCE.md` 落在数据旁

复核：`scripts/pairwise_audit_gate.py`、`scripts/trace_crossphylum_mf1.py`

### ③ 数据规模战线 —— PASS（估算，无实跑）

- 子集 4,606 vs DCS 全量 140,471 = **30.50×**（每物种 19.6–39.4×）
- 全量单 seed **¥180–320**，GPU（SATURN 5–6 h，¥154–185）占 85%+；oPCA 全量内存 **≈39 GB**（须 32c128g）
- 结论方向不翻转，但所有 CI 会变窄——不能拿子集 CI 说全量

复核：`docs/reports/audit-scale-20261111.md` §任务清单 10 项

### ④ 文档一致性战线 —— PASS

- 唯一权威索引：`docs/reports/number-index-20261111.md`
- 25 个历史留档 .md 已插统一作废声明（`scripts/stamp_historical_docs.py`，幂等）
- 五份 docx 表格收敛 v2 值（老师回应稿走「不改正文 + 附录 A 对照」）
- 更正索引两条「已按新值重出」的**不实声明**改写为实测状况
- pptx 图表缓存全仓扫描 9 命中，现行 v5 唯一命中在标注的对照序列

复核：`scripts/scan_pptx_chart_cache.py`、`scripts/scan_teacher_docx.py`

### ⑤ 复现战线 —— PASS

- 118 个脚本逐个判定 → 30 个进一键流程；**全量 30/30、退出码 0、278.5 s**
- 证据目录：`results/repro-20261111-215553/`（manifest.json + 30 个步骤 stdout.log，163 文件）
- 已知断点 10 条：`/Files`、`/data/work` 平台数据缺失 → oPCA/SAMap/scVI 三条臂**只能验证到混淆矩阵**

复核：`docs/reports/audit-repro-20261111.md`、`docs/execution/20261111-repro-manifest.md`

### ⑥ 发表战线 —— 路线已定，缺项已列

三条路线与缺项见 `docs/reports/audit-publish-20261111.md`：
workshop 短文（4–6 页）/ methods note（2–4 页）/ 完整 benchmark（10–14 页）。
必做三件：主表重建（含分母与 BH 校正）、in-sample 判定（CPU 臂先行）、正对照 + SATURN 上界。

## 实现：已修正的交付物

| 交付物 | 状态 |
|---|---|
| `deliverables/课题5-汇报-v5-20261111.pptx` / `.pdf` | 设计验收全 PASS，10 页 |
| `deliverables/课题5-老师七条意见回应-20261030.docx` / `.pdf` | 修订说明 + 附录 A 13 行对照，13 页 |
| `deliverables/课题5-总交接文档-20261028.docx` / `.pdf` | 表 2 两列换 v2 值，P67 倍数修正 |
| `deliverables/课题5-组员交接总纲-20261104.docx` / `.pdf` | 表 2 oPCA 四值 |
| `deliverables/课题5-组员入门手册-20261104.docx` / `.pdf` | T11 / T14 全表重算，T13 加口径注 |
| `deliverables/课题5-组员汇报说明-小白版-20261110.docx` / `.pdf` | 表 4 oPCA 四值 |
| `deliverables/场景化选型指南-v8-20261109.md` | 现行版；本轮再改 13 处（oPCA 四向 + SATURN 六向 + 倍数） |
| `deliverables/课题5-组员入门手册-20261104.docx` | 本轮改 10 处 + 定向 4 处（0.1654→0.1506、2.4→2.7 倍），表头标「原口径 · 错」 |
| `deliverables/课题5-老师七条意见回应-20261030.docx` | 三张旧口径表头补标「（旧口径，见附录 A）」 |
| `docs/execution/20261028-master-handoff.md` | 本轮改 20 处（含「修正后六向」错列、2.4→2.7 倍、1499→1469） |
| `deliverables/PPT交接包/02_逐页brief.md` + PPT制作交接包 docx | 300 倍 → 约 104 倍，0.4147 → 0.3522 |
| `results/bootstrap-20261030/_SUPERSEDED-saturn_convention_v2.md` | 命名撞车隔离（v2 指约定不指映射） |

## 验证（一次性复核全部战线）

```powershell
cd D:\projects\course5-prep
# 1. 设计
.\.venv39\Scripts\python.exe scripts\check_design_v5.py        # 期望 10/10 PASS
# 2. 复现（全量，约 280 s，期望 30/30、rc=0）
.\.venv39\Scripts\python.exe scripts\reproduce_all.py
# 3. 统计闸门
.\.venv39\Scripts\python.exe scripts\pairwise_audit_gate.py
# 4. 一致性
.\.venv39\Scripts\python.exe scripts\scan_pptx_chart_cache.py
.\.venv39\Scripts\python.exe scripts\stamp_historical_docs.py   # 期望 0 待插入（幂等）
# 5. 数字索引
Select-String -Path docs\reports\number-index-20261111.md -Pattern '0.3522'
```

## 坑（踩过且已写进各战线报告）

1. **体检脚本口径错会让人白改一版**：白底阈值 / 白底对比 / 全量网格对齐，三处全错。
2. **`pathlib.rglob` 在本仓直接抛**（junction / 权限目录），必须 `os.walk` + 剪枝。
3. **docx 的 `cell.text` 与 `paragraph.text` 是两套**：只改段落不改单元格，表格里旧值会留下。
4. **判据要看旧值在句子里的角色**：part4 的 `0.4147` 是对照表里的反例，不是现值，不该盖作废戳。
5. **python-pptx 读不到图表缓存**：正文改对、图里还是旧数，必须解 `chart*.xml` 的 `<c:v>`。

## 下一步（按性价比）

1. **P0-4 拉回 `/Files` 与 `/data/work`**：不做，三条臂永远只到混淆矩阵，说「全流程可复现」是假话
2. **P0-1 主表重建**（分母进表 + BH 校正 + 第二实现交叉）：5–7 天
3. **P0-2 CPU 臂 in-sample 判定**（18 细胞）：4–6 天
4. 全量重跑（¥180–320，GPU 85%）——用来说服审稿人「不是子集运气」
5. 发表路线二选一：先 methods note（2–4 页，缺项最少），再扩展成 benchmark

## 证据索引（每条结论对应一条命令）

| 结论 | 命令 | 期望回显 |
|---|---|---|
| v5 十页设计全达标 | `.venv39\Scripts\python.exe scripts\check_design_v5.py` | `全部达标: True`，留白 44.4–78.4%，对齐极差 ≤0.040" |
| v4 底数与 v4→v5 差异 | `python scripts\measure_v4_v5.py` | v4 每页低对比 2–6 处、字号层 4–8 → v5 全 0、3 层 |
| 每个数字有出处 | `python scripts\verify_numbers.py` | `28/28 PASS`（SATURN strict_cell 与 oPCA/scVI 混淆矩阵均重算） |
| 干净解释器 30/30 | `Python313\python.exe scripts\reproduce_all.py --out results\repro-clean2-20261111-2344` | `30/30、678.3s`，`[results/repro-clean2-20261111-2344/](results/repro-clean2-20261111-2344/)` |
| 一键入口可用 | `powershell -File scripts\reproduce_oneclick.ps1 -Fast` | 打印解释器/依赖/退出码 |
| 现行件无作废数字 | `python scripts\scan_all_stale.py` | CURRENT 仅剩叙述型引用，逐条在 `scan-current-context-20261111.md` |
| 历史件已加声明 | 同上（带 `--stamp`） | 27 个 HISTORY 文件顶部/末页有声明 |
| 环境清单可查 | `python scripts\env_manifest.py` | `docs\execution\env-manifest-20261111.md` |

### 复现依赖的坑（已修）

`requirements.txt` 原来只有 5 个包，干净解释器跑第一步就崩：
`ModuleNotFoundError: No module named 'h5py'` → 25/30。
补 `h5py==3.16.0` 与 `pandas==2.2.3` 后单次全量 30/30。
这条只能靠**换解释器真跑**才会暴露——在 `.venv39` 里跑永远是 30/30。
