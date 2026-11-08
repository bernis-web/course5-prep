# 会话状态快照（供上下文压缩后无缝续接）

> 生成时间：2026-10-18 12:3x
> 用途：上下文被自动压缩后，先读本文件即可继续任务，无需回溯长对话。

---

## 一、当前在跑的任务

| 项 | 值 |
|---|---|
| 任务号 | **`W202610180071516`** |
| 实体 ID | `scvi-xspecies-r2` |
| 流程 | **`scvi_cross` v1.0.0**（本次新建） |
| 状态 | 待分析（提交于 2026-10-18 12:18） |
| 输入 | `script_txt`=`/Files/ResultData/Notebook/scvi_cross_species.txt`（19,796 B）<br>`pylibs_tar`=`/Files/ResultData/Notebook/pylibs_full.tar.gz`（200.80 MB） |
| 输出 | `/Files/ResultData/Workflow/<taskId>`（平台默认） |
| 费用上限 | 1 元 |

**重复提交的 `W202610180071475` 已通过 `POST /api/task/dcsTask/cancelTasks` 取消，状态「取消」，未消耗算力。**

---

## 二、`scvi_cross` 流程的设计（关键，勿丢）

新建流程，未修改 `opca_v2`。命令段：

```bash
set -e; set -o pipefail
tar xzf ${pylibs_tar}
export PYTHONPATH=$PWD/pylibs_full:$PYTHONPATH
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
cp ${script_txt} ./scvi_script.py
export OPCA_OUT_ROOT=$PWD
mkdir -p ./result
REC=
for d in $(find /work/user50719-8334 -maxdepth 8 -type d -name 'opca-scvi-*' 2>/dev/null); do
  if [ -f $d/metrics.json ]; then REC=$d; break; fi
done
if [ -n "$REC" ]; then
  echo RECOVER $REC
  cp -r $REC/. ./result/
else
  python3 ./scvi_script.py
  OUT=$(ls -d ./opca-scvi-* | head -1)
  cp -r $OUT/. ./result/
fi
ls -la ./result | head -20
```

runtime：`req_cpu: 2`、`req_memory: "8Gi"`、`docker_url` 与 `opca_v2` 相同（平台关联镜像显示 **SATURN--22**）。
输出：`File result = "./result"`。

**设计意图**：上次 `W202610170092924` 失败是因为旧 WDL 末句 `cp -r ../opca-full-* ../result` 与脚本输出的 `opca-scvi-*` 前缀不匹配，`set -e` 导致判失败。新流程先把结果拷进 `./result/` 再交给 WDL 声明，同时优先从 `/work` 捞回上次 4.5 小时算出的结果（几秒完成），捞不到才重算。

---

## 三、已确认的事实（勿重复验证）

1. **镜像有 torch / scvi-tools**：上次任务顶层 `import torch` / `import scvi` 通过，跑了 4.5 小时才失败，排除缺包。
2. **上次失败费用 ¥0.11**，无任何产物（`/Files/ResultData/Workflow/` 为空）。
3. **`opca_v2` 的 WDL 原文**（只读，未改）：
   - `runtime { req_cpu: 2; req_memory: "8Gi"; docker_url: "public-library/zhongliyuan_57362367597d49499e5bc388096a17f1_public:latest" }`
   - 末句 `cp -r ../opca-full-* ../result`，输出 `File result = "./result"`
4. **平台接口**（在已登录页面内 `fetch` + `credentials:"include"` 可用）：
   - 文件列表：`POST /api/data/file/meta/query?projectId=…&parentId=…&zone=st`
   - 下载：`GET /api/data/file/downloadFile?id=…&projectId=…&zone=st`（**仅 cookie，不加自定义头**）
   - 取消任务：`POST /api/task/dcsTask/cancelTasks`，body `{taskIds:["W…"], projectId:"P20260920085640327"}`
   - 任务详情：`GET /api/task/dcsTask/getUserTaskById?taskId=…`
   - 任务日志：`GET /api/task/bioc/queryJobLog`（路径片段，需再确认参数）
5. **UI 坑**：任务列表表格宽 1554px、可视区 1094px，右侧操作列需先把 `.vxe-table--body-inner-wrapper` 的 `scrollLeft` 设到 `scrollWidth` 才能点到；操作列只有「收藏」+ 三点菜单，三点菜单点击无响应。
6. **提交表单坑**：分析方式默认「运行界面输入」，误点「表格数据输入」会导致要选表格且无法继续；实体 ID 的 combobox 输入后会弹下拉，需先点空白处关闭再点「下一步」。

