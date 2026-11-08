# Phase 0 只读审阅结果（2026-10-10）

审阅对象：`docs/execution/20261010-phase0-review-request.md` 列出的 5 项核对内容。
审阅性质：只读复核。未运行模型、未提交 DCS、未训练、未启动 GPU、未充值、未读取或输出任何凭据。

环境：Windows 10.0.22631 · PowerShell 7.6.6 · git 2.53.0.windows.2 · Python 3.9.6（`.venv39`）· 审阅时间 2026-10-10T15:42:12+08:00

**重要限定**：本记录是本地只读复核，不等同于 Claude/Flash 外部反方审阅。审阅通道现状见 `docs/execution/20261010-review-channel-check.md`，`results/phase-20261010/review-gate-status.json` 的 `status` 仍为 `pending`。

---

## 1. Phase 0 是否确实只读，是否没有训练 / DCS 提交 / GPU / 充值 —— 通过

- `results/phase-20261010/run_scope.json:7-10`：`no_training`、`no_platform_submission`、`no_gpu`、`no_recharge` 四项均为 `true`；`:12-13` 明确 `frozen_results_root=results/pilot-v1` 与 `new_results_root=results/phase-20261010` 分离。
- `results/phase-20261010/` 下只有 `run_scope.json`、`baseline/git-status.txt`、`baseline/input-sha256.tsv`（12:34 新增的 `review-gate-status.json` 属审阅通道记录），没有任何提交产物、训练产物、费用或 GPU 记录。
- 全仓 2026-10-10T11:04:48 之后新增的文件全部是 Phase 0 / 交接 / 审阅通道文档，没有 DCS payload 或模型输出。
- `results/pilot-v1` 下**没有任何文件**的 mtime 晚于 11:04:48（`Get-ChildItem -Recurse | Where LastWriteTime -gt 快照时间` 返回空），冻结目录确实未被触碰。
- 本次复核未读取、未打印任何 token、密码、cookie、API key 或凭据。

## 2. `input-sha256.tsv` 的 SHA 是否与当前文件一致 —— 通过（11/11）

方法：对 TSV 中每一行用 `Get-FileHash -Algorithm SHA256` 重算，并同时比对 `size_bytes`。

| 文件 | size | sha256 |
|---|---|---|
| `results/pilot-v1/ortholog-pca-v98/manifest.json` | 6212 匹配 | 匹配 |
| `results/pilot-v1/ortholog-pca-v98/metrics.json` | 34929 匹配 | 匹配 |
| `results/pilot-v1/ortholog-pca-v98/confusion/coarse_human_to_mouse.json` | 809 匹配 | 匹配 |
| `results/pilot-v1/ortholog-pca-v98/predictions/coarse_human_to_mouse.json` | 1283386 匹配 | 匹配 |
| `results/pilot-v1/samap-v98/wdl-run/extracted/manifest.json` | 871 匹配 | 匹配 |
| `results/pilot-v1/samap-v98/wdl-run/extracted/metrics.json` | 6611331 匹配 | 匹配 |
| `results/pilot-v1/saturn-v99/raw/recovered-20261001/manifest.json` | 4761 匹配 | 匹配 |
| `results/pilot-v1/saturn-v99/raw/recovered-20261001/metrics.json` | 43486 匹配 | 匹配 |
| `results/pilot-v1/saturn-v99/raw/recovered-20261001/metrics.content.json` | 38930 匹配 | 匹配 |
| `results/pilot-v1/saturn-v99/raw/recovered-20261001/sha256.tsv` | 4581 匹配 | 匹配 |
| `config/heart-celltype-map-v1.tsv` | 5127 匹配 | 匹配 |

结果：**11/11 匹配，0 不匹配**。与 `docs/execution/20261010-task1-preflight.md:9` 的记录一致。

## 3. oPCA v98 / SAMap v98 / SATURN v99 recovered 的目录与口径描述 —— 通过（附 3 条附注）

- **oPCA v98**：40 files / 18,098,994 bytes，`predictions` 18 份、`confusion` 18 份，另有 `command.txt`、`environment.json`、`manifest.json`、`metrics.json`。与 `input-sha256.tsv:15`、`20261010-baseline.md:22` 完全一致。
- **SAMap v98 extracted**：21 files / 12,730,056 bytes，构成 = 18 份方向×层级 JSON + `environment.txt` + `manifest.json` + `metrics.json`。与 `input-sha256.tsv:16`、`20261010-baseline.md:23` 一致。
  - 附注 A：`20261010-baseline.md:23` 只列了 18 份结果 + manifest + metrics，漏记 `environment.txt`。属描述不完整，不属错误，建议补齐。
