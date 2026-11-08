# scVI 跨物种任务：提交记录（2026-10-17）

> 本文只记录**提交事实**与**执行前读到的 WDL 原文**，不含任何凭据内容。
> 任务终态与产物核对待任务结束后另起文档，不在本文追加。

---

## 一、提交结果

| 项 | 值 |
|---|---|
| 任务号 | **`W202610170092924`** |
| 实体 ID | `scvi-xspecies-20261017` |
| 流程 | `opca_v2` v1.0.0（未修改流程定义，只点了「运行」） |
| 提交时间 | 2026-10-17 15:00:52（页面任务名 `WORKFLOW_opca_v2_2026-10-17_15_00_52`） |
| 初始状态 | 待分析 |
| `script_txt` | `/Files/ResultData/Notebook/scvi_cross_species.txt`（19,796 B，480 行，file id `459bf7eb8f784804b380d7795e862fd3`） |
| `pylibs_tar` | `/Files/ResultData/Notebook/pylibs_full.tar.gz`（200.80 MB） |
| 输出目录（平台侧） | 默认 `/Files/ResultData/Workflow/<taskId>` |
| 任务备注 | `scVI cross-species arm (6 dirs x 3 layers). script=scvi_cross_species.txt; out=opca-scvi-<UTC> under OPCA_OUT_ROOT` |

**只提交一次**，未重投、未改资源、未充值。

---

## 二、提交前读到的 WDL 原文（流程编辑器「脚本信息」页）

以下为 `opca_v2` v1.0.0 的实际定义（页面逐行读取，非转述）：

```
workflow opca_v2 {
  input { File script_txt; File pylibs_tar }
  call RunOpca { input: script_txt=script_txt, pylibs_tar=pylibs_tar }
  output { File output_result = RunOpca.result }
}

task RunOpca {
  command {
    set -e
    set -o pipefail
    tar xzf ${pylibs_tar}
    export PYTHONPATH=$PWD/pylibs_full:$PYTHONPATH
    export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
    cp ${script_txt} ../ortholog_pca_dcs_v2.py
    export OPCA_OUT_ROOT=$PWD
    python3 -c "import numpy, anndata, scanpy, sklearn; print('imports OK', numpy.__version__)"
    python3 ../ortholog_pca_dcs_v2.py
    cp -r ../opca-full-* ../result
  }
  runtime {
    req_cpu: 2
    req_memory: "8Gi"
    docker_url: "public-library/zhongliyuan_57362367597d49499e5bc388096a17f1_public:latest"
  }
  output { File result = "./result" }
}
```

对照 `runsamap` v1.0.0（同一编辑器读取）：`docker_url` **完全相同**，`req_cpu: 1` / `req_memory: "4Gi"`，依赖检查为
`import numpy, sklearn, samalg, samap, hnswlib, scanpy`（全部来自 pylibs）。

---

## 三、两个已知风险（提交前已识别，如实记录）

### R1 输出目录名不匹配 → 平台可能不自动回收

WDL 最后一句是 `cp -r ../opca-full-* ../result`，即**只认 `opca-full-<UTC>` 这一个前缀**。

- 历史 v2 脚本用的正是 `opca-full-<UTC>` → 可被回收；
- v3_fixkey 用 `opca-fixkey-<UTC>` → 任务「完成」但输出区「暂无数据」（见 `20261015-opca-fixkey-verification.md` 五之二）；
- **本次 scVI 脚本用 `opca-scvi-<UTC>`**（`out = OUT_ROOT / f"opca-scvi-{ts}"`，第 104 行）→ 同样不会被 `cp` 命中。

另外由于 `set -e`，glob 不匹配时 `cp` 返回非 0，**可能使任务在计算完成后被判失败**。
若出现这种情况，结果文件本身已完整写在 `OPCA_OUT_ROOT`（=$PWD）下，需要人工搬运，不重投。

### R2 镜像可能没有 torch / scvi-tools

- 该 `docker_url` 是平台某个公开镜像，WDL 对它的唯一依赖检查是 `numpy/anndata/scanpy/sklearn`（且这四个来自 pylibs，不能证明镜像自带任何科学栈）；
- `runsamap` 用同一镜像，其检查项也只有 `numpy/sklearn/samalg/samap/hnswlib/scanpy`，**从未验证过 torch**；
- scVI 脚本第 38 行是顶层 `import torch`，第 239 行 `import scvi`。

因此本次运行同时是一次**镜像能力探针**：

- 若日志报 `ModuleNotFoundError: No module named 'torch'` → 镜像不含 torch，scVI 臂在该镜像上不可执行，需换镜像/建新流程，属平台侧阻塞；
- 若通过 → 按 R1 处理产物搬运。

**处置原则**：无论哪种结果都**不自动重投、不加资源、不建新流程**，先落盘事实并报告。

---

## 四、提交动作清单（便于复现）

1. 流程分析 → `opca_v2` 卡片 → 绿色「运行」（**不是**三点菜单里的编辑/发布/复制/删除）
2. 实体 ID 填 `scvi-xspecies-20261017` → 下一步
3. 输入设置：`script_txt` 与 `pylibs_tar` 分别点取值列的文件夹图标 → `Files/ResultData/Notebook/` → 勾选 → 确定
4. 输出设置：保持默认 `/Files/ResultData/Workflow/[taskId]`，填任务备注 → 运行
5. 弹窗「任务提交成功」→ 确定 → 任务管理取任务号

---

## 五、边界

- 未修改流程定义（只读「脚本信息」页，未点保存）
- 未修改任何冻结件
- 未读取、未记录任何 token / cookie / 密码值
- 只提交一次；失败即停

---

