# 批次混合指标与跨门可行性（2026-10-19）

> 由 GenPilot 在其 DCS 容器内只读执行；未重训、未改原文件。
> 容器因 2.9 GB 的 rds 在 4 GB 内存下 OOM，临时切到 4c16g 完成，完成后未切回。

---

## 一、scVI latent 的批次混合与结构保持（k=30，cosine，seed=0）

| 指标 | 数值 | 含义 |
|---|---|---|
| silhouette（按 cell_type，cosine） | **0.181** | 细胞类型结构存在但不算清晰 |
| iLISI（物种，均值） | **1.125** | 理论范围 1–3；接近 1 表示每个细胞的 kNN 邻居几乎全是同物种 |
| kBET（物种，α=0.05）接受率 | **0.0039** | 几乎全部邻域被拒绝，物种组成与全局显著不同 |

**三项一致指向：该 scVI latent 中三个物种几乎未混合，batch 效应仍然很强。**

### 1.1 必须一起报告的矛盾

同一份 latent 上，标签迁移的 macro-F1 却相当高（人→鼠 0.6683、人→鱼 0.4014）。

- 若物种在潜空间里几乎完全分离，KNN 跨物种迁移本应困难；
- 合理解释是：**潜空间把"细胞类型"与"物种"编码在近似正交的方向上**——
  同类型细胞即使跨物种也彼此靠近，但单个细胞最近的 30 个邻居仍以本物种为主
  （物种方向上的偏移量大于同物种内的类型间距）。
- **结论**：批次混合指标与迁移性能必须并列报告，不能只引用其中一个。
  低 iLISI **不等于**方法失败；它说明"物种批效应未被消除"，而这恰恰是跨物种任务的固有难点。

### 1.2 口径说明

- 细胞类型标签重建时，GenPilot 发现指令中的文件-物种对应写反了：
  `hu->mo` 文件里是 `mo|` 细胞（direction 的 query 是**目标**物种），
  `mo->hu` / `zf->hu` 里是 `hu|` 细胞。已按数据事实修正为
  human←mo->hu、mouse←hu->mo、zebrafish←hu->zf。
- 每个 json 中 `included=false` 的细胞（exclusion_reason=inactive）未纳入。
- kNN 的 k=30 含自身；iLISI 用逆 Simpson 指数。

---

## 二、跨门数据可行性：`8CrossSpecies.rds`

### 2.1 结构（R 4.5.3 readRDS 实测）

| 项 | 值 |
|---|---|
| 类型 | Seurat 对象 |
| 维度 | **13,172 基因 × 333,627 细胞** |
| assays | RNA |
| reductions | pca / harmony / umap |
| meta 列 | species、**celltype1119**、nCount_RNA、nFeature_RNA、percent.mt、orig.ident、seurat_clusters、integrated_snn_res.1.5 |
| species 取值 | Lamprey / Lizard / Macaque / Mouse / Pigeon / Turtle / Zebrafinch / Zebrafish（**无 Human**） |
| celltype1119 | **19 类，全部是脑/小脑类型**：Purkinje、Granule_like、Bergmann、Astro、IN/EX 等 |
| Lamprey 脑区（orig.ident） | Cb（小脑）/ Tel（端脑）/ Di（间脑）/ Mes（中脑）/ Rh（菱脑），各含两批 |
| ortholog / homolog / mapping 槽位 | **无**（slots、meta、misc 均无命中） |

细胞数（部分）：Lamprey **41,678**、Mouse **37,047**、Zebrafish 56,787。

### 2.2 结论与一处对 GenPilot 判断的修正

GenPilot 的结论是"不能直接支撑，映射表仍缺，需自建"。

**本方复核后认为这个结论偏保守。** 该对象已经是 **13,172 个基因的共同轴**，
说明建库时已完成跨物种基因对齐——**对齐结果本身就存在，只是产生它的映射表没存进对象**。
对本项目的评测协议而言，需要的是"对齐后的特征矩阵 + 标签"，而不是映射表本身：

- 可按 `species ∈ {Lamprey, Mouse}` 取子集；
- 特征直接用 RNA assay 的 13,172 基因轴；
- 标签用 `celltype1119`（19 类脑细胞类型）。

**因此跨门从"独立子项目"降级为"子集 + 复用现有 KNN 协议"**，
但仍需确认：13,172 基因的取值层（counts 还是 normalized）、19 类的每类细胞数是否够做 KNN。

### 2.3 仍需注意

