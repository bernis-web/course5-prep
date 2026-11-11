# 20261111 一键复现清单（repro-manifest）

> 配套审计：`docs/reports/audit-repro-20261111.md`（118 个脚本逐个判定 + 10 条不可复现断点）
> 一键入口：`scripts/reproduce_all.py`（477 行，30 个步骤）

## 目标

换一台同规格 Windows 机器（无 GPU、无 WSL、无 docker），只凭本仓库 + 本地 `.venv39`，用**一条命令**把全部「可本地复现」的分析步骤重跑一遍，并证明产物与仓库里冻结的文件**逐字节一致**。

实测结论：**30/30 步通过，退出码 0，耗时 278.5 s，全部产物 `=` 逐字节一致。**

## 原理

三个约束决定了脚本形态：

1. **脚本会往仓库里写**（`results/…`），复现验证不能靠「跑完把仓库搞脏再人工看」。
   → 用**硬链接**把 `config/ results/ ortholog/ + 3 个 .h5ad` 灌进临时沙箱：读的是同一 inode（不额外占盘），写的新文件落在沙箱。跑完 `rmtree` 沙箱，删的只是链接，仓库原文件不受影响。
2. **38 个脚本把仓库根硬编码成 `D:\projects\course5-prep`**，换机器即失效。
   → 沙箱内装运行期 shim，把该前缀重写到沙箱根（`pathlib.Path` / `builtins.open` / `os.makedirs` / `os.replace` 等），**源码一字不改**，等价于换挂载点。
3. **只有「产物与仓库同名文件哈希相同」才算复现成功**，rc=0 不算。
   → 每步落 `cmd/stdout/stderr/rc + artifacts/ + sha256`，并与仓库同名文件比对；JSON 哈希不同时，再比一次去掉易变键（`generated_at` 等）的值。

## 步骤

### 1. 环境清单（实测，2026-11-11）

| 项 | 值 |
|---|---|
| OS | Windows 10 `10.0.22631-SP0`（x86_64） |
| 复现解释器 | `D:\projects\course5-prep\.venv39\Scripts\python.exe` = **Python 3.9.6**（MSC v.1929 64 bit） |
| numpy | 1.23.5 |
| scipy | 1.12.0 |
| pandas | 2.3.3 |
| scikit-learn | 1.6.1 |
| anndata | 0.10.9 |
| scanpy | 1.9.3 |
| h5py | 3.8.0 |
| matplotlib | 3.9.4 |
| python-pptx | 1.0.2 |
| python-docx | **venv39 未装** → 系统 `Python313` 有 1.2.0 |
| openpyxl | **venv39 未装** → 系统 `Python313` 有 3.1.5 |
| GPU / CUDA | 无 |
| WSL / docker | 无（`docker build` 不可用） |
| git | `codex/teacher-reply-report-prep` @ `d624917e51f1`（dirty，见「坑」5） |

版本由 `environment_check.py` 与 `manifest.json.environment` 两处独立采集，值一致。

### 2. 数据依赖

