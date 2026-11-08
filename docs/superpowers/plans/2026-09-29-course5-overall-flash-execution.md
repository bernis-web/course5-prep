# 课题5总体执行计划：Flash 实施，Codex 分阶段审查

> 日期：2026-09-29
>
> 适用对象：Flash / GLM-5.3-flash 执行者、Codex 审查者、课题组成员
>
> 当前授权边界：只允许本地仓库工作和读取既有 DCS 任务证据；不得新建、重跑、取消或修改 DCS 任务；不得 commit、push、清理或回退现有工作区。

## 一、先给结论

本轮总体方向不变：先把三物种单细胞整合的评测协议和证据链做扎实，再决定是否投入 DCS 大规模计算。

但上一轮反馈中的两项状态必须拆开处理：

1. SATURN v97g 的 61.79% 已写入证据文档，计算规则看起来符合“unmapped 从训练与分母双向排除”的冻结规则；但仓库中尚无独立的任务编号、原始命令、原始日志、逐细胞预测、混淆矩阵和 SHA 清单。因此它目前是“候选正式 transductive 数字”，不是完整归档完成。
2. “SAMap 合规重跑 18/18 完成”与现有产物冲突。当前 local_samap3_out.txt 仍出现 3 次重复 observation warning 和 truth NA=3；六份预测 JSON 的条码没有物种前缀，且只落了 coarse 层逐细胞结果。当前 SAMap 产物只能标记为 legacy_noncompliant_20260928，实现对照，不得进入正式结果列。

因此下一步不是直接写最终报告，而是先完成两个修复门：恢复 v97g 的可回溯证据；真正完成 SAMap v98 合规重跑。

## 二、全局原则

- 只在 D:\projects\course5-prep 内工作。
- 开始前和每个审查点都记录 git status；不处理与本计划无关的修改。
- 不覆盖 local_samap3.py、local_samap3_out.txt、local_samap3_emb.h5ad 和现有六份预测 JSON；它们作为 legacy 证据保留。
- 不把 v71、v72、v97f、v97g、SAMap legacy 和 SAMap v98 混写为同一个运行。
- 所有新结果必须包含：协议标签、命令、输入哈希、输出哈希、软件版本、随机种子、逐细胞结果、混淆矩阵、coverage 和 excluded 数量。
- exact 层保留全部有真值的细胞；coarse 和 fine 层统一按冻结 mapping 中 mapping_status=active 进入训练和分母。mouse 排除 30、zebrafish 排除 44，总计 74 个；排除必须对 reference 和 query 双向生效。
- 条码必须在进入算法前完成物种命名空间化：human 使用 hu|，mouse 使用 mo|，zebrafish 使用 zf|。不得依赖 AnnData 自动追加 -1 来消歧。
- 结果只能按实际协议命名。现阶段 SATURN 与 SAMap 都是 transductive formal reassessment，不是 inductive，不是 held-out benchmark。
- 任何未找到的 DCS 证据都写为 pending 或 blocked，不允许凭记忆补值。
- 每个阶段完成后必须停下，由 Codex 复审；未收到“通过”不得进入下一阶段。

## 三、总路线图

| 阶段 | 执行者 | 目标 | 是否使用 DCS | Codex 硬停点 |
| --- | --- | --- | --- | --- |
| 0 | Flash | 冻结当前状态和纠正错误状态标签 | 否 | 审查快照和文档纠偏 |
| A | Flash | 恢复 v97g 既有任务的证据链 | 只读既有任务 | 审查任务来源、原始文件和哈希 |
| B | Flash | 实现并运行 SAMap v98 合规流程 | 否，优先本地 | 审查代码、条码、排除规则和 18 份结果 |
| C | 用户或导师 | 完成 mapping v1 人工签认 | 否 | 审查签认对象和 SHA |
| D | Flash | 生成统一方法对比矩阵和统计摘要 | 否 | 审查同口径比较和结论边界 |
| E | Flash | 冻结报告素材、证据索引和组员交接 | 否 | 审查后才生成 Word |
| F | 另行批准后执行 | 设计并运行 inductive 新实验 | 需要新 DCS 任务 | 用户批准和预算门 |

