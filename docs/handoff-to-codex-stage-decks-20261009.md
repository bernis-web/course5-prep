# 交接给 Codex：阶段汇报 3–10 成品包与汇报 2 校模板版（只读审计）

> 交给：Codex 做只读审计。执行者：ZCode/Flash。Claude 已做/待做逐阶段审阅。
> 日期：2026-10-09。工作目录：`D:\projects\course5-prep`
> 本轮没有新计算、没有新任务提交；全部为"已有证据 → 汇报材料"的整理与校验。

## 0. 先读，再审计

1. `docs/superpowers/plans/2026-10-08-course5-report-cycle-and-ppt-audit.md`（10 阶段划分与每阶段验收点）
2. `docs/final-evidence-matrix-20261005.md`（全部对外数字的唯一出处）
3. `results/stage-reports-20261009/index.md`（本轮产物索引：阶段表 + 文件清单 + 校验记录）
4. `docs/phase6-closure-20261005.md`（SAMap WDL 关账）
5. `docs/mapping-v1-ai-review-opinion-20261005.md`（映射表 AI 复核意见书）
6. `results/report-02-metric-lineage-20261008/render-report.md`（汇报 2 校模板版生成与验证记录）

开始前记录 `git status --short`。

## 1. 硬边界（审计时必须检查执行者是否违反）

- 不把 AI 复核写成导师签认；mapping v1 仍为 `needs-reviewer`。
- 全部结果标注 `transductive / in-sample`；不得出现 held-out / inductive 表述（汇报 9 除外，且必须写明"设计，未运行"）。
- 不把 SATURN 0.6179 / 0.4749 / 0.4844 合并；三个数字必须分列并标口径。
- 不按单一总分排三方法冠军；跨方法同表仅作方向性参考。
- 旧草表数字（80.9/38.3/40.5/22.4/11.9/79.5）只允许出现在"作废对照"语境（汇报 4、7 各有专页）。
- 数字必须从冻结 metrics/证据矩阵逐格回溯；不得凭记忆手改。
- 旧 PPT/报告不得被覆盖；本轮新增均在 `results/stage-reports-20261009/` 与 `results/report-02-metric-lineage-20261008/` 内。

## 2. 本轮产物（待审计清单）

### 2.1 汇报 2 校模板版（先行交付）

- `results/report-02-metric-lineage-20261008/课题5第二阶段汇报_数字来源链_校模板版.pptx`（8 页）
- 同目录 PDF 预览；旧版 `课题5第二阶段汇报_数字来源链.pptx` 保留未动
- 生成脚本：`build_report02_template.js`；后处理：`postprocess_template_bars.py`
- 审阅闭环：`docs/reports/claude-review-02-report02-20261009.md`（复审 revise → 补齐第 7 页 seed 提示 → 最终确认 pass）

### 2.2 阶段汇报 3–10（8 册，共 55 页）

目录：`results/stage-reports-20261009/`

| 文件 | 页数 | 内容稿（docs/reports/） |
|---|---|---|
| 课题5第03次汇报_三方法公平比较边界.pptx | 7 | report-03-method-comparison-20261008.md |
| 课题5第04次汇报_ortholog-PCA基线闭环.pptx | 7 | report-04-evidence-closure-20261008.md |
| 课题5第05次汇报_SATURN信号与协议效应.pptx | 7 | report-05-saturn-signal-20261009.md |
| 课题5第06次汇报_SAMap复现与负结果.pptx | 7 | report-06-samap-negative-result-20261009.md |
| 课题5第07次汇报_三方法总矩阵与老师问题.pptx | 7 | report-07-three-method-matrix-20261009.md |
| 课题5第08次汇报_映射签认与证据责任.pptx | 7 | report-08-mapping-signoff-20261009.md |
| 课题5第09次汇报_最小inductive方案.pptx | 6 | report-09-inductive-design-20261008.md |
| 课题5第10次汇报_收口与下一阶段.pptx | 7 | report-10-closure-and-next-phase-20261008.md |

生成方式：`build_reportNN.js`（node + pptxgenjs，共用 `lib/report-template.js`）→ `lib/postprocess_bars.py`（顶栏斜切+渐变注入）。渲染件：`render/rXX-pYY.png`（55 张）。

## 3. 审计项（逐项给"通过 / 需修改 / 阻塞"，引用文件与行号）

### A. 数字回溯（抽查不少于 8 格）

对每格：从 PPT 文本抽取数字 → 与冻结来源比对 → 记录一致/不一致。

来源对照：
- ortholog-PCA 六方向 × 三层：`results/pilot-v1/ortholog-pca-v98/metrics.json`（SHA b2b3ac6b…c725）
- SATURN v99：`results/pilot-v1/saturn-v99/raw/recovered-20261001/metrics.json`（SHA d1081cfd…dc261）
- SATURN v97g：`docs/transductive-formal-v74-evidence-20260928.md` L58-69（日志级，无逐细胞文件）
- SAMap v98 WDL：`results/pilot-v1/samap-v98/wdl-run/extracted/metrics.json`（SHA 3c719399…954f）
- 排除规则/映射表：`config/heart-celltype-map-v1.tsv`（SHA be985735…3165，38 行）
- 汇总：`docs/final-evidence-matrix-20261005.md` §二/§三