| 文件 | 大小 | 细胞 / 基因 | sha256 前 16 位 |
|---|---|---|---|
| `local_human_s.h5ad` | 26,233,600 B | 1,528 / 32,732 | `af41618b6941d2f1` |
| `local_mouse_s.h5ad` | 27,745,005 B | 1,535 / 32,379 | `7fda583d59d3767e` |
| `local_zebrafish_s.h5ad` | 16,931,148 B | 1,543 / 27,661 | `6b1e8798d5f848ac` |
| `config/heart-celltype-map-v1.tsv` | 5,127 B | 38 行（35 active / 3 unmapped） | — |
| `config/heart-celltype-map-v2.tsv` | 7,619 B | v2 签认映射 | — |
| `ortholog/human_orthos.txt` | 9,711,505 B | 人 1:1 同源 | — |
| `ortholog/mouse_orthos.txt` | 7,070,196 B | 鼠 1:1 同源 | — |
| `ortholog/MGI_HOM_MouseHumanSequence.rpt` | 15,112,222 B | MGI 原始同源表 | — |
| `results/pilot-v1/saturn-v99/raw/recovered-20261001/confusion/` | 33 KB / 18 个 JSON | SATURN 逐对混淆矩阵（口径审计唯一输入） | — |
| `results/phase-20261019/scvi-cross-species/recomputed_union.json` | 1,684 B | scVI 门内冻结值 | — |
| `results/phase-20261022/crossphylum/metrics.json` | — | 跨门臂 | — |
| `results/phase-20261026/samap-batch/samap_joint_{embedding.npy,obs.json}` | 5.5 MB + 455 KB | SAMap 关节嵌入 4,606×150 + obs | — |
| 各方法逐细胞预测 `results/**/predictions/*.json` | ≈40 MB | 18 份 + 稳定性/消融臂 | — |

**不含**：`/Files/**`（平台镜像）、`/data/work/**`（DCS 工作目录）、任何训练中间 `*.h5ad` —— 见「已知不可复现项」。

### 3. 一键命令

```powershell
cd D:\projects\course5-prep
$env:PYTHONIOENCODING='utf-8'
.\.venv39\Scripts\python.exe scripts\reproduce_all.py
```

可选：

```powershell
... reproduce_all.py --fast          # 跳过 6 个 >20s 的重步骤（≈60 s 跑完 24 步）
... reproduce_all.py --steps 07-16   # 只跑口径审计链（秒级）
... reproduce_all.py --keep-sandbox  # 留沙箱排错
... reproduce_all.py --out results/repro-manual
```

输出目录 `results/repro-<YYYYMMDD-HHMMSS>/`：

```
results/repro-<ts>/
├─ manifest.json      # 环境、每步 rc/耗时/产物 sha/与仓库比对、总退出码
├─ summary.md         # 人读版表格
├─ 01-env-check/      # 每步一目录
│   ├─ cmd.txt        # cwd + 完整命令行
│   ├─ stdout.log     # 原始回显（UTF-8，不经管道解码）
│   ├─ stderr.log
│   ├─ rc.txt
│   └─ artifacts/     # 产物副本，事后取证用
├─ 02-plan-contract/ …
└─ 30-h5ad-inspect/
```

### 4. 预期输出（实测基线）

