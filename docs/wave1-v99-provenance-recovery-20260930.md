# Wave 1: v99 Provenance 本地回收与只读验收（2026-09-30，修订版）

## 本轮范围

只读回收 DCS 容器内 v99 provenance 产物的可访问部分，验证文件完整性和指标一致性。

## DCS 任务 ID

- v99 评估：g5-provenance-v99-readout-r6，batch 2104910134758707202，**RC=0**
- 文件导出：g5-v99-file-export-1，subtask 2105270145805012994，Completed（42,844 字符日志）
- 文件读取：g5-v99-file-readout-slim，subtask 2105279363597926402，Completed（25,575 字符日志）
- **18 predictions + 18 confusion 文件在容器内已确认存在**（PRED_COUNT=18, CONF_COUNT=18）——注意：容器级存在确认 ≠ 本地文件已回收

## 关键确认

| 检查项 | 结果 |
|---|---|
| Final AnnData SHA-256 | ✅ 20cf807f…（manifest.json 内记录） |
| 表示层 | ✅ obsm/macrogenes (4606×1000) |
| 物种计数 | ✅ human 1528 / mouse 1535 / zebrafish 1543 |
| 协议标签 | ✅ transductive_formal_reassessment |
| 脚本 SHA-256 | ✅ 7ad1a479… |
| Python 版本 | ✅ 3.9.12 conda-forge |
| UTC/北京时间 | ✅ 2026-09-29T12:27:04Z / 20:27:04+08 |
| predictions/ 文件数 | ✅ 18 |
| confusion/ 文件数 | ✅ 18 |
| candidate_hashes（含 v95/v96 命令、脚本） | ✅ 全部有 SHA-256 |
| saturn_src_tree | ✅ 214 文件 |
| v99_mapping_embedded.json | ✅ d92e32aa… |
| seed | ✅ 0 |
| KNN/distance/nperm | ✅ 15/cosine/200 |

## 尚未本地回收的文件

predictions/ 和 confusion/ 下 18+18 个 JSON 文件本体仍在 DCS 容器 /data/work/ 中，**未完成本地归档**。notebook 后端 /normal/content 路径映射不通，无法逐文件拉取。需后续（DCS-P2 或表单恢复后）批量下载。

**口径修正**：本文件中"已确认存在"均指**容器级存在确认**（通过任务日志的 ls/find 输出确认），不代表本地文件已回收。本地回收目录 results/pilot-v1/saturn-v99/raw/ 中目前仅保存了导出日志尾部（v99_export_log_full.txt, 42,844 字符），不包含完整 JSON 文件本体。

## Wave 1 验收结论

v99 provenance 从 blocked 升级为 **candidate**（日志级）：
- ✅ 容器内评估数字已通过日志通道回收并归档
- ✅ 18+18 文件容器级存在已确认
- ✅ manifest/env/cmd/sha256 元数据已通过日志回收
- ⏸ per-cell 预测与混淆矩阵的完整 JSON 文件**未本地回收**（notebook 后端阻塞）
- ⏸ 文件级 provenance 仍 **pending/blocked**

**标签空间注意**：v99 的 coarse/fine 使用 exact 标签 + inactive 排除（非 mapped 标签空间），与 v97g 的 mapped 标签语义不同。两组数字双报，不合并。

## Phase 1 文件级回收（2026-10-02，接续）

### 已完成：4/6 核心文件字节级回收（无需 DCS）

从 `v99_slim_export_full.txt`（25,575 字符日志）重建字节流，按 sha256.tsv 目标哈希验证：

| 文件 | 状态 | SHA-256 验证 |
|---|---|---|
| manifest.json | **byte_exact** | 84267bd7… ✓（无尾换行变体） |
| environment.txt | **byte_exact** | 2c9dcb5d… ✓（= JSON + pip freeze 全文，13,872 B，尾换行） |
| command.txt | **byte_exact** | 0e5ee3dc… ✓（尾换行） |
| v99_mapping_embedded.json | **byte_exact** | d92e32aa… ✓（本地 scripts/ 副本逐字节一致） |
| sha256.tsv | content-only | 46 行内容完整；行序无法从日志确定字节序，待容器内重算闭环 |
| metrics.json | 未回收 | 两个日志均未打印其内容 |

产物目录：`results/pilot-v1/saturn-v99/raw/recovered-20261001/`（新目录，未覆盖旧日志）。
提取脚本：`scripts/extract_v99_from_logs_v1.py`（含 `_extraction-report.json`）。

注意：raw/ 下旧 `command.txt`/`environment.txt`（137/145 B）是早前失败导出任务的报错文本，非容器文件本体，已在报告中标注废弃，不删除。

### DCS 任务：g5-v99-rec-r1（2026-10-02 01:31:52 提交）

- 直连 POST /stereonote/api/offline/save 成功（code 0）
- batch/parent: `2105712313899782145`；subtask: **`2105712313941725186`**（g5-v99-rec-r1-1）
- 镜像 SATURN--22（uuid 57362367…）、1c 4g（resource_id=259）
- 脚本 `scripts/g5_v99_rec_r1.py`（本地 mock 树测试通过）：只读 /data/work/course5_v99/
- 输出协议：HASHVER（46 文件新鲜 SHA+size）/ SHATSVB64（tsv 字节级回收）/ METRICS 全文 / 6 个字节互异 confusion 全文 + 12 条 CONFDUP 恒等行 / PREDMETA（逐文件 bytes/sha/rows/included/acc）/ PREDPLAN（去 neighbor 的压缩载荷 b64 长度 + gzip SHA）
- 预算：stdout ≈ 40-50KB < 100K 截断线
- 后续：R2..Rn 按 PREDPLAN 分块拉取 18 份预测载荷，每任务 ≤85KB
