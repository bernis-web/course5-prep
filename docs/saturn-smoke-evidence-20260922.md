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

## 真实数据预处理成功（2026-09-24 凌晨）

- **hm 任务（09-23 12:01–12:08，1c4g，Completed）**：人/鼠 ESM2 嵌入分片合并校验通过——human_embedding.torch 410,886,729 B（19,790 键）、mouse_embedding.torch 463,508,361 B（22,324 键），样本 A1BG → float32 tensor(5120)。
- **final/v56 失败根因（09-23）**：prep_real.py 路径写错 `/data/work/wh_all/…`（实际无 wh_all 子目录）→ FileNotFoundError 17 秒退；v56 是 shell `mv *.bin` 无匹配即断（分片实为 .txt 名）。
- **v60 预处理（09-24 00:42–00:43，1c4g，89 秒）**：backed 读 + 匹配 ESM2 键 + varm["X_protein_embedding"]（float32）+ cell_type/donor|orig.ident 映射 + 分层下采样 3000/物种（seed 0）。
  - human：32,732 基因 → 19,302 匹配；3,169 细胞 × 12 cell types（全量版另存 *_saturn_input_full.h5ad）
  - mouse：32,379 → 18,703 匹配；3,164 细胞 × 12 cell types
  - in_data_real.csv（species,path,embedding_path 三列）就绪
- **v61 SATURN 真实训练（09-24 00:53 提交，1c4g）**：烟测配方 + hv_genes 500 / num_macrogenes 16，CUDA 补丁幂等自愈，输出 saturn_real_v61_out.txt。
- 运维备忘：/data/work 跨任务持久（jdfsms1，75T 可用）；离线子任务日志可 API 读（POST /offline/subTask/logs/<子任务taskId>）；RawData 三物种 h5ad 路径 /Files/RawData/{Homo_sapiens,Mus_musculus,Danio_rerio}_sc.h5ad；v57（32c128g）提交 24h 仍 Submitted 未调度，待观察。

## 首个真实数据 SATURN 训练完成（2026-09-24 凌晨）

- **v62 人+鼠真实训练（01:14–01:54，1c4g，40 分钟，Completed）**：3,169 人 + 3,164 鼠心脏细胞 × 真实 ESM2 嵌入，50 epochs loss 0.094→0.0925 正常收敛，每轮 24-29 万 mined triplets。四产物落盘 `saturn_out_real/saturn_results/test256_data_*`（Final AnnData / triplets / epoch_scores / celltype_id pkl）。要点：train-saturn.py 在 saturn-src 的嵌套子目录（用 find 定位）。
- **v63 斑马鱼预处理（01:25 提交，Completed）**：6 个 .txt 分片容器内合并=537,414,921 B（与本地 md5 校验总量一致）；25,881 嵌入键，27,661 基因中 **24,007 匹配（87%）**，下采样 3,170 细胞 × 14 cell types。斑马鱼分片上传结论：`.bin` 后缀触发内容检测（60030），改 `.txt` 上传+容器内去后缀，6/6 全部 200。
- **v64 三物种训练（02:13 提交）**：in_data_real3.csv（human/mouse/zebrafish，9,503 细胞），参数同 v62。
- **v65 评估（02:15 提交，排在 v64 后）**：从 v62 Final AnnData 做 KNN15 距离加权跨物种标签迁移（human→mouse / mouse→human 双向），同时探测 AnnData 结构。
- 三物种预处理汇总：human 3,169×19,302（12 类）/ mouse 3,164×18,703（12 类）/ zebrafish 3,170×24,007（14 类），分层下采样 3000/物种 seed=0，全量版另存 *_saturn_input_full.h5ad。

## OOM 取证与 1c4g 瘦身方案（2026-09-24 凌晨后半）

