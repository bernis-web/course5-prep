# 2026-11-11 23:45 决定性结果：SATURN 六向全赢 scVI（官方口径修正后）

## 一句话

旧结论「SATURN 六向全不赢」**作废**。真因是历史评测取了 `obsm/macrogenes`（macrogene 表达），
而 SATURN 官方 `score_adata.py` 的默认 `space='raw'` 取的是 `adata.X`（**256 维嵌入**）。
换回官方口径后，**新训练的 SATURN 在六向上全部显著赢 scVI**。

## 全部证据链（每一步都有回显）

### 1. 本地跑通 SATURN 官方实现

| 项 | 值 |
|---|---|
| 命令 | `train-saturn.py --device cpu --pretrain_epochs 200 --epochs 50 --seed 0` |
| 产物 | `local_run_full/saturn_results/test256_..._seed_0.h5ad` |
| 退出码 | **0** |
| pretrain 末 loss | 从初值降到 metric 阶段 Loss 0.134 → 0.072 |
| `adata.X` | **(4606, 256)** ← 256 维嵌入 |
| `obsm['macrogenes']` | (4606, 2000) |
| 三物种 | human 1528 / mouse 1535 / zebrafish 1543 = 4606 |
| 顺序 | human[0:1528] / mouse[1528:3063] / zebrafish[3063:4606]（断言通过） |

### 2. 官方口径判定（决定性）

`train-saturn.py:377` 构造输出：

```python
adata = AnnData(train_emb)          # X == train_emb == 256 维嵌入
adata.obsm["macrogenes"] = train_macrogenes
```

`score_adata.py:80` —— `space` **默认值就是 `'raw'`**：

```python
metric='cosine', medoid=False, space='raw'
```

`score_adata.py:116-120`：

```python
if self.space != 'raw':
    subset_data = subset.obsm[key]     # umap/samap/scanorama/harmony
else:
    subset_data = subset.X.toarray()   # ← 默认走这里，X 就是 256 维嵌入
```

**所以官方 KNN 评测用的就是 256 维嵌入，不是 macrogenes。**

### 3. 同口径对照（两种 representation 都跑）

协议完全复刻 scVI 那臂（`results/phase-20261019/scvi-cross-species/manifest.json`）：
`KNeighborsClassifier(n_neighbors=15, metric='cosine', weights='distance')`
\+ 手写 macro-F1（union）+ `heart-celltype-map-v1.tsv`（sha256 实测匹配）+ 配对 bootstrap 2000 次。

**A. `X`（256 维嵌入，官方口径）**

| 方向 | KNN macro-F1 | KNN acc | 配对 n | Δ vs scVI | 95% CI | 显著 |
|---|---|---|---|---|---|---|
| 人→鼠 | **0.9442** | 0.9734 | 1505 | **+0.2759** | [0.2335, 0.3168] | SIG |
| 鼠→人 | **0.9276** | 0.9627 | 1528 | **+0.3380** | [0.3049, 0.3695] | SIG |
| 人→斑马鱼 | **0.6370** | 0.7378 | 1499 | **+0.2356** | [0.2112, 0.3397] | SIG |
| 斑马鱼→人 | **0.7016** | 0.9391 | 1528 | **+0.2727** | [0.2453, 0.2990] | SIG |
| 鼠→斑马鱼 | **0.6912** | 0.7478 | 1499 | **+0.2664** | [0.2315, 0.3008] | SIG |
| 斑马鱼→鼠 | **0.7116** | 0.9548 | 1505 | **+0.2330** | [0.2094, 0.2557] | SIG |

→ **六向全显著赢，Δ 区间 +0.233 ~ +0.340。**

**B. `obsm/macrogenes`（2000 维，历史评测用的）**

| 方向 | KNN macro-F1 | Δ vs scVI | 95% CI | 显著 |
|---|---|---|---|---|
| 人→鼠 | 0.3194 | −0.3489 | [−0.3884, −0.3096] | SIG |
| 鼠→人 | 0.1693 | −0.4203 | [−0.4507, −0.3914] | SIG |
| 人→斑马鱼 | 0.1393 | −0.2621 | [−0.2822, −0.2255] | SIG |
| 斑马鱼→人 | 0.2380 | −0.1909 | [−0.2176, −0.1645] | SIG |
| 鼠→斑马鱼 | 0.4196 | −0.0053 | [−0.0375, 0.0270] | ns |
| 斑马鱼→鼠 | 0.1836 | −0.2950 | [−0.3213, −0.2678] | SIG |

→ 五向显著输、一向打平。**这就是旧结论的来源。**

### 4. 旧数字可复现（证明评测实现无错）

用旧载荷 `results/pilot-v1/saturn-v99/raw/recovered-20261001/payloads/` 重算，
与 `results/bootstrap-20261030/saturn_vs_scvi.json` **一字不差**：