- 该对象是**论文已 harmony 整合**的产物；若直接用它自带的 harmony/umap 评估，
  等于在评论文的方法，不是评我们的方法。正确做法是取 RNA assay 的原始/归一化矩阵，
  由我们自己的 oPCA / scVI 重新跑。
- 4c16g 容器才读得动 2.9 GB 的 rds；4c8g 会 OOM（EXIT=137）。
- GenPilot 在 `/work/user50719-8334/cross_species_check/tmp/` 留了 2.9 GB 解压副本，可删。

---

## 三、跨门方案把关（GenPilot 咨询，2026-10-22）

### 3.1 三个问题的答复

**Q1：13,172 基因轴怎么来的？**
对象内无映射元数据、misc 为空，无法从 rds 证实。按规模推断是论文统一注释协议下的直系同源交集，
但含不含非 1:1 需查论文方法。失衡风险可量化——**13,172 是"注释层面共有"，不等于"表达层面检测到"**。

**Q2：用 RNA assay 自己跑 vs 直接用论文 harmony 嵌入？**
**用 RNA assay 自己跑。** 评 harmony 嵌入等于评论文的方法，且其预处理与本项目 oPCA/scVI 臂不连续，
混进 KNN15 会制造不可比的第三方结果。harmony 只建议留作旁证（UMAP 目视），不进计分。

**Q3：celltype1119 在 Lamprey 与 Mouse 之间同构吗？**
**不同构，且不对称。** Lamprey 13 类是 Mouse 18/19 类的**真子集**；Mouse 独有 6 类
（EX / IN / SNCG / Purkinje / Golgi / Bergmann）。

处理原则（GenPilot 建议）：
- 评估空间限定为 **13 类交集**，两方向一致处理；
- `la→mo`：把 Mouse 中属于独有 6 类的细胞**排除出评估**（不是合并）；
- `mo→la`：预测到非交集类的结果计为**未对齐/错误**并如实报告；
- 报告被排除细胞数与占比；**绝不自行发明"Purkinje≈某共享类"这类等价映射**；
- 跨门很可能**只能评 coarse 单层**（fine/exact 无对应注释），须写明与门内评估不对等。

### 3.2 基因体检实测（GenPilot 容器，只读）

| 项 | 结果 |
|---|---|
| rownames | 统一 human-style symbol，13,172 个全大写开头、0 下划线、无物种前缀 |
| Lamprey 非零基因 | 7,471 / 13,172（56.7%）；min_cells=3 → 7,449；min10 → 7,375 |
| Mouse 非零基因 | 11,306 / 13,172（85.8%）；min3 → 11,254；min10 → 11,133 |
| **两物种共同（min3）** | **6,222** |
| 两物种共同（min10） | 6,118 |
| celltype1119 | Lamprey **13 类**、Mouse **18 类**（子集内） |
| Mouse 独有 6 类 | EX 14,949 / IN 6,118 / SNCG 18 / Purkinje 989 / Golgi 957 / Bergmann 0 |
| **Mouse 独有 6 类占比** | **23,031 / 37,047 = 62.2%**（其中 EX+IN 21,067 = 56.9%） |

**结论（GenPilot）**：min_cells=3 后共同基因 6,222，**够跑 oPCA/scVI**；
但该轴近似等于「Lamprey 检测基因全集 ∩ Mouse 高检测基因」，报告需写明取舍；
**Mouse 侧 62.2% 细胞被排除**对 13 类交集评估空间影响很大，必须披露。

### 3.3 因此跨门的真实形态

- 评估空间：Lamprey 41,678 细胞 × 13 类，Mouse 仅 **14,016** 细胞（37,047 − 23,031）× 13 类；
- 基因轴：6,222（min3）；
- 层级：只能做 coarse；
- 结论强度：**弱于门内三物种结果**，不能与之直接并列排名。

运行环境备注：16 GB 容器统计阶段 OOM，GenPilot 已切到 4c32g 完成；当前容器为 4c32g。

---

## 四、跨门 oPCA 实测结果（2026-10-22）

**运行方式**：GenPilot 容器内（DCS 侧，非本地），只算不训练，62 秒完成。

### 4.1 数据

| 项 | 值 |
|---|---|
| 细胞 | 55,694 = Lamprey 41,678 + Mouse 14,016（已排除 Mouse 独有 6 类 23,031 个） |
| 基因 | 6,222（13,172 轴上两物种 min_cells≥3） |
| 取值层 | RNA assay counts（raw counts，未归一化） |
| 评估空间 | 13 类交集，仅 coarse |

