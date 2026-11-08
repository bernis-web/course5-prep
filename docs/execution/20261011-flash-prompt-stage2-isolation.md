# 给 Flash 的提示词 · 阶段 2 第一步（隔离层，不跑全量）

> 用法：整段复制给 Flash/zcode。本文件是副本，便于直接指向路径。

```text
工作目录：D:\projects\course5-prep
当前 HEAD：8b597d788352009609688e28c7f2ed23a0358f17（分支 codex/teacher-reply-report-prep）

## 本阶段目标
课题5 阶段 2 的第一步：**为 A 档全量复算建立输出隔离层**。
只做隔离与预检，**不跑全量复算**。

## 先读（只读，不修改）
1. docs/superpowers/plans/2026-10-10-course5-master-roadmap-flash.md   ← 总纲，冲突时以它为准
2. docs/superpowers/plans/2026-10-10-course5-genpilot-dcs-longrun.md   ← 阶段细则
3. docs/execution/20261010-baseline.md        ← 尤其"覆盖风险"一节
4. docs/execution/20261010-task1-preflight.md ← 阶段 1 的隔离做法与预检清单
5. docs/execution/20261010-task1-a-smoke-report.md ← 阶段 1 成果与已知项
6. docs/execution/20261010-master-roadmap-review.md ← 路线图审阅记录
7. results/phase-20261010/review-gate-status.json

## 背景事实（已核实，可直接采信，但你可以自己复核）
- 阶段 0、阶段 1 已完成并通过外部审阅。阶段 1 产物在 results/phase-20261010/A-smoke/：13 个文件，verification.json 16/16 通过，混淆矩阵与逐细胞预测表与冻结产物**逐字节相同**。
- 权威脚本 scripts/ortholog_pca_local_v1.py 的 SHA-256 是
  6582d8736c3570f3de23ed36cb57c9cf58f6190c4730c3d39e29928415fd0c44，
  等于冻结 ortholog-pca-v98/manifest.json 记录的 script_sha256。
  **不得修改这个文件**，否则会切断"它就是产出冻结数字的那个脚本"的溯源链。
- 危险路径（当前无守卫）：
  * scripts/ortholog_pca_local_v1.py:158 —— 全量模式 out = results/pilot-v1/ortholog-pca-v98，存在性守卫只在 --smoke 分支（:159-160）。
  * scripts/run_samap_compliant_v98.py:249-250 —— output_dir 硬编码 results/pilot-v1/samap-v98，mkdir(parents=True, exist_ok=True)，无守卫。
- 阶段 1 的隔离做法可复用：scripts/ortholog_pca_task1_isolated.py
  （SHA-256 71ab5642ad8e8a964717ad738c7f60524f9d1372fcc5bbc534cf63c64d7002ed）。
  它不改权威脚本，而是：读源码 → 施加"每个锚点必须恰好匹配一次"的文本补丁 → 把补丁后源码落盘到输出目录再执行 → 把完整补丁 diff 写进 wrapper-provenance.json。

## 本阶段只做
1. **只读复核阶段 1**：确认 review-gate-status.json 的 task1=completed / status=passed；A-smoke/ 的 13 个文件；verification.json 的 16/16；predictions/confusion 与冻结产物的 SHA 一致。
   **不得重跑阶段 1，不得新建第二个默认 A-smoke/ 目录。**
2. **为全量复算建立隔离层**，二选一：
   (a) 新增隔离 wrapper（推荐，沿用阶段 1 的模式），或
   (b) 为脚本新增 --out 参数。
   无论选哪种，scripts/ortholog_pca_local_v1.py 与 scripts/run_samap_compliant_v98.py 都必须保持**字节不变**。
3. 隔离层必须满足：
   - 输出只写 results/phase-20261010/A-full-<timestamp>/（SAMap 用对应的独立目录）；
   - **第一步就硬拒绝**已存在或非空的目标目录（非 0 退出码），绝不覆盖；
   - 拒绝任何解析后落在 results/pilot-v1 内的输出路径；
   - 执行前预检：断言 ortholog/ 与 3 个直系同源文件、config/heart-celltype-map-v1.tsv、三个 h5ad 全部存在，BASE 指向仓库根，层级/方向集合符合预期；**预检必须在创建输出目录之前完成**；
   - 产物含 manifest.json / command.txt / environment.txt / metrics.json / confusion / 逐细胞 predictions / sha256.tsv / 隔离 provenance（脚本 SHA、补丁或参数、输入 SHA、输出 SHA）。
4. 跑 --dry-run 形式的预检并留记录：**不执行模型、不创建输出目录**。
5. 写阶段报告并停止。

## 本阶段不做
- 不跑全量复算（不执行 6 方向 × 3 层级）。
- 不提交 DCS、不调用 GenPilot、不训练、不启动 GPU、不充值。
- 不修改 / 删除 / 覆盖 results/pilot-v1 的任何文件。
- 不修改 scripts/ortholog_pca_local_v1.py 与 scripts/run_samap_compliant_v98.py。
- 不 reset / checkout / clean，不删除既有未提交改动。
- 不读取、打印或保存任何 token、密码、cookie、API key、凭据或环境变量值。
- 不新建第二个默认 A-smoke/ 目录。

## 环境
- Python 用 D:\projects\course5-prep\.venv39\Scripts\python.exe（3.9.6；numpy 1.23.5 / anndata 0.10.9 / scanpy 1.9.3 / sklearn 1.6.1）。
- 注意：Python 3.9 的 Path.write_text **没有** newline 参数（3.10 才加）。要保证"落盘字节哈希 == 记录的文本哈希"，直接写字节
  （write_bytes(x.encode("utf-8"))）；否则 Windows 会把 \n 翻成 CRLF，同一产物里会出现两个都自称"源码哈希"的不同值
  —— 阶段 0 审阅第三轮发现的 F1 就是这么来的。

## 完成后必须输出
做了什么 / 产物路径 / 证据（SHA、预检项数、退出码）/ 通过-需修改-阻塞 / 费用与任务状态（本阶段应为 0）/ 下一阶段前置条件。

## 然后做 Claude 反方审阅（必做）
调用方式（stdout 与 stderr 必须分开保存，否则警告会混进正文）：

  claude -p "<审阅提示词>" --allowedTools "Read,Glob,Grep,Bash,PowerShell" --disallowedTools "Edit,Write,NotebookEdit"

要点：
- **不加** --model 覆盖。输出里若出现 "isn't described by this version's model catalog" 或
  [claude-code:unrecognized_model]，那是 **stderr 警告，不是失败**（退出码 0 即为正常）。
  项目曾把这条警告误判成"通道不可用"，见 docs/execution/20261010-review-channel-check.md 的"更正"一节。
- 要求 Claude 逐项给 PASS / REVISE / BLOCK，引用文件与行号，并**自己动手重算**，不得采信你的自述。
- 明确要求它验证：两个权威脚本字节未变、隔离层真的拒绝非空目录、拒绝写进 results/pilot-v1、
  预检覆盖全部输入路径、产物清单完整。
- Claude 给 REVISE 就先修正再复审；给 BLOCK 就停止并汇报，不自行越门。

## 停止条件（命中任一立即停止并汇报）
- 任何操作会覆盖 results/pilot-v1 或既有 A-smoke/。
- 隔离层无法证明"目标目录已存在即拒绝"。
- 预检发现输入缺失或 BASE 解析错误。
- 需要修改两个权威脚本才能实现隔离。
- Claude 审阅给 BLOCK。

## 明确停止点
本阶段在"隔离层已建好、预检通过、Claude 审阅 PASS"处停止。
**全量复算是下一步，不在本提示词范围内**；未拿到本阶段 PASS 之前不得运行全量模式。
```
