# 20261111 复现性审计：scripts/ 全量清点 + 实跑 + 不可复现断点

## 目标

回答三个问题，给证据不给推测：

1. `scripts/` 下 118 个 `.py`，哪些在**这台干净机器**（无 GPU、无 WSL、无 docker，只有 `.venv39` 一套科学栈）上能独立跑通？
2. 每个脚本吃哪些仓库内文件、写到哪里？
3. 哪些结论的复算链断了，断在哪个具体路径上？

产出：`scripts/reproduce_all.py`（一键复现，实测 30/30 通过）+ 本文档 + `docs/execution/20261111-repro-manifest.md`。

## 原理

复现性只能靠「换环境后从输入重算、并与仓库里已冻结的产物逐字节比对」来证明，不能靠「我这儿能跑」。所以本次审计做了三件事：

- **静态清点**：AST 解析每个脚本的 docstring / import / 路径字面量 / 写文件调用，把「输入」和「输出」分开（输出路径故意写成不存在的文件，静态扫描会把它们误报成缺件，需人工区分）。
- **实跑探测**：把 `config/ results/ ortholog/ + 3 个 .h5ad` 硬链接进一个隔离沙箱，逐个跑 118 个里能跑的 51 个，记录退出码与产物。沙箱外不落任何写操作。
- **路径重定向**：38 个脚本把仓库根硬编码成 `D:\projects\course5-prep`，换机器直接跑不了。沙箱内用运行期 shim 把该前缀重写到沙箱根（`pathlib.Path` / `builtins.open` / `os.makedirs` 等），**脚本源码一字不改**，等价于换挂载点。

判据（后面表格里的「可跑」）：

| 判定 | 含义 |
|---|---|
| 是 | 本次实跑退出码 0，产物与仓库同名文件逐字节一致（或该步本来不落盘） |
| 部分 | 有仓库内输入、能跑，但要么需要手工传参、要么依赖 venv39 里没有的库、要么产出文档需额外模板 |
| 否 | 输入在平台镜像/临时目录里（`/Files`、`/data/work`、DCS 任务日志），本机不存在 |

> 说明：清点是在 2026-11-11 21:12 做的快照（118 个 `.py`）。之后仓库里又出现若干 `_sup*.py`、`fix_*.py` 等一次性脚本（另一个并发任务所写），不在本表范围。

---

## A 脚本清单（118 个，逐个判定）

