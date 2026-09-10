# Teacher Reply And Report Prep Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将老师对课题5实验范围、阶段顺序和报告形式的回复落实为可执行但仍受启动门约束的仓库计划。

**Architecture:** 保留现有 `benchmark-plan.json` 作为实验真相源，新增阶段门、模态边界和报告交付说明；把未知的 DCS 路径、字段、镜像入口和 kBET 版本继续保持 `pending`。报告先以 Markdown/JSON 作为可审计源文件，最终通过 Word 导出流程生成 `.docx`。

**Tech Stack:** Python 3 标准库、JSON、Markdown、现有 unittest 套件、仓库内 DOCX 工具说明。

## Global Constraints

- 不创建 DCS 实例、不提交云任务、不上传数据、不安装 DCS 包、不消耗余额。
- HEART 首轮只使用 2–3 个物种验证流程；后续覆盖近缘、远缘和不同类别组合。
- 主实验只评测单细胞数据；LBSPA 单核在单细胞结论后小规模补充；空间数据暂不纳入主实验。
- 未经课程管理员确认的路径、字段、物种清单、镜像入口、版本和正式 kBET 保持 `null`/`pending`。
- 最终报告交付 Word；仓库保留机器可读源文件与导出说明。

### Task 1: Correct teacher-reply facts and phase gates

**Files:**
- Modify: `config/benchmark-plan.json`
- Modify: `docs/course-requirements-audit.md`
- Modify: `docs/source-notes.md`
- Modify: `README.md`
- Modify: `docs/minimal-verification-runbook.md`
- Modify: `docs/handoff-to-teammates.md`
- Modify: `docs/ai-use-log.tsv`
- Test: `tests/test_smoke_test.py`

**Interfaces:**
- `scripts/plan_contract.py` continues to validate the existing safety contract.
- New phase metadata is additive and must not turn the plan into an executable cloud plan.

- [x] **Step 1: Write the failing test**

Add tests asserting that the plan declares a 2–3 species pilot, later near/far/different-category coverage, single-cell-first modality policy, and post-conclusion snRNA follow-up.

- [x] **Step 2: Run the focused test to verify it fails**

Run `python -m unittest tests.test_smoke_test.SmokeEvaluatorTests.test_teacher_reply_phase_gates -v`.
Expected: FAIL because the new phase metadata is absent.

- [x] **Step 3: Write the minimal configuration and documentation changes**

Add only additive JSON fields and concise documentation. Do not fill unknown DCS paths or exact species names.

- [x] **Step 4: Run focused and full tests**

Run `python -m unittest tests.test_smoke_test.SmokeEvaluatorTests.test_teacher_reply_phase_gates -v` and then `python -m unittest discover -s tests -q`.
Expected: the focused test and the full suite pass.

- [x] **Step 5: Record the change**

Append one row to `docs/ai-use-log.tsv` with the fresh test count and `no remote actions`.

### Task 2: Add Word report source and export contract

**Files:**
- Create: `docs/report-delivery.md`
- Create: `docs/report-template.md`
- Modify: `README.md`
- Modify: `docs/handoff-to-teammates.md`
- Test: `tests/test_smoke_test.py`

**Interfaces:**
- Report source sections must map to final artifacts and metrics in `config/benchmark-plan.json`.
- DOCX generation remains review-only until real results exist; no fabricated results may be inserted.

- [x] **Step 1: Write the failing test**

Add a test that checks the report-delivery document names `.docx` as the final format, keeps Markdown/JSON as source, and includes the required sections and no-real-results rule.

- [x] **Step 2: Run the focused test to verify it fails**

Run `python -m unittest tests.test_smoke_test.SmokeEvaluatorTests.test_report_delivery_contract -v`.
Expected: FAIL because the report documents do not yet exist.

- [x] **Step 3: Write the minimal report documents**

Create a concise template covering abstract, data and scope, methods, fairness controls, results tables/figures, resource use, limitations, scenario guide, and appendix. State that placeholder examples and smoke proxies cannot be presented as final results.

- [x] **Step 4: Run focused and full tests**

Run the focused test and `python -m unittest discover -s tests -q`.
Expected: all tests pass.

### Task 3: Final local verification and handoff

**Files:**
- Modify: `docs/minimal-verification-runbook.md`
- Modify: `docs/ai-use-log.tsv`

- [x] **Step 1: Run plan, smoke, source, and readiness checks**

Run `python scripts/plan_contract.py`, `python scripts/smoke_test.py --outdir smoke-output`, `python scripts/startup_preflight.py`, and the full unittest suite.

- [x] **Step 2: Check the diff for secrets and accidental DCS actions**

Run `git diff --check` and inspect changed paths; reject any credential, cookie, token, raw data, or cloud submission artifact.

- [x] **Step 3: Update the handoff status**

Record the fresh test count and keep `approval_status: pending` unless the teacher has supplied the missing machine-readable fields.