- **平台调度现状**：仅 1c4g 档正常调度（秒级）；8c32g 实测 35 分钟不动，32c128g 卡 24h+。取消接口从前端包挖出：`POST /offline/subTask/cancel/<子任务taskId>`（还有 resume/delete/batchDelete）。已取消 v57/v68/v69（Aborted）。
- **v64 OOM（RC=137，83 秒）**：SATURN prep 把全部基因嵌入堆成 n_genes×5120 矩阵，三物种 1.23GB，叠加嵌入字典 1.41GB + h5ad 超 4GB。
- **v67 评估（v62 产物）**：Final AnnData 结构 = cells×256 + obsm['macrogenes']（16 维）+ obs(labels/labels2/ref_labels/species)；ref_labels=细胞自身类型（验证用），labels=整数类 id。真值需按条码从输入 h5ad 回连。**16 macrogenes 潜空间太弱**：KNN15 跨物种迁移 human→mouse 仅 3.4%、mouse→human 17.1%。为复现 v71 方案，后续对照暂固定 1000 macrogenes（与 SATURN 论文默认配置一致）；这不是“1000 必然最优”或容量因果已证实的结论，容量效应需单独消融。
- **v70 教训**：截断嵌入+1500 细胞/物种仍 5 分钟 OOM——嵌入矩阵与宏基因数无关，n_genes×5120 才是主导项。
- **v71 方案（运行中）**：每物种 seurat-flavor HVG top-2500 预切基因宇宙（log1p 后选 HVG，原始计数子集保存），嵌入矩阵 3×2500×5120≈154MB，宏基因 1000、hv 2000。文档化偏离：基因宇宙=每物种 HVG 候选集，SATURN 内部再选 2000 HVG。

## 三物种 SATURN 运行与探索性迁移结果（2026-09-24 早晨，v71/v72）

**训练**（v71，1c4g，04:26–06:19，113 分钟）：1528 人 + 1535 鼠 + 1543 斑马鱼心脏细胞 × 每物种 2500 HVG 候选集，真实 ESM2 嵌入（截断到匹配基因），1000 macrogenes，hv 2000，50 epochs loss 收敛至 ~0.07-0.08，mined triplets 1-1.8 万/轮。产物：`saturn_out_real3_h/saturn_results/`（Final AnnData 4606×1000 obsm['macrogenes'] + triplets + epoch_scores + celltype_id）。

**评估**（v72，KNN15 距离加权，真值按条码回连，lat=1000 维 macrogene 潜空间）：

| 方向 | 准确率 |
|---|---|
| human → mouse | **56.68%** |
| mouse → human | 18.46% |
| mouse → zebrafish | 20.93% |
| human → zebrafish | 11.54% |
| zebrafish → mouse | 6.71% |
| zebrafish → human | 0.07% |

**与 16-macrogene 试点（v62）对比**：human→mouse 3.38%→56.68%（17×），mouse→human 17.1%→18.5%。

**解读**：数字受跨物种标签命名体系强约束（精确字符串匹配）。人→鼠高（56.7%）因两物种标签命名同源；斑马鱼→人近 0 因 14 类斑马鱼型名与人类型名几乎无精确重合。下一步做同源类型映射表（如斑马鱼 atrium/ventricle CM→Cardiomyocyte）并重新计算映射后指标；当时“预计全线大幅提升”只是待验证假设，不能作为结果性表述，后续 v73/v74b 的实测结果以映射表和 majority baseline 对照为准。已记录的方案性偏离：1500 细胞/物种、基因宇宙=每物种 2500 HVG 候选（平台仅 1c4g 可调度+4GB 内存约束所致，大规格恢复后可全基因重跑）。

## 映射后全量统计评估（2026-09-25 中午，v73/v74b，按 Claude 指挥单执行）

**映射表 v1**（config/heart-celltype-map-v1.tsv，38 行）：双层 coarse(9 类)/fine(17 类)，38 行全部带 evidence_source 与置信度；mouse/fish Proliferating、fish mt 标 unmapped（fine 层剔除计 coverage，coarse 层暂作 other 类参与）。数据只用于验证、不用于生成映射（防循环论证，冻结待 pseudobulk 核验后 commit hash+sha256）。

**三层 × 六方向 KNN15（1000d macrogene 潜空间，括号为 majority baseline）：**

