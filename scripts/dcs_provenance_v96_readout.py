#!/usr/bin/env python3
"""Minimal read-only readout for the v95 provenance collector.

The script reads only the three v95 output files. It writes its own v96 JSON,
error log, and nothing else. It never deletes, moves, or rewrites prior files.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(os.environ.get("G5_V96_ROOT", "/data/work"))
OUT = ROOT / "g5-provenance-v96-out.json"
ERR = ROOT / "g5-provenance-v96-err.log"
SELF = Path(__file__).resolve()
COMMAND_FILE = ROOT / "g5-provenance-v96-command.txt"
TARGETS = (
    "g5-provenance-v95-out.json",
    "g5-provenance-v95-err.log",
    "g5-provenance-v95-command.txt",
)
MAX_JSON_BYTES = 32 * 1024 * 1024
MAX_TEXT_BYTES = 2 * 1024 * 1024
MAX_FILE_ROWS = 250
MAX_KEY_LINES = 120
SENSITIVE_WORDS = ("token", "cookie", "password", "authorization", "bearer")
KEY_LINE_TOKENS = (
    "in_label_col",
    "ref_label_col",
    "num_macrogenes",
    "unfreeze_macrogenes",
    "use_ref_labels",
    "random_state",
    "seed",
    "final anndata",
    "final triplets",
    "final epoch",
    "macrogenes",
    "h5ad",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str | None:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_text(path: Path) -> str | None:
    if path.stat().st_size > MAX_TEXT_BYTES:
        return None
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def redact(line: str) -> str:
    if any(word in line.lower() for word in SENSITIVE_WORDS):
        return "[REDACTED_SENSITIVE_LINE]"
    return line[:1000]


def target_record(name: str) -> dict[str, Any]:
    path = ROOT / name
    record: dict[str, Any] = {
        "name": name,
        "path": str(path),
        "exists": path.exists(),
    }
    if not path.exists() or not path.is_file():
        return record
    stat = path.stat()
    record.update(
        {
            "size_bytes": stat.st_size,
            "mtime_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
            "sha256": sha256_file(path),
        }
    )
    text = safe_text(path)
    if text is not None:
        lines = text.splitlines()
        record["line_count"] = len(lines)
        if name != "g5-provenance-v95-out.json":
            record["first_20_lines"] = [redact(line) for line in lines[:20]]
            record["last_20_lines"] = [redact(line) for line in lines[-20:]]
    return record


def compact_file_rows(data: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in data.get("files", []):
        rows.append(
            {
                "relative_path": item.get("relative_path"),
                "size_bytes": item.get("size_bytes"),
                "sha256": item.get("sha256"),
            }
        )
        if len(rows) >= MAX_FILE_ROWS:
            break
    return rows


def key_lines(data: dict[str, Any]) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for excerpt in data.get("text_and_log_excerpts", []):
        source = excerpt.get("path") or excerpt.get("relative_path")
        candidates = list(excerpt.get("matches", []))
        candidates.extend(excerpt.get("first_30_lines", []))
        candidates.extend(excerpt.get("last_50_lines", []))
        for candidate in candidates:
            line = str(candidate.get("line", ""))
            if not any(token in line.lower() for token in KEY_LINE_TOKENS):
                continue
            selected.append(
                {
                    "source": source,
                    "line_number": candidate.get("line_number"),
                    "line": redact(line),
                }
            )
            if len(selected) >= MAX_KEY_LINES:
                return selected
    return selected


def h5ad_rows(data: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in data.get("h5ad_metadata", []):
        rows.append(
            {
                "path": item.get("path"),
                "sha256": item.get("sha256"),
                "shape": item.get("shape"),
                "obs_index_name": item.get("obs_index_name"),
                "duplicate_barcode_count": item.get("duplicate_barcode_count"),
                "first_barcodes": item.get("first_barcodes", [])[:5],
                "error": item.get("error"),
            }
        )
    return rows


def summarize_v95_json(path: Path) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "path": str(path),
        "json_parse_attempted": False,
        "json_valid": False,
    }
    if not path.is_file() or path.stat().st_size > MAX_JSON_BYTES:
        return summary
    summary["json_parse_attempted"] = True
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        summary["json_error"] = f"{type(exc).__name__}: {exc}"
        return summary
    if not isinstance(data, dict):
        summary["json_error"] = "top_level_is_not_object"
        return summary
    summary.update(
        {
            "json_valid": True,
            "schema_version": data.get("schema_version"),
            "generated_at_utc": data.get("generated_at_utc"),
            "purpose": data.get("purpose"),
            "self_record": data.get("self_record"),
            "scope": data.get("scope"),
            "negative_findings": data.get("negative_findings"),
            "top_level_keys": sorted(data.keys()),
            "file_entry_count": len(data.get("files", [])),
            "excerpt_count": len(data.get("text_and_log_excerpts", [])),
            "h5ad_metadata_count": len(data.get("h5ad_metadata", [])),
            "compact_file_rows": compact_file_rows(data),
            "key_lines": key_lines(data),
            "h5ad_rows": h5ad_rows(data),
        }
    )
    return summary


def main() -> int:
    report = {
        "schema_version": "g5-provenance-v96-readout-readonly/1",
        "generated_at_utc": utc_now(),
        "purpose": "Read only v95 out/err/command and emit a compact provenance summary.",
        "self_record": {
            "script_path": str(SELF),
            "script_sha256": sha256_file(SELF),
            "command_file_path": str(COMMAND_FILE),
            "command_file_sha256": (
                sha256_file(COMMAND_FILE) if COMMAND_FILE.is_file() else "missing"
            ),
            "python_version": sys.version,
            "platform": platform.platform(),
            "cwd": os.getcwd(),
            "root": str(ROOT),
            "declared_mode": "readonly",
            "prior_artifacts_modified": False,
        },
        "targets": [target_record(name) for name in TARGETS],
        "v95_json_summary": summarize_v95_json(ROOT / TARGETS[0]),
    }
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        message = f"v96 readout fatal error: {type(exc).__name__}: {exc}\n"
        ERR.write_text(message, encoding="utf-8")
        print(message, file=sys.stderr)
        raise
