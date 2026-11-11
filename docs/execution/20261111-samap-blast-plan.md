# SAMap BLAST 全同源图正对照 —— 执行方案

**日期**：2026-11-11
**目标**：目标②的后半 —— 「用 SAMap 官方 tutorial + BLAST 全同源图跑一遍，与原文差 ≤5 个百分点」。

---

## 一、我们目前做了什么（已查明）

**脚本**：`local_samap3.py`

```python
# 第 22 行、43 行、48 行：手工构建同源图
for line in open(BASE + '/ortholog/MGI_HOM_MouseHumanSequence.rpt', ...):   # human↔mouse
    ...
fh_raw = zfin(BASE + '/ortholog/human_orthos.txt')                          # 涉 zebrafish
fm_raw = zfin(BASE + '/ortholog/mouse_orthos.txt')

# 第 70-71 行：把自建图传进去
from samap.mapping import SAMAP
sm = SAMAP(sams, keys={'hu':'cell_type','ms':'cell_type','zf':'cell_type'}, gnnm=gnnm)
```

**→ 我们传的是自己用 MGI + ZFIN 建的「1:1 直系同源」图。**

**而 SAMap 官方流程是「不传 `gnnm`」**，让它自己用 **BLAST** 对蛋白组做互相搜索来建全同源图。

**所以正对照的核心改动只有一处：去掉 `gnnm=gnnm` 参数。**
但**代价在于要让 SAMap 能真的跑起 BLAST**。

---

## 二、依赖清单（本地实测结果）

| 依赖 | 本地现状 | 说明 |
|---|---|---|
| `samap` 包 | ✅ 已装在 `.venv39`（`site-packages/samap`） | `from samap.mapping import SAMAP` 可用 |
| **`blastp` / `makeblastdb`** | ❌ **无** | 必须装 BLAST+ |
| **SAMap 数据目录**（`~/samap`） | ❌ **不存在** | 官方流程会在此存蛋白组与 BLAST 库 |
| **物种蛋白组 FASTA** | ❌ **本地一个都没有** | human / mouse / zebrafish 全缺 |

**→ 本地跑 BLAST 正对照，需要：装 BLAST+、拿三份蛋白组。都是外部下载。**

---

## 三、两条可行路径

### 路径 A：在 DCS 平台跑（**推荐**）

**理由**：
1. 平台的 `SATURN--22` 镜像**可能已带 BLAST**（待查）；
2. 平台有网（虽然慢），能下蛋白组；
3. 平台 `/Files` 有 27 PB，放蛋白组没压力；
4. BLAST 是**计算密集型**，平台能给多核。

**要做的事**：
```bash
# 1. 查镜像里有没有 BLAST
which blastp makeblastdb; blastp -version

# 2. 查 SAMap 数据目录
ls -la ~/samap 2>/dev/null; python3 -c "import samap,os;print(os.path.dirname(samap.__file__))"

# 3. 若缺 BLAST → 装（conda 或直接下 NCBI 预编译包）
# 4. 让 SAMap 自己下载蛋白组并建图（首次会慢，因为 BLAST 三物种互搜）
# 5. 跑时不传 gnnm：
#    sm = SAMAP(sams, keys={...})     # ← 去掉 gnnm
```

**预估耗时**：BLAST 三物种互搜 + SAMap 建图，**数小时量级**（比 SATURN 训练更重）。

### 路径 B：本地跑

**需要**：
- 装 BLAST+（Windows 版有预编译包）
- 下三份蛋白组（Ensembl/NCBI，每份数百 MB）
- 本地 8 核跑 BLAST，**预计数小时到十几小时**

**不推荐**：下载慢（此前实测 PyPI 都不稳），且占用本地机器很久。

---

## 四、🔴 决定性发现（2026-11-11 18:50 读源码得出）—— 任务比预想的重

### 发现 1：不传 `gnnm` 确实走 BLAST 分支 ✅

`samap/mapping.py:142-151`：
```python
if gnnm is None:
    gnnm, gns, gns_dict = _calculate_blast_graph(...)       # ← 走 BLAST 路径
    gnnm, gns_dict, gns = _coarsen_blast_graph(gnnm, gns, names)
    gnnm = _filter_gnnm(gnnm, thr=0.25)
else:
    gnnm, gns, gns_dict = gnnm                               # ← 用传入的图
```
**确认：去掉 `gnnm` 参数会进入 BLAST 路径。**

