"""Read-only runtime preflight for the course 5 benchmark.

The checker inspects the current interpreter, selected package metadata,
common executables, and (when available) ``nvidia-smi``. It never installs,
downloads, uploads, or starts a cloud task.
"""

from __future__ import annotations

import argparse
import importlib.metadata
import importlib.util
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


PACKAGE_NAMES = (
    "anndata",
    "scanpy",
    "scvi",
    "harmonypy",
    "saturn",
    "samap",
    "torch",
    "sklearn",
)
EXECUTABLE_NAMES = ("nvidia-smi", "conda", "mamba", "micromamba", "docker", "podman")


def _package_status(name: str) -> dict[str, Any]:
    available = importlib.util.find_spec(name) is not None
    version = None
    if available:
        distribution_name = {"sklearn": "scikit-learn", "scvi": "scvi-tools"}.get(name, name)
        try:
            version = importlib.metadata.version(distribution_name)
        except importlib.metadata.PackageNotFoundError:
            version = "importable_without_distribution_metadata"
    return {"available": available, "version": version}


def _gpu_status() -> dict[str, Any]:
    executable = shutil.which("nvidia-smi")
    if executable is None:
        return {"available": False, "executable": None, "devices": [], "error": "nvidia-smi not found"}
    try:
        result = subprocess.run(
            [executable, "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return {"available": False, "executable": executable, "devices": [], "error": str(exc)}
    devices = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return {
        "available": result.returncode == 0 and bool(devices),
        "executable": executable,
        "devices": devices,
        "error": result.stderr.strip() if result.returncode else None,
    }


def collect_environment() -> dict[str, Any]:
    """Collect local facts without mutating the environment."""
    memory_gb = None
    try:
        import psutil  # type: ignore

        memory_gb = round(psutil.virtual_memory().total / (1024**3), 2)
    except ImportError:
        pass
    return {
        "scope": "local_runtime",
        "python": {
            "version": platform.python_version(),
            "executable": sys.executable,
        },
        "hardware": {
            "cpu_count": os.cpu_count(),
            "ram_gb": memory_gb,
            "gpu": _gpu_status(),
        },
        "packages": {name: _package_status(name) for name in PACKAGE_NAMES},
        "executables": {name: shutil.which(name) for name in EXECUTABLE_NAMES},
        "side_effects": [],
    }


def write_environment_report(path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(collect_environment(), ensure_ascii=True, indent=2), encoding="utf-8")
    return str(path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("environment-report.json"))
    args = parser.parse_args()
    print(json.dumps({"report_path": write_environment_report(args.output)}, ensure_ascii=True))


if __name__ == "__main__":
    main()
