import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from validate_eval_manifest import (  # noqa: E402
    ManifestContractError,
    load_barcode_roles,
    load_manifest,
    validate_eval_manifest,
)


ROOT = Path(__file__).resolve().parents[1]


def _row(barcode: str, species: str, role: str, label: str) -> dict[str, str]:
    return {
        "barcode": barcode,
        "species": species,
        "role": role,
        "query_or_reference": role,
        "source_file": f"{species}.h5ad",
        "duplicate_group": "none",
        "label_exact": label,
        "label_mapped": label,
        "mapping_status": "confirmed",
        "reviewer": "reviewer-1",
        "evidence_status": "confirmed",
    }


class EvalManifestTests(unittest.TestCase):
    def test_current_manifest_is_valid_but_not_ready_and_header_only_roles_block(self):
        manifest = load_manifest(ROOT / "config" / "eval-manifest-v73.json")
        rows = load_barcode_roles(ROOT / "config" / "barcode-roles-v73.tsv")
        result = validate_eval_manifest(manifest, rows)

        self.assertTrue(result["valid"])
        self.assertFalse(result["ready_for_confirmation"])
        self.assertIn("evidence_status_pending", result["blocking_items"])
        self.assertIn("barcode_role_table_empty", result["blocking_items"])
        # V96 confirmed this partial field while the overall provenance gate remains pending.
        self.assertNotIn(
            "representation.evaluation_layer", result["blocking_items"]
        )
        self.assertFalse(result["side_effects"])

    def test_pending_manifest_reports_missing_evaluation_layer_without_error(self):
        manifest = load_manifest(ROOT / "config" / "eval-manifest-v73.json")
        manifest["representation"]["evaluation_layer"] = "pending"
        result = validate_eval_manifest(manifest, [])
        self.assertTrue(result["valid"])
        self.assertFalse(result["ready_for_confirmation"])
        self.assertIn(
            "representation.evaluation_layer", result["blocking_items"]
        )

    def test_pending_manifest_rejects_verified_looking_task_id(self):
        manifest = load_manifest(ROOT / "config" / "eval-manifest-v73.json")
        manifest["run"]["dcs_task_id"] = "should-not-be-guessed"
        with self.assertRaises(ManifestContractError):
            validate_eval_manifest(manifest, [])

    def test_confirmed_manifest_requires_complete_provenance_and_clean_roles(self):
        manifest = load_manifest(ROOT / "config" / "eval-manifest-v73.json")
        manifest["evidence_status"] = "confirmed"
        manifest["run"].update(
            {
                "dcs_task_id": "task-v71",
                "original_command": "python train-saturn.py --seed 7",
                "complete_log_path": "logs/v71.log",
                "input_manifest_path": "inputs-v71.tsv",
            }
        )
        manifest["representation"]["evaluation_layer"] = "obsm/macrogenes"
        manifest["labels"]["reviewer"] = "reviewer-1"
        manifest["training_parameters"].update(
            {"use_ref_labels": False, "unfreeze_macrogenes": False, "seed": 7}
        )
        manifest["evaluation_protocol"]["transductive"]["status"] = "confirmed_transductive"
        rows = [
            _row("h1", "Homo_sapiens", "reference", "A"),
            _row("m1", "Mus_musculus", "query", "A"),
        ]
        for index, dataset in enumerate(manifest["datasets"]):
            dataset.update(
                {
                    "role": "reference" if index == 0 else "query",
                    "query_or_reference": "reference" if index == 0 else "query",
                    "input_path": f"input-{index}.h5ad",
                    "input_sha256": "a" * 64,
                    "final_anndata_path": f"final-{index}.h5ad",
                    "final_anndata_sha256": "b" * 64,
                    "barcode_list_path": f"barcodes-{index}.tsv",
                    "barcode_sha256": "c" * 64,
                    "label_column": "labels",
                    "batch_column": "batch",
                }
            )
        result = validate_eval_manifest(manifest, rows)
        self.assertTrue(result["valid"])
        self.assertTrue(result["ready_for_confirmation"])
        self.assertEqual(result["blocking_items"], [])

    def test_cloud_actions_must_remain_disabled(self):
        manifest = load_manifest(ROOT / "config" / "eval-manifest-v73.json")
        manifest["provenance"]["cloud_actions_allowed"] = True
        with self.assertRaises(ManifestContractError):
            validate_eval_manifest(manifest, [])

    def test_cli_reports_pending_manifest_without_mutation(self):
        script = ROOT / "scripts" / "validate_eval_manifest.py"
        completed = subprocess.run(
            [sys.executable, str(script)],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertTrue(result["valid"])
        self.assertFalse(result["ready_for_confirmation"])


if __name__ == "__main__":
    unittest.main()
