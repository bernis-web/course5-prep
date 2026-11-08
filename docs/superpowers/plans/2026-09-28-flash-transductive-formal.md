# Transductive-Formal Re-evaluation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an auditable, direction-explicit, per-cell SATURN v71/v72 re-evaluation path without claiming a new held-out benchmark.

**Architecture:** Keep `config/eval-manifest-v73.json` as the evidence gate and create a separate v74 evaluation workspace. A local builder verifies the frozen Final AnnData, applies species-prefixed barcodes, emits explicit NPZ bundles and direction-specific role tables, then the existing evaluator produces exact/coarse/fine summaries with full exclusion audit. Real execution is blocked until the SHA-256-verified Final AnnData is locally available; no DCS task is authorized by this plan.

**Tech Stack:** Python 3, unittest, numpy, pandas, anndata only for the real-file reader, existing `scripts/evaluate_cross_species_transfer.py`, JSON/TSV/SHA-256 manifests.

## Global Constraints

- Work only in `D:\projects\course5-prep`; do not clean, revert, commit, push, or touch unrelated dirty files.
- Do not submit, cancel, retry, or modify any DCS task. Any future DCS extraction task needs a new explicit user approval.
- Keep `config/eval-manifest-v73.json` at `evidence_status=pending`; v74 outputs are a formal re-evaluation of an existing exploratory run, not an independent benchmark.
- Never fill v71/v72 run fields with v95/v96 task IDs or hashes. V96 only supports partial provenance.
- Use `obsm["macrogenes"]`, 1,000 dimensions, cosine distance, and k=15.
- Use `obs["ref_labels"]` as the biological label source and `obs["species"]` as the species source; never use numeric `obs["labels"]` as cell type.
- Prefix every barcode by species before evaluation: `hu|`, `mo|`, and `zf|`. Refuse duplicates after prefixing rather than silently dropping them.
- Each direction has its own role table because a species is reference in some directions and query in others. Do not populate the global header-only `config/barcode-roles-v73.tsv` with six-direction roles.
- Report exact, coarse-mapped, and fine-mapped results separately. Exclude `mapping_status=unmapped` only from the mapped denominator and report its coverage.
- Every result index must say: `transductive_formal_reassessment_of_v71_v72; not_inductive; not_held_out_benchmark`.

---

## Current Evidence Snapshot

Use these exact values; do not rederive or guess them:

- Final AnnData path on DCS: `/data/work/saturn_out_real3_h/saturn_results/test256_data_human_saturn_input_hvg_mouse_saturn_input_hvg_zebrafish_saturn_input_hvg_org_human_seed_0.h5ad`
- SHA-256: `20cf807fcaa5e8ed9ac65a28d50e781c82c9c48cdac9b7a1820dcf74bdf5143f`
- Expected cells and dimensions: `4606 × 1000` for `obsm["macrogenes"]`
- Species counts: human 1,528; mouse 1,535; zebrafish 1,543
- Raw duplicate barcode count before species prefixing: 6
- Evidence: `docs/dcs-provenance-recovery-v96-20260928.md`
- The 256-column AnnData `X`/storage shape and the 1,000-dimensional evaluation layer are different concepts; do not compare them as a contradiction.

## Task 1: Let Manifest Validation Recognize Closed Partial Evidence

**Files:**

- Modify: `scripts/validate_eval_manifest.py`
- Modify: `tests/test_eval_manifest.py`

**Interfaces:**

- Consumes: `representation.evaluation_layer="obsm/macrogenes"` in the pending v73 manifest.
- Produces: validator output where a valid evaluation layer is not listed as a blocker, while pending run/barcode/reviewer fields still block confirmation.

- [ ] **Step 1: Add regression assertions**

In `tests/test_eval_manifest.py::EvalManifestTests::test_current_manifest_is_valid_but_not_ready_and_header_only_roles_block`, add:

```python
# V96 confirmed this partial field while the overall provenance gate remains pending.
self.assertNotIn(
    "representation.evaluation_layer", result["blocking_items"]
)
```

Add a second test to the same class:

