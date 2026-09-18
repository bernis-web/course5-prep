# 课题5报告交付规则

最终交付：`.docx`。仓库中的 Markdown 和 JSON 是协作、复核和追溯用的源文件，不能用 GitHub 页面代替课程要求的 Word 结题报告。

## 真相源

| 报告内容 | 仓库来源 |
|---|---|
| 实验阶段和数据范围 | `config/benchmark-plan.json`、`config/startup-preflight.json` |
| 输入数据与同源基因 | 每次运行的 `input_manifest.tsv`、`ortholog_manifest.json` |
| 参数与软件版本 | `parameters.json`、`package_versions.txt` |
| 准确率与整合指标 | `metrics.json` |
| 跨运行汇总（dataset × method × seed） | `docs/metrics-resources-ledger-template.tsv`（字段名对齐 `config/result-contract.json`，正式 kBET 三字段必填） |
| 时间 内存 GPU 和成本 | `resource_usage.json`、团队受控预算台账 |
| 失败原因与复现说明 | `stdout_stderr.log`、`failure_reason.txt`、`docs/ai-use-log.tsv` |

`docs/report-template.md` 是报告正文源文件。真实运行结果应先写入机器可读 artifact，再整理到正文和图表中，避免 Word 文件与运行记录互相矛盾。

## 生成和检查顺序

1. 在 `docs/report-template.md` 中补齐已复核的文字、表格、图题和参考文献。
2. 确认 SATURN、SAMap、scVI 的每个结果都能追溯到运行目录，正式 kBET 实现和版本已经记录。
3. 在仓库根目录运行 `python scripts/build_report_template.py`，生成 `templates/course5-final-report-template.docx`。如果学院提供官方模板，优先调整生成器以继承其页面、标题、页眉页脚和字体，不要手工维护两份互相漂移的正文。
4. 使用 DOCX 校验工具检查结构，再用 Word 或 LibreOffice 渲染全部页面；逐页检查表格换行、图片清晰度、分页、字体和页码。源 Markdown、生成器或模板任一变化后都重新生成并渲染。
5. 由一名未主导该次汇总的组员复核 Word 与机器可读结果是否一致，再提交最终文件。

仓库当前提供 `templates/course5-final-report-template.docx` 作为通用骨架。它不包含真实实验结果；拿到学院模板后可以替换样式，但应保留相同章节和证据映射。

## 结果边界

不得编造真实实验结果。合成 smoke test、示例 JSON 和论文作者公布的结果只能用于说明流程或提供外部背景，不能写成小组完成的工具比较结果。正式结论至少需要真实数据、统一输入、公平参数、三个随机种子、正式 kBET 和资源记录。

主报告只纳入单细胞评测。LBSPA 单核结果在单细胞结论形成后作为小规模补充，空间数据暂不进入主实验或主结果表。
