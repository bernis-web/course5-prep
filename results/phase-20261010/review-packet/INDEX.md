# 审阅包索引（阶段 2 隔离层，2026-10-11）

> 自包含可审包，供平台侧独立审阅（GenPilot 容器无法访问本地 D: 盘）。
> 不含冻结数据（pilot-v1 的 h5ad/metrics 未打包）；仅含脚本文本、报告与实测证据。
> 以 `.txt` 后缀推送（平台 `dcs data push` 不收 `.py`）。
> 本包于 2026-10-11 17:4x 重建（第四轮审阅 4 项修正后的重算哈希）。

包内文件：**8 个 `.txt`** + 索引 `INDEX.md` / `INDEX.md.txt`。

| 文件 | SHA-256 | 说明 |
|---|---|---|
| `baseline-20261010.md.txt` | `3f658648190ca8145dfe16818f58e423bc085dc87e8af12e963784c3e66cb835` | 阶段 0 基线（覆盖风险一节＝隔离层由来） |
| `consultation-stage2-isolation.md.txt` | `8ee91e6d269069f008755f1080f5b2efa2da90724127c7af41f65a041477eb44` | 平台会商记录（含 MD5/SHA256 口径更正、三方版本拓扑） |
| `dry-run-evidence.txt` | `9728c3fe16819c5e37c00828c38a87d411a4d3c7d141b7e42fbeb2b8ef7170a2` | dry-run 与拒绝语义实测（2 正例 exit 0；10 负例 exit 2/3，真实退出码） |
| `genpilot-review-stage2.md.txt` | `036175ec34ea9f4a9cad823cd70f46c6c6a7e04a2dab11612afd94fe9db6fd5a` | GenPilot 替代审阅记录（可达性 BLOCK + 其纠正的哈希口径 + 平台侧越界实测 PASS） |
| `report-stage2-isolation.md.txt` | `85aab1786dedaeb468008d0cebe1bd986a6a3780e1dd311c8b1475cd98830af2` | **阶段 2 主报告**（§1–§7；§7.2 审阅轮次台账：6 轮 Claude + 1 轮 GenPilot，全部闭环）|
| `review-gate-status.json.txt` | `561654b9078daa67d63ad275120fd13ad29b94d861486beeb9518c707befd31c` | 阶段门状态（task1=completed / task2=not_started） |
| `wrapper-A-ortholog_pca_full_isolated.py.txt` | `48d79ad1c41d85ac3a68d806ec771e3dca7c8d927f4a27dc608ec8bb81bee83c` | 隔离 wrapper A（oPCA 全量）——**审阅对象 1** |
| `wrapper-B-run_samap_full_isolated.py.txt` | `6f1385cd12d464fc43d392d8fc04a7efaeb5b5854e0d14854773c6963cfe26fa` | 隔离 wrapper B（SAMap 全量）——**审阅对象 2** |
| `review-archive.md.txt` | `0e9d2b0c20f3ae26f4ae484b32af6bd28e3caec10eb65ede7b277bd29c535525` | 六轮 Claude 审阅 + 一轮 GenPilot 替代审阅的原文归档 |

## 审阅人可自行复现的命令

```bash
.venv39/Scripts/python.exe scripts/ortholog_pca_full_isolated.py --dry-run   # 期望 PREFLIGHT|18/18 exit=0
.venv39/Scripts/python.exe scripts/run_samap_full_isolated.py --dry-run     # 期望 PREFLIGHT|20/20 exit=0
.venv39/Scripts/python.exe scripts/ortholog_pca_full_isolated.py --dry-run --out results/phase-20261010/A-smoke  # exit=3
.venv39/Scripts/python.exe scripts/ortholog_pca_full_isolated.py --dry-run --out results/pilot-v1/x              # exit=3
.venv39/Scripts/python.exe scripts/ortholog_pca_full_isolated.py --dry-run --out results/PILOT-V1/x             # exit=3
(cd results && ../.venv39/Scripts/python.exe ../scripts/ortholog_pca_full_isolated.py --dry-run --out pilot-v1/x)  # exit=2
```

重建时间：2026-10-11T17:30:45
