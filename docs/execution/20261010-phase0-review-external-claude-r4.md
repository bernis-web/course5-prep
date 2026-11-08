All six items verified independently. Report below.

---

# Phase 0 门 · 第四轮独立复核（只读）

工作目录 `D:\projects\course5-prep`。全程未创建/修改/删除任何文件，未 git 操作，未提交 DCS/GenPilot/训练/GPU。

## 1. wrapper sha256 vs 文档声明 — 一致

```
sha256sum scripts/ortholog_pca_task1_isolated.py
71ab5642ad8e8a964717ad738c7f60524f9d1372fcc5bbc534cf63c64d7002ed
```
`docs/execution/20261010-task1-preflight.md:33` 声明 `71ab5642ad8e8a964717ad738c7f60524f9d1372fcc5bbc534cf63c64d7002ed`。**逐字符相同。**

## 2. F1 是否真的修好 — 是

- **落盘走 `write_bytes`**：`scripts/ortholog_pca_task1_isolated.py:436` `patched_path.write_bytes(patched.encode("utf-8"))`。`grep -n "write_bytes\|write_text"` 显示全脚本 9 处 `write_text` 全部是 `verification.json`(×2, 268/357)、`sha256.tsv`(370)、`predictions.json`(450)、`confusion.json`(451)、`environment.txt`(454)、`wrapper-provenance.json`(474) — **没有一处把 `_patched_source.py` 交给 `write_text`**。
- **硬断言存在**：`:437-440` `written_sha = sha256_file(patched_path)`；`if written_sha != sha256_text(patched): die(..., 2)`。
- **内存独立复算**（`python -B`，未落任何文件）：

| 量 | 值 |
|---|---|
| `sha256_text(original)` | `6582d8736c3570f3de23ed36cb57c9cf58f6190c4730c3d39e29928415fd0c44` |
| `sha256_file(SOURCE)` | `6582d873…`（两者相等） |
| `sha256_text(patched)` | `c56d3ee7607cf4a5b20af446ba279390f1cef3ba361e7b76d55ec3871367ba55` |
| `hashlib.sha256(patched.encode("utf-8"))` | 同上（`LF==disk-bytes model: True`） |
| CRLF 形态 `patched.replace("\n","\r\n")` | `cc8f59e216499d1913cf929f4972036b9944d779cbb0b819ea41afc1ba97171b` |

  即 `sha256(patched.encode("utf-8")) == sha256_text(patched) == c56d3ee7…`，且 **CRLF 形态确实得到不同值**（`cc8f59e2…`，与文档 §F1 引用的值一致）。原缺陷成立：`ortholog_pca_local_v1.py:344` `"script_sha256": sha256_file(__file__)`（磁盘字节），而 wrapper `:177` 把 `__file__` 指向 `patched_path`，故 manifest 走磁盘字节、`:471`/`:484` 走 `sha256_text` — 修复前两者必然差一个换行变换，现在三处同为 `c56d3ee7…`。**F1 已闭合。**

  Python 3.9 的 `Path.write_text` 无 `newline` 参数属实（3.10 才加）。我未单独复现该 `TypeError`，但这一点不承重：`write_bytes` 在任何版本上都正确。

## 3. 两条残留 — 都已修

- **(a) `.get` 链在 `try` 内**：`:226-232` — `try:` 在 226，`frozen = load_json(...)` 在 227，`block = frozen.get(DIRECTION, {}).get(LEVEL)` 在 230-231，`except Exception` 在 232。另外 `:230` 还加了 `isinstance(frozen, dict)` 守卫。非 dict 中间值 → `block` 保持 `None` → `:234` `frozen_metrics:has_human->mouse/coarse` 记 `ok=False`，**不存在静默通过**。
- **(b) `verify()` 形状异常走退出码 4**：`:275-295` 四条路径全覆盖 — 新 metrics 缺失(`:276-278`)、冻结 metrics 缺失(`:279-281`)、新 metrics 形状异常(`:284-289`)、冻结 metrics 形状异常(`:290-295`)，每条都先 `write_failure_report(out, …)`（定义在 `:258-270`，写 `verification.json`）再 `die(…, 4)`。`:285`/`:291` 的 `[DIRECTION][LEVEL]` 查找不再可能裸抛 `KeyError`。

