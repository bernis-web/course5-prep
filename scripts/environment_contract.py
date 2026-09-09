"""Evaluate a read-only environment report against candidate image requirements."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAN = ROOT / "config" / "environment-compatibility-plan.json"


class EnvironmentContractError(ValueError):
    """Raised when an environment report or compatibility plan is malformed."""


def load_environment_plan(path: Path | None = None) -> dict[str, Any]:
    source = path or DEFAULT_PLAN
    if not source.is_file():
        raise FileNotFoundError(source)
    try:
        plan = json.loads(source.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise EnvironmentContractError(f"invalid JSON in {source}: {exc}") from exc
    if not isinstance(plan, dict) or not isinstance(plan.get("profiles"), dict):
        raise EnvironmentContractError("environment plan requires a profiles object")
    return plan


def evaluate_environment(
    report: dict[str, Any], profile_name: str, plan: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Return blockers without installing, importing, or probing anything."""
    compatibility = plan or load_environment_plan()
    profiles = compatibility.get("profiles", {})
    profile = profiles.get(profile_name)
    if not isinstance(profile, dict):
        raise EnvironmentContractError(f"unknown environment profile: {profile_name}")
    packages = report.get("packages")
    hardware = report.get("hardware")
    if not isinstance(packages, dict) or not isinstance(hardware, dict):
        raise EnvironmentContractError("environment report requires packages and hardware")

    blockers: list[str] = []
    for package_name in profile.get("required_packages", []):
        package = packages.get(package_name)
        if not isinstance(package, dict) or not package.get("available"):
            blockers.append(f"package:{package_name}:unavailable")
        elif not package.get("version"):
            blockers.append(f"package:{package_name}:version_missing")

    gpu = hardware.get("gpu")
    if not isinstance(gpu, dict):
        gpu = {"available": False, "devices": []}
    if profile.get("gpu_required") and not gpu.get("available"):
        blockers.append("gpu:unavailable")
    if profile.get("gpu_required") and not gpu.get("devices"):
        blockers.append("gpu:device_record_missing")

    return {
        "profile_name": profile_name,
        "report_scope": report.get("scope", "unspecified"),
        "role": profile.get("role"),
        "ready_for_execution": not blockers,
        "blocking_items": list(dict.fromkeys(blockers)),
        "required_packages": list(profile.get("required_packages", [])),
        "gpu_required": bool(profile.get("gpu_required")),
        "page_reported_versions": profile.get("page_reported_versions", {}),
        "unresolved": profile.get("unresolved", []),
        "side_effects": [],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("environment_report", type=Path)
    parser.add_argument("--profile", default="SATURN--22")
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    args = parser.parse_args()
    try:
        report = json.loads(args.environment_report.read_text(encoding="utf-8"))
        result = evaluate_environment(report, profile_name=args.profile, plan=load_environment_plan(args.plan))
    except (OSError, json.JSONDecodeError, EnvironmentContractError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, ensure_ascii=True, indent=2))
        raise SystemExit(2) from exc
    print(json.dumps({"valid": True, **result}, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
