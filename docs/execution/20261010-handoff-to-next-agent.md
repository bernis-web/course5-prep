# 课题5执行交接（2026-10-10）

工作目录：D:\projects\course5-prep  
分支：codex/teacher-reply-report-prep  
基线 HEAD：8b597d788352009609688e28c7f2ed23a0358f17

## 当前结论

项目处于 Phase 0 基线冻结、等待 Claude/Flash 反方审阅。尚未启动 Task 1 smoke；没有新的 DCS 提交、训练、GPU 任务或充值。下一步必须先读取 docs/execution/20261010-phase0-review-request.md，完成只读审阅并返回最后一行：

    verdict: PASS

没有 PASS 就停止，不运行 smoke、不训练、不调用 DCS/GenPilot。

## 已有证据

- docs/execution/20261010-baseline.md
- docs/execution/20261010-phase0-review-request.md
- docs/execution/20261010-task1-preflight.md
- docs/superpowers/plans/2026-10-10-course5-genpilot-dcs-longrun.md
- results/phase-20261010/run_scope.json
- results/phase-20261010/baseline/git-status.txt
- results/phase-20261010/baseline/input-sha256.tsv

input-sha256.tsv 表头以下 11 个文件已重算，11/11 匹配。当前边界：no_training=true、no_platform_submission=true、no_gpu=true、no_recharge=true；不得覆盖 results/pilot-v1。

## 不可改变的科研口径

1. 既有跨物种结果是 transductive/in-sample，不是泛化或 inductive。
2. oPCA 是 label-free 参考方法，但只限于表示层（PCA 载荷不用标签，标签只在评估 KNN 用）；v98 的 PCA 在 src+tgt 联合矩阵上拟合，是 transductive 投影，不得写成 inductive。
3. SATURN 默认配置下训练使用 labels；ref_labels 主要用于输出/评估。源码有默认关闭的 --use_ref_labels 开关（train-saturn.py:70,100-101,1025）可把它送进 miner，原始训练命令待核实，所以不能笼统写成"ref_labels 参与训练"。
4. SAMap 当前是 keys=cell_type 的 label-aware 口径；没有原生冻结图投影，后续只能称 SAMap-approx 或近似 inductive。
5. v97g 是日志级数字，不能伪造逐细胞 predictions/confusion，也不能把 candidate/provenance 写成 confirmed。
6. SATURN inductive 是源码级 blocked；C2 当前最多 54 格：oPCA 27 + SAMap-approx 27，SATURN 27 格不在可执行集合。
7. 单细胞优先，只筛 cell_or_nuclei == cell；单核后置小规模对照；空间数据不进入主评估。
8. 没有正式统计检验时只写数值更高/方向性差异，不能写显著优于或泛化能力更强。

## PASS 后执行顺序

### Task 1：零成本最小 smoke

只做 human→mouse/coarse，不做三物种全量或六方向全量。输出必须放新目录 results/phase-20261010/A-smoke/，绝不能删除或覆盖旧目录 results/pilot-v1/ortholog-pca-smoke/。生成 manifest、command、environment、输入/输出 SHA、metrics、confusion 和逐细胞预测表。用混淆矩阵对角线与 accuracy×n_q 双重核对，并要求与冻结数字 abs_diff <= 1e-12；任意差异立即停止。完成后写阶段报告并再次交 Claude/Flash 审阅。

### Task 2：A 档全量本地复算

Task 1 与复审通过后再做，使用新隔离目录，不覆盖 pilot-v1；保留协议、标签空间、分母、coverage 和 provenance。

### Task 3：负控与方法对照

优先本地零费用：ortholog-PCA 统一评分、SAMap v98 只读核对、shuffle/majority/ceiling/seed 对照。label-free 与 label-aware 不可直接排名。每阶段都要有 manifest、命令、环境、哈希和复审。

### Task 4：DCS/GenPilot 小规模测试

仅在本地证据链和审批门通过、用户确认资源后执行；单细胞优先，一次性提交，不自动重试、不擅自加资源、不充值。任务 Pending/失败只做一次状态检查，随后停止并汇报，禁止轮询死循环。

### Task 5：单核对照

单细胞主结论稳定后才做小规模单核，不能混入单细胞主 benchmark，也不做空间组。

## 已知问题

- scripts/ortholog_pca_local_v1.py --smoke 固定写入旧目录，旧目录已存在；不能删除/覆盖，需 wrapper 或副本重定向到 A-smoke，并限制 human→mouse/coarse。注意同一脚本 **全量模式**（第 158 行）无守卫直写 results/pilot-v1/ortholog-pca-v98，禁止直接运行；同类风险还有 run_samap_compliant_v98.py:249 与 extract_v99_from_logs_v1.py:17，完整清单见 docs/execution/20261010-baseline.md 的“覆盖风险”一节。
- Claude/Flash CLI 可能仍报模型不可用；不要改配置、碰凭据或无限重试。用用户已恢复的 UI、zcode 或 GenPilot 读取审阅请求；仍以明确 verdict: PASS 为门。
- SATURN inductive 需要独立方案和审批，不得作为默认 GPU 任务提交。

## 阶段汇报目标

按 8–10 次汇报拆分：Phase 0 协议、smoke、A 档全量、指标来源/分母、三方法差异、负控/稳定性、DCS 小规模单细胞、单核对照、完整 PPT/Word、老师意见修订。每轮产出证据和 Claude/Flash 反方审阅后暂停等待老师反馈。

## 禁止事项

不 reset/checkout/clean，不删除或覆盖既有改动；不覆盖 results/pilot-v1；不把 transductive 写成 inductive；不把日志级 candidate 写成 confirmed；不自动提交/取消重提/扩大 DCS；不读取、保存或打印 token、密码、cookie、API key 或凭据。

## 回报格式

阶段：
实际执行：
产物路径：
证据/哈希：
测试：
Claude/Flash 结论：
DCS/GenPilot 状态：
阻塞：
是否进入下一阶段：是/否

当前交接点：先完成 Phase 0 只读反方审阅；没有 PASS 就停在这里。
