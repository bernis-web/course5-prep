# Task 1 preflight (2026-10-10)

## Current conclusion

This record is read-only evidence. No model was run, `results/pilot-v1` was not modified, no DCS task was submitted, no GPU was started, and no recharge was made.

## Baseline input SHA

The 11 file rows below the header in `results/phase-20261010/baseline/input-sha256.tsv` were recomputed in this turn. All 11/11 SHA-256 values matched; the header is not a file row.

## Task 1 protocol mismatches found

1. `scripts/ortholog_pca_local_v1.py` `--smoke` hard-codes output to `results/pilot-v1/ortholog-pca-smoke/` (lines 158-160) and refuses to run when that directory exists. The directory already exists. Deleting it would violate the no-clean/no-overwrite boundary.
2. The same smoke branch samples all three species and continues through six directions and exact/coarse/fine levels. That is not the Task 1 requirement of a single `human->mouse`, `coarse` smoke.

## Proposed handling (not executed)

After the Phase 0 Claude/Flash gate returns `verdict: PASS`, create an isolated wrapper or equivalent copy that:

- writes only to `results/phase-20261010/A-smoke/`;
- reads human and mouse only;
- computes only `human->mouse` at the coarse level;
- emits `manifest.json`, `command.txt`, `environment.txt`, `metrics.json`, `confusion.json`, and `sha256.tsv`;
- checks the confusion diagonal and `accuracy * n_q` independently, with `abs_diff <= 1e-12` against frozen metrics **after rounding the recomputed values to the frozen precision** — the frozen `acc` / `majority` / `shuffle_p` / `coverage_q` are stored as `round(x, 4)` (`scripts/ortholog_pca_local_v1.py:315-318`), so comparing a full-precision recomputation against those 4-decimal values differs by ~1e-5 and would abort the run for the wrong reason;
- stops on any mismatch and leaves old results untouched.

No wrapper or smoke run is started before the review gate passes.

## Wrapper prepared (not executed)

`scripts/ortholog_pca_task1_isolated.py` implements the isolated handling above. It does **not** reimplement the pipeline: it reads the authoritative source, applies six text patches whose anchors must each match exactly once (otherwise it hard-stops), writes the patched source into the output dir and executes it — so the reproduction is protocol-faithful by construction, and the patch diff is recorded in `wrapper-provenance.json`.

- wrapper sha256: `71ab5642ad8e8a964717ad738c7f60524f9d1372fcc5bbc534cf63c64d7002ed`
- authoritative source: `scripts/ortholog_pca_local_v1.py`, sha256 `6582d8736c3570f3de23ed36cb57c9cf58f6190c4730c3d39e29928415fd0c44` — identical to the `script_sha256` recorded in `results/pilot-v1/ortholog-pca-v98/manifest.json`, i.e. the wrapper patches the same script that produced the frozen numbers
- patched source sha256: `c56d3ee7607cf4a5b20af446ba279390f1cef3ba361e7b76d55ec3871367ba55`
- patches: P1 main-header, P2 species-loop, P3 direction-map, P4 levels, P5 done-print, P6 base-scope
- guard rails: refuses a non-empty output dir (exit 3); refuses any `--out` resolving inside `results/pilot-v1` (exit 3); exits 4 when the frozen-number comparison fails; the pre-flight runs **before** any directory is created, so a failed pre-flight leaves nothing behind
- **C1（外部审阅第一轮发现，已修）**: the first version pointed `__file__` at `A-smoke/_patched_source.py`, while the authoritative source derives `BASE` from `__file__` at line 33 — so `ORTH_DIR`, `MAPPING_TSV` and all three h5ad inputs resolved under `results/phase-20261010/` and the run would have died at `die("missing input")`. Patch P6 now pins `BASE` to the absolute repo root, and `--dry-run` was upgraded to actually exec the patched source. See `20261010-phase0-review-external-claude.md` §3-C1.
- **N2（外部审阅第二轮提出，已加固）**: the pre-flight now also parses the frozen `metrics.json` and asserts that `human->mouse` / `coarse` exists with all ten fields `verify()` compares — otherwise a malformed frozen file would only surface as an uncaught `KeyError` (exit 1) after a full model run, instead of the documented `verification.json` + exit 4. Two residual gaps raised in the third round are closed as well: the whole `.get` chain sits inside the `try` (a non-dict intermediate value can no longer raise `AttributeError`), and `verify()` now wraps its own reads of the A-smoke and frozen metrics so a shape problem writes `verification.json` and exits 4 rather than raising a bare `KeyError`.
- **F1（外部审阅第三轮发现，已修）**: `_patched_source.py` was written with `Path.write_text`, which translates `\n` to CRLF on Windows. The manifest's `script_sha256` comes from `sha256_file(__file__)` (disk bytes) while `wrapper-provenance.json` / `environment.txt` recorded `sha256_text(patched)` (LF text) — so a single run would have emitted **two different values both labelled "patched source hash"**, and the provenance's `patched_source` path would have pointed at a file whose byte hash did not equal the recorded value. Reproduced: LF `c56d3ee7…` vs CRLF `cc8f59e2…`. Fixed by writing bytes directly (`write_bytes(patched.encode("utf-8"))`) plus a hard assertion that the on-disk hash equals the recorded text hash. Note Python 3.9's `Path.write_text` has no `newline` parameter (added in 3.10), so the byte-write form is required, not merely preferred.
- `--dry-run` is now a real pre-flight: apply patches → exec the patched source (`__name__ != "__main__"`, so `main()` does not run) → assert `BASE` is the repo root and `ORTH_DIR`, the three ortholog files, `MAPPING_TSV` and all three h5ad inputs exist, plus `LEVELS == ("coarse",)`, `NPERM_FULL == 200` and the frozen-metrics structure. Measured 2026-10-10T16:28:36+08:00: **15/15 checks pass**, `results/phase-20261010/A-smoke/` **was not created**, no output artifact written. It does **not** run the model, so it proves the wrapper can start — not that the numbers reproduce.
- **N1（外部审阅第二轮提出，已记录）**: the A-smoke `manifest.json` will record `script_sha256` as the hash of the **patched** source, so it will differ from the frozen manifest's `6582d873…`. This is correct behaviour — the field documents the artifact actually executed — and after F1 it is the same single value the wrapper records as `patched_source_sha256` (`c56d3ee7…`). Do not read the difference from `6582d873…` as protocol drift.
- **N3（外部审阅第二轮提出，第三轮补充，已记录）**: P2 restricts only the data-loading loop, so `SPECIES_FILES` and the `inputs` / `input_sha256` registration still list `local_zebrafish_s.h5ad`; the A-smoke manifest will therefore name a zebrafish input that is never read. The pre-flight likewise requires that file to exist, because it mirrors the patched script's own input check. Cosmetic only — no number depends on it.
- **Operational note（外部审阅第三轮）**: the output directory is created before the model runs, so a hard stop inside the patched `main()` (for example `<1000` shared orthologs) leaves a partial `A-smoke/`, and the non-empty-directory guard will refuse a retry at the same path. Recover by running with a fresh `--out <new dir>`; no deletion is required and none is performed by the wrapper.
- Task 1 smoke: **NOT RUN**

