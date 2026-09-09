"""Collect package, command, and GPU metadata without changing the runtime."""

from __future__ import annotations

import argparse
import importlib.metadata
import importlib.util
import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


PACKAGE_SPECS = {
    "saturn": ("saturn", "saturn"),
    "samap": ("samap", "samap"),
    "scvi": ("scvi", "scvi-tools"),
    "anndata": ("anndata", "anndata"),
    "scanpy": ("scanpy", "scanpy"),
    "torch": ("torch", "torch"),
    "fair-esm": ("esm", "fair-esm"),
    "faiss-gpu": ("faiss", "faiss-gpu"),
}
COMMAND_NAMES = ("saturn", "samap", "python", "nvidia-smi")


def _package_probe(import_name: str, distribution_name: str) -> dict[str, Any]:
    try:
        available = importlib.util.find_spec(import_name) is not None
    except (ImportError, ValueError):
        available = False
    version = None
    if available:
        try:
            version = importlib.metadata.version(distribution_name)
        except importlib.metadata.PackageNotFoundError:
            version = "importable_without_distribution_metadata"
    return {
        "import_name": import_name,
        "available": available,
        "version": version,
    }


def _command_probe(name: str) -> dict[str, Any]:
    path = shutil.which(name)
    result: dict[str, Any] = {"available": bool(path), "path": path}
    if path is None:
        return result
    try:
        completed = subprocess.run(
            [path, "--version"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        result.update({"probe": "--version", "return_code": None, "error": str(exc)})
        return result
    output = "\n".join(part.strip() for part in (completed.stdout, completed.stderr) if part.strip())
    result.update(
        {
            "probe": "--version",
            "return_code": completed.returncode,
            "output": output[:2000],
        }
    )
    return result


def _gpu_probe() -> dict[str, Any]:
    path = shutil.which("nvidia-smi")
    if path is None:
        return {"available": False, "path": None, "devices": [], "error": "nvidia-smi not found"}
    try:
        completed = subprocess.run(
            [
                path,
                "--query-gpu=name,memory.total,driver_version",
                "--format=csv,noheader",
            ],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return {"available": False, "path": path, "devices": [], "error": str(exc)}
    devices = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
    return {
        "available": completed.returncode == 0 and bool(devices),
        "path": path,
        "devices": devices,
        "return_code": completed.returncode,
        "error": completed.stderr.strip() if completed.returncode else None,
    }


def probe_runtime() -> dict[str, Any]:
    """Return read-only runtime facts suitable for an image evidence record."""
    return {
        "probe_version": 1,
        "scope": "runtime_probe",
        "python": {
            "version": platform.python_version(),
            "executable": sys.executable,
        },
        "packages": {
            name: _package_probe(import_name, distribution_name)
            for name, (import_name, distribution_name) in PACKAGE_SPECS.items()
        },
        "commands": {name: _command_probe(name) for name in COMMAND_NAMES},
        "gpu": _gpu_probe(),
        "side_effects": [],
    }


def write_probe(path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(probe_runtime(), ensure_ascii=True, indent=2), encoding="utf-8")
    return str(path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.output is None:
        print(json.dumps(probe_runtime(), ensure_ascii=True, indent=2))
    else:
        print(json.dumps({"report_path": write_probe(args.output)}, ensure_ascii=True))


if __name__ == "__main__":
    main()