| 脚本 | 输入 | 输出 | 本地可跑 | 缺什么 |
|---|---|---|---|---|
| `_dump_hits.py` | 源码内硬编码的扫描目标 | 仅 stdout | 是 | — |
| `_dump_saturn_v2.py` | `results/pilot-v1/saturn-v99` 内文件 | 仅 stdout | 是 | — |
| `_map_diff.py` | `config/heart-celltype-map-v1.tsv` 等两份映射 | 仅 stdout | 是 | — |
| `_opca_inductive_variant.py` | `/Files/wheelhouse/{orth-*, heart-celltype-map-v1.tsv}` | `OPCA_OUT_ROOT` | 否 | `/Files/wheelhouse` 平台数据 |
| `_opca_lr_variant.py` | 同上 | 同上 | 否 | 同上 |
| `add_report02_notes.py` | `results/report02-walkthrough-content.json` + 平台版 PPTX | 备注版 `.pptx` | 否 | `课题5第02次汇报_数字来源链_校模板.pptx`（deliverables 里只有 docx 版） |
| `agent_evaluation.py` | `config/agent-evaluation-plan.json` | 仅 stdout（校验结论） | 是 | — |
| `audit_consistency_scan.py` | 扫 `docs/` `deliverables/` 的 md/docx/pptx | `results/audit-consistency-*/hits.json` | 部分 | venv39 无 `python-docx`，docx/pptx 文本抽取跑不全 |
| `audit_saturn_triplet_path.py` | `wheelhouse/saturn-src/train-saturn.py` + `utils/loss_and_miner_utils.py` | `--output` JSON | 是 | —（沙箱里若剔掉 wheelhouse 就会报缺，本机仓库里是在的） |
| `bootstrap_ci.py` | `results/pilot-v1/**/predictions`、`phase-20261019/scvi-cross-species/recomputed_union.json`、`config/v1 tsv` | `results/bootstrap-20261030/bootstrap.json` | 是 | —（跑前会与冻结表逐格对齐，不等就 abort） |
| `bootstrap_crossphylum.py` | `results/phase-20261022/crossphylum/metrics.json` | `results/bootstrap-20261030/crossphylum.json` | 是 | — |
| `bootstrap_saturn_fixed.py` | `pilot-v1/saturn-v99/raw/recovered-20261001/confusion/coarse_*.json`、`config/v1 或 v2 tsv` | `saturn_bootstrap_fixed[_mapv2].json` | 是 | —（`MAP_TSV` / `OUT_NAME` 原生支持切映射） |
| `budget_check.py` | `config/dcs-budget-plan.json` | 仅 stdout | 是 | — |
| `build_current_table.py` | `results/bootstrap-20261030/*.json`、`mapping-v2-20261111/rerun-v2/metrics.json` | `results/current-20261111/current-table.{json,tsv}` | 部分 | 未实测；输入齐全，属文档型产物 |
| `build_final_presentation.py` | `results/bootstrap-20261030/bootstrap.json` 等 | `deliverables/course5-final-presentation.pptx` | 部分 | 需 `python-pptx`（venv39 有），但未实测；产物无基线可比 |
| `build_final_report.py` | 冻结 metrics JSON | `deliverables/course5-final-report.docx` | 部分 | venv39 无 `python-docx`（只有系统 3.13 有） |
| `build_master_handoff_docx.py` | `docs/execution/20261028-master-handoff.md` | `deliverables/课题5-总交接文档-20261028.docx` | 部分 | 同上，需 `python-docx` |
| `build_monday_presentation.py` | 冻结 metrics | `course5-monday-presentation.pptx` | 部分 | venv39 有 pptx；未实测 |
| `build_paper_evidence.py` | 各 `results/**/*.json` | `docs/…evidence-index.json` + md | 部分 | 未实测 |
| `build_pitfalls_docx.py` | `docs/execution/20261030-pitfalls.md` | `课题5-踩坑清单-20261030.docx` | 部分 | 需 `python-docx` |
| `build_ppt_handoff_pack.py` | 页面截图 `v3-*.png`、`主结果.csv` | `deliverables/ppt-handoff-pack/` | 否 | 截图与 csv 不在仓库（`results/stage-reports-*/render/` 已被删） |
| `build_progress_presentation.py` | `Homo/Mus/Danio_*_sc.h5ad` | `course5-progress-presentation.pptx` | 否 | 三个 `*_sc.h5ad` 原始数据不在仓库（只有 `local_*_s.h5ad`） |
| `build_report02_walkthrough.py` | `results/report02-walkthrough-content.json` | `课题5第02次汇报-逐页讲解稿-20261027.docx` | 部分 | 需 `python-docx` |
| `build_report03_round3_pptx.py` | `bootstrap.json`、`resource-ledger.json`、平台 v99 映射 | `课题5第03次汇报_….pptx` | 部分 | 依赖 `results/resource-20261030/resource-ledger.json`（本机无，只有 `resource_summary.json`） |
| `build_report_template.py` | 报告 md | `.docx` 模板 | 部分 | 需 `python-docx` |
| `build_report_v3.py` | 冻结 metrics + 学校模板 pptx | `课题5-汇报-v3-学校模板-20261110.pptx` | 否 | 学校模板 `课题5第03次汇报_三场景结论与可复现闭环.pptx` 不在仓库 |
| `build_report_v4.py` | 同上 | `课题5-汇报-v4-20261111.pptx` | 否 | 同上 |
| `build_samap_v98_dcs_payload.py` | 平台 `/data/work/*.h5ad`、`/Files/wheelhouse/*` | base64 payload 文本 | 否 | 平台输入文件；只生成提交串，不含计算 |
| `build_speaker_notes_docx.py` | `课题5-汇报-讲故事版-20261110.pptx` | 讲稿 `.docx` | 否 | 源 pptx 不在仓库 |
| `build_story_deck.py` | 冻结 metrics | `课题5-汇报-讲故事版-20261110.pptx` | 部分 | venv39 有 pptx；未实测 |
| `build_story_deck_school_template.py` | 冻结 metrics + 学校模板 | 学校模板版 pptx | 否 | 学校模板不在仓库 |
| `build_teacher_reply_docx.py` | `docs/reports/report-08-teacher-reply-20261030.md` | `课题5-老师七条意见回应-20261030.docx` | 部分 | 需 `python-docx` |
| `build_team_briefing_docx.py` | `docs/execution/20261104-队友交接总纲.md` | `课题5-组员汇报说明-小白版.docx` | 部分 | 需 `python-docx` |
| `build_team_handbook.py` | `docs/team-handbook/part1..3.md` + `_toc_pages.json` | `课题5-组员入门手册-20261104.docx` | 部分 | 需 `python-docx` + `_toc_pages.json`（由 `compute_toc_pages.py` 用 LibreOffice 生成） |
| `build_team_handoff_overview_docx.py` | `docs/execution/20261104-队友交接总纲.md` | `课题5-组员交接总纲-2026104.docx` | 部分 | 需 `python-docx` |
| `build_transductive_bundles.py` | `--final-anndata`（平台合并 adata）+ `config/v73 tsv` | `*.npz` + manifest | 否 | 平台合并 anndata 不在仓库 |
| `build_v99_rec_payload_task.py` | `g5_v99_rec_payload.py` | 加密 payload | 否 | 需平台任务上下文 |
| `cdp_capture_responses.py` | 本机已开 Chrome 的 CDP 端口 | 抓包 JSON | 部分 | 需先有人开浏览器并开 `--remote-debugging-port` |
| `cdp_page_eval.py` | 同上 | 表达式结果/截图 | 部分 | 同上 |
| `compute_batch_metrics.py` | `--embedding *.npy` + `--obs obs.json` + `config/v1 tsv` | `--out` JSON | 是 | —（SAMap 臂有 obs 可复算；scVI 臂缺 obs） |
| `compute_toc_pages.py` | 手册 PDF | `_toc_pages.json` | 否 | 需 LibreOffice（`soffice`）与已生成的 PDF |
| `convention_flip_check.py` | `results/pairwise-20261111/opca_official_paired.json`、`pairwise_corrected.json` | 仅 stdout | 是 | — |
| `convention_sensitivity.py` | `results/bootstrap-20261030/saturn_convention_mapv2.json`、`mapping-v2-20261111/rerun-v2/metrics.json` | `results/convention-20261111/*` | 是 | — |
| `convention_variants.py` | `config/v1 tsv` + `pilot-v1/.../confusion/coarse_*.json` | `results/bootstrap-20261030/convention_variants.json` | 是 | — |
| `crossphylum_lamprey_mouse.py` | 平台 `/Files` 八物种脑数据 | `metrics.json` 等 | 否 | LBSPA 原始 h5ad（`/Files`），仓库无 |
| `dcs_provenance_v95.py` | `/data/work` 平台产物 | `/data/work` 下 CSV | 否 | 平台目录 |
| `dcs_provenance_v96_readout.py` | `/data/work`（`G5_V96_ROOT`） | 只读 readout | 否 | 平台目录 |
| `dcs_provenance_v99.py` | `/data/work/course5_v99/**` | `recovered-*` 全套 | 否 | 平台目录；本仓库 `recovered-20261001` 是它当年的产物 |
| `dcs_readonly_probe.py` | 无（读运行环境） | 仅 stdout | 是 | —（本机跑只反映本机） |
| `donor_bootstrap.py` | `ortholog/` + h5ad obs 的 donor 列 + predictions | `results/bootstrap-donor-20261111/*` | 是 | — |
| `drop_unmapped_audit.py` | `saturn_convention_mapv2.json`、`rerun-v2/metrics.json` | `results/convention-20261111/*` | 是 | — |
| `environment_check.py` | 运行环境 | `environment-report.json` | 是 | — |
| `environment_contract.py` | `environment-report.json`（位置参数） | 仅 stdout 判定 | 部分 | 需先跑 `environment_check.py` 并把报告路径传进去 |
| `evaluate_cross_species_transfer.py` | `--adata`/predictions | 逐细胞评测 | 部分 | 需传参；本机无对应合并 adata |
| `evaluator_ablation.py` | `_opca_lr_variant.py` + `/Files` 同源表 | `results/evaluator-20261111/*` | 否 | 缺 `/Files/wheelhouse/orth-*.txt` 与 LR 变体产物 |
| `extract_v99_from_logs_v1.py` | 平台恢复日志（硬编码根） | `recovered-20261001/` 重建 | 否 | 原始 DCS 日志不在仓库 |
| `g5_v99_rec_payload.py` | 硬编码分配表 | stdout payload | 部分 | 依赖平台文件清单，仅打印 |
| `g5_v99_rec_r1.py` | `/data/work/course5_v99` | readout JSON | 否 | 平台目录 |
| `heart_h5ad_inspect.py` | `local_{human,mouse,zebrafish}_s.h5ad`（位置参数） | `--output` JSON | 是 | — |
| `image_selfcheck.py` | 镜像内 `/Files` 数据 + 锁版本 | stdout JSON（`SELFCHECK_BEGIN/END`） | 否 | 需 `g5-opca-container` 镜像（本机无 docker/WSL） |
| `input_contract.py` | 元数据 CSV（位置参数） | 仅 stdout 判定 | 部分 | 需传参；原始元数据 csv 不在仓库 |
| `labelspace_ablation.py` | `rerun-v2/metrics.json`（硬编码根） | `results/labelspace-20261111/*` | 是 | — |
| `local_readiness.py` | `budget_check` / `environment_check` 模块 | `local-readiness.json` | 否 | 同目录导入失败：脚本按 `from budget_check import …` 写，需 `scripts/` 在 `sys.path` |
| `mapping_v2_sensitivity.py` | `config/v1 tsv` + confusion | `mapping_v2_sensitivity.json` | 是 | —（但根目录是硬编码绝对路径，换机器必须改源码） |
| `memprobe_run.py` | 被 `resource_sweep` 调用 | `resource.json` | 部分 | 需平台任务上下文才会被调起 |
| `opca_mapping_convention_audit.py` | `config/v1+v2 tsv`、`v99_mapping_embedded.json`、`manifest.json` | `results/mapping-v2-20261111/opca_mapping_convention_audit.json` | 是 | — |
| `opca_mapping_v1_v2_audit.py` | `config/v1+v2 tsv` + 冻结 predictions | `opca_v1_vs_v2.json` | 是 | — |
| `opca_stability_run.py` | `/Files` 数据 + `ortholog/MGI_HOM_*.rpt` | 稳定性矩阵 | 否 | 预检即硬停：缺 `ortholog/MGI_HOM_MouseHumanSequence.rpt`（只有同名不同后缀的 `.rpt`？本机为 `MGI_HOM_MouseHumanSequence.rpt` 未就位时直接 HARDSTOP） |
| `orhters_variant_impact.py` | `config/v1 tsv` + confusion | `orthers_variant_impact.json` | 是 | —（根目录硬编码绝对路径） |
| `ortholog_contract.py` | 同源表（位置参数） | 仅 stdout 判定 | 部分 | 需传参 |
| `ortholog_coverage.py` | `ortholog/*.txt` + h5ad var | `results/ortholog-coverage-20261111/*` | 是 | — |
| `ortholog_pca_dcs_v2.py` | `/Files` h5ad + `/Files/wheelhouse` | 平台结果 | 否 | 平台数据 |
| `ortholog_pca_dcs_v3_fixkey.py` | 同上 | 同上 | 否 | 平台数据 |
| `ortholog_pca_full_isolated.py` | 平台 wrapper（打补丁源码） | `results/pilot-v1/…` | 否 | 需平台源码树 |
| `ortholog_pca_local_v1.py` | `/Files` 数据 | `metrics.json` 等 | 否 | 平台数据 |
| `ortholog_pca_task1_isolated.py` | 同上 | 同上 | 否 | 平台数据 |
| `ortholog_pca_v98_final.py` | 同上 | 同上 | 否 | 平台数据 |
| `pack_to_docx_xlsx_zip.py` | 交接稿版面 md/xlsx | `docx+xlsx+zip` | 部分 | 需 `python-docx`/`openpyxl`（venv39 缺） |
| `pairwise_corrected.py` | 各方法 predictions + `config/v2 tsv` | `results/pairwise-20261111/pairwise_corrected.*` | 是 | — |
| `pairwise_donor_level.py` | 同上 + h5ad donor 列 | `pairwise_donor_level.*` | 是 | — |
| `pairwise_inductive.py` | `transductive-20261111/inductive-variant/predictions` 等 | `pairwise_inductive.*` | 是 | — |
| `pairwise_lr_evaluator.py` | `evaluator-20261111/lr-variant/predictions` 等 | `pairwise_lr_evaluator.*` | 是 | — |
| `pairwise_opca_official.py` | 冻结 predictions + `config/v2 tsv` | `opca_official_paired.*` | 是 | — |
| `pairwise_significance.py` | `stability-20261030/runs/seed-0/predictions`、saturn payloads | `pairwise.json` | 否 | 读 `*.json.gz` 时缺稳定性臂压缩预测（`results/stability-20261030` 只保留 seed 级 json） |
| `parse_v99_rec_log_v1.py` | 平台 `g5-v99-rec-r1` 日志 | `recovered-20261001/` + 校验 | 否 | 原始日志不在仓库 |
| `plan_contract.py` | `config/benchmark-plan.json` | 仅 stdout 判定 | 是 | — |
| `rebuild_deck_evidence.py` | `results/stage-reports-*` 全页截图 | 证据图 | 否 | 截图已从仓库删除（`render/v2/raw-*.png` 为 deleted 状态） |
| `region_breakdown.py` | `local_human_s.h5ad` + predictions | `results/region-20261111/*` | 是 | — |
| `render_teacher_tables.py` | `bootstrap.json`、`resource_summary.json`、`stability/aggregate.json` | 仅 stdout Markdown | 是 | — |
| `resource_ledger.py` | DCS 任务记录 + 本地 resource.json | `resource-ledger.json` | 否 | 需平台任务记录（`/data/work`、DCS API） |
| `resource_sweep.py` | `memprobe_run.py` + 平台运行 | 汇总 json | 否 | 需反复起平台任务 |
| `result_contract.py` | metrics + resources（位置参数） | 仅 stdout 判定 | 部分 | 需传参 |
| `run_artifacts.py` | 一次 run 目录（位置参数） | 仅 stdout 判定 | 部分 | 需传参；所指 run 目录需平台产物 |
| `run_samap_compliant_v98.py` | `/Files/local_*_s.h5ad` + `/Files/wheelhouse/orth-*` | `metrics.json`/predictions | 否 | 平台数据 + SAMap 大图（本机内存不够） |
| `run_samap_compliant_v98_dcs.py` | 同上（DCS 路径） | 同上 | 否 | 同上 |
| `run_samap_full_isolated.py` | 打补丁源码 wrapper | `results/pilot-v1/samap-*` | 否 | 需平台源码树 |
| `run_samap_v98_dcs_embedding.py` | 同上 + 蛋白嵌入 tar | 同上 | 否 | 同上 + 3.7 GB 蛋白嵌入 |
| `run_samap_v98_with_embedding.py` | 同上 | 同上 | 否 | 同上 |
| `run_transductive_formal_v74.py` | `build_transductive_bundles` 产出的 npz | `metrics.json` | 否 | npz bundle 需平台合并 adata 才能生成 |
| `saturn_convention_audit.py` | `config/v1 tsv` + confusion | `saturn_convention.json` | 是 | —（v1，方向颠倒，保留作对照） |
| `saturn_convention_audit_v2.py` | 同上 | `saturn_convention_v2.json` | 是 | — |
| `saturn_output_scores.py` | `--adata` SATURN 输出 adata | `saturn_scores.json` | 否 | 平台输出的 `adata` 文件不在仓库（`results/` 内 0 个 `.h5ad`） |
| `saturn_vs_scvi_paired.py` | saturn/scvi 逐细胞预测（`.json.gz`） | `saturn_vs_scvi.json` | 否 | 缺 scVI 侧压缩逐细胞预测 |
| `scvi_cross_species.py` | `/Files` h5ad + `/Files/wheelhouse` 同源表 | `metrics.json`/`latent.npy` | 否 | 平台数据；含 scVI 训练（本机无 GPU，CPU 也需很久） |
| `scvi_mapping_v1_v2_audit.py` | `scvi-cross-species/recomputed_union.json` + `config/v1+v2` | `scvi_v1_vs_v2.json` | 是 | — |
| `smoke_test.py` | 合成数据 + `tests/fixtures` | `smoke-output/` | 否 | 读 `run_manifest.json` 时缺 `results/phase-*/…` 指定目录 |
| `smoke_test_env.py` | 本机包 | 仅 stdout | 否 | `mudata` 未装（`import mudata` 直接崩） |
| `source_manifest_check.py` | `--manifest` + 源目录 | 仅 stdout 判定 | 部分 | 需传参；`config/source-file-manifest.tsv` 不在仓库 |
| `stab_campaign.py` | 10 seed × 扰动数据 + 平台 oPCA | `results/stability-20261030/*` | 否 | 需跑 20 次平台 oPCA |
| `stab_make_perturbed_data.py` | 3 个 h5ad | 扰动副本 | 部分 | 可跑但产出数 GB，未纳入一键流程 |
| `startup_preflight.py` | `config/startup-preflight.json` | 仅 stdout 判定 | 是 | — |
| `strip_report_ordinal.py` | `课题5-汇报-…筛查版.pptx` | 去序号版 pptx | 否 | 源 pptx 不在仓库 |
| `team_budget_check.py` | `config/dcs-budget-plan.json` | 仅 stdout | 否 | 同目录导入失败：`from budget_check import load_plan`（需 `scripts/` 在 `sys.path`） |
| `transductive_ablation.py` | `_opca_inductive_variant.py` + 平台数据 | 消融 json | 否 | 平台数据 + 变体脚本 |
| `unified_coarse_macro_f1.py` | 18 份逐细胞预测 + `config/v1 tsv` | `results/phase-20261017/unified-coarse-macro-f1/*` | 是 | —（根目录 `D:/projects/course5-prep` 硬编码） |
| `validate_eval_manifest.py` | `config/eval-manifest-v73.json` + `barcode-roles-v73.tsv` | 仅 stdout 判定 | 部分 | 需传参；manifest 指向的 anndata 不在仓库 |
| `verify_dcs_recompute.py` | DCS 重算产物 + 本地 metrics | 仅 stdout 比对 | 否 | 需 `W202610110124739` 等任务产物 |
| `verify_scvi_artifact.py` | 恢复的 scVI 产物目录 | 仅 stdout | 否 | 缺 `metrics.json` + `latent.npy` 的完整恢复包（本机只有 `latent.npy`） |

