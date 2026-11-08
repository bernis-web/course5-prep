# Inductive Pilot 实验设计 manifest v1（设计完成，未运行）

> 状态：设计完成，等用户与导师批准后方可运行。本文档不构成已执行实验的证据。

## 目的

弥补当前全部结果为 transductive/in-sample 的结构性局限。通过留一物种（leave-one-species-out）的严格 inductive 协议，测试跨物种映射方法的泛化能力。

## 设计

| 参数 | 值 | 说明 |
|---|---|---|
| 留出策略 | leave-one-species-out ×3 | 轮流留出鼠/鱼/人作为严格 held-out query |
| query 物种可见性 | 表达数据和标签在训练阶段完全不可见 | 与 transductive 的根本区别 |
| 表示层训练 | 仅用剩余两物种训练；第三物种投影时模型不更新 | 严格 inductive |
| 评估 | KNN15 cosine（同 transductive 协议）+ coverage + majority | 保持可比较 |
| 方法 | ortholog-PCA + SATURN + SAMap（三方法同跑） | 公平比较 |
| seed | 0, 1, 2（三 seed 取均值±sd） | 解决单 seed 限制 |
| 资源档 | SATURN 需 GPU；其余 CPU | 预算见下 |
| 预算上限 | 单次 GPU 运行 ≤ ¥50 | 保险丝不变 |
| 预期产物 | 3 物种 × 3 方法 × 3 seed × exact/coarse/fine = 81 格 | 全部为 inductive |
| 停止条件 | 任何任务失败 → 停止 → 分析原因 → 用户批准后方可重试 | 不自动重试 |
| 产出层级 | inductive（首次可写 held-out benchmark） | 与 transductive 严格分开 |

## 前置条件

- mapping v1 获导师签认（或 v2 按导师意见修订后签认）
- 离线调度通道恢复（或 WDL 通道被批准为正式运行通道）
- 用户明确批准 GPU 预算
- 本报告经 Claude 审阅通过

## 与 transductive 结果的关系

- transductive 回答：目标物种参与整合后，标签迁移有多好？
- inductive 回答：训练时完全没见过的物种，模型能迁移吗？
- 两者不可互相替代；inductive 预期低于 transductive（幅度=方法泛化能力的度量）
