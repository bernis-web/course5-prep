# HEART pilot 首个数据点：scVI 基线（2026-09-21）

## 运行环境（平台记录）

- 任务：`g3-scvi-baseline-v11-cpu`（2026-09-21 18:23:01 提交，18:38:01 完成，32c 128g CPU，SATURN--22 镜像，cluster-st，课程方计费）
- 执行通道：公网离线任务（G3 批准方案；GPU 档任务 v10 提交 5 小时不调度，判定 GPU 离线任务当前不可用，按方案改 CPU 档）
- 数据：`/Files/RawData/Homo_sapiens_sc.h5ad`（30,000 细胞 × 32,732 基因，只读挂载，v9 实证可见）

## 方法

scvi-tools 1.1.6.post2（SCVI，n_latent=10，batch_key=donor[22 供体]，labels_key=celltype，max_epochs=5，early_stopping，CPU 模式）→ 潜空间 30,000×10 → train_test_split(80/20, stratify=celltype, seed=0) → KNeighborsClassifier(n_neighbors=15) 对金标准 celltype（12 类）预测。

## 结果（scvi_v11_out.txt 原文 JSON）

```json
{"scanpy": "1.10.3", "scvi": "1.1.6.post2", "numpy": "1.26.0", "shape": [30000, 32732], "latent": [30000, 10], "knn_acc": 0.9838, "elapsed_s": 68.4}
```

**KNN 细胞类型准确率 = 0.9838**（98.38%，20% 留出集）；全程 68.4 秒。

## 备注

- counts 层警告（数据自带层可能非原始计数）——不阻塞基线，正式评测前核对 X/counts 语义并在报告 methods 注明。
- GPU 型号取证维持三源证据（K8s 事件+购买页 3080Ti+官方 FAQ L4）；本任务 CPU 节点 nvidia-smi 不可用（gpu_v11.txt 未生成，符合预期）。
- 这是三方法 benchmark 的第一个数字：**scVI 基线 98.38%**。SATURN/SAMap 待自建镜像后补（方案 `docs/custom-image-plan-20260921.md`）。