## 四、阶段 0：证据快照与状态纠偏

### 0.1 建立只读基线

Flash 先运行并记录：

    git status --short --branch
    .\.venv39\Scripts\python.exe -m unittest discover -s tests -q
    .\.venv39\Scripts\python.exe scripts\validate_eval_manifest.py
    git diff --check

把输出摘要写入 docs\execution-snapshot-20260929.md，至少包含：

- 分支及 ahead 状态；
- 已修改和未跟踪文件清单；
- 测试数量与结果；
- manifest 的 valid、evidence_status、ready_for_confirmation 和 blocking_items；
- mapping v1 SHA-256；
- 当前 local_samap3.py、local_samap3_out.txt、local_samap3_emb.h5ad 的 SHA-256。

不得把虚拟环境、H5AD 二进制或临时浏览器目录加入 Git。

### 0.2 纠正 SAMap 状态标签

只做最小文档修正，不删除历史文字：

- 在 docs\transductive-formal-v74-evidence-20260928.md 的 SAMap 段落前增加“2026-09-29 Codex 复审纠偏”。
- 将当前六方向结果标记为 legacy_noncompliant_20260928。
- 明确三项缺陷：算法输入前未全局前缀化、truth NA=3、只保存 coarse 层逐细胞预测。
- 在 docs\handoff-v74-20260928.md 中把“实证闭环”改成“SATURN 候选数字已形成，证据归档与 SAMap 合规重跑待完成”。
- 不改旧数值本身；只改变证据等级和可引用范围。

### 阶段 0 交付物

- docs\execution-snapshot-20260929.md
- 两份文档中的纠偏说明
- 无代码逻辑变化

### Codex 审查点 0

必须同时满足：

- 现有 legacy 文件未被覆盖；
- 测试仍全绿；
- git diff --check 通过；
- 文档不再宣称 SAMap 合规完成；
- 没有 commit、push 或 DCS 写操作。

通过后才进入阶段 A 和 B。阶段 A、B 可以并行准备，但各自必须独立停审。

## 五、阶段 A：恢复 v97g 既有任务证据

### A1 只定位既有任务

目标是找到产生 v97g 规则合规数字的既有 DCS 任务或子任务。只读取，不创建新任务。

优先寻找：

- 任务名称、task ID、subtask ID；
- 提交时间、完成时间、镜像名称、资源规格；
- 原始命令或执行入口；
- 实际脚本内容；
- stdout、stderr 或平台完整日志；
- 输入 Final AnnData 路径与 SHA-256；
- 输出指标、逐细胞预测、混淆矩阵或日志中的机器可读 JSON。

若页面或接口无法访问，不反复尝试，不新建取证任务。记录：

    BLOCKED_EXISTING_DCS_EVIDENCE_NOT_ACCESSIBLE

并写清尝试入口、时间和缺失字段。

### A2 建立不可改写的证据目录

建议创建：

- results\pilot-v1\saturn-v97g\raw\task-metadata.json
- results\pilot-v1\saturn-v97g\raw\command.txt
- results\pilot-v1\saturn-v97g\raw\stdout.log
- results\pilot-v1\saturn-v97g\raw\stderr.log
- results\pilot-v1\saturn-v97g\raw\scripts\
- results\pilot-v1\saturn-v97g\predictions\
- results\pilot-v1\saturn-v97g\confusion\
- results\pilot-v1\saturn-v97g\metrics.json
- results\pilot-v1\saturn-v97g\sha256.tsv
- docs\saturn-v97g-evidence-20260929.md

原始日志原样保存；解释和结论只写在 docs 文档中。

### A3 v97g 验收条件

只有满足以下条件，v97g 才能从“候选正式数字”升级为“正式 transductive 重评估”：

