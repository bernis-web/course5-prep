# GenPilot 咨询记录（2026-10-19）

> 咨询议题：scVI 臂完成后的三个技术问题 + 跨门数据可行性。
> GenPilot 会话经 DCS 顶部入口进入（`genpilot.dcs.cloud` 独立域名需单独登录）。

---

## 一、问题 1：删 pylibs 旧 anndata 是否有隐患

**GenPilot 答复要点**

- 删除是对的，隐患不在 `normalize_total` / `log1p` 本身；全流程已跑通就是最有力的证据。
- 要注意两点：
  1. anndata 0.10 收紧了**切片视图的就地写**语义。凡对 `adata[:, genes]` 这类切片直接改 `X`，先 `.copy()`。
  2. `pylibs_full` 里其他按旧 anndata 编译/编写的包（mudata / muon 及其依赖）可能藏着**第二个 `AlignedViewMixin` 式的不兼容**，只是还没触发。
- 建议留一道**冒烟脚本**固化验证：`import scvi / mudata / scanpy` + 跑一遍 mini 预处理管线。
- 后续若遇到怪错，优先把 **scanpy 升到 1.10.x** 配 anndata 0.10.8，而不是退回旧 anndata。

**本项目处置**：已新增 `scripts/smoke_test_env.py`，覆盖 5 个 import + normalize/log1p + 切片 `.copy()` + `scvi.setup_anndata`。AST 校验通过。

---

## 二、问题 2：基因轴不同怎么写才不算误导

**GenPilot 答复要点**

- 9,018 与 15,869/9,311/8,160 **不能放进同一张"基因数"表**，更不能并排，否则必被读成"scVI 信息量少"。
- 写法：在方法节**分别交代两次特征空间定义**——
  - scVI：共享 human 直系同源交集 9,018（模型架构要求跨物种基因一一对齐，取交集是保守标准做法）；
  - oPCA：每方向独立用该方向物种基因集，PCA 是各自 SVD，无需共享轴，保留物种特异信号。
- 结论里加一句"特征空间按方法学约束各自定义，非同一数量，不做横向比较"，把可比性限定在**输出层面**（F1、批混合、结构保持）。
- 把 macro-F1 的 `set(y_true)` vs 并集差异**合并进同一段"可比性声明"**，两个坑一起交代，报告更严谨。

**本项目处置**：已在 `docs/reports/scvi-cross-species-result-20261019.md` 新增 §5.0「可比性声明」，并把口径差异并入同一节。

---

## 三、问题 3：剩余缺口优先级

**GenPilot 答复**

1. **跨门第一**：课程硬性要求 + 单价低 + 复用现有 pipeline，属必修分。
2. **kBET / iLISI / silhouette 第二**：直接吃现成 scVI latent（无需重训），能显著加强"scVI 批次校正优于/区别于 oPCA"这条核心结论。
3. **文档与 Agent 友好度最后**，但别拖到截止；建议在跨门排队窗口期穿插写，优先补三样：可复现命令、环境修复记录（anndata 那个坑）、可比性声明。

---

## 四、跨门数据可行性核查（GenPilot 结论 + 本方复核）

### 4.1 GenPilot 检查 LBSPA.zip（只读，未解压）

- 全 zip 仅 **5 个条目**，3 个数据文件：`LBSPA/8CrossSpecies.rds`、`LBSPA/lamprey_sn_nodoublets.h5ad`、`LBSPA/lamrepy.3d.h5ad`；
- **无任何** ortholog / homolog / mapping / 1to1 命名的同源映射文件；
- 文件名层面无 cell_type 注释线索（h5ad 内部 obs 需解压才能确认）。
- **结论**：zip 与 `/Files` 里都没有现成的七鳃鳗↔小鼠直系同源表；建议自建（Ensembl Compara 的 lamprey↔mouse/human one-to-one），约 0 元、半天工作量，**不建议标 blocked**。

### 4.2 本方复核（补充 GenPilot 未掌握的事实）

| 项 | 实测 |
|---|---|
| `/Files/wheelhouse` | 只有 human/mouse/zebrafish 的同源表，**无 lamprey** |
| `/Files/lamprey/stage3-8` | 那套成果是 **Lrei vs Pmar 两个七鳃鳗物种**之间的比较（Lrei 4,699 核 vs Pmar 525 细胞），**不是**七鳃鳗↔小鼠；小鼠仅作 5-HT 描述参考 |
| `/Files` 根目录数据文件 | 只有 `local_human_s.h5ad` / `local_mouse_s.h5ad` / `local_zebrafish_s.h5ad`（**均为心脏**）+ 一个论文附表 zip；**没有小鼠脑数据** |

### 4.3 因此跨门的真实成本

GenPilot 最初估「0.2–0.5 元、换个物种对复用 pipeline」，这个估计**低估了**。实际需要：

1. 建立七鳃鳗↔小鼠直系同源表（Ensembl Compara，或从 `8CrossSpecies.rds` 反推）；
2. 找到并上传**小鼠脑**单细胞数据（平台上没有）；
3. 建立脑区/细胞类型的 coarse 标签映射表（心脏那张 `heart-celltype-map-v1.tsv` 不适用）；
4. 新写一个跨门脚本（不能直接复用心脏脚本的标签体系）；
5. 平台上传通道此前返回 60030，需走 GenPilot 容器 `dcs data push`。

**这不是「必修分顺手拿」，而是一个独立子项目。** 是否投入需用户裁定。
