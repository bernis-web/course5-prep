# Phase 1 关账报告：v99 文件级 provenance 全量回收（2026-10-04）

> 结论：**Phase 1 验收标准全部满足**。v99 的全部四类证据（元数据 6 件、18 confusion、18 prediction、46 文件树完整性）已回收并独立验证。R1d/r1_out.txt 双通道互证。

## 一、回收通道（本次打通的三层）

1. **NFS 只读挂载**：Genpilot 容器 /work/Analysis ← 离线任务 /data/work 主机真身（jdfsms1/.../users/<user>/<ws>/online）；46 文件全部健在
2. **dcs data push**：Genpilot 容器 → /Files/ResultData/Notebook/（项目文件空间，零损坏文件通道；r1_out.txt + 7 个文件已推）
3. **downloadFile API**：GET /api/data/file/downloadFile?id=<id>，全套头（X-Access-Token/X-Zone/X-Client-App/X-Domain-Code/X-Domain-Type/projectId）——数据管理页文件的程序化读取通道（缺 X-Client-App/X-Domain-Code/projectId 三头即 500，此为关键）

## 二、本地持有清单（results/pilot-v1/saturn-v99/raw/recovered-20261001/）

| 类别 | 文件 | 验证 |
|---|---|---|
| 元数据 | manifest.json | byte_exact 84267bd7 ✓ |
| 元数据 | environment.txt | byte_exact 2c9dcb5d ✓（含 pip freeze 全文） |
| 元数据 | command.txt | byte_exact 0e5ee3dc ✓ |
| 映射 | v99_mapping_embedded.json | byte_exact d92e32aa ✓（与冻结 TSV be98…3165 38 行全等） |
| 指标 | metrics.json | **byte_exact d1081cfd ✓**（Genpilot 分段 b64 传输；引用必须带此 SHA。工作文件 metrics.content.json 为 JSON 等价但序列化不同的中间产物，**禁止作为引用对象**） |
| 索引 | sha256.tsv | as-is 26fc554a（4581B；46 行与 09-30 日志版逐行一致；自引用行悖论已记录） |
| 混淆 | confusion/ ×18 | **byte_exact 18/18**（11 互异经 b64 传输 + 7 个 SHA 等价重建，全部对表） |
| 载荷 | payloads/ ×6 唯一 | gz 字节收讫；**逐份解压重算 acc 与容器 6/6 一致** |
| 全量 | files-channel/r1_out.txt | 84,752 B（R1 完整 stdout：HASHVER+METRICS+CONF+PREDMETA+PREDPLAN），md5 b999aa1d |
| 全量 | files-channel/p1.b64 | 28,044 B，md5 d0e9b0a0（= Genpilot 独立报值） |

## 三、四重独立验证（全部通过）

1. **HASHVER 46/46**：Genpilot 容器今日新鲜重算的全树哈希 vs sha256.tsv——45 个内容文件逐一相等；唯一"分歧"是 sha256.tsv 自引用行（自指哈希悖论，已记录）
2. **新鲜逐文件重算复现**：Genpilot 容器重跑回收脚本，18 格 PREDMETA 新鲜重算 acc 与 09-29 版逐字段相等，另有本地端到端独立复现（评估确定性证据；完整评分重跑日志待存档）
3. **18 份预测文件字节级**：downloadFile 下载的 18 份原始文件，页内 SHA-256 全部等于 sha256.tsv 记录（18/18，分三批）
4. **载荷独立重算**：6 份唯一载荷解压后逐细胞重算 acc，与容器 PREDMETA 6/6 一致（0.474919/0.109527/0.176047/0.186001/0.187173/0.330293）

## 四、计划规定抽查：h→m coarse 三件套一致性 ✅

预测载荷行（1,535）→ 施作冻结映射排除（30 个 mouse status≠active 细胞）→ 重算：
- acc = **0.4844** == metrics.json coarse acc ✓
- n_q = **1505** == metrics n_q ✓
- confusion 逐项 == confusion/coarse_human_to_mouse.json ✓

## 五、结构性新认知（写入方法学）

- v99 的 exact/coarse/fine 三层**预测文件内容相同**（仅内嵌 level 字符串不同，字节差=层名长度差）；层间差异全部在 metrics/confusion 的**评分期排除**（coarse/fine 双向剔除 status≠active）。故"三层共用预测文件"非异常，是 v99 设计。
- metrics 的 exact 层 acc == 预测文件自带 acc（0.474919 等六方向全部吻合）——exact 层无排除，两者理应相等，互证成立。
- sha256.tsv 自引用行（c84dd378）≠ 文件实际哈希（26fc554a）——自指悖论；审计以其余 45 行为准。

## 六、数字口径提醒（引用 v99 数字必读）

v99 统一评分器数字（exact 0.4749 / coarse 0.4844 等）与 v97g 口径（61.79%）**不可直接比较**（标签空间+排除规则+评分器三重差异，见 v99-score-reconciliation 文档）。所有 v99 数字为 transductive reassessment 口径。

## 七、Phase 1 验收结论

| 原验收项 | 状态 |
|---|---|
| manifest/env/cmd/mapping 回收 | ✅ byte_exact |
| metrics.json 回收 | ✅ byte_exact（新增） |
| 18 predictions + 18 confusion 回收 | ✅ 18 confusion byte_exact + 18 prediction SHA 验证 + 6 载荷逐细胞数据本地持有 |
| sha256.tsv 重算全部哈希 | ✅ 46/46（含自引用行说明） |
| h→m coarse 抽查三者一致 | ✅ 全绿 |
| 缺文件/502/解析失败/SHA 不一致停止条件 | 未触发 |

**Phase 1：关账。** Claude Gate 1 复核裁决 pass，**v99 provenance 升级 confirmed**——范围限定为 **course5_v99 输出树 46 文件（file-level）**；18 份预测文件的全字节（含 neighbor_barcodes）未本地落盘，未来 neighbor 级工作需重新拉取；输入 h5ad（20cf807f…）本轮未新鲜复验。报告引用 v99 数字仍为 transductive reassessment 口径（candidate-grade for reporting）。
