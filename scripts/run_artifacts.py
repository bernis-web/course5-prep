"""Validate the required, auditable artifacts for one benchmark run."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REQUIRED_ARTIFACTS = (
    "input_manifest.tsv",
    "ortholog_manifest.json",
    "parameters.json",
    "package_versions.txt",
    "stdout_stderr.log",
    "metrics.json",
    "resource_usage.json",
    "failure_reason.txt",
)


class ArtifactContractError(ValueError):
    """Raised when a run directory cannot be audited reproducibly."""


def validate_run_artifacts(root: Path, run_status: str = "success") -> dict[str, Any]:
    """Validate required files without reading or modifying their contents."""
    if run_status not in {"success", "failed"}:
        raise ArtifactContractError("run_status must be 'success' or 'failed'")
    if not root.is_dir():
        raise FileNotFoundError(root)

    required = list(REQUIRED_ARTIFACTS)
    if run_status == "success":
        required.remove("failure_reason.txt")
    missing = [name for name in required if not (root / name).is_file()]
    empty = [name for name in required if (root / name).is_file() and (root / name).stat().st_size == 0]
    reason_path = root / "failure_reason.txt"
    failure_reason_required = run_status == "failed"
    if failure_reason_required and (not reason_path.is_file() or reason_path.stat().st_size == 0):
        if "failure_reason.txt" not in missing and "failure_reason.txt" not in empty:
            missing.append("failure_reason.txt")
    if missing or empty:
        raise ArtifactContractError(
            json.dumps({"missing": missing, "empty": empty}, ensure_ascii=True)
        )
    return {
        "root": str(root.resolve()),
        "run_status": run_status,
        "required": required,
        "missing": [],
        "empty": [],
        "failure_reason_required": failure_reason_required,
        "side_effects": [],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--status", choices=("success", "failed"), default="success")
    args = parser.parse_args()
    try:
        result = validate_run_artifacts(args.run_dir, args.status)
    except (ArtifactContractError, FileNotFoundError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, ensure_ascii=True, indent=2))
        raise SystemExit(2) from exc
    print(json.dumps({"valid": True, **result}, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