---

## 四、项目路径

- 仓库：`D:\projects\course5-prep`
- 本次记录：`docs/execution/20261017-scvi-task-submission.md`
- 校验脚本：`scripts/verify_scvi_artifact.py`（用法 `python scripts/verify_scvi_artifact.py <解压目录>`）
- 结果应落到：`results/phase-20261017/scvi-cross-species/`（新目录，不覆盖既有）

---

## 五、下一步（按序）

1. 监督 `W202610180071516` 到终态（每 5–10 分钟查一次，不轮询已结束任务）。
2. 完成后：
   - 取日志中 6 行 `{src}->{tgt} done macroF1(coarse)=…`；
   - 下载 `/Files/ResultData/Workflow/W202610180071516/` 下的产物；
   - 跑 `verify_scvi_artifact.py`；
   - 写 `docs/reports/scvi-cross-species-result-20261018.md`，含 6 方向 × 3 层表 + 与 oPCA/SATURN/SAMap 并列 + transductive 限定 + 样本量差异披露。
3. 失败则：只读原因、追加到 `20261017-scvi-task-submission.md`、**不重投、不加资源**。

---

## 六、硬约束（持续有效）

- 不读取/打印/复制 token、cookie、密码、API key；不启动本地训练；不在本地做模型运算。
- 不重投失败任务、不加资源、不充值；费用上限 1 元。
- 不修改/删除/覆盖 `results/pilot-v1`；不覆盖旧 PPT/报告。
- 不把 transductive 写成 held-out / inductive。
- 任何 PPT/Word 数字必须从冻结 metrics 生成或逐格核对。
- 不按单一总分给三个方法排「冠军」。
- mapping v1 在真人签字前保持 needs-reviewer。

---

## 七、重大更正（2026-10-18 14:0x）

### 7.1 上次任务 W202610170092924 的真实情况（推翻此前判断）

通过 `POST /api/task/bioc/getJobStepInfo?taskId=…` 与 `GET /api/task/dcsTask/getUserTaskById?taskId=…` 实测：

| 项 | 实测值 | 此前的错误说法 |
|---|---|---|
| `analyseStartTime` → `analyseFinishTime` | **约 9.4 分钟**（`analyseBillingDuration` = 566 秒） | ❌ "跑了 4.5 小时" |
| `cpu` | **0.00815 小时 ≈ 29 秒** | ❌ 未提及 |
| `io` | 0.916 GB | — |
| `maxmem` | 0.78 GB | — |
| `failures.Message` | **`Container exited with status 1`** | 推测为 cp glob 失败 |
| `returnCode` | 0（cromwell 层） | — |
| 费用 | ¥0.11 | 同 |

**"4.5 小时"是误读**：任务列表页长时间未刷新，读到的是缓存的「运行中」状态；实际任务在启动后约 9 分钟就已失败。

### 7.2 "镜像有 torch / scvi-tools" 的推断不成立

此前用"跑了很久才失败"反推 torch 存在，**该推断已失效**（真实只跑了 29 秒 CPU）。
`opca_v2` 的 WDL 依赖检查只有 `numpy/anndata/scanpy/sklearn`，且这四个来自 `pylibs_full.tar.gz`，
**从未验证过 torch / scvi**。`pylibs_full.tar.gz` 是 SAMap 栈（samap/samalg/hnswlib），不含 scvi-tools。

**当前最可能根因：脚本第 239 行 `import scvi` 失败（ModuleNotFoundError）**，在 29 秒内退出。
待探针任务确认。

### 7.3 本次 WDL 的严重 bug（我的错）

`scvi_cross` v1.0.0 中写了：

```bash
if [ -n $REC ]; then      # ← 错：$REC 为空时退化为 [ -n ]，bash 判为真
```

`$REC` 为空 → `[ -n ]` 是单参数测试，"-n" 非空 → **判真** → 走 `cp -r $REC/. ./result/`
→ 实际执行 `cp -r /. ./result/`，开始递归拷贝整个根文件系统。

实测后果：任务运行约 40 分钟，IO 冲到 **95.4 GB**、内存逼近 8 GB 上限，费用 **¥0.58**。
已通过 `cancelTasks` 立即取消（`W202610180071516` 终态「取消」）。

**修复**：改为 `[ -n "$REC" ]`；更彻底的做法是删掉该 RECOVER 分支（已确认上次没有产生任何 `opca-scvi-*` 目录）。

