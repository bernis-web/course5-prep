# Phase 7：发给导师的邮件草稿（2026-10-04，请过目后自行发送）

> 用途：课题5 阶段汇报 + 映射表 v1 签认请求。以下为建议正文，可自行增删。

---

主题：单细胞跨物种映射评估——阶段结果与一份需您签认的映射表

老师您好：

课题5（心脏样本三物种单细胞跨物种映射评估）阶段性结果如下，其中有一份映射表需要您签认。

## 一、需您签认：心脏细胞类型同源映射表 v1

我们为跨物种标签迁移评估冻结了"心脏细胞类型同源映射表 v1"（38 行 = 人 12 + 鼠 12 + 斑马鱼 14 个类型；SHA-256 固定，改动需出 v2 并披露）。请花 2 分钟审一遍映射合理性，回复"确认"或指出问题。

双层结构：
- coarse（9 粗类）：cardiomyocyte / endothelial / fibroblast / smooth_muscle / immune / epicardial / adipocyte / erythroid / neural / other
- fine（17 细类）：尽量保留种内分辨率（如 ventricular/atrial 心肌分开），跨物种对不上的标 ambiguous

需要重点确认的 4 个低置信映射（其余为教科书级 marker 锚定）：
1. mouse Valve + zebrafish Valve → coarse=fibroblast（瓣膜间质归间质/成纤维大类）
2. human Mesothelial cell → coarse=epicardial（心外膜与间皮同源）
3. zebrafish Perivascular cells → smooth muscle（mural 细胞合并，rgs5/pdgfrb 佐证）
4. zebrafish "Orthers"（原始表拼写如此）→ neural（marker 为 scn1ba/scn4ab/sncga 神经程序；pseudobulk 验证 rank 10/14，最弱一条）

已做验证：1:1 直系同源基因 pseudobulk Spearman——人鼠 8 对映射全进 top5（5 对 rank-1，内皮 ρ=0.82）；人鱼方向噪声大但 EC/髓系/心室 CM rank-1。

排除规则：mouse/fish 增殖细胞与 fish 线粒体群（低质量）不入 mapped 分母，单列 coverage。

## 二、阶段结果（供参考，均为 transductive 重评估口径）

1. **零整合基线（ortholog-PCA）表现强**：1:1 直系同源基因 + PCA50 + KNN15，人→鼠 coarse 准确率 86.2%（多数类 48.2%），鼠→人 73.7%（多数类 31.2%）；全部涉及斑马鱼的方向为阴性/弱结果。已通过独立复核（评估全确定性复现 + 18 格逐细胞重算一致）。
2. **SATURN（蛋白同源嵌入）**：人→鼠 coarse 61.8%，低于零整合基线——"简单同源基线难超越"的方法学结论得到支持。
3. **SAMap 对照**：因平台离线调度通道故障暂时受阻（已提工单催单），恢复后补跑。
4. **v99 统一评分器**：评估产物 provenance 已通过独立审计升级 confirmed（46 文件树哈希全对表 + 评估确定性复现）。

## 三、请求

1. 映射表 v1 签认（回复"确认"或修改意见）；
2. 平台离线任务调度故障，已提交工单 TK20261003235804338 并加急，如老师方便可帮忙催一下平台。

谢谢老师！

---

## 附：发送前检查清单（发件人自用）

- [ ] 确认映射表文件本体（config/heart-celltype-map-v1.tsv）随邮件附上
- [ ] 数字口径：正文引用的 86.2%/73.7%/61.8% 均为 coarse 层、transductive 重评估口径，与报告一致
- [ ] 如需完整证据：docs/final-evidence-matrix-ortholog-pca-20261003.md + docs/phase1-closure-20261004.md
