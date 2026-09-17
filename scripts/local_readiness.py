"""Build a local-only readiness report for the course 5 benchmark.

This command reads checked-in plans and the current Python environment. It does
not contact DCS, start an instance, upload data, or install packages.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from budget_check import BudgetPlanError, evaluate_trial, load_plan
from environment_check import collect_environment
from environment_contract import EnvironmentContractError, evaluate_environment, load_environment_plan
from plan_contract import PlanContractError, load_benchmark_plan, validate_benchmark_plan
from source_manifest_check import DEFAULT_MANIFEST, SourceManifestError, verify_manifest
from startup_preflight import DEFAULT_PHASE, PreflightError, load_preflight, validate_preflight


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "smoke-output" / "local-readiness.json"


def build_readiness_report(
    budget_profile: str = "4090x1",
    environment_profile: str = "SATURN--22",
    phase: str = DEFAULT_PHASE,
    benchmark_plan_path: Path | None = None,
    budget_plan_path: Path | None = None,
    environment_plan_path: Path | None = None,
    environment_report_path: Path | None = None,
    preflight_path: Path | None = None,
    source_root: Path | None = None,
    source_manifest_path: Path | None = None,
) -> dict[str, Any]:
    """Return a deterministic readiness summary without remote side effects."""
    benchmark_plan = load_benchmark_plan(benchmark_plan_path)
    plan_result = validate_benchmark_plan(benchmark_plan)

    budget_plan = load_plan(budget_plan_path)
    policy = budget_plan["trial_policy"]
    budget_result = evaluate_trial(
        budget_plan,
        profile_name=budget_profile,
        hard_stop_minutes=float(policy["max_trial_minutes"]),
        reserved_minutes=float(policy["reserved_minutes"]),
    )

    preflight_result = validate_preflight(load_preflight(preflight_path), phase=phase)

    if environment_report_path is None:
        environment_report = collect_environment()
    else:
        try:
            environment_report = json.loads(environment_report_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise EnvironmentContractError(
                f"cannot read environment report {environment_report_path}: {exc}"
            ) from exc
    environment_result = evaluate_environment(
        environment_report,
        profile_name=environment_profile,
        plan=load_environment_plan(environment_plan_path),
    )

    if source_root is None:
        source_result: dict[str, Any] = {
            "valid": None,
            "scope": "source_files",
            "status": "not_checked",
            "side_effects": [],
        }
    else:
        try:
            source_result = verify_manifest(source_root, source_manifest_path or DEFAULT_MANIFEST)
        except (OSError, SourceManifestError) as exc:
            source_result = {
                "valid": False,
                "scope": "source_files",
                "status": "error",
                "error": str(exc),
                "side_effects": [],
            }

    blocking_items: list[str] = []
    if not budget_result["within_cost_cap"]:
        blocking_items.append("budget:trial_cost_cap")
    if source_result.get("valid") is False:
        blocking_items.append("source_materials")
    blocking_items.extend(f"startup:{item}" for item in preflight_result["blocking_items"])
    blocking_items.extend(f"environment:{item}" for item in environment_result["blocking_items"])

    return {
        "valid": True,
        "ready_for_execution": not blocking_items,
        "scope": "local_only",
        "budget_profile": budget_profile,
        "environment_profile": environment_profile,
        "target_phase": phase,
        "status": plan_result["status"],
        "blocking_items": list(dict.fromkeys(blocking_items)),
        "checks": {
            "benchmark_plan": plan_result,
            "budget": budget_result,
            "startup_preflight": preflight_result,
            "environment": environment_result,
            "source_materials": source_result,
        },
        "remote_actions": [],
        "side_effects": [],
    }


def _write_report(report: dict[str, Any], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=True, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--budget-profile", default="4090x1")
    parser.add_argument("--environment-profile", default="SATURN--22")
    parser.add_argument("--phase", default=DEFAULT_PHASE)
    parser.add_argument("--environment-report", type=Path)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--source-root", type=Path)
    parser.add_argument("--source-manifest", type=Path)
    args = parser.parse_args()

    try:
        report = build_readiness_report(
            budget_profile=args.budget_profile,
            environment_profile=args.environment_profile,
            phase=args.phase,
            environment_report_path=args.environment_report,
            source_root=args.source_root,
            source_manifest_path=args.source_manifest,
        )
    except (BudgetPlanError, EnvironmentContractError, PlanContractError, PreflightError, FileNotFoundError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, ensure_ascii=True, indent=2))
        raise SystemExit(3) from exc

    _write_report(report, args.output)
    print(json.dumps(report, ensure_ascii=True, indent=2))
    if not report["ready_for_execution"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