### 7.4 累计费用

| 任务 | 费用 | 状态 |
|---|---|---|
| `W202610170092924`（opca_v2 / scVI） | ¥0.11 | 失败 |
| `W202610180071475`（scvi_cross） | ¥0.00 | 取消（未调度） |
| `W202610180071516`（scvi_cross） | ¥0.58 | 取消（我的 WDL bug） |
| **合计** | **¥0.69** | 在 1 元上限内 |

---

## 八、诊断进展（2026-10-18 18:4x）

### 8.1 已确认：新流程本身没问题

最小 echo 测试 `W202610180095873`（实体 `scvi-echo-20261018`）**成功**：

| 项 | 值 |
|---|---|
| 命令 | 仅 `mkdir -p ./result` + `echo hello > ./result/diag.txt` |
| 终态 | **完成** |
| 时长 | 25m 5s（含排队） |
| 费用 | ¥0.01 |
| 产物 | `/Files/ResultData/Workflow/W202610180095873/result/result` = `hello\n`（6 B，已下载验证） |

**结论**：`scvi_cross` 流程定义、`./result` 输出声明、`docker_url` 镜像、平台回收链路**全部正常**。
之前的失败不是流程配置问题，而是**命令段中某个具体步骤**导致的。

### 8.2 已排除

- ❌ 不是镜像问题（同一 docker_url 的 echo 成功）
- ❌ 不是输出路径问题（`./result` 能被回收）
- ❌ 不是 `../result` vs `./result`（echo 用 `./result` 成功）
- ❌ 不是新流程未授权/未发布（能正常调度执行）

### 8.3 下一步：二分定位

待测可疑命令（按嫌疑排序）：

1. `tar xzf ${pylibs_tar}` —— 200 MB 解压，最可能（磁盘配额/超时）
2. `python3 -c 'import torch'` —— 若镜像无 torch 会失败，但已加 `2>&1` 且无 `set -e`，理论上不该中断
3. `ls /Files/local_human_s.h5ad` —— 路径可能不存在

注：diag3 用了 `set -u` + 全部重定向到文件，仍失败且 CPU 仅 1 秒，说明**在写 diag.txt 之前就挂了**——
`mkdir -p ../result` 或第一条 `echo` 失败。这与 echo 测试（`./result`）成功矛盾，**说明 `../result` 在容器里不可写**。

**修正判断**：应使用 `./result`（已验证可写），不是 `../result`。

---

## 九、根因确认（2026-10-18 19:3x）

二分测试任务 `W202610180098593`（实体 `scvi-bisect-20261018`）**成功**（`STAGE_DONE`，IO 0.87 GB，¥0.0x），
产物 `result/result`（1239 B）内容完整：

```
S1
S2_tar_ok
S3
torch 2.6.0+cu124
S4
Traceback (most recent call last):
  ...
  File ".../scvi/data/_utils.py", line 29, in <module>
    from mudata import MuData
  ...
  File ".../mudata/_core/mudata.py", line 21, in <module>
    from anndata._core.aligned_mapping import (AlignedViewMixin, ...)
ImportError: cannot import name 'AlignedViewMixin' from 'anndata._core.aligned_mapping'
    (.../pylibs_full/anndata/_core/aligned_mapping.py)
S5
/Files/local_human_s.h5ad
S6_end
```

### 9.1 结论

| 项 | 实测 |
|---|---|
| **torch** | **`2.6.0+cu124` —— 镜像自带，可用** ✅ |
| **scvi-tools** | **镜像里存在**（`/usr/local/lib/python3.9/site-packages/scvi/`），但**导入失败** ❌ |
| 失败原因 | **anndata 版本冲突**：`PYTHONPATH` 把 `pylibs_full/anndata`（旧版）排在镜像 site-packages 前面，`mudata` 需要新版 anndata 的 `AlignedViewMixin` |
| 数据文件 | `/Files/local_human_s.h5ad` **存在** ✅ |
| pylibs 解压 | 正常（0.87 GB IO，`S2_tar_ok`）✅ |

### 9.2 这解释了此前所有失败

