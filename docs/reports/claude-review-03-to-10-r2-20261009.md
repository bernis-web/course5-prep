# Claude 定向复核（批次三）：追加修订后最终版汇报 3–10（2026-10-09）

> 审阅人：Claude（claude CLI --print，只读；未修改任何文件）
> 对象：results/stage-reports-20261009/ 8 册 PPT（**批次三时点版本**，绑定当时 SHA256SUMS.txt）
> **[时效注记，批次四]** 批次四因方向表述更正重建了第 3/10 册：03 SHA 16b1fdfa→d04a02e8、10 SHA 3a1e58ee→105ae7ec；其余 6 册不变。本记录的 SHA 绑定为批次三时点值；当前有效绑定见批次四记录与 SHA256SUMS.txt（8/8 一致）。
> 背景：批次一审阅（claude-review-03-to-10-20261009.md，已加批次标注）→ 追加更正（消融基线等）→ Codex 第 2 轮 6 项收尾 → 本定向复核
> 结论：**revise**（①②③④⑤ 通过，SHA 复算 8/8；⑥ 索引批次区分待改；另发现上游矩阵 §三/§五 同类残留）
> **复核后执行者追加修正（未再经 Claude 复核，待 Codex 第三轮确认）**：
>   1. method-comparison-matrix §三 表：v97g → mapped-space；v99 n_q/coverage 拆 coarse（1,505/0.9805）与 exact（1,535/1.0）
>   2. 同文件 §五：斑马鱼→鼠例外多数类 0.4618 → 0.4817（映射空间）；斑马鱼方向行曾注明"query=鱼 范围"——**该范围写法于批次四被判定为错误并改为逐方向列数**（鱼作 query：z→h 0.1813 / z→m 0.5761；0.1961 / 0.2755 为鱼作目标）
>   3. index.md 重写：当前有效状态在前 + 历史批次标注取代关系（⑥）
>   4. SHA256SUMS.txt 行尾 CRLF → LF（sha256sum -c 可直接校验）

## 产物 SHA-256 清单（本复核绑定）

```
16b1fdfabdbdf232531ac784cb242d93ba45649e1707eb6d6bd1a78b9ea1fc7f  课题5第03次汇报_三方法公平比较边界.pptx
45f258ef0aa9f3811fedccef3e48c582673f94fd06cec680e013ad8cefc616c5  课题5第04次汇报_ortholog-PCA基线闭环.pptx
9b9dbf9644f613396fb5ae2b92d14644940f94ba9fb28fae04327ee4dc8dcf1c  课题5第05次汇报_SATURN信号与协议效应.pptx
64dd30ae871eef1b6179c0fc9cf8cc45594a5eb46ba946e5808dbe8517199ee2  课题5第06次汇报_SAMap复现与负结果.pptx
90b4d8f5b6f8c8c95f806c5ffd3a10d30f35a05a394ecbbd23e557cd961fb338  课题5第07次汇报_三方法总矩阵与老师问题.pptx
d8ec5c68d491b9a2a8bb3cbdaccbee2b73a5e18db6005e59a46eb61baf857b54  课题5第08次汇报_映射签认与证据责任.pptx
2dfac337eae2f48ae137dab25e8d4e6b74b03762420eb4eb35b9b6f23d550bab  课题5第09次汇报_最小inductive方案.pptx
3a1e58ee62faccf96fe651e31a986ed97bdab5690102af57db707a1a9a79951f  课题5第10次汇报_收口与下一阶段.pptx
```

---

复核完成。以下为定向复核（第 2 轮）结果。

---

# 定向复核（第 2 轮）：追加更正后最终版汇报 3–10（2026-10-09）

> 审阅人：Claude（只读；未修改任何文件）
> 对象：`results/stage-reports-20261009/` 8 册 PPT，绑定 `SHA256SUMS.txt`
> 环境：HEAD `8b597d7…`（工作树含未提交改动；本目录整体 untracked）

## 0. SHA-256 复算（先报告）

- 清单 `results/stage-reports-20261009/SHA256SUMS.txt` 列 8 份 pptx。
- **复算结果：8/8 与清单一致（OK）。**
- 发现一处清单文件本身的格式点：`SHA256SUMS.txt` 为 **CRLF 行尾**，直接 `sha256sum -c` 会把 `\r` 计入文件名而全部 "No such file"；剥离 CR 后 8/8 OK。逐文件实测值与清单逐行相同（例：03=`16b1fdfa…`、07=`90b4d8f5…`、10=`3a1e58ee…`）。

