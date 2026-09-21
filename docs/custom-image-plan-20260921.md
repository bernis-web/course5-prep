# 自建镜像执行方案（Claude×Codex 规划，2026-09-21）

> 来源：Claude Code 规划会话（Codex 因代理 502 三次未通，恢复后需补评审）。本机直连外网 TLS 全被拦截，wheel 准备须在有网构建环境做。
> 状态：**待执行**——canary 探网是第一步；v10 GPU 基线结果出来前不动镜像。

# 课题5 · DCS 平台"自建镜像"方案规划（三问建议，2026-09-21）

## Context

**目标**：benchmark SATURN / SAMap / scVI 三方法，需要 SATURN 本体 + scib-metrics（kBET）可用。DCS 离线任务容器无外网（v8 实测 pypi Errno 101），装包唯一官方通道 = 平台"镜像管理→添加镜像"自建镜像烘焙。

**镜像实测基线**（probe_v6）：py3.9.12 / scvi-tools 1.1.6.post2 / scanpy 1.10.3 / torch 2.6.0+cu124 / anndata 0.10.8 / fair-esm 2.0.0 / faiss-gpu 1.7.2；SATURN、samap、scib-metrics 均不在。

**⚠️ 流程偏差声明**：用户要求"先与 Codex 商讨"——已尝试 3 次 `codex exec --sandbox read-only -m gpt-5.6-terra`，全部 502（CC Switch 代理→星舰上游 `127.0.0.1:15721/v1/responses` 不可达，5 次重连耗尽）。本方案基于仓库证据文档 + web 核验独立完成；**Codex 恢复后应补一轮评审**（G2 双评审先例），再进入执行。

**本机环境事实**：直连外网 TLS 全被拦截（curl exit 35 / PowerShell SSL 失败，含 pypi.org 与 raw.githubusercontent.com）→ wheel 准备/依赖解析必须放在有网的构建环境做，不能在本机做。

---

## 问1：自建镜像可行路径

**推荐方案：基于 SATURN--22（uuid `57362367...17f1`）加层 + 双环境隔离 + canary 探网**

1. **先发 canary 构建验证平台构建期网络**：Dockerfile 第一层 `RUN pip download --no-deps -d /tmp/probe scib-metrics || echo OFFLINE > /tmp/net_status`，构建日志/产物即证据。构建网络可用 → 直接在线 pip；不可用 → 走 wheelhouse 离线层。
2. **wheelhouse 兜底**（构建也不通网时）：在有网机器 `pip download -d wheelhouse/ --platform manylinux2014_x86_64 --python-version 39 --only-binary=:all: <全部依赖>`，COPY 进构建上下文，`pip install --no-index --find-links /wheels`。SATURN 旧栈同理对 py 版本另备一套 wheel。
3. **双环境布局**（保护已验证的 scVI 基线）：
   - 基础 env **不动**：只新增 scib-metrics（py3.9 兼容版）+ jax/jaxlib——轻量、无 torch 冲突。
   - 新建独立 venv/conda env `saturn`：clone snap-stanford/SATURN → 按其 requirements 装（内含 **torch==1.10.2+cu113** 旧栈），与基础 env 完全隔离。
   - 运行时数据预烘焙：ESM 预计算嵌入（snap.stanford.edu 分发，repo issue #19 有预计算包）+ 直系同源映射文件，COPY 进镜像。

**关键风险**：
- SATURN requirements 强钉 torch 1.10.2+cu113：若混装进基础 env 会**摧毁已验证的 scvi-tools 1.1.6 + torch 2.6 栈**——隔离是硬要求，不是优化。
- 平台是否接受外部 `docker save` tar 导入未验证——离线构建兜底链的最终一环，需先小实验确认，否则 wheelhouse 是唯一兜底。
- 构建产物大小（两套 torch ≈ 数 GB）可能触平台镜像配额/推送时长限制。

---

## 问2：SATURN 安装现实性

**推荐方案：GitHub 源码脚本式安装（snap-stanford/SATURN），独立 env + 数据预烘焙**

- SATURN **不是标准 pip 包**：无 setup.py 安装路径，入口是 `train-saturn.py` 等脚本；pip 装 `saturn`/`saturn-scripts` 这条路已被 v8 实测证死（索引不存在 + 权限拒绝）。正解 = clone 仓库 + `pip install -r requirements.txt`（在独立 sat env 内）+ 预计算数据落盘。
- 基镜像已有 fair-esm 2.0.0 + faiss-gpu 1.7.2 → 兜底能力：若 ESM 预计算嵌入下载不可达，可用镜像内 fair-esm **自产嵌入**（需 GPU 档任务跑推理，方案要先小规模验证）。
- **Plan B（若 SATURN 旧栈在平台 GPU/CUDA 12.4 驱动上跑不起来）**：降级为"scVI 限 1:1 直系同源基因"做跨物种基线扩展——scvi-tools 本在镜像内、零安装风险；报告中如实写"两方法 + 扩展基线"，不虚称三方法对等评测。