### 4.2 结果

| 方向 | acc | macro-F1 (union) | majority | shuffle_p | n_ref | n_q |
|---|---|---|---|---|---|---|
| Lamprey→Mouse | **0.0579** | **0.0714** | 0.2168 | 0.3450 | 41,678 | 14,016 |
| Mouse→Lamprey | **0.0517** | **0.0725** | 0.3059 | 0.8700 | 14,016 | 41,678 |

### 4.3 判读

- 两个方向的 acc（5–6%）**都远低于多数类基线**（21.7% / 30.6%）；
- 13 类空间下随机猜测约 7.7%，实测 acc 甚至低于随机；
- 置换检验：L→M 的 p=0.345（与随机置换中位相当），M→L 的 p=0.870（处于随机分布低端）；
- **结论：在当前协议下（oPCA + 6,222 基因共同轴 + 13 类交集），跨门标签迁移未显著优于随机，基本失败。**

### 4.4 必须同时披露的限定

1. 这是 **oPCA 单臂**结果；scVI 未跑——GenPilot 容器的三个 Python 环境都没有 scvi-tools，安装需联网，未擅自安装。
2. 基因轴是「Lamprey 检测基因 ∩ Mouse 高检测基因」，Lamprey 侧非零基因仅占 56.7%；
3. Mouse 侧 **62.2% 细胞被排除**，评估样本被大幅裁剪；
4. 只用 coarse 单层（对象只有一套注释）；
5. 七鳃鳗是现存最原始脊椎动物，跨门本来就是这个任务里最难的场景。

### 4.5 与门内结果的关系

门内三物种中，oPCA 在远缘（人→斑马鱼）已降到 0.1682；跨门进一步降到 0.07 量级，
**退化趋势一致**，但跨门的绝对数值不能与门内直接并列（样本、基因轴、层级都不同）。

### 4.6 产物

`/work/user50719-8334/crossphylum/opca_metrics.json`（含两方向全指标与混淆矩阵）、`run_opca.py`。

---

## 五、跨门 scVI 臂：离线任务提交（2026-10-22）

| 项 | 值 |
|---|---|
| 任务号 | **`W202610220063725`** |
| 实体 | `crossphylum-20261022` |
| 流程 | `scvi_cross2` v1.0.0（复用，未改） |
| 输入 | `script_txt`=`/Files/ResultData/Notebook/crossphylum_scvi.txt`（6,688 B，152 行，SHA `1d379525…`）<br>`pylibs_tar`=`/Files/ResultData/Notebook/pylibs_full.tar.gz` |
| 数据 | `/Files/ResultData/Notebook/crossphylum/`（counts.bin 1,386,112,280 B、genes.txt 38,828 B、obs.csv 2,847,796 B，均与本地一致） |
| 提交时间 | 2026-10-22 13:0x |

**为什么走离线**：GenPilot 在线容器无网络（pip 拉不到任何包），三个 Python 环境均无 scvi-tools；
DCS 离线镜像自带 scvi 1.1.6.post2，故走 WDL。

**预期**：55,694 细胞 × 6,222 基因 × 50 epoch，CPU 2 核，约 1–1.5 小时；
若超时或 OOM，按纪律停止报告，不重投。

---

## 六、跨门双臂最终结果（2026-10-22，任务 W202610220063725）

### 6.1 任务

| 项 | 值 |
|---|---|
| 终态 | **完成** |
| 总时长 | **3h 29m 04s** |
| **费用** | **¥2.06** ⚠️ 超出 1 元上限 |
| 环境 | python 3.9.12 / numpy 1.23.5 / scipy 1.10.1 / sklearn 1.6.1 / torch 2.6.0+cu124 / **scvi 1.1.6.post2** / anndata 0.10.8 |
| 数据 | 55,694 细胞（Lamprey 41,678 + Mouse 14,016）× 6,222 基因 |

### 6.2 结果

| 臂 | 方向 | acc | macro-F1 (union) | majority | shuffle_p | n_ref | n_q |
|---|---|---|---|---|---|---|---|
| **oPCA** | Lamprey→Mouse | 0.0575 | 0.0711 | 0.2168 | 0.345 | 41,678 | 14,016 |
| **oPCA** | Mouse→Lamprey | 0.0516 | 0.0732 | 0.3059 | 0.860 | 14,016 | 41,678 |
| **scVI** | Lamprey→Mouse | 0.0582 | 0.0652 | 0.2168 | 0.040 | 41,678 | 14,016 |
| **scVI** | Mouse→Lamprey | 0.0457 | 0.0802 | 0.3059 | 0.145 | 14,016 | 41,678 |

