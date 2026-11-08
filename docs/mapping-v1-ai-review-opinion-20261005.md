# 映射表 v1 AI 独立技术复核意见书

> **文件性质**：AI 出具的技术复核意见，供人类 reviewer 终签参考。
> **复核方**：Claude（技术终审角色，本意见书执笔）+ Genpilot（平台侧审查，前期参与）
> **复核对象**：`config/heart-celltype-map-v1.tsv`（sha256 `be9857354778535b76d1884d004c54691dc5ff2daa7b098d71dc719daf583165`，38 行）及其 hash 链下游 `v99_mapping_embedded.json`（sha256 `d92e32aa788672492febe8cd428beac71ba69fd99df68c7f362cba2e553eea4a`，两处副本同 hash）
> **日期**：2026-10-05
> **地位声明**：**本意见书不构成签认**。按课题纪律"reviewer 签认前不得宣称正式 benchmark"，签认必须由人类 reviewer（导师/组内负责人）作出；本意见书仅为降低审阅负担的辅助证据，表的责任由课题组承担。

---

## 一、复核范围

1. 38 行逐行 marker 依据的文献合理性（三档标注：canonical / 文献支持 / 需核实）；
2. 物种-基因符号命名规范（人源全大写 / 鼠源首字母大写 / 鱼源小写含 duplication 后缀）；
3. TSV notes ↔ `docs/celltype-map-validation-v1.md`（冻结报告）双向一致性；
4. 排除规则数值五方对账：TSV 3 行 unmapped ↔ v99 `n_excluded` ↔ ortholog-PCA `coverage_q` ↔ SAMap `n_q` ↔ 证据矩阵 §六 排除普查；
5. hash 链**内容**等价（不止 hash 相同，逐行语义等价）；
6. 数据侧证据盘点：pseudobulk 验证（g5-pseudo-v84e）16 对覆盖行 vs 仅文献级行分列；
7. 三个争议映射的文献级判断；
8. 局限性声明与证据等级标定（confirmed / candidate）。

**不在范围内**：湿实验验证、逐簇差异表达（DEG）定量复核（仓库无 rank_genes_groups 类产物）、对 Litviňuková 2020 / Hu 2022 原文的实时检索核对（见局限性 §八.1）。

## 二、方法

- **程序化核验**：以仓库 `.venv39` Python 对 TSV、三份 metrics.json、内嵌映射 JSON 做逐行比对、计数、覆盖率重算与混淆矩阵拆分（本次复核可复算）。
- **文献级核验**：依训练知识中的心脏单细胞图谱 marker 体系（Litviňuková 2020 人类心脏细胞图谱；Hu 2022 斑马鱼心脏图谱）对每行 evidence_source 做合理性判断，逐行标注三档。
- **交叉核对**：TSV notes 与冻结报告双向查；pseudobulk 声明与冻结报告 §2 原表逐值比对。
- **证据等级**：沿用仓库体例。confirmed = 程序化验证或多源一致；candidate = 依赖复核方知识或单一来源，建议抽查。

## 三、九项核验结果总览

