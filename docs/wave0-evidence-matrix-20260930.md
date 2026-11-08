# Wave 0 只读证据矩阵（2026-09-30）

> 本轮为只读证据审计，未提交 DCS 任务、未启动训练/GPU、未修改旧结果、未 commit/push、未读写凭据。

## 一、总体判定

课题 5 第一阶段的**核心数字链已可复算、可溯源**：SATURN v97g 六方向×三层（规则合规版）数字、冻结映射表 v1（SHA-256 锚定）、置换检验定义、统计纪律（majority+shuffle_p+coverage）全部有本地证据支撑。主要缺口集中在三处：① v99 容器产物未完成本地回收与哈希复核；② ortholog-PCA 尚未用统一评分器复算；③ mapping reviewer 人工签认缺位。据此，v97g 数字定位为 **candidate**（候选正式 transductive 数字，待 per-cell 回放后升级），SAMap 全 18 格定位为 **candidate/exploratory**（合规重跑已做但 per-cell 结构刚补，未经二轮复核），PCA 定位为 **candidate（阶段草表）**，mapping 签认定位为 **needs-reviewer**。

## 二、四分类矩阵

| 项目 | 分类 | 证据 | 缺口 |
| --- | --- | --- | --- |
| SATURN v97g 六方向×三层指标 | **candidate** | 任务日志 EVAL3G JSON（70,484 字符）+ 证据文档双报表 | per-cell 逐细胞预测未落盘；统一评分器未逐行 diff |
| SATURN v97f 全保留版（实现对照） | **candidate** | 同上（v97f 日志） | 仅作对照，不进主表 |
| v72-era 67.4% | **confirmed（历史对照）** | docs/saturn-smoke-evidence-20260922.md | 明确降级：只作旧实现对照 |
| ortholog-PCA 六方向 | **candidate（阶段草表）** | v75c/v78b 容器内输出（六方向数字 + ortholog 文件哈希） | 未用统一评分器复算；未产出逐细胞文件 |
| SAMap 本地合规重跑 18 格 | **candidate** | local_samap3_pred_*.json ×6 + evidence 文档 | per-cell 记录结构刚补齐（included/exclusion_reason），未经二轮审计 |
| SAMap v98 DCS 容器复现 | **blocked** | r10 OOM RC=137（UMAP 未禁用） | 修复 = `umap=False` 一行，下批执行 |
| mapping v1（38 行双层） | **needs-reviewer** | SHA-256 be98…3165 + pseudobulk 验证报告 | 4 个低置信映射 + reviewer 签名均待人工 |
| v99 容器内产物（manifest/metrics/predictions 等） | **blocked（本地回收）** | v99-r6 RC=0 完成声明 + 日志回传的 metrics JSON | 文件本体在 /data/work/course5_v99/，未回收到本地并重算哈希 |
| SATURN v71 运行时 provenance | **blocked** | v71/v72 元数据（batch/subtask ID、镜像名、资源、费用） | 原始命令、训练参数、镜像 digest 未从平台恢复 |
| 物种内 ceiling（85.5/93.5/74.2） | **candidate** | v97f 同一 Final AnnData 50/50 分半 KNN15 | 与跨物种评估共享同一潜空间，解释须成对引用 |
| ESM2 消融（61.8%→20.4%） | **confirmed（方向性结论）** | v80 置换运行日志 | 数字为实现对照口径（61.8% 系 v72-era），正式引用须标注 |
| seed 稳定性（±3.8pp / 双峰） | **confirmed（方向性结论）** | seed 0/1/2 三次运行 | 鱼方向双峰为定性结论 |
| 讲稿 + PPT | **candidate** | docs/phase1-results-briefing-20260929.md + PPT 11 页 | 数字已换基线（61.8%），但 PPT 第 3 页脚注仍引 v72-era 67.4% 需核对 |
| 冻结映射表 SHA-256 | **confirmed** | be98…3165（重算一致） | — |
| 置换检验定义 | **confirmed** | 证据文档"置换检验定义（钉死）"节 | 尚未写入 manifest |

## 三、SATURN v97g 六方向核对表

来源：任务 g5-v97f-incore-eval（全保留版）+ g5-v97g-rule-compliant-eval（规则合规版）；subtask 2104517269960364034 / 2104535560372703234；日志回传 JSON。

