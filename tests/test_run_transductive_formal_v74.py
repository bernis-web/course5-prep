import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from build_transductive_bundles import SCOPE_STRING  # noqa: E402
from run_transductive_formal_v74 import run_all  # noqa: E402


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_bundle(root: Path, scope: str = SCOPE_STRING, corrupt: str = "") -> Path:
    """Create a tiny but contract-valid bundle workspace; return the directory."""
    bundles = root / "bundles"
    mappings = root / "mappings"
    roles = root / "roles"
    for directory in (bundles, mappings, roles):
        directory.mkdir(parents=True, exist_ok=True)

    direction = "hu->mo"
    ref_emb = np.array([[1.0, 0.0], [0.9, 0.1]])
    qry_emb = np.array([[0.95, 0.05]])
    payload = {
        "reference_embeddings": ref_emb,
        "query_embeddings": qry_emb,
        "reference_barcodes": np.array(["hu|A", "hu|B"]),
        "query_barcodes": np.array(["mo|A"]),
        "reference_labels": np.array(["Endothelial cell", "Endothelial cell"]),
        "query_labels": np.array(["Endothelial cell"]),
    }
    per_direction = {}
    stem = direction.replace(">", "-")
    for level in ("exact", "coarse", "fine"):
        npz_path = bundles / f"{level}_{stem}.npz"
        np.savez_compressed(npz_path, **payload)
        mapping = {} if level == "exact" else {"Endothelial cell": "endothelial"}
        mapping_path = mappings / f"{level}_{stem}.json"
        mapping_path.write_text(
            json.dumps(mapping, ensure_ascii=False, indent=1), encoding="utf-8"
        )
        per_direction.setdefault(direction, {})[level] = {
            "n_reference": 2,
            "n_query": 1,
            "n_unmapped_reference": 0,
            "n_unmapped_query": 0,
            "bundle": f"bundles/{npz_path.name}",
            "bundle_sha256": _sha(npz_path.read_bytes()),
            "mapping_sha256": _sha(mapping_path.read_bytes()),
        }

    roles_path = roles / f"roles_{stem}.tsv"
    roles_path.write_text(
        "direction\treference_species\tquery_species\tbarcode\tspecies\t"
        "query_or_reference\tlabel_exact\tmapping_status\n"
        f"{direction}\thuman\tmouse\thu|A\thuman\treference\tEndothelial cell\tactive\n",
        encoding="utf-8",
    )

    manifest = {
        "build_version": "v74",
        "evaluation_scope": scope,
        "source_path": "final.h5ad",
        "source_sha256": "d" * 64,
        "source_cells": 3,
        "representation_key": "macrogenes",
        "representation_dimensions": 2,
        "species_counts": {"human": 2, "mouse": 1},
        "mapping_tsv": "heart-celltype-map-v1.tsv",
        "mapping_sha256": "e" * 64,
        "per_direction": per_direction,
        "output_sha256": {},
    }
    manifest_path = root / "build-manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    if corrupt == "bundle":
        np.savez_compressed(bundles / "exact_hu--mo.npz", **{**payload, "query_embeddings": np.array([[0.5, 0.5]])})
    if corrupt == "missing":
        (bundles / "exact_hu--mo.npz").unlink()
    return root


class RunnerTests(unittest.TestCase):
    def test_run_all_writes_results_index_and_ready_marker(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "workspace"
            _write_bundle(root)
            results = Path(tmp) / "results"
            index_path = run_all(root, results, k=15)
            self.assertTrue(index_path.is_file())
            self.assertTrue((results / "READY.json").is_file())
            for level in ("exact", "coarse", "fine"):
                result_path = results / f"{level}_hu--mo.json"
                self.assertTrue(result_path.is_file())
                payload = json.loads(result_path.read_text(encoding="utf-8"))
                self.assertEqual(payload["direction"], "hu->mo")
                self.assertEqual(payload["level"], level)
                self.assertEqual(payload["protocol"], "transductive")
                self.assertEqual(payload["k"], 15)
                self.assertEqual(payload["evaluation_scope"], SCOPE_STRING)
                self.assertIn("bundle_sha256", payload)
                self.assertIn("evaluation", payload)
                self.assertIn("predictions", payload["evaluation"])
            index = json.loads(index_path.read_text(encoding="utf-8"))
            self.assertEqual(index["evaluation_scope"], SCOPE_STRING)
            self.assertIn("hu->mo", index["directions"])
            summary = index["directions"]["hu->mo"]["exact"]
            self.assertIn("metrics", summary)
            self.assertIn("audit", summary)
            self.assertNotIn("predictions", summary)

    def test_run_all_refuses_changed_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "workspace"
            _write_bundle(root, scope="something_else")
            with self.assertRaises(ValueError):
                run_all(root, Path(tmp) / "results", k=15)
            self.assertFalse((Path(tmp) / "results" / "READY.json").is_file())

    def test_run_all_refuses_hash_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "workspace"
            _write_bundle(root, corrupt="bundle")
            with self.assertRaises(ValueError):
                run_all(root, Path(tmp) / "results", k=15)

    def test_run_all_refuses_missing_bundle(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "workspace"
            _write_bundle(root, corrupt="missing")
            with self.assertRaises(ValueError):
                run_all(root, Path(tmp) / "results", k=15)

    def test_runner_has_no_network_imports(self):
        source = (
            Path(__file__).resolve().parents[1] / "scripts" / "run_transductive_formal_v74.py"
        ).read_text(encoding="utf-8")
        for forbidden in ("urllib", "requests", "socket", "http.client", "httpx"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