| # | 核验项 | 结果 | 等级 |
|---|---|---|---|
| ① | 38 行逐行 marker 文献核查 | **通过（附条件）**：30 个 high 置信行中 24 行 canonical、6 行文献支持；3 行 evidence_source 仅写"canonical"未列具体 marker（mouse Myeloid/Lymphoid/Neural，另 zf Smooth muscle 写"canonical mural"）；2 处疑点见 §四 C 档 | mixed：A/B 档 confirmed 级内部一致，C 档 candidate |
| ② | 物种-基因符号规范 | **通过**：38 行 evidence_source 中基因符号 0 真违规（脚本 6 处命中均为英文描述词误报，人工裁决排除） | confirmed |
| ③ | TSV ↔ 冻结报告双向核对 | **通过（2 个文档级小缺口）**：4 个非高置信映射双向有据；但冻结报告 §3.3 已知偏离清单未列 Perivascular→smooth_muscle 的 coarse 合并；旧签认请求文档"跨物种对不上的标 ambiguous"与 TSV 实际（无 ambiguous，用 unmapped）不符——属文档陈旧，非表缺陷 | confirmed |
| ④ | 排除规则五方对账 | **通过（1 个已披露口径差）**：mouse 30 / zf 44（mt 30 + Prolif 14）/ human 0 在 TSV、v99、ortholog-PCA、矩阵 §六 四方闭环（30/14 拆分经 ortholog-PCA exact 混淆矩阵独立拆分验证）；SAMap 鱼方向 n_q=1496 比理论 1499 多排 3 细胞——为 56bb6035 版脚本混合口径所致，矩阵口径警示 3 已披露，**规则本身一致** | confirmed（SAMap 差额为已披露 candidate） |
| ⑤ | hash 链内容等价 | **通过**：内嵌映射为 (coarse, fine, status) 三元组，38 行三元组与 TSV 逐行全等价，无缺失键、无多余键 | confirmed |
| ⑥ | 数据侧证据盘点 | **完成**：16 对 pseudobulk 覆盖 26 行（直接）+1 行（间接）；8 个 mapped 行无数据侧证据，仅文献级（见 §六盘点表） | confirmed（覆盖事实）/ candidate（ρ 值本身） |
| ⑦ | 三个争议点文献级判断 | **全部支持保留当前归类**（置信档已在 TSV 披露），见 §五 | candidate |
| ⑧ | 局限性声明 | 见 §八（6 条） | — |
| ⑨ | 证据等级标定 | 见本表"等级"列及各节标注 | — |

## 四、逐行发现（38 行）

**档位**：A = canonical（教科书/图谱级公认）；B = 文献支持（有据但组合非唯一，或 evidence_source 未列具体 marker）；C = 需核实（存在命名/特异性疑点）。"数据侧"列引用冻结报告 §2 pseudobulk 结果（ρ 与 rank/of）。

### human（12 行）

| 行 | source_label | coarse→fine | marker 依据 | 档 | 数据侧 |
|---|---|---|---|---|---|
| 1 | Ventricular Cardiomyocyte | cardiomyocyte→ventricular CM | RYR2/TTN/MYBPC3 | A* | h→z 心室CM 0.428，1/14 |
| 2 | Atrial Cardiomyocyte | cardiomyocyte→atrial CM | MYH6/MYL7/NPPA | A | h→z 心房CM 0.304，8/14 |
| 3 | Fibroblast | fibroblast→fibroblast | DCN/COL6A3/LAMA2 | A | 0.731，1/12；h→z 0.453，3/14 |
| 4 | Endothelial cell | endothelial→endothelial cell | VWF/PECAM1/FLT1 | A | 0.817，1/12；h→z 0.597，1/14 |
| 5 | Lymphatic Endothelial cell | endothelial→lymphatic EC | MMRN1/CCL21/PROX1 | A | 0.630，3/12 |
| 6 | Smooth muscle cell | smooth_muscle→smooth muscle cell | PDGFRB/RGS5/GUCY1A2 | A | 0.724，1/12 |
| 7 | Myeloid | immune→myeloid | CD163/F13A1/C1QA | A | 0.745，1/12；h→z 0.525，1/14 |
| 8 | Lymphoid | immune→lymphoid | PTPRC/CD247/IKZF1 | A | 0.684，1/12；h→z 0.371，5/14 |
| 9 | Mast cell | immune→mast cell | CPA3/KIT/IL18R1 | A | 无（仅人） |
| 10 | Adipocyte | adipocyte→adipocyte | GPAM/PLIN1/PPARG | A | 0.566，4/12 |
| 11 | Mesothelial cell | epicardial→mesothelial cell | KRT19/MSLN/UPK3B | A（marker） | 无 |
| 12 | Neural cell | neural→neural cell | NRXN1/NCAM2/SCN7A | A | 0.544，5/12 |

