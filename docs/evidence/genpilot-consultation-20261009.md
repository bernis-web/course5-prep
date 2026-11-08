# GenPilot 会商记录（2026-10-09，两轮）

> 方式：DCS Cloud → Genpilot（https://genpilot.dcs.cloud/?zone=st&projectId=P20260920085640327），对话区"我们课程项目"会话。
> 纪律：原答复要点照录；平台侧证据标注位置/ID；核不实的标"待核实"；**GenPilot 建议不替代本地 metrics、日志、源码、逐细胞预测或导师签认**。
> 时间：第一轮提问 18:27（北京时间，页面 time 标记），汇总回复 18:47；第二轮提问见 §2。

## 第一轮：平台事实核对（提问 18:27；深挖 18:27–18:46 后人工停止；汇总回复 18:47）

### ① 三份 h5ad 输入文件（结论 + 证据）

| 物种 | file id | 形状 | 关键字段 |
|---|---|---|---|
| human | `6ff9e0733a2b4b409afa49b29daad0fa` | 1528 × 19302（416MB） | obs：cell_type / celltype / **cell_or_nuclei** / modality / species 等；obsm：X_harmony / X_pca / X_umap；varm：X_protein_embedding |
| mouse | `2d1e6596a67344878ae7f4e5ecd65d8a` | 1535 × 18703（408MB） | obs：cell_type / celltype / species 等（同结构） |
| zebrafish | `2092aee8750247cf8389a4233734d5c3` | 1543 × 24007（507MB） | obs：同结构，另含 percent.mt |

- 存放位置：`/Files/ResultData/Notebook/`；md5 与 online 树一致。
- 证据：`dcs preview info` + `POST /api/data/file/meta/query`（本轮实查）。
- 平台侧核对结果：**与本地 pilot 子集（1528/1535/1543）完全一致** ✓

### ② SATURN--22 镜像（确认）

- 结论：`public-library/zhongliyuan_57362367597d49499e5bc388096a17f1_public:latest`（创建人 zhongliyuan，jupyter，公共库镜像）。
- 证据：`dcs image ls` 中 SATURN--22 行的镜像 URL 即该地址。
- 与工单修正后地址一致 ✓（此前 R1d 失败正是因用了 `docker.io/library/57362367597d49499e5bc388096a17f1:latest` 这一错误地址）

### ③ 资源档与单价

- 资源档：平台共 29 档（0.5c1g ～ 88c320g），含 GPU 档（3080Ti×1、L4×1）。
- 单价：**平台无公开计价接口 → 待核实（无公开接口）**。
- 实证反推：WDL 1c4Gi 档 16m24s 计费 0.18 元 ≈ **0.011 元/分钟·1c4Gi**（非官方单价）。
- 证据：`terminal_list_resources`、`dcs task ls` 费用列。

### ④ r1d 离线任务现状

- 状态：**失败**（finished=True，更新 10-09 15:41:59；任务 2106401728586420226，g5-v99-rec-r1d-1，4c16g，SATURN--22）。
- 失败原因：日志已清理（`dcs task log` 报"数据不存在"）→ **待核实**。
- 关键推断（GenPilot）：由"待分析"变为"失败"说明 **s 类离线队列至少已尝试调度过该任务**（此前 30+ 小时 Pending 的通道疑似已恢复）。
- 证据：`dcs task info`。

### ⑤ 结果回收通道

- **downloadFile 公网端点已可用**：`GET {base}/api/data/file/downloadFile?id={fileId}` 返回 200（实测脚本文件 16778 字节完整）；可作公网下载正式通道（此前该端点从公网 500，现恢复正常）。
- `dcs data push` 路径：本地文件须在 `/work/{user}/` 下，命令 `dcs data push <本地绝对路径> </Files/目标目录>`；异步上传；不支持 .py 扩展名（改 .txt）；目录需打包 tar.gz。
- 证据：本轮 HTTP 实测 + 多次 push 实测。

### ⑥ WDL 已花费汇总

- `dcs task ls`（w 类）共 10 条 runsamap：完成 1 条（0.18 元）+ 失败 9 条（0.95 元）= **总额 1.13 元**。
- 证据：`dcs task ls -o /work/user50719-8334/runsamap/tasklist.txt`（费用列逐条相加）。
- 注意：本地此前的"14 次失败"记录与平台 w 类 10 条不完全对应（部分失败可能未计费或属其它通道）——**待核实**（不改动任何历史记录）。

## 第一轮的过程说明（如实记录）