## 4. 补丁集与补丁后哈希 — 未变

dry-run 实测输出：`patches_applied=6`，名称 `P1 main-header / P2 species-loop / P3 direction-map / P4 levels / P5 done-print / P6 base-scope`，各锚点 sha256 与 `:76-124` 定义一一对应；`patched_sha256=c56d3ee7…`，`source_sha256=6582d873…`。P6 仍在（`:120-123`），且其锚点 `BASE = Path(__file__).resolve().parents[1]` 在权威源码中仍**恰好出现一次**（`ortholog_pca_local_v1.py:33`）。**P1–P6、c56d3ee7… 均未变。**

## 5. 只读复核 — 全部通过

| 检查 | 结果 |
|---|---|
| `results/phase-20261010/A-smoke/` | **不存在**（`test -e` → ABSENT；dry-run 后复查仍 ABSENT） |
| `scripts/ortholog_pca_local_v1.py` | `6582d8736c3570f3de23ed36cb57c9cf58f6190c4730c3d39e29928415fd0c44` ✓ |
| `results/pilot-v1` mtime | 196 个文件，`find -newermt "2026-10-10T11:04:48+08:00"` **返回空** ✓ |

`results/phase-20261010/` 下仅 4 个文件（baseline 两件 + 两个 json），无 A-smoke 产物。

## 6. 两项声明 — 属实

- **"15/15 checks pass"**：实跑只读 dry-run（`PYTHONDONTWRITEBYTECODE=1 .venv39/Scripts/python.exe -B … --dry-run`）得到 `DRYRUN|preflight_checks=15 failed=0` 与 `DRYRUN|preflight=PASS`，退出码 0。静态计数亦为 15（BASE 1 + ORTH_DIR 1 + ortholog 3 + MAPPING 1 + input 3 + LEVELS/NPERM/smoke/out 4 + frozen 2）。冻结 `metrics.json` 的 `human->mouse/coarse` 确实存在且 10 个字段齐全，与 `:237-238` 的 required 列表吻合。
- **新 wrapper sha256**：见第 1 条，一致。

## 非阻断观察（不影响 PASS）

- **O1**：`scripts/__pycache__/ortholog_pca_task1_isolated.cpython-39.pyc` 存在，mtime `2026-10-10 16:28:28`，比文档记录的 dry-run 时刻（16:28:36）早 8 秒 —— 因此**不是 dry-run 产生的**（脚本以 `__main__` 运行不会缓存自身），而是第三轮工作期某次 import 留下的。该文件被 `.gitignore:2`（`__pycache__/`）忽略，不在 `results/` 内，也无任何声明哈希覆盖它。属构建副产物，仅提示：若要求"预检不留痕"，用 import 方式调用会留下 pyc。
- **O2**：`:450-451` 的顶层 `predictions.json` / `confusion.json` 副本走 `write_text`，Windows 上 LF→CRLF，故与原生 `predictions/coarse_human_to_mouse.json` / `confusion/coarse_human_to_mouse.json` **非逐字节相同**（JSON 语义相同）。无声明要求字节相同，且 `sha256.tsv` 记录的是实际磁盘字节，自洽；但下游若按字节比对两份副本会看到差异。`environment.txt` / `verification.json` / `wrapper-provenance.json` 同理（wrapper 自撰文本，无外部字节声明）。
- **O3**：`:437-440` 的断言是**重言式**（写入的就是 `patched.encode("utf-8")`，哈希必然相等）。作为回归护栏有效，但除文件系统篡改写入外不可能失败，不应被当作独立验证。
- **O4**：`frozen_metrics:parse` 仅在异常时添加；顶层非 dict 时不加该项，但会由 `frozen_metrics:has_…` 记 FAIL —— 仍无静默通过。

本次会话内仓库中唯一 mtime 晚于开工时刻的文件是 `.tmp-claude-phase0-review-r4.err.log`（评审调用方自身的 stderr 捕获），非我经工具创建。

**结论：F1 已真正修复，两条残留已闭合，补丁集与冻结哈希未漂移，只读边界完好，文档两项声明与实测一致。无阻断项。**

verdict: PASS
