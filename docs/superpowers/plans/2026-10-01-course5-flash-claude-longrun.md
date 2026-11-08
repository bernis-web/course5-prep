# 课题5 Flash-Claude 长任务执行计划

> Flash/zcode 执行重活，Claude 做每阶段的中间审阅；Codex 暂停，用户回来后再最终复核。模型口头汇报不等于证据。

**日期：**2026-10-01  
**项目：**`D:\projects\course5-prep`  
**目标：**完成 v99 证据闭环、ortholog-PCA 统一复算、SAMap v98 修复验证，并形成可用于老师汇报的证据包、Word 报告和修订版 PPT。

## 全局边界

1. 不删除、覆盖或回退已有结果；新结果写入新目录/新版本。
2. 不保存 token、cookie、密码或 DCS 凭据；不把真实凭据写入代码/日志。
3. 不 `git add .`、不 commit/push，除非用户另行明确授权。
4. 不把“容器中存在”写成“本地已回收”，不把日志级数字写成文件级证据。
5. 每次运行先冻结 transductive/inductive、query/reference、标签空间、分母、coverage、seed、置换定义。
6. 未经用户批准，不启动 inductive、空间/单核扩展、扩大物种或高价 GPU。
7. DCS 任务只允许一次性提交和一次性结果检查；结束任务不得无限轮询或自动重试。
8. 出现 502、OOM/137、SHA 不匹配、JSON 解析失败、协议漂移或数字来源不唯一，立即停止并汇报。

## 当前起点

- SATURN v97g 六方向是 transductive/in-sample formal reassessment candidate，不能称 held-out/inductive benchmark。
- v99 仅有容器级 46 文件存在证据；本地 18 predictions + 18 confusion 尚未完整回收，文件级 provenance pending/blocked。
- `scripts/ortholog_pca_local_v1.py` 语法通过，但需修复变量、mapping 键、归一化协议、共享 ortholog 硬停止和完整输出。
- `scripts/run_samap_compliant_v98_dcs.py` 语法通过，但主流程尚未证明接入物种前缀和 `truth_na=0` 失败门；SAMap v98 暂不提交。

## 阶段计划

### Phase 0：状态冻结

读取：`docs/course5-longrun-state-20260930.md`、`docs/v99-score-reconciliation-20261001.md`、`docs/wave3-ortholog-pca-manifest-20260930.md`、`docs/wave0-evidence-matrix-20260930.md`、`docs/transductive-formal-v74-evidence-20260928.md`。

运行：

```powershell
Set-Location D:\projects\course5-prep
git status --short --branch
python -m unittest discover -s tests -v
```

写 `docs/flash-phase0-snapshot-20261001.md`，只记录状态、测试退出码和不触碰的旧结果，然后停止。

**Claude Gate 0：**核对状态表、证据等级和禁止事项；数字来源不唯一则停止。

### Phase 1：v99 文件级 provenance

优先从 `/data/work/course5_v99/` 回收 `manifest.json`、`metrics.json`、`sha256.tsv`、`command.txt`、`environment.txt`、`v99_mapping_embedded.json`，再回收 18 predictions 与 18 confusion。写入新目录 `results/pilot-v1/saturn-v99/raw/recovered-20261001/`，不得覆盖旧日志。

按 `sha256.tsv` 重算全部哈希，抽查 human→mouse coarse 的 prediction、confusion、metrics 三者。缺文件、502、解析失败或 SHA 不一致时停止，不重跑训练。

**Claude Gate 1：**只读核对本地清单、哈希、协议标签和抽查。全绿才可把 provenance 标文件级 confirmed。

### Phase 2：修复 ortholog-PCA

目标：`scripts/ortholog_pca_local_v1.py`；同步修订 `docs/wave3-ortholog-pca-manifest-20260930.md`，不得写入未运行验证的数字。

必须完成：保存 `X`、`var_set`、`var_idx`；在共享 ortholog 上明确 source/query、target/reference 和 PCA；mapping 仅使用冻结表的 `species|cell_type` 字符串键；删除/定义所有未定义变量；让实现与 manifest 使用同一归一化协议；共享 ortholog <1000 时非零退出；`--smoke` 只写 `results/pilot-v1/ortholog-pca-smoke/`；正式模式落盘 manifest、environment、metrics、18 predictions、18 confusion、command、输入/输出 SHA。

静态检查：`.venv39\Scripts\python.exe -m py_compile scripts/ortholog_pca_local_v1.py`。

**Claude Gate 2：**检查标签泄漏、角色、mapping、归一化和硬停止；未通过不得跑 full PCA。

### Phase 3：PCA smoke

Gate 2 通过后运行：

```powershell
Set-Location D:\projects\course5-prep
.venv39\Scripts\python.exe scripts/ortholog_pca_local_v1.py --smoke
```