**关键风险**：
- pytorch-lightning 旧版钉定 + torch 1.10 组合是最大不确定点（API 代差），canary 冒烟必须包含 `train-saturn.py --help` 级验证。
- ESM 嵌入数据（数百 MB～GB 级）预烘焙体积与获取通道（snap.stanford.edu 在构建期是否可达）待验。

---

## 问3：scib-metrics kBET 与原版 R kBET 可比性论证（报告写法）

**推荐方案：四层论证**

1. **引证声明**：引 Büttner et al. 2019（Nature Methods）原文 + 明写"实现采用 scib-metrics vX.Y.Z"，版本号按例外 3 走镜像内实测回填（`pip show scib-metrics`），不提前填。
2. **差异披露**：把已知偏差写进 methods——①方向反转（scib-metrics 是 acceptance rate，R 原版是 rejection rate）；②无 `adapt` 选项（官方文档自述 "does not exactly mirror the default original implementation"）；③基于 kNN 邻域卡方检验的近似。同时写明 G3 已批准的方法变更记录（方案 B，commit 31efade）。
3. **内部一致性主张**：三方法（SATURN/SAMap/scVI）**全部用同一 kBET 实现** → 跨方法相对排序内部有效；只主张方法间比较，**不过度声明**与 R 原版数值等价。
4. **桥接验证（可选加分项）**：在任一有 R 的环境用原版 theislab/kBET（钉 commit SHA）对小子集复算，报告两实现在方法排序上的 Spearman 秩相关——有 maarten-devries/scib-benchmark（12 指标双实现等价性研究）作方法学先例。

**关键风险**：
- **scipy≥1.14 破坏 kBET**（2024-07 已知坑）——依赖必须钉 `scipy<1.14`。
- jax/jaxlib 版本一并钉进 image_versions；基础 env 现有 numpy/pandas 与 jax 0.4.x 的兼容性在冒烟任务里实测。
- kbet_version 红灯（例外 3）不能因"镜像装好了"提前变绿——必须容器内取证回填。

---

## 版本钉定速查（构建环境最终确认）

| 包 | 约束 | 依据 |
|---|---|---|
| scib-metrics | py3.9 → 只能 0.4.x / 0.5 早期；0.5 后期 ≥3.11，0.6.0+ ≥3.12 | PyPI/docs 版本阶梯（web 核验） |
| jax/jaxlib | py3.9 上限 ~0.4.3x；2023 实配 0.4.13 | 生态先例 |
| scipy | <1.14 | kBET 破坏坑 |
| torch(sat env) | 1.10.2+cu113（SATURN 原钉，隔离在 sat env） | SATURN requirements |
| theislab/kBET | 钉完整 commit SHA（若走桥接） | 例外记录惯例 |

## 验证路径（获批后执行序）

1. canary 镜像构建 → 判定平台构建期网络三态（通 / 不通 / 平台拒收外部 tar）。
2. 按结果选在线 pip 或 wheelhouse 离线层，产出含双 env + ESM 数据的镜像。
3. 新镜像发 1c4g 冒烟离线任务：`import scib_metrics`、`import jax`、sat env `python train-saturn.py --help`、全版本取证 → 回填 kbet_version / image_versions。
4. 三 h5ad（/Files/RawData/ 已实证可见）小样本端到端 SATURN + scib-metrics 冒烟。
5. 例外 2/3 补证关账；Codex 恢复后补评审一轮。

## Sources（web 核验）

