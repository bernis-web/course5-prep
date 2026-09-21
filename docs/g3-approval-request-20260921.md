# G3 启动批准申请（HEART pilot，2026-09-21）

> 致：四人批准小组。本文是 G3 门的一次性批准材料。批准=允许按"运行方案"节启动 HEART pilot；不批准或要求修改请直接批注。

## 一、门状态（截至今晨）

| 门 | 状态 | 证据 |
|---|---|---|
| G0 本地基线 | 通过 | 60 tests 绿（2026-09-21 复跑） |
| G1 数据 | 通过（09-20 关账） | 三物种 h5ad 落盘 RawData 逐字节核对；金标准列 celltype |
| G2 环境 | 通过（09-21 带三项例外关账） | `docs/g2-closure-exceptions-20260921.md` + `docs/g2-offline-probe-evidence-20260921.md` |
| G3 | **本申请** | preflight 剩余阻塞：approval_status（本件）+ kbet_version（首跑实测后回填，例外3） |

## 二、需四人裁决的事项：kBET 实现路线（二选一）

| | 方案 A：原版 R kBET | 方案 B：scib-metrics |
|---|---|---|
| 来源 | GitHub `theislab/kBET` 钉 commit SHA | pip 装 `scib-metrics` |
| 与文献可比性 | 原始实现，与发表基准直接可比 | Python 重实现，与原版结果**不完全一致** |
| 安装成本 | 需 R 环境+GitHub 离线依赖（镜像有 R 系包但安装链未验证） | pip 一步，与镜像 scanpy 生态同栈 |
| 评审意见 | Codex 荐（换实现=方法变更须显式批准） | Claude 荐（版本仍须实测钉死） |

**请批注：A / B / 暂缓**。裁决后首跑实测版本回填 `kbet_version`（例外3 关闭条件）。

## 三、运行方案（批准对象）

1. **通道**：DCS 离线任务（公网可用，无需 VPN/notebook 界面）；脚本经 printf 单行化写入执行（坑已入档）。
2. **数据**：仅 `/Files/RawData/` 三物种 h5ad 只读挂载，不复制不上传。
3. **步骤**：①1c4g 冒烟（SATURN pip 安装+kBET 装机+版本取证，回填 kbet_version）；②GPU 档（3080Ti×1 88c320g，约 ¥30.78/h，课程方计费组）跑 scVI 基线单物种（人，30k 细胞）；③结果经 ResultData/文件 API 回读。
4. **停止线**：单次 GPU 会话 ¥10 或 25 分钟硬停（以先到者为准）；脚本内置超时；异常=立即停+记录 `failure_reason.txt`；结束即停容器。
5. **记录**：全程入 `docs/ai-use-log.tsv` 与运行目录骨架（startup-shutdown-checklist v0.1 执行）。

## 四、风险与对策

- 离线 runner 单行化：已解（printf 法，v6 实证）。
- SATURN 包需安装：镜像无 SATURN 本体，首跑 pip 装（若装不上→只跑 scVI/SAMap 线，SATURN 线单独重议）。
- GPU 型号存疑（L4 vs 3080Ti 页面矛盾）：首跑 GPU 会话 nvidia-smi 取证定夺。

## 五、批准记录（四人签名）

| 姓名 | 批准/否决/批注 | kBET 选择 | 日期 |
|---|---|---|---|
| | | | |
| | | | |
| | | | |
| | | | |
