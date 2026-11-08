#!/usr/bin/env python3
"""Independent structural check for a recovered scVI cross-species artifact.

Usage:
    python scripts/verify_scvi_artifact.py <artifact_dir>

Reads only files produced by the platform run (no recomputation of any model).
Checks:
  1. metrics.json has the 6 expected directions x 3 label levels
  2. required keys exist in every cell and are internally consistent
  3. sha256.tsv matches the files on disk
  4. prints a compact table for manual comparison against oPCA / SATURN / SAMap

Exit codes: 0 = all checks pass, 1 = at least one check failed.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

DIRECTIONS = [
    "human->mouse", "mouse->human",
    "human->zebrafish", "zebrafish->human",
    "mouse->zebrafish", "zebrafish->mouse",
]
LEVELS = ["exact", "coarse", "fine"]
CELL_KEYS = ["acc", "macro_f1", "majority", "shuffle_p", "n_ref", "n_q",
             "n_q_total", "coverage_q", "confusion", "n_perm"]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__.strip().splitlines()[2])
        return 1
    root = Path(argv[1])
    if not root.is_dir():
        print(f"FAIL not a directory: {root}")
        return 1

    fails: list[str] = []
    metrics_path = root / "metrics.json"
    if not metrics_path.is_file():
        print(f"FAIL missing {metrics_path}")
        return 1
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))

    missing_dirs = [d for d in DIRECTIONS if d not in metrics]
    extra_dirs = [d for d in metrics if d not in DIRECTIONS]
    if missing_dirs:
        fails.append(f"missing directions: {missing_dirs}")
    if extra_dirs:
        fails.append(f"unexpected directions: {extra_dirs}")

    print(f"{'direction':<20}{'level':<8}{'acc':>8}{'macro_f1':>10}{'majority':>10}"
          f"{'p':>8}{'n_ref':>8}{'n_q':>7}{'cov':>7}")
    rows = 0
    for direction in DIRECTIONS:
        block = metrics.get(direction, {})
        for level in LEVELS:
            cell = block.get(level)
            if not isinstance(cell, dict):
                fails.append(f"{direction}/{level}: missing cell")
                continue
            rows += 1
            miss = [k for k in CELL_KEYS if k not in cell]
            if miss:
                fails.append(f"{direction}/{level}: missing keys {miss}")
            if cell.get("n_perm") != 200:
                fails.append(f"{direction}/{level}: n_perm={cell.get('n_perm')} != 200")
            if cell.get("n_ref", 0) <= 0 or cell.get("n_q", 0) <= 0:
                fails.append(f"{direction}/{level}: empty ref/query split")
            print(f"{direction:<20}{level:<8}{cell.get('acc', float('nan')):>8.4f}"
                  f"{cell.get('macro_f1', float('nan')):>10.4f}"
                  f"{cell.get('majority', float('nan')):>10.4f}"
                  f"{cell.get('shuffle_p', float('nan')):>8.4f}"
                  f"{cell.get('n_ref', 0):>8d}{cell.get('n_q', 0):>7d}"
                  f"{cell.get('coverage_q', float('nan')):>7.3f}")
        print()

    sha_path = root / "sha256.tsv"
    if sha_path.is_file():
        bad = 0
        for line in sha_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            digest, rel = line.split("  ", 1)
            target = root / rel
            if not target.is_file():
                fails.append(f"sha256.tsv names a missing file: {rel}")
                bad += 1
            elif sha256_file(target) != digest:
                fails.append(f"sha256 mismatch: {rel}")
                bad += 1
        print(f"sha256.tsv checked, mismatches={bad}")
    else:
        fails.append("missing sha256.tsv")

    print(f"\ncells={rows} failures={len(fails)}")
    for f in fails:
        print("  FAIL " + f)
    return 0 if not fails else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