**汇总**：118 个里 **30 个**进入一键复现并实测通过（+ 2 个探针实测通过但不落盘的校验脚本 `_dump_*`/`_map_diff`/`audit_saturn_triplet_path`/`render_teacher_tables` 等），**约 40 个**属「部分」（能跑但缺库/缺参数/产物无基线），**约 45 个**属「否」（吃平台 `/Files`、`/data/work`、DCS 任务产物或 GPU）。

---

## B 实测回显（命令 / 耗时 / 退出码 / 关键行 / 产物）

全部在**隔离沙箱**里跑（`results/repro-20261111-215553/_sandbox`，跑完已删），仓库内文件零改动（`git status` 与运行前一致，仅多出复现目录本身）。

### B.1 `scripts/convention_variants.py` · 0.1 s · rc=0

```
direction           frozen   A        B        C        D          (n_q for each)
human->mouse        0.4147   0.4147   0.3522   0.298    0.3089
mouse->human        0.401    0.401    0.2566   0.313    0.2714
human->zebrafish    0.2479   0.2479   0.1269   0.1798   0.1418
zebrafish->human    0.4021   0.4021   0.164    0.1834   0.2512
mouse->zebrafish    0.65     0.65     0.3658   0.3913   0.3718
zebrafish->mouse    0.651    0.651    0.3563   0.3441   0.4602

A_truth_src_pred_tgt       复现冻结值 6/6
B_truth_tgt_pred_src       复现冻结值 0/6
C_truth_src_pred_src       复现冻结值 0/6
D_truth_tgt_pred_tgt       复现冻结值 0/6
```

