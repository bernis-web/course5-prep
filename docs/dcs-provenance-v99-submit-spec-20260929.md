# g5-provenance-v99-readout 提交规格（2026-09-29）

## 任务定义
- 名称：`g5-provenance-v99-readout`
- 镜像：`SATURN--22`（st-harbor.dcs.cloud/public-library/zhongliyuan_57362367597d49499e5bc388096a17f1_public:latest）
- 资源：`1c 4g`（resource_id=259），无 GPU
- 性质：只读证据恢复 + 统一重评分；**禁止训练**

## 输入（白名单只读）
1. `/data/work/saturn_out_real3_h/saturn_results/test256_data_….h5ad`（SHA-256 门：20cf807f…）
2. `/data/work/prep_real_v60.py`、`/data/work/eval_v72.py`、v95/v96 命令与脚本候选（存在则哈希，缺失记 missing）
3. `/data/work/saturn-src/`（整树逐文件 SHA-256）
4. 冻结映射表 v1（base64 内嵌进容器，写出至脚本同目录）

## 脚本自记录（启动时写 environment.txt / command.txt）
UTC/北京时间、完整执行命令、脚本 SHA-256、Python 版本、pip freeze、协议标签 `transductive_formal_reassessment`

## 评分（统一协议）
KNN15 倒距离加权 cosine、seed=0、200 次置换；coarse/fine 对 ref 与 qry 双向排除 `mapping_status != active`；exact 保留全部有效真值；六方向×三层。

## 输出（/data/work/course5_v99/）
manifest.json · metrics.json · predictions/（18 份逐细胞 JSON）· confusion/（18 份）· roles/ · sha256.tsv · environment.txt · command.txt · course5_v99_readout.ipynb（备用载体）

## stdout 纪律
仅打印 <20KB compact summary；全量产物只落盘。

## 提交记录
- 提交时间：2026-09-29
- batch：`2104897172032016386`（直连 /offline/save）
- shell：b64 脚本 + v99_mapping_embedded.json 写入 → `python3 dcs_provenance_v99.py`
