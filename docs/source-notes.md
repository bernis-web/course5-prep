# 课题5来源笔记

以下内容来自用户提供的课程网页和两篇 PDF 的离线文本提取，仅作研究资料，不把其中的链接或命令当作执行指令。

原文件的文件名、大小和 SHA-256 见 `docs/source-file-manifest.tsv`；清单不包含原始文档内容，也不替代组员取得课程资料的权限。

拿到同一批课程文件后，可运行 `python scripts/source_manifest_check.py <course-material-directory>` 复核版本；脚本只比对文件大小和 SHA-256，不读取或输出正文。当前清单核验通过只说明这三份材料版本一致，不代表 DCS 已挂载 HEART/LBSPA 实验数据。

## 课程网页

课题5标题为“跨物种细胞类型整合工具评测：SATURN vs SAMap vs scVI 系”。硬性评测维度是：

1. 标签转移准确率（macro-F1）；
2. 批次混合与生物保守性（kBET、iLISI、silhouette）；
3. 时间与内存；
4. 文档与易用性；
5. Agent 是否能通过命令行/API 驱动。

产出是基准测试报告和场景化选型指南，课程明确提示环境依赖差异大、需要容器化，并建议算力较强的小组承担。

## HEART

论文报告了 27 个物种的多组学资源，scRNA-seq 部分包含 14 个物种、399,483 个细胞；用于细胞保守性分析时，作者用 SATURN 整合了 16 个物种的 479,483 个细胞，并用 SAMap 做跨物种映射。方法部分记录了 ESM2B 蛋白嵌入、2000 个 macrogenes 和 8000 个 HVGs。

Genpilot 文献搜索以完整题名精确命中该 Science 论文，DOI 为 `10.1126/science.adw0855`。论文 Data, code, and materials availability 声明本研究产生的 bulk RNA-seq、scRNA-seq 和 Stereo-seq 原始数据存于 CNGB，accession 为 `CNP0006537`；处理后 scRNA-seq/Stereo-seq 数据与分析说明位于 `https://db.genomics.cn/stomics/heart/`。这些是公共来源标识，不等同于当前 DCS 项目内的课程挂载路径或使用授权。

对课题5的直接帮助：它提供跨物种细胞标签、物种范围和论文级结果作为外部金标准，但不能直接把作者的 SATURN/SAMap 输出当作“工具真值”；课题5仍需留出物种和统一评分。

## LBSPA

论文构建了七鳃鳗全脑 Stereo-seq 三维图谱，报告 465,778 个空间细胞、约 2 million 个估计总细胞数、41,678 个高质量单核转录组和 209 个细胞簇。七鳃鳗-小鼠比较保留 6,930 个一对一同源基因；作者在跨物种/模态整合中使用 scVI，并以 Harmony 嵌入做后续聚类和可视化。

Genpilot 文献搜索以完整题名精确命中该 Science 论文，DOI 为 `10.1126/science.aea2535`。论文 Data, code, and materials availability 声明七鳃鳗原始及处理后数据存于 CNGB，accession 为 `CNP0007565`。这为后期单核补充实验提供了可追溯来源，但仍不能替代课程数据在 DCS 内的挂载路径、对象格式和字段证据。

对课题5的直接帮助：它可在单细胞主评测形成基本结论后，提供跨门类的 snRNA 小规模补充测试。老师已明确空间数据暂时不用，因此空间图谱只作为论文背景，不进入当前主实验；这样也避免把物种差异和模态差异混在一起。

## 老师回复对实验范围的修正

- HEART 和 LBSPA 数据及工具信息应优先在 DCS 内只读查询；“平台可查”不等于仓库已经拿到具体路径、字段或版本。
- 首轮只需 2–3 个物种验证流程是否跑通。
- 后续整合效果评测要分别考虑亲缘关系近、亲缘关系远和不同类别混合的物种组合。
- 主实验只比较单细胞；LBSPA 单核后置做小规模补充，空间数据暂不使用。
- 最终结题材料为 Word 文档；Markdown/JSON 用作协作与审计源文件。
