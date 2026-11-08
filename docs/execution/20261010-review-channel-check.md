# Phase 0 审阅通道复核记录（2026-10-10）

## 目的

记录本轮对 Claude/Flash 与 ZCode 审阅通道的只读可用性检查，避免把“通道失败”误判成 Phase 0 已通过。

## 检查结果

### Claude Code

- CLI 版本：`2.1.296 (Claude Code)`。
- `claude --print` 默认路由失败：当前配置模型 `deepseek-v4.1-flash` 不在本版本模型目录中。
- 显式指定 `--model sonnet` 也失败：选择的 `claude-sonnet-5-5` 不存在或当前账号不可用。
- 本轮未读取、修改或输出任何凭据；未修改 Claude 配置。

### ZCode

- `node D:\zcode\resources\glm\zcode.cjs doctor --json` 可运行，版本 `0.16.9`。
- 只读 `--prompt` 仍失败：CLI 试图读取
  `D:\zcode\resources\glm\provider\zcode-builtin.json` 或
  `D:\config\provider\zcode-builtin.json`，但实际安装配置位于
  `D:\zcode\resources\config\provider\zcode-builtin.json`。
- 未修改 ZCode 安装目录、未创建 junction、未改 provider 配置。

## 当前判定（**已被下方"更正"取代，勿引用**）

- Phase 0 审阅门仍为 `pending`。
- 没有获得正式 `verdict: PASS`，因此不能把本轮视为审阅通过。
- 不启动 Task 1，不运行 smoke，不提交 DCS，不训练，不启动 GPU，不充值。

## 更正（2026-10-10 16:31）

上文的"通道失败"判断**是误判**。实测 `claude -p "<prompt>"` 退出码 **0** 并正常返回正文；输出里那两行

```text
"deepseek-v4.1-flash" isn't described by this version's model catalog; …
[claude-code:unrecognized_model] {"model":"deepseek-v4.1-flash","query_source":"sdk"}
```

是 **stderr 警告**（模型不在本版本的模型目录里、自动压缩按 200k 上下文估计），**不是失败**。此前把这条警告当成了模型不可用。

正确调用方式（只读）：

```text
claude -p "<prompt>" --allowedTools "Read,Glob,Grep,Bash,PowerShell" --disallowedTools "Edit,Write,NotebookEdit"
```

要点：`stdout` 与 `stderr` 必须分开重定向，否则警告会混进审阅正文；不要加 `--model` 覆盖（此前失败的 `deepseek-flash` 就是覆盖出来的、确实不在目录里的名字）。

已按此跑完 4 轮外部反方审阅（2 轮 REVISE、2 轮 PASS，最终 PASS），见 `20261010-task1-preflight.md` 的 Review status 与 `results/phase-20261010/review-gate-status.json`。