- **SATURN v99 recovered**：34 files / 350,869 bytes。实际构成：`manifest.json`、`metrics.json`、`metrics.content.json`、`sha256.tsv`、`command.txt`、`environment.txt`、`_extraction-report.json`、`v99_mapping_embedded.json`、18 份 confusion、`files-channel/`（2 文件）、`payloads/`（6 文件）。
  - 附注 B（实质限制）：本地逐细胞 payload **只有 6 个 coarse 方向**（`p1_coarse_mouse_to_human` … `p6_coarse_human_to_mouse`）；`exact` / `fine` 只有 confusion，没有逐细胞 payload。因此 SATURN 在本地**无法**做 exact/fine 逐细胞复算。`20261010-baseline.md:24` 的"部分 payload"表述准确，但 Task 2 若把 SATURN 纳入逐细胞复算，必须先补数据。
  - 附注 C：`recovered-20261001/manifest.json:27` 用的是 `candidate_hashes` 字段名，`:2` 为 `protocol_label=transductive_formal_reassessment`。未发现 candidate 被写成 confirmed。
- **v97g**：`results/pilot-v1/saturn-v97g` 下只有 `raw/task-metadata.json`（1661 B），**没有** predictions / confusion。`20261010-baseline.md:31` 与 `20261010-handoff-to-next-agent.md:33` 的"日志级数字"说法成立。

## 4. 科研口径（transductive / label-free / labels 与 ref_labels / keys=cell_type / v97g） —— 通过（1 处需补充措辞）

- **transductive/in-sample**：`ortholog-pca-v98/manifest.json:2`、`samap-v98/.../manifest.json:7,11`、`saturn-v99/.../manifest.json:2` 三处均为 `transductive_formal_reassessment`。与 `20261010-baseline.md:29` 一致，未见任何写成泛化或 inductive 的位置。
- **oPCA label-free**：口径方向正确，但表述需要收窄，见 F2。代码事实：`scripts/ortholog_pca_local_v1.py:254` `X_joint = np.vstack([Xs, Xt])`，`:258` `PCA(n_components=NPCS, random_state=SEED).fit_transform(X_joint)` —— PCA 载荷在 **src + tgt 联合矩阵**上拟合，属 transductive 投影；PCA 本身不使用标签，所以"label-free"只在**表示层**成立。`:266` `knn.fit(Z[m_s][keep_r], ytr[keep_r])` 的分类头**使用 reference 标签**。笼统写"oPCA 是 label-free 方法"容易被读成"全流程无标签且可 inductive"。
- **SATURN `labels` / `ref_labels`**：`docs/superpowers/plans/2026-10-10-course5-genpilot-dcs-longrun.md:187` 与 `scripts/build_final_report.py:124` 的写法（miner 用 `labels`，`ref_labels` 仅输出列/评估真值）与 `scripts/dcs_provenance_v99.py:362`（评估真值取 `adata.obs["ref_labels"]`）一致。`build_final_report.py:124` 已带"运行时源码版本与训练命令待核实"限定，未把待核实项写成结论。通过。
- **SAMap `keys=cell_type`**：`scripts/run_samap_compliant_v98_dcs.py:28` `TRUTH_COLUMN = "cell_type"`，`:351` `SAMAP(sams, keys={s: TRUTH_COLUMN for s in sams})`，`:435` 显式声明 `label_aware`。与 `20261010-baseline.md:30` 一致。
- **SAMap 无原生冻结图投影、只能称 SAMap-approx**：`plan:118`、`plan:130` 已写明，Phase 0 未越界。
- **SATURN inductive 仍 blocked**：`plan:18`、`plan:119` 保持，Phase 0 未改变其状态。
- **C2 最多 54 格**：`plan:130` 与 `20261010-handoff-to-next-agent.md:34` 一致，未宣称 81 格可执行。

## 5. 是否存在会覆盖 `results/pilot-v1`、绕过审批门或提前训练的路径 —— 需修改

存在的覆盖路径（均为既有脚本，非 Phase 0 新增）：

- **P1（最严重）** `scripts/ortholog_pca_local_v1.py:158`
  `out = BASE / "results" / "pilot-v1" / ("ortholog-pca-smoke" if smoke else "ortholog-pca-v98")`
  存在性守卫只在 smoke 分支（`:159-160`）。**全量模式没有任何守卫**：不带参数直接运行就会把 `manifest.json` / `metrics.json` / 18 份 predictions / 18 份 confusion 全部覆盖到冻结目录，且不会有任何提示或报错。
  `20261010-baseline.md`、`run_scope.json`、`20261010-task1-preflight.md` 均未记录这条。