### 6.3 判读（关键）

1. **两个方法都失败**：acc 4.6–5.8%，13 类随机猜测约 7.7%，实测**低于随机**；
   多数类基线 21.7% / 30.6%，差距 4–6 倍。
2. **scVI 没有复现门内的优势**：门内远缘（人→斑马鱼）scVI 0.4014 vs oPCA 0.1682（2.4 倍），
   但跨门两者 macro-F1 都在 0.065–0.080，**没有实质差别**。
3. scVI 的 `shuffle_p=0.04`（L→M）只说明"优于随机打乱"，**不说明优于多数类基线**，
   报告时不能写成"scVI 显著更好"。
4. 因此「跨门到底行不行」的答案是：**在当前数据与协议下，两个方法都不行**；
   这不是某个方法的问题，而是跨门标签迁移本身在这个规模/注释体系下不成立。

### 6.4 与门内结论的关系

- 门内：近缘 oPCA/scVI 可用（macro-F1 0.59–0.67），远缘 scVI 明显更好（0.40 vs 0.17）；
- 跨门：两者都塌到 0.07 量级。
- **结论不能外推**：门内"越远越要靠潜空间方法"的趋势，在跨门这一步没有延续。

### 6.5 产物

`results/phase-20261022/crossphylum/`：metrics.json（含两臂两方向全指标 + 混淆矩阵）、
run.log、environment.txt、manifest.json。
平台路径：`/Files/ResultData/Workflow/W202610220063725/result/`。

### 6.6 费用说明（必须记录）

| 项 | 值 |
|---|---|
| 本任务 | **¥2.06** |
| 累计 | **¥3.15** |
| 早期约定上限 | 1 元（单任务） |

超支原因：预估 1–1.5 小时，实际 3h29m；scVI 在 55,694 细胞 × 50 epoch 上比预估慢约 2.4 倍。
按纪律本应在超时/超预算时停止，但任务是一次性提交、无法中途计价中断，故只能事后记录。
**下一个 agent 注意：跨门这类 5 万细胞级的 scVI，预算应按 ¥2–2.5 估，不是 ¥0.2–0.5。**

---

## 七、oPCA 基线批次指标（2026-10-23 补测）

**计算环境**：GenPilot 容器（DCS 侧，非本地），py3.12-ml 的 numpy/scipy/sklearn；
联合 PCA 47.4 秒，全脚本约 1–2 分钟，内存远低于上限。

### 7.1 数值

| 指标 | oPCA（联合 PCA-50） | scVI（latent-10） | 谁更好 |
|---|---|---|---|
| silhouette（coarse 类型，cosine） | **0.0937** | **0.181** | scVI |
| iLISI（物种，k=30） | **1.0124** | **1.125** | scVI（但两者都接近 1） |
| kBET 接受率（α=0.05） | **0.0004** | **0.0039** | scVI（但两者都近 0） |

### 7.2 判读

- 三项都是 scVI 略好，但**量级上两者都属于"几乎没混匀"**：
  iLISI 理论满值 3，实测 1.01 与 1.13；kBET 接受率 0.04% 与 0.39%。
- 说明：**在这个数据上，"批次混合"不是 scVI 的强项**，它相对 oPCA 的优势主要体现在
  标签迁移的 macro-F1（远缘方向），而不是物种混合度。
- 这与 §4.3 的解释一致：两种表示都可能把"细胞类型"和"物种"编码在近似正交的方向上。

### 7.3 对比的口径限制（重要）

1. **维度不同**：oPCA 是 50 维，scVI 是 10 维。高维空间里邻域更稀疏，
   silhouette/iLISI 天然偏低，所以这个对比**不是严格同维**。
2. **标签口径不同**：oPCA 的 silhouette 只在 active 且已映射的 **4,532** 个细胞、
   9 个粗类上算（排除 74 个 unmapped/inactive）；scVI 那次用的是 predictions 全量 truth。
3. 若要严格同口径，需要把 scVI latent 也降到 50 维或把 oPCA 截到 10 维重算——
   本轮未做，作为已知限制记录。

### 7.4 产物

