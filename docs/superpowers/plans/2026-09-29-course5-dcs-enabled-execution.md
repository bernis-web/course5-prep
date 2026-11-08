# 课题5 DCS 已授权执行计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. 每批结束后必须停在规定审查点。

**Goal:** 用 DCS 补齐 SATURN v97g 的可追溯证据；本地完成 SAMap v98 合规实现后，再用 DCS 做一次低成本容器复现，为三方法统一比较和后续 inductive 实验建立可信起点。

**Architecture:** 采用“本地开发与审查 + DCS 可复现执行”。DCS 第一阶段只允许一个 provenance recovery 任务；SAMap 必须先本地通过条码、真值、排除和 18 份结果门，随后才允许一个 CPU 容器复现任务。SATURN 新训练和正式 inductive benchmark 仍属于后续阶段。

**Tech Stack:** Python 3.9、AnnData/Scanpy、SAMap 1.0.16、SATURN--22、DCS 离线任务、`unittest`、SHA-256、TSV/JSON/Markdown。

## Global Constraints

- 工作目录固定为 `D:\projects\course5-prep`。
- 本计划补充并局部覆盖 `docs\superpowers\plans\2026-09-29-course5-overall-flash-execution.md` 的 DCS 授权边界；原计划的科学口径、文件边界和审查点继续有效。
- 用户已授权使用 DCS，但仅覆盖本文列出的低成本任务；不得启动大规模 SATURN、全数据多 seed 或 GPU 正式训练。
- 当前工作区有大量用户和队友未提交改动；不得清理、回退、commit 或 push。
- 不读取、打印、复制或保存 token、cookie、密码或凭据文件。DCS 提交通过已登录页面完成，仓库只保存脱敏任务元数据。
- 不覆盖 `local_samap3.py`、`local_samap3_out.txt`、`local_samap3_emb.h5ad` 和现有六份预测 JSON；它们固定为 `legacy_noncompliant_20260928`。
- v97g 在任务号、命令、逐细胞结果、混淆矩阵和哈希齐备前，只能称为“候选正式 transductive 数字”。
- 当前 SATURN 和 SAMap 协议名为 `transductive_formal_reassessment`，不是 inductive，也不是 held-out benchmark。
- DCS 新任务必须自记录命令、脚本 SHA、输入 SHA、环境、协议标签、输出路径、输出 SHA 和退出码。

## 一、当前判断

1. 首要问题不是算力，而是证据链：v97g 的 `61.79%`、majority `48.17%`、coverage `0.9805` 尚不能由仓库内逐细胞产物独立复算。
2. 当前 SAMap 文件仍有重复 observation warning、`truth NA=3`、条码无物种前缀和仅 coarse 层逐细胞结果，因此“18/18 已合规完成”不能进入正式报告。
3. SAMap 现有规模约 4,606 细胞，本地主步骤约一分钟量级，优先本地修复；DCS 只做环境复现，不承担探索性调参。
4. DCS 的近期价值依次是：恢复 provenance、复现评分、验证容器；正式 SATURN inductive 训练排在这些门之后。

## 二、DCS 任务分级

| 编号 | 任务 | 当前授权 | 推荐资源 | 训练模型 | 目的 |
| --- | --- | --- | --- | --- | --- |
| DCS-P0 | 现有 v97g 任务只读定位 | 立即执行 | 无新增资源 | 否 | 找 task/subtask、日志和既有产物 |
| DCS-P1 | SATURN provenance recovery | 允许提交 1 次 | `1c 4g`，`resource_id=259` | 否 | 补命令、哈希、预测和混淆矩阵 |
| LOCAL-B | SAMap v98 本地实现与运行 | 立即执行 | 本机 CPU | 否 | 修复条码、真值、排除和产物结构 |
| DCS-P2 | SAMap v98 容器复现 | LOCAL-B 审查后 1 次 | 首选 `1c 4g` CPU | 否 | 验证环境可复现性 |
| DCS-F | SATURN inductive smoke/formal | 当前不执行 | 后续估算 | 是 | 建立正式泛化基准 |

## 三、Task 1：冻结本轮执行快照

**Files:** Create `docs\execution-snapshot-dcs-enabled-20260929.md`。

- [ ] 运行并原样记录：

```powershell
git status --short --branch
.\.venv39\Scripts\python.exe -m unittest discover -s tests -q
.\.venv39\Scripts\python.exe scripts\validate_eval_manifest.py
git diff --check
Get-FileHash local_samap3.py,local_samap3_out.txt,local_samap3_emb.h5ad -Algorithm SHA256
Get-FileHash config\heart-celltype-map-v1.tsv -Algorithm SHA256
```