- **P2** `scripts/run_samap_compliant_v98.py:249-250`
  `output_dir = root / "results" / "pilot-v1" / "samap-v98"` + `mkdir(parents=True, exist_ok=True)`，无守卫，重跑即覆盖冻结的 SAMap 结果。
- **P3** `scripts/extract_v99_from_logs_v1.py:17`、`scripts/parse_v99_rec_log_v1.py:21`
  `RAW = Path(r"D:\projects\course5-prep\results\pilot-v1\saturn-v99\raw")`，重跑会重写 recovered 目录。
- **P4** Task 1 的 `--smoke` 路径：`20261010-task1-preflight.md:13-14` 已识别，`:18-25` 已提出隔离 wrapper，该条已被覆盖。

未发现的部分：

- 没有绕过审批门的自动提交路径（plan Task 5/Task 7 的审批单要求仍在，Phase 0 未生成 DCS payload）。
- 没有提前训练路径（未调用 SATURN 训练；`wheelhouse/saturn-src` 仅为 tracked-modified 工作树状态）。
- Phase 0 自身没有执行任何覆盖动作（见第 1 项）。

判定：P1/P2/P3 是既有脚本的覆盖面。在任何"全量复算/重跑"发生之前必须先有守卫或隔离输出，否则一次误跑就会摧毁整条证据链所依赖的冻结基线。因此本项判为**需修改**。

---

## 附加发现（影响 Task 1 验收口径）

**A1. `abs_diff <= 1e-12` 必须写明比较精度。**
冻结 `metrics.json` 中 `acc` / `majority` / `shuffle_p` / `coverage_q` 都是 4 位小数（`scripts/ortholog_pca_local_v1.py:315-318` 用 `round(x, 4)` 写入）。本地重算若拿全精度值直接与 4 位小数的冻结值比，差值约 1e-5，会触发"立即停止"的**假警报**。Task 1 验收必须写明：重算后按与冻结文件相同的精度取整再比较，或逐字段声明容差。

**A2. 冻结侧 18 格内部一致性已核对（只读）。**
我用混淆矩阵独立复核了全部 18 格：

- 18/18：混淆矩阵条目计数之和 == `n_q`
- 18/18：`round(diag / n_q, 4)` == 冻结 `acc`（最大差 0）
- 18/18：`|acc × n_q − diag| < 0.5`

这为 Task 1 的"混淆矩阵对角线 + `accuracy × n_q` 双重核对"提供了冻结侧基线，Task 1 只需复现这些值。

**A3. git 状态计数漂移是正常的。**
`20261010-baseline.md:12-15` 记录 228 条（staged 0 / tracked unstaged 29 / untracked 199）；当前重算为 230 条（staged 0 / ` M` 29 / `??` 201）。多出的 2 条 untracked 正是 Phase 0 之后自己新建的 `docs/execution/` 与 `results/phase-20261010/`。HEAD `8b597d788352009609688e28c7f2ed23a0358f17`、分支 `codex/teacher-reply-report-prep` 与 `:10-11` 一致。建议在 baseline 注明"计数为 11:04:48 时点快照"。

---

## 必须修正项

| 编号 | 对应项 | 修正内容 |
|---|---|---|
| F1 | 第 5 项 | 在 `docs/execution/20261010-baseline.md` 增补覆盖面记录：列出 P1/P2/P3 三处写入 `results/pilot-v1` 的脚本与行号；明确 Task 1 走隔离 wrapper（`20261010-task1-preflight.md:18-25` 已提出），Task 2 之前必须先有 `--out` 参数或等价副本，且目标目录已存在时硬停止。 |
| F2 | 第 4 项 | 收窄 label-free 表述。建议写法："oPCA 的表示层不使用标签（label-free）；v98 的 PCA 载荷在 src+tgt 联合矩阵上拟合（`scripts/ortholog_pca_local_v1.py:254-258`），因此是 transductive 投影，不得写成 inductive；kNN 分类头使用 reference 标签（`:266`）。" |
| F3 | 附加 A1 | 在 `docs/execution/20261010-task1-preflight.md` 的验收条目补精度说明：与冻结值比较前，先按冻结精度（4 位小数）取整。 |
| F4（可选） | 附加 A3 | 在 `20261010-baseline.md` 注明 git 计数为时点快照。 |

---

## 结论

第 1、2、3、4 项通过；第 5 项需修改。在 F1–F3 落地并复核之前，不进入 Task 1，不运行 smoke，不提交 DCS，不训练，不启动 GPU，不充值。

verdict: REVISE
