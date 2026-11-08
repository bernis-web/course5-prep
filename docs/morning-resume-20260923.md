# 晨间复工清单（2026-09-23 凌晨阻塞记录 + 一键复工）

## 凌晨阻塞点

平台登录态过期（JWT 到期+localStorage 清空，跳转 #/login）——上传/提交任务/读结果全部阻塞。**已确认无残留凭据可用**。需要：用户在内置浏览器重新登录 www.dcs.cloud（扫码/账号均可），登录后一切即刻恢复。

## 已就绪（零重复劳动）

- **真实嵌入已解压待传**：wheelhouse/protein_embeddings_export/ESM2/ 下 human_embedding.torch（410MB，ZIP_OK）、mouse_embedding.torch（463MB，ZIP_OK）已切分为 human-part-00..04（5片）+ mouse-part-00..05（6片），各 90MB
- **三物种嵌入全部就绪**：嵌入包续传完成（3,738,581,381 字节），human 410MB（ZIP_OK）切 5 片、mouse 463MB（ZIP_OK）切 6 片、**zebrafish 537MB 已补全（ZIP_OK）需切 6 片**（`split -b 90M -d zebrafish_embedding.torch zebra-part-`，尚未切）——共 17 片
- **上传目标**：/Files/wheelhouse/（menuId 01a0c4a5d4f37c8d91edf83195756a90），.bin 后缀直传（二进制文件名含 .whl/.tar.gz 才触发检测，.bin/.txt 均可）

## 复工步骤（登录后 ~30 分钟内完成）

1. 切分斑马鱼（`split -b 90M -d zebrafish_embedding.torch zebra-part-`，wheelhouse 目录）→ 上传全部 17 个分片（human-part-*.bin × 5、mouse-part-*.bin × 6、zebra-part-*.bin × 6）
2. 提交离线任务（1c4g 即可）：合并分片 `cat human-part-* > human_embedding.torch`（mouse/zebra 同法），校验 ZIP_OK
3. 构造真实嵌入输入（参照 v54 配方，见 saturn-smoke-evidence-20260922.md 最终配方节）：
   - 用真实 .pt（torch.load 后是 {gene_symbol: tensor}）+ 真实 h5ad（/Files/RawData/，var_names 对齐到真实基因 symbol，抽样 5000 细胞）
   - in_data.csv 三列 species/path/embedding_path
4. SATURN 训练（CUDA 补丁 + hv_span 1.0，配方同 v52-v54）→ 出三物种数字
5. commit + push（代理开着的话）

## 今日其他待办

- codex 规划商量（代理开着时）：SAMap 正式跑数路线（直系同源文件来源）+ SATURN 正式训练资源规划
- 群通知待发：三物种 scVI 数字 + SAMap 1.0.16 实测（底稿 docs/teammate-notice-20260921.md 可补数字）
