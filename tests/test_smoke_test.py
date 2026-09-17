import json
import hashlib
import subprocess
import sys
import tempfile
import unittest
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from environment_check import collect_environment, write_environment_report  # noqa: E402
from environment_contract import EnvironmentContractError, evaluate_environment, load_environment_plan  # noqa: E402
from input_contract import InputContractError, validate_metadata, write_metadata_manifest  # noqa: E402
from ortholog_contract import OrthologContractError, read_orthologs, validate_orthologs, write_ortholog_manifest  # noqa: E402
from budget_check import BudgetPlanError, evaluate_trial, load_plan  # noqa: E402
from team_budget_check import TeamBudgetPlanError, evaluate_team_budget, load_team_plan  # noqa: E402
from run_artifacts import ArtifactContractError, REQUIRED_ARTIFACTS, validate_run_artifacts  # noqa: E402
from result_contract import ResultContractError, validate_result  # noqa: E402
from plan_contract import PlanContractError, load_benchmark_plan, validate_benchmark_plan  # noqa: E402
from local_readiness import build_readiness_report  # noqa: E402
from agent_evaluation import AgentMatrixError, load_agent_matrix, validate_agent_matrix  # noqa: E402
from startup_preflight import PreflightError, load_preflight, validate_preflight  # noqa: E402
from dcs_readonly_probe import probe_runtime, write_probe  # noqa: E402
from source_manifest_check import verify_manifest, write_report  # noqa: E402
from smoke_test import (  # noqa: E402
    evaluate_embedding,
    evaluate_labels,
    evaluate_leave_one_species_out,
    run_smoke_test,
)


