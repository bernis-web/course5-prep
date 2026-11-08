# Claude 最终复审：验收修正后的最终文件（2026-10-09）

> 审阅人：Claude（claude CLI --print，只读）｜范围：第 5 册（1,000 维修正）、Word + 生成脚本、第 3 册（因果措辞）、
> 三档方案（C1-SATURN 源码级判定、次数/费用重算）、SHA 清单
> 结论：**pass**（sha_ok=true；4 项非阻断残余见文末 JSON）
> 执行者处理：残余 ①（scratch 文件过期标注）②（行号偏差，仅记录）③（index 补新 SHA）④（本记录归档）均已处理。

---

All six items verified. Here is the targeted re-review.

---

## ① 第5册 p2/p6 — 1,000 维表述 → **通过**

- `课题5第05次汇报_SATURN信号与协议效应.pptx` slide 2（p2，`② macrogene 聚合`）实际文本：`• 1,000 个 macrogene 聚合基因表达` … `• 表示层为 1,000 维 macrogene 空间（v99 评分读取 obsm["macrogenes"]，形状 4,606 × 1,000）`。
- slide 6（p6，`容量：1,000 macrogenes`）：`• 1,000 是本轮设置`；`• 与 PCA-50 的对比：不是同一维度量级（1,000 维 vs 50 维）；macrogene 是学习出来的聚合，PCA 是线性投影`。
- 与 `scripts/dcs_provenance_v99.py:22` 的 `EXPECTED_EMBEDDING_SHAPE = (4606, 1000)` 完全一致。
- 全仓 pptx/docx 扫描：**无** "50 维级" 残留；脚本 `build_report05.js` L22/L74 同步正确。
- 唯一残留：`extract_all.txt:320`（**非交付物**的前置 scratch dump，mtime 16:13，仍含旧文与旧 `ref_labels 参与训练`）——见结尾 remaining。

## ② Word 与生成脚本 → **通过（重建不会冲掉修正）**

- `deliverables/course5-final-report.docx` 主表（§4.1）表头 = `方向 / ortholog-PCA / SATURN v97g / SAMap v98 / v99 统一评分器 / 多数类·映射空间 / 多数类·原始标签` → **双多数类列在位**；h→m 值 `0.4817 / 0.4618`，与 `orth[coarse].majority / v99[coarse].majority` 的 metrics 逐格一致。
- 读数含 0.4817：docx `P73`「人→鼠 0.8618 vs 其映射空间多数类 0.4817」= 脚本 L167。
- 脚本内六处修正齐备：鱼方向分组 L84（`按 query 分组逐方向：人/鼠→鱼… 鱼→人/鼠…`）、双多数类列 L163-164、读数 0.4817 L167、消融 `67.4%→20.4%` L208、§5.2 标签空间拆分 L219-220、§5.10 needs-reviewer L231-234。
- **重建实测**：以脚本重跑（仅写 `/tmp`）后与现有 docx 对比 —— 段落数 171=171、表 4=4、`total para diffs: 0`；`settings.xml` 现有与重建均为 `<w:zoom w:percent="100"/>`（percent 已在，`fix_settings_zoom` L279-295）。
- 小注：任务书引用的 `L163（读数）/L204（消融）` 与当前文件实际 `L167/L208` 差 4 行（内容在位，属行号描述偏差，非缺陷）。

## ③ 第3册 p4 因果措辞 → **通过**

- slide 4（p4）「这意味着什么」：`• SATURN/SAMap 的训练机制使用细胞类型标签（SATURN：species 前缀 labels；SAMap：keys=cell_type）• 该机制对本次分数的贡献尚未单独量化 • 不能与 label-free 的 ortholog-PCA 直接互比` —— 与要求措辞一致，旧「高分包含真值标签的贡献」已清除。
- 待核实标注保留：p4 表述格 `labels 通道参与 miner（ref_labels 仅评估；运行时待核实）`。

## ④ SATURN 未见物种可行性（方案 §档C1） → **通过**

