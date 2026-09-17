"""Estimate a four-account DCS planning budget without contacting DCS."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from budget_check import load_plan


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEAM_PLAN = ROOT / "config" / "team-budget-plan.json"
DEFAULT_BUDGET_PLAN = ROOT / "config" / "dcs-budget-plan.json"


class TeamBudgetPlanError(ValueError):
    """Raised when the team budget plan is missing or inconsistent."""


def load_team_plan(path: Path | None = None) -> dict[str, Any]:
    """Read a team planning budget; this function never contacts DCS."""
    source = path or DEFAULT_TEAM_PLAN
    if not source.is_file():
        raise FileNotFoundError(source)
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise TeamBudgetPlanError(f"invalid JSON in {source}: {exc}") from exc
    if not isinstance(payload, dict):
        raise TeamBudgetPlanError("team budget plan root must be an object")

    account_count = payload.get("account_count")
    per_account = payload.get("per_account_credit_cny")
    total_nominal = payload.get("total_nominal_budget_cny")
    reserve = payload.get("reserve_cny")
    operational_cap = payload.get("operational_spend_cap_cny")
    if not isinstance(account_count, int) or account_count < 1:
        raise TeamBudgetPlanError("account_count must be a positive integer")
    for name, value in (
        ("per_account_credit_cny", per_account),
        ("total_nominal_budget_cny", total_nominal),
        ("reserve_cny", reserve),
        ("operational_spend_cap_cny", operational_cap),
    ):
        if not isinstance(value, (int, float)) or value < 0:
            raise TeamBudgetPlanError(f"{name} must be non-negative")
    expected_total = round(account_count * float(per_account), 2)
    if round(float(total_nominal), 2) != expected_total:
        raise TeamBudgetPlanError("total_nominal_budget_cny must equal account_count * per_account_credit_cny")
    if float(reserve) >= float(total_nominal):
        raise TeamBudgetPlanError("reserve_cny must be less than total_nominal_budget_cny")
    expected_cap = round(float(total_nominal) - float(reserve), 2)
    if round(float(operational_cap), 2) != expected_cap:
        raise TeamBudgetPlanError("operational_spend_cap_cny must equal total_nominal_budget_cny - reserve_cny")
    if payload.get("account_merge_status") not in {"not_verified", "verified", "unknown"}:
        raise TeamBudgetPlanError("account_merge_status must be not_verified, verified, or unknown")
    return payload


def evaluate_team_budget(
    team_plan: dict[str, Any],
    budget_plan: dict[str, Any],
    profile_name: str,
    reserved_minutes: float,
    runs: int,
) -> dict[str, Any]:
    """Estimate cost for repeated runs and compare separate/team limits."""
    if reserved_minutes <= 0:
        raise TeamBudgetPlanError("reserved_minutes must be positive")
    if not isinstance(runs, int) or runs < 1:
        raise TeamBudgetPlanError("runs must be a positive integer")
    profile = budget_plan.get("profiles", {}).get(profile_name)
    if not isinstance(profile, dict):
        raise TeamBudgetPlanError(f"unknown profile: {profile_name}")
    rate = profile.get("hourly_rate_cny")
    if not isinstance(rate, (int, float)) or rate <= 0:
        raise TeamBudgetPlanError(f"profile {profile_name} has invalid hourly_rate_cny")
    cost_per_run = round(float(rate) * reserved_minutes / 60.0, 2)
    estimated_cost = round(cost_per_run * runs, 2)
    per_account_credit = float(team_plan["per_account_credit_cny"])
    per_account_reserve = float(team_plan["reserve_cny"]) / team_plan["account_count"]
    per_account_operational_cap = round(per_account_credit - per_account_reserve, 2)
    team_cap = float(team_plan["operational_spend_cap_cny"])
    runs_on_busiest_account = (runs + team_plan["account_count"] - 1) // team_plan["account_count"]
    max_runs_per_account = math.floor(per_account_operational_cap / cost_per_run)
    max_distributable_runs = max_runs_per_account * team_plan["account_count"]
    estimated_cost_per_account = round(estimated_cost / team_plan["account_count"], 2)
    max_estimated_cost_per_account = round(cost_per_run * runs_on_busiest_account, 2)
    return {
        "currency": team_plan.get("currency", "CNY"),
        "profile_name": profile_name,
        "profile": profile,
        "account_count": team_plan["account_count"],
        "per_account_credit_cny": per_account_credit,
        "per_account_reserve_cny": round(per_account_reserve, 2),
        "per_account_operational_cap_cny": per_account_operational_cap,
        "total_nominal_budget_cny": float(team_plan["total_nominal_budget_cny"]),
        "reserve_cny": float(team_plan["reserve_cny"]),
        "operational_spend_cap_cny": team_cap,
        "account_merge_status": team_plan["account_merge_status"],
        "reserved_minutes": reserved_minutes,
        "runs": runs,
        "cost_per_run_cny": cost_per_run,
        "max_runs_per_account": max_runs_per_account,
        "max_distributable_runs": max_distributable_runs,
        "estimated_cost_cny": estimated_cost,
        "runs_on_busiest_account": runs_on_busiest_account,
        "estimated_cost_per_account_cny": estimated_cost_per_account,
        "max_estimated_cost_per_account_cny": max_estimated_cost_per_account,
        "estimated_team_balance_after_cny": round(team_cap - estimated_cost, 2),
        "within_single_account_credit": estimated_cost <= per_account_credit,
        "requires_multiple_accounts": estimated_cost > per_account_credit,
        "within_account_capacity": max_estimated_cost_per_account <= per_account_operational_cap,
        "within_team_spend_cap": estimated_cost <= team_cap,
        "side_effects": [],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--team-plan", type=Path, default=DEFAULT_TEAM_PLAN)
    parser.add_argument("--budget-plan", type=Path, default=DEFAULT_BUDGET_PLAN)
    parser.add_argument("--profile", default="4090x1")
    parser.add_argument("--reserved-minutes", type=float)
    parser.add_argument("--runs", type=int, default=1)
    args = parser.parse_args()

    team_plan = load_team_plan(args.team_plan)
    budget_plan = load_plan(args.budget_plan)
    default_minutes = team_plan["expanded_trial_policy"]["default_reserved_minutes"]
    result = evaluate_team_budget(
        team_plan,
        budget_plan,
        profile_name=args.profile,
        reserved_minutes=float(args.reserved_minutes or default_minutes),
        runs=args.runs,
    )
    print(json.dumps(result, ensure_ascii=True, indent=2))
    if not result["within_account_capacity"] or not result["within_team_spend_cap"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