- [ ] 快照写明：`DCS authorized for P0/P1 and reviewed P2 only`；同时写明 `SATURN inductive training not authorized in this batch`。
- [ ] 测试失败时记录真实输出，不得用旧的“91 tests 全绿”替代本轮结果。

## 四、Task 2：DCS-P0 只读定位 v97g

**Files:** Create `docs\dcs-v97g-readonly-locate-20260929.md`；找到后 create `results\pilot-v1\saturn-v97g\raw\task-metadata.json`。

- [ ] 在离线任务历史中按创建时间、任务名和 v97f/v97g 关键词定位候选任务。
- [ ] 每个候选只记录非敏感字段：batch/subtask ID、任务名、状态、镜像、资源、时间和费用。
- [ ] 核对共同指纹：Final AnnData SHA `20cf807fcaa5e8ed9ac65a28d50e781c82c9c48cdac9b7a1820dcf74bdf5143f`、`obsm["macrogenes"]`、`4606 x 1000`、`k=15`、`cosine`、固定 seed、coarse/fine 对 unmapped 双向排除。
- [ ] 只有指纹匹配才认定为 v97g；名称相似但指纹不符时写入候选排除表。
- [ ] 20 分钟内无法定位则记录 `BLOCKED_V97G_TASK_NOT_IDENTIFIED`，进入 DCS-P1，不反复浏览页面。

**Review gate A0:** Codex 核对任务是否可能被 v97f、v72 或 v95/v96 冒充。

## 五、Task 3：DCS-P1 provenance recovery