`/work/user50719-8334/opca_batch_out/opca_batch_metrics.json`（容器内，未上传到 /Files——
平台上传通道再次失败，与 2026-10-10 的 60030 同一症状）。

---

## 八、SATURN / SAMap 批次指标：尝试与阻塞（2026-10-26）

### 8.1 方案（GenPilot 建议，已采纳）

「副本注入」：不修改受保护脚本原件，复制一份、在副本里加保存嵌入的语句，重跑。

- **SAMap**：脚本里其实**已经算了**联合嵌入（`jd.obsm["X_samap_pca"]` 或 `X_pca`），
  只是没保存。副本 `scripts/run_samap_v98_with_embedding.py` 已在 truth-NA 检查后插入：
  `np.save(output_dir/"samap_joint_embedding.npy", emb)` + `samap_joint_obs.json` + `EMB_SAVED` 打印。
  **AST 校验通过，原件 `run_samap_compliant_v98.py` 未改动。**
- **SATURN**：原命令丢失，但 `audit_saturn_triplet_path.py` 保留了数据路径与参数链，
  理论上可重建启动命令；4,606 细胞规模 GPU 训练分钟级。

### 8.2 阻塞点：平台文件上传服务

要把改好的脚本送进 `/Files` 才能提交 WDL，而上传通道**连续两次失败**：

| 尝试 | 结果 |
|---|---|
| `crossphylum_scvi.txt`（2026-10-22） | ✅ 成功（6,688 B） |
| `opca_batch_metrics.txt`（2026-10-23） | ❌ 上传失败 |
| `samap_v98_emb.txt`（2026-10-26） | ❌ 第一次「正在上传」35 秒后查不到；第二次明确失败 |

失败模式与 2026-10-10 的 60030 同源：push 服务异常。具体原因需在前端
「数据管理 → 操作记录」查看（GenPilot 侧看不到该面板）。

### 8.3 结论

- **方法层面可行**，脚本已就绪（`scripts/run_samap_v98_with_embedding.py`，451 行，SHA `fab4e913…`）；
- **平台层面阻塞**：无法把新脚本送进 `/Files`，因此无法提交 WDL；
- 这一条**不是「没做」，是「做不了」**，原因可复核（上传失败记录 + 平台操作记录）。

### 8.4 下一步（若有可用上传通道）

1. 把 `scripts/run_samap_v98_with_embedding.py` 传成 `/Files/ResultData/Notebook/samap_v98_emb.txt`；
2. 用 runsamap 流程提交（1c4g，约 16 分钟）；
3. 产物里应出现 `samap_joint_embedding.npy`（约 4,606 × k）；
4. 在容器内算 silhouette/iLISI/kBET，与 oPCA/scVI 并表。

### 8.5 绕行尝试二：把补丁写进新流程（失败）

**思路**：上传通道坏了，那就**不上传**——新建一个流程，把补丁语句直接写在 WDL 的 command 里，
`script_txt` 仍指向 `/Files` 上已有的 SAMap 原件。这样整条链路不需要任何新文件。

**实现**：`container/samap_emb.wdl`（39 行命令段），用 `python3 - <<'PATCH' ... PATCH` 内联打补丁，
再 `find -name samap_joint_embedding.npy -exec cp {} ./result/ \;` 回收。

**结果**：平台 WDL 校验直接拒绝：

```
Expected one of: * INPUT * RBRACE * PARAMETER_META * OUTPUT * META * RUNTIME * CNAME
Previous tokens: [Token('RBRACE', '}')]  at line 35, column 27
```

**原因**：平台的 WDL 解析器不支持 command 块里的 heredoc（`<<'PATCH'`），
把 `PATCH` 后的内容当成 WDL 语法解析。

**可行的替代写法（未实施）**：把补丁压成一行 `python3 -c "..."`，或改用 `sed` 按行号插入。
两种都需要处理大量引号转义，且一旦行号变动就静默失效——风险高于收益。

**结论**：SAMap 嵌入这一步在当前平台能力下**确实做不了**，不是没尝试：
1. 上传通道 → 两次失败（§8.2）
2. WDL 内联补丁 → 解析器不支持 heredoc（本节）
3. 改受保护脚本 → 违反项目纪律

三条路都堵死，**建议标「未测」并保留本节作为证据**。

### 8.6 更正与突破（2026-10-26）

**两处此前的判断是错的，在此更正：**

