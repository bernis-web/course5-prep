# 断点续接 · 2026-10-26/27

## 已完成

| 项 | 结果 |
|---|---|
| SAMap 批次指标任务 | **W202610260103163**（runsamap）完成，44m27s，¥0.02 |
| 产物归档 | `results/phase-20261026/samap-batch/`（嵌入 4,606×150、obs、metrics、manifest） |
| 三项批次指标 | silhouette **0.0431** / iLISI **1.0061** / kBET **0.0011** |
| 复算脚本 | `scripts/compute_batch_metrics.py`（已在 scVI 上验证：0.1810/1.1202/0.0039） |
| 报告 | `batch-mixing…md` 新增 §8.8（真正修法）、§8.9（脚本验证）、§8.10（三方法并表） |
| 选型指南 | `deliverables/场景化选型指南-v6-20261027.md`（新增场景 9 批次混合） |
| 第 02 次汇报讲解稿 | `deliverables/课题5第02次汇报-逐页讲解稿-20261027.docx`（12 页） |
| 第 02 次汇报备注版 PPT | `results/stage-reports-20261019/…-备注版.pptx`（9 页，逐页口播） |

## 三方法批次指标（最终）

| 指标 | oPCA(50d) | scVI(10d) | SAMap(150d) |
|---|---|---|---|
| silhouette | 0.0937 | **0.1810** | 0.0431 |
| iLISI (满值 3) | 1.0124 | **1.1202** | 1.0061 |
| kBET 接受率 | 0.0004 | **0.0039** | 0.0011 |

## 仍未做（2026-10-27 已全部查清，均为「有明确边界的缺口」）

1. **SATURN 批次指标：已核实为不可补，不是没做。**
   - Final AnnData（`obsm/macrogenes`，4,606×1,000，SHA `20cf807f…`）已被平台清理，本地无留存；
   - 重跑所需的 ESM2 `.pt` 也不存在（`/Files` 全量 `find *.pt` 零命中），只剩 `proteomes .fa` 与源码；
   - 最小路径 = ESM2 推理 + SATURN 重训，且重训产出的是**新的**表示，与 v99 macro-F1 不是同一次训练，
     并表会制造假对照。详见 batch-mixing 报告 §8.11。
2. **容器：脚本已端到端跑通，只剩 `docker build` 未执行（2026-10-28 更新）**
   - **修掉一个真实缺陷**：entrypoint 只导出 `OPCA_ORTH_DIR`，而脚本从不读它，
     实际读 `OPCA_ORTH_MGI/HF/MF`（默认 `/Files/wheelhouse/…`）。容器内没有 `/Files`，
     前置检查会过、脚本一 open 就 `FileNotFoundError`。已在 entrypoint 补齐三个变量。
   - **端到端验证通过**：按容器变量契约在本地跑完整评估，耗时 28.2s，
     **6 方向 × 3 层 = 18 格全部与冻结值逐位一致**（`frozen_comparison.json`，all_match=true），
     `manifest.json` 的 `output_sha256` **39/39 与磁盘哈希一致**。
   - 归档：`results/phase-20261028/container-contract-verify/`
   - **平台镜像构建通道已证实可用**（旧「通道失败」结论作废）：`g5-canary-pinned` 于
     2026-09-21 20:43 基于 SATURN--22 构建成功。
   - **手动步骤已写好但未由我验证**：`docs/execution/20261028-platform-image-manual-steps.md`。
     平台「镜像管理」页当前渲染失败（内容 iframe 恒 `display:none`、innerText 为空，
     等 30s / 刷新 / 换标签页均无效），需用户手动操作并回报结果。
   - **版本容差已实证**（新）：本地 scipy 1.12.0 / pandas 2.3.3 / anndata 0.10.9
     与锁版本（1.10.1 / 1.5.3 / 0.10.8）不同，但 **6/6 冻结值完全复现**。
     说明 oPCA 数值对这三个包版本不敏感，锁版本是为可复现性而非数值正确性。
     自检脚本 `scripts/image_selfcheck.py`，归档 `results/phase-20261028/image-selfcheck-local/`。
   - 仍缺：`docker build`。本机 Docker Desktop 29.8.2 已装但 WSL 无发行版，daemon 起不来；
     补法 `wsl --install -d Ubuntu`（需重启）或在有 Docker 的机器/CI 跑一次。
     注意平台镜像构建 ≠ docker build，两者不能互相替代。
3. **时间/内存受控 benchmark**：共享队列单次时长不可靠，非本项目能控。

## 关键更正（不要再走错）

`samap_emb` 流程只声明 script+pylibs 两个输入，三份 h5ad 从未 stage 进 cwd，
即使 `cp` 成功也会在读数据时失败。正确做法是用 `runsamap`（5 个输入）。
`container/samap_emb.wdl` 与 `samap_emb_v2.wdl` 均已标注 SUPERSEDED，仅留作审计。

## 约束

- 不重投失败任务、不加资源、不充值；失败即停并记录。
- 不覆盖旧文件；新结果写新目录（v6 另存）。
- 全部 transductive / in-sample，不写成 held-out。
