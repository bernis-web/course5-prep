# SATURN 训练冒烟成功证据（2026-09-22 晚）

## 结果

任务 `g5-saturn-smoke-v54`（1c4g CPU，18 分钟）：SATURN（snap-stanford）在 DCS 离线通道内**完整训练跑通**——两物种假嵌入数据 300 细胞 × 200 基因，预训练+加权训练 50 epochs，loss 0.13→0.12 正常收敛，TRAIN_RC=0，四个结果文件落盘（Final AnnData / triplets csv / epoch scores csv / celltype_id pkl）。

## 最终可用配方（全部实测验证）

1. 源码：SATURN main 分支 tar（st-src-0922a.txt），解压后根=…/saturn-src（walk 找 train-saturn.py+model/）
2. **CUDA 补丁**：`torch.cuda.set_device(args.device_num)` → 条件化 `if args.device=='gpu'`（镜像/离线 CPU 节点无 NVIDIA 驱动，源码写死 CUDA 调用会崩）
3. 输入数据：**不是 h5ad 直接吃**，是物种清单 CSV（species/path/embedding_path 三列）；每物种 h5ad 需带 `varm["X_protein_embedding"]`（var 维度，不是 obsm）；var_names 必须与嵌入 .pt 的键对齐（ENSG id）
4. 嵌入 .pt：`{gene_symbol: torch.float32 tensor}`（float64 会 Double/Float 崩）；生成用 base64 管道写脚本（printf 吃缩进）
5. HVG seurat_v3 假均匀数据触发 loess 外插 bug → `--hv_span 1.0` + 泊松计数数据解决
6. 运行脚本：`python train-saturn.py --in_data in_data.csv --device cpu --org human --num_macrogenes 8 --hv_genes 50 --hv_span 1.0 --embedding_model ESM2 --in_label_col cell_type --ref_label_col cell_type --work_dir ... --log_dir ...`

## 换真实数据清单（下一步）

① 下载 SATURN 官方预计算基因嵌入（human/mouse/zebrafish ESM2 .pt，需代理）替换假 .pt ② 真实 h5ad 数据/Files/RawData（已在）③ 真实标签列映射（celltype）④ GPU 档任务跑正式训练（可选，CPU 小数据已证可跑）⑤ epoch_scores 收敛后取 Final AnnData 做基准评估。
