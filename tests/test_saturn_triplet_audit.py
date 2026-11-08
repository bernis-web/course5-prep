import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from audit_saturn_triplet_path import audit_source  # noqa: E402


class SaturnTripletAuditTests(unittest.TestCase):
    def test_current_checked_in_source_reports_cross_species_and_unconsumed_ref_labels(self):
        root = Path(__file__).resolve().parents[1]
        source = root / "wheelhouse" / "saturn-src" / "train-saturn.py"
        report = audit_source(source)

        self.assertEqual(report["checks"]["triplet_miner"]["miner_type_values"], ["cross_species"])
        self.assertTrue(report["checks"]["use_ref_labels_branch"]["found"])
        self.assertTrue(report["checks"]["use_ref_labels_branch"]["true_branch_passes_ref_labels"])
        self.assertTrue(report["checks"]["use_ref_labels_branch"]["false_branch_omits_ref_labels"])
        selection = report["checks"]["ref_labels_selection"]
        self.assertTrue(selection["parameter_found"])
        self.assertFalse(selection["reads_outside_default_initialization"])
        self.assertFalse(selection["participates_in_triplet_selection"])
        self.assertTrue(report["checks"]["macrogenes_output"]["found"])
        self.assertEqual(report["summary"]["status"], "warning")

    def test_fixture_detects_ref_labels_used_by_selection_logic(self):
        source_text = """
def train(metric, embeddings, labels, species, ref_labels, use_ref_labels):
    miner = TripletMarginMiner(miner_type="cross_species")
    if use_ref_labels:
        return miner(embeddings, labels, species, ref_labels=ref_labels)
    return miner(embeddings, labels, species)

def get_species_triplet_indices(labels, species, embeddings, distance, ref_labels=None):
    ref_labels = labels if ref_labels is None else ref_labels
    positives = where(ref_labels == labels)
    return positives

def create_output_anndata(adata, train_macrogenes):
    adata.obsm["macrogenes"] = train_macrogenes
"""
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "fixture.py"
            source.write_text(source_text, encoding="utf-8")
            report = audit_source(source)

        selection = report["checks"]["ref_labels_selection"]
        self.assertTrue(selection["reads_outside_default_initialization"])
        self.assertTrue(selection["participates_in_triplet_selection"])
        self.assertEqual(report["summary"]["status"], "pass")

    def test_cli_writes_json_report(self):
        root = Path(__file__).resolve().parents[1]
        script = root / "scripts" / "audit_saturn_triplet_path.py"
        source = root / "wheelhouse" / "saturn-src" / "train-saturn.py"
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "audit.json"
            completed = subprocess.run(
                [sys.executable, str(script), "--source", str(source), "--format", "json", "--output", str(output)],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(report["source"]["path"], str(source.resolve()))
            self.assertIn("sha256", report["source"])
            self.assertIn("ref_labels_selection", report["checks"])


if __name__ == "__main__":
    unittest.main()