```python
def test_pending_manifest_reports_missing_evaluation_layer_without_error(self):
    manifest = load_manifest(ROOT / "config" / "eval-manifest-v73.json")
    manifest["representation"]["evaluation_layer"] = "pending"
    result = validate_eval_manifest(manifest, [])
    self.assertTrue(result["valid"])
    self.assertFalse(result["ready_for_confirmation"])
    self.assertIn(
        "representation.evaluation_layer", result["blocking_items"]
    )
```

- [ ] **Step 2: Run the failing test**

```powershell
python -m unittest tests.test_eval_manifest -v
```

Expected before implementation: the new assertion fails because the pending branch currently appends `representation.evaluation_layer` unconditionally.

- [ ] **Step 3: Make the blocker conditional**

In the `if evidence_status == "pending":` branch of `scripts/validate_eval_manifest.py`, replace:

```python
blockers.append("representation.evaluation_layer")
```

with:

```python
if representation.get("evaluation_layer") not in ALLOWED_REPRESENTATIONS:
    blockers.append("representation.evaluation_layer")
```

Do not change any rule that keeps run IDs, original commands, training flags, reviewer, datasets, or barcode roles pending.

- [ ] **Step 4: Verify**

```powershell
python -m unittest tests.test_eval_manifest -v
python scripts/validate_eval_manifest.py
```

Expected: all tests pass; `valid=true`, `evidence_status=pending`, `ready_for_confirmation=false`; `representation.evaluation_layer` is absent from blockers, while barcode/reviewer/run blockers remain.

## Task 2: Add Mapping and Barcode Namespace Contracts

**Files:**

- Create: `scripts/build_transductive_bundles.py`
- Create: `tests/test_build_transductive_bundles.py`

**Interfaces:**

- Produces module-level constants and pure functions used by later tasks:

```python
SPECIES_PREFIXES = {
    "human": "hu",
    "mouse": "mo",
    "zebrafish": "zf",
}

def canonical_species(value: str) -> str: ...
def prefixed_barcode(species: str, barcode: str) -> str: ...
def load_mapping_rows(path: Path) -> list[dict[str, str]]: ...
def level_mapping(
    rows: list[dict[str, str]],
    selected_species: set[str],
    level: str,
) -> dict[str, str]: ...
```

- `level_mapping` accepts `level="coarse"` or `level="fine"`, uses only rows from `selected_species`, maps to `coarse_level` or `fine_mapped_label`, and raises `BundleBuildError` if one exact source label maps to different values in the selected species pair.
- Rows with `mapping_status="unmapped"` are omitted from the active mapping and later omitted from mapped bundles; their counts must be reported.

- [ ] **Step 1: Write failing tests**

Create these tests:

```python
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from build_transductive_bundles import (  # noqa: E402
    BundleBuildError,
    SPECIES_PREFIXES,
    canonical_species,
    level_mapping,
    load_mapping_rows,
    prefixed_barcode,
)


class MappingNamespaceTests(unittest.TestCase):
    def test_species_names_are_canonicalized_and_prefixed(self):
        self.assertEqual(canonical_species("Homo_sapiens"), "human")
        self.assertEqual(canonical_species("Mus_musculus"), "mouse")
        self.assertEqual(canonical_species("Danio_rerio"), "zebrafish")
        self.assertEqual(prefixed_barcode("human", "AAAC-1"), "hu|AAAC-1")
        self.assertEqual(prefixed_barcode("mouse", "AAAC-1"), "mo|AAAC-1")
        self.assertEqual(prefixed_barcode("zebrafish", "AAAC-1"), "zf|AAAC-1")
        with self.assertRaises(BundleBuildError):
            canonical_species("lamprey")

    def test_level_mapping_is_direction_safe_and_excludes_unmapped(self):
        rows = [
            {
                "source_species": "human",
                "source_label": "Endothelial cell",
                "coarse_level": "endothelial",
                "fine_mapped_label": "endothelial cell",
                "mapping_status": "active",
            },
            {
                "source_species": "mouse",
                "source_label": "Endothelial cell",
                "coarse_level": "endothelial",
                "fine_mapped_label": "endothelial cell",
                "mapping_status": "active",
            },
            {
                "source_species": "mouse",
                "source_label": "Proliferating cell",
                "coarse_level": "other",
                "fine_mapped_label": "unmapped",
                "mapping_status": "unmapped",
            },
        ]
        mapping = level_mapping(rows, {"human", "mouse"}, "coarse")
        self.assertEqual(mapping["Endothelial cell"], "endothelial")
        self.assertNotIn("Proliferating cell", mapping)

    def test_conflicting mappings_are_rejected(self):
        rows = [
            {
                "source_species": "human",
                "source_label": "Valve",
                "coarse_level": "fibroblast",
                "fine_mapped_label": "human valve",
                "mapping_status": "active",
            },
            {
                "source_species": "mouse",
                "source_label": "Valve",
                "coarse_level": "fibroblast",
                "fine_mapped_label": "mouse valve",
                "mapping_status": "active",
            },
        ]
        with self.assertRaises(BundleBuildError):
            level_mapping(rows, {"human", "mouse"}, "fine")

    def test_real_mapping_file_loads(self):
        root = Path(__file__).resolve().parents[1]
        rows = load_mapping_rows(root / "config" / "heart-celltype-map-v1.tsv")
        self.assertEqual(len(rows), 38)
        self.assertEqual(SPECIES_PREFIXES["zebrafish"], "zf")
```