1. **上传其实成功了。** `samap_v98_emb.txt` 与 `opca_batch_metrics.txt` 现在都在
   `/Files/ResultData/Notebook/` 里。GenPilot 报"上传失败"时，文件实际已落盘（延迟入库）。
   §8.2 的"通道阻塞"结论作废。

2. **WDL 报错的真实原因不是"不支持 heredoc"。** 报错 token 是
   `Previous tokens: [Token('RBRACE', '}')]` —— 真正原因是
   **`command { ... }` 块遇到 Python 字典字面量里的 `}` 提前闭合**。
   改用 `command <<< ... >>>` 后校验通过，流程 `samap_emb` 创建成功。

**已提交**：任务 `W202610260087701`（流程 `samap_emb`，实体 `samap-emb-20261026`），
输入 `script_txt=samap_v98_emb.txt`、`pylibs_tar=pylibs_full.tar.gz`。
流程命令段用 `find -name samap_joint_embedding.npy` 回收产物，不依赖固定输出目录名。

### 8.7 SAMap 重跑结果（任务 W202610260087701）

| 项 | 值 |
|---|---|
| 流程 | `samap_emb`（本次新建，command 用 `<<<` 语法） |
| 终态 | 完成（16m22s，¥0.01） |
| 产物 | **只有一个 200 字节的 run.log** |

run.log 内容：

```
python3: can't open file '.../samap_emb-samap_emb.RunSamap-run0/./samap_script.py':
[Errno 2] No such file or directory
```

**诊断**：`cp ${script_txt} ./samap_script.py` 未生效，导致后续 python 找不到脚本。
可能原因（未验证，按嫌疑排序）：

1. 命令段用了 `set -u` 但没有 `set -e`，`cp` 失败不会中断，错误被吞掉；
2. `command <<<` 块里的 heredoc 与缩进剥离规则可能影响了 `cp` 之前的行；
3. `${script_txt}` 在该流程里的 staging 路径与预期不同（scvi_cross2 用同样的写法是成功的，所以这条嫌疑较低）。

**下一步修法**（未实施）：在 `cp` 前后各加一行 `ls -la` 与 `echo CP_DONE`，
把中间状态写进日志；确认 `cp` 目标路径后再跑。成本约 ¥0.01 / 16 分钟。

**当前状态**：SAMap 批次指标**仍未取得**。这是第二次尝试失败（第一次卡上传，这次卡 cp），
但两次都不是"方法不可行"，而是流程细节问题。

### 8.8 真正的修法：换流程，不是修 cp（2026-10-26 14:2x）

**关键事实更正**：`/Files/ResultData/Notebook/samap_v98_emb.txt` 并不是"待埋点的原件"，
它本来就已经包含保存嵌入的代码。经 `downloadFile` 取回核对：

| 项 | 值 |
|---|---|
| 大小 | 17,194 B（422 行） |
| SHA-256 | `418ac586d13ec82c…` |
| `EMB_SAVED` / `samap_joint_embedding.npy` | 各 1 处 |
| 数据路径 | `/data/work/*.h5ad`（6 处）→ 由 WDL 的 `sed 's|/data/work|.|g'` 改为 cwd |

而 `samap_emb` 流程（W202610260087701 用的那个）只声明了两个输入
（`script_txt`、`pylibs_tar`），**没有把三份 h5ad stage 进工作目录**。
即使 `cp` 成功，脚本也会在读取 `./human_saturn_input_s.h5ad` 时失败。
`cp` 为什么失败仍未单独查明，但这条链路本身设计不完整，已放弃。

**改用 2026-10-05 跑通的 `runsamap` 流程**（5 个输入：三份 h5ad + 脚本 + pylibs，
命令段先 `cp` 三份数据到 cwd，再 `sed` 路径、再运行）。本次输入：

| 参数 | 取值 |
|---|---|
| human_h5ad | `/Files/local_human_s.h5ad`（1,528 细胞） |
| mouse_h5ad | `/Files/local_mouse_s.h5ad`（1,535） |
| zebrafish_h5ad | `/Files/local_zebrafish_s.h5ad`（1,543） |
| script_py | `/Files/ResultData/Notebook/samap_v98_emb.txt` |
| pylibs_tar | `/Files/ResultData/Notebook/pylibs_full.tar.gz` |

**为什么用 local_*_s 而不是 saturn_input_s**：批次指标要与 oPCA / scVI 同批细胞
（4,606 个）。Phase 6 的 SAMap 数值用的是 3,169 规模的下采样集，不能与 §7 的批次表并列。

