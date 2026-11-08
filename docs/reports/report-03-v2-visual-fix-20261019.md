# 第 03 次汇报 PPT 视觉返工（v2）

- 产物：`results/stage-reports-20261009/课题5第03次汇报_三方法公平比较边界_v2.pptx`（1,327 KB，7 页）
- SHA-256：`3F650EF69FE6E9A257D938AF424DC471F0A9A4FC4C89B7743DD1F8D746014F4A`
- 生成器：`results/stage-reports-20261009/build_report03_v2.js`（v1 `build_report03.js` 的定点改版）
- 基线：`课题5第03次汇报_三方法公平比较边界.pptx`（v1，**未改动**，10-09 19:37 原样）
- 校模板：仍走 `lib/report-template.js`，顶栏斜切/渐变由 `lib/postprocess_bars.py` 注入（patched 6 slides）

> 原则：数字、口径、结论措辞逐字不动。核对方式见 §三：**126 个数字 token 完全一致**。

## 一、缺陷清单

| 级 | 页 | 缺陷 | 规则 | 修法 |
|---|---|---|---|---|
| 致命 | 5 | 表 y=1.82 + 7 行 × `rowH 0.40` = 4.62"，而两张卡片在 4.35" —— PowerPoint 里行高是**下限**，必叠 0.27"（LibreOffice 只按内容排，所以预览看不出来） | B6 | `rowH 0.36`（表底 4.34"）+ 卡片下移 4.62"，留 0.28" |
| 明显 | 7 | 斑马鱼四方向 12 个数字塞在 3 行文本里，「z→m 0.4651」「z→m 0.0000」被折行**把数字劈成两行** | D6/E6 | 改成 4 行（方向）× 3 列（方法）小表，数字永不被折断 |
| 明显 | 2 | 表下到结论条 0.95" 空洞；正文 10.5pt 投到教室偏小 | B5/D2 | 字号 10.5→12、`rowH 0.44→0.50`，表格高度 3.6→4.2" |
| 明显 | 3 | 三张卡高 4.3"，正文只到卡内 60%，卡内空 1.5" | B5 | 卡高 4.3→3.62、起点 1.82→1.98 居中，正文 10.5→11pt |
| 明显 | 4 | 表底（6 行 × 0.40 + 表头 = 4.67"）与卡片 4.5" 之间的余量只剩 0.09" | B6 | `rowH 0.34`（表底 4.31"）+ 卡片 4.62"，余量 0.31" |
| 打磨 | 6 | 卡片底 6.18" 距结论条 0.17"，贴得太近 | B6 | 卡高 1.84→1.72，底 6.06"，余量 0.29" |
| 打磨 | 4/5/6 | 卡片正文 10.5→11pt，与第 2、3 页统一 | D2 | 统一 11pt |

### 试过但已回退的改法（写清楚，避免下一位再踩）

用 `pptxgenjs` 原生 `bullet: {code:'2022'}` + `indentLevel` 做「悬挂缩进」，想让长句折行后回到项目符号缩进位。结果：

- LibreOffice 渲染出 **0.5" 的项目符号→文字空档**，比 v1 的字面 `•` 更难看；
- 续行（`indentLevel:1`）在 `margin:0` 下会顶到左边距，层级反而丢了。

结论：**卡片继续走模板 `box()` + 字面 `•`**。悬挂缩进这件事在 pptxgenjs 里不可控（PowerPoint 与 LibreOffice 对 `marL/indent` 的解释不同），要做只能改用 python-pptx 直接写 `<a:pPr marL= indent=>`。已回退，不留半成品。

## 二、审美决策表（延续 02 v2 那套，未新增颜色）

| 项 | 值 |
|---|---|
| 色板 | 模板蓝+金条（不可改）｜字 `1F2D3D`｜标题 `12365A`｜弱化 `60758F`｜卡片底 `EAF4FB` / `FFF2CC` / `FCE4D6` / `E2EFDA`｜表头 `005BAC` 白字｜小表头 `CFE0EC` |
| 字体 | 微软雅黑；页标题 24pt Bold；卡标题 14.5pt Bold；正文 11pt；表格 10.5–12pt；页脚 8.5pt |
| 网格 | 左右边距 0.7"；结论条固定 y=6.35（h=0.44）；页脚 y=7.06；卡片间隙 0.3" |
| 硬规则 | **任何表格：y + 行数 × rowH ≤ 下一块元素 y − 0.3"**（PowerPoint 行高是下限，这条必须按最坏情况算） |

## 三、验证记录

1. `validate.py --original v1` → `All validations PASSED!`
   - 注：首次跑可能报 `docProps/core.xml` 的 Dublin Core XSD 抓取失败——那是**校验器联网取 XSD**，断网时会误报；v1 单独校验也会报同样的错，重跑即过。
2. 7 页全部渲染（LibreOffice → PDF → 120dpi JPEG）逐页肉眼检查。
3. 文本核对（`dump_text` + 脚本比对）：
   - 数字 token：v1 126 个 / v2 126 个，**多集完全一致**，没有任何新增或丢失；
   - 字符差：v1 独有 `／ ： ⚠`（全角斜杠、表格化后不再重复的方向标签、警示符号），v2 独有 `方 | △`——都是排布符号与表格分隔，**无一处实质文案改动**；
   - 顺带说明：`⚠` 改成 `△`，因为 emoji/符号字形跨平台不一致（PPT 里更常用 △）。
4. 表格底线用 XML 里的 `<a:tr h>` 反算（不信预览），才敢定 `rowH`。

## 四、未修项与已知风险

1. **第 2 页表下仍有 0.9" 留白。** 要把这块填满只能再放大字号（12→13pt），但 SATURN 那一格会折成两行、表格反而顶到结论条；判断为「保持留白」更安全。
2. **第 3 页三张卡内下部仍有约 0.5" 空白**（正文就那么多），卡高已按内容收到 3.62"。
3. **第 7 页左卡（五项不可比）下部空约 0.8"**，与右卡等高是刻意的；单独看会觉得空。
4. 卡片内长句折行后仍回到左边距（不是悬挂缩进）——原因见 §一「已回退的改法」，属 pptxgenjs 的硬限制。
5. 封面与模板元素未动。

## 五、复现

```powershell
$env:NODE_PATH='C:\Users\28417\.dsh\skills\pptx\node_modules'
$py='C:\Users\28417\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe'
cd D:\projects\course5-prep\results\stage-reports-20261009
node build_report03_v2.js
& $py .\lib\postprocess_bars.py .\课题5第03次汇报_三方法公平比较边界_v2.pptx
& $py C:\Users\28417\.dsh\skills\pptx\scripts\office\validate.py .\课题5第03次汇报_三方法公平比较边界_v2.pptx --original .\课题5第03次汇报_三方法公平比较边界.pptx
& $py C:\Users\28417\.dsh\skills\pptx\scripts\office\soffice.py --headless --convert-to pdf .\课题5第03次汇报_三方法公平比较边界_v2.pptx
pdftoppm -jpeg -r 120 "课题5第03次汇报_三方法公平比较边界_v2.pdf" slide
```
