# 审阅通道检查（2026-10-11）—— 本轮不可用

## 一、现象

第 1 轮外部审阅（REVISE）顺利完成后，第 2 轮复审**无法执行**：

```
$ claude -p "只回复 OK" --allowedTools "Read"
exit=1
stdout: There's an issue with the selected model (deepseek-v4.1-flash).
        It may not exist or you may not have access to it. Run --model to pick a different model.
stderr: "deepseek-v4.1-flash" isn't described by this version's model catalog; ...
        [claude-code:unrecognized_model] {"model":"deepseek-v4.1-flash","query_source":"sdk"}
```

## 二、与历史"误判"的区别（必须区分）

| 场景 | 退出码 | stdout | 判定 |
|---|---|---|---|
| 2026-10-10 历史记录的"警告"（见 20261010-review-channel-check.md 更正一节） | **0** | 正常审阅文本 | 通道可用；`unrecognized_model` 只是 stderr 警告 |
| **本轮（2026-10-11）** | **1** | **错误文本本身**（无审阅内容） | **通道不可用** |

即：本轮的同一行 `unrecognized_model` 出现在 stderr，但**退出码为 1、stdout 无审阅内容**——属真实失败，不是警告混入。

## 三、处理（按纪律：不自行改模型）

- **未**添加 `--model` 覆盖（提示词明确禁止；且换模型会改变审阅者，属实质变更，须用户/维护者决定）。
- **未**把失败当成"通过"，**未**伪造审阅结论。
- 本轮阶段 2 隔离层状态据此冻结为：**修订完成 + 第 1 轮审阅已闭环 + 第 2 轮复审待通道恢复**。

## 四、待复现/待办

1. 恢复通道后，把 `.tmp-claude-stage2-r2.md`（复审提示词，5 项 must_fix + 2 项回归）原样交给 Claude 执行；
2. 预期复审对象（本轮修订后 SHA）：
   - `scripts/ortholog_pca_full_isolated.py` = `48d79ad1c41d85ac3a68d806ec771e3dca7c8d927f4a27dc608ec8bb81bee83c`
   - `scripts/run_samap_full_isolated.py` = `6603c71b394282f53c8dec253cc900a7e1cc8ab166b8e20b0a145279bb967111`
3. 若维护者确认应指定其它模型，请给出模型名后再跑（不擅自选择）。

## 五、可能的成因（供维护者判断）

- 本会话早期 `claude -p` 可用（同配置、exit 0），说明 CLI 与凭据链本身完好；本轮失败发生在**同一配置**下，指向 provider 侧对该模型名的可用性变化，或 SDK 侧模型目录校验收紧。
- 与本仓库改动无关：本轮只新增/修改了 `scripts/*_isolated.py` 与 `docs/execution/`，未触碰 Claude 配置。