class SmokeEvaluatorTests(unittest.TestCase):
    def test_report_word_template_is_readable_and_placeholder_only(self):
        root = Path(__file__).resolve().parents[1]
        template_path = root / "templates" / "course5-final-report-template.docx"

        self.assertTrue(template_path.is_file())
        with zipfile.ZipFile(template_path) as archive:
            document_xml = archive.read("word/document.xml").decode("utf-8")
            styles_xml = archive.read("word/styles.xml")
            core_xml = archive.read("docProps/core.xml").decode("utf-8")

        self.assertIn("跨物种细胞类型整合工具评测", document_xml)
        self.assertIn("2至3物种流程试跑", document_xml)
        self.assertIn("场景化选型指南", document_xml)
        self.assertIn("待填写", document_xml)
        self.assertNotIn("479,483", document_xml)
        self.assertNotIn("示例结果", document_xml)
        self.assertNotIn("<w:pageBreakBefore", document_xml)
        self.assertIn("<dc:creator>课题5小组</dc:creator>", core_xml)
        self.assertNotIn("<dc:creator>python-docx</dc:creator>", core_xml)

        word_ns = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        ns = {"w": word_ns}
        styles_root = ET.fromstring(styles_xml)
        title_style = next(
            style
            for style in styles_root.findall("w:style", ns)
            if style.get(f"{{{word_ns}}}styleId") == "Title"
        )
        self.assertIsNone(title_style.find("w:pPr/w:pBdr", ns))
        document_root = ET.fromstring(document_xml)
        page_size = document_root.find(".//w:sectPr/w:pgSz", ns)
        self.assertIsNotNone(page_size)
        self.assertEqual(page_size.get(f"{{{word_ns}}}w"), "11906")
        self.assertEqual(page_size.get(f"{{{word_ns}}}h"), "16838")

    def test_report_delivery_contract(self):
        root = Path(__file__).resolve().parents[1]
        delivery_path = root / "docs" / "report-delivery.md"
        template_path = root / "docs" / "report-template.md"

        self.assertTrue(delivery_path.is_file())
        self.assertTrue(template_path.is_file())
        delivery = delivery_path.read_text(encoding="utf-8")
        template = template_path.read_text(encoding="utf-8")

        self.assertIn("最终交付：`.docx`", delivery)
        self.assertIn("Markdown", delivery)
        self.assertIn("JSON", delivery)
        self.assertIn("不得编造真实实验结果", delivery)
        self.assertIn("python scripts/build_report_template.py", delivery)
        for heading in (
            "## 摘要",
            "## 数据与实验范围",
            "## 方法与公平性控制",
            "## 结果",
            "## 算力与成本",
            "## 局限性",
            "## 场景化选型指南",
            "## 附录",
        ):
            self.assertIn(heading, template)
        self.assertIn("smoke test 不能作为最终结果", template)

    def test_teacher_reply_phase_gates(self):
        plan = load_benchmark_plan()

        result = validate_benchmark_plan(plan)
        phase_policy = plan["phase_policy"]

        self.assertEqual(phase_policy["pilot_species_count_range"], [2, 3])
        self.assertEqual(
            phase_policy["later_relationship_coverage"],
            ["near", "far", "mixed_categories"],
        )
        self.assertEqual(phase_policy["primary_modality"], "scRNA")
        self.assertEqual(phase_policy["spatial_policy"], "out_of_primary_scope")
        self.assertEqual(
            phase_policy["snRNA_policy"],
            "small_followup_after_scRNA_conclusion",
        )
        relationship_matrix = plan["datasets"]["heart_relationship_matrix"]
        self.assertEqual(
            relationship_matrix["relationship_coverage"],
            ["near", "far", "mixed_categories"],
        )
        self.assertEqual(relationship_matrix["species_count_policy"], "selected_per_combination")
        self.assertEqual(plan["datasets"]["heart_mid"]["role"], "optional_eight_species_scaling_tier")
        self.assertEqual(result["phase_policy"], phase_policy)

    def test_plan_contract_rejects_spatial_data_in_primary_scope(self):
        plan = load_benchmark_plan()
        plan["phase_policy"]["spatial_policy"] = "primary_benchmark"

        with self.assertRaises(PlanContractError):
            validate_benchmark_plan(plan)

    def test_team_budget_plan_models_separate_credits_and_reserve(self):
        team_plan = load_team_plan()
        budget_plan = load_plan()

        result = evaluate_team_budget(
            team_plan,
            budget_plan,
            profile_name="4090x1",
            reserved_minutes=60,
            runs=1,
        )

        self.assertEqual(result["account_count"], 4)
        self.assertEqual(result["total_nominal_budget_cny"], 400.0)
        self.assertEqual(result["operational_spend_cap_cny"], 320.0)
        self.assertAlmostEqual(result["estimated_cost_cny"], 17.4, places=2)
        self.assertTrue(result["within_single_account_credit"])
        self.assertTrue(result["within_team_spend_cap"])
        self.assertEqual(result["account_merge_status"], "not_verified")

    def test_team_budget_rejects_invalid_run_count(self):
        team_plan = load_team_plan()
        budget_plan = load_plan()

        with self.assertRaises(TeamBudgetPlanError):
            evaluate_team_budget(
                team_plan,
                budget_plan,
                profile_name="4090x1",
                reserved_minutes=60,
                runs=0,
            )

    def test_team_budget_can_distribute_runs_across_separate_accounts(self):
        team_plan = load_team_plan()
        budget_plan = load_plan()

        result = evaluate_team_budget(
            team_plan,
            budget_plan,
            profile_name="4090x1",
            reserved_minutes=60,
            runs=16,
        )

        self.assertAlmostEqual(result["estimated_cost_cny"], 278.4, places=2)
        self.assertAlmostEqual(result["estimated_cost_per_account_cny"], 69.6, places=2)
        self.assertTrue(result["within_account_capacity"])
        self.assertTrue(result["within_team_spend_cap"])

    def test_team_budget_rejects_runs_that_exceed_per_account_reserve(self):
        team_plan = load_team_plan()
        budget_plan = load_plan()

        result = evaluate_team_budget(
            team_plan,
            budget_plan,
            profile_name="4090x1",
            reserved_minutes=60,
            runs=17,
        )

        self.assertFalse(result["within_account_capacity"])
        self.assertTrue(result["within_team_spend_cap"])

    def test_team_budget_reports_max_distributable_runs(self):
        team_plan = load_team_plan()
        budget_plan = load_plan()

        one_gpu = evaluate_team_budget(
            team_plan,
            budget_plan,
            profile_name="4090x1",
            reserved_minutes=60,
            runs=1,
        )
        two_gpu = evaluate_team_budget(
            team_plan,
            budget_plan,
            profile_name="4090x2",
            reserved_minutes=30,
            runs=1,
        )

        self.assertEqual(one_gpu["max_distributable_runs"], 16)
        self.assertEqual(two_gpu["max_distributable_runs"], 12)

    def test_source_manifest_check_verifies_files_without_exposing_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "materials"
            root.mkdir()
            source = root / "course.html"
            source.write_bytes(b"course material bytes")
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            manifest = Path(tmp) / "manifest.tsv"
            manifest.write_text(
                "filename\tformat\tbytes\tsha256\tchecked_at\n"
                f"course.html\thtml\t{source.stat().st_size}\t{digest}\t2026-09-10\n",
                encoding="utf-8",
            )

            result = verify_manifest(root, manifest)

            self.assertTrue(result["valid"])
            self.assertEqual(result["scope"], "source_files")
            self.assertEqual(result["files"][0]["status"], "ok")
            self.assertNotIn("content", result["files"][0])

            source.write_bytes(b"changed")
            changed = verify_manifest(root, manifest)
            self.assertFalse(changed["valid"])
            self.assertEqual(changed["files"][0]["status"], "mismatch")

            output = write_report(changed, Path(tmp) / "report.json")
            self.assertTrue(Path(output).exists())

    def test_dcs_readonly_probe_is_metadata_only_and_structured(self):
        report = probe_runtime()

        self.assertEqual(report["scope"], "runtime_probe")
        self.assertIn("saturn", report["packages"])
        self.assertIn("samap", report["packages"])
        self.assertIn("scvi", report["packages"])
        self.assertNotIn("scvi-tools", report["packages"])
        self.assertIn("nvidia-smi", report["commands"])
        self.assertIn("gpu", report)
        self.assertEqual(report["side_effects"], [])
        compatible = evaluate_environment(report, profile_name="SATURN--22")
        self.assertEqual(compatible["report_scope"], "runtime_probe")
        self.assertIn("package:saturn:unavailable", compatible["blocking_items"])

        with tempfile.TemporaryDirectory() as tmp:
            output = write_probe(Path(tmp) / "probe.json")
            payload = json.loads(Path(output).read_text(encoding="utf-8"))
            self.assertEqual(payload["scope"], "runtime_probe")
            self.assertEqual(payload["side_effects"], [])

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
            self.assertEqual(manifest["label_transfer_protocol"], "leave_one_species_out")
            self.assertEqual(manifest["label_transfer_estimator"], "synthetic_knn")
            metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
            self.assertEqual(metrics["label_transfer"]["evaluation_protocol"], "leave_one_species_out")
            self.assertEqual(metrics["label_transfer"]["n_folds"], 3)

    def test_leave_one_species_out_label_transfer_reports_each_fold(self):
        embedding = np.array(
            [
                [0.0, 0.0],
                [5.0, 5.0],
                [10.0, 0.0],
                [0.1, 0.0],
                [5.1, 5.0],
                [10.1, 0.0],
                [0.2, 0.0],
                [5.2, 5.0],
                [10.2, 0.0],
            ]
        )
        labels = np.array(["A", "B", "C"] * 3)
        species = np.array(["s1"] * 3 + ["s2"] * 3 + ["s3"] * 3)

        result = evaluate_leave_one_species_out(embedding, labels, species, neighbors=1)

        self.assertEqual(result["evaluation_protocol"], "leave_one_species_out")
        self.assertEqual(result["n_folds"], 3)
        self.assertEqual([fold["held_out_species"] for fold in result["folds"]], ["s1", "s2", "s3"])
        self.assertGreaterEqual(result["macro_f1"], 0.99)

    def test_environment_report_is_read_only_and_structured(self):
        report = collect_environment()

        self.assertEqual(report["scope"], "local_runtime")
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
            self.assertEqual(payload["scope"], "local_runtime")
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

    def test_budget_cli_rejects_profile_over_cost_cap(self):
        script = SCRIPT_DIR / "budget_check.py"

        result = subprocess.run(
            [sys.executable, str(script), "--profile", "4090x2"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn('"within_cost_cap": false', result.stdout)

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

    def test_public_accessions_are_recorded_without_unblocking_dcs_paths(self):
        preflight = load_preflight()

        references = preflight["public_data_references"]

        self.assertEqual(references["HEART"]["doi"], "10.1126/science.adw0855")
        self.assertEqual(references["HEART"]["cngb_accession"], "CNP0006537")
        self.assertEqual(references["LBSPA"]["doi"], "10.1126/science.aea2535")
        self.assertEqual(references["LBSPA"]["cngb_accession"], "CNP0007565")
        self.assertIsNone(preflight["heart_data_path"])
        self.assertIsNone(preflight["lbspa_snRNA_path"])
        self.assertFalse(validate_preflight(preflight)["ready_for_execution"])

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

    def test_heart_pilot_phase_does_not_block_on_empty_lbspa_snrna_path(self):
        preflight = load_preflight()

        result = validate_preflight(preflight, phase="heart_pilot")

        self.assertNotIn("lbspa_snRNA_path", result["blocking_items"])
        self.assertIn("heart_data_path", result["blocking_items"])
        self.assertFalse(result["ready_for_execution"])

    def test_lbspa_followup_phase_requires_snrna_path_and_scrna_conclusion_evidence(self):
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

        result = validate_preflight(preflight, phase="lbspa_followup")

        self.assertFalse(result["ready_for_execution"])
        self.assertIn("lbspa_snRNA_path", result["blocking_items"])
        self.assertIn("evidence.scrna_conclusion", result["blocking_items"])

    def test_unknown_preflight_phase_raises_preflight_error(self):
        preflight = load_preflight()

        with self.assertRaises(PreflightError):
            validate_preflight(preflight, phase="unknown_phase")

    def test_environment_contract_blocks_unavailable_or_unversioned_requirements(self):
        plan = load_environment_plan()
        report = {
            "scope": "synthetic_fixture",
            "packages": {
                "saturn": {"available": False, "version": None},
                "anndata": {"available": True, "version": "0.10.8"},
                "scanpy": {"available": True, "version": "1.10.3"},
                "scvi": {"available": True, "version": "1.1.6.post2"},
                "torch": {"available": True, "version": "2.6.0"},
            },
            "hardware": {"gpu": {"available": False, "devices": []}},
        }

        result = evaluate_environment(report, profile_name="SATURN--22", plan=plan)

        self.assertFalse(result["ready_for_execution"])
        self.assertIn("package:saturn:unavailable", result["blocking_items"])
        self.assertIn("gpu:unavailable", result["blocking_items"])
        self.assertEqual(result["report_scope"], "synthetic_fixture")

    def test_environment_contract_accepts_complete_profile(self):
        plan = load_environment_plan()
        required = plan["profiles"]["SATURN--22"]["required_packages"]
        report = {
            "packages": {name: {"available": True, "version": "1.0.0"} for name in required},
            "hardware": {"gpu": {"available": True, "devices": ["RTX 4090, 24 GB, 550.0"]}},
        }

        result = evaluate_environment(report, profile_name="SATURN--22", plan=plan)

        self.assertTrue(result["ready_for_execution"])
        self.assertEqual(result["blocking_items"], [])

    def test_ortholog_contract_accepts_one_to_one_pairs(self):
        rows = [
            {"species_a": "lamprey", "gene_a": "g1", "species_b": "mouse", "gene_b": "m1"},
            {"species_a": "lamprey", "gene_a": "g2", "species_b": "mouse", "gene_b": "m2"},
            {"species_a": "lamprey", "gene_a": "g1", "species_b": "zebrafish", "gene_b": "z1"},
        ]

        result = validate_orthologs(rows)

        self.assertEqual(result["n_pairs"], 3)
        self.assertEqual(result["species_pairs"], ["lamprey--mouse", "lamprey--zebrafish"])

    def test_ortholog_contract_rejects_duplicate_gene_mapping(self):
        rows = [
            {"species_a": "lamprey", "gene_a": "g1", "species_b": "mouse", "gene_b": "m1"},
            {"species_a": "mouse", "gene_a": "m2", "species_b": "lamprey", "gene_b": "g1"},
        ]

        with self.assertRaises(OrthologContractError):
            validate_orthologs(rows)

    def test_ortholog_manifest_is_reproducible(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "orthologs.tsv"
            source.write_text(
                "species_a\tgene_a\tspecies_b\tgene_b\n"
                "lamprey\tg1\tmouse\tm1\n",
                encoding="utf-8",
            )
            output = write_ortholog_manifest(source, Path(tmp) / "manifest.json")
            payload = json.loads(Path(output).read_text(encoding="utf-8"))

            self.assertEqual(payload["n_pairs"], 1)
            self.assertEqual(len(payload["sha256"]), 64)

    def test_run_artifact_contract_names_ortholog_manifest_as_json(self):
        self.assertIn("ortholog_manifest.json", REQUIRED_ARTIFACTS)
        self.assertNotIn("ortholog_manifest.tsv", REQUIRED_ARTIFACTS)

    def test_result_contract_accepts_complete_final_record(self):
        metrics = {
            "label_transfer": {
                "macro_f1": 0.82,
                "evaluation_protocol": "leave_one_species_out",
                "n_folds": 3,
            },
            "embedding": {
                "silhouette": 0.31,
                "ilisi": 1.8,
                "kbet_rejection_rate": 0.12,
                "kbet_method": "official-package",
                "kbet_implementation": "example-kbet-package",
                "kbet_version": "example-version",
            },
        }
        resources = {
            "wall_time_seconds": 412.5,
            "peak_memory_gb": 42.0,
            "gpu_count": 1,
            "gpu_name": "RTX 4090",
            "cost_cny": 2.1,
            "cost_source": "DCS billing record",
        }

        result = validate_result(metrics, resources, stage="final")

        self.assertTrue(result["valid"])
        self.assertEqual(result["kbet_method"], "official-package")
        self.assertEqual(result["kbet_implementation"], "example-kbet-package")
        self.assertEqual(result["kbet_version"], "example-version")

    def test_result_contract_requires_kbet_implementation_and_version_for_final_record(self):
        metrics = {
            "label_transfer": {
                "macro_f1": 0.82,
                "evaluation_protocol": "leave_one_species_out",
                "n_folds": 3,
            },
            "embedding": {
                "silhouette": 0.31,
                "ilisi": 1.8,
                "kbet_rejection_rate": 0.12,
                "kbet_method": "official-package",
            },
        }
        resources = {
            "wall_time_seconds": 412.5,
            "peak_memory_gb": 42.0,
            "gpu_count": 1,
            "gpu_name": "RTX 4090",
            "cost_cny": 2.1,
            "cost_source": "DCS billing record",
        }

        with self.assertRaisesRegex(ResultContractError, "kbet_implementation"):
            validate_result(metrics, resources, stage="final")

    def test_result_contract_requires_leave_one_species_out_protocol(self):
        metrics = {
            "label_transfer": {"macro_f1": 0.82, "n_folds": 3},
            "embedding": {
                "silhouette": 0.31,
                "ilisi": 1.8,
                "kbet_rejection_rate": 0.12,
                "kbet_method": "official-package",
            },
        }
        resources = {
            "wall_time_seconds": 412.5,
            "peak_memory_gb": 42.0,
            "gpu_count": 1,
            "gpu_name": "RTX 4090",
            "cost_cny": 2.1,
            "cost_source": "DCS billing record",
        }

        with self.assertRaises(ResultContractError):
            validate_result(metrics, resources, stage="final")

    def test_result_contract_rejects_proxy_kbet_in_final_record(self):
        metrics = {
            "label_transfer": {
                "macro_f1": 0.82,
                "evaluation_protocol": "leave_one_species_out",
                "n_folds": 3,
            },
            "embedding": {
                "silhouette": 0.31,
                "ilisi": 1.8,
                "kbet_rejection_rate": 0.12,
                "kbet_method": "chi2_neighborhood_proxy",
            },
        }
        resources = {
            "wall_time_seconds": 10,
            "peak_memory_gb": 1,
            "gpu_count": 0,
            "gpu_name": "none",
            "cost_cny": 0,
            "cost_source": "local smoke test",
        }

        with self.assertRaises(ResultContractError):
            validate_result(metrics, resources, stage="final")

    def test_benchmark_plan_preserves_safe_experiment_boundaries(self):
        plan = load_benchmark_plan()

        result = validate_benchmark_plan(plan)

        self.assertTrue(result["valid"])
        self.assertEqual(result["methods"], ["SATURN", "SAMap", "scVI"])
        self.assertEqual(result["status"], "preflight_only")

    def test_benchmark_plan_rejects_boundary_relaxation(self):
        plan = load_benchmark_plan()
        plan["status"] = "ready"

        with self.assertRaises(PlanContractError):
            validate_benchmark_plan(plan)

        plan = load_benchmark_plan()
        plan["stopping_rules"]["max_trial_cost_cny"] = 100

        with self.assertRaises(PlanContractError):
            validate_benchmark_plan(plan)

    def test_local_readiness_report_stays_blocked_until_course_confirmation(self):
        report = build_readiness_report()

        self.assertTrue(report["valid"])
        self.assertFalse(report["ready_for_execution"])
        self.assertIn("startup:approval_status", report["blocking_items"])
        self.assertEqual(report["scope"], "local_only")
        self.assertEqual(report["checks"]["environment"]["report_scope"], "local_runtime")
        self.assertEqual(report["side_effects"], [])

    def test_local_readiness_can_include_source_material_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "materials"
            root.mkdir()
            source = root / "course.html"
            source.write_bytes(b"course material bytes")
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            manifest = Path(tmp) / "manifest.tsv"
            manifest.write_text(
                "filename\tformat\tbytes\tsha256\tchecked_at\n"
                f"course.html\thtml\t{source.stat().st_size}\t{digest}\t2026-09-10\n",
                encoding="utf-8",
            )

            report = build_readiness_report(source_root=root, source_manifest_path=manifest)

            self.assertTrue(report["checks"]["source_materials"]["valid"])
            self.assertNotIn("source_materials", report["blocking_items"])

    def test_local_readiness_can_consume_runtime_probe_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            environment_path = Path(tmp) / "runtime-probe.json"
            environment_path.write_text(
                json.dumps(probe_runtime(), ensure_ascii=True), encoding="utf-8"
            )

            report = build_readiness_report(environment_report_path=environment_path)

            self.assertEqual(report["checks"]["environment"]["report_scope"], "runtime_probe")
            self.assertIn("environment:package:saturn:unavailable", report["blocking_items"])

    def test_local_readiness_report_blocks_over_budget_profile(self):
        report = build_readiness_report(budget_profile="4090x2")

        self.assertFalse(report["ready_for_execution"])
        self.assertIn("budget:trial_cost_cap", report["blocking_items"])

    def test_local_readiness_cli_writes_blocked_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "readiness.json"
            result = subprocess.run(
                [sys.executable, str(SCRIPT_DIR / "local_readiness.py"), "--output", str(output)],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )

            self.assertEqual(result.returncode, 2)
            self.assertTrue(output.is_file())
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertFalse(payload["ready_for_execution"])


if __name__ == "__main__":
    unittest.main()
