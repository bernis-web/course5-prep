#!/usr/bin/env python3
"""Smoke test: verify the anndata / scanpy / scvi combination after removing
the stale anndata bundled in pylibs_full.tar.gz.

Why this exists
---------------
`pylibs_full.tar.gz` ships an old `anndata`. Because `PYTHONPATH` takes
precedence over site-packages, that old copy shadows the image's
`anndata 0.10.8`, and `mudata` then fails to import `AlignedViewMixin`,
which makes `import scvi` fail. The fix is to delete the bundled copy:

    rm -rf ./pylibs_full/anndata ./pylibs_full/anndata-*.dist-info

This script locks that fix in. Run it in the container right after
untarring pylibs and before the real analysis. It also exercises the two
anndata 0.10 behaviours most likely to bite later:

  * sliced views (`adata[:, genes]`) must be `.copy()`-ed before being
    written in place;
  * `normalize_total` / `log1p` on a full (non-view) AnnData.

Exit code 0 = all good; non-zero = do not start the analysis.

Usage:
    python3 smoke_test_env.py
"""
from __future__ import annotations

import sys
import traceback


def check_anndata():
    import anndata as ad
    print(f"     anndata {ad.__version__} @ {ad.__file__}")
    assert "pylibs_full" not in str(ad.__file__), (
        "anndata is still loaded from pylibs_full; "
        "delete pylibs_full/anndata* before running this"
    )


def check_mudata():
    import mudata
    print(f"     mudata {getattr(mudata, '__version__', 'unknown')}")


def check_scanpy():
    import scanpy as sc
    print(f"     scanpy {sc.__version__}")


def check_scvi():
    import scvi
    print(f"     scvi {scvi.__version__}")


def check_torch():
    import torch
    print(f"     torch {torch.__version__}")


def check_normalize_log1p():
    import numpy as np
    import anndata as ad
    import scanpy as sc

    rng = np.random.default_rng(0)
    X = rng.poisson(2.0, size=(60, 40)).astype("float32")
    a = ad.AnnData(X)
    a.obs_names = [f"c{i}" for i in range(a.n_obs)]
    a.var_names = [f"g{i}" for i in range(a.n_vars)]
    sc.pp.normalize_total(a, target_sum=1e4)
    sc.pp.log1p(a)
    assert np.isfinite(a.X).all(), "non-finite values after log1p"


def check_sliced_view_copy():
    import numpy as np
    import anndata as ad

    rng = np.random.default_rng(1)
    a = ad.AnnData(rng.random((30, 20)).astype("float32"))
    view = a[:, :5].copy()
    view.X = view.X * 2
    assert view.X is not None


def check_scvi_setup():
    import numpy as np
    import anndata as ad
    import scvi

    rng = np.random.default_rng(2)
    a = ad.AnnData(rng.poisson(1.0, size=(40, 30)).astype("float32"))
    a.obs_names = [f"c{i}" for i in range(a.n_obs)]
    a.var_names = [f"g{i}" for i in range(a.n_vars)]
    a.obs["species"] = ["a"] * 20 + ["b"] * 20
    scvi.model.SCVI.setup_anndata(a, batch_key="species")


CHECKS = [
    ("import anndata", check_anndata),
    ("import mudata (needs AlignedViewMixin)", check_mudata),
    ("import scanpy", check_scanpy),
    ("import scvi", check_scvi),
    ("import torch", check_torch),
    ("normalize_total + log1p on full AnnData", check_normalize_log1p),
    ("sliced view copied before in-place edit", check_sliced_view_copy),
    ("scvi setup_anndata with batch_key", check_scvi_setup),
]


def main() -> int:
    print("smoke test: anndata / mudata / scanpy / scvi / torch")
    for name, fn in CHECKS:
        try:
            fn()
        except Exception:
            print(f"FAIL {name}")
            traceback.print_exc()
            return 1
        print(f"OK   {name}")
    print("\nall checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
