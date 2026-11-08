# Phase 0 反方审阅请求（给 Claude/Flash）

工作目录：`D:\projects\course5-prep`

请只读审阅，不修改文件、不提交、不推送、不调用 DCS/GenPilot、不训练、不充值，也不读取任何凭据。先阅读：

- `docs/superpowers/plans/2026-10-10-course5-genpilot-dcs-longrun.md`
- `docs/execution/20261010-baseline.md`
- `results/phase-20261010/run_scope.json`
- `results/phase-20261010/baseline/git-status.txt`
- `results/phase-20261010/baseline/input-sha256.tsv`

核对内容：

1. Phase 0 是否确实只读，是否明确没有训练、DCS 提交、GPU 和充值。
2. `input-sha256.tsv` 中列出的 SHA 是否与当前文件一致。
3. oPCA v98、SAMap v98、SATURN v99 recovered 的目录和口径是否被准确描述，是否把 candidate 写成 confirmed。
4. transductive/in-sample、oPCA label-free、SATURN `labels`/`ref_labels`、SAMap `keys=cell_type`、v97g 日志级限制是否写对。
5. 是否存在会覆盖 `results/pilot-v1` 冻结结果、绕过审批门或提前训练的路径。

输出正常 Markdown，逐项给出“通过/需修改/阻塞”，引用文件和行号；最后给出：

`verdict: PASS | REVISE | BLOCK`

只有 PASS 才能进入 Task 1 的 human→mouse coarse 零成本 smoke。若发现任一 SHA、协议、分母、coverage 或输入角色不一致，要求停止并列出修正项。
