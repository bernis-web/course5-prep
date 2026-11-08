# Claude 定向复核（审阅③，批次四）：方向表述更正后的最终版（2026-10-09）

> 审阅人：Claude（claude CLI --print，只读；未修改任何文件）
> 对象：results/stage-reports-20261009/ 8 册 PPT（批次四重建后版本，绑定 SHA256SUMS.txt）
> 背景：Codex 第三轮指出第 3 册 p7 与方法矩阵 §五 的斑马鱼方向表述错误（query/目标搞反）→ 执行者改为逐方向列数 → 本复核
> 结论：**pass**（六项全部通过；4 项非阻断残余见文末，其中 3 项已在本记录归档时同步处理）
> 说明：批次四重建了第 3/10 册，SHA 已重算（03 16b1fdfa→d04a02e8；10 3a1e58ee→105ae7ec；其余 6 册不变）。

## 产物 SHA-256 清单（本复核绑定，批次四重建后）

```
d04a02e84a322d9e4b6e684ef00d891bb612f59f30c82f1125702db5ee193650  课题5第03次汇报_三方法公平比较边界.pptx
45f258ef0aa9f3811fedccef3e48c582673f94fd06cec680e013ad8cefc616c5  课题5第04次汇报_ortholog-PCA基线闭环.pptx
9b9dbf9644f613396fb5ae2b92d14644940f94ba9fb28fae04327ee4dc8dcf1c  课题5第05次汇报_SATURN信号与协议效应.pptx
64dd30ae871eef1b6179c0fc9cf8cc45594a5eb46ba946e5808dbe8517199ee2  课题5第06次汇报_SAMap复现与负结果.pptx
90b4d8f5b6f8c8c95f806c5ffd3a10d30f35a05a394ecbbd23e557cd961fb338  课题5第07次汇报_三方法总矩阵与老师问题.pptx
d8ec5c68d491b9a2a8bb3cbdaccbee2b73a5e18db6005e59a46eb61baf857b54  课题5第08次汇报_映射签认与证据责任.pptx
2dfac337eae2f48ae137dab25e8d4e6b74b03762420eb4eb35b9b6f23d550bab  课题5第09次汇报_最小inductive方案.pptx
105ae7ecc6c24c886dbfdf90d74aff4fb691da4c99ecab67022273bce86854a8  课题5第10次汇报_收口与下一阶段.pptx
```

---

复核完成。以下是逐项结果。

**环境**：`D:\projects\course5-prep`；HEAD `8b597d7`（`results/stage-reports-20261009/` 整体 untracked，工作树含未提交改动）。本轮只读，未修改任何文件。

---

## ① 第 3 册 p7「可讲的方向性观察」卡 — **通过**

**依据**
- 成品 PPTX 第 7 页（python-pptx 抽取）与生成脚本 `results/stage-reports-20261009/build_report03.js` L94–95 文本一致：
  `oPCA：h→z 0.1961 ／ m→z 0.2755 ／ z→h 0.1813 ／ z→m 0.5761`；`SATURN v97g：h→z 0.1835 ／ m→z 0.3009 ／ z→h 0.2474 ／ z→m 0.4651`；`SAMap：h→z 0.0341 ／ m→z 0.0000 ／ z→h 0.0000 ／ z→m 0.0000`。
- 逐格复算 `results/pilot-v1/ortholog-pca-v98/metrics.json`（coarse 层）：`human->zebrafish 0.1961`、`mouse->zebrafish 0.2755`、`zebrafish->human 0.1813`、`zebrafish->mouse 0.5761` — **全对**。方向语义正确：h/z 作 query、目标为 z/h（鱼作 query 即 z→h 0.1813 / z→m 0.5761，与 Codex 指正一致；0.1961/0.2755 为鱼作目标）。
- `samap-v98/wdl-run/extracted/metrics.json`（coarse）：h→z `0.0341`、m→z `0.0`、z→h `0.0`、z→m `0.0` — **全对**。
- v97g 以 `docs/transductive-formal-v74-evidence-20260928.md` L62–69 合规表：human→zebrafish 18.35%、mouse→zebrafish 30.09%、zebrafish→human 24.74%、zebrafish→mouse 46.51% — **全对**（与 `frozen-numbers.json` 的 saturn_v97g 节点一致）。
- 读数行「仅 oPCA 的 z→m（0.5761）超过其多数类 0.4817」亦真：z→m coarse majority = 0.4817（metrics），其余方向均低于各自多数类。

## ② 方法矩阵 §五 同步 + 多数类 0.4817 — **通过**

**依据**（`docs/evidence/method-comparison-matrix-20261008.md`）
- L49 已改为**逐方向列数**：`逐方向（h→z / m→z / z→h / z→m）：oPCA 0.1961 / 0.2755 / 0.1813 / 0.5761；SATURN v97g 0.1835 / 0.3009 / 0.2474 / 0.4651；SAMap 0.0341 / 0 / 0 / 0`，与①同源逐格吻合，无含混范围。
- L50「唯一例外：斑马鱼→鼠 ortholog-PCA 高于多数类」= `0.5761 > 0.4817（映射空间多数类）` — oPCA 属映射空间，z→m coarse majority = **0.4817**（metrics.json `zebrafish->mouse.coarse.majority`），**正确**（此前误用的 0.4618 系原始标签空间，已消除）。
- 旁证：§三（L25–35）本轮已同步（v97g=mapped-space；v99 拆 coarse 1,505/0.9805 与 exact 1,535/1.0），未回退。