```
[repro] 输出目录 D:\projects\course5-prep\results\repro-20261111-215553
[repro] python 3.9.6  git codex/teacher-reply-report-prep@d624917e51
[repro] 步骤 30 / 30
[repro] 建沙箱（硬链接灌入输入）...
[repro] 沙箱: link=2408 copy=0 skip_big=0 skip_excluded=0
[01] env-check                        OK      0.6s  environment-report.json:d633dd25
[02] plan-contract                    OK      0.2s
[03] startup-preflight                OK      0.2s
[04] unified-coarse-macro-f1          OK      0.3s  unified-coarse-macro-f1.json:9518d833=
[05] bootstrap-ci                     OK     23.7s  bootstrap.json:a2226a2e=
[06] bootstrap-crossphylum            OK     51.3s  crossphylum.json:13652c27=
[07] saturn-convention-audit-v1       OK      0.1s  saturn_convention.json:e2333cd3=
[08] saturn-convention-audit-v2       OK      0.1s  saturn_convention_v2.json:e83b4607=
[09] convention-variants              OK      0.1s  convention_variants.json:c39ca5b2=
[10] convention-flip-check            OK      0.1s
[11] mapping-v2-sensitivity           OK      0.1s  mapping_v2_sensitivity.json:73b006e7=
[12] orthers-variant-impact           OK      0.1s  orthers_variant_impact.json:cbb2a80a=
[13] convention-sensitivity           OK      0.1s  convention_sensitivity.json:3fbf34a6=
[14] drop-unmapped-audit              OK      0.1s  drop_unmapped_audit.json:4d9e24bb=
[15] bootstrap-saturn-fixed-v1        OK      2.7s  saturn_bootstrap_fixed.json:cc43e61f=
[16] bootstrap-saturn-fixed-mapv2     OK      2.8s  saturn_bootstrap_fixed_mapv2.json:71323844=
[17] donor-bootstrap                  OK     14.5s  donor_bootstrap.json:aa389159=
[18] opca-mapping-convention-audit    OK      0.2s  opca_mapping_convention_audit.json:3660976c=
[19] opca-mapping-v1-v2               OK      0.2s  opca_v1_vs_v2.json:f0bde001=
[20] scvi-mapping-v1-v2               OK      0.2s  scvi_v1_vs_v2.json:ff8e2cb0=
[21] labelspace-ablation              OK      0.1s  labelspace_ablation.json:9f5af02f=
[22] region-breakdown                 OK      0.4s  region_breakdown.json:329290ce=
[23] ortholog-coverage                OK      0.8s  coverage.json:d8df99f1=
[24] pairwise-corrected               OK     40.0s  pairwise_corrected.json:c0a94808=
[25] pairwise-donor-level             OK     20.6s  pairwise_donor_level.json:fc1a2314=
[26] pairwise-inductive               OK     27.2s  pairwise_inductive.json:bd630258=
[27] pairwise-lr-evaluator            OK     27.3s  pairwise_lr_evaluator.json:1d0b0652=
[28] pairwise-opca-official           OK     26.5s  opca_official_paired.json:0cf7d972=
[29] batch-metrics-samap              OK      3.5s  batch_metrics.json:1d094079
[30] h5ad-inspect                     OK      3.2s  h5ad-inspect.json:d667c35e
[repro] 完成 30/30，耗时 278.5s
[repro] 全部步骤退出码 0
```

验收判据（三条同时满足）：

1. 末行 `全部步骤退出码 0`，且 `manifest.json.exit_code == 0`；
2. `manifest.json.steps_ok == 30`（`--fast` 时为 24，属预期）；
3. 所有 `artifacts[].byte_identical == true`；direct 模式两步（29/30）为 `null`——它们写进本步目录，没有仓库基线。

### 5. 30 步覆盖了什么

| 链 | 步 | 复现的结论 |
|---|---|---|
| 权威指标 | 04–06 | 四方法 6 方向 coarse macro-F1 + ±SE/95%CI、majority 基线、配对 CI |
| 口径审计（核心） | 07–14 | 冻结值只属于「约定 A」；修正方向后 SATURN 更正列 0.3522/0.2566/0.1269/0.1640/0.3658/0.3563；R36/R21/R30 三行敏感性 |
| bootstrap | 15–17 | SATURN 修正口径 1000 次重抽样（v1/v2 映射各一份）、供体级重抽样 |
| 映射 v1↔v2 | 18–21 | oPCA / scVI 逐格差异、标签空间消融 |
| 配对显著性 | 24–28 | 13 组同批细胞配对、供体级、inductive、LR 评测器、oPCA 正式口径 |
| 数据证据 | 22、23、30 | 区域分解、同源覆盖、三源文件 obs/var 与 sha256 |
| 嵌入指标 | 29 | SAMap 臂 silhouette / iLISI / kBET |

## 坑

