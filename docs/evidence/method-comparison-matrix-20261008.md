# 三方法公平比较矩阵（2026-10-08）

> 目的：解释为什么不能把三列按一个总分排冠军。
> 每个方法回答不同的科学问题；协议差异是设计选择，不是方法缺陷。

## 一、表示层与同源信息

| 维度 | ortholog-PCA | SATURN | SAMap |
|---|---|---|---|
| 同源信息载体 | 1:1 直系同源基因表（硬过滤） | ESM2 蛋白语言模型（软嵌入） | 1:1 直系同源基因近邻图 |
| 跨物种桥梁 | 基因名匹配后取交集 | 蛋白序列嵌入空间对齐 | 基因-基因拓扑对齐 |
| 降维 | 联合 PCA-50 | macrogene 聚合（1000） | SAM 潜空间（npcs=100） |
| 整合范式 | 零整合（零训练零校正） | 深度生成联合训练 | 图对齐迭代 |

## 二、标签使用与训练协议

| 维度 | ortholog-PCA | SATURN | SAMap |
|---|---|---|---|
| 训练阶段标签 | 不使用（label-free） | labels（细胞类型 id）经 cross_species miner 参与；ref_labels 仅输出/评估真值（运行时源码版本待核实） | keys=cell_type 参与联合图（运行脚本内容待回捞） |
| 评估阶段标签 | KNN 监督 | KNN 监督 | KNN 监督 |
| label-aware/free | **label-free** | label-aware（labels 通道） | label-aware（keys 通道） |
| 训练参数 | 无训练 | epochs=50, macrogenes=1000 | NUMITERS=3 |
| 算力成本 | CPU 秒级（17.9s） | GPU 4090（离线通道历史运行） | CPU 1c4g WDL（约 16 分钟） |

## 三、标签空间与分母

| 维度 | ortholog-PCA | SATURN v97g | SATURN v99 | SAMap v98 |
|---|---|---|---|---|
| coarse 标签空间 | 映射词汇（9 粗类） | mapped-space（映射后粗类） | 原始标签+status 过滤 | 原始标签+status 过滤 |
| 排除规则 | status≠active 双向 | 规则合规列（74 细胞双向排除） | coarse/fine 排除；exact 不排除 | status≠active 双向 |
| n_q（h→m）· coarse | 1,505 | ≈1,505（日志级限定） | 1,505 | 1,505 |
| n_q（h→m）· exact | 1,535 | 1,535 | 1,535 | 1,535 |
| coverage_q · coarse | 0.9805 | 0.9805（日志级限定） | 0.9805 | 0.9805 |
| coverage_q · exact | 1.0 | 1.0 | 1.0 | 1.0 |

## 四、回答的问题与不能回答的问题

| 方法 | 能回答 | 不能回答 |
|---|---|---|
| ortholog-PCA | 同源基因投影本身携带多少跨物种信号？ | 深度模型是否比简单基线更好（需要同协议对比） |
| SATURN | 蛋白语言模型嵌入在同数据上比 scVI/零基线好多少？ | label-free 场景下的表现（训练标签经 labels 通道参与 miner；运行时版本待核实） |
| SAMap | 转录组对齐在 label-aware 协议下是否产生可分联合流形？ | label-free 场景的表现（keys 参与了联合图） |

## 五、观察到的方向性差异（transductive 口径）

| 发现 | 支撑数字 | 证据等级 |
|---|---|---|
| 哺乳动物对：零整合基线 ≥ SATURN ≥ SAMap | 0.8618 ≥ 0.6179 ≥ 0.1050 | candidate-final（oPCA+SAMap）+ confirmed（SATURN） |
| 斑马鱼相关四方向：三方法均弱或无信号（唯一例外见下行） | 逐方向（h→z / m→z / z→h / z→m）：oPCA 0.1961 / 0.2755 / 0.1813 / 0.5761；SATURN v97g 0.1835 / 0.3009 / 0.2474 / 0.4651；SAMap 0.0341 / 0 / 0 / 0 | 同上 |
| 唯一例外：斑马鱼→鼠 ortholog-PCA 高于多数类 | 0.5761 > 0.4817（映射空间多数类） | candidate-final |
| ESM2 蛋白信号为真 | 消融 67.4→20.4（v72-era 协议内配对；v97g 协议下未重跑） | confirmed（方向性） |
| SAMap 在 label-aware 下仍无信号 | 六方向 coarse 0.00–0.105 | candidate-final（探索性复现） |

## 六、不可比项清单

1. 标签空间两套：ortholog-PCA 与 SATURN v97g coarse/fine = 映射标签空间；SATURN v99 与 SAMap = 原始标签空间（按各自规则过滤）——跨空间数值**不可直接排名**
2. SAMap label-aware vs ortholog-PCA label-free——不是同一问题的比较
3. v97g（mapped-space）vs v99（exact-space）双口径——同方法内部两套数字也不可合并
4. 三方法的置换检验零分布定义不同（v99/v98 用预测向量洗牌；ortholog-PCA 同）
5. 算力成本差异悬殊（17 秒 CPU vs 4090 GPU vs 16 分钟 CPU 1c4g）——效率比较需另行设计
