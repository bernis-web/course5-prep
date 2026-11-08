# 课题5 长跑状态文件（2026-09-30 唯一状态源）

> 本文件是全项目唯一执行状态源。所有后续阶段启动前必须读本文件并核对本表。

## 1. 已确认结果

| 项目 | 数字/结论 | 证据来源 | 证据等级 |
|---|---|---|---|
| 物种细胞数 | 人 1528 / 鼠 1535 / 鱼 1543 | v97f 日志 + local_regen_subset.py 逐类型一致 | confirmed |
| 冻结映射表 v1 SHA-256 | be98…3165 | sha256sum 重算 + celltype-map-validation-v1.md | confirmed |
| pseudobulk 验证（人鼠 8/8 top5） | docs/celltype-map-validation-v1.md | g5-pseudo-v84e 日志 | confirmed |
| 置换检验定义 | 200 次 RandomState(0) 洗牌 query 预测，p=P(null≥obs) | docs/transductive-formal-v74-evidence-20260928.md "置换检验定义"节 | confirmed |
| Final AnnData SHA-256 | 20cf…43f | v97 任务日志 SHA 门 + v99-r6 重验证 | confirmed |
| ESM2 消融方向性结论 | 蛋白信号为真（61.8%→20.4%，61.8% 系 v72-era 口径） | v80 置换运行日志 | confirmed（方向性） |
| ortholog-PCA 基线 | h→m 80.9% > SATURN 61.8% > SAMap ≈2% | v75c/v78b/v97g 三方交叉 | confirmed（方向性）；61.8% 系 v97g 口径 |
| SAMap 合规 18 格全 ≤ 随机 | 本地合规重跑 18 格 + shuffle_p ≥ 0.98 | local_samap3.py 修复版 + v99-file-export | confirmed |

## 2. candidate 结果

| 项目 | 数字 | 证据来源 | 升级条件 |
|---|---|---|---|
| SATURN v97g coarse 六方向 | h→m 61.79% / m→h 25.39% / h→z 18.35% / m→z 30.09% / z→h 24.74% / z→m 46.51% | EVAL3G 日志 + v99-r6 统一评分器交叉 | per-cell 逐细胞预测回放 |
| SAMap v98 DCS 复现六方向 | 待 umap=False 修复后运行 | — | Wave 2 通过门 |
| ⚠ 候选表鱼方向数字 caveat | z→h 24.74 / z→m 46.51 / m→z 30.09 均为单 seed（seed=0）结果；seed 双峰已 confirmed | — | — |
| ortholog-PCA 六方向（阶段草表） | h→m 80.9% / m→h 38.3% / h→z 40.5% / m→z 22.4% / z→h 11.9% / z→m 79.5% | v75c/v78b 容器内输出 | Wave 3 统一评分器复算 |
| v99 统一评分器 h→m coarse | 48.44%(maj 46.18%) | v99-r6 日志 | 与 v97g 双报，不合并 |
| 物种内 ceiling | 85.5 / 93.5 / 74.2 | v79 ceiling 任务 | — |（与跨物种共享潜空间，须成对引用）|
| seed 稳定性 | h→m 67.1±3.8 稳定；鱼方向双峰（11.3/48.8/8.3）| v81/v82 三 seed 运行 | confirmed（方向性） |

## 3. blocked/pending 结果

| 项目 | 阻塞原因 | 解除条件 |
|---|---|---|
| SAMap v98 DCS 复现 | UMAP OOM（137）| `umap=False` + ncpus=1 + **build_gnnm 函数补齐 + 本地语法验证** 后单次修复重跑 |
| v99 文件级 provenance 本地回收 | notebook 后端 502/路径映射不通；100K 日志截断 | 分块导出任务（Phase 1） |
| v99 数字口径消歧 | v99 统一评分器 48.44% vs v97g 映射标签 61.79%（不同协议双报） | Phase 2 消歧文档 |
| v99 coarse 双源矛盾 | v97f 60.59% vs v97g 61.79% vs v99 48.44%——标签空间+排除规则+评分器实现三重差异 | Phase 2 消歧文档 + Phase 1 metrics.json 回收 |
| mapping reviewer 签认 | 等人工签名 | Wave 4 / 用户发请求 |
| v99 mapped-space 重评 | 需 Phase 1 回收 predictions/ 后本地重算（本地可做，不需 DCS） | Phase 1 完成后 |
| v71 运行时 provenance 恢复 | 原始命令/训练参数/镜像 digest 未从平台恢复 | Wave 3 后置 |
| inductive 最小试验 | 需用户批准 + 前置门通过 | Wave 5 |