→ `sha_verified = true`

---

## 逐项复核

### ① 第 3 册 p7 与 method-comparison-matrix —— **需修改**（核心已达成；同文件 §三 未同步）

**已达成部分：**
- 第 3 册 p7 ①：「标签空间两套：ortholog-PCA、SATURN v97g = 映射标签空间；SATURN v99、SAMap = 原始标签空间（按各自规则过滤）」——与要求逐字一致 ✓；第③条亦已由旧稿 "v99（exact-space）" 改为 "v99（原始标签空间）" ✓（渲染 r03-p07 已确认）。
- `docs/evidence/method-comparison-matrix-20261008.md` **§六 item1**：由旧稿合写「SATURN/SAMap = 原始标签+过滤」改为「ortholog-PCA 与 SATURN v97g coarse/fine = 映射标签空间；SATURN v99 与 SAMap = 原始标签空间（按各自规则过滤）」✓（git diff 确认）。

**未同步（同文件 §三，「标签空间与分母」表）：**
- 第 29 行「coarse 标签」：SATURN **v97g = "原始标签+status 过滤"**（应 `mapped-space`）；v99 列 n_q/coverage 仍写 exact 值 `1,535（exact 无排除）` / `1.0`（coarse 应为 `1,505`/`0.9805`）。
- 此与勘误二（v97g=mapped 标签）、**第 3 册 p5**（v97g = "mapped-space（映射后粗类）"）、**第 7 册 p6**（"v97g：mapped-space"）直接冲突。git diff 显示本轮只改了 §五/§六，§三 未动。

→ 结论：指定拆分在 p7 与 §六 已落实，但同文件 §三 仍把 v97g 归入原始标签，**需同步**。

### ② 逐方向分母 —— **通过**
- 第 7 册 p3 口径框：「coarse 层 n_q 逐方向（h→m / m→h / h→z / m→z / z→h / z→m）：ortholog-PCA 与 v99 = 1,505 / 1,528 / 1,499 / 1,499 / 1,528 / 1,505；SAMap = 1,505 / 1,528 / 1,496 / 1,496 / 1,528 / 1,505（鱼方向差 3 待核验）」——与要求逐字一致，且我用 python 读三份 metrics.json 逐格复核**完全吻合**（oPCA/v99 coarse n_q=1505/1528/1499/1499/1528/1505；SAMap=1505/1528/1496/1496/1528/1505）。同页 v97g：「mapped-space · 日志级 …（n_q/coverage 保持日志级限定）」✓。
- 第 6 册 p6 ③：「18 格各按各自分母计算（n_q 1,496–1,528），全部 ≤ 10.5%；158 ÷ 1,505 仅为 h→m coarse 示例；included 旗标（1,398）不是另一种合法计分口径」——逐字一致 ✓（渲染 r06-p06）。
- `docs/reports/report-04-evidence-closure-20261008.md`：「ortholog-PCA coarse …n_q 逐方向…= 1505 / 1528 / 1499 / 1499 / 1528 / 1505」「SAMap coarse …= 1505 / 1528 / 1496 / 1496 / 1528 / 1505（鱼方向 1496 与 v99 的 1499 差 3，根因待核验）」——分母序列已更正、SAMap 鱼方向例外已注明 ✓。

### ③ 映射议题计数与同步 —— **通过**
- 第 8 册 p5 标题：「请导师重点审阅的 5 个议题（涉及 6 条源映射）」✓；第 5 行置信 = **"high（另有命名疑点）"** ✓（渲染 r08-p05）。
- 第 10 册 p5 行 2：「映射表 v1 人工签认（5 个议题，涉及 6 条源映射）」✓（渲染 r10-p05）。
- `docs/reports/report-08-mapping-signoff-20261009.md` L7：「整理 5 个审阅议题（涉及 6 条源映射：3 low + 2 medium + 1 high 命名疑点）」✓。
- 三处同步一致，且 3低+2中+1高=6 与"5 议题"自洽（议题 1 含 mouse Valve + 斑马鱼 Valve 两条）。