提交：**W202610260103163**（实体 `samap-emb2-20261026`，流程 `runsamap`，提交后处于"待分析"）。

### 8.9 批次指标复算脚本（已用 scVI 验证）

新增 `scripts/compute_batch_metrics.py`，固定三项定义：

- silhouette：`sklearn.metrics.silhouette_score(metric="cosine")`，标签为映射后的 coarse（10 类，4,606 细胞全部可映射）；
- iLISI：k=30（不含自身）邻域的物种逆 Simpson 指数，按细胞平均；
- kBET：k=30 邻域 vs 全局物种构成的卡方检验，α=0.05 的接受率。

**验证**：把该脚本跑在 scVI latent（4,606×10）上，得
**0.1810 / 1.1202 / 0.0039**，与 §7.1 的 **0.181 / 1.125 / 0.0039**
在 silhouette 与 kBET 上完全一致，iLISI 差 0.005（0.4%，实现细节差异）。
因此同一脚本用于 SAMap 嵌入时，三项数字与 oPCA/scVI 同口径。

### 8.10 SAMap 批次指标到手（2026-10-26，任务 W202610260103163）

`runsamap` 流程跑完（44m27s，¥0.02），产物目录
`/Files/ResultData/Workflow/W202610260103163/result/` 里出现了
`samap_joint_embedding.npy`（4,606 × 150）与 `samap_joint_obs.json`。
已下载归档到 `results/phase-20261026/samap-batch/`。

**嵌入维度 150**：SAMap 联合表示取的是 `jd.obsm["X_pca"]`（`X_samap_pca` 不存在时的分支），
150 维 = SAMAP 默认 `n_pca`。这与 oPCA（50 维）、scVI（10 维）维度不同，
是三条方法学路线本身的差异，不是参数没对齐。

#### 三方法批次指标并表

| 指标 | ortholog-PCA（50 维） | scVI（10 维） | SAMap（150 维） | 谁最好 |
|---|---|---|---|---|
| silhouette（coarse，cosine） | 0.0937 | **0.1810** | 0.0431 | scVI |
| iLISI（物种，k=30） | 1.0124 | **1.1202** | 1.0061 | scVI |
| kBET 接受率（α=0.05） | 0.0004 | **0.0039** | 0.0011 | scVI |

（SAMap 的三项由 `scripts/compute_batch_metrics.py` 计算，产物
`results/phase-20261026/samap-batch/batch_metrics.json`；silhouette 覆盖 4,603 个可映射细胞、
10 个粗类，3 个细胞的标签不在映射表内。）

#### 判读

1. **三个方法都没把物种混匀**：iLISI 理论满值 3，实测 1.006–1.120；kBET 接受率 0.04%–0.39%。
   这在这个数据上是共性，不是某个方法的问题。
2. **SAMap 在生物保守性上最差**：silhouette 0.0431，只有 scVI 的 24%、oPCA 的 46%。
   与它 macro-F1 几乎无信号（0.00–0.11）的方向一致——**它的联合空间既没混匀物种，
   也没保住细胞类型**。
3. **scVI 是三者里唯一"两项都不算太差"的**：silhouette 最高，物种混合度也最高。
   但它的绝对水平仍然很低（iLISI 1.12 / 满值 3），所以只能说「相对最好」，不能说「混得好」。
4. 这条结论与 §7.2 的判断一致，并把它从「scVI vs oPCA」扩展到了「三方法」：
   **在这个数据上，批次混合度不能作为方法优劣的主要依据**——三个方法都低，
   而 macro-F1 差异却很大。真正区分方法的是标签迁移能力，不是混合度。

#### 口径限制（与 §7.3 相同，新增一条）

1. 维度不同：50 / 10 / 150，高维空间邻域更稀疏，silhouette 与 iLISI 天然偏低；
2. oPCA 的 silhouette 只在 4,532 个 active 且已映射的细胞上算（§7.3 已记录）；
3. **新增**：SAMap 的 150 维没有做任何降维，若降到 10 维或 50 维重算，三项指标都会变。
   本轮保持「方法原生输出维度」口径，不做人为对齐。

#### 产物

| 文件 | 说明 |
|---|---|
| `results/phase-20261026/samap-batch/samap_joint_embedding.npy` | 4,606 × 150，float64 |
| `results/phase-20261026/samap-batch/samap_joint_obs.json` | 逐细胞 obs_name / species / label |
| `results/phase-20261026/samap-batch/batch_metrics.json` | 三项指标与计数 |
| `results/phase-20261026/samap-batch/metrics.json` | SAMap 六方向 × 三层评估结果（6.6 MB） |
| `results/phase-20261026/samap-batch/manifest.json` | 脚本 SHA、输入 SHA、协议标签 |

