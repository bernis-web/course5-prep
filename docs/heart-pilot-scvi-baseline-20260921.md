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

## 三物种补全（2026-09-21 深夜，v16/v17）

| 物种 | 细胞数 | KNN 准确率 | 耗时 | 任务 |
|---|---|---|---|---|
| Homo_sapiens（人） | 30,000 | **0.9838** | 68.4s | g3-scvi-baseline-v11-cpu |
| Mus_musculus（小鼠） | 60,471 | **0.9812** | 128.9s | g5-scvi-mouse-v16 |
| Danio_rerio（斑马鱼） | 50,000 | **0.9251** | 275.2s | g5-scvi-zebrafish-v17 |

统一协议：scvi-tools 1.1.6.post2（SCVI n_latent=10，max_epochs=5，early_stopping，CPU）；batch_key 人=donor/鼠鱼=orig.ident（G1 映射）；labels_key=celltype（金标准）；HVG 2000；KNN15，20% 留出集（stratify，seed=0）。全部 32c128g CPU 档离线任务，输出原文见工作区 scvi_v1{1,6,7}_out.txt。

**观察**：哺乳类两物种 ≈98%；斑马鱼低 ~6 个点（92.51%）——与该数据红细胞占比高（11,717/50,000）、细胞类型谱更杂一致；亦不排除演化距离影响（正式报告讨论点）。SATURN/SAMap 数字待环境就绪后按同协议补齐。
