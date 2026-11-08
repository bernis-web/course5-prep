# DCS-P0：v97g 只读定位（2026-09-29）

## 结论

v97g 已唯一定位：**g5-v97g-rule-compliant-eval-1**，subtask `2104535560372703234`，batch `2104535560355926018`。

## 定位过程

在 offline/page（subTask=1）最近 10 条中按任务名 v97 关键词筛选，共 7 条 v97 系列候选。逐一核对：

| 候选 | 指纹判定 |
|---|---|
| g5-v97g-rule-compliant-eval-1 | **匹配**：SHA 门 assert 通过（20cf807f…）+ coarse/fine 双向排除 + EVAL3G 全量指标 |
| g5-v97f-incore-eval-1 | 排除：全保留版（unmapped 未排除），协议不符 |
| g5-v97e-incore-eval-1 / probe0 | 排除：轴错误版 / 占位探针 |
| g5-v97-extract / v97b-cat / v97c-cat | 排除：提取与日志容量测试任务，非评估 |

## 关键元数据（非敏感字段）

- subtask ID：`2104535560372703234`
- batch ID：`2104535560355926018`
- 状态：**Failed**（脚本收尾段退出码非零；EVAL3G 指标行在失败前已完整打印——`eval3_v97g_out.txt` 全文在盘）
- 镜像/资源：SATURN--22 / 1c 4g
- 时间：2026-09-28 19:35:53 → 19:36:45（52 秒）
- 既有产物（/data/work，持久）：`eval3_v97g_out.txt`（含 EVAL3G 全量 JSON）、`eval3_v97g.py`、`v97_out/`（bundle_core.npz + 5 分块 + READY.json + SHA256S.txt）、`/Files/wheelhouse/v97_out/` 镜像副本

## 指纹核对

- Final AnnData SHA-256 = `20cf807f…`（脚本内 assert 通过）✓
- obsm/macrogenes 4606×1000 ✓；k=15 cosine ✓；seed=0 ✓
- coarse/fine 双向排除 unmapped（v97g 脚本逻辑 + coverage/excluded 单列）✓

完整元数据：`results/pilot-v1/saturn-v97g/raw/task-metadata.json`