- `W202610170092924`（opca_v2）：`import scvi` 在 29 秒 CPU 内失败 → `Container exited with status 1`（**不是**输出目录问题，我此前的推断错误）
- `W202610180077350`（probe）：同样在 `import scvi` 处失败
- `W202610180087103`（diag）：用了 `../result`，写不进去 → 1 秒失败
- `W202610180092855`（diag3）：同上
- `W202610180095873`（echo）：仅 `./result` + `echo` → **成功**（证明流程链路正常）
- `W202610180098593`（bisect）：`./result` + tar + torch/scvi → **成功**（因为无 `set -e`，scvi 失败被容忍）

### 9.3 修复方案（下一步）

**不要用 `pylibs_full` 的 anndata 覆盖镜像的 anndata。** 三种做法：

1. **只把 pylibs 用于缺失的包**：解压后，从 `PYTHONPATH` 中排除 `anndata`、`numpy`、`scipy` 等镜像已自带的包（删掉 `pylibs_full/anndata` 等目录）；
2. **优先镜像 site-packages**：把 `PYTHONPATH` 设为 `$PWD/pylibs_full` 但把 `anndata` 子目录改名，或设置 `PYTHONPATH` 在 `site-packages` **之后**（默认 `PYTHONPATH` 优先于 site-packages，所以只能删/改名）；
3. **完全不用 pylibs 的 anndata**：解压 pylibs 后 `rm -rf ./pylibs_full/anndata ./pylibs_full/anndata*`，让镜像自带的 anndata 生效。

**推荐做法 3**（最简单，且已验证镜像自带 anndata 能满足 mudata）。

需确认：镜像自带的 anndata 版本是否 ≥ 0.10（`AlignedViewMixin` 需要 0.10+）。下一次诊断会一并验证。

### 9.4 累计费用

| 任务 | 费用 |
|---|---|
| W202610170092924 | ¥0.11 |
| W202610180071475 | ¥0.00 |
| W202610180071516 | ¥0.58 |
| W202610180077350 | ¥0.04 |
| W202610180087103 | ¥0.03 |
| W202610180092855 | ¥0.02 |
| W202610180095873 | ¥0.01 |
| W202610180098593 | ~¥0.01 |
| **合计** | **约 ¥0.80** |

---

## 十、修复验证任务（进行中）

| 项 | 值 |
|---|---|
| 任务号 | **`W202610180101096`** |
| 实体 | `scvi-fix-20261018` |
| 改动 | 解压 pylibs 后 `rm -rf ./pylibs_full/anndata*`，让镜像自带的 anndata 生效 |
| 验证点 | `import anndata` / `import scvi` / `import scanpy` 的版本与文件路径，写入 `result/diag.txt` 与 `result/pylibs_list.txt` |
| 输出 | `./result`（已由 `W202610180095873` echo 测试验证可回收） |
| 提交时间 | 2026-10-18 19:2x |
| 状态 | **未知**（内置浏览器会话被重置，未能读取终态） |

### 10.1 恢复后第一件事

登录 DCS 后：
1. 打开 `任务管理`，读 `W202610180101096` 的终态与费用；
2. 若「完成」，去 `/Files/ResultData/Workflow/W202610180101096/result/` 取 `diag.txt` 与 `pylibs_list.txt`；
3. 确认 `import scvi` 是否通过。通过则把 WDL 的 `diag` 段替换为正式运行段（见 §二 原始设计），提交正式任务。

### 10.2 已确认的根因与修复方向（勿再重查）

- 镜像自带 `torch 2.6.0+cu124`；`scvi` 在 `/usr/local/lib/python3.9/site-packages/scvi/` 存在；
- 失败原因是 `PYTHONPATH=$PWD/pylibs_full` 里**旧版 anndata** 抢先，`mudata` 需要新版 anndata 的 `AlignedViewMixin`；
- 修复：删掉 `pylibs_full/anndata*`，或不用 pylibs 的 anndata；
- 另一独立教训：**输出目录必须写 `./result`**（`../result` 在容器里不可写，1 秒即失败）。

---

## 十一、正式任务已提交（2026-10-19）

| 项 | 值 |
|---|---|
| 任务号 | **`W202610190042919`** |
| 实体 | `scvi-run-20261019` |
| 流程 | **`scvi_cross2` v1.0.0**（新建，干净编辑器一次写入，55 行） |
| 提交时间 | 2026-10-19 10:4x |
| 状态 | 待分析 |

### 11.1 `scvi_cross2` 与 `scvi_cross` 的差异