建议命令（python-pptx 抽取全部文本后逐项检索）：

```python
from pptx import Presentation
prs = Presentation("results/stage-reports-20261009/课题5第04次汇报_ortholog-PCA基线闭环.pptx")
text = []
for s in prs.slides:
    for sh in s.shapes:
        if sh.has_text_frame: text.append(sh.text_frame.text)
        if sh.has_table:
            for r in sh.table.rows: text.append(" | ".join(c.text for c in r.cells))
full = "\n".join(text)
for token in ["0.8618","0.7369","0.1961","0.2755","0.1813","0.5761","1,505","1,528","1,499"]:
    print(token, token in full)
```

### B. 状态分类正确性

- 各册中 evidence 等级标注是否与 `docs/evidence/status-matrix-20261008.md` 一致：
  ortholog-PCA = candidate-final；SATURN v97g = confirmed（日志级）；SATURN v99 = provenance confirmed（报告数字 candidate）；SAMap WDL = candidate-final（探索性复现）；mapping v1 = needs-reviewer。
- 检查是否有把日志级写成文件级、把候选写成 confirmed 的表述。

### C. 教师意见闭环（汇报 7 专页）

- 三个问题（数字过时 / SAMap 表述过时 / 含金量与防误读）是否逐一回应。
- 旧草表 80.9… 是否仅出现在"旧版（作废/过时）"列。
- "v98 尚需修正复跑"是否已不存在于任何新 PPT（旧文件除外）。

### D. 过度结论检查（重点）

- 是否出现"谁更好/排名/冠军/SOTA/超越"类表述（允许"方向性参考"措辞）。
- 是否出现 held-out / inductive 的既成事实表述（汇报 9 必须全文为设计语气，且注明未运行）。
- SAMap 负结果是否被推广为"工具无效"（汇报 6 应明确三层读法）。
- 鱼方向数字是否附单 seed 提示（汇报 4/5/7）。

### E. 模板合规（对第一阶段的校模板）

对照源：`E:\xwechat_files\wxid_2gvkgptwgs8b22_6b72\msg\file\2026-09\课题5第一阶段成果汇报_内容充实版.pptx`（或解包副本 `tmp/ppt-inspect/original_extract/`）。

- 顶栏：蓝条 (0, 0.723, 9.556, 0.191) 为 snip2DiagRect + 渐变 002060→0076D2；金条 (10.19, 0.723, 3.144, 0.191, FFC000)。
- logo (10.63, 0.09, 1.92×0.59)；标题色 12365A；页脚 8.5pt 60758F 左标签+右页码；封面藏青带 (0, 2.14, 13.333, 1.99, 002060)。
- 建议命令（形状校验）：

```python
import zipfile, re
z = zipfile.ZipFile("results/stage-reports-20261009/课题5第03次汇报_三方法公平比较边界.pptx")
for n in z.namelist():
    if re.match(r"ppt/slides/slide\d+\.xml$", n):
        x = z.read(n).decode("utf-8")
        if 'name="bar-blue"' in x:
            i = x.find('name="bar-blue"'); blk = x[x.rfind("<p:sp>",0,i):x.find("</p:sp>",i)+7]
            print(n, "snip:", "snip2DiagRect" in blk, "grad:", "gradFill" in blk)
```

### F. 版式（碰撞）复核

- 执行者记录：程序化碰撞检测（卡片上边缘切字/压行）修正 12 处后 0 处；渲染件在 `render/`。
- Codex 可复算：对任一册转 PDF（`soffice --headless --convert-to pdf`）后用 pymupdf 检查"非白色填充矩形上边缘 7pt 内是否有文字底线"（执行者所用规则），或直接抽查 `render/` 中任意 10 张。

### G. 文件完整性

- 8 册 PPT 均存在且可打开（python-pptx 能读出页数）；55 张渲染件齐全。
- `index.md` 的阶段表与实际文件一一对应。
- 内容稿 3–10 全部存在（5–8 为本轮新写）。
- 旧文件未被覆盖：`results/report-02-metric-lineage-20261008/课题5第二阶段汇报_数字来源链.pptx`、`results/phase1-revised*/` 时间戳未变。

### H. 未提交声明

- 本轮未 commit、未 push、未清理。检查 `git status --short` 中本目录文件的出现方式（应为本轮新增/修改，不应有删除或回退痕迹）。

## 4. 输出要求

- 逐项（A–H）给 `通过 / 需修改 / 阻塞`，每条引用文件与行号（或页码+文本）。
- 结尾附一行 JSON：

```json
{"stage_decks_audit": "pass|revise|block", "must_fix": ["..."], "checked_items": 8}
```

- 只读：不修改任何文件、不提交、不推送、不清理、不覆盖。