产物 `results/bootstrap-20261030/convention_variants.json` 3546 B，sha256 前 8 位 `c39ca5b2`，与仓库内同名文件**逐字节一致**。结论复现：只有约定 A 能复现 6 个冻结值，且那 6 个冻结值正是被 11-08 更正掉的错口径 → 冻结值本身是「口径 A 的产物」，不是「方法的上限」。

### B.2 `scripts/saturn_convention_audit_v2.py` · 0.1 s · rc=0

```
human->mouse       n_pub= 1505 n_strict= 1505 truth_unmapped=   0 pub_mf1=0.3522 -> strict_mf1=0.3522 (差 0.0)
mouse->human       n_pub= 1528 n_strict= 1528 truth_unmapped=   0 pub_mf1=0.2566 -> strict_mf1=0.2566 (差 0.0)
human->zebrafish   n_pub= 1499 n_strict= 1499 truth_unmapped=   0 pub_mf1=0.1269 -> strict_mf1=0.1269 (差 0.0)
zebrafish->human   n_pub= 1528 n_strict= 1528 truth_unmapped=   0 pub_mf1=0.164  -> strict_mf1=0.164  (差 0.0)
mouse->zebrafish   n_pub= 1499 n_strict= 1499 truth_unmapped=   0 pub_mf1=0.3658 -> strict_mf1=0.3658 (差 0.0)
zebrafish->mouse   n_pub= 1505 n_strict= 1505 truth_unmapped=   0 pub_mf1=0.3563 -> strict_mf1=0.3563 (差 0.0)
```