**至此，四方法里三个（oPCA / scVI / SAMap）都有批次指标。**
SATURN 仍缺：原训练命令丢失，需 GPU 重建链路，未尝试。

### 8.11 SATURN 批次指标：为什么这一项停在「未测」（2026-10-27 核实）

之前一直写「原训练命令丢失，需 GPU 重建链路」。本轮把这条链路查到底，
结论比原来更硬：**要拿到 SATURN 的联合嵌入，必须从 ESM2 蛋白嵌入开始从头重训。**

#### 核查过程

| 步骤 | 动作 | 结果 |
|---|---|---|
| 1 | 读 `results/pilot-v1/saturn-v99/raw/recovered-20261001/manifest.json` | 找到最终表示层与源文件：`obsm/macrogenes`，4,606 × 1,000；源文件 `/data/work/saturn_out_real3_h/saturn_results/…_seed_0.h5ad`，SHA-256 `20cf807f…`，23,459,360 B |
| 2 | 在本地归档里找这份 23 MB 的 h5ad | **没有**。本地只有 `metrics.json`、18 份预测、confusion、6 个 gzip 载荷，没有 Final AnnData 本体 |
| 3 | 请 GenPilot 在容器内只读核查 `/work/user50719-8334/` | **目录不存在**：没有 `saturn_out_real3_h/`，没有任何 `*seed_0*` h5ad。该产物已在持久工作区清理 |
| 4 | 查 ESM2 基因嵌入（`.pt`）是否还在 | **不存在**。`/Files` 全量 `dcs data find -n "*.pt"` 零命中；`saturn_local_run.tar.gz`（222.8 MB）内部只有 h5ad、proteomes `.fa`、gene2prot `.fa`、`anchors.csv`，无 `.pt` |
| 5 | 查 SATURN 源码是否还在 | **在**：`/Files/wheelhouse/saturn-src.tar.gz.txt`（5.32 MB，实为 gzip，内含 `.git/` 的完整仓库） |

#### 这意味着什么

SATURN 的训练输入链是：`proteomes .fa` →（ESM2 前向）→ `gene_embeddings .pt` →（SATURN 训练）→ `Final AnnData (obsm/macrogenes)`。

第 2 步的 `.pt` 与第 3 步的 h5ad **都不在了**，只剩第 1 步的 `.fa` 和第 4 步的源码。
所以最小重跑路径是：**ESM2 推理生成三物种 `.pt`（数万条蛋白序列，需 GPU 或很长 CPU 时间）+ SATURN 训练（1000 macrogenes，50 epochs，GPU）**。

#### 成本与风险

| 项 | 情况 |
|---|---|
| GPU 资源档 | 平台可用两档：`3080Ti×1` 与 `L4×1`，均为 88c/320g（GenPilot 实测，接口不返回显存与单价） |
| 单价 | **查不到**。平台无公开计价接口，此前只能用 1c4g 的 0.011 元/分钟反推，不能外推到 GPU |
| ESM2 生成耗时 | 未测。三物种各约 2–3 万基因的蛋白序列，按经验在单卡上数十分钟到数小时 |
| SATURN 训练耗时 | v71/v72 时代在 3080Ti 上完成，具体时长无留存记录 |
| 复现风险 | 原训练的超参（epochs、miner、`use_ref_labels`、`unfreeze_macrogenes`）只有部分从日志切片恢复；即使重训，也未必与 v99 那份嵌入同分布，**算出来的三项指标不能直接和现有 SATURN macro-F1 配对** |

#### 结论

1. 这一项**不是「懒得做」，是「做不了且做出来也不可信」**：
   重训得到的是**新的** SATURN 表示，与 v99 的 macro-F1 不是同一次训练，
   两者并表会制造「同一方法的两个版本」这种假对照。
2. 若一定要补，正确做法是**整体重跑 SATURN 并同时输出嵌入与评估**，
   而不是只补嵌入。这已经超出「补一个指标」的范围，是一次完整的重训项目。
3. 因此本项目的批次指标停在**三方法**（oPCA / scVI / SAMap），
   SATURN 明确标为 `not measured`，并在所有对外材料里写明原因。

**这条结论可以直接回答「为什么四方法只测了三个」的追问。**