- [ ] **Step 2: Run the failing tests**

```powershell
python -m unittest tests.test_build_transductive_bundles -v
```

Expected: import failure because the module does not exist.

- [ ] **Step 3: Implement only the pure contracts**

Create `scripts/build_transductive_bundles.py` with:

```python
class BundleBuildError(ValueError):
    """Raised when a v74 evaluation bundle would violate the audit contract."""


SPECIES_ALIASES = {
    "human": "human",
    "homo_sapiens": "human",
    "mouse": "mouse",
    "mus_musculus": "mouse",
    "zebrafish": "zebrafish",
    "danio_rerio": "zebrafish",
}

SPECIES_PREFIXES = {
    "human": "hu",
    "mouse": "mo",
    "zebrafish": "zf",
}

MAPPING_COLUMNS = (
    "source_species",
    "source_label",
    "coarse_level",
    "fine_mapped_label",
    "mapping_status",
)
```

Implement `canonical_species`, `prefixed_barcode`, `load_mapping_rows`, and `level_mapping` exactly as described in Interfaces. `load_mapping_rows` must use UTF-8 with newline handling, validate required columns, strip whitespace, and reject empty source species/label/mapping status.

- [ ] **Step 4: Verify**

```powershell
python -m unittest tests.test_build_transductive_bundles -v
```

Expected: all tests pass.

## Task 3: Build Direction-Explicit NPZ Bundles and Role Tables

**Files:**

- Modify: `scripts/build_transductive_bundles.py`
- Modify: `tests/test_build_transductive_bundles.py`

**Interfaces:**

- Add a pure row model:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class CellRecord:
    barcode: str
    species: str
    label_exact: str
    row_index: int
```

- Add:

```python
def validate_cells(
    species: list[str],
    barcodes: list[str],
    labels: list[str],
) -> list[CellRecord]: ...

def direction_bundles(
    cells: list[CellRecord],
    embedding: numpy.ndarray,
    mapping_rows: list[dict[str, str]],
) -> dict[str, dict[str, object]]: ...
```

- `validate_cells` requires equal non-empty lengths, canonicalizes species, prefixes barcodes, and rejects any duplicate prefixed barcode within a species.
- `direction_bundles` returns one entry per ordered species pair. Recommended stable direction keys are `hu->mo`, `hu->zf`, `mo->hu`, `mo->zf`, `zf->hu`, and `zf->mo`.
- Each entry has exact, coarse, and fine bundle descriptions. Exact uses all cells and no label mapping. Coarse/fine use only cells whose `(species,label_exact)` has active mapping, plus a direction-local JSON mapping.

- [ ] **Step 1: Add failing synthetic tests**

Add an explicit fixture at the top of the test class:

```python
def _cells(self):
    return [
        CellRecord("hu|E1", "human", "Endothelial cell", 0),
        CellRecord("mo|E1", "mouse", "Endothelial cell", 1),
        CellRecord("zf|E2", "zebrafish", "Endothelial cell", 2),
        CellRecord("zf|P1", "zebrafish", "Proliferating cell", 3),
    ]

