# 复现运行 20261111-215553

- python `3.9.6` @ `D:\projects\course5-prep\.venv39\Scripts\python.exe`
- git `codex/teacher-reply-report-prep` @ `d624917e51f1`（dirty=True）
- 耗时 278.5 s，步骤 30/30 通过

| 步 | 脚本 | rc | 秒 | 产物 (sha8) | 与仓库同名文件 |
|---|---|---|---|---|---|
| 01 | `environment_check.py` | 0 | 0.56 | `environment-report.json` `d633dd25` ≠ | |
| 02 | `plan_contract.py` | 0 | 0.23 | — | |
| 03 | `startup_preflight.py` | 0 | 0.21 | — | |
| 04 | `unified_coarse_macro_f1.py` | 0 | 0.3 | `unified-coarse-macro-f1.json` `9518d833` =逐字节<br>`run.log` `bf0dfb9a` =逐字节 | |
| 05 | `bootstrap_ci.py` | 0 | 23.66 | `bootstrap.json` `a2226a2e` =逐字节 | |
| 06 | `bootstrap_crossphylum.py` | 0 | 51.3 | `crossphylum.json` `13652c27` =逐字节 | |
| 07 | `saturn_convention_audit.py` | 0 | 0.11 | `saturn_convention.json` `e2333cd3` =逐字节 | |
| 08 | `saturn_convention_audit_v2.py` | 0 | 0.12 | `saturn_convention_v2.json` `e83b4607` =逐字节 | |
| 09 | `convention_variants.py` | 0 | 0.12 | `convention_variants.json` `c39ca5b2` =逐字节 | |
| 10 | `convention_flip_check.py` | 0 | 0.1 | — | |
| 11 | `mapping_v2_sensitivity.py` | 0 | 0.13 | `mapping_v2_sensitivity.json` `73b006e7` =逐字节 | |
| 12 | `orhters_variant_impact.py` | 0 | 0.11 | `orthers_variant_impact.json` `cbb2a80a` =逐字节 | |
| 13 | `convention_sensitivity.py` | 0 | 0.11 | `convention_sensitivity.json` `3fbf34a6` =逐字节<br>`convention_sensitivity.md` `fbf52001` =逐字节 | |
| 14 | `drop_unmapped_audit.py` | 0 | 0.14 | `drop_unmapped_audit.json` `4d9e24bb` =逐字节<br>`drop_unmapped_audit.md` `6ec4b899` =逐字节 | |
| 15 | `bootstrap_saturn_fixed.py` | 0 | 2.69 | `saturn_bootstrap_fixed.json` `cc43e61f` =逐字节 | |
| 16 | `bootstrap_saturn_fixed.py` | 0 | 2.79 | `saturn_bootstrap_fixed_mapv2.json` `71323844` =逐字节 | |
| 17 | `donor_bootstrap.py` | 0 | 14.53 | `donor_bootstrap.json` `aa389159` =逐字节<br>`donor_bootstrap.md` `5de61521` =逐字节 | |
| 18 | `opca_mapping_convention_audit.py` | 0 | 0.17 | `opca_mapping_convention_audit.json` `3660976c` =逐字节 | |
| 19 | `opca_mapping_v1_v2_audit.py` | 0 | 0.24 | `opca_v1_vs_v2.json` `f0bde001` =逐字节 | |
| 20 | `scvi_mapping_v1_v2_audit.py` | 0 | 0.17 | `scvi_v1_vs_v2.json` `ff8e2cb0` =逐字节 | |
| 21 | `labelspace_ablation.py` | 0 | 0.14 | `labelspace_ablation.json` `9f5af02f` =逐字节<br>`labelspace_ablation.md` `c45b6f0e` =逐字节 | |
| 22 | `region_breakdown.py` | 0 | 0.42 | `region_breakdown.json` `329290ce` =逐字节<br>`region_breakdown.md` `bf86b290` =逐字节 | |
| 23 | `ortholog_coverage.py` | 0 | 0.75 | `coverage.json` `d8df99f1` =逐字节<br>`coverage.md` `7cc374d3` =逐字节 | |
| 24 | `pairwise_corrected.py` | 0 | 40.01 | `pairwise_corrected.json` `c0a94808` =逐字节<br>`pairwise_corrected.md` `0705e434` =逐字节 | |
| 25 | `pairwise_donor_level.py` | 0 | 20.55 | `pairwise_donor_level.json` `fc1a2314` =逐字节<br>`pairwise_donor_level.md` `da2e9935` =逐字节 | |
| 26 | `pairwise_inductive.py` | 0 | 27.16 | `pairwise_inductive.json` `bd630258` =逐字节<br>`pairwise_inductive.md` `653d3a37` =逐字节 | |
| 27 | `pairwise_lr_evaluator.py` | 0 | 27.26 | `pairwise_lr_evaluator.json` `1d0b0652` =逐字节<br>`pairwise_lr_evaluator.md` `3830e4db` =逐字节 | |
| 28 | `pairwise_opca_official.py` | 0 | 26.51 | `opca_official_paired.json` `0cf7d972` =逐字节<br>`opca_official_paired.md` `6493d047` =逐字节 | |
| 29 | `compute_batch_metrics.py` | 0 | 3.53 | `batch_metrics.json` `1d094079` ≠ | |
| 30 | `heart_h5ad_inspect.py` | 0 | 3.16 | `h5ad-inspect.json` `d667c35e` ≠ | |

判据：rc=0 且产物 sha256 与仓库内同名文件一致（`=` 逐字节，`~` 去易变键后值相同）。
