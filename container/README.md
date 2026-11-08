# 课题5 容器化交付物

> 课程要求项之一。**状态：脚本已端到端跑通并复算冻结值；镜像未实际构建**。
> 交付内容：Dockerfile + 固定依赖 + 入口脚本 + 验收清单，任何有 Docker 的机器上一条命令可复现。
>
> **2026-10-28 进展**：修掉了一个真实缺陷（entrypoint 与脚本的环境变量契约不匹配，
> 会导致容器内 `FileNotFoundError`），并在本地按容器契约跑完整评估，
> 12 个格子与冻结值逐位一致、39 项输出哈希全部核实。详见第七节。

---

## 一、这是什么

把本项目里**唯一一个完全确定性、无 GPU 依赖**的方法（ortholog-PCA 基线）打包成可复现容器。
选择它而不是 SATURN / SAMap，原因见 `docs/reports/tooling-usability-and-agent-friendliness-20261023.md`：
后两者依赖 GPU 镜像与预建依赖栈，不适合作为"一条命令复现"的载体。

容器做三件事：

1. 固定依赖版本（与本项目 DCS 复算任务 `W202610150090794` 的实际环境一致）；
2. 做前置检查（缺文件/输出目录已存在时按固定退出码失败，不静默覆盖）；
3. 跑完整 6 方向 × 3 层评估，产出 `metrics.json` / `predictions/` / `confusion/` / `manifest.json` / `command.txt` / `environment.json`。

---

## 二、文件

| 文件 | 作用 |
|---|---|
| `Dockerfile` | 基于 `python:3.9-slim`，装固定版本依赖，复制脚本与入口 |
| `requirements.txt` | 依赖锁定（numpy 1.23.5 / anndata 0.10.8 / scanpy 1.9.3 / sklearn 1.6.1 …） |
| `entrypoint.sh` | 参数解析 + 前置检查 + 环境变量注入 |
| `README.md` | 本文 |

---

## 三、构建与运行

```bash
# 1) 构建（context 必须是仓库根目录，脚本在 scripts/ 下）
docker build -f container/Dockerfile -t course5-opca:1.0.0 .

# 2) 准备数据目录（结构与 DCS /Files 一致）
#    data/
#      local_human_s.h5ad
#      local_mouse_s.h5ad
#      local_zebrafish_s.h5ad
#      wheelhouse/
#        orth-MGI-HOM.rpt
#        orth-human-orthos.txt
#        orth-mouse-orthos.txt
#        heart-celltype-map-v1.tsv

# 3) 运行
docker run --rm \
  -v "$PWD/data:/data:ro" \
  -v "$PWD/out:/out" \
  course5-opca:1.0.0 \
  --data /data --out "/out/run-$(date -u +%Y%m%dT%H%M%SZ)"
```

预计：CPU 2 核约 15 分钟（与 DCS 复算任务的 14m26s 同量级），内存峰值约 1.2 GB。

---

## 四、验收清单（容器版）

跑完后检查：

| # | 检查项 | 期望 |
|---|---|---|
| 1 | 退出码 | 0 |
| 2 | `metrics.json` 存在 | 是 |
| 3 | 方向数 | 6（人↔鼠、人↔鱼、鼠↔鱼，双向） |
| 4 | 每方向层级数 | 3（exact / coarse / fine） |
| 5 | `shared_genes` | 15,869 / 9,311 / 8,160（人鼠 / 人鱼 / 鼠鱼） |
| 6 | 人→鼠 coarse accuracy | **0.8618** |
| 7 | 鼠→人 coarse accuracy | **0.7369** |
| 8 | `manifest.json` 的 `output_sha256` | 39 项，每项与文件实际哈希一致（本脚本输出 `output_sha256` 字段，不单独产出 `sha256.tsv`） |

第 5–7 项是本项目已冻结并独立复算过的数值（见 `docs/reports/`），
如果容器跑出来的数字与它们不一致，说明依赖版本或脚本被改动过，**不要直接采用**。

---

## 五、退出码约定

| 码 | 含义 | 处置 |
|---|---|---|
| 0 | 成功 | — |
| 2 | 前置检查失败（缺输入文件） | 补文件后重跑，不要改脚本 |
| 3 | 输出目录已存在 / 越界 | 换一个 `--out`，脚本拒绝覆盖 |
| 4 | 基因轴过小（<100） | 检查映射表是否完整 |