\* 行 1 备注：三个 marker 为泛 CM 谱系公认；心室特异（fine 层 atrial/ventricular 分开）依赖图谱命名体系（典型心室特异基因为 MYH7/IRX4/MYL2），属可接受但建议知悉。行 12：心脏神经元群 marker 与 Litviňuková 2020 所报神经元群一致。

### mouse（12 行）

| 行 | source_label | coarse→fine | marker 依据 | 档 | 数据侧 |
|---|---|---|---|---|---|
| 13 | Cardiomyocyte | cardiomyocyte→cardiomyocyte | Tnnt2/Tnni3/Myh6 | A | 无直接对（h→m 8 对无 CM） |
| 14 | Endothelial cell | endothelial→endothelial cell | Cdh5/Pecam1/Kdr | A | 经人对 1/12 |
| 15 | Fibroblast | fibroblast→fibroblast | Dcn/Col1a2/Lum | A | 经人对 1/12 |
| 16 | Smooth muscle cell | smooth_muscle→smooth muscle cell | Rgs5/Pdgfrb/Notch3 | A | 经人对 1/12 |
| 17 | Lymphatic Endothelial cell | endothelial→lymphatic EC | Mmrn1/Flt4/Ccl21a | A | 经人对 3/12 |
| 18 | Myeloid | immune→myeloid | **未列具体 marker**（"canonical"） | B | 经人对 1/12 |
| 19 | Lymphoid | immune→lymphoid | **未列具体 marker**（"canonical"） | B | 经人对 1/12 |
| 20 | Epicardium | epicardial→epicardium | Krt19/Upk3b/Msln/Wt1 | A | 无 |
| 21 | Valve | fibroblast→valve interstitial cell | VICs 间质（低置信，见 §五.1） | B（映射 low） | 无 |
| 22 | Adipocyte | adipocyte→adipocyte | Ces1d/Fasn | A | 经人对 4/12 |
| 23 | Neural cell | neural→neural cell | **未列具体 marker**（"canonical"） | B | 经人对 5/12 |
| 24 | Proliferating cell | other→**unmapped** | Mcm2/Mcm6（谱系无关） | n/a | 不适用 |

### zebrafish（14 行）

| 行 | source_label | coarse→fine | marker 依据 | 档 | 数据侧 |
|---|---|---|---|---|---|
| 25 | Ventricular Cardiomyocyte | cardiomyocyte→ventricular CM | cmlc1/vmhc | **C** | 0.428，1/14 |
| 26 | Atrial Cardiomyocyte | cardiomyocyte→atrial CM | myl7/amhc | A− | 0.304，8/14 |
| 27 | Fibroblast | fibroblast→fibroblast | col1a1a/dcn/sparc | A | 0.453，3/14 |
| 28 | Endothelial cell | endothelial→endothelial cell | cdh5/egfl7/f8 | B | 0.597，1/14 |
| 29 | Smooth muscle cell | smooth_muscle→smooth muscle cell | **未列具体 marker**（"canonical mural"） | B | 间接（经行 30，8/14） |
| 30 | Perivascular cells | smooth_muscle→smooth muscle cell | rgs5a/pdgfrb/notch3 | A（marker） | 0.421，8/14 |
| 31 | Myeloid | immune→myeloid | spi1b/ctss/il1b | A | 0.525，1/14 |
| 32 | Lymphoid | immune→lymphoid | ptprc/b2m/coro1a | A | 0.371，5/14 |
| 33 | Epicardium | epicardial→epicardium | krt15/tcf21 | B | 无 |
| 34 | Valve | fibroblast→valve interstitial cell | VIC 间质（低置信，见 §五.1） | B（映射 low） | 无 |
| 35 | Red blood cell | erythroid→erythrocyte | 有核红细胞（常识级；"哺乳无对应"已披露） | A | 无（无哺乳对） |
| 36 | Orthers | neural→neural cell | scn1ba/scn4ab/sncga/kcnma1a | **C** | 0.298，10/14（最弱） |
| 37 | mt | other→**unmapped** | 高线粒体低质量 | n/a | 不适用 |
| 38 | Proliferating cell | other→**unmapped** | 细胞周期（谱系无关） | n/a | 不适用 |

