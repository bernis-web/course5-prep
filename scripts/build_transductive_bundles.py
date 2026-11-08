"""Build direction-explicit NPZ bundles for the v74 transductive-formal re-evaluation.

The module separates pure contract logic (species namespaces, mapping rows,
cell validation, bundle selection) from the real-file reader so that every
contract is unit-testable without ``anndata``.  It never talks to DCS.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


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

ACTIVE_STATUS = "active"
MAPPING_LEVELS = {"coarse": "coarse_level", "fine": "fine_mapped_label"}


def canonical_species(value: str) -> str:
    """Canonicalize a species name or raise BundleBuildError."""
    key = str(value).strip().lower().replace("-", "_").replace(" ", "_")
    canonical = SPECIES_ALIASES.get(key)
    if canonical is None:
        raise BundleBuildError(f"unknown species: {value!r}")
    return canonical


def prefixed_barcode(species: str, barcode: str) -> str:
    """Prefix a raw barcode with its species namespace."""
    return f"{SPECIES_PREFIXES[canonical_species(species)]}|{str(barcode).strip()}"


def load_mapping_rows(path: Path) -> list[dict[str, str]]:
    """Load the frozen mapping TSV and validate required columns and values."""
    text = Path(path).read_text(encoding="utf-8-sig")
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        raise BundleBuildError(f"mapping file is empty: {path}")
    header = [column.strip() for column in lines[0].split("\t")]
    missing = [column for column in MAPPING_COLUMNS if column not in header]
    if missing:
        raise BundleBuildError(f"mapping file missing columns: {', '.join(missing)}")
    rows: list[dict[str, str]] = []
    for line_number, line in enumerate(lines[1:], start=2):
        values = [value.strip() for value in line.split("\t")]
        if len(values) < len(header):
            values += [""] * (len(header) - len(values))
        row = dict(zip(header, values))
        for column in ("source_species", "source_label", "mapping_status"):
            if not row.get(column):
                raise BundleBuildError(
                    f"mapping row {line_number}: empty {column}"
                )
        row["source_species"] = canonical_species(row["source_species"])
        rows.append({column: row.get(column, "") for column in MAPPING_COLUMNS})
    return rows


def level_mapping(
    rows: list[dict[str, str]],
    selected_species: set[str],
    level: str,
) -> dict[str, str]:
    """Build a label mapping for the selected species at the requested level.

    Rows whose ``mapping_status`` is not active are omitted.  Raises
    BundleBuildError when one exact source label maps to different values.
    """
    if level not in MAPPING_LEVELS:
        raise BundleBuildError(f"unknown mapping level: {level!r}")
    value_column = MAPPING_LEVELS[level]
    mapping: dict[str, str] = {}
    sources: dict[str, set[str]] = {}
    for row in rows:
        if row.get("mapping_status") != ACTIVE_STATUS:
            continue
        species = canonical_species(row["source_species"])
        if species not in selected_species:
            continue
        label = row["source_label"]
        value = row[value_column]
        if not value:
            continue
        previous = mapping.get(label)
        if previous is not None and previous != value:
            raise BundleBuildError(
                f"conflicting mapping for {label!r}: {previous!r} vs {value!r}"
            )
        mapping[label] = value
        sources.setdefault(label, set()).add(species)
    return mapping


@dataclass(frozen=True)
class CellRecord:
    barcode: str
    species: str
    label_exact: str
    row_index: int


def validate_cells(
    species: list[str],
    barcodes: list[str],
    labels: list[str],
) -> list[CellRecord]:
    """Validate parallel cell arrays and return prefixed CellRecords."""
    if not len(species) == len(barcodes) == len(labels):
        raise BundleBuildError("species/barcodes/labels length mismatch")
    if len(species) == 0:
        raise BundleBuildError("no cells supplied")
    records: list[CellRecord] = []
    seen: dict[str, str] = {}
    for index, (raw_species, raw_barcode, label) in enumerate(zip(species, barcodes, labels)):
        species_canonical = canonical_species(raw_species)
        barcode_raw = str(raw_barcode).strip()
        if not barcode_raw:
            raise BundleBuildError(f"row {index}: empty barcode")
        if not str(label).strip():
            raise BundleBuildError(f"row {index}: empty label")
        prefixed = prefixed_barcode(species_canonical, barcode_raw)
        if prefixed in seen:
            raise BundleBuildError(
                f"duplicate prefixed barcode {prefixed!r} at rows {seen[prefixed]} and {index}"
            )
        seen[prefixed] = str(index)
        records.append(
            CellRecord(
                barcode=prefixed,
                species=species_canonical,
                label_exact=str(label).strip(),
                row_index=index,
            )
        )
    return records


def safe_file_stem(direction_key: str) -> str:
    """Windows-safe file stem for a direction key (hu->mo -> hu-mo)."""
    return direction_key.replace(">", "-")


def direction_key(reference_species: str, query_species: str) -> str:
    return f"{SPECIES_PREFIXES[reference_species]}->{SPECIES_PREFIXES[query_species]}"


def direction_bundles(
    cells: list[CellRecord],
    embedding: np.ndarray,
    mapping_rows: list[dict[str, str]],
) -> dict[str, dict[str, Any]]:
    """Select exact/coarse/fine cells per ordered species pair.

    Returns one description per ordered pair.  Exact bundles keep all cells;
    coarse/fine bundles keep only cells whose ``(species, label_exact)`` pair
    has an active mapping at that level.  Unmapped counts are reported.
    """
    embedding = np.asarray(embedding)
    if embedding.ndim != 2 or embedding.shape[0] != len(cells):
        raise BundleBuildError(
            f"embedding shape {embedding.shape} does not match {len(cells)} cells"
        )
    species_set = {cell.species for cell in cells}
    level_maps = {
        level: level_mapping(mapping_rows, species_set, level)
        for level in MAPPING_LEVELS
    }

    def active(cell: CellRecord, level: str) -> bool:
        return (
            cell.label_exact in level_maps[level]
            and cell.species in {
                canonical_species(row["source_species"])
                for row in mapping_rows
                if row.get("mapping_status") == ACTIVE_STATUS
            }
        )

    descriptions: dict[str, dict[str, Any]] = {}
    for reference in sorted(species_set):
        for query in sorted(species_set):
            if reference == query:
                continue
            ref_cells = [c for c in cells if c.species == reference]
            qry_cells = [c for c in cells if c.species == query]
            key = direction_key(reference, query)
            description: dict[str, Any] = {
                "direction": key,
                "reference_species": reference,
                "query_species": query,
            }
            for level in ("exact", "coarse", "fine"):
                if level == "exact":
                    selected = ref_cells + qry_cells
                    mapping_out: dict[str, str] = {}
                    n_unmapped_ref = 0
                    n_unmapped_qry = 0
                else:
                    level_map = level_maps[level]
                    mapping_out = dict(level_map)
                    selected = [
                        c for c in ref_cells + qry_cells if active(c, level)
                    ]
                    n_unmapped_ref = sum(1 for c in ref_cells if not active(c, level))
                    n_unmapped_qry = sum(1 for c in qry_cells if not active(c, level))
                description[level] = {
                    "selected_cells": [c.barcode for c in selected],
                    "n_reference": sum(1 for c in selected if c.species == reference),
                    "n_query": sum(1 for c in selected if c.species == query),
                    "n_unmapped_reference": n_unmapped_ref,
                    "n_unmapped_query": n_unmapped_qry,
                    "mapping": mapping_out,
                }
            descriptions[key] = description
    return descriptions


def _embeddings_for(cells: list[CellRecord], embedding: np.ndarray) -> np.ndarray:
    return embedding[[c.row_index for c in cells]]


def _sha256_file(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


EXPECTED_SPECIES_COUNTS = {"human": 1528, "mouse": 1535, "zebrafish": 1543}

SCOPE_STRING = (
    "transductive_formal_reassessment_of_v71_v72; not_inductive; not_held_out_benchmark"
)

ROLE_HEADER = (
    "direction\treference_species\tquery_species\tbarcode\tspecies\t"
    "query_or_reference\tlabel_exact\tmapping_status"
)


def _mapping_status_for(
    species: str, label_exact: str, mapping_rows: list[dict[str, str]]
) -> str:
    for row in mapping_rows:
        if (
            canonical_species(row["source_species"]) == species
            and row["source_label"] == label_exact
        ):
            return row.get("mapping_status", "missing_from_mapping")
    return "missing_from_mapping"


def read_and_build(
    final_anndata: Path,
    mapping_tsv: Path,
    output_dir: Path,
    expected_sha256: str,
    species_column: str = "species",
    label_column: str = "ref_labels",
    representation_key: str = "macrogenes",
    expected_cells: int = 4606,
    expected_dimensions: int = 1000,
) -> Path:
    """Read the SHA-256-verified Final AnnData and write v74 bundle artifacts."""
    import anndata  # imported only here: the contract layer stays anndata-free

    final_anndata = Path(final_anndata)
    if not final_anndata.is_file():
        raise BundleBuildError(f"final anndata not found: {final_anndata}")
    actual_sha = _sha256_file(final_anndata)
    if actual_sha != expected_sha256:
        raise BundleBuildError(
            f"final anndata SHA-256 mismatch: expected {expected_sha256}, got {actual_sha}"
        )

    adata = anndata.read_h5ad(final_anndata)
    if adata.n_obs != expected_cells:
        raise BundleBuildError(
            f"expected {expected_cells} cells, found {adata.n_obs}"
        )
    if representation_key not in adata.obsm:
        raise BundleBuildError(f"obsm[{representation_key!r}] missing from Final AnnData")
    embedding = np.asarray(adata.obsm[representation_key])
    if embedding.shape != (expected_cells, expected_dimensions):
        raise BundleBuildError(
            f"obsm[{representation_key!r}] shape {embedding.shape} != "
            f"({expected_cells}, {expected_dimensions})"
        )
    if not np.isfinite(embedding).all():
        raise BundleBuildError("embedding contains non-finite values")
    for column in (species_column, label_column):
        if column not in adata.obs.columns:
            raise BundleBuildError(f"obs[{column!r}] missing from Final AnnData")

    species_values = [str(v) for v in adata.obs[species_column]]
    label_values = [str(v) for v in adata.obs[label_column]]
    barcode_values = [str(v) for v in adata.obs_names]
    cells = validate_cells(species_values, barcode_values, label_values)

    counts: dict[str, int] = {}
    for cell in cells:
        counts[cell.species] = counts.get(cell.species, 0) + 1
    for species_key, expected_count in EXPECTED_SPECIES_COUNTS.items():
        if counts.get(species_key, 0) != expected_count:
            raise BundleBuildError(
                f"{species_key} count {counts.get(species_key, 0)} != {expected_count}"
            )

    mapping_rows = load_mapping_rows(mapping_tsv)
    mapping_sha = _sha256_file(mapping_tsv)
    descriptions = direction_bundles(cells, embedding, mapping_rows)

    output_dir = Path(output_dir)
    bundles_dir = output_dir / "bundles"
    mappings_dir = output_dir / "mappings"
    roles_dir = output_dir / "roles"
    for directory in (bundles_dir, mappings_dir, roles_dir):
        directory.mkdir(parents=True, exist_ok=True)

    output_hashes: dict[str, str] = {}
    per_direction: dict[str, Any] = {}
    cell_by_barcode = {cell.barcode: cell for cell in cells}

    for key, description in descriptions.items():
        stem = safe_file_stem(key)
        reference_species = description["reference_species"]
        query_species = description["query_species"]
        per_direction[key] = {}
        for level in ("exact", "coarse", "fine"):
            block = description[level]
            selected = set(block["selected_cells"])
            ref_cells = [
                c
                for c in cells
                if c.species == reference_species and c.barcode in selected
            ]
            qry_cells = [
                c
                for c in cells
                if c.species == query_species and c.barcode in selected
            ]
            npz_path = bundles_dir / f"{level}_{stem}.npz"
            np.savez_compressed(
                npz_path,
                reference_embeddings=embedding[
                    [c.row_index for c in ref_cells]
                ],
                query_embeddings=embedding[[c.row_index for c in qry_cells]],
                reference_barcodes=np.array([c.barcode for c in ref_cells]),
                query_barcodes=np.array([c.barcode for c in qry_cells]),
                reference_labels=np.array([c.label_exact for c in ref_cells]),
                query_labels=np.array([c.label_exact for c in qry_cells]),
            )
            output_hashes[npz_path.name] = _sha256_file(npz_path)
            mapping_path = mappings_dir / f"{level}_{stem}.json"
            mapping_path.write_text(
                json.dumps(block["mapping"], ensure_ascii=False, indent=1, sort_keys=True),
                encoding="utf-8",
            )
            output_hashes[mapping_path.name] = _sha256_file(mapping_path)
            per_direction[key][level] = {
                "n_reference": block["n_reference"],
                "n_query": block["n_query"],
                "n_unmapped_reference": block["n_unmapped_reference"],
                "n_unmapped_query": block["n_unmapped_query"],
                "bundle": f"bundles/{npz_path.name}",
                "bundle_sha256": output_hashes[npz_path.name],
            }

        role_lines = [ROLE_HEADER]
        for cell in cells:
            if cell.species not in (reference_species, query_species):
                continue
            role = "reference" if cell.species == reference_species else "query"
            role_lines.append(
                "\t".join(
                    [
                        key,
                        reference_species,
                        query_species,
                        cell.barcode,
                        cell.species,
                        role,
                        cell.label_exact,
                        _mapping_status_for(cell.species, cell.label_exact, mapping_rows),
                    ]
                )
            )
        roles_path = roles_dir / f"roles_{stem}.tsv"
        roles_path.write_text("\n".join(role_lines) + "\n", encoding="utf-8")
        output_hashes[roles_path.name] = _sha256_file(roles_path)

    build_manifest = {
        "build_version": "v74",
        "evaluation_scope": SCOPE_STRING,
        "source_path": str(final_anndata),
        "source_sha256": actual_sha,
        "source_cells": adata.n_obs,
        "representation_key": representation_key,
        "representation_dimensions": expected_dimensions,
        "species_counts": counts,
        "mapping_tsv": str(mapping_tsv),
        "mapping_sha256": mapping_sha,
        "per_direction": per_direction,
        "output_sha256": output_hashes,
    }
    manifest_path = output_dir / "build-manifest.json"
    manifest_path.write_text(
        json.dumps(build_manifest, ensure_ascii=False, indent=1, sort_keys=True),
        encoding="utf-8",
    )
    return manifest_path


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Build v74 transductive-formal evaluation bundles."
    )
    parser.add_argument("--final-anndata", type=Path, required=True)
    parser.add_argument("--mapping-tsv", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--expected-sha256", type=str, required=True)
    parser.add_argument("--species-column", type=str, default="species")
    parser.add_argument("--label-column", type=str, default="ref_labels")
    parser.add_argument("--representation-key", type=str, default="macrogenes")
    parser.add_argument("--expected-cells", type=int, default=4606)
    parser.add_argument("--expected-dimensions", type=int, default=1000)
    args = parser.parse_args()
    try:
        manifest_path = read_and_build(
            final_anndata=args.final_anndata,
            mapping_tsv=args.mapping_tsv,
            output_dir=args.output_dir,
            expected_sha256=args.expected_sha256,
            species_column=args.species_column,
            label_column=args.label_column,
            representation_key=args.representation_key,
            expected_cells=args.expected_cells,
            expected_dimensions=args.expected_dimensions,
        )
    except BundleBuildError as exc:
        print(json.dumps({"built": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        raise SystemExit(2) from exc
    print(json.dumps({"built": True, "manifest": str(manifest_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
