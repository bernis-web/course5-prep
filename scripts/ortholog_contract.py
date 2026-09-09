"""Validate a shared one-to-one ortholog table before integration runs."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping


REQUIRED_COLUMNS = ("species_a", "gene_a", "species_b", "gene_b")
ROOT = Path(__file__).resolve().parents[1]


class OrthologContractError(ValueError):
    """Raised when an ortholog table is not one-to-one and auditable."""


def _canonical_row(row: Mapping[str, Any], index: int) -> dict[str, str]:
    values = {column: str(row.get(column, "")).strip() for column in REQUIRED_COLUMNS}
    blank = [column for column, value in values.items() if not value]
    if blank:
        raise OrthologContractError(f"row {index} has blank fields: {', '.join(blank)}")
    if values["species_a"] == values["species_b"]:
        raise OrthologContractError(f"row {index} maps a species to itself")
    if values["species_a"] > values["species_b"]:
        values = {
            "species_a": values["species_b"],
            "gene_a": values["gene_b"],
            "species_b": values["species_a"],
            "gene_b": values["gene_a"],
        }
    return values


def validate_orthologs(rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """Validate pairwise one-to-one mappings and return deterministic counts."""
    materialized = [dict(row) for row in rows]
    if not materialized:
        raise OrthologContractError("ortholog table contains no rows")
    missing_columns = sorted(set(REQUIRED_COLUMNS) - set(materialized[0]))
    if missing_columns:
        raise OrthologContractError(f"missing required columns: {', '.join(missing_columns)}")

    seen_rows: set[tuple[str, str, str, str]] = set()
    pair_gene_a: defaultdict[str, set[str]] = defaultdict(set)
    pair_gene_b: defaultdict[str, set[str]] = defaultdict(set)
    normalized: list[dict[str, str]] = []
    for index, row in enumerate(materialized, start=2):
        values = _canonical_row(row, index)
        pair_name = f"{values['species_a']}--{values['species_b']}"
        identity = (pair_name, values["gene_a"], values["gene_b"], values["species_a"])
        if identity in seen_rows:
            raise OrthologContractError(f"duplicate ortholog row at row {index}")
        seen_rows.add(identity)
        if values["gene_a"] in pair_gene_a[pair_name]:
            raise OrthologContractError(
                f"gene_a maps more than once in {pair_name}: {values['gene_a']}"
            )
        if values["gene_b"] in pair_gene_b[pair_name]:
            raise OrthologContractError(
                f"gene_b maps more than once in {pair_name}: {values['gene_b']}"
            )
        pair_gene_a[pair_name].add(values["gene_a"])
        pair_gene_b[pair_name].add(values["gene_b"])
        normalized.append(values)

    species = sorted({row[column] for row in normalized for column in ("species_a", "species_b")})
    species_pairs = sorted({f"{row['species_a']}--{row['species_b']}" for row in normalized})
    return {
        "n_pairs": len(normalized),
        "n_species": len(species),
        "species": species,
        "species_pairs": species_pairs,
        "pairs_per_species_pair": {
            pair: len(pair_gene_a[pair]) for pair in species_pairs
        },
        "required_columns": list(REQUIRED_COLUMNS),
    }


def read_orthologs(path: Path) -> list[dict[str, str]]:
    suffix = path.suffix.lower()
    if suffix not in {".csv", ".tsv"}:
        raise OrthologContractError("ortholog input must be .csv or .tsv")
    delimiter = "," if suffix == ".csv" else "\t"
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=delimiter)
        if reader.fieldnames is None:
            raise OrthologContractError("ortholog table has no header row")
        return [dict(row) for row in reader]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_ortholog_manifest(source: Path, output: Path) -> str:
    """Write a JSON manifest without changing the source table."""
    if not source.is_file():
        raise FileNotFoundError(source)
    summary = validate_orthologs(read_orthologs(source))
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
    parser.add_argument("orthologs", type=Path)
    parser.add_argument("--output", type=Path, default=Path("ortholog_manifest.json"))
    args = parser.parse_args()
    print(json.dumps({"manifest_path": write_ortholog_manifest(args.orthologs, args.output)}))


if __name__ == "__main__":
    main()
