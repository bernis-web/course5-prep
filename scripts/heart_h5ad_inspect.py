"""Inspect heart h5ad files and emit a JSON evidence report.

The inspector is read-only: it hashes each input from the raw byte stream,
then uses anndata (when installed) to summarise dimensions, dtypes, metadata
columns, and cardiomyocyte/fibroblast annotation coverage. Files are processed
independently so one unreadable input never aborts the whole report.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

CM_FB_PATTERN = re.compile(r"(?i)cardiomyo|fibroblast|myofibroblast")
VALUE_COUNTS_LIMIT = 50
ANNDATA_MISSING_ERROR = "anndata not installed"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _import_anndata():
    """Return the anndata module, or None when it is not importable."""
    try:
        return importlib.import_module("anndata")
    except ImportError:
        return None


def _counts_dict(series) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value, count in series.value_counts(dropna=True).items():
        key = str(value)
        counts[key] = counts.get(key, 0) + int(count)
    return counts


def _regex_hits(series, pattern: re.Pattern) -> int:
    """Count cells whose value matches the pattern, via value-level grouping."""
    hits = 0
    for value, count in series.value_counts(dropna=True).items():
        if pattern.search(str(value)):
            hits += int(count)
    return hits


def _inspect_adata(adata) -> dict[str, Any]:
    import pandas as pd

    obs_columns: list[dict[str, Any]] = []
    cm_fb_hits: dict[str, int] = {}
    for name in adata.obs.columns:
        series = adata.obs[name]
        column: dict[str, Any] = {
            "name": str(name),
            "dtype": str(series.dtype),
            "n_unique": int(series.nunique(dropna=True)),
        }
        if column["n_unique"] <= VALUE_COUNTS_LIMIT:
            column["value_counts"] = _counts_dict(series)
        else:
            column["value_counts"] = None
        obs_columns.append(column)
        is_textlike = pd.api.types.is_object_dtype(series.dtype) or isinstance(
            series.dtype, pd.CategoricalDtype
        )
        if is_textlike:
            hits = _regex_hits(series, CM_FB_PATTERN)
            if hits:
                cm_fb_hits[str(name)] = hits

    x = adata.X
    return {
        "n_obs": int(adata.n_obs),
        "n_var": int(adata.n_vars),
        "x_dtype": str(x.dtype) if x is not None and hasattr(x, "dtype") else None,
        "layers": sorted(str(key) for key in adata.layers.keys() if key is not None),
        "obsm": sorted(str(key) for key in adata.obsm.keys()),
        "uns": sorted(str(key) for key in adata.uns.keys()),
        "obs_columns": obs_columns,
        "cm_fb_hits": cm_fb_hits,
        "var_columns": [str(name) for name in adata.var.columns],
    }


def inspect_file(path: Path, anndata_module) -> dict[str, Any]:
    """Inspect one input; hash and size are produced even without anndata."""
    record: dict[str, Any] = {"file": str(path)}
    try:
        record["sha256"] = _sha256(path)
        record["size"] = int(path.stat().st_size)
    except OSError as exc:
        record["ok"] = False
        record["error"] = f"cannot read file bytes: {exc}"
        return record
    if anndata_module is None:
        record["ok"] = False
        record["error"] = ANNDATA_MISSING_ERROR
        return record
    try:
        adata = anndata_module.read_h5ad(path)
    except Exception as exc:  # noqa: BLE001 - reader failures are recorded as evidence
        record["ok"] = False
        record["error"] = f"{type(exc).__name__}: {exc}"
        return record
    record.update(_inspect_adata(adata))
    record["ok"] = True
    return record


def build_report(paths) -> dict[str, Any]:
    anndata_module = _import_anndata()
    files = [inspect_file(path, anndata_module) for path in paths]
    return {
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "anndata_available": anndata_module is not None,
        "files": files,
    }


def write_report(report: dict[str, Any], output: Path) -> str:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(output)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", type=Path, help="h5ad files to inspect")
    parser.add_argument("--output", type=Path, required=True, help="path of the JSON evidence report")
    return parser


def main(argv=None) -> None:
    args = build_parser().parse_args(argv)
    report = build_report(args.files)
    write_report(report, args.output)
    failed = sum(1 for item in report["files"] if not item.get("ok"))
    print(
        json.dumps(
            {
                "report_path": str(args.output),
                "n_files": len(report["files"]),
                "failed_files": failed,
            },
            ensure_ascii=False,
        )
    )
    # Missing anndata is an expected environment state (exit 0); a real reader
    # failure on any file means the evidence is incomplete (exit 2).
    if report["anndata_available"] and failed:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