### 发现 2：但 `_calculate_blast_graph` **不跑 BLAST，只读预先算好的表** 🔴

`samap/mapping.py:1052-1074`：
```python
def _calculate_blast_graph(ids, f_maps="maps/", eval_thr=1e-6, reciprocate=False):
    for i in range(len(ids)):
        for j in range(i, len(ids)):
            if i != j:
                if os.path.exists(f_maps + f"{id1}{id2}"):
                    fA = f_maps + f"{id1}{id2}/{id1}_to_{id2}.txt"    # 读表
                    fB = f_maps + f"{id1}{id2}/{id2}_to_{id1}.txt"
                elif os.path.exists(f_maps + f"{id2}{id1}"):
                    ...
                else:
                    raise FileExistsError(                             # 找不到就报错
                        "BLAST mapping tables with the input IDs ({} and {}) not found ...")
```

**→ 它要的是 `maps/<id1><id2>/<id1>_to_<id2>.txt` 这种预生成文件。**
**→ 找不到直接 `FileExistsError`，不会自动去跑 BLAST。**

### 发现 3：`.venv39` 里的 `samap` 包**根本没有跑 BLAST 的代码** 🔴

包里只有 4 个文件：`__init__.py` / `analysis.py` / `mapping.py` / `utils.py`。
里面与 BLAST 相关的只有三个函数：
- `_prepend_blast_prefix`（字符串处理）
- `_calculate_blast_graph`（**读表**）
- `_coarsen_blast_graph`（粗化图）

**没有任何 `blastp` / `makeblastdb` 的调用。**
→ **这个 pip 包自己跑不了 BLAST。**

### 这三条合起来意味着什么

**「让 SAMap 自己用 BLAST 建图」这个说法要修正**：
SAMap 的 BLAST **不在这个 pip 包里**，而要靠**官方仓库的独立脚本**（或按 tutorial 自己跑 BLAST+ 生成表）。

**所以 BLAST 正对照的完整依赖是**：

| # | 需要 | 现状 |
|---|---|---|
| 1 | `blastp` / `makeblastdb`（BLAST+ 可执行文件） | ❌ 本地无；平台待查 |
| 2 | 三物种蛋白组 FASTA | ❌ 全无 |
| 3 | **跑 BLAST 的脚本**（官方仓库的，或自己按 tutorial 写） | ❌ 只有 4 文件的 pip 包 |
| 4 | 把 BLAST 结果转成 `maps/<id1><id2>/<id1>_to_<id2>.txt` 的**正确格式** | ❌ 需先弄清格式 |
| 5 | 跑通后 SAMap 才读得到（`f_maps="maps/"` 是**相对路径**，注意 cwd） | — |

**⚠️ 第 4 条是最大风险**：`_calculate_blast_graph` 对表的格式有隐含要求
（`pd.read_csv(sep="\t", header=None, index_col=0)`，然后取 `A.columns=="10"` 之类）。
**格式不对会静默误解析——数字出来是错的，而且看不出来。**

**→ 所以在没有官方脚本/官方示例表可对照之前，不应该自己猜格式。**

---

## 四·补、修正后的结论

**这条正对照的难度，从我原先估的「改一行去掉 gnnm」修正为「需要完整搭一套 BLAST 流程」。**

**这解释了当初为什么我们手工建 `gnnm`** —— 因为跑 BLAST 流程的成本高，
所以用 MGI/ZFIN 的 1:1 同源替代。**这不是偷懒，是合理的工程折中——但它确实不是原文的做法。**

**建议的下一步（按性价比排序）**：
1. **先查平台镜像有没有官方 SAMap 仓库**（可能带 `run_blast` 之类脚本 + 示例 maps）
   —— 有就省掉自己写的风险；
2. 若没有，**去 SAMap 官方仓库拿到那套脚本**（而不是自己猜格式）；
3. 蛋白组与 BLAST+ 可执行文件按官方 tutorial 备齐；
4. **全部就绪后再投任务**（数小时量级）。

---

## 五、✅ 最终确认：我们从未跑过 BLAST（2026-11-11 19:00）

**读 `scripts/run_samap_compliant_v98.py`（437 行，我们的「合规模版」）**：

