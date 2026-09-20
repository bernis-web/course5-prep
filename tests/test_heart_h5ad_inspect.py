"""Tests for the heart h5ad evidence inspector.

No real h5ad fixture is required: the absent-anndata and JSON structure paths
run on plain byte files, and the anndata-backed assertions are skipped unless
anndata is importable in the local environment.
"""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest import mock

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import heart_h5ad_inspect  # noqa: E402

try:
    import anndata as _anndata  # noqa: F401

    ANNDATA_IMPORTABLE = True
except ImportError:
    ANNDATA_IMPORTABLE = False


def _run_main(argv, *, anndata_absent=False):
    """Run the CLI in-process and return (exit_code, stdout_text)."""
    stdout = io.StringIO()
    with contextlib.ExitStack() as stack:
        if anndata_absent:
            stack.enter_context(mock.patch.dict(sys.modules, {"anndata": None}))
        stack.enter_context(contextlib.redirect_stdout(stdout))
        try:
            heart_h5ad_inspect.main(argv)
            exit_code = 0
        except SystemExit as exc:
            exit_code = exc.code
    return exit_code, stdout.getvalue()


class CliContractTests(unittest.TestCase):
    def test_parser_accepts_multiple_inputs_and_required_output(self):
        parser = heart_h5ad_inspect.build_parser()

        args = parser.parse_args(["a.h5ad", "b.h5ad", "--output", "evidence/evidence.json"])

        self.assertEqual(args.files, [Path("a.h5ad"), Path("b.h5ad")])
        self.assertEqual(args.output, Path("evidence/evidence.json"))

    def test_parser_requires_output_and_at_least_one_file(self):
        parser = heart_h5ad_inspect.build_parser()

        with self.assertRaises(SystemExit):
            parser.parse_args([])
        with self.assertRaises(SystemExit):
            parser.parse_args(["a.h5ad"])


class AnndataMissingTests(unittest.TestCase):
    def test_missing_anndata_keeps_hash_and_size_and_exits_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake = Path(tmp) / "heart_3species.h5ad"
            fake.write_bytes(b"placeholder bytes, not an h5ad")
            output = Path(tmp) / "evidence.json"

            code, _ = _run_main([str(fake), "--output", str(output)], anndata_absent=True)

            self.assertEqual(code, 0)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertFalse(payload["anndata_available"])
            self.assertEqual(
                payload["files"],
                [
                    {
                        "file": str(fake),
                        "sha256": hashlib.sha256(fake.read_bytes()).hexdigest(),
                        "size": fake.stat().st_size,
                        "ok": False,
                        "error": "anndata not installed",
                    }
                ],
            )

    def test_missing_anndata_omits_anndata_only_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake = Path(tmp) / "heart_3species.h5ad"
            fake.write_bytes(b"placeholder bytes, not an h5ad")
            output = Path(tmp) / "evidence.json"

            _run_main([str(fake), "--output", str(output)], anndata_absent=True)

            payload = json.loads(output.read_text(encoding="utf-8"))
            for field in ("n_obs", "n_var", "x_dtype", "layers", "obs_columns", "cm_fb_hits"):
                self.assertNotIn(field, payload["files"][0])