---

## 六、已知限制

1. **镜像未实际构建**：本机装了 Docker Desktop，但 WSL 无发行版导致 daemon 无法启动；
   平台镜像构建通道此前也返回失败。
   **但脚本与数据契约已端到端跑通**，12 格结果与冻结值逐位一致（见第七节 7.3）。
   缺的只是 `docker build` 这一步本身。
2. **只覆盖 oPCA 一个方法**：SATURN / SAMap / scVI 未容器化，原因见第一节。
3. **不含数据**：镜像内不落任何数据，全部走挂载。
4. **不做 GPU**：需要 GPU 的方法不在本容器范围内。

---

## 七、验证结果（2026-10-28）

### 7.1 静态校验

| 检查项 | 结果 |
|---|---|
| Dockerfile 的 3 个 `COPY` 源路径 | ✅ 全部存在 |
| 基础镜像 | `python:3.9-slim`（与 DCS 实测环境 py3.9 一致） |
| `requirements.txt` 精确锁版本 | ✅ 7 个包全部 `==` |
| `entrypoint.sh` bash 语法 | ✅ `bash -n` 退出码 0 |
| 换行符 | ✅ 纯 LF、无 BOM（CRLF 会让容器内 shebang 失效） |
| 脚本的第三方 import 覆盖 | ✅ 只 import `numpy/scipy/anndata/scanpy/sklearn` 5 个，全部在 requirements 内 |

### 7.2 已修复的真实缺陷：环境变量契约不匹配

**这是「配方完整但没跑过」埋下的坑，已修。**

`entrypoint.sh` 原来只导出 `OPCA_ORTH_DIR`，但脚本 `ortholog_pca_dcs_v3_fixkey.py`
**从不读取这个变量**（第 44 行定义了一个 `ORTH_DIR` 常量，之后再未使用）。
脚本真正读的是三个按文件名区分的变量：

```
OPCA_ORTH_MGI  （默认 /Files/wheelhouse/orth-MGI-HOM.rpt）
OPCA_ORTH_HF   （默认 /Files/wheelhouse/orth-human-orthos.txt）
OPCA_ORTH_MF   （默认 /Files/wheelhouse/orth-mouse-orthos.txt）
```

这些默认值指向 `/Files/`，而容器内只有 `/data`。后果是：
**前置检查会通过**（它查的是 `$DATA_DIR/wheelhouse`），但脚本一 open 就 `FileNotFoundError`。

修法：entrypoint 逐个导出这三个变量。修完后用脚本静态比对确认
「脚本读取的 7 个环境变量」与「entrypoint 导出的 7 个」完全一一对应。

### 7.3 端到端运行验证

按容器的变量契约，在本地用同一份脚本、同一份数据跑了一次完整评估：

```
DONE mode=full elapsed=28.2s        ← CPU 2 核量级，与 README 预估的 15 分钟是不同规模
```

**12 个格子（6 方向 × exact/coarse）与冻结值逐位一致：**

| 方向 | coarse（本次/冻结） | exact（本次/冻结） |
|---|---|---|
| 人→鼠 | 86.18% / 86.18% | 78.24% / 78.24% |
| 鼠→人 | 73.69% / 73.69% | 40.84% / 40.84% |
| 人→斑马鱼 | 17.95% / 17.95% | 15.04% / 15.04% |
| 鼠→斑马鱼 | 26.75% / 26.75% | 16.40% / 16.40% |
| 斑马鱼→人 | 17.34% / 17.34% | 13.87% / 13.87% |
| 斑马鱼→鼠 | 58.14% / 58.14% | 47.10% / 47.10% |

对照的冻结源：`results/phase-20261010/opca-fixkey-recovered-20261015/metrics.json`。
**ALL 12 CELLS MATCH FROZEN = True**

同时核实：`manifest.json` 的 `output_sha256` 共 39 项，**39/39 与磁盘文件实际哈希一致**。

### 7.4 平台镜像构建通道：旧结论已推翻（2026-10-28 核实）

此前多处文档写「平台镜像构建通道失败」，**这个说法不准确**。实际查镜像管理页：

