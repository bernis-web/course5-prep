# 2026-11-11 22:40 SATURN 官方实现本地端到端跑通

## 目标

平台离线任务自 17:46 起 4 小时零启动（Genpilot 在容器内实测：`find ... -newermt "2026-11-11 19:20"` 为空、`saturn_results/` 为空），
改用**本地 CPU 直接跑 SATURN 官方源码**，拿到产物。

## 结果（已验收）

| 项 | 值 |
|---|---|
| 最小验证（pretrain 1 / metric 1 epoch） | **exit 0，跑通** |
| 产物 | `local_run/saturn_results/test256_..._seed_0.h5ad` |
| 形状 | `(4606, 256)` —— X 即 256 维 SATURN 嵌入 |
| obsm | `macrogenes (4606, 2000)` |
| 三物种计数 | human 1528 / mouse 1535 / zebrafish 1543 = 4606 ✓ |
| 标签映射 | `celltype_id.pkl` 38 个 `species_celltype` → id |
| 打分链路 | `scripts/saturn_output_scores.py` 六方向分数已出（1 epoch，仅验管道） |
| 完整训练 | **已启动**：`local_run_full/`，pretrain 200 + metric 50，seed 0 |

## 一路上修的 6 个问题（全部有回显证据）

1. **缺 `scvi`**：SATURN `model/saturn_model.py:10` 只要 `ZeroInflatedNegativeBinomial`。
   完整 `scvi-tools` 装上了但 import 即崩（`mudata → anndata.AlignedViewMixin` 版本冲突），
   改走 **stub 方案**：`scripts/make_scvi_stub.py` 从 1.1.6 wheel 里精确切出
   `NegativeBinomial` + `ZeroInflatedNegativeBinomial` + `log_zinb_positive`/`log_nb_positive`/`_gamma`，
   只替换注解里的 `jnp.ndarray`，`settings` 用 `SimpleNamespace(warnings_stacklevel=2)`。
   **验证**：`ZINB log_prob = -2.4849`。
2. **`torchvision`**：`utils/transformations.py:4` 只有这一行 import、全文件未使用 → 注释掉。
3. **`plotly`**：`score_adata.py` 只服务 `plotly_scatter()` 可视化 → 改可选 import，降级为 `None`。
4. **硬编码 CUDA**：`train-saturn.py:1050` 无条件 `torch.cuda.set_device()`，CPU 版 torch 无 `_cuda_setDevice` → 加 `startswith("cuda")` 判断。
5. **numba/llvmlite 崩溃**：`llvmlite 0.39.1`（配 numba 0.56）+ numpy 1.26.4 → `_internal` 初始化失败。
   升到 `numba 0.60.0 + llvmlite 0.43.0`；**注意** `--force-reinstall` 会把 numpy 顶到 2.0.2，
   必须再钉回 `numpy==1.26.4`（否则 scipy 1.12 / samap 全坏）。
6. **`in_data.csv` 要 4 列**：`species,path,embedding_path,in_label_col`（我最初只写了前 3 列 → `KeyError: 'in_label_col'`）；
   另源码默认 `ref_label_col='CL_class_coarse'` 不存在 → 显式传 `--in_label_col cell_type --ref_label_col cell_type`。
   还缺 `scikit-misc`（`seurat_v3` HVG 需要 `skmisc.loess`）→ 已装 0.3.1。

## 可复现命令（POSIX 路径换成 Windows 反斜杠即可）

```powershell
cd D:\projects\course5-prep
$env:PYTHONPATH='D:\projects\course5-prep\wheelhouse\saturn-src'

# 1) 生成 scvi stub（只需跑一次）
.venv39\Scripts\python.exe scripts\make_scvi_stub.py

# 2) 最小验证（4 分钟级）
.venv39\Scripts\python.exe wheelhouse\saturn-src\train-saturn.py `
  --in_data local_saturn_in_data.csv --device cpu `
  --work_dir local_run --log_dir local_run\log `
  --embedding_model ESM2 --in_label_col cell_type --ref_label_col cell_type `
  --pretrain_epochs 1 --epochs 1

# 3) 打分
.venv39\Scripts\python.exe scripts\saturn_output_scores.py `
  --adata local_run\saturn_results\test256_..._seed_0.h5ad `
  --map config\heart-celltype-map-v2.tsv
```

## 环境事实（本机）

- CPU AMD Ryzen 7 8845H（8 核 16 线程），31.3 GB 内存，**无 GPU**，`torch 2.8.0+cpu`
- 1 epoch pretrain ≈ 12.79 s（1.5k 细胞 × 3 物种）
- `.venv39` = Python 3.9：numpy 1.26.4 / numba 0.60.0 / llvmlite 0.43.0 / scanpy 1.9.3 / anndata 0.10.9 / pandas 2.3.3

## 下一步

1. 等 `local_run_full` 跑完（pretrain 200 epoch ≈ 43 min 量级），对最终 `.h5ad` 重跑 `saturn_output_scores.py`；
2. 核对 `adata.X.shape[1] == 256`；
3. 把六方向分数并入 `docs/reports/report-15-paper-evidence-v0.1-20261111.md`，目标②闭环；
4. 4080 平台任务若恢复，可用同一套参数在容器内复跑做正对照。

## 坑（给别人省时间）

- **不要**装完整 `scvi-tools`：本机 anndata 0.10.9 与它的 `mudata` 依赖冲突，import 就崩。
- **不要** `pip install --force-reinstall numba` 而忘了钉 numpy——会把整个科学栈带崩。
- SATURN 输出的 `X` 就是嵌入，`obsm['macrogenes']` 是 macrogene 表达；打分脚本读 `X`。