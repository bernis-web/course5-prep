"""Estimate DCS trial costs from a checked-in, read-only price plan."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAN = ROOT / "config" / "dcs-budget-plan.json"


class BudgetPlanError(ValueError):
    """Raised when a budget plan is missing or internally inconsistent."""


def load_plan(path: Path | None = None) -> dict[str, Any]:
    """Read and validate a local budget plan without contacting DCS."""
    source = path or DEFAULT_PLAN
    if not source.is_file():
        raise FileNotFoundError(source)
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise BudgetPlanError(f"invalid JSON in {source}: {exc}") from exc
    if not isinstance(payload, dict):
        raise BudgetPlanError("budget plan root must be an object")
    policy = payload.get("trial_policy")
    profiles = payload.get("profiles")
    if not isinstance(policy, dict) or not isinstance(profiles, dict) or not profiles:
        raise BudgetPlanError("budget plan requires trial_policy and profiles")
    for key in ("max_trial_minutes", "reserved_minutes", "max_trial_cost_cny"):
        value = policy.get(key)
        if not isinstance(value, (int, float)) or value <= 0:
            raise BudgetPlanError(f"trial_policy.{key} must be positive")
    for name, profile in profiles.items():
        if not isinstance(profile, dict):
            raise BudgetPlanError(f"profile {name} must be an object")
        rate = profile.get("hourly_rate_cny")
        if not isinstance(rate, (int, float)) or rate <= 0:
            raise BudgetPlanError(f"profile {name} has invalid hourly_rate_cny")
        if not isinstance(profile.get("gpu_count"), int) or profile["gpu_count"] < 1:
            raise BudgetPlanError(f"profile {name} has invalid gpu_count")
    return payload


def evaluate_trial(
    plan: dict[str, Any],
    profile_name: str,
    hard_stop_minutes: float,
    reserved_minutes: float,
) -> dict[str, Any]:
    """Return deterministic cost estimates and cap checks for one trial."""
    if hard_stop_minutes <= 0 or reserved_minutes <= 0:
        raise BudgetPlanError("trial durations must be positive")
    profiles = plan.get("profiles", {})
    profile = profiles.get(profile_name)
    if not isinstance(profile, dict):
        raise BudgetPlanError(f"unknown profile: {profile_name}")
    rate = float(profile["hourly_rate_cny"])
    cap = float(plan["trial_policy"]["max_trial_cost_cny"])
    hard_stop_cost = round(rate * hard_stop_minutes / 60.0, 2)
    reserved_cost = round(rate * reserved_minutes / 60.0, 2)
    balance = plan.get("account_balance_cny")
    return {
        "currency": plan.get("currency", "CNY"),
        "profile_name": profile_name,
        "profile": profile,
        "hourly_rate_cny": rate,
        "hard_stop_minutes": hard_stop_minutes,
        "hard_stop_cost_cny": hard_stop_cost,
        "reserved_minutes": reserved_minutes,
        "reserved_cost_cny": reserved_cost,
        "max_trial_cost_cny": cap,
        "within_cost_cap": reserved_cost <= cap,
        "estimated_balance_after_reserved_cny": round(float(balance) - reserved_cost, 2)
        if isinstance(balance, (int, float))
        else None,
        "side_effects": [],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--profile", default="4090x1")
    parser.add_argument("--hard-stop-minutes", type=float)
    parser.add_argument("--reserved-minutes", type=float)
    args = parser.parse_args()
    plan = load_plan(args.plan)
    policy = plan["trial_policy"]
    result = evaluate_trial(
        plan,
        profile_name=args.profile,
        hard_stop_minutes=float(args.hard_stop_minutes or policy["max_trial_minutes"]),
        reserved_minutes=float(args.reserved_minutes or policy["reserved_minutes"]),
    )
    print(json.dumps(result, ensure_ascii=True, indent=2))
    if not result["within_cost_cap"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