## 4. 不允许引用的历史结果

| 数字 | 原因 |
|---|---|
| v72-era 67.4% | 旧实现对照（sklearn 系），正式引用一律以 v97g 61.79% / v97f 60.59% 为准 |
| legacy SAMap（未前缀化） | 已被合规重跑覆盖 |
| v74b 部分数字 | z→h 方向 PCA<SATURN 的"5/6"表述在 v97g 基线下为 4/6 |
| v95/v96 | 被取消的任务，不得引用 |

## 5. 本轮唯一执行顺序

```
Phase 0: 状态冻结（本文档）→ Claude 审查
Phase 1: v99 文件级 provenance 分块导出 + 本地 SHA 验收
Phase 2: v99/v97g 数字口径消歧文档
Phase 3: SAMap v98 umap=False 修复重跑（需批准）
Phase 4: ortholog-PCA 统一评分器复算
Phase 5: mapping reviewer 签认
Phase 6: 最终证据包和汇报材料
```

## 6. 各阶段任务 ID、日志、产物和验收状态

| 阶段 | 任务 ID | 日志 | 产物 | 状态 |
|---|---|---|---|---|
| v97f 六方向×三层评估 | g5-v97f-incore-eval | 2104517269960364034 | /data/work/eval3_v97e_out.txt | Completed，EVAL3G 全量 |
| v97g 规则合规 | g5-v97g-rule-compliant-eval | 2104535560372703234 | /data/work/eval3_v97g_out.txt | Failed（尾部退出码），指标完整 |
| v99-r6 provenance | g5-provenance-v99-readout-r6 | 2104910134758707202 | /data/work/course5_v99/ 全量 | Completed RC=0 |
| v99-file-export | g5-v99-file-export-1 | 2105270145805012994 | 42,844 字符日志尾部（100K 截断）| Completed |
| v99-r10 OOM | g5-provenance-v99-readout-r10 | 2105013236648726530 | /data/work/v99_run_log10.txt | Failed RC=137 OOM |
| v98-dcs-r5 ortholog | g5-samap-v98-dcs-r5 | 2104988047516471297 | /data/work/v98_dcs_log5.txt | Failed（samalg import OK，gnnm 路径不一致） |
| v98-dcs-r10 OOM | g5-samap-v98-dcs-r10 | — | — | Failed RC=137（umap 未禁用） |
| local SAMap 合规 | 本地 local_samap3.py 修复版 | — | local_samap3_out.txt + 6 pred JSON | Completed，18 格全≤随机 |

## 7. 当前工具链状态

| 工具 | 位置 | 状态 |
|---|---|---|
| 本地 venv | .venv39/ (py3.9 + samap + samalg + hnswlib shim + anndata) | ✅ |
| 冻结评分器 | scripts/evaluate_cross_species_transfer.py | ✅ |
| v99 脚本 | scripts/dcs_provenance_v99.py | ✅（compact_summary 已修） |
| v98 DCS 脚本 | scripts/run_samap_compliant_v98_dcs.py | ⚠ build_gnnm 函数缺失（r8 截断问题） |
| 映射表 v1 | config/heart-celltype-map-v1.tsv | ✅ 冻结 SHA be98…3165 |
| reviewer 签名请求 | docs/reviewer-signoff-request-mapping-v1.md | ✅ 已备好 |
| ortholog 文件（本地） | ortholog/orth-MGI-HOM.rpt + human/mouse_orthos.txt | ✅ |
| ortholog 文件（平台） | /Files/wheelhouse/orth-MGI-HOM.rpt + orth-human-orthos.txt + orth-mouse-orthos.txt | ✅ |

## 8. 平台运维速查

| 项 | 值 |
|---|---|
| 提交 API | POST /stereonote/api/offline/save（AES stereonote） |
| 取消 API | POST /offline/subTask/cancel/<子任务taskId> |
| 日志 API | POST /offline/subTask/logs/<子任务taskId>（100K 截断） |
| resource_id | 259 = 1c 4g |
| PYTHONPATH | /data/work/pylibs（samap + samalg + hnswlib shim） |
| 中文炸 JSON | projectName 等字段用 ASCII |
| 表单 API | 404 持续，直连 /offline/save 是唯一提交路径 |
| notebook 后端 | 502/路径映射不通 → /data/work 不可逐文件读取 |

