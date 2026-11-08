# 映射表 v1 reviewer 签名请求（发给导师/组内）

@老师/组内：以下是我们为跨物种标签迁移评估冻结的"心脏细胞类型同源映射表 v1"，请花 2 分钟审一遍映射合理性并回复"确认"或指出问题。签认后它将作为评估的冻结真值映射（sha256 固定，改动需 v2 + 披露）。

**文件**：`config/heart-celltype-map-v1.tsv`（38 行 = 人 12 + 鼠 12 + 斑马鱼 14 个类型）

**双层结构**：
- coarse（9 粗类）：cardiomyocyte / endothelial / fibroblast / smooth_muscle / immune / epicardial / adipocyte / erythroid / neural / other
- fine（17 细类）：尽量保留种内分辨率（如 ventricular/atrial CM 分开），跨物种对不上的标 ambiguous

**需要重点确认的 4 个低置信映射**（其余为教科书级 marker 锚定）：
1. mouse Valve + zebrafish Valve → coarse=fibroblast（瓣膜间质细胞归间质/成纤维大类）
2. human Mesothelial cell → coarse=epicardial（心外膜与间皮同源）
3. zebrafish Perivascular cells → 归入 smooth muscle（mural 细胞合并，rgs5/pdgfrb 标记佐证）
4. zebrafish "Orthers"（原始表拼写如此）→ 归 neural（该群 marker 是 scn1ba/scn4ab/sncga 神经程序；pseudobulk 验证 rank 10/14，最弱的一条）

**已做验证**：1:1 直系同源基因 pseudobulk Spearman——人鼠 8 对映射全进 top5（5 对 rank-1，内皮 ρ=0.82）；人鱼方向噪声大但 EC/髓系/心室 CM rank-1。

**排除规则**：mouse/fish Proliferating 与 fish mt（低质量）不入 mapped 分母，单列 coverage。

回复格式建议：`确认` 或 `第 N 条改为 …`。谢谢！