class ReportStructureTests(unittest.TestCase):
    def test_report_json_structure_and_local_timezone_timestamp(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake = Path(tmp) / "心脏_subset.h5ad"
            fake.write_bytes(b"\x89HDF\r\n placeholder bytes")
            output = Path(tmp) / "evidence.json"

            code, _ = _run_main([str(fake), "--output", str(output)], anndata_absent=True)

            self.assertEqual(code, 0)
            raw = output.read_text(encoding="utf-8")
            payload = json.loads(raw)
            self.assertEqual(set(payload), {"generated_at", "anndata_available", "files"})
            parsed_at = datetime.fromisoformat(payload["generated_at"])
            self.assertIsNotNone(parsed_at.utcoffset())
            self.assertEqual(len(payload["files"]), 1)
            # ensure_ascii=False keeps non-ASCII file names readable in the report.
            self.assertIn("心脏_subset.h5ad", raw)
            self.assertIn('"ok": false', raw)


@unittest.skipUnless(ANNDATA_IMPORTABLE, "anndata is not importable")
class AnndataInspectionTests(unittest.TestCase):
    @staticmethod
    def _write_fixture(path: Path) -> None:
        import anndata as ad
        import numpy as np
        import pandas as pd

        obs = pd.DataFrame(
            {
                "cell_type": pd.Categorical(
                    ["Cardiomyocyte", "Fibroblast", "Endothelial", "Myofibroblast", "Cardiomyocyte"]
                ),
                "batch": ["b1", "b1", "b2", "b2", "b1"],
                "score": [0.1, 0.2, 0.3, 0.4, 0.5],
            },
            index=[f"cell{index}" for index in range(5)],
        )
        var = pd.DataFrame(
            {"highly_variable": [True, False, True]},
            index=[f"gene{index}" for index in range(3)],
        )
        x = np.arange(15, dtype=np.float32).reshape(5, 3)
        adata = ad.AnnData(X=x, obs=obs, var=var)
        adata.layers["counts"] = x.astype(np.int32)
        adata.obsm["X_pca"] = np.zeros((5, 2), dtype=np.float32)
        adata.uns["workflow"] = "heart_pilot"
        adata.write_h5ad(path)

    def test_inspection_covers_dimensions_metadata_and_cm_fb_hits(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake = Path(tmp) / "tiny_heart.h5ad"
            self._write_fixture(fake)
            output = Path(tmp) / "evidence.json"

            code, _ = _run_main([str(fake), "--output", str(output)])

            self.assertEqual(code, 0)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertTrue(payload["anndata_available"])
            record = payload["files"][0]
            self.assertTrue(record["ok"])
            self.assertEqual(record["n_obs"], 5)
            self.assertEqual(record["n_var"], 3)
            self.assertEqual(record["x_dtype"], "float32")
            self.assertEqual(record["layers"], ["counts"])
            self.assertEqual(record["obsm"], ["X_pca"])
            self.assertEqual(record["uns"], ["workflow"])
            self.assertEqual(record["var_columns"], ["highly_variable"])

            columns = {column["name"]: column for column in record["obs_columns"]}
            self.assertEqual(set(columns), {"cell_type", "batch", "score"})
            self.assertEqual(columns["cell_type"]["n_unique"], 4)
            self.assertEqual(
                columns["cell_type"]["value_counts"],
                {
                    "Cardiomyocyte": 2,
                    "Fibroblast": 1,
                    "Endothelial": 1,
                    "Myofibroblast": 1,
                },
            )
            self.assertEqual(columns["batch"]["value_counts"], {"b1": 3, "b2": 2})
            self.assertEqual(columns["score"]["n_unique"], 5)
            self.assertIsNotNone(columns["score"]["value_counts"])
            # Cardiomyocyte x2 + Fibroblast + Myofibroblast, counted per cell.
            self.assertEqual(record["cm_fb_hits"], {"cell_type": 4})

    def test_value_counts_suppressed_past_fifty_unique_values(self):
        import anndata as ad
        import numpy as np
        import pandas as pd

        with tempfile.TemporaryDirectory() as tmp:
            fake = Path(tmp) / "wide_obs.h5ad"
            n_cells = 60
            obs = pd.DataFrame(
                {"cell_code": np.arange(n_cells)},
                index=[f"cell{index}" for index in range(n_cells)],
            )
            var = pd.DataFrame(index=["gene0"])
            adata = ad.AnnData(X=np.zeros((n_cells, 1), dtype=np.float32), obs=obs, var=var)
            adata.write_h5ad(fake)
            output = Path(tmp) / "evidence.json"

            code, _ = _run_main([str(fake), "--output", str(output)])

            self.assertEqual(code, 0)
            payload = json.loads(output.read_text(encoding="utf-8"))
            record = payload["files"][0]
            self.assertTrue(record["ok"])
            column = record["obs_columns"][0]
            self.assertEqual(column["name"], "cell_code")
            self.assertEqual(column["n_unique"], n_cells)
            self.assertIsNone(column["value_counts"])
            self.assertEqual(record["cm_fb_hits"], {})

    def test_unreadable_h5ad_is_recorded_and_exit_code_is_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake = Path(tmp) / "broken.h5ad"
            fake.write_bytes(b"definitely not hdf5")
            output = Path(tmp) / "evidence.json"

            code, _ = _run_main([str(fake), "--output", str(output)])

            self.assertEqual(code, 2)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertTrue(payload["anndata_available"])
            record = payload["files"][0]
            self.assertFalse(record["ok"])
            self.assertIn("error", record)
            self.assertNotIn("n_obs", record)
            self.assertEqual(record["sha256"], hashlib.sha256(fake.read_bytes()).hexdigest())
            self.assertEqual(record["size"], fake.stat().st_size)


if __name__ == "__main__":
    unittest.main()