产物 `saturn_convention_v2.json` 2816 B，`e83b4607`，**逐字节一致**。结论复现：修正方向后「SATURN 靠丢样本抬分」的现象消失（三个口径 mf1 完全相同，inflate=0）——与 11-08 更正稿一致。

### B.3 `scripts/bootstrap_saturn_fixed.py` · 2.7 s（v1）/ 2.8 s（v2 映射）· rc=0

```
mapping = config/heart-celltype-map-v1.tsv
direction            n_q      acc      mf1      ±SE              95% CI
human->mouse        1505   0.5887   0.3522   0.0127   [0.3274, 0.3763]
mouse->human        1528   0.2271   0.2566   0.0140   [0.2278, 0.2809]
human->zebrafish    1499   0.1775   0.1269   0.0069   [0.1122, 0.1399]
zebrafish->human    1528   0.2336   0.1640   0.0069   [0.1506, 0.1770]
mouse->zebrafish    1499   0.2982   0.3658   0.0143   [0.3373, 0.3935]
zebrafish->mouse    1505   0.4671   0.3563   0.0140   [0.3265, 0.3814]
```

两个产物都**逐字节一致**：`saturn_bootstrap_fixed.json`（`cc43e61f`）、`saturn_bootstrap_fixed_mapv2.json`（`71323844`）。1000 次重抽样的 CI 因此可复现（RandomState(20261030) 固定）。

