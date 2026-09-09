"""Validate the course 5 experiment plan and its safety boundaries."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAN = ROOT / "config" / "benchmark-plan.json"
REQUIRED_METHODS = ("SATURN", "SAMap", "scVI")
REQUIRED_PROHIBITIONS = (
    "create_cloud_instance",
    "start_cloud_task",
    "upload_user_data",
    "download_large_dataset",
    "install_packages_on_dcs",
)
REQUIRED_METRICS = (
    "macro_f1",
    "kbet",
    "ilisi",
    "silhouette",
    "wall_time_seconds",
    "peak_memory_gb",
)
REQUIRED_ARTIFACTS = (
    "input_manifest.tsv",
    "ortholog_manifest.json",
    "parameters.json",
    "package_versions.txt",
    "stdout_stderr.log",
    "metrics.json",
    "resource_usage.json",
    "failure_reason.txt",
)


class PlanContractError(ValueError):
    """Raised when an experiment plan weakens a required boundary."""


def load_benchmark_plan(path: Path | None = None) -> dict[str, Any]:
    source = path or DEFAULT_PLAN
    if not source.is_file():
        raise FileNotFoundError(source)
    try:
        plan = json.loads(source.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PlanContractError(f"invalid JSON in {source}: {exc}") from exc
    if not isinstance(plan, dict):
        raise PlanContractError("benchmark plan must be an object")
    return plan


def _positive_number(value: Any, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        raise PlanContractError(f"{name} must be positive")


def validate_benchmark_plan(plan: dict[str, Any]) -> dict[str, Any]:
    """Validate fixed methods, controls, limits, and prohibited cloud actions."""
    if plan.get("project") != "course5_cross_species_integration":
        raise PlanContractError("unexpected project name")
    if plan.get("status") != "preflight_only":
        raise PlanContractError("plan status must remain preflight_only")

    prohibited = plan.get("prohibited_until_explicit_approval")
    if not isinstance(prohibited, list) or not set(REQUIRED_PROHIBITIONS).issubset(prohibited):
        raise PlanContractError("required cloud prohibitions are missing")

    methods = plan.get("methods")
    if not isinstance(methods, list):
        raise PlanContractError("methods must be a list")
    method_names = [method.get("name") for method in methods if isinstance(method, dict)]
    if method_names != list(REQUIRED_METHODS):
        raise PlanContractError(f"methods must be exactly {list(REQUIRED_METHODS)} in order")

    controls = plan.get("fixed_controls")
    if not isinstance(controls, dict):
        raise PlanContractError("fixed_controls must be an object")
    if controls.get("random_seeds") != [7, 17, 27]:
        raise PlanContractError("random seeds must remain [7, 17, 27]")
    if controls.get("hvg_policy") != "fit_each_training_split_only":
        raise PlanContractError("HVG policy must fit each training split only")
    if controls.get("label_transfer") != "leave_one_species_out":
        raise PlanContractError("label transfer must be leave-one-species-out")
    if controls.get("neighbor_count") != 15:
        raise PlanContractError("neighbor_count must remain 15")
    metrics = controls.get("metrics")
    if not isinstance(metrics, list) or not set(REQUIRED_METRICS).issubset(metrics):
        raise PlanContractError("required benchmark metrics are missing")

    stopping = plan.get("stopping_rules")
    if not isinstance(stopping, dict):
        raise PlanContractError("stopping_rules must be an object")
    _positive_number(stopping.get("max_trial_minutes"), "max_trial_minutes")
    _positive_number(stopping.get("max_peak_memory_gb"), "max_peak_memory_gb")
    _positive_number(stopping.get("max_trial_cost_cny"), "max_trial_cost_cny")
    if stopping["max_trial_minutes"] > 25:
        raise PlanContractError("max_trial_minutes cannot exceed 25")
    if stopping["max_peak_memory_gb"] > 75:
        raise PlanContractError("max_peak_memory_gb cannot exceed 75")
    if stopping["max_trial_cost_cny"] > 10:
        raise PlanContractError("max_trial_cost_cny cannot exceed 10")
    if stopping.get("stop_instance_after_run") is not True:
        raise PlanContractError("stop_instance_after_run must remain true")

    datasets = plan.get("datasets")
    if not isinstance(datasets, dict):
        raise PlanContractError("datasets must be an object")
    expected_species = {"heart_near": 3, "heart_mid": 8, "heart_full": 16}
    for name, count in expected_species.items():
        if not isinstance(datasets.get(name), dict) or datasets[name].get("species_count") != count:
            raise PlanContractError(f"{name} must contain species_count={count}")
    lbspa = datasets.get("lbspa_cross_phylum")
    if not isinstance(lbspa, dict) or lbspa.get("modality") != "snRNA_only_first" or lbspa.get("ortholog_policy") != "one_to_one_only":
        raise PlanContractError("LBSPA must start with snRNA and one-to-one orthologs")

    artifacts = plan.get("required_artifacts_per_run")
    if not isinstance(artifacts, list) or not set(REQUIRED_ARTIFACTS).issubset(artifacts):
        raise PlanContractError("required run artifacts are incomplete")
    return {
        "valid": True,
        "project": plan["project"],
        "status": plan["status"],
        "methods": method_names,
        "prohibitions": list(REQUIRED_PROHIBITIONS),
        "side_effects": [],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    args = parser.parse_args()
    try:
        result = validate_benchmark_plan(load_benchmark_plan(args.plan))
    except (PlanContractError, FileNotFoundError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, ensure_ascii=True, indent=2))
        raise SystemExit(2) from exc
    print(json.dumps(result, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