逐条对照源码，四条依据均成立：
1. `model/saturn_model.py:106` `filler_idx = self.species_to_gene_idx[species]`（`species_to_gene_idx` 为按物种 key 的 dict，L42/44）→ 未见物种 **KeyError**；块由 `train-saturn.py:522-533`（`species_to_gene_idx_hv[species]=(ct, ct+n)`，`ct` 累加拼接）定义。
2. `train-saturn.py:525/528` 在 `for species in sorted_species_names` 循环内 `sc.pp.highly_variable_genes(adata, flavor='seurat_v3', n_top_genes=args.hv_genes)` 于**各物种自身 adata** 上选 HVG（L526-527 子集）→ 若照搬即为用 held-out 表达定义特征空间（泄漏），冻结词典替代路径不存在。
3. `model:42` `num_species = len(species_to_gene_idx)`；用于 `L75` decoder 首层输入维 `self.embed_dim + self.num_species + self.num_batch_labels` 与 `L135/L458` `torch.zeros(batch_size, self.num_species)` → 新物种改变权重形状，**冻结权重不兼容**；无预留物种槽。
4. `model:46-49` `num_genes = max(v[1])` → `L51 p_weights`；且 `train-saturn.py:644/751` 建模时固定传入 `species_to_gene_idx=species_to_gene_idx_hv` → **无冻结指派路径**。

结论 **"C1-SATURN 阻塞；C2 中 SATURN 格一并阻塞"** 恰当（"eval()+no_grad() 不足以证明可直接投影"成立）。

## ⑤ 次数/费用重算 → **通过**

- 结构自洽：81 格 = 3 折×3 方法×3 seed×3 层；**运行次数 = 每方法 3 折×3 seed = 9**（27 runs 总量）。
- "单次表示可评三层"佐证成立：`results/pilot-v1/samap-v98/wdl-run/extracted/metrics.json` 为单次 WDL 任务产物，含 6 方向 × `exact/coarse/fine` = **18 格**（附：单任务 16m24s = 0.18 元实证）。
- 费用：9×~16.4min≈148min × 0.011 元/min ≈ **1.63 元 ≈1.6 元**，且自标 **"待澄清估算（LOO 单次时长未实测）"**。
- 与旧值差异已说明：旧「27 次×16min≈4.75 元」系按"逐层重跑"计（27=3×3×3），方案 C2 行 L79 明确"现有证据不支持逐层重跑 → 以 9 次为准"。
- 小注：任务书任务号 `W202610050003100` 与仓库一致使用的 `W202610050003104`（"系列"表述覆盖），不影响推理。

## ⑥ 新 SHA → **通过**

- `sha256sum -c SHA256SUMS.txt` → **8/8 OK**；文件为 LF（`grep -c $'\r'` = 0，UTF-8）。
- 03 = `c06f791b…`、05 = `4990a046…`，与"验收修正重建"说明一致：`docs/longrun-20261009-final-handoff.md:98`、`docs/longrun-20261009-worklog.md:114` 均为 `03 c06f791b… / 05 4990a046…`。
- `index.md:149` 的 `d04a02e8→c858e731 / 9b9dbf96→8c8ecedc` 是**批次五中间值**；final-handoff:55 记录完整链 `d04a02e8→c858e731→c06f791b`、`9b9dbf96→8c8ecedc→4990a046`，无矛盾。

---

### 结论
五项验收问题均已按"验收修正"落地，且**脚本重建可复现最终产物**（Word 逐段 0 diff；PPTX 文本与 build_reportNN.js 一致；SHA 8/8 复核通过）。仅剩文档性/清理性小项，不构成阻塞。

```json
{"final_r2": "pass", "remaining": ["非交付物 scratch 文件 extract_all.txt:320/396 仍含旧文（'50 维级'、'ref_labels 参与训练'），易误引，建议清理或标注为过期（不在 SHA 绑定集内）", "任务书行号 L163(读数)/L204(消融) 与 scripts/build_final_report.py 实际 L167/L208 不符（内容均在位，仅引用行号偏差）", "index.md:149 仍记批次五中间 SHA（c858e731/8c8ecedc），可与最终 SHA（c06f791b/4990a046）并列以免误读（可选）", "docs/reports/claude-final-r2-review-20261009.md 尚待归档（final-handoff:98 预指的复审记录）"], "sha_ok": true}
```