- GenPilot 首轮深挖 18 分钟仍未收尾（卡在计价端点探测，连续探测 8 个疑似端点均 404/无果）；按"卡住即停该分支"的纪律，执行者人工点击"停止生成"（页面显示"已处理 18m57s"），随后以补充消息要求"基于已有证据直接汇总，缺的标待核实"，26 秒后得到上述汇总。
- 因此：③单价与④失败原因两项为**待核实**，非平台确认结论。

## 第二轮：科学方案（提问 18:49）

内容（照录要点）：
1. 训练时目标标签是否参与（oPCA label-free / SATURN ref_labels / SAMap keys=cell_type）——请给平台侧脚本或 manifest 证据；
2. query 是否进入建图/拟合（transductive 本质），各方法哪一步用了 query 表达；
3. 是否具备合法 out-of-sample 投影接口（冻结表示/模型后仅投影新物种，不更新、不用其标签）——oPCA 固定 PCA 载荷 / SATURN 固定 macrogenes+权重 / SAMap 固定联合图，分别说明可执行性与改动点；
4. 泄漏防护：条码级隔离、标签隔离、投影后不回流——平台侧机制 vs 需自保证的部分；
5. 资源与成本：A 档（现有三物种单细胞子集小规模对照）与 B 档（留一物种×3 方法×3 seed×三层=81 格）的档位、时长、费用（按 0.011 元/分钟·1c4Gi 反推；GPU 档位名与经验时长）；
6. 做不到的部分请明确列出。



## 第二轮答复（18:49 提问 → 18:58 完成；7 步取证计划，逐条附脚本行号）

### 一、训练时目标标签是否参与（问题 1）

| 方法 | 结论 | 证据（GenPilot 平台侧实查） |
|---|---|---|
| ortholog-PCA | **label-free**（PCA 仅拟合表达矩阵；标签只在评估 KNN 用） | ortholog_pca_v98_final.py L118 `fit_transform(X)`；标签用于 L125-128 |
| SATURN | **无法确认**：ref_labels 是否参与取决于 `--use_ref_labels`，**默认 False**；历史训练命令未留档 | train-saturn.py L968 / L100-101（参数默认值）；训练任务 2102857229180948482 的完整命令行未找到 |
| SAMap | **label-aware**：keys=cell_type 参与联合图对齐（方法学固有监督锚点） | run_samap_compliant_v98_dcs.py L28 / L335 |

**⚠ 对本地材料的直接影响**：本地方法比较矩阵、汇报 3/5、Word 报告均标注"SATURN = label-aware（ref_labels 参与训练）"。
GenPilot 平台侧证据显示该结论**不可考**（flag 默认 False 且历史命令无留档）→ 需降级为"待核实"或补证（列入未关问题与 Claude 审阅重点）。

### 二、query 是否进入建图/拟合（问题 2）

- 三者**全部 transductive**：oPCA 合并矩阵一起 PCA；SATURN 三物种联合训练（输出 4,606 = 1528+1535+1543）；SAMap 联合图迭代（mapping.py `_concatenate_sam`）。
- 结论：现有 acc 不反映泛化能力（与本地口径一致 ✓）。

### 三、out-of-sample 投影接口（问题 3）

| 方法 | 可执行性 | 说明 |
|---|---|---|
| ortholog-PCA | ✅ 直接可行 | 固定 PCA 载荷 `transform` |
| SATURN | ⚠️ 需自写脚本 | 有 `get_all_embeddings`（model.eval + no_grad）但无现成 query-only 投影脚本 |
| SAMap | ❌ 无原生冻结图投影 | 只能"冻结同源图 + ref 锚点 KNN"近似，**需如实声明为近似** |

### 四、泄漏防护（问题 4）

- 现成机制：条码前缀隔离（`hu|`/`mo|`/`zf|` + assert_prefix_unique）、标签按物种 name_map 隔离、投影后不回流。
- 需脚本层自检：inductive 纪律（不回流、断言 query 不在训练 index）——平台无自动保障。

### 五、资源与成本（问题 5；按 0.011 元/分钟·1c4Gi 实测反推，非官方单价）

| 档 | 方法 | 时长 | 费用（估） |
|---|---|---|---|
| A（同批小规模） | oPCA | ~1h | ~0.66 元 |
| A | SAMap | ~50min | ~0.55 元 |
| A | SATURN | GPU 5-6h | **单价待核实**（无公开端点） |
| B（留一物种 81 格 = 27 次主运行） | oPCA | — | ~1.4 元 |
| B | SAMap | — | ~1.6 元 |
| B | SATURN | GPU ~18h（串行） | 单价待核实 |

