"""Validate the metadata contract before any cross-species integration run."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Iterable, Mapping, Any


REQUIRED_COLUMNS = ("cell_id", "species", "cell_type", "batch")


class InputContractError(ValueError):
    """Raised when metadata cannot support a reproducible benchmark."""


def validate_metadata(rows: Iterable[Mapping[str, Any]], min_species: int = 2) -> dict[str, Any]:
    """Validate rows and return deterministic counts for a benchmark manifest."""
    if min_species < 1:
        raise ValueError("min_species must be positive")
    materialized = [dict(row) for row in rows]
    if not materialized:
        raise InputContractError("metadata contains no rows")
    missing_columns = sorted(set(REQUIRED_COLUMNS) - set(materialized[0]))
    if missing_columns:
        raise InputContractError(f"missing required columns: {', '.join(missing_columns)}")

    seen_ids: set[str] = set()
    normalized: list[dict[str, str]] = []
    for index, row in enumerate(materialized, start=2):
        values = {column: str(row.get(column, "")).strip() for column in REQUIRED_COLUMNS}
        blank = [column for column, value in values.items() if not value]
        if blank:
            raise InputContractError(f"row {index} has blank fields: {', '.join(blank)}")
        if values["cell_id"] in seen_ids:
            raise InputContractError(f"duplicate cell_id at row {index}: {values['cell_id']}")
        seen_ids.add(values["cell_id"])
        normalized.append(values)

    species = sorted({row["species"] for row in normalized})
    if len(species) < min_species:
        raise InputContractError(f"need at least {min_species} species, found {len(species)}")
    labels = sorted({row["cell_type"] for row in normalized})
    batches = sorted({row["batch"] for row in normalized})
    return {
        "n_cells": len(normalized),
        "n_species": len(species),
        "species": species,
        "labels": labels,
        "batches": batches,
        "cells_per_species": dict(sorted(Counter(row["species"] for row in normalized).items())),
        "cells_per_label": dict(sorted(Counter(row["cell_type"] for row in normalized).items())),
        "cells_per_batch": dict(sorted(Counter(row["batch"] for row in normalized).items())),
        "required_columns": list(REQUIRED_COLUMNS),
    }


def read_metadata(path: Path) -> list[dict[str, str]]:
    suffix = path.suffix.lower()
    if suffix not in {".csv", ".tsv"}:
        raise InputContractError("metadata input must be .csv or .tsv")
    delimiter = "," if suffix == ".csv" else "\t"
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=delimiter)
        if reader.fieldnames is None:
            raise InputContractError("metadata has no header row")
        return [dict(row) for row in reader]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_metadata_manifest(source: Path, output: Path, min_species: int = 2) -> str:
    """Write a JSON manifest; this function does not modify the source file."""
    if not source.is_file():
        raise FileNotFoundError(source)
    summary = validate_metadata(read_metadata(source), min_species=min_species)
    summary.update(
        {
            "source_path": str(source.resolve()),
            "source_format": source.suffix.lower().lstrip("."),
            "source_bytes": source.stat().st_size,
            "sha256": _sha256(source),
            "side_effects": [],
        }
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, ensure_ascii=True, indent=2), encoding="utf-8")
    return str(output)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("metadata", type=Path)
    parser.add_argument("--output", type=Path, default=Path("metadata-manifest.json"))
    parser.add_argument("--min-species", type=int, default=2)
    args = parser.parse_args()
    print(json.dumps({"manifest_path": write_metadata_manifest(args.metadata, args.output, args.min_species)}))


if __name__ == "__main__":
    main()
