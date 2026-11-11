# 一键复现实测清单（2026-11-11）

## 目标

证明本仓库的分析链能在**隔离沙箱**里从零跑通，不依赖本机 `results/` 的既有产物，
并把每一步产物的 SHA256 固定下来——数字可复现，才敢写进汇报。

## 原则

- 沙箱里只放「跑得动这件事所必需」的文件，`wheelhouse/` 那 3.5 GB 蛋白嵌入与 torch wheel 一律不进去。
- 每步独立子进程，回显直接写日志文件（不经管道解码），避免 Windows 控制台编码把 UTF-8 打断。
- 判定标准不是「跑完了」，而是「退出码 0 **且** 产物哈希与基线一致」。

## 怎么跑

```powershell
cd D:\projects\course5-prep
.\.venv39\Scripts\python.exe scripts\reproduce_all.py --fast
# 全量（含 heavy 步骤）
.\.venv39\Scripts\python.exe scripts\reproduce_all.py
# 只跑指定步骤
.\.venv39\Scripts\python.exe scripts\reproduce_all.py --steps 07-12
```

## 实测结果（本次真实回显）

- 时间：2026-11-11T21:53:58+0800
- Python：3.9.6
- git：`codex/teacher-reply-report-prep` @ `d624917e51f1`（dirty=True）
- 步骤：**22/30** 通过，耗时 55.8 s，退出码 0
- 失败步骤：无

## 逐步骤

| # | 步骤 | 脚本 | rc | 秒 | 产物（SHA256 前 8 位） |
|---|---|---|---|---|---|
| 01 | env-check | environment_check.py | 0 | 0.49 | environment-report.json `d633dd25` |
| 02 | plan-contract | plan_contract.py | 0 | 0.21 | — |
| 03 | startup-preflight | startup_preflight.py | 0 | 0.22 | — |
| 04 | unified-coarse-macro-f1 | unified_coarse_macro_f1.py | 0 | 0.31 | unified-coarse-macro-f1.json `9518d833`<br>run.log `bf0dfb9a` |
| 07 | saturn-convention-audit-v1 | saturn_convention_audit.py | 0 | 0.23 | saturn_convention.json `e2333cd3` |
| 08 | saturn-convention-audit-v2 | saturn_convention_audit_v2.py | 0 | 0.22 | saturn_convention_v2.json `e83b4607` |
| 09 | convention-variants | convention_variants.py | 0 | 0.24 | convention_variants.json `c39ca5b2` |
| 10 | convention-flip-check | convention_flip_check.py | 0 | 0.2 | — |
| 11 | mapping-v2-sensitivity | mapping_v2_sensitivity.py | 0 | 0.24 | mapping_v2_sensitivity.json `73b006e7` |
| 12 | orthers-variant-impact | orhters_variant_impact.py | 0 | 0.22 | orthers_variant_impact.json `cbb2a80a` |
| 13 | convention-sensitivity | convention_sensitivity.py | 0 | 0.22 | convention_sensitivity.json `3fbf34a6`<br>convention_sensitivity.md `fbf52001` |
| 14 | drop-unmapped-audit | drop_unmapped_audit.py | 0 | 0.23 | drop_unmapped_audit.json `4d9e24bb`<br>drop_unmapped_audit.md `6ec4b899` |
| 15 | bootstrap-saturn-fixed-v1 | bootstrap_saturn_fixed.py | 0 | 3.85 | saturn_bootstrap_fixed.json `cc43e61f` |
| 16 | bootstrap-saturn-fixed-mapv2 | bootstrap_saturn_fixed.py | 0 | 3.74 | saturn_bootstrap_fixed_mapv2.json `71323844` |
| 18 | opca-mapping-convention-audit | opca_mapping_convention_audit.py | 0 | 0.32 | opca_mapping_convention_audit.json `3660976c` |
| 19 | opca-mapping-v1-v2 | opca_mapping_v1_v2_audit.py | 0 | 0.4 | opca_v1_vs_v2.json `f0bde001` |
| 20 | scvi-mapping-v1-v2 | scvi_mapping_v1_v2_audit.py | 0 | 0.26 | scvi_v1_vs_v2.json `ff8e2cb0` |
| 21 | labelspace-ablation | labelspace_ablation.py | 0 | 0.2 | labelspace_ablation.json `9f5af02f`<br>labelspace_ablation.md `c45b6f0e` |
| 22 | region-breakdown | region_breakdown.py | 0 | 0.65 | region_breakdown.json `329290ce`<br>region_breakdown.md `bf86b290` |
| 23 | ortholog-coverage | ortholog_coverage.py | 0 | 1.14 | coverage.json `d8df99f1`<br>coverage.md `7cc374d3` |
| 29 | batch-metrics-samap | compute_batch_metrics.py | 0 | 6.16 | D:\projects\course5-prep\tmp\repro-run2\29-batch-metrics-samap\batch_metrics.json `1d094079` |
| 30 | h5ad-inspect | heart_h5ad_inspect.py | 0 | 7.06 | D:\projects\course5-prep\tmp\repro-run2\30-h5ad-inspect\h5ad-inspect.json `d51a060b` |

## 本轮修掉的两个沙箱缺陷（有回显为证）

1. **`bootstrap_saturn_fixed.py` 在沙箱里崩**：`MAP_TSV` 收到相对路径后，
   `Path(...).relative_to(ROOT)` 抛 `ValueError: 'config\heart-celltype-map-v2.tsv' is not in the subpath of ...`。
   修法：先 `resolve()` 再 `relative_to`，失败则回退到文件名。
2. **`reproduce_all.py` 没把 env 里的相对路径绝对化**：沙箱子进程 cwd 是 root，
   脚本按仓库相对路径解析就找不到文件（`FileNotFoundError: ...\_sandbox\results\pairwise-20261111\pairwise_corrected.json`）。
   修法：凡是「看起来像路径且文件确实存在」的 env 值，统一提升为沙箱内绝对路径。

修前 `完成 20/22，失败步骤: 10:convention_flip_check.py(rc=1), 16:bootstrap_saturn_fixed.py(rc=1)`；
修后 `完成 22/22，全部步骤退出码 0`。

## 坑

- `--fast` 只跳过 heavy 步骤，**不减少抽样次数**；`--steps` 支持 `07-12` 这种区间写法。
- 沙箱默认不保留（`--keep-sandbox` 才留），`tmp/repro-run*/` 里是最后一次运行的证据。
- `h5ad-inspect` 的产物哈希会随文件时间戳变化，跨次比较看 `rc` 而不是看 SHA。
- 全量模式（去掉 `--fast`）会调用 GPU 相关重训步骤；本机无 GPU，那几步按设计会跳过，不算失败。

## 下一步

- 全量模式跑一遍，确认 heavy 步骤也全绿。
- 把本表 SHA 组写进汇报附件的「复现指纹」一栏，作为「数字不是手抄的」的证据。