### ④ 状态矩阵消融 —— **通过**
- `docs/evidence/status-matrix-20261008.md` A7 行已改为「ESM2 消融（67.4→20.4，v72-era 同协议历史配对；v97g 对应消融未重跑）」，缺口列「原"61.8%→20.4%"为跨协议混排，已按勘误三更正」✓（git diff 确认 61.8→67.4）。

### ⑤ 批次标注 + SHA 绑定 —— **通过**
- 批次一审阅记录 `docs/reports/claude-review-03-to-10-20261009.md` 第 6–9 行已加：「**[批次标注，2026-10-09 追加]** 本记录为**批次一**…**本批次结论不直接代表最终版**；追加修订的定向复核见 `docs/reports/claude-review-03-to-10-r2-20261009.md`（绑定最终产物 SHA-256）」✓。
- SHA 绑定：本 r2 记录以 `SHA256SUMS.txt` 复算为锚（8/8 OK），满足"归档为 claude-review-03-to-10-r2-20261009.md 并绑定 SHA"。

### ⑥ index.md 批次/状态区分 —— **需修改**
- `results/stage-reports-20261009/index.md` 虽按轮次分节（"## Codex 只读审计第 1 轮…与修订记录"、"## Claude 逐册审阅"），但**未区分"历史批次"与"当前有效状态"**：全文无"历史批次/当前有效状态"标注；且"阶段划分"状态列仍为 **"初稿（Claude 评审待闭环）"**（第 13–20 行）、"待办"仍列 **"Claude 逐册审阅（每阶段固定评审回合）"**（第 49 行），与同一文件末尾"Claude 逐册审阅…结论 **pass（8/8 册）**"及追加更正后的状态不一致。建议加一行批次/状态说明并同步状态列。

---

## 抽核：修订页渲染（r03-p07 / r06-p06 / r07-p03 / r08-p05 / r10-p05）—— **通过**
- 目视 5 页：卡片文字、表格末行、口径长行均完整，无遮挡、无越界。
- 程序化几何检测（页内文字元素两两求交，阈值 2e4 EMU²）：**0 处显著重叠、0 处出界文字**，5 页均 clean。

## 回归：未引入新错误
- 第 7 册 p3 表用 metrics.json 逐格复核：acc（0.8618/0.7369/0.1961/0.2755/0.1813/0.5761 等）与多数类分列（映射空间 oPCA 0.4817 / 原始标签 v99·SAMap 0.4618；h→z·m→z 0.3976/0.3977）**全部吻合**。
- 第 6 册 p4 SAMap 表（0.1050/0.0196/0.0341/0/0/0；n_q 1505/1528/1496/1496/1528/1505）与 metrics 一致；第 8 册 p4「SAMap 47*」（1,543−1,496=47）自洽。

---

## 残余 / 未关项

1. **matrix §三 未同步**（见 ①）：v97g 标签空间仍标"原始标签"，v99 coarse 列误用 exact 值。
2. **matrix §五 口径**：第 48 行「唯一例外…0.5761 > **0.4618**」用的是原始标签空间多数类；oPCA 属映射空间，应为 **0.4817**（第 3 册 p7 已用 0.4817），同一文件内不一致（本轮未动此行）。
3. **index.md ⑥**：未明确区分历史批次与当前有效状态（状态列/待办未随最新结论更新）。

（说明：①②③④⑤ 与 5 页渲染、SHA 复算均通过；未发现修订在**册内数字**层面引入的新错误。剩余均为上游证据文档/索引层面的一处同步与口径不一致。）

```json
{"review_r2": "revise", "sha_verified": true, "remaining": ["docs/evidence/method-comparison-matrix-20261008.md §三「coarse 标签」行 SATURN v97g 仍标'原始标签+status 过滤'（应 mapped-space），v99 列 n_q/coverage 仍为 exact 值 1,535/1.0（coarse 应 1,505/0.9805），与勘误二、第 3 册 p5、第 7 册 p6 冲突", "同文件 §五「0.5761 > 0.4618」多数类口径不一致：oPCA 属映射空间，应为 0.4817（第 3 册 p7 用 0.4817）", "results/stage-reports-20261009/index.md 未明确区分历史批次与当前有效状态：阶段划分状态列仍'初稿（Claude 评审待闭环）'、待办仍列'Claude 逐册审阅'，与文件内 Claude pass 结论及追加更正后状态不一致"]}
```