## 9. 停止条件（不可覆盖）

出现以下任一情况，立即停止并汇报，不自动重试：
- DCS 任务 OOM/137
- SHA 不匹配
- JSON 解析失败
- 连续两次同类导出失败
- 数字来源无法唯一确定
- 协议标签未预注册
- notebook/API 再次 502
- 需要用户或导师决定的科学口径问题

---

## 2026-10-02 执行进展（Flash 夜班，Claude 审阅待插入）

### 已完成

| 阶段 | 内容 | commit/证据 |
|---|---|---|
| Phase 0 | 状态冻结快照，112 tests | dce62b1 / docs/flash-phase0-snapshot-20261001.md |
| Phase 1(局部) | 4/6 核心文件**字节级**回收：manifest.json、environment.txt、command.txt、v99_mapping_embedded.json（SHA 全对表）；sha256.tsv 内容完整（字节序待 R1 闭环） | 37c4caf / results/pilot-v1/saturn-v99/raw/recovered-20261001/ |
| Phase 2 | ortholog_pca_local_v1.py Gate-2 重写（元组键→字符串键、active 排除、<1000 exit(2)、联合 PCA X 修复、全量落盘、smoke 守卫、zf 142 重复符号确定性去重） | d079824 + 17d354b |
| Phase 3 | smoke RC=0（8.1s）：18+18 文件、37/37 输出 SHA、逐细胞重算 acc/coverage/majority/confusion 全一致、无 NaN/重复 barcode；smoke 数字不进主表 | 17d354b / docs/flash-phase23-smoke-20261002.md |
| Phase 5 | SAMap v98 双变体同步修复：主流程接 load_species+assert_prefix_unique+assert_no_na_truth、truth_na>0 非零退出、included 语义+confidence、predictions/confusion 分离落盘、全量输出 SHA、嵌入键 X_samap_pca 回退；新增 3 个失败门测试，全套 112 tests OK | e351f59 |

### 进行中

- **Phase 1 R1 容器任务**：g5-v99-rec-r1（subtask 2105712313941725186，01:31:53 提交，1c4g）——至 02:25 仍 Submitted 排队（平台夜间 GPU 任务拥挤）。日志通道三次检查为空（未运行），无失败迹象。R2..Rn 载荷脚本已备好（scripts/g5_v99_rec_payload.py，按 R1 PREDPLAN 分组 ≤85KB/任务），解析器已备好（scripts/parse_v99_rec_log_v1.py）。

### 待 Claude 审阅（Gate 2/3/5 自检材料）

- Gate 2/3：docs/flash-phase23-smoke-20261002.md（含三条裁决问题）
- Gate 5：run_samap_compliant_v98_dcs.py 主流程调用链（load_species→assert_no_na_truth→SAM(adata_raw=)→assert_prefix_unique→SAMAP→run(NUMITERS=3,ncpus=1,umap=False)→truth_na 硬停→分方向评估）

### 未变blocked

- Phase 4 全量 PCA：等 Gate 2/3 放行（本地 .venv39，计划文本内授权的本地轻量运算）
- Phase 6 SAMap DCS：等 Gate 5 + 用户批准
- Phase 7 mapping 签认：等用户发导师

### R1 队列事件（2026-10-02 傍晚）

- g5-v99-rec-r1（2105712313941725186）自 01:31 起 **Pending 17 小时未调度**（startTime/instanceId 均空）——夜间 CPU 队列被大量 odms GPU 任务挤压。18:23 经用户在场确认后 `POST /offline/subTask/cancel/<id>` 取消成功（code 0）。
- 同 payload 重提为 **g5-v99-rec-r1b**（subtask `2105967078739628034`，18:24:13，一次性提交）。若再 starvation，停止重试，升级给用户向平台/老师询问 1c4g 队列状态。
- 备妥工具：`scripts/build_v99_rec_payload_task.py`（R2 分组提交构建器，AES 回路自测通过）+ `scripts/parse_v99_rec_log_v1.py`（R1 日志解析+SHA 验收）。