记录退出码、共享 ortholog、细胞数、prediction/confusion 数、coverage、majority、shuffle_p、输出 SHA 和峰值内存（若可测）。smoke 数字不得进主表。

**Claude Gate 3：**从实际文件核对可解析、无 NaN/重复 barcode、coverage 可重算、置换定义一致、失败门真实生效。

### Phase 4：PCA 全量本地复算

六方向 × exact/coarse/fine，固定 mapping v1、seed=0、K=15、cosine、倒距离加权和 200 次置换。18 predictions、18 confusion、metrics、manifest、environment、command、SHA 必须齐全。结果先标 candidate，逐项解释草表差异。

**Claude Gate 4：**审阅全量结果、方向性、seed/ceiling 对照和讲稿“4/6”口径。

### Phase 5：SAMap v98 本地修复门

目标 `scripts/run_samap_compliant_v98_dcs.py`，此阶段不提交 DCS：

1. 每个物种通过 `load_species()` 应用 `hu|`、`mo|`、`zf|`；
2. 合并前执行 `assert_prefix_unique()`；
3. 每个 truth 列执行 `assert_no_na_truth()`，失败非零退出；
4. 写 command、environment、manifest、metrics、predictions/confusion、全量 SHA；
5. 固定 `sm.run(NUMITERS=3, ncpus=1, umap=False)`。

用 unittest 新增重复 barcode、缺 truth、truth_na>0 失败门测试；pytest 不可用时不安装依赖。

**Claude Gate 5：**检查主流程调用链，不只看辅助函数。

### Phase 6：一次性 SAMap DCS（需用户批准）

仅在 Gate 5 通过且用户明确批准后提交；资源固定 1c4g、`ncpus=1`、`umap=False`，只提交一次。RC=137/OOM、导入错误、truth_na>0、重复 barcode、输出缺失、SHA 不匹配或 502 均立即停止；结束后只读一次状态和一次结果，不自动重试。

**Claude Gate 6：**审阅 DCS 日志、manifest、输出和停止原因；失败不得自行扩大资源或重提交。

### Phase 7：mapping reviewer

使用 `docs/reviewer-signoff-request-mapping-v1.md`，请导师/组内 reviewer 确认 4 个低置信映射和整表。修改另存新版本及 SHA；未签认时保持 `needs-reviewer`，不得宣称正式 benchmark。

### Phase 8：最终证据包、Word 与 PPT

数值冻结后解释论文方法和本方法的输入、同源基因/蛋白、macrogene/embedding、训练/评估、标签空间、分母、coverage、majority、置换、query/reference 与适用边界。明确当前结果只能支持方法学探索或 transductive reassessment，不能推出 inductive 泛化或工具普遍优劣；纳入 OOM、无稳定 SAMap 信号、seed 双峰、v99/v97g 口径差异。

交付：`docs/final-evidence-matrix-*.md`、Word 报告、按原格式修订 PPT、AI 使用日志。每个数字必须回到证据矩阵，不能手工改数字。

**Claude Gate 7：**逐页检查数字、协议、证据等级、局限性和“论文方法 vs 我们方法”；用户回来后由 Codex 最终复核。

## 暂不启动的扩展

inductive 留一物种、单核补充、更多物种、空间组学和大规模 GPU 训练必须另开 manifest，待 Phase 1–8 完成、mapping 人工签认、预算和方案获用户批准后再启动。

## Flash 每轮汇报模板

```text
本轮阶段：Phase X / Gate X
Claude 审阅：通过/不通过；逐条意见：
修改文件：
实际执行命令：
退出码：
本地测试：
输出文件及数量：
SHA-256：
关键数字及完整协议口径：
是否提交 DCS：是/否；任务 ID：
失败或阻塞：
下一阶段请求：
```

## 给 Flash 的第一条指令

```text
你负责执行 D:\projects\course5-prep 的课题5长任务，Codex 暂时停用。先阅读：
docs/superpowers/plans/2026-10-01-course5-flash-claude-longrun.md
docs/course5-longrun-state-20260930.md
docs/v99-score-reconciliation-20261001.md
docs/wave3-ortholog-pca-manifest-20260930.md

本轮只做 Phase 0：只读冻结状态、运行现有 unittest、记录 git status，写 docs/flash-phase0-snapshot-20261001.md，然后停止。
每个后续阶段开始前和结束后都必须让 Claude 做只读审阅；Claude 未通过不得越过阶段门。不得把口头汇报当证据，必须回传文件路径、命令、退出码、测试、输出数量和 SHA。不得删除/覆盖旧结果，不得 commit/push，不得启动未经批准的 DCS 或 inductive 任务，不得对结束任务循环轮询。遇到 502、OOM/137、SHA 不匹配、协议不一致、数字来源不唯一或需要用户决定的科学问题，立即停止并汇报。
```