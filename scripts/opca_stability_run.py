"""Stability harness for ortholog-PCA.

Runs the FROZEN scoring script (scripts/ortholog_pca_dcs_v3_fixkey.py) unchanged,
only overriding module-level SEED so the PCA randomised-SVD seed can vary, and
optionally pointing OPCA_H5AD_DIR at a perturbed copy of the three .h5ad files.

Why this shape: the authoritative numbers come from the frozen script.  Any
harness that re-implements the scoring loop risks drifting from it.  So the
scoring code is imported and executed verbatim, and every perturbation is
applied to the INPUT data (cell subsample / gene subsample) or to one declared
constant (SEED).

Usage (env-driven, one run per invocation):
  STAB_SEED=0 STAB_OPCA_OUT=tmp/stab/base python scripts/opca_stability_run.py
"""
import importlib.util
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "scripts" / "ortholog_pca_dcs_v3_fixkey.py"

DEFAULTS = {
    "OPCA_MAPPING": str(ROOT / "config" / "heart-celltype-map-v1.tsv"),
    "OPCA_ORTH_MGI": str(ROOT / "ortholog" / "MGI_HOM_MouseHumanSequence.rpt"),
    "OPCA_ORTH_HF": str(ROOT / "ortholog" / "human_orthos.txt"),
    "OPCA_ORTH_MF": str(ROOT / "ortholog" / "mouse_orthos.txt"),
}
for k, v in DEFAULTS.items():
    os.environ.setdefault(k, v)


def load_frozen():
    spec = importlib.util.spec_from_file_location("opca_frozen", FROZEN)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    seed = int(os.environ.get("STAB_SEED", "0"))
    nperm = int(os.environ.get("STAB_NPERM", "200"))
    mod = load_frozen()
    mod.SEED = seed
    mod.NPERM_FULL = nperm
    mod.NPERM_SMOKE = nperm
    print(f"HARNESS seed={seed} nperm={nperm} h5ad_dir={os.environ.get('OPCA_H5AD_DIR', '/Files')} "
          f"out={os.environ.get('OPCA_OUT')}", flush=True)
    mod.main()


if __name__ == "__main__":
    main()