- task ID 和 subtask ID 可回溯；
- 原始命令或等价自足脚本可回溯；
- Final AnnData SHA 与 20cf807fcaa5e8ed9ac65a28d50e781c82c9c48cdac9b7a1820dcf74bdf5143f 一致；
- 表示层明确为 obsm/macrogenes，维度为 4606 × 1000；
- k=15、cosine、置换次数和 seed 可回溯；
- coarse/fine 对 74 个 unmapped 的 reference/query 双向排除可由逐细胞文件或代码验证；
- h→m coarse 61.79%、majority 48.17%、coverage 0.9805 可从原始结果独立重算；
- 六方向 × 三层均有机器可读结果；
- 所有新增证据有 SHA-256 清单。

如果只有日志中的汇总数字，没有逐细胞结果或混淆矩阵，则状态写为：

    transductive_summary_recovered_but_not_fully_recomputable

不得写“完整归档完成”。

### Codex 审查点 A

Flash 完成 A1-A3 后必须停下，只提交文件清单和审计摘要给 Codex。Codex 将检查：

- 证据是否确实来自 v97g，而不是 v97f、v72 或其他任务；
- 日志和脚本是否原样保存；
- SHA 清单是否覆盖全部关键文件；
- 数字能否从逐细胞产物复算；
- 是否错误填充 v73 manifest 的原始 v71/v72 字段。

## 六、阶段 B：SAMap v98 真正合规重跑

### B1 先写失败测试

新增：

- tests\test_run_samap_compliant_v98.py
- 必要时扩展 tests\test_build_transductive_bundles.py
- 必要时扩展 tests\test_run_transductive_formal_v74.py

测试至少覆盖：

1. 三个物种相同原始条码经前缀化后全局唯一。
2. 输入 AnnData 在进入 SAM 和 SAMAP 对象前 obs_names 已带 hu|、mo|、zf|。
3. 未前缀化、重复条码、空条码或未知物种立即失败。
4. 联合 embedding 的 observation 名称全局唯一。
5. truth 不允许 NA；若标签回填失败必须报错，不能继续评分。
6. exact 层保留全部有效真值细胞。
7. coarse/fine 层按 mapping_status=active 对 reference 和 query 双向排除。
8. mouse 排除 30、zebrafish 排除 44；数量不符立即失败。
9. 六方向 × 三层必须产生 18 份逐细胞结果和 18 份混淆矩阵。
10. 每份逐细胞结果包含 prefixed_barcode、source_species、target_species、level、truth、prediction、included、exclusion_reason。
11. 运行记录包含 seed、包版本、命令、输入输出 SHA 和协议标签。
12. 置换检验使用同一实现和同一 seed，不允许根据结果临时更改算法。

先运行新增测试并保存预期失败证据，再实现。

### B2 新增独立运行器，不覆盖 legacy

新增 scripts\run_samap_compliant_v98.py。

输入：

- local_human_s.h5ad
- local_mouse_s.h5ad
- local_zebrafish_s.h5ad
- config\heart-celltype-map-v1.tsv
- 输出目录 results\pilot-v1\samap-v98
- 显式 seed

核心顺序必须是：

1. 读取单物种 AnnData。
2. 保存原始条码到 obs 中的 source_barcode。
3. 根据物种生成 prefixed_barcode。
4. 在创建 SAM 对象之前把 obs_names 替换为 prefixed_barcode。
5. 断言每个对象内部唯一、三物种合并后全局唯一、无空值。
6. 运行 SAM/SAMAP。
7. 导出联合 embedding，推荐键名 X_samap_pca。
8. 用 prefixed_barcode 从冻结输入回填 species 和 exact truth；断言 NA=0。
9. 保存 results\pilot-v1\samap-v98\samap-v98-embedding.h5ad。
10. 生成环境、命令和哈希记录。

禁止调用 obs_names_make_unique 作为修复手段；发现重复应在前缀化前查明来源并失败。

### B3 复用统一评估器

不要在 SAMap 脚本里复制一套新的 KNN 评分逻辑。优先复用：

