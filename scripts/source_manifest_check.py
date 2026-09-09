"""Verify course source files against a checked-in size and SHA-256 manifest."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "docs" / "source-file-manifest.tsv"
REQUIRED_COLUMNS = ("filename", "format", "bytes", "sha256", "checked_at")


class SourceManifestError(ValueError):
    """Raised when a source manifest cannot be verified safely."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _read_manifest(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames is None or set(REQUIRED_COLUMNS) - set(reader.fieldnames):
            raise SourceManifestError("source manifest is missing required columns")
        rows = [dict(row) for row in reader]
    if not rows:
        raise SourceManifestError("source manifest contains no files")
    return rows


def verify_manifest(source_root: Path, manifest: Path = DEFAULT_MANIFEST) -> dict[str, Any]:
    """Return file-level hash status without exposing source contents."""
    if not source_root.is_dir():
        raise FileNotFoundError(source_root)

    results: list[dict[str, Any]] = []
    for index, row in enumerate(_read_manifest(manifest), start=2):
        filename = str(row.get("filename", "")).strip()
        if not filename or Path(filename).name != filename:
            raise SourceManifestError(f"row {index} filename must be a direct child name")
        try:
            expected_bytes = int(str(row.get("bytes", "")).strip())
        except ValueError as exc:
            raise SourceManifestError(f"row {index} bytes must be an integer") from exc
        expected_sha256 = str(row.get("sha256", "")).strip().upper()
        if len(expected_sha256) != 64 or any(char not in "0123456789ABCDEF" for char in expected_sha256):
            raise SourceManifestError(f"row {index} sha256 must be 64 hexadecimal characters")

        path = source_root / filename
        if not path.is_file():
            results.append(
                {
                    "filename": filename,
                    "expected_bytes": expected_bytes,
                    "expected_sha256": expected_sha256,
                    "status": "missing",
                }
            )
            continue

        actual_bytes = path.stat().st_size
        actual_sha256 = _sha256(path)
        status = "ok" if actual_bytes == expected_bytes and actual_sha256 == expected_sha256 else "mismatch"
        results.append(
            {
                "filename": filename,
                "expected_bytes": expected_bytes,
                "actual_bytes": actual_bytes,
                "expected_sha256": expected_sha256,
                "actual_sha256": actual_sha256,
                "status": status,
            }
        )

    return {
        "valid": all(item["status"] == "ok" for item in results),
        "scope": "source_files",
        "manifest_name": manifest.name,
        "n_files": len(results),
        "files": results,
        "side_effects": [],
    }


def write_report(report: dict[str, Any], output: Path) -> str:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=True, indent=2), encoding="utf-8")
    return str(output)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_root", type=Path)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        report = verify_manifest(args.source_root, args.manifest)
    except (OSError, SourceManifestError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, ensure_ascii=True, indent=2))
        raise SystemExit(2) from exc
    if args.output is None:
        print(json.dumps(report, ensure_ascii=True, indent=2))
    else:
        print(json.dumps({"report_path": write_report(report, args.output)}, ensure_ascii=True))
    if not report["valid"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