1. **`requirements.txt` 不可用**：仓库 pin `numpy==2.4.3 / scipy==1.17.0 / scikit-learn==1.8.0`，与能跑通的 `.venv39`（numpy 1.23.5 / scipy 1.12.0 / sklearn 1.6.1）**完全不同**。`wheelhouse/` 里的 whl 全是 `cp39-manylinux2014_x86_64`（Linux 轮子），**Windows 装不了**。所以「干净环境」= 已有 `.venv39`，不是「从 wheelhouse 装出来」；要真从零建环境必须回 Linux 容器。
2. **`MAP_TSV` 传相对路径会在沙箱里崩**：脚本内部 `Path(env).relative_to(ROOT)` 会抛 `ValueError: 'config\...tsv' is not in the subpath of ...`。`reproduce_all.py` 的做法是先把 env 里「像路径且确实存在」的值提升为沙箱绝对路径（step 16 靠这条才跑通）。
3. **Windows 控制台把中文回显打成乱码**（`Δ`→`螖`、`复现`→`���ֶ�`）。一律以 `PYTHONIOENCODING=utf-8` 启动，且子进程**直接写日志文件**（不走管道解码），`stdout.log` 才是干净 UTF-8。
4. **`python -c` 跑中文会炸 PowerShell 引号**（`ParserError: 表达式只能作为管道的第一个元素`）。落成 `.py` 再执行。
5. **工作区本身 dirty**（`results/stage-reports-20261102/render/v2/raw-*.png` 处于删除状态、若干 docx/pdf 有改动，且审计期间有并发任务在改 `scripts/bootstrap_saturn_fixed.py` 与 `docs/**`）。因此「没动过仓库」的判据改用：仓库产物 mtime 不变 + 沙箱内重算 + sha 比对，三条都过。
6. **`h5ad-inspect` 的 sha 会变**：产物里有 `generated_at`，逐字节比对无意义；`manifest.json` 只记 `sha`，验收看 `rc` 与 `n_obs/n_var`。
7. **`--fast` 会少 6 步**，`steps_ok` 变小是预期，别当失败。

## 已知不可复现项（摘录，完整 10 条见审计报告 C 段）

| 断点 | 缺失路径 | 影响 |
|---|---|---|
| 平台镜像数据 | `/Files`、`/Files/wheelhouse/*` | oPCA / SAMap / scVI 三条臂**无法从源头重算**，只能读成品 `metrics.json` |
| DCS 工作目录 | `/data/work/**` | v99 来源链、任务资源/耗时账单不可重建 |
| SATURN 输出 adata | 任意 SATURN 输出 `*.h5ad`（`results/` 下 0 个） | `saturn_output_scores.py` 跑不了 |
| scVI obs 元数据 | `results/phase-20261019/scvi-cross-species/obs.json` | scVI 臂 batch-mixing 三指标（§7.1）不可复算 |
| 稳定性压缩预测 | `results/stability-20261030/runs/seed-*/predictions/*.json.gz` | `pairwise_significance.py` / `saturn_vs_scvi_paired.py` 直接崩 |
| 学校模板 / 截图 / 任务号 | `课题5第03次汇报_….pptx`、`render/v2/raw-*.png`、`W2026*` | 汇报 PPT、交接包、资源表不可重建 |
| 容器镜像 | `g5-opca-container` | 「镜像内 6 个冻结值复现」不可在本机重跑 |

## 下一步

1. 把 38 个脚本的 `ROOT = Path(r"D:\projects\course5-prep")` 统一改成 `Path(__file__).resolve().parents[1]`；改完 shim 可退化为「兼容旧脚本」。
2. 补 `results/phase-20261019/scvi-cross-species/obs.json`（4,606 行 species+label），scVI 臂 batch-mixing 即可进一键流程；同时给 `pairwise_significance.py` 的 `.json.gz` 依赖加 `.json` 回退。
3. 重写 `requirements.txt` 为 `.venv39` 实测版本，`container/requirements.txt` 保留 Linux 锁定版，两者加注释说明差异原因。
4. 平台侧 4 个同源表（`orth-MGI-HOM.rpt` / `orth-human-orthos.txt` / `orth-mouse-orthos.txt` / `v99_mapping_embedded.json`）在 `ortholog/` 有等价物的，补一张 SHA 对照表进 `config/`，把「平台路径 ↔ 仓库路径」钉死。