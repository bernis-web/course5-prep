# Claude/Codex 路线图查缺补漏记录（2026-09-29）

## Claude 调用状态

- `claude --print --bare --model glm-5.3-flash "只回复 OK"` 在本次会话返回 `OK`，说明最小连通性正常。
- 三次只读长审查（其中一次禁用全部工具并直接提供计划全文）和一次聚焦协议审查均在限定等待时间内无正文输出，已按停止线中断。
- 因此本轮没有可归因于 Claude 的实质科学意见，也没有把超时当作审查通过；未修改或提交任何 DCS 资源。

## Codex 审计后必须加入的门

1. 将 SH 拆成 SH-T 与 SH-I，并把完全未见物种单列 OOS-S；三者不得混排。
2. query truth 作为 scoring-only 文件与训练任务隔离；重排 truth 后 embedding/预测 SHA 必须不变。
3. 主榜在共同 eligible universe 上计算，abstention 主指标计错，同时报告 covered-only 指标、coverage 和 risk-coverage 曲线。
4. 预注册 `TLB × coarse` 主检验族，正式置换报告 BH-FDR；200 次只用于流程检查。
5. CI 优先按 donor/sample/region cluster bootstrap；三个 seed 只描述算法随机性，不替代生物学重复。
6. 冻结最低 class support；SH-I 缺少至少 3 个独立单位时填 `N/A`，不退化为随机细胞切分。
7. 资源只因可复现工程失败升一级，重试费计入预算，达到阶段门 80% 时先停止汇报。
8. 物种对在查看模型性能前按数据质量、共同标签、ortholog 覆盖和系统发育层级冻结，避免结果驱动选对。

## 判词

总体路线可执行，但在上述门补齐前，不应启动新的 GPU 正式训练。近期优先级仍是 provenance 恢复、SAMap v98 合规产物、mapping 人工签认和统一评分器。