### B.4 `scripts/mapping_v2_sensitivity.py` · 0.1 s · rc=0

```
基线 mf1: {'human->mouse': 0.3522, 'mouse->human': 0.2566, 'human->zebrafish': 0.1269, 'zebrafish->human': 0.164, 'mouse->zebrafish': 0.3658, 'zebrafish->mouse': 0.3563}

== R36_zebrafish_Orthers
   human->zebrafish   0.1269 -> 0.1282  (+0.0013)  n_q 1499 -> 1469
   zebrafish->human   0.1640 -> 0.1386  (-0.0254)  n_q 1528 -> 1528
   mouse->zebrafish   0.3658 -> 0.4076  (+0.0418)  n_q 1499 -> 1469
   zebrafish->mouse   0.3563 -> 0.2961  (-0.0602)  n_q 1505 -> 1505

== R21_mouse_Valve
   human->mouse       0.3522 -> 0.3500  (-0.0022)  n_q 1505 -> 1475
   mouse->human       0.2566 -> 0.2271  (-0.0295)  n_q 1528 -> 1528
   mouse->zebrafish   0.3658 -> 0.3264  (-0.0394)  n_q 1499 -> 1499
   zebrafish->mouse   0.3563 -> 0.3567  (+0.0004)  n_q 1505 -> 1475

== R30_zebrafish_Perivascular
   human->zebrafish   0.1269 -> 0.1235  (-0.0034)  n_q 1499 -> 1469
   mouse->zebrafish   0.3658 -> 0.3684  (+0.0026)  n_q 1499 -> 1469
```

