# Phase 5 Gate 5 自检材料：SAMap v98 主流程调用链（2026-10-02，commit e351f59）

> 供 Claude 审阅。审阅对象 `scripts/run_samap_compliant_v98_dcs.py`（DCS 提交用）与 `scripts/run_samap_compliant_v98.py`（本地镜像变体，测试引用它）。

## 主流程调用链（Phase 5 检查单逐项）

| # | 计划要求 | 实现位置 | 状态 |
|---|---|---|---|
| 1 | 每物种经 `load_species()` 应用 `hu\|/mo\|/zf\|` | main: `a = load_species(root / fn, sp_name)` → `s = SAM(); s.adata_raw = a`（不再用 `s.load_data()` 直读） | ✅ |
| 2 | 合并前 `assert_prefix_unique()` | main: SAMAP 构造前 `assert_prefix_unique([prefixed[human,mouse,zebrafish]])` | ✅ |
| 3 | 每 truth 列 `assert_no_na_truth()` 失败非零退出 | main: 每物种加载后即断言；合并后再查 join 残留 NA，`>0 → raise V98Error`（进程非零退出） | ✅ 双重 |
| 4 | 写 command/environment/manifest/metrics/predictions/confusion/全量 SHA | main: environment.txt、command.txt、metrics.json、predictions/×18、confusion/×18、manifest.output_sha256 全文件 | ✅ |
| 5 | 固定 `sm.run(NUMITERS=3, ncpus=1, umap=False)` | main L343 | ✅ |
| 6 | unittest 失败门测试 | tests/test_run_samap_compliant_v98.py：GateTests 缺 truth 列 / NA 真值 / 重复 barcode 三例 + 既有 6 例 = 9/9 | ✅ |

## 每物种循环内顺序（防泄漏视角）

```
load_species(path, species)     # 前缀化 obs_names + zf 重复基因确定性去重(记录 uns)
assert_no_na_truth(a)           # NA 真值 → V98Error（非零退出）
SAM(); s.adata_raw = a          # SAMAP.prepend_var_prefix 依赖 adata_raw
s.preprocess_data(cell_median/log/0.96)   # 仅表达值，不含标签
s.run(StandardScaler, npcs=100, k=20)     # 无监督
assert_prefix_unique([...])     # 三物种全局唯一后才允许 SAMAP 合并
SAMAP(sams, keys={sp: "cell_type"}, gnnm=...)  # label-aware 已在 manifest 声明
sm.run(NUMITERS=3, ncpus=1, umap=False)
```

## 评估器口径（与 v99/ortholog-PCA 统一协议对齐）

- K=15 cosine 倒距离加权（`1/(d+1e-12)` 累计投票，`max((score,label))` 决胜——平票取字典序最大，确定性）
- coarse/fine 双向排除 `mapping_status != active`（ref+qry），exact 保留全部有效真值
- **included 语义**：查询细胞真值不在参考训练标签集 → 不进 acc/confusion 分母，逐细胞记 `exclusion_reason=truth_not_in_reference_training_labels`，报 `n_q_total / coverage_q`
- 置换：RandomState(seed=0) 洗牌 included 预测 200 次，单侧 p
- confidence = 胜出标签票权 / 全部票权（4 位小数）

## 请 Claude 裁决

1. 调用链是否有标签泄漏路径（keys=cell_type 影响 SAMAP 联合图构建已声明 label_aware——是否接受此 operationalization，还是要求去掉 keys 重跑？）
2. included=真值∈参考训练标签集 的语义与 v99 的 mapping_status 排除叠加后，分母口径是否与 v99 一致（差异点：v99 无"真值不在参考标签集"这层）？
3. `max((score, label))` 平票决胜规则是否可接受（v99 用的同类决胜但实现不同）？
4. DCS 一次性提交前还需什么证据？