| 方向 | v97g coarse acc | majority | coverage_q | 排除规则 | 表示层 | shuffle_p | 任务/来源 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| human→mouse | 61.79% | 48.17% | 0.9805 | fine=unmapped 双向排除（30 q） | obsm/macrogenes (1000d) | 0.0 | g5-v97g / 日志 EVAL3G |
| mouse→human | 25.39% | 31.15% | 1.0 | 同上（0 q；ref 侧 30） | 同上 | 0.0 | 同上 |
| human→zebrafish | 18.35% | 39.76% | 0.9715 | 同上（44 q） | 同上 | 0.0 | 同上 |
| mouse→zebrafish | 30.09% | 39.76% | 0.9715 | 同上（44 q） | 同上 | 0.0 | 同上 |
| zebrafish→human | 24.74% | 31.15% | 1.0 | 同上（0 q；ref 侧 44） | 同上 | 0.0 | 同上 |
| zebrafish→mouse | 46.51% | 48.17% | 0.9805 | 同上（30 q） | 同上 | 0.0 | 同上 |

**逐项核对**：
- accuracy：六方向与证据文档 v97g 表逐项一致 ✓
- majority：与 v97g 日志一致 ✓（注意：v97g 的 majority 是排除后重算，与 v97f 全保留版不同）
- coverage：human→mouse 0.9805（30 排除）、人鱼 0.9715（44 排除）、m→h/z→h 1.0 ✓
- query/reference 角色：v97g 脚本内固定 src/tgt，无显式角色表 ⚠（角色=方向定义本身，但无独立 TSV 留痕）
- coarse/fine 排除规则：v97g 代码内双向排除 ✓；但与 v97f 的差值口径已在文档声明 ✓
- 表示层：obsm["macrogenes"] 1000d，SHA 门验证 ✓
- shuffle_p：200 次 RandomState(0) 洗牌 query 预测，p=P(null≥obs) ✓
- 任务编号：g5-v97g-rule-compliant-eval-1 / batch 2104535560355926018 / subtask 2104535560372703234 ✓

**已知口径风险**：v97g 的 coarse 未做"标签空间重映射"（unmapped 类名保留而非折叠），与 v99 统一评分器的实现存在语义差；两组数字已双报，正式引用以 v97g 列为准。

## 四、SAMap 核对表

来源：本地合规重跑（exec_a6bad，2026-09-28，修复门 1–6 全部应用）；18 格 + per-cell 预测 ×6 文件。

| 检查项 | 状态 |
| --- | --- |
| 18 个方向×层级结果 | ✅ 全部产出（exact/coarse/fine × 6 方向），全部 ≤ 随机或等于 majority |
| 正式 benchmark 资格 | ❌ **candidate/exploratory**——per-cell 记录结构刚补齐，未经二轮审计；不得写入正式排名 |
| shuffle_p | ✅ 全部 ≥0.98（exploratory 口径下确认 ≤ 随机） |
| truth_na | ⚠ 合规重跑版已消除（物种前缀条码），但 legacy 版有 3 个 NA——local-samap3-readonly-audit 已记录 |
| barcode 前缀 | ✅ hu|/mo|/zf| 前缀后全局唯一（合规版） |
| 重复条码 | ⚠ legacy 版 3 个跨物种碰撞（CELL10600_N1_4 等）；合规版已消除 |
| v98 OOM 阻塞 | ✅ 根因定位（umap 未禁用）+ 修复方案预注册（`sm.run(..., umap=False)` + ncpus=1） |
| 本地 vs 平台交叉验证 | ✅ 人鼠两方向四位小数一致 |

## 五、ortholog-PCA 核对表

| 检查项 | 状态 |
| --- | --- |
| 六方向数字 | ✅ 已产出（h→m 80.9、m→h 38.3、h→z 40.5、m→z 22.4、z→h 11.9、z→m 79.5，coarse） |
| 统一评分器复算 | ❌ **未做**——v75c/v78b 为容器内 numpy 实现，非冻结评分器 |
| 分类 | **阶段草表 / candidate**——不得写入正式排名 |
| 升级路径 | Wave 3（统一评分器复算 + 逐细胞预测 + SHA）后可改 confirmed baseline |

## 六、mapping reviewer 状态

- 行数：39（38 数据行 + 1 表头）✓
- 层级：coarse（9 类）/ fine（17 类）双层 ✓
- SHA-256：`be9857354778535b76d1884d004c54691dc5ff2daa7b098d71dc719daf583165` ✓（重算一致）
- 4 个低置信映射：mouse Valve→fibroblast(VIC)、zebrafish Valve→fibroblast(VIC)、human Mesothelial→epicardial、zebrafish Orthers→neural —— 已在 TSV notes 与签名请求稿列出
- pseudobulk 验证：人鼠 8/8 进 top5（5 rank-1）；人鱼方向 EC/髓系/心室 CM rank-1，Orthers rank 10/14（最弱）
- reviewer 签名：**未签**（pending_human_signoff）——签名请求稿已备好（docs/reviewer-signoff-request-mapping-v1.md），等用户发送导师

