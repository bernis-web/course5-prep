#!/usr/bin/env python3
"""Read-only provenance collector for SATURN v71/v72 artifacts on DCS.

The collector writes only its own v95 output files under /data/work. It never
deletes, moves, or rewrites prior artifacts.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path("/data/work")
OUT = ROOT / "g5-provenance-v95-out.json"
ERR = ROOT / "g5-provenance-v95-err.log"
SELF = Path(__file__).resolve()
COMMAND_FILE = ROOT / "g5-provenance-v95-command.txt"

TOKENS = (
    "g5-saturn-3s-hvg-v71",
    "g5-eval-v72",
    "2102857229180948482",
    "2102886857156694017",
    "prep_real_v60",
    "prep_real",
    "samap3_v91",
    "eval_final",
    "saturn_out_real3_h",
    "saturn_out_real3",
    "saturn_out_real",
    "saturn_results",
    "finalann",
    "final_anndata",
    "epoch_scores",
    "triplets",
    "v65",
    "v66",
    "v67",
    "v71",
    "v72",
    "v91",
)
SOURCE_DIR_TOKENS = ("saturn-src",)
SOURCE_SUFFIXES = {".py", ".sh", ".js", ".json", ".txt", ".tsv", ".csv", ".md"}
SMALL_TEXT_SUFFIXES = {".py", ".sh", ".js"}
MAX_WALK_FILES = 20000
MAX_SOURCE_FILES = 500
MAX_CANDIDATES = 500
MAX_HASH_BYTES = 2 * 1024 * 1024 * 1024


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> dict[str, Any]:
    stat = path.stat()
    item: dict[str, Any] = {
        "path": str(path),
        "relative_path": path.relative_to(ROOT).as_posix(),
        "size_bytes": stat.st_size,
        "mtime_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
    }
    if stat.st_size <= MAX_HASH_BYTES:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        item["sha256"] = digest.hexdigest()
    else:
        item["sha256"] = "skipped_size_gt_2gb"
    return item


def pruned_walk() -> list[Path]:
    files: list[Path] = []
    if not ROOT.exists():
        return files
    for current, dirs, names in os.walk(ROOT):
        rel = Path(current).relative_to(ROOT)
        dirs[:] = sorted(
            d
            for d in dirs
            if d not in {".git", "__pycache__", ".ipynb_checkpoints", ".cache", ".venv", "venv"}
            and not d.startswith("pylibs")
        )
        for name in sorted(names):
            files.append(Path(current) / name)
            if len(files) >= MAX_WALK_FILES:
                return files
        if len(rel.parts) >= 6:
            dirs[:] = []
    return files


def is_source_tree_file(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix().lower()
    return any(token in rel for token in SOURCE_DIR_TOKENS) and path.suffix.lower() in SOURCE_SUFFIXES


def is_candidate(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix().lower()
    name = path.name.lower()
    return any(token in rel or token in name for token in TOKENS)


def text_excerpt(path: Path) -> dict[str, Any] | None:
    suffix = path.suffix.lower()
    if suffix not in SMALL_TEXT_SUFFIXES or path.stat().st_size > 512 * 1024:
        return None
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return {"path": str(path), "error": str(exc)}
    return {
        "path": str(path),
        "size_bytes": path.stat().st_size,
        "content": text,
        "matches": [
            {"line_number": i, "line": line}
            for i, line in enumerate(text.splitlines(), 1)
            if any(
                token in line.lower()
                for token in (
                    "in_label_col",
                    "ref_label_col",
                    "num_macrogenes",
                    "unfreeze_macrogenes",
                    "use_ref_labels",
                    "random_state",
                    "seed",
                    "macrogenes",
                    "saturn",
                    "h5ad",
                )
            )
        ][:500],
    }


def log_excerpt(path: Path) -> dict[str, Any] | None:
    suffix = path.suffix.lower()
    if suffix not in {".txt", ".log", ".out", ".json", ".csv", ".tsv"}:
        return None
    size = path.stat().st_size
    if size > 2 * 1024 * 1024:
        return None
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        return {"path": str(path), "error": str(exc)}
    selected = [
        {"line_number": i, "line": line}
        for i, line in enumerate(lines, 1)
        if any(token in line.lower() for token in TOKENS)
    ][:500]
    return {
        "path": str(path),
        "size_bytes": size,
        "line_count": len(lines),
        "matched_lines": selected,
        "first_30_lines": [{"line_number": i, "line": line} for i, line in enumerate(lines[:30], 1)],
        "last_50_lines": [
            {"line_number": len(lines) - len(lines[-50:]) + i, "line": line}
            for i, line in enumerate(lines[-50:], 0)
        ],
    }


def inspect_h5ad(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {"path": str(path), "sha256": sha256_file(path)["sha256"]}
    try:
        import anndata

        adata = anndata.read_h5ad(path, backed="r")
        result["shape"] = list(adata.shape)
        result["obs_columns"] = list(adata.obs.columns)
        result["obs_index_name"] = adata.obs.index.name
        result["obsm"] = {key: list(value.shape) for key, value in adata.obsm.items()}
        result["var_columns"] = list(adata.var.columns)
        result["layers"] = list(adata.layers.keys())
        result["first_barcodes"] = [str(x) for x in adata.obs.index[:10].tolist()]
        result["duplicate_barcode_count"] = int(adata.obs.index.duplicated(keep=False).sum())
        for column in ("species", "organism", "orig.ident", "dataset", "celltype", "cell_type"):
            if column in adata.obs.columns:
                values = adata.obs[column].astype(str)
                result.setdefault("value_counts", {})[column] = {
                    str(key): int(value) for key, value in values.value_counts().items()
                }
        adata.file.close()
    except Exception as exc:  # h5ad metadata is optional evidence; collector must survive.
        result["error"] = f"{type(exc).__name__}: {exc}"
    return result


def main() -> int:
    all_files = pruned_walk()
    top_level = []
    for child in sorted(ROOT.iterdir(), key=lambda x: x.name.lower()) if ROOT.exists() else []:
        top_level.append(
            {
                "name": child.name,
                "type": "directory" if child.is_dir() else "file",
                "size_bytes": child.stat().st_size if child.is_file() else None,
                "mtime_utc": datetime.fromtimestamp(child.stat().st_mtime, timezone.utc).isoformat(),
            }
        )

    source_files = [path for path in all_files if is_source_tree_file(path)][:MAX_SOURCE_FILES]
    candidate_files = [path for path in all_files if is_candidate(path)][:MAX_CANDIDATES]
    selected = {}
    for path in source_files + candidate_files:
        selected[str(path)] = path
    evidence_files = [sha256_file(path) for path in sorted(selected.values(), key=lambda x: str(x).lower())]
    excerpts = []
    for path in selected.values():
        if len(excerpts) >= 200:
            break
        excerpt = text_excerpt(path) or log_excerpt(path)
        if excerpt:
            excerpts.append(excerpt)

    h5ad_files = [path for path in selected.values() if path.suffix.lower() == ".h5ad"][:50]
    h5ad_metadata = [inspect_h5ad(path) for path in h5ad_files]

    report = {
        "schema_version": "g5-provenance-v95-readonly/1",
        "generated_at_utc": utc_now(),
        "purpose": "Read-only recovery of SATURN v71/v72 provenance; does not rerun training.",
        "self_record": {
            "script_path": str(SELF),
            "script_sha256": sha256_file(SELF)["sha256"],
            "command_file_path": str(COMMAND_FILE),
            "command_file_sha256": (
                sha256_file(COMMAND_FILE)["sha256"] if COMMAND_FILE.exists() else "missing"
            ),
            "python_version": sys.version,
            "platform": platform.platform(),
            "cwd": os.getcwd(),
            "root": str(ROOT),
        },
        "scope": {
            "walked_file_count": len(all_files),
            "walk_cap": MAX_WALK_FILES,
            "selected_file_count": len(evidence_files),
            "source_file_count": len(source_files),
            "candidate_file_count": len(candidate_files),
            "h5ad_metadata_count": len(h5ad_metadata),
        },
        "top_level": top_level,
        "files": evidence_files,
        "text_and_log_excerpts": excerpts,
        "h5ad_metadata": h5ad_metadata,
        "negative_findings": {
            "root_exists": ROOT.exists(),
            "no_selected_files": not bool(evidence_files),
        },
    }
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        message = f"v95 collector fatal error: {type(exc).__name__}: {exc}\n"
        ERR.write_text(message, encoding="utf-8")
        print(message, file=sys.stderr)
        raise
