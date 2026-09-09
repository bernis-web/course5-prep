# 三人协作分工

这不是固定排班，而是三条可以轮换的主线。每个人先认领一条主线，同时至少复核另一条主线的一个交付物；不要因为分工而绕过共同的启动门和预算规则。

## 打开仓库后的轻量认领

先把自己的名字写进分支名或 Pull Request 标题，再从下面选一条主线。表里的“第一件事”是为了让大家马上能开始，不代表以后只能做这一类工作。

| 建议认领 | 主要关注 | 第一件事（不需要云资源） | 主要交付位置 | 建议复核 |
| --- | --- | --- | --- | --- |
| 组员 A | 数据与生物学 | 逐项整理 `docs/teacher-data-request.md` 的 6 个待确认问题，收到老师回复前保持 `pending`，不要猜路径或字段 | `config/startup-preflight.json`、`input_manifest.tsv`、`ortholog_manifest.json` | 组员 C 复核标签转移和金标准定义 |
| 组员 B | 环境与算力 | 运行本地预算/环境预检，读懂 `docs/dcs-image-probe-plan.md` 的证据边界，先不启动实例 | `config/environment-compatibility-plan.json`、`config/dcs-budget-plan.json`、资源记录 | 组员 A 复核数据挂载与内存假设 |
| 组员 C | 评测与报告 | 运行测试与合成 smoke test，按 `config/benchmark-plan.json` 建立真实数据的指标表骨架 | `tests/`、`config/benchmark-plan.json`、运行报告 | 组员 B 复核版本、时间、内存和公平性记录 |

如果某条主线被课程确认事项卡住，可以先接手另一条主线的复核任务；认领人负责推进和记录，所有人共同决定是否进入真实运行。没有必要为了“分工完整”提前填写未知信息。

## 主线 A：数据与生物学

**建议主责：** 熟悉论文、数据结构和细胞类型定义的同学。

**第一步：** 根据 `docs/teacher-data-request.md` 和 `docs/course-admin-reply-template.md` 向课程管理员确认 HEART/LBSPA 路径、文件格式、物种/细胞类型/批次/金标准字段，以及一对一同源基因表的来源。

**交付物：**

- 填写 `config/startup-preflight.json` 中的数据字段和子集信息；
- 为每个数据子集准备不含原始表达矩阵的 `input_manifest.tsv`、同源基因源表和 `ortholog_manifest.json`；
- 用 `python scripts/ortholog_contract.py <ortholog-table.tsv> --output <ortholog_manifest.json>` 检查一对一同源基因表，并把 SHA-256 和物种对写入运行记录；
- 在 `docs/source-notes.md` 或新的数据说明中记录标签来源、排除规则和 modality 边界。

**需要协作：** 请环境与算力主线复核路径是否可读、文件是否适合候选镜像；请评测与报告主线复核留一物种标签转移设计。

## 主线 B：环境与算力

**建议主责：** 愿意核对 DCS 页面、镜像和资源成本的同学。

**第一步：** 在获得课程管理员确认后，按 `docs/dcs-image-probe-plan.md` 和 `docs/containerization-plan.md` 做只读核验，再用 `environment_check.py` 和 `environment_contract.py` 检查 `SATURN--22`、`samap_all` 或课程指定镜像；不安装包、不启动实例，除非组内明确批准。

**交付物：**

- 更新 `config/environment-compatibility-plan.json` 的实例内版本和命令级证据；
- 更新 `config/dcs-budget-plan.json` 或运行资源记录，保留价格来源、GPU/内存、耗时和停止原因；
- 为一次单卡 smoke run 写出可复用的启动/停止检查清单。

**需要协作：** 请数据与生物学主线确认挂载路径和内存需求；请评测与报告主线确认同一工具是否在公平的容器和版本条件下比较。

## 主线 C：评测与报告

**建议主责：** 擅长指标、可视化、写作或整理实验记录的同学。

**第一步：** 先在合成数据上运行测试，确认 macro-F1、silhouette、iLISI、kBET 代理和资源记录格式，再设计真实数据的留一物种评估表。

**交付物：**

- 维护 `config/benchmark-plan.json` 的固定随机种子、HVG、邻居数和指标定义；
- 用 `run_artifacts.py` 检查每次运行的参数、版本、日志、指标和资源文件；
- 汇总 `agent_evaluation.py` 所需的命令/API、输出和失败证据，最终形成基准报告和场景化选型指南。

**需要协作：** 请数据与生物学主线复核金标准和生物保守性解释；请环境与算力主线复核时间、峰值内存、GPU 和成本记录。

## 共同工作方式

1. 任何人都可以接手另一条主线；主责只是当前推进人，不是审批人。
2. 每个 Pull Request 说明：改了什么、使用了哪份输入、如何验证、是否触碰 DCS。
3. 真实运行前，三个人共同确认 `startup_preflight.py` 返回 `ready_for_execution: true`，并明确单次预算和停止条件。
4. 真实运行后，至少一名非主责成员复核 manifest、版本、日志、资源和失败原因；AI 使用记录追加到 `docs/ai-use-log.tsv`。
5. 任何路径、版本或指标未确认时，宁可标记 `pending`，不要用猜测填满表格。

### 每次提交只回答四件事

Pull Request 或工作记录尽量写清楚：改了什么、使用了哪份输入、如何验证、是否触碰 DCS。三个人可以共同修改同一条主线，但每次提交最好只推进一个小问题，方便互相复核和回退。

## 推荐的第一周顺序

1. A 收集课程管理员的六项确认；B 复核仓库中的预算/镜像约束；C 运行本地测试套件并熟悉运行产物（测试数量以当前仓库输出为准）。
2. A 拿到字段后更新启动门；B 根据只读环境报告更新镜像证据；C 准备真实运行的指标表和报告骨架。
3. 三人共同审查启动门和预算，确认后再决定是否申请第一次单卡试运行。