def _embedding(self):
    return numpy.array(
        [
            [1.0, 0.0],
            [0.0, 1.0],
            [0.9, 0.1],
            [0.1, 0.9],
        ],
        dtype=float,
    )

def _mapping_rows(self):
    return [
        {
            "source_species": "human",
            "source_label": "Endothelial cell",
            "coarse_level": "endothelial",
            "fine_mapped_label": "endothelial cell",
            "mapping_status": "active",
        },
        {
            "source_species": "mouse",
            "source_label": "Endothelial cell",
            "coarse_level": "endothelial",
            "fine_mapped_label": "endothelial cell",
            "mapping_status": "active",
        },
        {
            "source_species": "zebrafish",
            "source_label": "Endothelial cell",
            "coarse_level": "endothelial",
            "fine_mapped_label": "endothelial cell",
            "mapping_status": "active",
        },
        {
            "source_species": "zebrafish",
            "source_label": "Proliferating cell",
            "coarse_level": "other",
            "fine_mapped_label": "unmapped",
            "mapping_status": "unmapped",
        },
    ]
```

Verify:

```python
descriptions = direction_bundles(cells, embedding, mapping_rows)
self.assertEqual(
    sorted(descriptions),
    [
        "hu->mo", "hu->zf", "mo->hu",
        "mo->zf", "zf->hu", "zf->mo",
    ],
)
item = descriptions["hu->mo"]
self.assertEqual(item["reference_species"], "human")
self.assertEqual(item["query_species"], "mouse")
self.assertEqual(item["exact"]["n_reference"], 1)
self.assertEqual(item["exact"]["n_query"], 1)
self.assertIn("Endothelial cell", item["coarse"]["mapping"])

fish_item = descriptions["hu->zf"]
self.assertEqual(fish_item["exact"]["n_query"], 2)
self.assertEqual(fish_item["coarse"]["n_query"], 1)
self.assertEqual(fish_item["fine"]["n_unmapped_query"], 1)
```

Also test:

```python
with self.assertRaises(BundleBuildError):
    validate_cells(
        ["human", "human"],
        ["AAAC-1", "AAAC-1"],
        ["A", "B"],
    )
