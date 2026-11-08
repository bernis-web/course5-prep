import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

SCRIPT_DIR = __import__("pathlib").Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from evaluate_cross_species_transfer import EvaluationError, evaluate_transfer  # noqa: E402


class CrossSpeciesEvaluatorTests(unittest.TestCase):
    def test_excludes_overlapping_and_duplicate_barcodes_and_reports_mapped_metrics(self):
        reference = np.array([[1.0, 0.0], [0.0, 1.0], [0.9, 0.1], [0.0, 0.9]], dtype=float)
        query = np.array([[1.0, 0.0], [0.0, 1.0]], dtype=float)
        result = evaluate_transfer(
            reference,
            ["r1", "r2", "r2", "r3"],
            ["A", "B", "B", "B"],
            query,
            ["r1", "q2"],
            ["A", "B"],
            label_mapping={"A": "contract_A", "B": "contract_B"},
            k=1,
            protocol="inductive",
        )

        self.assertEqual(result["audit"]["excluded_reference_duplicate_barcodes"], ["r2"])
        self.assertEqual(result["audit"]["excluded_query_overlap_barcodes"], ["r1"])
        self.assertEqual(result["audit"]["n_scored"], 1)
        self.assertEqual(result["metrics"]["exact"]["accuracy"], 1.0)
        self.assertEqual(result["metrics"]["mapped"]["macro_f1"], 1.0)
        self.assertEqual(result["predictions"][0]["barcode"], "q2")

    def test_abstention_is_explicit_and_coverage_is_not_hidden(self):
        reference = np.array([[1.0, 0.0], [0.0, 1.0]], dtype=float)
        query = np.array([[1.0, 1.0]], dtype=float)
        result = evaluate_transfer(
            reference,
            ["r1", "r2"],
            ["A", "B"],
            query,
            ["q1"],
            ["A"],
            k=2,
            abstain_below=0.75,
            protocol="inductive",
        )

        self.assertTrue(result["predictions"][0]["abstained"])
        self.assertEqual(result["metrics"]["exact"]["coverage"], 0.0)
        self.assertEqual(result["metrics"]["exact"]["abstention_rate"], 1.0)
        self.assertEqual(result["metrics"]["exact"]["n_scored"], 0)

    def test_rejects_implicit_or_mismatched_inputs(self):
        with self.assertRaises(EvaluationError):
            evaluate_transfer(
                np.ones((2, 2)),
                ["r1", "r2"],
                ["A"],
                np.ones((1, 2)),
                ["q1"],
                ["A"],
                protocol="inductive",
            )

    def test_result_is_json_serializable_and_contains_top_k(self):
        result = evaluate_transfer(
            np.array([[1.0, 0.0], [0.0, 1.0]]),
            ["r1", "r2"],
            ["A", "B"],
            np.array([[0.9, 0.1]]),
            ["q1"],
            ["B"],
            k=2,
            protocol="inductive",
        )
        json.dumps(result, ensure_ascii=False)
        self.assertEqual(result["predictions"][0]["top_k"], ["A", "B"])
        self.assertEqual(result["metrics"]["exact"]["top3_accuracy"], 1.0)

    def test_cli_requires_explicit_representation_and_writes_summary(self):
        root = Path(__file__).resolve().parents[1]
        script = root / "scripts" / "evaluate_cross_species_transfer.py"
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            bundle = tmp_path / "bundle.npz"
            output = tmp_path / "summary.json"
            np.savez(
                bundle,
                reference_embeddings=np.array([[1.0, 0.0], [0.0, 1.0]]),
                query_embeddings=np.array([[1.0, 0.0]]),
                reference_barcodes=np.array(["r1", "r2"]),
                query_barcodes=np.array(["q1"]),
                reference_labels=np.array(["A", "B"]),
                query_labels=np.array(["A"]),
            )
            completed = subprocess.run(
                [sys.executable, str(script), "--input-npz", str(bundle), "--output", str(output)],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.assertEqual(completed.returncode, 2)
            self.assertIn("--representation", completed.stderr)
            completed = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--input-npz",
                    str(bundle),
                    "--output",
                    str(output),
                    "--representation",
                    "X",
                    "--protocol",
                    "inductive",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["representation"], "X")
            self.assertEqual(payload["metrics"]["exact"]["accuracy"], 1.0)


if __name__ == "__main__":
    unittest.main()