## Review status

- Local Phase 0 SHA check: PASS (11/11).
- Local read-only review round 1 (`docs/execution/20261010-phase0-review-result.md`): `verdict: REVISE` (item 5 overwrite paths; fixes F1–F3).
- Local read-only review round 2 (`docs/execution/20261010-phase0-review-result-r2.md`): `verdict: PASS` after F1–F4 landed. Local scope only.
- **External Claude review is available.** The earlier "model unavailable" reading was a misdiagnosis: `claude -p` exits 0 and returns text; the `unrecognized_model` line is a **stderr warning** about the model catalog / assumed context window, not a failure. Four read-only rounds were run with `--allowedTools Read,Glob,Grep,Bash,PowerShell --disallowedTools Edit,Write,NotebookEdit`:
  - round 1 (`20261010-phase0-review-external-claude.md`): `verdict: REVISE` — found **C1**, the `BASE`-scoping defect that made the wrapper unrunnable, plus C2–C5.
  - round 2 (`...-r2.md`): `verdict: PASS` after C1–C5 landed; the reviewer independently exec'd the patched source with a deliberately forged `__file__` and recomputed the C4 statistics.
  - round 3 (`...-r3.md`): `verdict: REVISE` — found **F1**, the patched-source hash split between LF text and CRLF disk bytes.
  - round 4 (`...-r4.md`): `verdict: PASS` — verified F1 closed, both residuals closed, patch set and frozen hashes undrifted, read-only boundary intact.
- Non-blocking observations from round 4 (recorded as-is, deliberately not "fixed" to avoid churning a reviewed artifact):
  - **O1**: `scripts/__pycache__/ortholog_pca_task1_isolated.cpython-39.pyc` exists from an import-based check; it is gitignored (`.gitignore:2`), outside `results/`, and covered by no declared hash.
  - **O2（已由 Task 1 运行后实测更正）**: round 4 predicted that the top-level `predictions.json` / `confusion.json` copies would be LF→CRLF translated by `write_text` and therefore not byte-identical to the native `predictions/` / `confusion/` files. **That inference was wrong.** `json.dumps` emits no newline characters at all, so the newline translation is an identity operation; after the actual Task 1 run all four files have CR=0 / LF=0 and pairwise identical SHA-256. See `20261010-task1-a-smoke-report.md` §更正 (D1).
  - **O3**: the byte-hash assertion added for F1 is a tautology by construction (`write_bytes` of `patched.encode("utf-8")`); it can only fail on external tampering. Treat it as a regression guard, not as independent verification.
  - **O4**: `frozen_metrics:parse` is only recorded on exception; a non-dict top level is still caught, because `frozen_metrics:has_human->mouse/coarse` records FAIL.
- Task 1: NOT STARTED.