```

Verify the unmapped `zf|P1` cell is absent from `fish_item["coarse"]["selected_cells"]` and `fish_item["fine"]["selected_cells"]` but remains in `fish_item["exact"]["selected_cells"]`.

- [ ] **Step 2: Run and confirm failure**

```powershell
python -m unittest tests.test_build_transductive_bundles -v
```

- [ ] **Step 3: Implement bundle selection**

Implement exact/coarse/fine selection without writing files yet. For each ordered pair:

1. reference cells are the selected reference species; query cells are the selected query species;
2. exact includes all matching cells;
3. mapped levels include only cells whose `(species,label_exact)` is active in `level_mapping`;
4. each description contains `reference_species`, `query_species`, `direction`, `selected_cells`, `n_reference`, `n_query`, `n_unmapped_reference`, `n_unmapped_query`, and `mapping`.

- [ ] **Step 4: Add real AnnData reader and writer**

Add a CLI with required arguments:

```text
--final-anndata PATH
--mapping-tsv config/heart-celltype-map-v1.tsv
--output-dir artifacts/transductive-formal-v74
--expected-sha256 20cf807fcaa5e8ed9ac65a28d50e781c82c9c48cdac9b7a1820dcf74bdf5143f
--species-column species
--label-column ref_labels
--representation-key macrogenes
--expected-cells 4606
--expected-dimensions 1000
```

The reader must:

1. hash the file before opening it and abort on mismatch;
2. read `obs[species_column]`, `obs[label_column]`, `obs_names`, and `obsm[representation_key]`;
3. reject non-finite embeddings and dimension mismatch;
4. call `validate_cells`;
5. verify species counts are 1,528/1,535/1,543.

The writer must create under the output directory:

```text
bundles/exact_<direction>.npz
bundles/coarse_<direction>.npz
bundles/fine_<direction>.npz
mappings/coarse_<direction>.json
mappings/fine_<direction>.json
roles/roles_<direction>.tsv
build-manifest.json
```

NPZ keys must exactly match the existing evaluator:

```text
reference_embeddings
query_embeddings
reference_barcodes
query_barcodes
reference_labels
query_labels
```

The role table header must be:

```text
direction\treference_species\tquery_species\tbarcode\tspecies\tquery_or_reference\tlabel_exact\tmapping_status
```

`build-manifest.json` must include source path, source SHA-256, AnnData cell count, representation key and dimension, species counts, mapping file SHA-256, per-direction selected/unmapped counts, output SHA-256 values, and:

```json
"evaluation_scope": "transductive_formal_reassessment_of_v71_v72; not_inductive; not_held_out_benchmark"
```

Because `anndata` may be unavailable in the base environment, keep all bundle-selection logic testable without importing anndata. Import anndata only inside the real-file reader function or CLI path.

- [ ] **Step 5: Verify**

```powershell
python -m unittest tests.test_build_transductive_bundles tests.test_cross_species_evaluator -v
python scripts/validate_eval_manifest.py
```

Expected: all tests pass and v73 remains pending.

## Task 4: Add the Six-Direction Runner and Result Index

**Files:**

- Create: `scripts/run_transductive_formal_v74.py`
- Create: `tests/test_run_transductive_formal_v74.py`
- Create output only after real data is available: `artifacts/transductive-formal-v74/results/`

**Interfaces:**

- Consumes `build-manifest.json`, bundle paths, mapping JSON paths, and `evaluate_transfer`.
- Produces one JSON per direction/level and `results/result-index.json`.

- [ ] **Step 1: Write runner tests with tiny in-memory bundles**

Do not require anndata. Test that:

1. exact, coarse, and fine are run separately;
2. each result carries direction, level, source bundle SHA-256, protocol `transductive`, k=15, and the non-benchmark scope string;
3. the index refuses a build manifest whose scope string is missing or changed;
4. the index refuses missing bundles or hash mismatch;
5. no code path calls a network API or DCS client.

- [ ] **Step 2: Implement the runner**

CLI:

```powershell
python scripts/run_transductive_formal_v74.py `
  --bundle-dir artifacts/transductive-formal-v74 `
  --output-dir artifacts/transductive-formal-v74/results `
  --k 15
```

The runner must:

1. load and validate `build-manifest.json`;
2. verify every bundle and mapping hash before evaluation;
3. import `load_npz_bundle` and `evaluate_transfer` from the existing evaluator;
4. run exact with an empty mapping, coarse with coarse mapping, and fine with fine mapping;
5. write `exact_<direction>.json`, `coarse_<direction>.json`, and `fine_<direction>.json`;
6. summarize only metrics and audit fields in `result-index.json`, while preserving full per-cell predictions in each direction file;
7. stop on any exception and leave no `READY` marker.

- [ ] **Step 3: Verify**

```powershell
python -m unittest tests.test_run_transductive_formal_v74 -v
python -m unittest discover -s tests -v
```

Expected: all tests pass; existing anndata-dependent skips may remain if the local environment lacks anndata.

## Task 5: Real-Data Execution Gate

**Files:**

- Input: locally available, SHA-256-verified Final AnnData
- Output: `artifacts/transductive-formal-v74/`

**Interfaces:**

- Consumes the Task 3/4 scripts.
- Produces the actual v74 re-evaluation artifacts and evidence document.

- [ ] **Step 1: Stop if the Final AnnData is not local**

The required local file must hash to:

```text
20cf807fcaa5e8ed9ac65a28d50e781c82c9c48cdac9b7a1820dcf74bdf5143f
```

If it is absent, report:

```text
BLOCKED: locally accessible v71 Final AnnData is required before real v74 execution.
```

Do not substitute `local_samap3_emb.h5ad`, `local_*_s.h5ad`, the 16-macrogene output, or any SATURN source file.

