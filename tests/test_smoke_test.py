import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from environment_check import collect_environment, write_environment_report  # noqa: E402
from input_contract import InputContractError, validate_metadata, write_metadata_manifest  # noqa: E402
from budget_check import BudgetPlanError, evaluate_trial, load_plan  # noqa: E402
from run_artifacts import ArtifactContractError, REQUIRED_ARTIFACTS, validate_run_artifacts  # noqa: E402
from agent_evaluation import AgentMatrixError, load_agent_matrix, validate_agent_matrix  # noqa: E402
from startup_preflight import PreflightError, load_preflight, validate_preflight  # noqa: E402
from smoke_test import evaluate_embedding, evaluate_labels, run_smoke_test  # noqa: E402


class SmokeEvaluatorTests(unittest.TestCase):
    def test_macro_f1_is_computed_per_class(self):
        y_true = np.array(["A", "A", "B", "B", "C", "C"])
        y_pred = np.array(["A", "B", "B", "B", "C", "A"])

        result = evaluate_labels(y_true, y_pred)

        self.assertAlmostEqual(result["macro_f1"], (0.5 + 0.8 + (2 / 3)) / 3, places=6)
        self.assertEqual(result["n_labels"], 3)

    def test_embedding_metrics_are_finite_and_bounded(self):
        embedding = np.array(
            [[0.0, 0.0], [0.1, 0.0], [5.0, 5.0], [5.1, 5.0], [10.0, 0.0], [10.1, 0.0]]
        )
        labels = np.array(["A", "A", "B", "B", "C", "C"])
        batches = np.array(["s1", "s2", "s1", "s2", "s1", "s2"])

        result = evaluate_embedding(embedding, labels, batches, neighbors=3)

        self.assertTrue(-1.0 <= result["silhouette"] <= 1.0)
        self.assertGreaterEqual(result["ilisi"], 1.0)
        self.assertGreaterEqual(result["kbet_rejection_rate"], 0.0)
        self.assertLessEqual(result["kbet_rejection_rate"], 1.0)

    def test_smoke_run_writes_auditable_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = run_smoke_test(Path(tmp), seed=7, n_cells=120, n_features=12)
            metrics_path = Path(output["metrics_path"])
            manifest_path = Path(output["manifest_path"])

            self.assertTrue(metrics_path.exists())
            self.assertTrue(manifest_path.exists())
            self.assertIn("macro_f1", metrics_path.read_text(encoding="utf-8"))
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["mode"], "synthetic_evaluator")
            self.assertEqual(manifest["n_cells"], 120)

    def test_environment_report_is_read_only_and_structured(self):
        report = collect_environment()

        self.assertIn("python", report)
        self.assertIn("packages", report)
        self.assertIn("executables", report)
        self.assertIn("saturn", report["packages"])
        self.assertIn("samap", report["packages"])
        self.assertIn("scvi", report["packages"])

    def test_environment_report_can_be_written_without_installing(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_environment_report(Path(tmp) / "environment.json")

            self.assertTrue(Path(path).exists())
            payload = json.loads(Path(path).read_text(encoding="utf-8"))
            self.assertIn("packages", payload)
            self.assertEqual(payload["side_effects"], [])

    def test_metadata_contract_accepts_minimal_cross_species_table(self):
        rows = [
            {"cell_id": "c1", "species": "sp1", "cell_type": "CM", "batch": "b1"},
            {"cell_id": "c2", "species": "sp1", "cell_type": "FB", "batch": "b1"},
            {"cell_id": "c3", "species": "sp2", "cell_type": "CM", "batch": "b2"},
            {"cell_id": "c4", "species": "sp2", "cell_type": "FB", "batch": "b2"},
        ]

        summary = validate_metadata(rows, min_species=2)

        self.assertEqual(summary["n_cells"], 4)
        self.assertEqual(summary["species"], ["sp1", "sp2"])
        self.assertEqual(summary["labels"], ["CM", "FB"])

    def test_metadata_contract_rejects_duplicate_ids_and_missing_labels(self):
        rows = [
            {"cell_id": "c1", "species": "sp1", "cell_type": "CM", "batch": "b1"},
            {"cell_id": "c1", "species": "sp2", "cell_type": "", "batch": "b2"},
        ]

        with self.assertRaises(InputContractError):
            validate_metadata(rows, min_species=2)

    def test_metadata_manifest_is_reproducible(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "metadata.tsv"
            source.write_text(
                "cell_id\tspecies\tcell_type\tbatch\n"
                "c1\tsp1\tCM\tb1\n"
                "c2\tsp2\tCM\tb2\n",
                encoding="utf-8",
            )
            output = write_metadata_manifest(source, Path(tmp) / "manifest.json", min_species=2)
            payload = json.loads(Path(output).read_text(encoding="utf-8"))

            self.assertEqual(payload["n_cells"], 2)
            self.assertEqual(payload["source_format"], "tsv")
            self.assertEqual(len(payload["sha256"]), 64)

    def test_budget_plan_estimates_single_gpu_trial_under_cap(self):
        plan = load_plan()

        result = evaluate_trial(plan, profile_name="4090x1", hard_stop_minutes=25, reserved_minutes=30)

        self.assertAlmostEqual(result["hard_stop_cost_cny"], 7.25, places=2)
        self.assertAlmostEqual(result["reserved_cost_cny"], 8.70, places=2)
        self.assertTrue(result["within_cost_cap"])
        self.assertEqual(result["profile"]["gpu_count"], 1)

    def test_budget_plan_rejects_unknown_profile_and_over_cap(self):
        plan = load_plan()

        with self.assertRaises(BudgetPlanError):
            evaluate_trial(plan, profile_name="unknown", hard_stop_minutes=25, reserved_minutes=30)

        result = evaluate_trial(plan, profile_name="4090x2", hard_stop_minutes=25, reserved_minutes=30)

        self.assertFalse(result["within_cost_cap"])
        self.assertGreater(result["reserved_cost_cny"], plan["trial_policy"]["max_trial_cost_cny"])

    def test_run_artifact_contract_accepts_successful_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in REQUIRED_ARTIFACTS:
                (root / name).write_text("placeholder\n", encoding="utf-8")

            result = validate_run_artifacts(root, run_status="success")

            self.assertEqual(result["missing"], [])
            self.assertEqual(result["empty"], [])
            self.assertFalse(result["failure_reason_required"])

    def test_run_artifact_contract_requires_reason_for_failed_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in REQUIRED_ARTIFACTS:
                if name != "failure_reason.txt":
                    (root / name).write_text("placeholder\n", encoding="utf-8")

            with self.assertRaises(ArtifactContractError):
                validate_run_artifacts(root, run_status="failed")

            (root / "failure_reason.txt").write_text("OOM during latent integration\n", encoding="utf-8")
            result = validate_run_artifacts(root, run_status="failed")

            self.assertEqual(result["missing"], [])
            self.assertTrue(result["failure_reason_required"])

    def test_agent_matrix_stays_pending_until_evidence_is_recorded(self):
        matrix = load_agent_matrix()

        result = validate_agent_matrix(matrix)

        self.assertEqual(result["methods"], ["SATURN", "SAMap", "scVI"])
        self.assertEqual(result["pending_methods"], ["SATURN", "SAMap", "scVI"])
        self.assertFalse(result["ready_for_comparison"])

    def test_agent_matrix_rejects_score_without_evidence(self):
        matrix = load_agent_matrix()
        matrix["methods"]["SATURN"]["dimensions"]["documentation_clarity"]["score"] = 3

        with self.assertRaises(AgentMatrixError):
            validate_agent_matrix(matrix)

    def test_startup_preflight_is_blocked_until_course_confirmation(self):
        preflight = load_preflight()

        result = validate_preflight(preflight)

        self.assertFalse(result["ready_for_execution"])
        self.assertIn("approval_status", result["blocking_items"])
        self.assertIn("heart_data_path", result["blocking_items"])

    def test_startup_preflight_accepts_complete_confirmed_record(self):
        preflight = load_preflight()
        preflight["approval_status"] = "confirmed"
        preflight["heart_data_path"] = "/dcs/course/heart"
        preflight["heart_file_format"] = "h5ad"
        preflight["heart_metadata_fields"] = {
            "species": "species",
            "cell_type": "cell_type",
            "batch": "batch",
            "gold_label": "paper_label",
        }
        preflight["heart_allowed_subsets"] = ["3_species", "8_species", "16_species"]
        preflight["lbspa_snRNA_path"] = "/dcs/course/lbspa_snRNA"
        preflight["lbspa_spatial_policy"] = "second_phase_only"
        preflight["image_recommendation"] = "SATURN--22"
        preflight["image_versions"] = {"SATURN": "locked", "SAMap": "locked", "scVI": "locked"}
        preflight["kbet_implementation"] = "official-package"
        preflight["kbet_version"] = "1.0.0"
        preflight["readonly_sample_command"] = "inspect-object --path <mounted-path>"
        preflight["evidence"] = {
            "course_admin_reply": "docs/course-admin-confirmation.txt",
            "recorded_at": "2026-09-10T10:00:00+08:00",
        }

        result = validate_preflight(preflight)

        self.assertTrue(result["ready_for_execution"])
        self.assertEqual(result["blocking_items"], [])


if __name__ == "__main__":
    unittest.main()
