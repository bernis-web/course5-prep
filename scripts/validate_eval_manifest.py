"""Validate the evidence gate for the course 5 v73 evaluation manifest.

The validator is intentionally read-only.  It distinguishes a structurally
valid but incomplete ``pending`` manifest from a ``confirmed`` manifest that
is ready for the next local evaluation step.  It never changes the manifest,
the barcode table, or any cloud object.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "config" / "eval-manifest-v73.json"
DEFAULT_BARCODE_ROLES = ROOT / "config" / "barcode-roles-v73.tsv"
ALLOWED_EVIDENCE_STATUS = {"pending", "confirmed"}
ALLOWED_REPRESENTATIONS = {"X", "obsm/macrogenes"}
REQUIRED_BARCODE_COLUMNS = (
    "barcode",
    "species",
    "role",
    "query_or_reference",
    "source_file",
    "duplicate_group",
    "label_exact",
    "label_mapped",
    "mapping_status",
    "reviewer",
    "evidence_status",
)


class ManifestContractError(ValueError):
    """Raised when the manifest is malformed or weakens a safety boundary."""


def _blank(value: Any) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def _object(parent: dict[str, Any], key: str) -> dict[str, Any]:
    value = parent.get(key)
    if not isinstance(value, dict):
        raise ManifestContractError(f"{key} must be an object")
    return value


def load_manifest(path: Path = DEFAULT_MANIFEST) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ManifestContractError(f"cannot read manifest {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ManifestContractError("manifest root must be an object")
    return value


def load_barcode_roles(path: Path = DEFAULT_BARCODE_ROLES) -> list[dict[str, str]]:
    if not path.is_file():
        raise ManifestContractError(f"barcode role table not found: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        fieldnames = tuple(reader.fieldnames or ())
        missing = [column for column in REQUIRED_BARCODE_COLUMNS if column not in fieldnames]
        if missing:
            raise ManifestContractError(f"barcode role table missing columns: {', '.join(missing)}")
        return [dict(row) for row in reader]


def _validate_barcode_rows(rows: Iterable[dict[str, Any]] | None) -> dict[str, Any]:
    if rows is None:
        return {
            "n_rows": 0,
            "n_query": 0,
            "n_reference": 0,
            "duplicate_barcodes": [],
            "query_reference_intersection": [],
            "blocking_items": ["barcode_role_table_not_loaded"],
        }

    materialized = [dict(row) for row in rows]
    normalized: list[dict[str, str]] = []
    row_blockers: list[str] = []
    for index, row in enumerate(materialized, start=2):
        values = {column: str(row.get(column, "")).strip() for column in REQUIRED_BARCODE_COLUMNS}
        missing = [column for column, value in values.items() if not value]
        if missing:
            row_blockers.append(f"barcode_row_{index}_missing:{','.join(missing)}")
        if values["role"] not in {"query", "reference"}:
            row_blockers.append(f"barcode_row_{index}_invalid_role")
        normalized.append(values)

    barcode_counts = Counter(row["barcode"] for row in normalized if row["barcode"])
    duplicates = sorted(barcode for barcode, count in barcode_counts.items() if count > 1)
    query = {row["barcode"] for row in normalized if row["query_or_reference"] == "query" and row["barcode"]}
    reference = {row["barcode"] for row in normalized if row["query_or_reference"] == "reference" and row["barcode"]}
    overlap = sorted(query & reference)
    blockers = list(row_blockers)
    if not normalized:
        blockers.append("barcode_role_table_empty")
    if duplicates:
        blockers.append("duplicate_barcodes_present")
    if overlap:
        blockers.append("query_reference_barcode_overlap")
    if not query:
        blockers.append("no_query_barcodes")
    if not reference:
        blockers.append("no_reference_barcodes")
    return {
        "n_rows": len(normalized),
        "n_query": len(query),
        "n_reference": len(reference),
        "duplicate_barcodes": duplicates,
        "query_reference_intersection": overlap,
        "blocking_items": sorted(set(blockers)),
    }


def validate_eval_manifest(
    manifest: dict[str, Any], barcode_rows: Iterable[dict[str, Any]] | None = None
) -> dict[str, Any]:
    """Return a read-only validation report for a v73 manifest."""
    if manifest.get("manifest_version") != "v73":
        raise ManifestContractError("manifest_version must be v73")
    evidence_status = manifest.get("evidence_status")
    if evidence_status not in ALLOWED_EVIDENCE_STATUS:
        raise ManifestContractError("evidence_status must be pending or confirmed")

    provenance = _object(manifest, "provenance")
    if provenance.get("cloud_actions_allowed") is not False:
        raise ManifestContractError("provenance.cloud_actions_allowed must remain false")
    run = _object(manifest, "run")
    datasets = manifest.get("datasets")
    if not isinstance(datasets, list) or not datasets:
        raise ManifestContractError("datasets must be a non-empty list")
    representation = _object(manifest, "representation")
    allowed = set(representation.get("allowed_values", []))
    if not ALLOWED_REPRESENTATIONS.issubset(allowed):
        raise ManifestContractError("representation.allowed_values must include X and obsm/macrogenes")
    labels = _object(manifest, "labels")
    training = _object(manifest, "training_parameters")
    protocol = _object(manifest, "evaluation_protocol")
    transductive = _object(protocol, "transductive")
    inductive = _object(protocol, "inductive")

    barcode_audit = _validate_barcode_rows(barcode_rows)
    blockers: list[str] = []
    warnings: list[str] = []

    if evidence_status == "pending":
        blockers.append("evidence_status_pending")
        for key in ("dcs_task_id", "original_command", "complete_log_path", "input_manifest_path"):
            if not _blank(run.get(key)):
                raise ManifestContractError(f"pending manifest cannot contain verified-looking run.{key}")
            blockers.append(f"run.{key}")
        if training.get("use_ref_labels") != "pending_from_original_command":
            raise ManifestContractError("pending manifest must keep training_parameters.use_ref_labels pending")
        if training.get("unfreeze_macrogenes") != "pending_from_original_command":
            raise ManifestContractError("pending manifest must keep training_parameters.unfreeze_macrogenes pending")
        if training.get("seed") != "pending_from_original_command":
            raise ManifestContractError("pending manifest must keep training_parameters.seed pending")
        if labels.get("reviewer") != "pending_human_signoff":
            raise ManifestContractError("pending manifest must keep labels.reviewer pending")
        blockers.append("labels.reviewer")
        if representation.get("evaluation_layer") not in ALLOWED_REPRESENTATIONS:
            blockers.append("representation.evaluation_layer")
        blockers.append("training_parameters.original_command_flags")
    else:
        required_run = ("dcs_task_id", "original_command", "complete_log_path", "input_manifest_path")
        for key in required_run:
            if _blank(run.get(key)):
                blockers.append(f"run.{key}")
        if _blank(labels.get("reviewer")) or labels.get("reviewer") == "pending_human_signoff":
            blockers.append("labels.reviewer")
        if representation.get("evaluation_layer") not in ALLOWED_REPRESENTATIONS:
            blockers.append("representation.evaluation_layer")
        for key in ("use_ref_labels", "unfreeze_macrogenes", "seed"):
            if _blank(training.get(key)) or str(training.get(key)).startswith("pending"):
                blockers.append(f"training_parameters.{key}")
        if transductive.get("status") == "pending_barcode_and_training_log_audit":
            blockers.append("evaluation_protocol.transductive.status")

    for index, dataset in enumerate(datasets):
        if not isinstance(dataset, dict):
            raise ManifestContractError(f"datasets[{index}] must be an object")
        if _blank(dataset.get("species")):
            raise ManifestContractError(f"datasets[{index}].species is required")
        if evidence_status == "confirmed":
            for key in ("input_path", "input_sha256", "final_anndata_path", "final_anndata_sha256", "barcode_list_path", "barcode_sha256", "label_column", "batch_column"):
                if _blank(dataset.get(key)):
                    blockers.append(f"datasets[{index}].{key}")
            if dataset.get("query_or_reference") not in {"query", "reference"}:
                blockers.append(f"datasets[{index}].query_or_reference")
        else:
            if dataset.get("role") != "pending" or dataset.get("query_or_reference") != "pending":
                raise ManifestContractError(f"pending datasets[{index}] must keep roles pending")

    blockers.extend(barcode_audit["blocking_items"])
    if barcode_rows is None:
        warnings.append("barcode role table was not supplied")
    elif not barcode_rows:
        warnings.append("barcode role table is header-only; no barcode evidence is present")

    # A confirmed manifest is only a provenance gate; it does not claim an
    # inductive benchmark has run.  That claim remains separately represented
    # by evaluation_protocol.inductive.status.
    return {
        "valid": True,
        "evidence_status": evidence_status,
        "ready_for_confirmation": not blockers,
        "blocking_items": sorted(set(blockers)),
        "warnings": warnings,
        "barcode_audit": barcode_audit,
        "side_effects": [],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--barcode-roles", type=Path, default=DEFAULT_BARCODE_ROLES)
    args = parser.parse_args()
    try:
        result = validate_eval_manifest(load_manifest(args.manifest), load_barcode_roles(args.barcode_roles))
    except (ManifestContractError, FileNotFoundError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        raise SystemExit(2) from exc
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
