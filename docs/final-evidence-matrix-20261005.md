# 课题5 最终证据矩阵（三方法对比，2026-10-05 数值冻结版）

> **本文件是全部对外数字的唯一出处。** 每个数字标注来源文件+SHA；引用禁止手工改动。
> 口径：全部为 transductive/in-sample 重评估（非 held-out/inductive）；coarse 层为主结论层。

## 一、方法与输入（三方法同一数据）

- 数据：心脏样本三物种 pilot 子集（人 1528 / 鼠 1535 / 鱼 1543 细胞，金标准标签列 celltype）
- 冻结映射表 v1：config/heart-celltype-map-v1.tsv（SHA be985735…583165，38 行，双层 coarse9/fine17）
- 排除规则：mouse/fish 增殖细胞与 fish mt（status≠active，共 mouse 30 / zf 44 / human 0）不入 mapped 分母

## 二、主表：coarse 层六方向（主结论层）

| direction | ortholog-PCA¹ | SATURN v97g² | SAMap v98³ | v99 统一评分器⁴ | 多数类⁴ |
|---|---|---|---|---|---|
| human→mouse | **0.8618** | 0.6179 | 0.1050 | 0.4844 | 0.4618 |
| mouse→human | **0.7369** | 0.2539 | 0.0196 | 0.1924 | 0.2526 |
| human→zebrafish | **0.1961** | 0.1835 | 0.0341 | 0.1127 | 0.3976 |
| mouse→zebrafish | 0.2755 | **0.3009** | 0.0000 | 0.1948 | 0.3976 |
| zebrafish→human | 0.1813 | **0.2474** | 0.0000 | 0.1872 | 0.2526 |
| zebrafish→mouse | **0.5761** | 0.4651 | 0.0000 | 0.3375 | 0.4618 |

（粗体 = 该方向最高；跨列标签空间/协议不同，见 §四口径警示——排名仅作方向性参考）

### exact 层（参考）

| direction | ortholog-PCA | SAMap v98 | v99 |
|---|---|---|---|
| human→mouse | — | 0.1029 | 0.4749 |
| mouse→human | — | 0.0196 | 0.1760 |
| human→zebrafish | — | 0.0331 | 0.1095 |
| mouse→zebrafish | — | 0.0000 | 0.1860 |
| zebrafish→human | — | 0.0000 | 0.1872 |
| zebrafish→mouse | — | 0.0000 | 0.3303 |

（ortholog-PCA 的 per-direction exact 见其 metrics.json exact 块：0.7824/0.4084/0.1698/0.1659/0.1453/0.4769）

## 三、来源与证据等级

| 列 | 来源文件 | SHA/锚点 | 证据等级 |
|---|---|---|---|
| ortholog-PCA | results/pilot-v1/ortholog-pca-v98/metrics.json | manifest.script_sha256 + 输出 39 文件 SHA | candidate-final（Claude Gate 2/3/4 pass） |
| SATURN v97g | EVAL3G 日志（v97g 六方向） | docs/transductive-formal-v74-evidence-20260928.md | confirmed |
| SAMap v98 WDL | results/pilot-v1/samap-v98/wdl-run/extracted/metrics.json | 任务 W202610050003104 + tar SHA | candidate-final（Claude 复核通过） |
| v99 统一评分器 | results/pilot-v1/saturn-v99/raw/recovered-20261001/metrics.json | **SHA d1081cfd…dc261** | provenance confirmed（file-level，Gate 1 pass）；报告数字 candidate |

## 四、口径警示（引用任何数字必须随带）

1. **全部为 transductive/in-sample 重评估**，不得表述为 held-out/inductive 泛化
2. **跨方法标签空间不同**：ortholog-PCA coarse/fine = 映射词汇（9 粗类）；SATURN/SAMap/v99 = 原始标签+status 过滤（无重映射）——跨方法同表仅作方向性参考，不可直接排名
3. **跨方法分母不同**：各列 n_q 随各自排除规则（ortholog-PCA coarse 1505/1496；v99 同；SAMap 1505/1496）；每个 acc 必须并列 n_q
4. **SAMap per_cell included 旗标**用"truth∈参考标签集"定义（1398），与 n_q（1505）口径不同，旗标不参与 acc——脚本 md5 56bb6035 版本口径
5. **v99/v97g 差异**（61.79% vs 48.44% h→m coarse）：标签空间+排除规则+评分器三重差异，双报不合并（v99-score-reconciliation-20261001.md）
6. **seed**：全部单 seed（0）；SATURN 鱼方向 seed 双峰已证实，各方法鱼方向数字均为单种子点估计
7. **shuffle_p** 零分布=预测边际×真值边际对角积 E[null]，非多数类检验；p 值只用于"优于随机预测向量"
8. **SAMap 依赖栈**：pylibs 预建栈复用（非重装）；脚本 md5 56bb6035 版（410 行，非 Phase 5 修复版 0a2063d3）

## 五、辅助证据（confirmed 级）

- **ESM2 消融**：蛋白嵌入打乱后 61.8%→20.4%，蛋白同源信号为真（v80 置换运行）
- **物种内 ceiling**（与跨物种共享潜空间，成对引用）：85.5 / 93.5 / 74.2
- **seed 稳定性**：h→m 67.1±3.8 稳定；鱼方向双峰（11.3/48.8/8.3）
- **pseudobulk 映射验证**：人鼠 8 对全进 top5（5 对 rank-1，内皮 ρ=0.82）

## 六、排除普查

mouse 30（Proliferating cell）/ zebrafish 44（mt 30 + Proliferating 14）/ human 0

## 七、v99 结构性事实

- 三层预测文件仅内嵌 level 字符串不同（PREDPLAN gzip sha 同）；层间差异全在评分期排除
- metrics exact 层 acc == 预测文件自带 acc（六方向全部吻合）
- coarse == fine（v99 标签从不重映射，排除是唯一机制）
