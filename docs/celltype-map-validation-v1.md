# 心脏细胞类型映射表 v1 冻结报告（2026-09-25）

## 冻结标识

- 文件：`config/heart-celltype-map-v1.tsv`（38 行，双层 coarse 9 类 / fine 17 类）
- sha256：`be9857354778535b76d1884d004c54691dc5ff2daa7b098d71dc719daf583165`
- 锚定 commit：`bb3b674`（2026-09-25 提交，含全部 38 行与 evidence_source）
- 冻结前验证：本文档 §2 pseudobulk 独立核验（平台任务 g5-pseudo-v84e）

## 1. 构建方式（防循环论证）

人工文献锚定起草（每行 evidence_source：canonical marker + Litviňuková 2020 人心脏图谱 / Hu 2022 斑马鱼心脏图谱命名体系），数据（ortholog pseudobulk 相关性）只用于独立验证，不用于生成映射。映射禁止引用任何整合方法（SATURN/SAMap/scVI/PCA）的输出。

## 2. pseudobulk 验证结果（g5-pseudo-v84e）

方法：每物种每类型对 1:1 ortholog 基因取 pseudobulk 均值（log-norm），跨物种 Spearman 相关，检查映射伙伴在目标物种全类型中的排名。

### human→mouse（15,694 共享基因，12 类型）

| 映射对 | ρ | rank/of |
|---|---|---|
| Endothelial | 0.817 | 1/12 |
| Myeloid | 0.745 | 1/12 |
| Fibroblast | 0.731 | 1/12 |
| Smooth muscle | 0.724 | 1/12 |
| Lymphoid | 0.684 | 1/12 |
| Lymphatic EC | 0.630 | 3/12 |
| Adipocyte | 0.566 | 4/12 |
| Neural | 0.544 | 5/12 |

8/8 映射对全部进入前 5；5 对 rank-1。LEC 的竞争者是姊妹群 Endothelial（生物学预期）。

### human→zebrafish（9,296 共享基因，14 类型）

| 映射对 | ρ | rank/of |
|---|---|---|
| Endothelial | 0.597 | 1/14 |
| Myeloid | 0.525 | 1/14 |
| Ventricular CM | 0.428 | 1/14 |
| Fibroblast | 0.453 | 3/14 |
| Lymphoid | 0.371 | 5/14 |
| Smooth muscle→Perivascular | 0.421 | 8/14 |
| Atrial CM | 0.304 | 8/14 |
| Neural→Orthers | 0.298 | 10/14 |

方向性支持成立（EC/髓系/心室 CM 均 rank-1），但鱼方向整体信噪比低。**低置信行确认为弱**：Neural→Orthers（rank 10）、Atrial CM（rank 8）与草稿中的 low 标注一致——保留映射但评估解读需注明。

## 3. 冻结声明与已知偏离

1. 映射 v1 即刻冻结；后续任何修改必须 bump v2、重新计算 sha256 并在论文中披露修改原因。
2. **披露**：mapped 指标（v74b）在冻结前已计算——顺序偏离 Claude 派工单的"先冻结后计算"，但映射本身未参考任何方法输出，循环论证风险可控；冻结后如需复算以冻结版为准。
3. coarse 层将 mouse/fish Valve 归入 fibroblast、人类 Mesothelial 归入 epicardial，均为 low/medium 置信且已在 TSV notes 声明。
4. mouse/fish Proliferating 与 fish mt 标 unmapped（fine 层不计入分母，coverage 单列）。