- scripts\build_transductive_bundles.py 的条码、mapping 和方向 bundle 逻辑；
- scripts\evaluate_cross_species_transfer.py 的 KNN15 cosine、F1 和混淆矩阵逻辑；
- scripts\run_transductive_formal_v74.py 的六方向 × 三层调度逻辑。

为支持 SAMap 表示，允许做最小泛化：

- build_transductive_bundles.py 接受可配置的 obsm key 和期望维度；
- run_transductive_formal_v74.py 接受 representation 字符串，不再硬编码 obsm/macrogenes；
- 对 SATURN 的现有默认值和测试结果必须完全不变；
- SAMap 调用时 representation 写为 obsm/X_samap_pca，维度以实际导出为准并写入 manifest。

如果泛化会影响 SATURN 旧结果，停止并为 SAMap 新建薄包装器，不修改既有 SATURN 输出。

### B4 统一输出结构

results\pilot-v1\samap-v98 至少包含：

- run-manifest.json
- command.txt
- environment.json
- input-sha256.tsv
- output-sha256.tsv
- samap-v98-embedding.h5ad
- bundles\18 个 NPZ
- roles\6 个方向角色表
- mappings\方向和层级映射快照
- predictions\18 个逐细胞 TSV 或 JSON
- confusion\18 个混淆矩阵 JSON
- metrics\18 个指标 JSON
- result-index.json
- permutation\18 个置换摘要

result-index.json 必须明确：

- protocol=transductive_formal_reassessment
- not_inductive=true
- not_held_out_benchmark=true
- mapping_file_sha256
- embedding_sha256
- seed
- k=15
- metric=cosine
- n_permutations=200

### B5 置换检验

沿用已冻结定义：对每个方向和层级，reference 标签固定，用训练好的预测向量与 query 真值配对计算 observed accuracy；对 query 预测向量做 200 次固定 seed 洗牌，计算单侧经验 p 值 P(null_acc >= observed_acc)。

不得预设“18/18 无信号”。运行完成后按实际结果报告：

- observed accuracy；
- majority baseline；
- macro-F1 和 weighted-F1；
- shuffle p；
- coverage；
- excluded reference/query 数量。

如果结果与 legacy 数字不同，优先解释协议和条码修复差异，不回写 legacy 文件。

### B6 本地验证命令

Flash 完成实现后运行：

    .\.venv39\Scripts\python.exe -m unittest discover -s tests -q
    .\.venv39\Scripts\python.exe scripts\validate_eval_manifest.py
    git diff --check

再运行一个专门的验收脚本或测试，输出：

- embedding 细胞数；
- observation 是否唯一；
- truth NA 数；
- 三物种前缀数量；
- 18 份 predictions、18 份 confusion、18 份 metrics 是否齐全；
- 每层每物种 included/excluded 计数；
- 全部关键文件 SHA-256。

### Codex 审查点 B

Flash 到此必须停下，不得自行把结果写进最终报告。Codex 将复审：

- 前缀是否发生在算法输入前；
- 是否完全消除 duplicate warning 和 NA；
- 74 个 unmapped 是否在 coarse/fine 的训练和分母双向排除；
- exact 是否没有错误排除；
- 18 份逐细胞结果、混淆矩阵、指标和置换摘要是否一一对应；
- SATURN 旧测试是否保持通过；
- 数字是否由产物可复算；
- 文档是否如实写结果，而不是延续旧结论。

通过前 SAMap 状态固定为 not_ready_for_report。

## 七、阶段 C：mapping v1 人工签认

使用现有 docs\reviewer-signoff-request-mapping-v1.md 发给导师或组内 reviewer。

签认对象必须是当前冻结 mapping 文件，SHA-256 为：

    be9857354778535b76d1884d004c54691dc5ff2daa7b098d71dc719daf583165

签认记录至少包含：

- reviewer 姓名或可识别身份；
- 日期；
- 结论：确认、确认但有备注、要求修改；
- 被签认文件路径和 SHA-256；
- 对四个低置信映射的逐项意见。