| 方向 | exact | coarse | fine |
|---|---|---|---|
| human→mouse | 56.7% (45.3) | **67.4% (47.2)** | 57.8% (46.2) |
| mouse→human | 18.5% (25.3) | 24.4% (31.2) | 19.3% (25.3) |
| mouse→zebrafish | 20.9% (38.6) | 31.2% (38.6) | 22.7% (39.8) |
| human→zebrafish | 11.5% (38.6) | 17.9% (38.6) | 12.1% (39.8) |
| zebrafish→mouse | 6.7% (45.3) | 11.3% (47.2) | 7.1% (46.2) |
| zebrafish→human | 0.1% (25.3) | 0.2% (31.2) | 0.1% (25.3) |

**关键发现：**
1. **唯一显著超过 majority baseline 的方向是 human→mouse**（67.4% vs 47.2%，bootstrap 95% CI [64.9, 69.7]，shuffle p<0.005）。其余方向全部 ≤ 常数预测器。
2. **zebrafish→human 与随机不可区分**（shuffle p=0.15–0.75）——斑马鱼作为参考源时潜空间对哺乳动物无对齐信号。
3. human→zebrafish 显著低于 baseline（17.9% vs 38.6%）——模型把鱼细胞推向少数类，劣于全猜内皮。
4. k 敏感性（coarse h>m）：k3 55.1% / k5 63.1% / k15 67.4% / k30 67.0%，平台期稳定；m>h 随 k 上升到 32% 但仅贴平 baseline。
5. 硬约束下的合理解读：SATURN 的跨物种对齐在 1c4g-slim 条件（1500 细胞/物种 × 2500 HVG）下只在哺乳动物对内有真信号；鱼-兽之间当前配置失败是实证发现而非标签命名问题（映射已消除命名差异仍失败）。

**待办（Claude 派工）**：ortholog-PCA 零整合基线（MGI/ZFIN 下载后台重试中）；ESM2 行置换消融（需平台跑，待用户放行）；物种内 ceiling；seed×2 误差棒；映射冻结核验（pseudobulk Spearman）。

## ortholog-PCA 零整合基线（2026-09-25 下午，v75c/v78b，Claude 派工 P0）

**协议**：每方向取 1:1 直系同源基因（MGI 人鼠 17,611 组→配对 15,694 基因；ZFIN 人鱼 9,296、鼠鱼 8,138），两侧 log-norm 后合并、PCA50、同一 KNN15/同一映射表/同一 200 次置换协议。人工笔误备注：人 taxonomy 写成 9608 致 v75b/v78 hm=0，9606 修复后 v78b 通过。

**SATURN vs ortholog-PCA（coarse 层，括号内 exact）：**

| 方向 | SATURN | ortholog-PCA | 胜者 |
|---|---|---|---|
| human→mouse | 67.4% (56.7%) | **80.9% (76.1%)** | PCA |
| mouse→human | 24.4% (18.5%) | **38.3% (34.2%)** | PCA |
| human→zebrafish | 17.9% (11.5%) | **40.5% (40.8%)** | PCA |
| zebrafish→human | 0.2% (0.1%) | **11.9% (8.0%)** | PCA |
| mouse→zebrafish | **31.2% (20.9%)** | 22.4% (11.9%) | SATURN |
| zebrafish→mouse | 11.3% (6.7%) | **79.5% (68.7%)** | PCA |

**核心发现**：6 方向中 5 个方向，朴素 ortholog-PCA（零整合、仅 50 维）显著优于 SATURN（全部 shuffle_p<0.005 且超 majority baseline）。唯一 SATURN 胜的方向是 mouse→zebrafish。合理解读：在 1500 细胞/物种 × 2500 HVG × 50 epochs 的低算力条件下，SATURN 的蛋白嵌入宏基因 shortcut 反而破坏了直系同源基因本身携带的跨物种对齐信号；SATURN 的卖点是免 1:1 ortholog 策划，但本数据下该代价未被补偿。此对比存在一个已知框架性差异（PCA 用了更强的先验=策划好的 1:1 ortholog 集合），需在论文中如实陈述。

