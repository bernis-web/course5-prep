# 报告 14：演示设计外部调研 + v4 的 CRAP 自审（2026-11-11）

> 上一份 `report-13` 是我「先量基准再改」的记录；这一份是**去外面找权威框架**之后的结果。
> 目的：把「我觉得好看」换成「有名字的规则」。

---

## 一、调研渠道与结果（都可复现）

| 渠道 | 查到什么 | 链接 |
|---|---|---|
| B站搜索「PPT 排版 设计 原则」 | 中文圈反复讲的就是**四原则**：对齐/对比/重复/亲密性 | `BV18a411Q7zN`（檀东东）、`BV16b411U7rt`（旁门左道）、`av113028641129051`（四大黄金原则） |
| B站搜索「组会 学术汇报 PPT」 | 高播放的是「文献汇报怎么做」「让导师不骂的汇报 PPT」——**受众是导师**，关心逻辑不是炫技 | `BV…354057` 播放量最高 |
| Exa 搜「slide design principles …」 | **CRAP/CARP 四原则**（Robin Williams《The Non-Designer's Design Book》）；**Presentation Zen 七原则**（Garr Reynolds）；华盛顿大学给科研人员的《Little Book of Visual Design Principles》 | wagner.edu、fsu.edu、oreilly（Presentation Zen 第 6 章）、depts.washington.edu |
| GitHub API 搜 slide/pptx 工具 | Markdown→幻灯工具一堆，且都把**演讲者备注当一等字段**：`k1LoW/deck` 1243★、`decker-edu/decker` 101★、`technopagan/slides-in-markdown` 91★（remark.js，带 presenter console） | github.com/k1LoW/deck 等 |

---

## 二、学到的两套框架（这才是标准）

### 2.1 CRAP 四原则（Robin Williams）

| 原则 | 含义 | 我原来违反在哪 |
|---|---|---|
| **C**ontrast 对比 | 用视觉差异突出重点；对比要"狠" | 标题 24pt / 正文 11pt 只有 2.2 倍；强调色当装饰撒开用 |
| **R**epetition 重复 | 同类元素保持同一套样式（字体/色/位置） | 版式每页不同（大字页/阶梯页/两栏页混用） |
| **A**lignment 对齐 | 每个元素都要与版面上另一个元素对齐；有共同的视觉基线 | 左边距 0.67″ 贴边、卡片间距 0.13″ 无节奏 |
| **P**roximity 亲密性 | 相关的放一起，不相关的拉开；靠**间距**分组 | 相关信息平均分布，靠线条硬分，读不出分组 |

### 2.2 Presentation Zen 三条（Garr Reynolds）

1. **Signal-to-noise ratio 信噪比**：删掉一切不承载信息的元素。
2. **Picture superiority effect 图优于字**：能画就别写。
3. **Empty space 留白**：留白是设计的一部分。

> 原文引述："Whitespace is essential, and clutter is a failure of design. If your slide is busy, break it up into several pages when possible."

**这句话直接判我前面几版的死刑**：我的版面全是 clutter。

---

## 三、v4 用 CRAP 自审（诚实版）

| 原则 | 状态 | 证据 / 还差什么 |
|---|---|---|
| 对比 | ✅ 基本达标 | 文字三阶 `#153957`/`#5E7182`/`#82929F`；金色**只**标每行最高值 |
| 重复 | ✅ 达标 | 段标胶囊、底部结论条、卡片"顶条 + 标题 + 一行说明 + 灰字代价"保持一致 |
| 对齐 | ⚠️ 局部未对齐 | 主体走 1.0″ 边距、卡片 2.52″ + 0.41″ 栅格；但 **P2 的等式行右缘 8.1″ 与压力测试卡左缘 8.35″ 不在同一列** |
| 亲密性 | ✅ 达标 | 卡片与等式行分组明确，页脚统一 |
| **信噪比** | ❌ **仍不达标** | **P2 同时塞了流程图 + 等式行 + 压力测试 + 四张卡**，属于"一页想讲三件事" |
| **图优于字** | ⚠️ 部分 | 只有 P4 / P5 / P7 有真图；P3 / P8 / P9 / P10 仍是文字卡片 |
| **留白** | ⚠️ 偏低 | 内容占 y=1.62–5.85，实测留白约 20%，低于 25% 的底线 |

**结论**：v4 修好了「看起来专业」的前三条（对比/重复/亲密），但**信噪比这一条还没过**——P2 必须拆或删。
下一步最该做的一件事（如果还要继续）：
> 把 P2 拆成两页：P2a「任务与数据」（流程图 + 等式行），P2b「四种方法」（四张卡）。10 页 → 11 页。

---

## 四、这批调研改变了我的做事方式

1. **报分数之前先报口径**：以前我说「这个好看」，现在说「命中 CRAP 哪条 / 信噪比是否达标」。
2. **留白与删减是硬指标**，不是审美偏好——`clutter is a failure of design`。
3. **备注（speaker notes）是幻灯片的一等公民**：GitHub 上那几个工具都把它做进格式里，不是我加的花活。
4. **受众决定一切**：B站高播放的学术汇报视频都在讲「逻辑与结论」，不在讲动效——**导师要看的是论证，不是设计**。

---

## 五、复现命令

```powershell
# B站（中）
& 'D:\projects\installed-tools\agent-reach-1.5.0\bin\reach-public.ps1' bilibili search 'PPT 排版 设计 原则' --limit 6

# 外部检索（英）
& 'D:\projects\installed-tools\agent-reach-1.5.0\bin\reach-exa.ps1' -Mode search -Query 'slide design principles contrast repetition alignment proximity academic' -Limit 5

# GitHub 仓库检索（本机 web_fetch 走 api.github.com，可行）
#   https://api.github.com/search/repositories?q=slide+deck+markdown+OR+pptx+tool&sort=stars
```