不要通过修改 mapping 文件来加入签名。签名应保存在独立的 reviewer-signoff 文档或截图/导出记录中。

如果 reviewer 要求修改映射：

1. 保留 v1 不变；
2. 新建 mapping v2；
3. 记录 v1→v2 的逐行差异和理由；
4. SATURN v97g、SAMap v98、ortholog-PCA 全部用 v2 重新评分；
5. 旧结果降为 v1 历史结果。

### Codex 审查点 C

Codex 只确认签认是否真实对应冻结 SHA，不替代人类 reviewer 签名。未收到签认时 reviewer 字段保持 pending。

## 八、阶段 D：统一方法比较矩阵

阶段 A、B、C 通过后，建立：

- results\pilot-v1\method-comparison.tsv
- results\pilot-v1\method-comparison.json
- docs\method-comparison-interpretation-20260929.md

每一行至少包括：

- method
- run_id
- evidence_grade
- protocol
- representation
- source_species
- target_species
- label_level
- n_reference_total
- n_reference_included
- n_query_total
- n_query_included
- n_excluded_reference
- n_excluded_query
- coverage_query
- accuracy
- macro_f1
- weighted_f1
- majority_accuracy
- shuffle_p
- seed
- mapping_sha256
- embedding_sha256
- predictions_sha256
- confusion_sha256

正式对比只允许同口径三列：

1. SATURN v97g；
2. SAMap v98；
3. ortholog-PCA 按同一 evaluator、mapping 和排除规则重评后的结果。

以下内容只能做历史或实现对照，不进正式排名：

- v72-era 67.4%；
- v97f 全保留版；
- legacy_noncompliant_20260928 SAMap；
- 缺少原始证据的消融或 seed 摘要。

### 统计解释边界

- transductive 结果只回答“同批细胞嵌入中是否存在可迁移的跨物种标签结构”。
- 不能写成“对新物种具有泛化能力”。
- 如果 SATURN 只略高于 majority，必须同时报告绝对差值、F1、coverage 和置换 p 值。
- 如果 SAMap 无显著信号，只能说“在当前三物种、当前预处理和当前样本规模下未检测到信号”，不能断言方法普遍无效。
- ortholog-PCA 若优于复杂模型，应作为重要方法学发现保留，而不是删去。

### Codex 审查点 D

Codex 将随机抽取至少三个方向、三个层级复算，并检查所有方法是否使用同一规则。通过后才能冻结报告数字。

## 九、阶段 E：报告、图表和交接

### E1 先冻结 Markdown，不直接写 Word

先完成以下 Markdown：

- docs\report-methods-draft.md
- docs\report-results-draft.md
- docs\report-limitations-draft.md
- docs\figure-table-plan.md
- docs\evidence-index-final.tsv
- docs\handoff-final.md

内容至少包括：

- 数据来源和三物种选择理由；
- SATURN、SAMap、ortholog-PCA 的同口径流程；
- transductive 与 inductive 的区别；
- mapping 审核和 unmapped 处理；
- 主要结果和负结果；
- 算力消耗位置与 DCS 的作用；
- 当前局限和下一步实验。

### E2 推荐图表

- 图 1：总体流程和证据门。
- 图 2：六方向 coarse accuracy 与 majority baseline。
- 图 3：六方向 macro-F1。
- 图 4：coverage 和 excluded 细胞数量。
- 图 5：SATURN、SAMap、ortholog-PCA 方法对比。
- 表 1：数据集、物种、细胞数、标签数和输入 SHA。
- 表 2：统一方法比较矩阵摘要。
- 表 3：证据等级、协议标签和可引用范围。

图中不能混用 v97f、v97g 或 legacy SAMap 数字。

### E3 生成 Word 的门

只有 Markdown 数字冻结且 Codex 审查通过后，才生成最终 Word 文档。Word 生成后另做：

- 表格和图题核对；
- 数字与 method-comparison.tsv 自动比对；
- 页眉页脚和版本日期；
- Word/WPS 视觉检查。

