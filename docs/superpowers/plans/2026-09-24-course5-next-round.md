# 课题 5 下一轮评估实施计划

> 本计划只允许在用户明确启动下一轮实验后执行；先完成每项的只读审计和 manifest，再提交 DCS 任务。

**Goal:** 在不改变 v71 输入清单的前提下，建立可复核的跨物种标签迁移评估，并分离容量、标签命名和 transductive 信息的影响。

**Architecture:** 先生成不可变输入/参数 manifest，再生成同源标签映射与 barcode 角色表；评估层独立读取 Final AnnData，输出逐细胞预测、混淆矩阵和汇总指标。所有方法共享同一评分协议，方法运行和评分分离。

**Tech Stack:** Python、AnnData、SATURN wheelhouse、现有 scripts 合约测试；DCS 仅用于获批后的离线运行。

## Global Constraints

- 首轮只做单细胞；空间数据不进入主 benchmark。
- 七鳃鳗 snRNA 只能在 scRNA 主评估形成结论后做小规模补充。
- 不把同一 Final AnnData 上的数字称为 held-out benchmark。
- 不使用未核实的 DCS 路径、任务号或模型输出替代原始证据。
- 最终结题材料写入 Word；Markdown/JSON 是审计源文件。

### Task 0: 本地 SATURN Triplet 路径静态审计

Files: scripts/audit_saturn_triplet_path.py, tests/test_saturn_triplet_audit.py

- [ ] 对 checked-in `wheelhouse/saturn-src/train-saturn.py` 做 AST 静态审计，不导入或执行 SATURN。
- [ ] 记录 `TripletMarginMiner` 的 `miner_type`、`use_ref_labels` 分支、`get_species_triplet_indices()` 是否在默认初始化之外读取 `ref_labels`，以及 `obsm["macrogenes"]` 输出。
- [ ] 输出带源码 SHA-256、行号和证据片段的 JSON/文本报告；发现 `ref_labels` 未参与正负样本选择时标记为 warning，不能把存在该参数误写成已使用。
- [ ] 只运行本地静态审计和单元测试，不启动 DCS、不上传数据、不提交或推送。

### Task 1: 冻结输入与角色表

Files: config/eval-manifest-v73.json, config/barcode-roles-v73.tsv, scripts/validate_eval_manifest.py, tests/test_eval_manifest.py

- [ ] 记录每个物种输入文件、SHA-256、细胞数、标签列、表达表示层、seed、候选基因范围和 num_macrogenes。
- [ ] 记录 query/reference 角色；检查 barcode 唯一性和 query/reference 交集为 0。
- [ ] 用只读校验器验证 `pending`/`confirmed` 状态转换：未取得 DCS provenance 时保持 pending；不允许用空条码表、缺 hash 或缺 reviewer 签名放行。
- [ ] 若 DCS 原始命令或 task ID 缺失，manifest 标记 evidence_status=pending，不得提交重跑。

### Task 2: 冻结同源标签映射

Files: config/heart-celltype-map-v1.tsv, docs/source-notes.md, tests/test_ortholog_contract.py

- [ ] 每行保留 source label、mapped label、evidence source、mapping confidence 和 reviewer。
- [ ] 同时保留 exact label；评分器输出 exact 与 mapped 两套结果。
- [ ] 无法可靠映射的标签使用 unknown/ambiguous，禁止强行归类。

### Task 3: 评估器与泄漏审计

Files: scripts/evaluate_cross_species_transfer.py, tests/test_cross_species_evaluator.py

- [ ] 输入固定的 X 或 obsm 键，不允许隐式回退。
- [ ] kNN 排除 self、重复 barcode 和角色表外记录。
- [ ] 输出逐细胞预测、confidence、abstain、coverage、macro-F1、micro-F1、top-k、混淆矩阵和 JSON 摘要。
- [ ] 运行 transductive 与 inductive 两个协议并列输出。

本地评估器只接受显式 NPZ bundle；不会自动从 h5ad 选择 `X` 或
`obsm["macrogenes"]`，也不会连接 DCS。示例（正式运行前需把 bundle 的提取命令、路径和 hash 写入 manifest）：

```powershell
python scripts/evaluate_cross_species_transfer.py `
  --input-npz <explicit-bundle.npz> `
  --output <summary.json> `
  --representation obsm/macrogenes `
  --protocol inductive `
  --k 15
```

### Task 4: 容量与稳定性小实验

Files: config/ablation-macrogenes-v1.json, docs/ablation-protocol-v1.md

- [ ] 固定 v71 的输入、HVG、epochs、miner 和表示层。
- [ ] 只改变 num_macrogenes 为 16、128、1000；每点 3 seeds。
- [ ] 先在本地/小规模数据完成评分器验收；DCS 运行需用户明确启动。

### Task 5: 质量门与 Word 报告素材

Files: docs/benchmark-quality-gate-v1.md, docs/report-template.md

- [ ] 将结果分为已证实、探索性、待补证据三类。
- [ ] 将输入、版本、命令、时间、内存、失败和重试记录写入可复制表格。
- [ ] 通过测试、preflight 和人工抽样检查后，才生成 Word 报告素材。

## Status snapshot (2026-09-26)

- Task 0 is complete as a local static audit. The checked-in SATURN source, Triplet miner branch, `ref_labels` handling, and `obsm["macrogenes"]` output are recorded in `docs/local-saturn-triplet-audit-20260925.json`; this does not prove the DCS runtime used the same source or image.
- Task 1 is partially advanced but intentionally still pending. DCS batch and subtask IDs, status, timestamps, resource tier, image name, startup logs, and runtime-log summaries for v71/v72 are now recorded in `docs/dcs-browser-offline-task-audit-20260926.md` and `docs/dcs-offline-task-history-20260926.md`. `config/eval-manifest-v73.json` remains `evidence_status=pending`, and `config/barcode-roles-v73.tsv` is header-only because original commands, query/reference barcodes, input/output hashes, and representation-extraction provenance have not been recovered.
- Tasks 2 and 3 have local contracts and exploratory evidence, but their results must not be upgraded to a formal benchmark until Task 1's provenance gate passes.
- Tasks 4 and 5 remain execution-gated. No DCS task may be submitted until the user explicitly starts the next experiment and the manifest passes validation.

## Validation refresh (2026-09-26)

- `python scripts/validate_eval_manifest.py` still returns `valid=true`, `evidence_status=pending`, and `ready_for_confirmation=false`; the remaining blockers are unchanged and include empty query/reference barcode roles, missing original command, missing complete log path, missing evaluation layer, and missing reviewer.
- `python -m unittest discover -s tests -v` completed with `Ran 76 tests ... OK (skipped=3)`. The three skips are the existing `anndata`-dependent inspection tests because `anndata` is not importable in this local environment; no test failure occurred.
- `git diff --check` completed without whitespace errors; Git only reported the existing LF/CRLF normalization warnings for tracked Markdown files.
- Added `docs/method-to-evaluation-matrix-20260926.md`, which translates BENGAL, scSpecies, HEART, LBSPA, CAMEX, and SATURN method lessons into fields and quality gates. This does not change the manifest or authorize cloud execution.