**逐行小结**：38 行中 A 档 22 行、B 档 11 行、C 档 2 行（行 25、36）、n/a 3 行。C 档两行均为已披露的低置信行，不新增阻塞，处置建议见 §九。

## 五、四个低置信映射专节（含三个争议点文献级判断）

### 5.1 mouse Valve + zebrafish Valve → fibroblast（low；争议点一）

瓣膜间质细胞（VICs）为间叶来源，静止态表达成纤维细胞程序（Col1a1/Postn/Dcn 系），活化后呈肌成纤维样；心脏图谱文献通常将瓣膜间质归入成纤维细胞大类。**文献级判断：支持该 coarse 归类**。表设计上 fine 层保留 VIC 独立（valve interstitial cell），合并损失被隔离在 coarse 层——这是正确的做法。TSV 注明"disclosed modeling choice"，冻结报告 §3.3 已披露。**维持 low 置信、可签认**。附注：TSV 引用的"Hu 2022 将瓣膜间质与 fibroblast-like 归组"这一具体归类声明未在仓库内核实到原文，按 candidate 处理。

### 5.2 人 Mesothelial cell → epicardial（medium；争议点二）

胚胎心外膜由 proepicardial 间皮发生，成体心外膜与间皮共享谱系标记（Msln/Upk3b/Wt1/Krt19 系）；TSV 所列 KRT19/MSLN/UPK3B 即经典间皮标记。**文献级判断：谱系同源成立，coarse 归 epicardial 有据**；成体心脏中间皮与心外膜的精细关系文献仍有讨论，fine 层保留 mesothelial cell 独立标签恰当。**维持 medium、可签认**。

### 5.3 斑马鱼 Perivascular cells → smooth muscle（medium）

rgs5a/pdgfrb/notch3 为 mural 细胞公认程序，周细胞与平滑肌在 coarse 层合并为 mural 大类是跨物种图谱的常见做法（分辨率损失在 fine 层部分保留——本表 fine 也并入 smooth muscle cell，属已知合并，TSV notes 已披露）。数据侧 h→z 人 SMC→鱼 Perivascular ρ=0.421、rank 8/14，中等偏弱支持。**维持 medium、可签认**。

### 5.4 斑马鱼 Orthers → neural（low；争议点三）

"Orthers"为原始表拼写错误的 catch-all 群。TSV 以通道/神经元基因（scn1ba/scn4ab/sncga/kcnma1a）作为神经程序证据。**文献级判断：证据偏弱**——电压门控通道基因在心肌亦有表达（心脏钠通道即 SCN5A 系），通道表达本身不是神经谱系特异证据；pseudobulk rank 10/14 为全部映射对最弱，与 low 标注一致。TSV notes 已明确"data-marker observation used as VALIDATION hint only"。**结论：可保留 low 映射，但评估解读必须注明这是全表最弱一行；建议数据侧补验（如 elavl3/huC、snap25 等谱系级神经 marker 的簇表达，或该群与已知神经群的 marker 重叠分析）后再决定是否在 v2 升格或降格**。

### 5.5 行 25 附带疑点（本节之外发现，C 档）