## ③ 渲染件 `render/r03-p07.png` 版式 — **通过**

**依据**
- 目视：标题、左卡「五项不可比」、右卡「可讲的方向性观察」、底部 band、页脚均完整；文字未与卡片边框/band/页脚重叠。
- 几何复核（pptx 形状）：右卡 `L7.28 T1.82 W5.32 H4.30 → bottom 6.12`；正文框 `T2.28 H3.74 → bottom 6.02`（< 6.12）；band `T6.35`。左卡右缘 7.02 < 右卡左缘 7.28。**无越界、无遮挡**。
- 唯一小瑕疵（非阻断）：SATURN 与 SAMap 两行因宽度折行（`… z→m` 换行接 `0.4651` / `0.0000`），仍可读。

## ④ 版本保留措辞 — **通过**

**依据**
- 第 10 册 p4（成品抽取 + `build_report10.js` L50/L60）：标题 `交付物清单（版本化；可核实旧件保留）`；band `可沿 SHA 回溯（SHA256SUMS.txt）；可核实原始旧件保留；中间修订版曾原地重建、未单独归档，历史"未覆盖"声明待基线核验。` — 两要素齐备。
- `index.md` L56：「未提交、未推送；**可核实的原始旧件**未被覆盖（中间修订版曾原地重建、未单独归档；历史"未覆盖"声明待逐轮基线累积核验）」；L114 同步说明第 3/10 册重建 + SHA 重算。

## ⑤ SHA256SUMS.txt 8/8 — **通过**

**依据**：`cd results/stage-reports-20261009 && sha256sum -c SHA256SUMS.txt` → **8/8 OK**。文件为 UTF-8/LF、8 行（可直接 `sha256sum -c`，CRLF 问题已修）。

## ⑥ 历史审阅记录更正注记 — **通过**

**依据**
- `docs/reports/claude-review-03-to-10-20261009.md`：L22 原文保留（「抽核 p7「斑马鱼方向」区间：oPCA 0.18–0.28…」），L23 新增 `>[更正注记，2026-10-09 批次四]`，标明"区间+query=鱼"写法错误、给出正确逐方向值（z→h 0.1813 / z→m 0.5761；0.1961 / 0.2755 为鱼作目标）、"保留原文以备对照"。
- `docs/reports/claude-review-03-to-10-r2-20261009.md`：L9 新增注记，「该范围写法于批次四被判定为错误并改为逐方向列数」，原文未改写。
- `index.md` 批次四「历史记录」行明确：「批次一/批次二审阅记录加**更正注记**（不改写原文）」——与两文件实证一致。

---

## 非阻断残余（供下一轮，不影响本轮六项结论）

1. **r2 记录的 SHA 绑定已过时**：r2 记录 L16/L23 绑定 03=`16b1fdfa…`、10=`3a1e58ee…`；批次四重建后现产物为 03=`d04a02e8…`、10=`105ae7ec…`（其余 6 册不变）。同时 `docs/handoff-to-codex-round3-20261009.md` L34「8 份 PPT 自定向复核后**未再重建**」与事实不符（03/10 确已重建）。当前 `SHA256SUMS.txt`（17:22）与产物一致，故 ⑤ 仍通过，但建议在 r3 交接/r2 记录补一句"03/10 因批次四重建、SHA 已重算"。
2. **批次编号不一致**：`index.md` 称 Claude 逐册审阅为「批次二」（该小节副题又写"批次一审阅"），而 `claude-review-03-to-10-20261009.md` 自标"批次一"、r2 自标"批次三"。同一工作流的轮次命名建议统一。
3. **陈旧描述未加注**：`handoff-to-codex-round3-20261009.md` L30 仍写 §五「斑马鱼方向行注明"query=鱼"范围（oPCA 0.18–0.28）」——该写法已在批次四判定为错，此交接件未加更正注记（属历史交接件，非审阅记录）。
4. **前向引用暂悬空**：`index.md` L116 引用 `docs/reports/claude-review-03-to-10-r4-20261009.md`（即本轮输出），当前该文件尚不存在，待本轮记录归档后消解。

---

```json
{"review_r4": "pass", "remaining": ["r2 定向复核记录绑定 SHA 已过时：03 由 16b1fdfa→d04a02e8、10 由 3a1e58ee→105ae7ec（批次四重建），且 handoff-to-codex-round3 L34 '未再重建' 与事实不符；建议补注记（当前 SHA256SUMS.txt 本身 8/8 一致）", "批次编号不一致：index.md 称 Claude 逐册审阅为'批次二'（小节副题又写'批次一审阅'），而 claude-review-03-to-10-20261009.md 自标'批次一'、r2 自标'批次三'", "handoff-to-codex-round3-20261009.md L30 仍描述 §五 为 'query=鱼 范围（oPCA 0.18–0.28）'（已属历史交接件），未加更正注记", "index.md L116 引用 claude-review-03-to-10-r4-20261009.md 尚不存在（本轮记录待归档后消解）"]}
```