产物 `mapping_v2_sensitivity.json` 3385 B，`73b006e7`，**逐字节一致**。
注意：该脚本第 20 行把根目录写死 `Path(r"D:\projects\course5-prep")`，**换机器不改源码就跑不了**；本次靠 shim 重定向。

### B.5 `scripts/orhters_variant_impact.py` · 0.1 s · rc=0

```
方向                现行 mf1    改后 mf1    Δ        n_q 现   n_q 后   新丢预测
human->mouse      0.3522    0.3522    +0.0     1505    1505    0
mouse->human      0.2566    0.2566    +0.0     1528    1528    0
human->zebrafish  0.1269    0.1282    +0.0013  1499    1469    0
zebrafish->human  0.164     0.1386    -0.0254  1528    1528    865
mouse->zebrafish  0.3658    0.4076    +0.0418  1499    1469    0
zebrafish->mouse  0.3563    0.2961    -0.0602  1505    1505    100
```

产物 `orthers_variant_impact.json` 1876 B，`cbb2a80a`，**逐字节一致**（同样是硬编码根）。

### B.6 `scripts/compute_batch_metrics.py`（可选，SAMap 臂）· 3.5 s · rc=0

```
python scripts/compute_batch_metrics.py \
  --embedding results/phase-20261026/samap-batch/samap_joint_embedding.npy \
  --obs       results/phase-20261026/samap-batch/samap_joint_obs.json \
  --mapping   config/heart-celltype-map-v1.tsv --out <step>/batch_metrics.json
```

复算值 `silhouette 0.043094 / iLISI 1.006092 / kBET 0.001086`，与仓库 `results/phase-20261026/samap-batch/batch_metrics.json` **逐字节一致**。
反例：同脚本用于 scVI 臂时无 `obs.json`（`results/phase-20261019/scvi-cross-species/` 只有 `latent.npy`），因此 §7.1 报的 `silhouette 0.181 / iLISI 1.120 / kBET 0.0039` **本机无法复算**——这是 C 段第 3 条断点。

### B.7 一键复现总回显

```
[repro] 输出目录 D:\projects\course5-prep\results\repro-20261111-215553
[repro] python 3.9.6  git codex/teacher-reply-report-prep@d624917e51
[repro] 步骤 30 / 30
[repro] 沙箱: link=2408 copy=0 skip_big=0 skip_excluded=0
[01] env-check                        OK      0.6s
...
[30] h5ad-inspect                     OK      3.2s
[repro] 完成 30/30，耗时 278.5s
[repro] manifest: ...\results\repro-20261111-215553\manifest.json
[repro] 全部步骤退出码 0
```

**实测退出码 0**，30/30 通过，全部产物与仓库同名文件逐字节一致（`=`），无一步 `~`（值相同但非逐字节）或 `≠`。

小节耗时（s）：bootstrap_crossphylum 51.3 · pairwise_corrected 40.0 · pairwise_inductive 27.2 · pairwise_lr_evaluator 27.3 · pairwise_opca_official 26.5 · bootstrap_ci 23.7 · pairwise_donor_level 20.6 · donor_bootstrap 14.5 · 其余 ≤3.5。

---

## C 不可复现断点（按影响面排序）