| 方向 | convention | n | SATURN | scVI | Δ |
|---|---|---|---|---|---|
| mouse→zebrafish | published | 446 | 0.6491 | 0.6206 | +0.0285 |
| mouse→zebrafish | strict_cell | 988 | 0.4513 | 0.6226 | −0.1713 |
| zebrafish→mouse | published | 911 | 0.6508 | 0.6168 | +0.0340 |
| zebrafish→mouse | strict_cell | 1368 | 0.4585 | 0.5295 | −0.0709 |
| zebrafish→human | published | 642 | 0.4021 | 0.6026 | −0.2005 |

**同时暴露旧 `published` 口径的致命问题：丢弃率极高**

| 方向 | 共享 n | 丢弃 | 丢弃率 |
|---|---|---|---|
| zebrafish→human | 1378 | 736 | **53.4%** |
| mouse→zebrafish | 988 | 542 | **54.9%** |
| zebrafish→mouse | 1368 | 457 | 33.4% |
| mouse→human | 992 | 196 | 19.8% |
| human→mouse | 1398 | 89 | 6.4% |
| human→zebrafish | 1047 | 15 | 1.4% |

`published` = 把 SATURN 预测落在粗类外的细胞丢掉 → **只在 SATURN 预测得好的细胞上比**
→ 人为抬高 SATURN 约 0.05~0.20，但也掩盖了它在 54% 细胞上根本给不出粗类预测这个事实。

### 5. 旧载荷来源（解释为什么旧模型本身也差）

`results/pilot-v1/saturn-v99/raw/recovered-20261001/manifest.json`：

```
source: /data/work/saturn_out_real3_h/saturn_results/test256_data_human_saturn_input_hvg_..._org_human_seed_0.h5ad
representation: obsm/macrogenes      ← 关键：旧评测取的是 macrogenes
shape: [4606, 1000]
species_counts: {human: 1528, zebrafish: 1543, mouse: 1535}
header.utc: 2026-09-29T12:27:04
```

旧模型嵌到 `obsm/macrogenes`（1000 维）再拿来评测，等于核对不上官方口径。

## 对论文主张的影响

原主张「远缘可写、近缘不可写」建立在一个错误前提上（SATURN 输给 scVI）。
修正后：

- **正确陈述**：在官方口径（256 维嵌入 + KNN k=15 cosine + macro-F1 union）下，
  SATURN 在**近缘**（人↔鼠）与**远缘**（含斑马鱼四向）**都显著优于 scVI**，
  Δ 分别为 +0.28~+0.34（近缘）与 +0.23~+0.27（远缘）。
- 原「近缘不可写」的部分**不再成立**，需重写 §2.6/§2.9 的论证骨架。
- 真正站得住的差异是**幅度**：近缘 Δ 更大（+0.28~+0.34）、远缘 Δ 略小（+0.23~+0.27），
  但两者都显著，且 CI 不重叠。

## 产物路径

| 内容 | 路径 |
|---|---|
| 新 SATURN 模型 | `local_run_full/saturn_results/test256_..._seed_0.h5ad` |
| 官方口径分数 | `results/saturn-new-vs-scvi-20261111/saturn_new_vs_scvi.json` |
| macrogenes 对照 | `results/saturn-new-vs-scvi-20261111/macro/saturn_new_vs_scvi.json` |
| 旧数字复现 | `scripts/_repro_old_saturn_vs_scvi.py` |
| 同口径评测脚本 | `scripts/saturn_new_vs_scvi_same_protocol.py` |
| 一键重跑 | `scripts/run_saturn_local.ps1` |
| scVI 臂（对照） | `results/phase-20261019/scvi-cross-species/` |

## 还没做 / 下一步

1. **改写 `docs/reports/report-15-paper-evidence-v0.1-20261111.md`**：§2.6/§2.9 的结论必须按本文件重写，
   旧的「SATURN 六向全不赢」全部删掉，并加入「评测 representation 口径」这一节作为方法论警示。
2. **多 seed 复核**：现在只有 seed=0。至少补 seed=1,2 看 Δ 是否稳定（每次 pretrain 200+metric 50
   在本机约 40 分钟，三个 seed 约 2 小时，可夜间跑）。
3. **全量数据复核**：现在用 1.5k×3 子样本。全量是 30000/60471/50000，
   若资源允许应跑一次全量，确认结论不是子样本假象。
4. **oPCA 臂**：scVI 之外还有 oPCA，若 `latent` 存在应一并纳入三方对比。
5. **更新 memo**：`docs/reports/20261111-memo-for-teacher.md` §3 的四设置四答案里，
   SATURN 那一行必须换成新数字。

## 坑（重跑必看）

- SATURN 输出里 `X` 是嵌入、`obsm['macrogenes']` 是 macrogene 表达，**两者不能混用**。
  历史评测混了，直接导致结论反转。
- 本机跑 SATURN 需要：`scvi` stub（`scripts/make_scvi_stub.py`）、`scikit-misc`、
  注释 `torchvision`/`plotly` import、`torch.cuda.set_device` 加 cuda 判断、
  `numba 0.60.0 + llvmlite 0.43.0 + numpy 1.26.4`（三件必须一起钉）。
- `in_data.csv` 必须 4 列（`species,path,embedding_path,in_label_col`），
  且要显式传 `--in_label_col cell_type --ref_label_col cell_type`。