```python
# :277
def build_gnnm_from_orthologs():        # ← 手工从 MGI/ZFIN 直系同源建图
    ...
    return gnnm

# :349-350
gnnm = build_gnnm_from_orthologs()
sm = SAMAP(sams, keys={s: TRUTH_COLUMN for s in sams}, gnnm=gnnm)   # ← 传自建图
```

**→ 连我们标注为「compliant（合规）」的 v98 版本，也是传自建 `gnnm`、不走 BLAST。**

**所以可以确定地说：**
> **我们在 SAMap 这一侧，从未使用 BLAST 全同源图。**
> **v71（legacy `local_samap3.py`）和 v98（`run_samap_compliant_v98.py`）都是用
> MGI/ZFIN 的直系同源构建的 `gnnm`。**

**这对论文的意义**：与原文的可比性**在输入层面就不成立**——
原文用 BLAST 全同源图（含一对多、序列相似性加权），我们用 1:1 直系同源（二值）。

**这正是目标③「输入」维度要量化的东西**：
`SAMap 1:1 vs Compara vs BLAST` 三档的差异。

---

## 六、补充搜索结论（2026-11-11 19:00）

**在我方仓库内穷尽搜索「官方 SAMap 的 BLAST 脚本」，结果**：

| 位置 | 结果 |
|---|---|
| `.venv39/lib/site-packages/samap/` | 只有 4 个模块，**无 BLAST** |
| `wheelhouse/samap-1.0.16/`（源码分发包） | **同样 4 个模块**，`SOURCES.txt` 确认 |
| `wheelhouse/samap-1.0.16.tar.gz` | 同上 |
| 全仓库搜 `blastp` / `makeblastdb` / `blastn` | **0 处命中** |

**→ 结论：PyPI 上的 `samap` 包（无论 wheel 还是 sdist）都不含 BLAST 流程。
BLAST 步骤在 SAMap 的 GitHub 仓库里，不在分发包里。**

**→ 所以要做 BLAST 正对照，必须去 SAMap 官方仓库取那套脚本。**

**另一条线索（记录，未跟进）**：
`results/phase-20261010/review-packet/wrapper-B-run_samap_full_isolated.py.txt` 提到
「线上 WDL 部署脚本 `samap_script.py`（c0f05b89…，410 行权威版），
可从 `/Files/ResultData/Notebook/run_samap_compliant_v98_dcs.txt` 回捞」。
**那个文件在平台上，值得一查**（但按上面结论，它大概率也是自建 gnnm 的版本）。

---

## 七、修正后的完整依赖（5 项，全缺）

| # | 需要 | 现状 | 风险 |
|---|---|---|---|
| 1 | `blastp` / `makeblastdb`（BLAST+） | ❌ 本地无，**平台待查** | — |
| 2 | 三物种蛋白组 FASTA | ❌ 全无 | 下载慢 |
| 3 | **跑 BLAST 的官方脚本** | ❌ **PyPI 包里没有，要去 GitHub 拿** | 中 |
| 4 | **BLAST 结果 → `maps/<id1><id2>/<id1>_to_<id2>.txt` 的正确格式** | ❌ 未知 | **⚠️ 最大** |
| 5 | cwd（`f_maps="maps/"` 是相对路径） | — | 低 |

**⚠️ 第 4 条仍是最大风险**：格式不对 → `_calculate_blast_graph` 静默误解析
→ **数字是错的，且看不出来**。
**→ 在拿到官方脚本或官方示例 `maps` 之前，不应该自己猜格式。**

**建议顺序（性价比）**：
1. **先查平台镜像有没有官方 SAMap 仓库**（可能带脚本 + 示例 maps）；
2. 有 → 直接用；没有 → **去 GitHub 拿官方仓库**（不自己写）；
3. 备齐蛋白组与 BLAST+；
4. **全部就绪后再投**（数小时量级）。

**⚠️ 纪律不变**：这条做不通之前，**跨门负结果不得当生物学结论**。

---

## 四·二、仍然必须先确认的三件事（原「四」节内容，保留）

> 其中**第 1 条已在上面确认**（不传 `gnnm` 会进入 BLAST 分支），但**第 1 条的后续更严格了**：
> 它进入的 `_calculate_blast_graph` **只读预生成的表、不会自己跑 BLAST**，所以「走 BLAST 分支」
> ≠ 「会自动帮你跑 BLAST」。