```bash
mkdir -p ./result
tar xzf ${pylibs_tar}
rm -rf ./pylibs_full/anndata ./pylibs_full/anndata-*.dist-info     # ← 关键修复
export PYTHONPATH=$PWD/pylibs_full:$PYTHONPATH
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
cp ${script_txt} ./scvi_script.py
export OPCA_OUT_ROOT=$PWD
python3 ./scvi_script.py > ./result/run.log 2>&1
OUT=$(ls -d ./opca-scvi-* ./scvi-cross-* 2>/dev/null | head -1)
if [ -n "$OUT" ] && [ -d "$OUT" ]; then      # ← 修复上次 cp -r /. 的严重隐患
  cp -r "$OUT"/. ./result/
else
  echo NO_OUTPUT_DIR >> ./result/run.log
fi
```

输出声明 `File result = "./result"`（echo 测试 `W202610180095873` 已验证可回收）。

### 11.2 已验证的环境事实

| 项 | 值 |
|---|---|
| 镜像自带 anndata | **0.10.8** |
| 镜像自带 scvi-tools | **1.1.6.post2**，删掉 pylibs anndata 后**导入成功** |
| 镜像自带 torch | **2.6.0+cu124** |
| pylibs scanpy | 1.9.3（与 anndata 0.10.8 共存已实测可导入） |
| 数据文件 | `/Files/local_human_s.h5ad` 存在 |

### 11.3 提交表单的一个可用技巧

文件选择器在嵌套 iframe 里定位不稳定时，可用**专业模式**直接编辑 JSON：
`{"scvi_cross2.script_txt": "...", "scvi_cross2.pylibs_tar": "..."}`。
注意该编辑器只追加不替换，需先点入编辑区 → Ctrl+A → Delete 清空再填。

---

## 十二、scVI 正式任务完成（2026-10-19）

任务 **`W202610190042919`** 完成，28m 40s，CPU 8.5 min，峰值内存 2.37 GB，产物全部回收。

**结果报告**：`docs/reports/scvi-cross-species-result-20261019.md`
**产物目录**：`results/phase-20261019/scvi-cross-species/`（metrics.json、18 个 predictions、latent.npy、run.log、manifest、environment、sha256.tsv、platform_script.txt）

### 12.1 核心数字（coarse macro-F1，union 口径，四方法可比）

| 方向 | scVI | oPCA | SATURN | SAMap |
|---|---|---|---|---|
| h→m | **0.6683** | 0.6435 | 0.4147 | 0.1127 |
| m→h | 0.5895 | **0.6729** | 0.4010 | 0.0401 |
| h→z | **0.4014** | 0.1682 | 0.2479 | 0.0477 |
| z→h | **0.4290** | 0.1585 | 0.4021 | n/a |
| m→z | 0.4248 | 0.2314 | **0.6500** | n/a |
| z→m | 0.4786 | 0.4396 | **0.6510** | n/a |

### 12.2 新发现：macro-F1 口径不一致（重要，勿再踩）

- 平台 scVI 脚本用 **truth-only**（`set(y_true)`）；
- `unified_coarse_macro_f1.py` 用 **union**（`set(y_true) | set(y_pred)`）；
- 差异在"只出现在预测里的类"：truth-only 忽略它们，union 记 F1=0；
- 结果：`metrics.json` 的 `macro_f1` 普遍**高于** union 口径（如 h→z coarse 0.4516 vs 0.4014），
  **不能直接与 oPCA/SATURN/SAMap 并列**。
- 已按 union 口径从 18 个预测文件独立重算，存 `recomputed_union.json` 与 `verify_recomputed_union.txt`。

### 12.3 核对结论

- accuracy：**18/18 与平台完全一致**；
- macro-F1：差异全部可用口径解释，无未知偏差；
- 全部 18 格 `shuffle_p = 0.0000`。

### 12.4 累计费用

约 **¥0.90**（上次 ¥0.80 + 本次正式任务 ¥0.05 + 期间两个小任务 ¥0.05），在 1 元上限内。

---

## 十三、交付物更新（2026-10-19）

| 交付物 | 文件 | 状态 |
|---|---|---|
| 场景化选型指南 | `deliverables/场景化选型指南-v2-20261019.md` | 新建（保留 v1） |
| 第 2 次汇报 PPT | `results/stage-reports-20261017/课题5第02次汇报_纠偏_7分钟版_v2.pptx` | 新建（旧的 7 分钟版未覆盖） |
| 构建脚本 | `results/stage-reports-20261017/build_report02_v2.js` | 新建 |
| 渲染检查图 | `results/stage-reports-20261017/render_v2/p01–p07.png` | 7 页逐页检查 |