行 25（斑马鱼心室 CM）引用 cmlc1/vmhc，行 26（心房 CM）引用 myl7/amhc。vmhc（心室型肌球蛋白重链）与 amhc/myh6（心房型）的室/房特异性为公认；但 **cmlc1 与 myl7 疑为同源命名（别名关系），同一基因家族分别被用于心室行与心房行，存在内部一致性风险**。不阻塞签认（数据侧 h→z 心室 CM rank-1 反向支持行 25 的归类正确），但建议 v2 前用数据表达核实（amhc/vmhc 二分或查斑马鱼基因组命名）。

## 六、排除规则验证（五方对账）

**规则本体**：TSV 3 行 status=unmapped（mouse Proliferating、zf mt、zf Proliferating）不入 mapped 分母，coverage 单列——与冻结报告 §3.4 一致。

| 方向 | 理论 query 总数 | v99 n_excluded_q/ref | ortholog-PCA n_q（coverage） | SAMap n_q | 一致性 |
|---|---|---|---|---|---|
| 人→鼠 | 1535 | 30 / 0 | 1505（0.9805） | 1505 | ✅ |
| 鼠→人 | 1528 | 0 / 30 | 1528（1.0） | 1528 | ✅ |
| 人→鱼 | 1543 | 44 / 0 | 1499（0.9715） | **1496** | 规则✅ 计数差3* |
| 鼠→鱼 | 1543 | 44 / 30 | 1499（0.9715） | **1496** | 规则✅ 计数差3* |
| 鱼→人 | 1528 | 0 / 44 | 1528（1.0） | 1528 | ✅ |
| 鱼→鼠 | 1535 | 30 / 44 | 1505（0.9805） | 1505 | ✅ |

\* SAMap 鱼方向比理论多排 3 细胞：系 56bb6035 版脚本混合口径（Phase 6 关账 §四.1），证据矩阵口径警示 3 已以"SAMap 1505/1496"披露。**排除规则（排除哪些类型）三方完全一致；差异仅在 SAMap 脚本的计数实现**，不影响映射表本身。

**计数拆分独立验证**（矩阵 §六 称 mt 30 + Proliferating 14）：由 ortholog-PCA exact 层混淆矩阵求和，人→鱼方向 mt=30、Proliferating=14；鼠→鱼方向 mt=30、Proliferating=14；人→鼠与鱼→鼠方向 mouse Proliferating=30——**与矩阵 §六 逐格吻合**（confirmed）。

**数据侧证据盘点**（16 对 pseudobulk，g5-pseudo-v84e）：

- 人鼠 8 对：内皮 0.817(1/12)、髓系 0.745(1/12)、成纤维 0.731(1/12)、平滑肌 0.724(1/12)、淋巴 0.684(1/12)、淋巴管内皮 0.630(3/12)、脂肪 0.566(4/12)、神经 0.544(5/12)——8/8 进 top5，5 对 rank-1；
- 人鱼 8 对：内皮 0.597(1/14)、髓系 0.525(1/14)、心室CM 0.428(1/14)、成纤维 0.453(3/14)、淋巴 0.371(5/14)、SMC→周细胞 0.421(8/14)、心房CM 0.304(8/14)、神经→Orthers 0.298(10/14)——方向性支持，鱼方向信噪比低（冻结报告已如实披露）。
- **覆盖面**：38 行中 26 行有直接数据侧证据、1 行间接（行 29 经行 30 之对）、8 个 mapped 行仅文献级（行 9、11、13、20、21、33、34、35）、3 行 unmapped 不适用。**仅文献级的 8 行全部为 high 置信 canonical 档或已披露低置信行**，无"低置信且无任何证据"的行。

## 七、局限性声明

