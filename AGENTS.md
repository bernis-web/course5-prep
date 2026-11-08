# AGENTS.md — 接手须知（课题5）

> 任何 agent 进入本仓库，先读这一页，再读它指向的交接文档。

## 第一件事

**读 `docs/execution/20261019-handoff-full.md`。**

这份文档包含：项目背景、当前进度（七次汇报）、全部数字与口径、DCS 平台状态、
关键技术坑、复现命令、硬约束、FAQ。读完即具备独立接续能力，无需回溯历史对话。

## 项目一句话

跨物种单细胞整合方法比较（课程题目：SATURN vs SAMap vs scVI 系），
三物种心脏 scRNA（人 1,528 / 鼠 1,535 / 斑马鱼 1,543 = 4,606 细胞）。

## 当前状态一句话

四方法矩阵完整（oPCA / SATURN / SAMap / scVI），macro-F1 口径已统一，scVI 臂已跑通并核对；
跨门场景（七鳃鳗↔小鼠）数据已定位但未跑。

## 三条最容易踩的坑（详情见交接文档 §7）

1. `pylibs_full.tar.gz` 里的旧 `anndata` 会让 `import scvi` 失败 —— 解压后必须
   `rm -rf ./pylibs_full/anndata*`。
2. 容器里输出目录只能写 `./result`；写 `../result` 会 1 秒内失败。
3. shell 变量必须加引号：`[ -n "$REC" ]`，否则空值时 `cp -r /.` 会拷贝根目录。

## 硬约束（不可协商）

- 不读取/打印/复制 token、cookie、密码、API key；
- 不在本地做模型运算，运算走 DCS；
- 不重投失败任务、不加资源、不充值；
- 不修改 `opca_v2` 流程，新需求新建流程；
- 不覆盖旧 PPT / 旧报告 / 用户已有改动；
- 不删除或回退 `results/pilot-v1`；
- 不把 transductive 写成 held-out / inductive；
- 不按单一总分给方法排冠军；
- 汇报 7–8 分钟，单双周交替（总共 7 次，已做第 1、2 次）。

## 目录速查

| 路径 | 内容 |
|---|---|
| `docs/execution/20261019-handoff-full.md` | **交接主文档** |
| `docs/execution/20261019-report-plan-7.md` | 七次汇报计划 |
| `docs/reports/report-02-metric-lineage-20261019.md` | 第 2 次汇报内容稿 |
| `deliverables/场景化选型指南-v2-20261019.md` | 课程核心交付物 |
| `results/phase-20261019/scvi-cross-species/` | scVI 全部产物 |
| `results/stage-reports-20261019/` | 第 2 次汇报 PPT 与构建脚本 |
| `scripts/` | 复算、校验、冒烟脚本 |