产物：/data/work/ortho_pca_v75c_out.txt、/data/work/ortho_hm_v78b_out.txt；ortholog 表 /Files/wheelhouse/orth-*.{rpt→txt}（注：平台保留 .rpt 原名文件内容异常，统一用 .txt 副本）。

## 消融 + 种子稳定性 + 物种内 ceiling（2026-09-25 晚，v79-v83）

**① 物种内 ceiling（SATURN 1000d 潜空间，50/50 split，KNN15）**：human 85.5% / mouse 93.5% / zebrafish 74.2%——均低于 scVI 基线（98.4/98.1/92.5），说明跨物种掉分里有潜空间质量本身的因素。

**② ESM2 行置换消融**（打乱基因-向量对应、保留真向量分布，其余协议与 v71 完全一致）：

| 方向 coarse | 真实嵌入 | 置换嵌入 |
|---|---|---|
| human→mouse | 67.4% | 20.4% |
| mouse→human | 24.4% | 10.0% |
| mouse→zebrafish | 31.2% | 29.3% |
| 其余鱼方向 | ~0-18% | ~10-12% |

结论：人鼠方向的 SATURN 增益确实来自真实蛋白同源信号（置换后崩到 20.4%，仍略高于随机因宏基因结构残差），不是单纯降维。鱼方向本来就没有信号，置换前后不变。

**③ seed 稳定性**（coarse，seed0/1/2）：
- human→mouse：67.4 / 71.5 / 62.3 → **67.1 ± 3.8**
- mouse→human：24.4 / 32.2 / 28.7 → 28.4 ± 3.2
- zebrafish→mouse：11.3 / **48.8** / 8.3 → 剧烈不稳定（seed1 异常跳高）
- zebrafish→human：0.2 / 26.4 / 0.2 → 同样双峰

新发现：鱼方向结果对 seed 强不稳定（双峰分布），低算力条件下该方法的鱼-兽对齐本身不可靠；人鼠方向相对稳。产物：/data/work/{saturn_out_real3_perm,saturn_out_real3_seed1,saturn_out_real3_seed2} + eval_final_v83_out.txt。

## SAMap 正式比对跑通（2026-09-26 凌晨，v86-v87c）

**技术路径**（完全绕过 BLAST 与代理依赖）：SAMap 1.0.16 API = `SAMAP(sams, gnnm=(同源邻接矩阵, 基因数组, 物种基因字典))`；用 MGI/ZFIN 1:1 ortholog 表直接构造同源图（hu_X↔ms_Y 边），联合 SAM 对象 `jsam.run()` 后 `obsm['X_pca']`（3063×150）即联合潜空间。注意点：species 列值带前缀（hu/ms）；ITER_DATA 是图矩阵不是嵌入；SVD 兜底会 OOM。容器内单对运行 ~1 分钟。

**人鼠结果（同协议：KNN15 精确匹配+置换检验）**：
- human→mouse：**1.95%**（majority 45.3%，shuffle_p=1.0，不优于随机）
- mouse→human：**17.2%**（majority 25.3%，shuffle_p=1.0，低于随机）

**三方法同协议对比（human→mouse 方向）**：ortholog-PCA 80.9% > SATURN 67.4% ≫ SAMap ~2%。

**解读与偏离声明**：SAMap 原生工作流输出基因映射分与簇对应，不是细胞级联合嵌入；本数字是"将 SAMap 联合空间用于细胞级标签迁移协议"的operationalization，需在论文中注明。即便如此，两个物种方向 shuffle_p=1.0 说明其联合空间在本数据规模下没有可用的跨物种细胞对齐信号——与 SATURN（有真信号但弱于朴素基线）形成方法学对比。鱼对（v88）运行中。

### 附：SAMap 鱼对状态（暂停，诊断存档）