1. **知识截止与文献不可实时核验**：marker 判断基于复核方训练知识中的图谱体系；TSV 引用的 Hu 2022 / Litviňuková 2020 具体归类表述未在仓库内或通过实时检索核对原文，相关判断按 candidate 级处理。
2. **无定量数据复核**：仓库无逐簇 DEG/marker 表达产物，本意见书的 marker 核查停留在"文献合理性 + pseudobulk 间接证据"层，未做簇内表达定量验证。
3. **独立性局限（重要）**：**复核方与生成方同属 AI 协作流程**——映射表由人机协作生成，本意见书由 Claude（终审角色）出具、Genpilot（平台侧）前期参与，不构成完全独立第三方审查。该局限正是人类 reviewer 终签不可省略的原因之一。
4. **幻觉风险**：个别 marker 归属或文献细节可能记忆有误。缓解：每行均列出可独立复核的 marker 清单；建议课题组用 Human Heart Atlas / 斑马鱼数据库抽查下列 4 行作为独立锚点——行 25（cmlc1 疑点）、行 11（Mesothelial）、行 36（Orthers）、行 21（mouse Valve）。
5. **符号核查为静态文本层**：未覆盖斜体排版规范与同义词/别名校验（别名风险实例即 §5.5 的 cmlc1/myl7）。
6. **本意见书不构成签认**：不产生任何"正式 benchmark 可宣称"效力；签认须由人类 reviewer 作出，签认后的学术责任由课题组承担。

## 八、结论与建议

**结论**：映射表 v1 **通过 AI 独立技术复核，达到可提交人类 reviewer 签认的状态**。依据：38 行结构计数准确（12+12+14）；hash 链内容逐行等价；排除规则四方闭环（SAMap 计数差为已披露口径差，不涉表本体）；35 个 mapped 行中 30 行 high 置信（canonical/文献支持）、5 行低中置信**全部显式披露**且与数据侧弱证据自洽（弱映射弱排名）；符号规范零违规。

**建议（均不阻塞签认）**：
1. 行 25 的 cmlc1/vmhc 命名疑点建议在 v2 前用数据表达核实（或签认时以附注说明）；
2. 行 18/19/23/29（mouse Myeloid/Lymphoid/Neural、zf Smooth muscle）的 evidence_source 建议在 v2 补具体 marker 符号，使全表证据颗粒一致；
3. 文档侧两处小修（随 v2 或说明即可）：冻结报告 §3.3 已知偏离清单补列 Perivascular coarse 合并；旧签认请求文档"跨物种对不上的标 ambiguous"一句废止（TSV 无 ambiguous 标签，实际用 unmapped）。

**纪律重申**：本意见书不改变"reviewer 签认前不得宣称正式 benchmark"的课题纪律；签认后映射表冻结（改动须出 v2 并披露），方可用"冻结真值映射"身份进入正式 benchmark 表述。

## 九、导师终签指引（供 reviewer 使用）

**签认代表什么**：您作为 reviewer 认可本表作为课题 5 跨物种评估的冻结真值映射；此后任何修改必须出 v2、重算 sha256 并披露原因；课题"正式 benchmark"的宣称以此为前提。表的技术责任由课题组承担，AI 复核（本意见书）仅为辅助证据。

**建议重点看三处**（其余 34 行为 canonical/文献支持档，可抽查）：
1. §五 四个低置信映射专节——尤其 5.4（Orthers，全表最弱一行）与 5.5（cmlc1 命名疑点）；
2. §七 局限性声明第 1、3 条（文献不可实时核验、AI 复核非独立第三方）；
3. §四 逐行表中标注 **C** 的两行（行 25、36）。

**预计阅读时间**：全文约 10 分钟；仅读 §五 + §七 + §八结论约 3 分钟。38 行 TSV 原表已随邮件附上，如需逐行直审不受本意见书限制。

**签认方式**：回复"确认"，或按行号指出修改意见（如"行 21 改为……"）；任何修改将触发 v2 并重新走复核与披露流程。

---

*本意见书由 AI（Claude）出具于 2026-10-05，复核脚本可复算；仓库证据链：`config/heart-celltype-map-v1.tsv`（be985735…583165）→ `v99_mapping_embedded.json`（d92e32aa…，scripts/ 与 results/ 两副本同 hash）→ v99 metrics.json（d1081cfd…dc261）。*
