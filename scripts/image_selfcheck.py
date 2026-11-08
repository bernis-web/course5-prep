"""Self-check script intended to run INSIDE the platform image g5-opca-container.

Purpose: prove that the image built from the pinned dependency list can (a) import
every package at the pinned version, and (b) reproduce the frozen oPCA numbers.

It writes a single JSON to stdout between markers so the report can be extracted
from a task log without any file-transfer step:

    SELFCHECK_BEGIN
    { ...json... }
    SELFCHECK_END

Exit codes: 0 = all pinned versions match; 3 = version drift; 4 = data missing.

This script is NOT part of the container image build. It is uploaded separately and
run as an offline task so the check happens in the real built image.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import sys
from pathlib import Path

PINNED = {
    "numpy": "1.23.5",
    "scipy": "1.10.1",
    "pandas": "1.5.3",
    "sklearn": "1.6.1",
    "anndata": "0.10.8",
    "scanpy": "1.9.3",
    "h5py": "3.8.0",
}

# Frozen values this image must reproduce (results/phase-20261010/opca-fixkey-recovered-20261015)
FROZEN = {
    "human->mouse|coarse": 0.8618,
    "mouse->human|coarse": 0.7369,
    "human->zebrafish|coarse": 0.1795,
    "mouse->zebrafish|coarse": 0.2675,
    "zebrafish->human|coarse": 0.1734,
    "zebrafish->mouse|coarse": 0.5814,
}

DATA_CANDIDATES = [
    Path(os.environ["SELFCHECK_DATA_DIR"]) if os.environ.get("SELFCHECK_DATA_DIR") else None,
    Path("/data"),
    Path("/Files"),
    Path("."),
    Path("data"),
]


def emit(payload: dict) -> None:
    print("SELFCHECK_BEGIN", flush=True)
    print(json.dumps(payload, ensure_ascii=False, indent=1), flush=True)
    print("SELFCHECK_END", flush=True)


def versions() -> dict[str, str]:
    import anndata
    import h5py
    import numpy
    import pandas
    import scanpy
    import scipy
    import sklearn

    return {
        "numpy": numpy.__version__,
        "scipy": scipy.__version__,
        "pandas": pandas.__version__,
        "sklearn": sklearn.__version__,
        "anndata": anndata.__version__,
        "scanpy": scanpy.__version__,
        "h5py": h5py.__version__,
    }


def find_inputs() -> tuple[Path | None, Path | None]:
    need = [
        "local_human_s.h5ad",
        "local_mouse_s.h5ad",
        "local_zebrafish_s.h5ad",
        "wheelhouse/orth-MGI-HOM.rpt",
        "wheelhouse/orth-human-orthos.txt",
        "wheelhouse/orth-mouse-orthos.txt",
        "wheelhouse/heart-celltype-map-v1.tsv",
    ]
    for base in DATA_CANDIDATES:
        if base is None or not base.is_dir():
            continue
        if all((base / n).exists() for n in need):
            return base, base / "wheelhouse"
    return None, None


def main() -> int:
    payload: dict = {
        "python": platform.python_version(),
        "executable": sys.executable,
        "cwd": os.getcwd(),
        "hostname": platform.node(),
    }

    try:
        got = versions()
    except Exception as exc:  # noqa: BLE001
        payload["import_error"] = f"{type(exc).__name__}: {exc}"
        payload["verdict"] = "import_failed"
        emit(payload)
        return 3

    payload["versions"] = got
    drift = {k: {"pinned": v, "actual": got.get(k)} for k, v in PINNED.items() if got.get(k) != v}
    payload["version_drift"] = drift
    payload["versions_match"] = not drift

    data_dir, orth_dir = find_inputs()
    payload["data_dir"] = str(data_dir) if data_dir else None
    payload["orth_dir"] = str(orth_dir) if orth_dir else None

    if data_dir is None:
        payload["verdict"] = "data_missing"
        emit(payload)
        return 4

    # Only attempt the numeric reproduction if an evaluation script is alongside us.
    script = Path(__file__).with_name("ortholog_pca_dcs_v3_fixkey.py")
    payload["eval_script"] = str(script) if script.exists() else None

    if script.exists():
        import subprocess
        import tempfile

        out_dir = Path(tempfile.mkdtemp(prefix="selfcheck-")) / "out"
        env = dict(os.environ)
        env.update(
            {
                "OPCA_H5AD_DIR": str(data_dir),
                "OPCA_ORTH_DIR": str(orth_dir),
                "OPCA_ORTH_MGI": str(orth_dir / "orth-MGI-HOM.rpt"),
                "OPCA_ORTH_HF": str(orth_dir / "orth-human-orthos.txt"),
                "OPCA_ORTH_MF": str(orth_dir / "orth-mouse-orthos.txt"),
                "OPCA_MAPPING": str(orth_dir / "heart-celltype-map-v1.tsv"),
                "OPCA_OUT": str(out_dir),
            }
        )
        proc = subprocess.run(
            [sys.executable, str(script)],
            env=env,
            capture_output=True,
            text=True,
            timeout=3600,
        )
        payload["eval_exit"] = proc.returncode
        payload["eval_tail"] = proc.stdout.strip().splitlines()[-6:]

        metrics = out_dir / "metrics.json"
        if proc.returncode == 0 and metrics.exists():
            m = json.loads(metrics.read_text(encoding="utf-8"))
            cells = {}
            mismatch = []
            for key, want in FROZEN.items():
                direction, level = key.split("|")
                got_val = m[direction][level]["acc"]
                same = abs(got_val - want) < 5e-5
                cells[key] = {"frozen": want, "actual": got_val, "match": same}
                if not same:
                    mismatch.append(key)
            payload["frozen_cells"] = cells
            payload["frozen_mismatch"] = mismatch
            payload["reproduces_frozen"] = not mismatch
        else:
            payload["reproduces_frozen"] = False
            payload["eval_stderr_tail"] = proc.stderr.strip().splitlines()[-6:]

    payload["verdict"] = "ok" if (not drift and payload.get("reproduces_frozen")) else (
        "version_drift" if drift else "did_not_reproduce"
    )
    emit(payload)
    if drift:
        return 3
    if not payload.get("reproduces_frozen"):
        return 5
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
