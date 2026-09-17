"""Check whether course 5 has enough confirmed information to start a run."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PREFLIGHT = ROOT / "config" / "startup-preflight.json"
REQUIRED_TOP_LEVEL = (
    "heart_data_path",
    "heart_file_format",
    "heart_metadata_fields",
    "heart_allowed_subsets",
    "lbspa_snRNA_path",
    "lbspa_spatial_policy",
    "image_recommendation",
    "image_versions",
    "kbet_implementation",
    "kbet_version",
    "readonly_sample_command",
)
REQUIRED_METADATA_FIELDS = ("species", "cell_type", "batch", "gold_label")
REQUIRED_METHODS = ("SATURN", "SAMap", "scVI")

PHASES = ("heart_pilot", "lbspa_followup")
DEFAULT_PHASE = "heart_pilot"


class PreflightError(ValueError):
    """Raised when the startup preflight record is malformed."""


def load_preflight(path: Path | None = None) -> dict[str, Any]:
    source = path or DEFAULT_PREFLIGHT
    if not source.is_file():
        raise FileNotFoundError(source)
    try:
        record = json.loads(source.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PreflightError(f"invalid JSON in {source}: {exc}") from exc
    if not isinstance(record, dict):
        raise PreflightError("startup preflight must be an object")
    return record


def _missing_value(value: Any) -> bool:
    return value is None or (isinstance(value, str) and not value.strip()) or value == []


def _required_top_level(phase: str) -> tuple[str, ...]:
    # heart_pilot keeps every HEART check; the deferred LBSPA snRNA path only
    # gates the lbspa_followup phase.
    if phase == "heart_pilot":
        return tuple(key for key in REQUIRED_TOP_LEVEL if key != "lbspa_snRNA_path")
    return REQUIRED_TOP_LEVEL


def validate_preflight(
    record: dict[str, Any], phase: str = DEFAULT_PHASE
) -> dict[str, Any]:
    """Return blockers; this function never checks remote paths or starts work."""
    if phase not in PHASES:
        raise PreflightError(f"phase must be one of {PHASES}, got {phase!r}")
    if record.get("approval_status") not in {"pending", "confirmed"}:
        raise PreflightError("approval_status must be 'pending' or 'confirmed'")
    blockers: list[str] = []
    if record.get("approval_status") != "confirmed":
        blockers.append("approval_status")
    for key in _required_top_level(phase):
        if _missing_value(record.get(key)):
            blockers.append(key)

    metadata = record.get("heart_metadata_fields")
    if not isinstance(metadata, dict):
        if "heart_metadata_fields" not in blockers:
            blockers.append("heart_metadata_fields")
    else:
        for field in REQUIRED_METADATA_FIELDS:
            if _missing_value(metadata.get(field)):
                blockers.append(f"heart_metadata_fields.{field}")

    versions = record.get("image_versions")
    if not isinstance(versions, dict):
        if "image_versions" not in blockers:
            blockers.append("image_versions")
    else:
        for method in REQUIRED_METHODS:
            if _missing_value(versions.get(method)):
                blockers.append(f"image_versions.{method}")

    evidence = record.get("evidence")
    if not isinstance(evidence, dict) or _missing_value(evidence.get("course_admin_reply")):
        blockers.append("evidence.course_admin_reply")
    if not isinstance(evidence, dict) or _missing_value(evidence.get("recorded_at")):
        blockers.append("evidence.recorded_at")
    if phase == "lbspa_followup":
        # The scRNA conclusion is the LBSPA activation gate; it stays empty in
        # the config until a real conclusion is recorded and must not be faked.
        if not isinstance(evidence, dict) or _missing_value(evidence.get("scrna_conclusion")):
            blockers.append("evidence.scrna_conclusion")

    # Preserve order while removing duplicate blockers from nested checks.
    unique_blockers = list(dict.fromkeys(blockers))
    return {
        "ready_for_execution": not unique_blockers,
        "approval_status": record.get("approval_status"),
        "target_phase": phase,
        "blocking_items": unique_blockers,
        "required_methods": list(REQUIRED_METHODS),
        "side_effects": [],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preflight", type=Path, default=DEFAULT_PREFLIGHT)
    parser.add_argument("--phase", default=DEFAULT_PHASE)
    args = parser.parse_args()
    try:
        result = validate_preflight(load_preflight(args.preflight), phase=args.phase)
    except (PreflightError, FileNotFoundError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, ensure_ascii=True, indent=2))
        raise SystemExit(2) from exc
    print(json.dumps({"valid": True, **result}, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