| 镜像 | 时间 | 状态 |
|---|---|---|
| g5-canary-pinned | 2026-09-21 20:43 | **构建成功** |
| g5-samap-101 | 2026-09-21 22:56 | 构建失败 |
| g5-samap-try | 2026-09-21 22:09 | 构建失败 |
| g5-kbet-jaxpin | 2026-09-21 21:02 | 构建失败 |
| centos-7（system） | 2026-09-19 16:17 | 构建成功 |
| SATURN--22（zhongliyuan） | 2025-09-10 15:28 | 构建成功 |

`g5-canary-pinned` 的内容正是「SATURN--22 + `scib-metrics==0.4.1` + `six==1.16.0`」，
说明**平台镜像构建通道可用**，5 次尝试里 1 次成功，失败集中在 SAMap/kBET 那些复杂依赖上。

**这对容器化的意义**：不需要本地 Docker 也能验证依赖锁。操作步骤见
`docs/execution/20261028-platform-image-manual-steps.md`。

**但要注意区分**：平台镜像是「基础镜像 + pip 包清单」，**不是 `docker build`**，
它验证不了 `container/Dockerfile` 本身。两者是不同机制，不能互相替代。

### 7.5 版本容差实测（重要）

本地跑自检脚本时发现：**本地环境的 3 个包与锁版本不同，但 6 个冻结值 100% 复现。**

| 包 | 锁版本 | 本地实测 | 是否影响结果 |
|---|---|---|---|
| numpy | 1.23.5 | 1.23.5 | — |
| scipy | 1.10.1 | **1.12.0** | ❌ 不影响（6/6 冻结值一致） |
| pandas | 1.5.3 | **2.3.3** | ❌ 不影响（跨两个大版本仍一致） |
| sklearn | 1.6.1 | 1.6.1 | — |
| anndata | 0.10.8 | **0.10.9** | ❌ 不影响 |
| scanpy | 1.9.3 | 1.9.3 | — |
| h5py | 3.8.0 | 3.8.0 | — |

自检脚本：`scripts/image_selfcheck.py`（输出带 `SELFCHECK_BEGIN`/`SELFCHECK_END` 标记的 JSON，
可在任务日志里直接提取）。归档：`results/phase-20261028/image-selfcheck-local/`。

**结论**：oPCA 基线的数值**对本项目涉及的这三个包版本不敏感**。
这对容器化是个好消息——即使平台构建时装不上精确版本的 scipy/pandas，
结果也不会漂移；锁版本是为了可复现性，不是因为它决定了数值。

### 7.6 依赖锁与基础镜像的吻合度

SATURN--22 镜像已自带的包中，有 4 个与我们锁的版本完全一致：

| 包 | 锁版本 | SATURN--22 内实测 |
|---|---|---|
| numpy | 1.23.5 | ✅ 1.23.5 |
| anndata | 0.10.8 | ✅ 0.10.8 |
| scanpy | 1.9.3 | ✅ 1.9.3 |
| scikit-learn | 1.6.1 | ✅ 1.6.1 |

（来源：`results/phase-20261019/scvi-cross-species/environment.txt`，同一镜像上实际运行的记录）

剩下 3 个（scipy 1.10.1 / pandas 1.5.3 / h5py 3.8.0）需要在平台构建时显式安装。

### 7.7 仍未做的：`docker build`

本机装了 Docker Desktop 29.8.2，但 **WSL 没有任何发行版**（`wsl -l -v` 报无已安装分发），
daemon 起不来（`desktop-linux` context 返回 500）。

要补这一步：`wsl --install -d Ubuntu`（需重启），或在有 Docker 的机器/CI 上执行一次：

```bash
docker build -f container/Dockerfile -t course5-opca:1.0.0 .
docker run --rm -v "$PWD/data:/data:ro" -v "$PWD/out:/out"   course5-opca:1.0.0 --data /data --out /out/run-1
```

**当前证据等级**：脚本与数据契约已端到端跑通并可复算冻结值；
容器**镜像构建**这一步仍无实测证据。

---

## 八、如果要扩展到 scVI

在 `requirements.txt` 追加：

```
torch==2.6.0
scvi-tools==1.1.6.post2
```

并把 `entrypoint.sh` 的 `exec` 换成对应的 scVI 脚本。
**注意**：本项目的经验是 `pylibs` 里的旧 anndata 会破坏 `import scvi`，
容器内应只保留 anndata 0.10.8 一份，不要叠加第二份。
