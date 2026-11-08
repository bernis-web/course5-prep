# 课题5 工作包交接（Flash → Claude 审阅 → Codex 终审规划，2026-10-02 晚）

## 一句话现状

longrun 计划 Phase 0/2/3/5 已完成并全部提交（9 个 commit，112 tests OK）；Phase 1 完成了全部本地可做部分（4/6 核心文件字节级回收），容器侧回收任务被平台 1c4g 队列饥饿卡住（两次提交均 Pending，已按停止条件停止重试）。

## 已完成并验证

| 项 | 证据 | commit |
|---|---|---|
| Phase 0 状态冻结 | docs/flash-phase0-snapshot-20261001.md | dce62b1 |
| Phase 1 本地半场：manifest.json / environment.txt / command.txt / v99_mapping_embedded.json **字节级**回收+SHA 全对表；sha256.tsv 46 行内容完整（字节序待容器复核） | results/pilot-v1/saturn-v99/raw/recovered-20261001/ + _extraction-report.json | 37c4caf |
| Phase 2 ortholog-PCA Gate-2 重写（元组键→字符串键、active 双向排除、<1000 exit(2)、联合 PCA 修复、全量落盘+SHA、smoke 守卫、zf 142 重复基因确定性去重） | scripts/ortholog_pca_local_v1.py + wave3 manifest 修订 | d079824 |
| Phase 3 smoke 全绿（RC=0；18+18 文件逐细胞重算与 metrics 一致；37/37 输出 SHA；三张失败门实测触发过） | docs/flash-phase23-smoke-20261002.md | 17d354b |
| Phase 5 SAMap v98 双变体修复（load_species→assert_no_na_truth→adata_raw→assert_prefix_unique→umap=False/ncpus=1；truth_na 硬停；included 语义+confidence；输出分离+全 SHA）+3 个新失败门测试 | docs/flash-phase5-samap-gate-20261002.md | e351f59 |
| R2 载荷任务构建器+解析器（AES 回路、payload 编解码回路均自测通过） | scripts/build_v99_rec_payload_task.py / parse_v99_rec_log_v1.py / g5_v99_rec_payload.py | 0f…(本包) |
| 状态文件全程更新 | docs/course5-longrun-state-20260930.md | d0f458b/0e63c61 等 |

## DCS 事件簿（平台侧，需用户/老师介入）

- g5-v99-rec-r1（2105712313941725186）：01:31 提交，**Pending 17h 未调度**，18:23 取消（code 0）。
- g5-v99-rec-r1b（2105967078739628034）：18:24 重提（同 payload，一次性），至 18:40 仍 Pending。
- 判断：1c4g CPU 队列被夜间大量 odms GPU 任务挤压，属平台调度问题。**停止条件已触发，不再重试**。建议用户向老师/平台询问 1c4g 队列状态或请求调度优先级。
- 解除后动作（全部机械化，工具已备好）：查日志→`parse_v99_rec_log_v1.py` 验收→按 PREDPLAN 分组→`build_v99_rec_payload_task.py` 生成 R2..Rn→逐个一次性提交→本地重组+SHA 验收→Phase 1 关账。

## 待 Claude 审阅（材料已就绪）

1. **Gate 2/3**（ortholog-PCA）：docs/flash-phase23-smoke-20261002.md 尾部三个裁决问题（标签泄漏视角/neighbor 口径/Phase 4 放行）。
2. **Gate 5**（SAMap）：docs/flash-phase5-samap-gate-20261002.md 四个裁决问题（keys=cell_type 的 label-aware operationalization、included 分母与 v99 差异、平票决胜、提交前证据）。
3. 通过后即执行：Phase 4 全量 PCA（本地 .venv39，约几分钟）→ Phase 6 SAMap DCS 一次性提交（还需用户批准）。

## 待 Codex 终审规划

- 长跑计划剩余：Phase 1 关账 → Phase 4 → Phase 6 → Phase 7（用户发导师签认）→ Phase 8（证据包/Word/PPT）。
- 需要裁决的边界问题：(a) 1c4g 饥饿时是否允许换更高资源档跑只读任务（成本≈0 但违反"固定 1c4g"字面）；(b) Phase 4 是否等 Claude 或凭 smoke 证据直接放行；(c) v99 mapped-space 本地重评（不需 DCS）是否插队到 Phase 4 之前。