**Files:**
- Create `scripts\dcs_provenance_v99.py`
- Create `tests\test_dcs_provenance_v99.py`
- Create `docs\dcs-provenance-v99-submit-spec-20260929.md`
- Runtime output `/data/work/course5_v99/`
- Archive target `results\pilot-v1\saturn-v97g\raw\`

- [ ] 测试必须验证脚本只读白名单路径、只写 `/data/work/course5_v99/`、不删除或覆盖旧文件。
- [ ] 脚本启动时写入：UTC/北京时间、完整执行命令、脚本 SHA-256、Python 版本、`pip freeze`、可见环境、协议标签 `transductive_formal_reassessment`。
- [ ] 检查并哈希以下候选：
  - Final AnnData：`/data/work/saturn_out_real3_h/saturn_results/test256_data_human_saturn_input_hvg_mouse_saturn_input_hvg_zebrafish_saturn_input_hvg_org_human_seed_0.h5ad`
  - `prep_real_v60.py`、`eval_v72.py`
  - `g5-provenance-v95-command.txt`、`g5-provenance-v96-command.txt`
  - `dcs_provenance_v95.py`、`dcs_provenance_v96_readout.py`
  - `saturn-src/` 源码树
- [ ] 从 Final AnnData 读取 `obsm["macrogenes"]`，断言形状 `4606 x 1000`；不满足则非零退出并写实际形状。
- [ ] 用冻结 mapping 和统一评分器生成六方向乘三层的逐细胞预测、混淆矩阵、指标和角色表；不得只打印汇总数字。
- [ ] coarse/fine 对 reference 和 query 同时排除 `mapping_status != active`；exact 保留全部有效真值。
- [ ] 生成 `manifest.json`、`metrics.json`、`predictions/`、`confusion/`、`roles/`、`sha256.tsv`、`environment.txt` 和 `command.txt`。
- [ ] stdout 只打印小于 20 KB 的 compact summary；另生成纯文本单元的 `course5_v99_readout.ipynb`，作为 DCS 文件接口不能读取 JSON/TXT 时的备用载体。
- [ ] 本地验证：

```powershell
.\.venv39\Scripts\python.exe -m unittest tests.test_dcs_provenance_v99 -v
```

- [ ] 测试通过后，Flash 可提交 1 个任务：名称 `g5-provenance-v99-readout`，镜像 `SATURN--22`，资源 `1c 4g`。禁止改为高配资源，禁止加入训练命令。
- [ ] 提交后立即记录 batch/subtask ID 和预计费用。任务失败时只允许修复一次明确的路径或语法问题；第二次失败必须停止反馈。
- [ ] 完成后把可读出的原始文件原样归档到 `results\pilot-v1\saturn-v97g\raw\`，解释另写文档，不改写日志。

**Acceptance A1:** Final AnnData SHA 匹配冻结值；18 组产物齐全；human→mouse coarse 的 accuracy、majority、coverage 可复算；若不是 `61.79% / 48.17% / 0.9805`，以新产物为准并保留差异说明；关键输出均在 `sha256.tsv`；无凭据入库。

**Review gate A1:** Flash 停止并交付任务元数据、文件清单、SHA、验收输出和仍缺字段。Codex 通过前，v97g 保持候选。

## 六、Task 4：LOCAL-B SAMap v98 合规实现

**Files:**
- Create `scripts\run_samap_compliant_v98.py`
- Create `tests\test_run_samap_compliant_v98.py`
- Create runtime output `results\pilot-v1\samap-v98\`
- Preserve `local_samap3.py` and all legacy outputs

- [ ] 先写失败测试，覆盖：输入前物种前缀化、全局唯一、未知物种失败、NA 失败、mouse 排除 30、zebrafish 排除 44、reference/query 双向排除和 18 份输出完整性。
- [ ] 构造 `SAM`/`SAMAP` 前把 observation 名称改为 `hu|原条码`、`mo|原条码`、`zf|原条码`，随后断言全局唯一。
- [ ] 不调用 `obs_names_make_unique()` 掩盖碰撞；发现重复直接失败并保存重复清单。
- [ ] exact、coarse、fine 使用同一冻结 mapping 快照和评分器；逐细胞文件包含 `prefixed_barcode`、方向、层级、truth、prediction、included、exclusion_reason。
- [ ] 使用固定 seed、`k=15`、`cosine` 和 200 次置换；不得预设结果必须等于或低于 majority。
- [ ] 执行：

```powershell
.\.venv39\Scripts\python.exe -m unittest tests.test_run_samap_compliant_v98 -v
.\.venv39\Scripts\python.exe -m unittest discover -s tests -q
.\.venv39\Scripts\python.exe scripts\run_samap_compliant_v98.py
```

- [ ] 验收摘要报告：细胞数、唯一 observation 数、truth NA、三种前缀计数、18 份 predictions/confusion/metrics/permutation 是否齐全、每层 excluded 数和全部 SHA。

**Acceptance B1:** 无 duplicate warning；truth NA 为 0；18 份结果一一对应；exact 无错误排除；coarse/fine 排除符合冻结 mapping；指标可从逐细胞文件复算。

**Review gate B1:** Codex 审查代码和本地产物。通过前不得提交 DCS-P2，不得更新正式报告数字。

## 七、Task 5：DCS-P2 SAMap v98 容器复现

**Files:**
- Create `docs\dcs-samap-v98-reproduction-20260929.md`
- Runtime output `/data/work/course5_samap_v98/`
- Local comparison `results\pilot-v1\samap-v98-dcs\`

- [ ] 仅使用 Codex 已通过的 `run_samap_compliant_v98.py`、冻结输入 SHA、mapping SHA 和本地产物索引。
- [ ] 任务开头记录 `samap==1.0.16`、`sam-algorithm==1.0.2`、AnnData、Scanpy、NumPy、Pandas、scikit-learn 版本和安装来源。
- [ ] 首选 `1c 4g` CPU；只有日志明确证明内存不足时才允许提高内存，不能因速度慢直接使用 GPU。
- [ ] 只复现冻结参数，不做参数搜索。
- [ ] 产物结构与本地 `results\pilot-v1\samap-v98\` 一致，并生成 local-vs-DCS 比较表：输入 SHA、环境、细胞数、18 个 accuracy、macro-F1、coverage、excluded 和输出 SHA。
- [ ] 浮点文件 SHA 不要求完全一致，但指标差异必须小于比较脚本预注册的容差；超出时标记 `environment_divergence`，不得挑较好一侧进报告。

**Review gate B2:** Codex 抽查至少三个方向和三个层级，并复算逐细胞指标。通过后 SAMap 才能进入统一方法比较矩阵。

## 八、Task 6：人工 mapping 签认

**Files:** Use `docs\reviewer-signoff-request-mapping-v1.md`；收到回复后 create `docs\reviewer-signoff-mapping-v1-20260929.md`。

- [ ] 发给导师或组内 reviewer；签认对象必须是 SHA-256 `be9857354778535b76d1884d004c54691dc5ff2daa7b098d71dc719daf583165` 对应的 v1 mapping。
- [ ] 保存 reviewer 身份、日期、结论和四个低置信映射意见；不得由 Codex 或 Flash 代签。
- [ ] 若要求修改，保留 v1，新增 v2，并对 SATURN、SAMap、ortholog-PCA 全部重新评分。

## 九、Task 7：统一比较与报告冻结

**Files:**
- Create `results\pilot-v1\method-comparison.tsv`
- Create `results\pilot-v1\method-comparison.json`
- Create `docs\method-comparison-interpretation-20260929.md`
- Later create `docs\report-methods-draft.md`、`docs\report-results-draft.md`、`docs\report-limitations-draft.md`

- [ ] 只有 A1、B2 和人工签认门通过后，才把 SATURN v97g、SAMap v98、ortholog-PCA 放入同一正式矩阵。
- [ ] v72 的 67.4% 只作历史 in-sample exploratory 对照；legacy SAMap 只作实现审计，不进入正式排名。
- [ ] 每行报告 accuracy、macro-F1、weighted-F1、majority、shuffle p、coverage、excluded reference/query、证据等级和协议标签。
- [ ] 先冻结 Markdown；数字和图表自动比对后才生成 Word，并保留 Word/WPS 视觉检查。

## 十、后续 inductive 实验启动门

正式 SATURN 新训练只有满足以下条件才进入 DCS-F：

- v97g provenance 已恢复或明确降级；
- SAMap v98 本地与 DCS 复现通过；
- mapping 已有人类签认；
- 三方法统一评分器冻结；
- 明确 leave-one-species-out 或 reference/query 分离；
- 先做 1 seed 降采样 smoke，再决定至少 3 seeds 正式运行；
- scRNA 结论稳定后才做少量 snRNA；空间组学不进入当前主榜。

算力主要消耗在 SATURN 的蛋白/基因嵌入准备、模型训练、多 seed 和多个留出协议，不在当前评分与 SAMap 小规模复现。因此现在使用高配 GPU 不会解决主要阻塞。

## 十一、Flash 第一批执行范围

Flash 现在按顺序执行：

1. Task 1：生成本轮快照。
2. Task 2：只读定位 v97g，最多 20 分钟。
3. Task 3：实现并测试 v99；若 v97g 已有完整逐细胞证据，可缩减为缺失字段恢复任务。
4. 提交一次 `g5-provenance-v99-readout`，资源固定 `1c 4g`，完成后停止反馈。
5. 等待 DCS-P1 时并行完成 Task 4 的测试和本地实现；三物种运行完成后停止反馈。

第一批不得执行：DCS-P2、SATURN 新训练、mapping 修改、最终 Word、commit、push、清理工作区。

## 十二、Flash 反馈格式

```text
【执行范围】完成的 Task 编号；跳过项和原因。
【DCS-P0】候选任务、排除理由、最终 task/subtask ID 或 blocked 代码。
【DCS-P1】任务元数据、资源、费用、退出码、产物目录和关键 SHA。
【v97g 复算】六方向三层是否齐全；h→m coarse 三个数字；与旧值差异。
【SAMap v98】前缀发生位置、唯一性、truth NA、排除计数、18 份产物完整性。
【验证】本轮测试命令和原始通过/失败数量；manifest；diff check。
【阻塞】只列需要用户、导师或 DCS 平台处理的问题。
【明确未做】DCS-P2、SATURN 训练、commit、push、最终报告。
```

## 十三、Codex 审查顺序

1. 先审 DCS-P1 是否真的是只读/重评估而非训练，以及证据是否来自正确 Final AnnData。
2. 再审 SAMap v98 的代码门和本地产物，不接受仅凭汇总日志的“18/18”。
3. 两者通过后才批准 DCS-P2。
4. DCS-P2 与本地一致后，审 mapping 签认和统一方法矩阵。
5. 最后才进入 Word 报告和 inductive 新实验计划。

## 十四、完成定义

本阶段只有在以下全部满足时才可称为完成：

- v97g 可由保存的逐细胞产物复算，或明确降级为仅汇总可回溯；
- SAMap v98 本地合规并通过 DCS 容器复现；
- mapping v1 获人类 reviewer 签认；
- SATURN、SAMap、ortholog-PCA 统一比较矩阵冻结；
- 所有正式数字可从机器可读产物重算；
- 测试、manifest validator 和 diff check 有本轮证据；
- 报告清楚区分正式、历史和探索性结果；
- 没有无法解释的 NA、重复条码或协议升级。