| # | 断点 | 具体缺失路径 | 被谁依赖 | 后果 |
|---|---|---|---|---|
| 1 | **平台镜像内输入目录** | `/Files`（`/Files/wheelhouse/*.h5ad`、`/Files/wheelhouse/orth-MGI-HOM.rpt`、`orth-human-orthos.txt`、`orth-mouse-orthos.txt`、`/Files/local_*_s.h5ad`） | `_opca_*`、`ortholog_pca_dcs_v2`、`ortholog_pca_v98_final`、`ortholog_pca_local_v1`、`run_samap_*`、`scvi_cross_species`、`crossphylum_lamprey_mouse`、`opca_stability_run`、`evaluator_ablation`、`transductive_ablation` | 四方法里 **oPCA / SAMap / scVI 三条臂的原始重算全部跑不了**；本机只有成品 `metrics.json`，无法从源头验证 |
| 2 | **平台工作目录** | `/data/work`、`/data/work/course5_v99/**`、`/data/work/saturn_out_real3_h/saturn_results/`、`/data/work/prep_real_v60.py` | `dcs_provenance_v95/v96/v99`、`g5_v99_rec_r1`、`parse_v99_rec_log_v1`、`extract_v99_from_logs_v1` | v99 的「来源链」只能读仓库里已恢复的 `results/pilot-v1/saturn-v99/raw/recovered-20261001/`，无法再生成 |
| 3 | **SATURN 输出 adata 缺失** | 任意 SATURN 输出 `*.h5ad`（`results/` 下 `.h5ad` 数量 = 0） | `saturn_output_scores.py --adata` | SATURN 逐类得分无法从 adata 复算，只能读 confusion 汇总 |
| 4 | **scVI 臂 obs 元数据缺失** | `results/phase-20261019/scvi-cross-species/obs.json`（目录里只有 `latent.npy`） | `compute_batch_metrics.py` 用于 scVI 臂 | 报告 §7.1 的 scVI batch-mixing 三指标（0.181 / 1.120 / 0.0039）本机不可复算 |
| 5 | **稳定性臂压缩预测被裁掉** | `results/stability-20261030/runs/seed-*/predictions/*.json.gz`（现存为 `.json`） | `pairwise_significance.py`、`saturn_vs_scvi_paired.py` | 依赖 `.json.gz` 的配对检验直接 `FileNotFoundError` |
| 6 | **学校模板 PPTX** | `课题5第03次汇报_三场景结论与可复现闭环.pptx`（`deliverables/` 与 `results/` 均无） | `build_report_v3/v4`、`build_story_deck_school_template`、`build_speaker_notes_docx`、`strip_report_ordinal`、`add_report02_notes` | 汇报 PPT 无法从源重建，只能改现成文件 |
| 7 | **汇报截图证据被删** | `results/stage-reports-20261102/render/v2/raw-*.png`（git 状态为 `D`） | `rebuild_deck_evidence.py`、`build_ppt_handoff_pack.py` | 「PPT 制作交接包」无法重建 |
| 8 | **DCS 任务记录** | `W202610050003104` / `W20261015…` / `W20261019…` / `W20261026…` 的任务日志与资源账单 | `resource_ledger.py`、`verify_dcs_recompute.py`、`build_report03_round3_pptx.py` | 资源/耗时/费用表无法复算，只能引用 `results/resource-20261030/resource_summary.json` |
| 9 | **v99 映射（平台版）** | `/Files/wheelhouse/v99_mapping_embedded.json`（38 条 dict） | `build_report03_round3_pptx`、`dcs_provenance_v99`（`V99_MAPPING_JSON`） | 平台侧映射与仓库 `config/v1 tsv` **不是同一物**，跨环境数字对不上时无法溯源 |
| 10 | **容器化验证链** | `docker build` 的 `g5-opca-container` 镜像（本机无 GPU、无 WSL、无 docker） | `image_selfcheck.py`、`container/Dockerfile` | 「镜像内 6 个冻结值逐位复现」这条**不可在本机重跑**，只能引用历史任务回显 |

补充断点（工程性，不是数据缺失）：

- **38 个脚本把仓库根硬编码成 `D:\projects\course5-prep`**（`mapping_v2_sensitivity.py:20`、`orhters_variant_impact.py:20`、`unified_coarse_macro_f1.py:15`、`pairwise_*`、`drop_unmapped_audit`、`labelspace_ablation`、`region_breakdown`…）。换机器/换用户名即失效，是「一键复现」最大的移植障碍。`reproduce_all.py` 已用运行期重定向绕开，但源头应改成 `Path(__file__).resolve().parents[1]`。
- **`requirements.txt` 与实际环境不一致**：仓库 pin 的是 `numpy==2.4.3 / scipy==1.17.0 / scikit-learn==1.8.0`，而实际能跑通的 `.venv39` 是 `numpy 1.23.5 / scipy 1.12.0 / pandas 2.3.3 / sklearn 1.6.1`。按 `requirements.txt` 装不出可复现环境。
- **4 个脚本的同目录导入在「从仓库根调用」时失败**：`local_readiness.py`、`team_budget_check.py`（`from budget_check import …`）。需 `scripts/` 进 `sys.path`，或用 `python -m` 方式。
- **2 个脚本产物文件名与映射无关**：`saturn_convention_audit_v2.py` 的 `OUT` 固定为 `saturn_convention_v2.json`，而仓库另有 `saturn_convention_mapv2.json`（手工改名产物），**无脚本可复现该文件名**——一次改名即断链。