- [ ] **Step 2: Build bundles**

```powershell
python scripts/build_transductive_bundles.py `
  --final-anndata <verified-final-anndata.h5ad> `
  --mapping-tsv config/heart-celltype-map-v1.tsv `
  --output-dir artifacts/transductive-formal-v74 `
  --expected-sha256 20cf807fcaa5e8ed9ac65a28d50e781c82c9c48cdac9b7a1820dcf74bdf5143f `
  --species-column species `
  --label-column ref_labels `
  --representation-key macrogenes `
  --expected-cells 4606 `
  --expected-dimensions 1000
```

Expected:

- six directions;
- 18 NPZ bundles total: exact/coarse/fine for each direction;
- no duplicate prefixed barcode;
- all source and output hashes recorded.

- [ ] **Step 3: Run evaluation**

```powershell
python scripts/run_transductive_formal_v74.py `
  --bundle-dir artifacts/transductive-formal-v74 `
  --output-dir artifacts/transductive-formal-v74/results `
  --k 15
```

Expected:

- 18 result JSON files and one result index;
- every result contains per-cell predictions, neighbor barcodes, exclusion audit, exact/mapped metrics, F1, coverage, abstention, and confusion matrix;
- no query/reference barcode overlap;
- the six duplicate raw barcodes disappear after correct species namespacing or the build aborts and reports their identities.

- [ ] **Step 4: Create evidence report**

Create `docs/transductive-formal-v74-evidence-20260928.md` with:

1. source file SHA and reader arguments;
2. species/barcode namespace audit;
3. exact/coarse/fine six-direction metric table;
4. unmapped coverage per direction;
5. comparison to old v72/v74b numbers and explanation of any differences;
6. explicit limitation paragraph:

```text
These are formal re-evaluations of the existing v71 Final AnnData. Training and evaluation use the same cells and target labels entered the SATURN training command path; therefore the results remain transductive/in-sample and are not held-out generalization performance.
```

Do not update `config/eval-manifest-v73.json` to confirmed and do not call the result a benchmark.

## Task 6: Final Review Handoff

**Files:**

- Modify only files created by Tasks 1-5 plus `docs/audit-completion-matrix-20260926.md`.

- [ ] **Step 1: Run full verification**

```powershell
python -m unittest discover -s tests -v
python scripts/validate_eval_manifest.py
python scripts/build_transductive_bundles.py --help
python scripts/run_transductive_formal_v74.py --help
git diff --check
git status --short
```

- [ ] **Step 2: Review boundaries**

Confirm all statements:

```text
evaluation_layer=obsm/macrogenes confirmed
v73 evidence_status=pending
v74 is transductive formal reassessment
not inductive
not held-out benchmark
no DCS task submitted
no credentials read or persisted
no unrelated dirty files touched
```

- [ ] **Step 3: Report to Codex/user**

Return a compact handoff containing changed files, test counts, real-data blocker if applicable, artifact paths if run, and any accidental deviation. Do not commit or push.

## Optional Future DCS Extraction Task

Only if the Final AnnData cannot be downloaded through the existing UI and the user gives explicit new approval, design a separate read-only extraction task. It must:

1. verify the source SHA-256 in-container;
2. write outputs under the persistent `online/` directory rather than only `/data/work/`;
3. write a small `READY.json` plus SHA-256 manifest before any large file;
4. avoid printing credentials or full JSON payloads;
5. remain a separate v97 evidence task, not a SATURN rerun and not authorization for inductive training.

That task is outside this plan's execution authority.

## Plan Self-Review

- Spec coverage: covers partial-evidence validation, mapping namespace, direction-specific roles, explicit bundles, six-direction exact/coarse/fine evaluation, real-data gate, evidence report, and review handoff.
- Placeholder scan: no TBD/TODO or “implement later” steps remain.
- Type consistency: NPZ key names match the existing evaluator; direction labels consistently use `hu->mo` style; label levels consistently use `exact`, `coarse`, and `fine`.
- Safety: v73 remains pending, v74 cannot be confused with inductive benchmark, and no cloud action is authorized.