1. **~~`gnnm` 去掉后 SAMap 会做什么~~** ✅ **已确认**：
   进入 `_calculate_blast_graph`，它**读 `maps/` 下的预生成表**；找不到就 `FileExistsError`。
2. **我们的 `sams`（SAM 对象）是按什么建的** ——
   官方流程要求每个物种先跑 `SAM`（含 `run_velocity` 等），
   我们是不是完整走了官方前置？**若不一致，正对照就不成立。**
3. **「与原文差 ≤5 个百分点」的原文数是多少** ——
   SAMap 论文报的是哪些方向、什么口径（accuracy？macro-F1？粗类还是细类？）。
   **口径不明确的对比没有意义**（这正是本课题的核心论点）。

**第 3 条尤其重要**：我们此前吃过「拿 union macro-F1 和原文 truth-only 类口径直接比」的亏
（见 `docs/execution/20261111-obsolete-numbers.md` 作废 6）。
**必须先确认原文的数是什么口径，再比。**

---

## 五、在五件事里的位置

| 件 | SAMap BLAST 正对照的位置 |
|---|---|
| ② 正对照 | **后半**：SATURN 那条已在跑；SAMap 这条是上面这个方案 |

**⚠️ 纪律提醒（目标原文）**：
> 「正对照失败则先 debug 实现，不加数据不烧 GPU」
> 「跨门负结果在拿到正对照前不得当生物学结论」

**→ SAMap BLAST 这条做不通之前，跨门（七鳃鳗↔鼠）那个负结果不能当生物学结论。**

---

## 六、建议的执行顺序

1. **等 SATURN 那个训练出结果**（定时器在盯）——先把「能拿到的一个正对照」拿到手；
2. 同时（不占 GPU/CPU）**只读地查平台的 BLAST 与 SAMap 环境**（上面路径 A 的第 1-2 步）；
3. 读 `samap/mapping.py` 确认无 `gnnm` 时的行为（路径 A 第 1 条）；
4. 查原文报的口径（路径 A 第 3 条）；
5. 都确认后**再投 BLAST 任务**（它是数小时量级，值得先确认好）。

**不建议现在直接开跑 BLAST**：依赖、前置、口径三件都还没确认，
**跑出来也不知道能不能用**——这正是「先确认再烧算力」的道理。

---

## 九、✅ 官方仓库与 BLAST 要求已确认（2026-11-11 20:00，第 71 轮）

**读 `wheelhouse/samap-1.0.16/PKG-INFO` 与 `README.md` 得出**：

    Home-page: https://github.com/atarashansky/SAMap
    Author:    Alexander J. Tarashansky (tarashan@stanford.edu)
    版本:      1.0.16

**README 原文明写**：
> **"NCBI BLAST must be installed for the commandline."**

**并给出安装步骤**：
    ncbi_blast_version='2.9.0'
    wget "ftp://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/${ncbi_blast_version}/ncbi-blast-${ncbi_blast_version}+-x64-linux.tar.gz"
    tar -xzvf "ncbi-blast-${ncbi_blast_version}+-x64-linux.tar.gz" "ncbi-blast-${ncbi_blast_version}+/bin/"

**官方使用方式（原文）**：
    git clone https://github.com/atarashansky/SAMap.git samap_directory
> "To run SAMap, use the `SAMAP` function in `samap/mapping.py`."

**→ 三条确认**：
1. **官方要求 BLAST+ 装在命令行**（与第 58 轮从源码读出的结论一致）；
2. **BLAST 相关脚本在 GitHub 仓库里**，不在 PyPI 包（包仍只有 4 个模块）；
3. **必做动作：git clone https://github.com/atarashansky/SAMap.git**，从仓库取官方 tutorial / BLAST 步骤。

**⚠️ 新卡点预判**：平台上 **clone GitHub 可能失败**
（实测：默认 PyPI 挂、清华源 403、直连 github.com:443 超时）。
→ 备选：**把仓库打包上传到 `/Files/`**（像 `saturn-src.tar.gz.txt` 那样），或本地 clone 后上传。

**这一步的信息已足够**：仓库地址、版本、BLAST 要求、安装步骤都明确。
**剩下的是「把 BLAST 跑起来」这个工程动作**（数小时量级）。