### 13.1 v2 相对 v1 的实质变化

- 主表从三方法扩为**四方法**（加 scVI 列）
- 远缘拆成两个场景：**人↔鱼 → scVI 首选**；**鼠↔鱼 → SATURN 首选**
- 无 GPU 场景：**scVI 实测 8.5 min CPU 可行**（此前假设深度学习必须 GPU）
- 近缘：scVI 与 oPCA 基本打平（均值 0.629 vs 0.658），oPCA 仍是首选但优势不再压倒
- 「还缺什么」页：scVI 臂标记为已补，剩余缺口是跨门 + kBET/iLISI/silhouette

### 13.2 渲染检查发现并修正

第 4 页正文原写「人↔鼠」有误（scVI 只在人→鼠领先，鼠→人是 oPCA 更高），
已改为「人→鼠、人→鱼、鱼→人、鱼→鼠；鼠→人 输给 oPCA，鼠→鱼 输给 SATURN」，重新渲染确认。

### 13.3 视觉验收说明

`presentations:visual-judge` 子代理启动失败（provider-not-found），
按交付规范降级为本人逐页检查 7 张 PNG：表格无溢出、卡片无遮挡、标题与正文无重复。

---

## 十四、第 2 次汇报 PPT v3（2026-10-19）

| 项 | 值 |
|---|---|
| 文件 | `results/stage-reports-20261017/课题5第02次汇报_纠偏_7分钟版_v3.pptx` |
| 构建脚本 | `results/stage-reports-20261017/build_report02_v3.js` |
| 页数 | 8 页（规格 6–8 页 / 7–8 分钟） |
| 渲染检查 | `results/stage-reports-20261017/render_v3/p01–p08.png` |

相对 v2 的变化：
- 新增第 5 页「批次混合：scVI latent 上物种并未混匀」（silhouette 0.181 / iLISI 1.125 / kBET 0.0039 + 与高 macro-F1 的矛盾及解释）；
- 第 6 页选型表「跨门」行由「无证据」改为「待跑 / 数据已定位」，并新增「跨门有新进展」卡片；
- 第 7 页「还缺什么」：kBET/iLISI/silhouette 由「缺」改为「部分（scVI 已测）」；最大缺口改为跨门的三个待确认前提；
- 第 8 页下一步：新增「批次混合指标已完成」「跨门三前提待确认」两行。

渲染检查发现并修正：第 5 页表格第三行被卡片压住（表格 y 1.75→1.62、行高 0.46→0.40、卡片 y 3.35→3.42），重新渲染确认无遮挡。

`presentations:visual-judge` 仍不可用（provider-not-found），按规范降级为本人逐页检查 8 张 PNG。

---

## 十五、第 2 次汇报按十次规划重做（2026-10-19）

**问题**：此前把第 2 次汇报做成了「纠偏」主题，偏离了既定十次规划。
规划中第 2 次的主题是 **数字来源链**（"一个百分比怎么来的？"，见
`docs/execution/20261015-claude-consultation-deviation.md` §2.4）。

**重做文件**：
- `results/stage-reports-20261019/课题5第02次汇报_数字来源链.pptx`（8 页）
- `results/stage-reports-20261019/build_report02_lineage.py`
- 渲染检查：`results/stage-reports-20261019/render/p01–p08.png`

**设计**：弃用校模板的圆角卡片 + 顶部色条（pptx 设计规范明确把"装饰色条/强调条"列为
AI 生成感来源）。改为：
- sandwich 结构：深色封面/收尾 + 白色正文
- 单一主色（深青 #14505E）+ 一个强调色（#C2410C），不做彩虹
- 无卡片网格、无标题下划线、无圆角；层级靠字号/字重/发丝线
- 每页一个视觉焦点（超大数字 / 流程图 / 柱状图）
- 所有形状移除主题样式（去阴影/描边）
- 图表带数值标签，页脚带来源行

**页序**：封面 → 论点（六个因素）→ 来源链（8 步）→ 86.18% 拆解 → 分母与四个量 →
macro-F1 口径（truth-only vs union）→ 四方法柱状图 → 收尾（下次主题）

**旧文件未覆盖**：`课题5第02次汇报_纠偏_7分钟版_v2/v3.pptx` 保留。

**说明**：环境中没有可下载的"PPT 审美"独立 skill；已安装的官方 `presentations:pptx`
插件自带完整幻灯片设计规范（配色、字体、版式反模式、QA），本次即按该规范执行。