## 七、v99 provenance 状态

| 产物 | 位置 | 本地回收 | 哈希验证 |
| --- | --- | --- | --- |
| manifest.json | /data/work/course5_v99/ | ❌ 仅远程声称 | ❌ |
| metrics.json | 同上 | ❌（日志回传了 compact 版） | ❌ |
| predictions/ 18 份逐细胞 | 同上 | ❌ 仅远程声称 | ❌ |
| confusion/ 18 份 | 同上 | ❌ 仅远程声称 | ❌ |
| sha256.tsv | 同上 | ❌ | ❌（自证，未独立复核） |
| environment.txt / command.txt | 同上 | ❌ | ❌ |
| saturn_src_tree_sha256.tsv | 同上 | ❌ | ❌ |
| course5_v99_readout.ipynb | 同上 | ❌ | ❌ |

Wave 1（本地回收 + 哈希复核 + 人→鼠 coarse 抽查）未执行前，v99 provenance 保持 **blocked/pending**。

## 八、与 PPT 主表对应关系

| PPT 页 | 数字 | 证据等级 | 说明 |
| --- | --- | --- | --- |
| 第 3 页核心数字表 | v97g 合规列 + PCA 草表 + SAMap 合规列 | **candidate**（v97g 主列）；PCA 列标"阶段草表"脚注 | 数字与证据文档一致 ✓ |
| 第 4 页基线对比图 | v97g/v78b 数字 | candidate | 图表数据源可复算 ✓ |
| 第 5 页消融 | 61.8%→20.4% | confirmed（方向性） | 61.8% 为 v72-era 口径，正式版换 v97g 基线时需重新消融 |
| 第 6 页容量 | 3.4%→61.8% | confirmed（两端锚点实测） | 中段为示意 |
| 第 7 页 seed | 67.1±3.8 / 双峰 | confirmed | — |
| 第 8 页 ceiling | 85.5/93.5/74.2 | candidate | 与跨物种共享潜空间，成对引用 |
| 讲稿"发现 1"表述 | "5/6 方向" | ⚠ **需修正为 4/6**——按 v97g 基线重算后 z→h 方向 SATURN(24.7%)>PCA(11.9%)，领先方向数从 5 变 4 | PPT 第 4 页文字同为"多数方向"尚可，讲稿需更新 |

## 九、发现的数字不一致或口径风险

1. **"5/6 方向"表述需降级**：v74b 基线（z→h PCA 11.9 < SATURN 0.2）下为 5/6；但 v97g 基线下 z→h SATURN 24.7% > PCA 11.9% → 实际为 **4/6**（且 z→h 两方法都低于 majority，"领先"无意义）。PPT 与讲稿应改为"4/6"或"多数方向（4/6，其中 z→h 双方均弱）"。
2. **消融对照口径**：61.8%→20.4% 的消融基线是 v72-era 67.4% 对应的实现；换用 v97g 协议后消融基线需重跑才能严格对齐（61.8% 数字本身不受影响）。
3. **coverage 语义差**：v97f 的 coarse coverage=1.0（'other' 类保留）；v97g/v99 的 coverage<1（unmapped 排除）。双报时必须注明各自分母。
4. **SAMap per-cell 结构**：合规版刚补 included/exclusion_reason 字段，尚未独立复核其正确性。
5. **v99 与 v97g 数字差异**：统一评分器（v99）h→m coarse 48.44% vs v97g 61.79%——差异源于标签空间语义（v99 用 exact 标签+排除；v97g 用 mapped 标签）与评分器实现，两组数字双报不抹平。

## 十、建议下一步（不执行）

1. **Wave 1**：v99 本地回收（/data/work/course5_v99/ → results/pilot-v1/saturn-v97g/raw/），按 sha256.tsv 重算，人→鼠 coarse 抽查——回收后 v99 从 blocked 改 confirmed。
2. **Wave 2**：SAMap v98 补 `umap=False` + ncpus=1 后单次重跑（已预注册修复）。
3. **Wave 3**：ortholog-PCA 统一评分器复算（PCA 列升级）。
4. **Wave 4**：mapping reviewer 签认（请求稿已备好，等用户发送）。
5. **Wave 5/6**：inductive 最小试验 + 统一矩阵冻结（在上述门通过后）。
6. PPT/讲稿修正：讲稿"5/6"→"4/6"；PPT 第 4 页脚注补"按 v97g 基线 z→h 方向 SATURN 略优于 PCA"。