v88b→v90 四轮：fish h5ad 无重复 var_names（ pseudobulk 的重复是 pandas 选列伪象）；修正 fh 映射方向（10398 对）；三物种全零基因过滤（human 16729/mouse 16992/fish 21659）。仍报 `inconsistent shapes` 于 `_get_pairs` 的 gnnm.multiply(W)——W 来自 samalg 内部基因权重向量，长度与我们的 gnnm 基因数不一致：samalg 在 prep 时自行做基因过滤，路径输入方式无法控制其基因集。**下一步（交接）**：改为预构建 `samalg.SAM` 对象（自己控制 N_genes/过滤后再传入 `SAMAP(sams={'hu': sam1, 'zf': sam2}, gnnm=...)`），或在 gnnm 构建前先跑一遍 SAM prep 读取其保留的基因列表。人鼠对（主线数字）不受影响。

### 附2：夜间攻坚补充（2026-09-26 上午，平台表单 API 404 中断处）

**三物种一体 SAMap 方案已完全设计好**（v91 设计 + v92/v93 源码侦查）：
- samalg 此版本无 `prep()`；预处理+特征选择都在 `SAM.run()` 内，**默认 n_genes=3000**（这就是 gnnm 形状不匹配的根因——SAMAP 拿 3000 入选基因与图求交）。
- SAMAP 对路径输入的标准预处理（源码 mapping.py L112-125）：`preprocess_data(sum_norm="cell_median", norm="log", thresh_low=0.0, thresh_high=0.96, min_expression=1)` + `run(preprocessing="StandardScaler", npcs=100, weight_PCs=False, k=20, n_genes=3000, weight_mode='rms')`；随后 `prepend_var_prefix` 就地加前缀、图与入选基因自动求交。
- 恢复执行步骤：按上述参数预构建三物种 SAM 对象 → 用 `s.adata.var_names`（run 后的实际基因集）构建 gnnm → `SAMAP(sams, keys, gnnm)` → run → `sm.samap.adata` 的 X_pca → 六方向评估（v91 脚本的后半段可复用）。
- 中断原因：平台新建任务表单依赖的接口持续 404（token 有效、offline/page 正常，仅表单初始化接口异常），v94 诊断任务无法提交。表单恢复后先提 v94（grep 'gene symbols match' + sed _get_pairs 源码）确认求交计数，再跑三物种版。

**当前已完成且不受影响**：SAMap 人鼠 1.9%/17.2%（三方法矩阵主列）、全部 SATURN/PCA/消融/seed/ceiling/冻结映射结论。

### 附3：三物种 SAMap 本地完成（2026-09-26，按 Claude 指挥本地化路线）

平台表单 404 期间转本地执行：py3.9 venv + 仓库 tarball（samap-1.0.16/sam-algorithm-1.0.2）+ hnswlib shim + harmonypy 0.0.9，全部依赖装通。细胞子集本地重生成并与平台 v73 清单**逐类型计数完全一致**（确定性等价）。**预构建 SAM 对象方案彻底解决形状不匹配**（SAMAP 源码证实其用 run(n_genes=3000) 的入选基因与图自动求交，此前失败是路径模式下 samalg 预处理对全零/低表达鱼的基因集过滤与我方 gnnm 不一致）。

**三物种一体 SAMap 六方向（本地，exact 层，括号 majority）**：

| 方向 | acc | majority |
|---|---|---|
| human→mouse | 1.95% | 45.3% |
| mouse→human | 17.2% | 25.3% |
| human→zebrafish | 0.0% | 38.6% |
| mouse→zebrafish | 38.6%(=majority) | 38.6% |
| zebrafish→human | 0.0% | 25.3% |
| zebrafish→mouse | 0.0% | 45.3% |

全部 shuffle_p≥0.31（多数 1.0）。**人鼠两方向与平台数字四位小数一致**（不同机器/不同基因宇宙/同细胞集 → 管线交叉验证通过）。

**SAMap 最终结论**：六个方向全部 ≤ 随机或等于 majority 常数预测器。本规模下 SAMap 联合空间无可用的跨物种细胞对齐信号。偏离声明：本地版用全基因宇宙（未做 ESM2 匹配预过滤），SAMap 联合空间评估为 operationalization（原生输出为基因映射分）。

三方法对比矩阵就此完整（六方向 × 四方法：SATURN / SAMap / ortholog-PCA / scVI物种内ceiling）。