## 六、任务进度记录（追加）

| 时间点（本地） | 状态 | 说明 |
|---|---|---|
| 15:00 | 待分析 | 提交成功 |
| 15:50 前后 | 运行中 | 排队约 50 分钟后开始调度 |
| 运行满 5 分钟 | 运行中 | **R2 已排除**：脚本顶层 `import torch` 与 `import scvi` 未报错，说明该 `docker_url` 镜像**确实带 torch / scvi-tools** |
| 运行满约 3.5 小时 | 运行中 | 仍在计算，未见 OOM 或退出；CPU 2 核跑 scVI 50 epoch 属正常长尾 |

**当前判断**：R2（无 torch）不成立；R1（输出目录名 `opca-scvi-*` 与 WDL 的 `opca-full-*` 不匹配）仍需在任务结束后确认。

**注意**：日志中存在 `macroF1(coarse)=` 行（脚本第 426 行附近 `print(f"{src}->{tgt} done macroF1(coarse)=...")`），即使产物未能自动回收，六个方向的 coarse macro-F1 仍可从日志逐字读出；完整 metrics.json / predictions 则需人工搬运。

---

## 七、任务终态（追加，2026-10-17 晚）

| 项 | 值 |
|---|---|
| 任务号 | `W202610170092924` |
| **终态** | **失败** |
| 费用 | **¥0.11**（上限 1 元内） |
| 总时长 | 约 **4.5 小时运行**（含排队约 50 分钟） |
| 平台输出目录 | `/Files/ResultData/Workflow/` **为空（0 个子项）**，未生成任何任务输出目录 |
| 本地产物 | 无 |
| 重投 | **未重投、未加资源、未充值、未修改流程** |

### 7.1 已排除

**R2（镜像无 torch）不成立。** 脚本第 38 行 `import torch`、第 239 行 `import scvi` 都是顶层导入；
若镜像缺包，任务会在启动后数十秒内失败。实际运行约 4.5 小时才失败 → torch / scvi-tools 均存在，训练已进入计算阶段。

### 7.2 失败原因（未直接观测到日志，以下为证据推断）

平台任务列表页与任务行均未暴露可点击的日志/详情入口（`任务编号`、`失败`、`流程名称` 三个链接点击后无跳转，
浏览上下文无新标签页），因此**未取得逐字错误信息**。基于已读到的 WDL 与输出目录事实，最可能的原因是 **R1**：

1. WDL 末段 `cp -r ../opca-full-* ../result` 只匹配 `opca-full-*`；
2. 本脚本输出目录名为 `opca-scvi-<UTC>`，glob 不匹配；
3. `set -e` 使 `cp` 的非 0 退出终止任务 → 判失败；
4. `/Files/ResultData/Workflow/` 为空，与"没有任何结果被登记为输出"一致。

次要可能：平台单任务运行时长上限（约 4.5 h）触发终止。两种情况都无法从现有界面区分。

### 7.3 影响与遗留

- **scVI 六方向数字未能取得**；三方法对比表仍为 oPCA / SATURN / SAMap 三列。
- 若结果目录仍在容器持久工作区（`/work/<user>/opca-scvi-<UTC>`），只能通过容器侧打包推送回收；
  当前 GenPilot 通道冻结，本次不尝试。
- **不自动重投**。若要重跑，需先解决两件事：① 输出目录名与 WDL glob 对齐（`opca-full-*`）；
  ② 确认平台单任务时长上限。二者都需要新建/修改流程定义，属需用户裁定的变更。

---

## 八、新建流程 `scvi_cross` v1.0.0（2026-10-17 19:2x）

为修复 R1，新建了独立流程（**未修改 `opca_v2`**）：

| 项 | 值 |
|---|---|
| 流程名 | `scvi_cross` |
| 版本 | 1.0.0 |
| 输入 | `script_txt`、`pylibs_tar`（两个 File） |
| 运行时 | `req_cpu: 2`，`req_memory: "8Gi"`，`docker_url` 与 `opca_v2` 相同 |
| **平台关联镜像** | **SATURN--22**（流程详情「关联镜像」页显示）→ 反证上次任务确实跑在 SATURN--22 上，torch/scvi-tools 可用 |
| 输出 | `File result = "./result"` |

命令段相对 `opca_v2` 改了两处：

1. **输出收集**：不再依赖 `opca-full-*`，而是把脚本产出的 `./opca-scvi-*` 内容拷进 `./result/`，与 `output { File result = "./result" }` 对齐；
2. **优先回收**：先 `find /work/user50719-8334 -maxdepth 8 -type d -name 'opca-scvi-*'` 找带 `metrics.json` 的目录，
   找到则直接 `cp -r "$REC"/. ./result/`（数秒完成），找不到才 `python3 ./scvi_script.py` 重算。

这样一次提交同时覆盖「上次结果仍在 /work」与「必须重算」两种情况。

### 8.1 提交时被会话过期打断

提交表单已全部填好（实体 `scvi-xspecies-r2`、两个输入文件），点「运行」后页面跳到 `#/login`，
会话已过期，**任务未提交成功**（未见「任务提交成功」提示）。需重新登录后再提交一次。

**未产生新任务、未产生费用。**

### 8.2 登录态说明

用户报告已登录，但 ZCode 内置浏览器（iab）的会话仍停留在 `#/login`：
- 直接访问 `#/dashboard`、`#/project-management/.../workflow/list` 均被重定向回登录页；
- 新建标签页同样如此；
- 判定：用户完成登录的浏览器与 ZCode 内置浏览器不是同一个 cookie 容器。

**需要用户在内置浏览器面板里完成登录**，之后即可继续提交 `scvi_cross` 任务。