### E4 队友交接

handoff-final.md 应告诉三位组员：

- 哪些文件是正式结果；
- 哪些是历史实现对照；
- 如何复跑测试；
- 如何核验 SHA；
- 哪些任务仍需要导师或用户批准；
- 不得自行覆盖冻结 mapping 或创建 DCS 大任务。

## 十、阶段 F：未来 inductive 实验，仅规划不执行

本阶段当前禁止执行。只有用户明确批准新 DCS 任务后才启动。

### 推荐最小设计

- 第一轮仍用 human、mouse、zebrafish 三物种 scRNA。
- human-mouse 代表相对近缘；zebrafish 代表较远关系。
- 先做 leave-one-species-out 或明确 train/query 分离的 inductive 设计。
- 每个正式配置至少 3 个 seed。
- 比较 SATURN、SAMap、ortholog-PCA，并保留 majority 和随机置换基线。
- 单细胞结果形成稳定结论后，再做小规模 snRNA 可迁移性检查。
- 空间组学暂不进入主榜。

### 算力预算门

提交前先估算每个任务：

- 镜像和环境启动成本；
- CPU、内存、GPU 类型与时长；
- 数据预处理、蛋白嵌入、模型训练、联合 embedding、评估各阶段耗时；
- 失败重试预留；
- 四位组员体验金如何分配。

推荐先用 1 个 seed 和降采样做 smoke test，确认产物和自记录包装完整，再扩大到正式规模。每个 DCS 任务必须在脚本开头自记录完整命令、环境、输入 SHA、输出路径和协议标签，避免再次出现 provenance 缺口。

## 十一、Flash 第一批可立即执行的范围

Flash 下一轮只执行以下内容：

1. 阶段 0.1：建立当前快照。
2. 阶段 0.2：纠正文档中的 SAMap 状态。
3. 阶段 A1：只读定位 v97g 既有任务；若不可访问则记录 blocked，不新建任务。
4. 阶段 B1：编写 SAMap v98 合规测试。
5. 阶段 B2：实现独立 v98 运行器，但先不要覆盖 legacy 文件。
6. 运行全套测试、manifest validator 和 diff check。
7. 停止，把文件清单、测试输出、阻塞项和建议交给 Codex。

第一批禁止事项：

- 不运行新的 DCS 任务；
- 不 commit 或 push；
- 不修改 mapping v1；
- 不生成最终 Word；
- 不把 SAMap v98 结果写入正式报告；
- 不宣称总体目标完成。

## 十二、给 Flash 的反馈模板

Flash 完成第一批后按以下格式反馈：

    【执行范围】
    完成了哪些编号；跳过了哪些编号及原因。

    【新增或修改文件】
    每个文件一行，说明用途。

    【验证】
    测试数量与结果；manifest 状态；diff check；关键 SHA。

    【v97g 证据】
    task/subtask ID；找到的原始命令、日志、脚本、逐细胞结果；仍缺什么。

    【SAMap v98】
    前缀发生位置；唯一性断言；NA 数；排除计数；是否已实际运行。

    【阻塞】
    只列需要用户、导师或 DCS 登录解决的问题。

    【明确未做】
    DCS 新任务、commit、push、最终报告、正式数字升级。

## 十三、最终完成定义

只有以下全部满足，课题5当前 pilot 阶段才可称为“归档收尾完成”：

- v97g 证据达到可回溯且可复算，或被明确降级为仅汇总可回溯；
- SAMap v98 真正通过条码、真值、排除、逐细胞和哈希门；
- mapping 获人类 reviewer 签认；
- SATURN、SAMap、ortholog-PCA 统一方法矩阵完成；
- 关键数字由产物自动复算；
- 全部测试通过且无 diff 格式错误；
- 报告中的正式、历史和探索性结果清楚分层；
- evidence index 和 handoff 完整；
- Word 文档完成数字核对和视觉检查；
- 未留下无法解释的 NA、重复条码或协议升级。