### 六、做不到的部分（问题 6）

1. GPU 单价：平台无公开计价接口 → 待核实；
2. SAMap 无原生 inductive 投影（见问题 3）；
3. SATURN 的 query-only 投影需自写脚本；
4. SATURN `--use_ref_labels` 历史取值不可考。

### 产物（GenPilot 工作区）

- 主结果文档：「会商2科学方案」；另：执行计划与汇总、SAMap v98 产物目录、三方法在线证据树（均在 GenPilot 工作区，本地未复制）。

### 与本地口径的一致性核对

| 项 | 本地 | GenPilot | 判定 |
|---|---|---|---|
| 全部 transductive/in-sample | 是 | 确认（三者均 query 入图/拟合） | 一致 ✓ |
| oPCA label-free | 是 | 确认（L118/L125-128） | 一致 ✓ |
| SAMap label-aware | 是 | 确认（L28/L335） | 一致 ✓ |
| SATURN label-aware | 是（材料中已写） | **不可考（flag 默认 False，历史命令未留档）** | **冲突 → 待核实** ⚠ |
| r1d 通道恢复 | 待观察 | s 类队列已尝试调度（任务转为失败） | 新信息 |

## Claude 反方审阅（2026-10-09）与对会商结论的更正

> 完整审阅：docs/reports/claude-protocol-review-20261009.md（结论 revise；① 为阻塞项，已修正）

### 对 GenPilot 结论的两处更正（本地复核后）

1. **"SATURN 标签可见性不可考"过强**（会商问题 1 的 SATURN 行）：
   - 源码层面**可考**：`wheelhouse/saturn-src/train-saturn.py` 默认 `use_ref_labels=False`（L56/L100-103/L1025），
     `create_output_anndata()` **无条件**写出 `ref_labels` 列（L373-393）——"输出里有"不等于"训练用了"；
     `loss_and_miner_utils.py:283-441` 的 cross_species miner 用 **`labels`（细胞类型整数 id）** 构造正/负样本。
   - 且项目自身 2026-09-24 审计（docs/audit-and-next-round-20260924.md:108-114、199、214-215）已明确：
     "Final AnnData 含有 ref_labels 只能证明该字段被输出，不能证明它曾参与 miner"。
   - **正确表述**：SATURN = label-aware，但标签通道是 **`labels`**（非 `ref_labels`；`ref_labels` 仅为输出/评估真值）。
   - **真正不可核的**：v71/v99 运行时源码/镜像是否等于 checked-in 版本（长期未闭合）+ 训练命令行整体缺失
     （saturn-v99 恢复 manifest 的 candidate_hashes 只含 prep/eval 脚本，无训练命令）→ 标"待核实"。
2. **oPCA/SAMap 溯源错配**（会商问题 1/4 引用的脚本行号）：
   - oPCA 冻结数字的权威脚本是 `scripts/ortholog_pca_local_v1.py`（manifest script_sha256=6582d873…），
     **不是** `ortholog_pca_v98_final.py`（后者 L117 的 `fit_transform(X)` 中 X 为载入循环遗留变量，文件不自洽，不应作行号证据）；
   - SAMap 冻结数字来自 WDL 部署脚本 `samap_script.py`（script_sha256=c0f05b89…），**与 checked-in
     `run_samap_compliant_v98_dcs.py`（71dd08a3…）不是同一文件** → "keys=cell_type→label-aware"的证据来自
     checked-in 脚本，**线上运行脚本内容待回捞**。

### 其余采纳项（已落入三档方案 v2）

- SAMap 投影只能"近似 inductive"：C1 增设硬闸门（ref-only 图 membership 证明），C2 命名 **SAMap-approx**；
- 泄漏清单扩至 8 项（基因集/HVG/统计量范围/batch-供体/供体级隔离/标签物理剥离/seed 预注册/inductive 负控）；
- 费用算术改正（27 次 × 16 min ≈ 4.75 元，非 1.6 元）；0.011 元/分钟仅适用 1c4Gi WDL 档；GPU 总额上限待申请列明；
- 档名对齐（会商 B = 本方案 C2）；mapping v1 签认为 C 档硬前置；LOO 标注"跨物种级，非跨供体级"；
- 档 A 逐细胞核对显式排除 v97g；单细胞子集筛选改 n 的警示。