- [snap-stanford/SATURN](https://github.com/snap-stanford/SATURN) — 安装形态、requirements 钉定、ESM 数据
- [scib-metrics docs · kbet](https://scib-metrics.readthedocs.io/en/stable/generated/scib_metrics.kbet.html) — 实现声明与偏差自述
- [scib-metrics · PyPI](https://pypi.org/project/scib-metrics/) 及版本历史 — requires_python 阶梯（3.8→3.11→3.12）
- [maarten-devries/scib-benchmark](https://github.com/maarten-devries/scib-benchmark) — 双实现等价性先例

## 附：Codex 独立评审意见（2026-09-21 晚，exec 只读）

- **总体**：架构可保留；执行前需补精确依赖锁定、SAMap 路线、SATURN GPU 冒烟、wheelhouse 可复现性、canary 三态错误分类。
- **canary**：不要把所有非零退出写成 OFFLINE——按 DNS/TLS/连接失败分类，记录状态码/错误类别/构建标识，保留构建日志（镜像内文件构建失败时取不回）。
- **Plan B（需修改后采用）**：现在就设为预批准交付分支+硬触发点（canary 完成/wheelhouse 构建完成/SATURN 过 --help+导入+GPU 检查+最小 forward 三道门槛，任一失败或超时即触发，不等完整运行失败）；报告措辞：SATURN 是"环境不可执行/未完成验证"，不能写成"性能较差"；scVI 直系同源基线是"可复现参照"不是等价第三方法；若课程硬性要求 SATURN 需同步取得课程方确认。

## 执行实录（2026-09-21 晚）

1. **镜像构建 API 破解**：`POST /stereonote/api/images/build`，载荷要点——image_toolkit 传**对象** `{latest:{Python3:[{toolkit_name,version}...],R:[]}}`（字符串形式 500 'str has no get'；缺 version 键 500）；其余：image_name/base_image_type='1'/build_type='tool'/base_image_id/base_image_name/base_image_url/root_type='1'/image_type=1/image_env=[]/project_id。
2. **canary 双投判定（三态收敛）**：net4（scib-metrics **latest**）→ status=2 构建失败=版本解析（latest 需 py≥3.11，镜像 py3.9）——**非网络问题**；pinned（**0.4.1**）→ status=1 构建成功（36.1GB）。**结论：平台构建期装包通道可用（内部镜像源），wheelhouse 兜底不需要，钉版本是硬要求**（Codex 评审的"错误分类"预判命中）。
3. **工作区换镜像的稳定通路**（镜像选择弹窗对自动化完全无效——历次任务其实都跑在工作区默认镜像上，此前"SATURN--22 选中"是默认值假象）：`POST /workspace/save` 克隆工作区，载荷关键字段 image_id/image_title/**image_url**（缺它 500 'image_url'）+version。已建 `g5-scib-verify-ws`（user50719-8334_3ea054f9b76a47e9a3fda9f939e2b35a，默认镜像 g5-canary-pinned）。
4. **v14 验证（pinned 镜像，14 秒完成）**：scib-metrics **0.4.1 已装入**（pip 元数据实测）；但 `import` 失败——基础镜像 jax 0.4.30 太新（`jax.random.KeyArray` 已移除，scib-metrics 0.4.1 需 jax≤0.4.23）。v12 对照组（SATURN--22）：scib MISSING ✓、six 1.16.0/jax 0.4.30/scipy 1.10.1（<1.14 kBET 安全）/numpy 1.26.0 均在。
5. **修正版构建中**：`g5-kbet-jaxpin`（9684374c7fbf4064a9a3df5118d9eb25）= scib-metrics 0.4.1 + **jax 0.4.23 + jaxlib 0.4.23** 三钉。构建完成后同工作区流程验证 import → kbet_version 回填。

## 收官（2026-09-21 21:57）

- **v15（KeyArray monkeypatch 版，pinned 镜像，21:57 完成）**：`import_scib: OK 0.4.1`、`kbet_fn: True`——**kBET 实现环境验证通过**。运行时需在脚本头部 `jax.random.KeyArray = jax.Array`（jax 0.4.30 兼容垫片，已写入 preflight 说明）。kbet_smoke "X must be a square matrix" 是冒烟调用姿势问题（scib kbet 需方阵距离矩阵），非环境缺陷。
- jaxpin 镜像（jax 0.4.23 降级）构建失败（status=2）——降级路线放弃，monkeypatch 路线胜出。
- **preflight 回填 kbet_version=0.4.1（实测）→ `ready_for_execution: true`，阻塞项清零**。测试护栏同步更新（60 tests 绿）。**课题5 全部门通过，HEART pilot 正式放行。**

## SAMap 攻坚（2026-09-21 深夜续）

- **g5-samap-try（samap==1.0.16）构建失败**（status=2）——内部镜像源装不上（依赖解析或源缺包）。
- **g5-samap-101（samap==1.0.1）构建中**（d79c575f705340e9a4bda3c2278afdd2，22:5x 投）。若再失败：SAMap 版本争议维持例外 1（页面歧义状态串），SAMap 数字改走"BENGAL 镜像入项申请"或平台工单请求开放 BENGAL。
- 注：平台自建的 BENGAL--SAMap--17 证明平台侧有能力构建 SAMAP 镜像（可能走 GitHub 通道）——若两版 pip 都失败，可在工单 TK20260921002545502 追问能否把 BENGAL 开放给课程项目。

## SAMap 攻坚结论（2026-09-21 23:0x）

- **g5-samap-101（samap==1.0.1）亦快速失败**（status=2，~2 分钟=解析/缺包级失败）——**内部镜像源不含 samap**（两版本皆试）。自建 SAMap 镜像路线关闭。
- **处置**：例外 1 维持（image_versions.SAMap 页面歧义状态串）；SAMap 数字依赖 **BENGAL--SAMap--17 开放**——已列入工单 TK20260921002545502 追问清单（请求把该镜像开放给课程项目，或提供平台侧 SAMAP 镜像的构建方式）。
- 今日 scVI 三物种 + kBET 环境两大战果不受影响。
