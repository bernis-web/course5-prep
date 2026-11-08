# Phase 2+3 执行记录：ortholog-PCA 修复与 smoke（2026-10-02）

> 供 Claude Gate 2 / Gate 3 审阅。Phase 4（全量）在此审阅通过前不启动。

## Phase 2：Gate-2 检查单逐项落实（commit d079824）

| 检查项 | 修复前 | 修复后 |
|---|---|---|
| 未定义变量 | L116 `Z = PCA().fit_transform(X)` 的 `X` 未定义（NameError） | `X_joint = vstack([Xs, Xt])`（transductive 联合 PCA，与协议标签一致） |
| mapping 键类型 | 元组键 `(species,label)` 查字符串键表 → 全部 miss → 全部 unmapped | `freeze_mapping` 字符串键 `"species\|label"`；单元测试验证 3 个 status=unmapped 行在 coarse/fine 双向排除 |
| 共享基因硬停 | `<100: SKIP` 继续跑 | `<1000: HARDSTOP + exit(2)`；smoke 实测 h-m 15,869 / h-f 9,131 / m-f 7,670 全过门 |
| 归一化协议 | 无文档口径 | manifest 写明 log1p(CPM/100) ≡ normalize_total(1e4)+log1p，**全基因空间归一化后**再取子矩阵（与 v98 DCS 版逐行一致） |
| 角色命名 | 隐式 | manifest `roles: src=reference(knn fit) tgt=query`，18 份 prediction 行内嵌 direction/level |
| 完整落盘 | 只有 metrics+environment | manifest（输入/输出全量 SHA-256）、environment、command、metrics、predictions×18、confusion×18 |
| 排除规则 | 仅 `coarse_level=='unmapped'` 字符串过滤（旧审计指认的错误） | `mapping_status != active` 双向排除（ref+qry），排除原因逐细胞记录（no_mapping_row / mapping_status:unmapped / layer_value_unmapped） |
| KNN 口径 | 默认欧氏 | `metric="cosine", weights="distance"`（K=15 倒距离加权 cosine，KNN classifier 的 distance 权重即 1/d） |
| 置换定义 | 200 次洗牌 query 预测 | 不变（RandomState(0)，full=200 / smoke=20），单侧 p |
| 数据完整性门 | 无 | 缺文件/重复 obs_names/重复前缀化 barcode/空真值 → exit(2)；斑马鱼 upper() 后 142 个重复符号：全空间归一化后按首次出现确定性去重（分母不变），计数打印进日志 |

新增防护：`--smoke` 输出目录已存在则拒绝运行（旧目录 `ortholog-pca-smoke-crash-20261001/` 保留旧脚本崩溃现场作证物，未删除）。

## Phase 3：smoke 实测（.venv39，RC=0，8.1s）

- 命令：`.venv39/Scripts/python.exe scripts/ortholog_pca_local_v1.py --smoke`
- 每物种 RandomState(0) 抽 120 细胞、nperm=20；写 `results/pilot-v1/ortholog-pca-smoke/`
- hard-stop 门实测生效：首跑抓出斑马鱼重复基因名（修复后放行）；文件名 `>` 在 Windows 非法 → 输出名改 `{level}_{src}_to_{tgt}.json`
- 18 predictions + 18 confusion + 37 个文件 SHA 全部落盘

## Gate 3 自检（全绿）

1. **可解析**：18+18 JSON 全部解析成功
2. **无 NaN/重复 barcode**：360 unique barcodes（3×120），行内无 NaN
3. **coverage 可重算**：18/18 与逐细胞 included 重算一致（tol=半位舍入）
4. **acc/majority/confusion 可重算**：18/18 一致
5. **置换定义一致**：manifest 记录 nperm/n_seed；smoke p 值与 majority 关系合理（m→f 低于 majority 时 p=1.0）
6. **失败门真实生效**：重复基因名、smoke 目录已存在、缺输入三个门均实测触发过
7. **输出 SHA**：manifest.output_sha256 37/37 复算一致

smoke 数字（0.09-0.58）仅验证管线，不进主表；方向性格局（h→m coarse 0.5847 vs maj 0.4492；m→f 低于 majority）与已知"鱼方向弱"叙事一致，待 Phase 4 全量复核。

## 请 Claude 裁决

1. Gate 2：标签泄漏（none expected：KNN 拟合只用 ref 标签；联合 PCA 属 transductive 已声明）、角色、mapping 键、归一化、硬停——是否放行 Phase 4？
2. Gate 3：上列自检是否充分；neighbor_barcodes 记录的是 reference 侧 kept 子集 barcode（索引语义已在代码内对齐）——口径是否接受？
3. 全量运行预计峰值内存 <1.5GB（稀疏存储 + 仅共享基因稠密化），在用户机器执行是否符合"运算不在我本地"边界的解释范围（计划文本本身指定本地 .venv39 执行 Phase 3/4）？
