"""Validate evidence-backed Agent-friendliness scores for course 5 methods."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAN = ROOT / "config" / "agent-evaluation-plan.json"
ALLOWED_STATUS = {"pending", "observed"}


class AgentMatrixError(ValueError):
    """Raised when a tool comparison score is not evidence-backed."""


def load_agent_matrix(path: Path | None = None) -> dict[str, Any]:
    source = path or DEFAULT_PLAN
    if not source.is_file():
        raise FileNotFoundError(source)
    try:
        matrix = json.loads(source.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise AgentMatrixError(f"invalid JSON in {source}: {exc}") from exc
    if not isinstance(matrix, dict):
        raise AgentMatrixError("agent evaluation plan must be an object")
    return matrix


def validate_agent_matrix(matrix: dict[str, Any]) -> dict[str, Any]:
    """Validate scores and return comparison readiness without assigning scores."""
    dimensions = matrix.get("dimensions")
    methods = matrix.get("methods")
    scale = matrix.get("scale")
    if not isinstance(dimensions, list) or not dimensions:
        raise AgentMatrixError("dimensions must be a non-empty list")
    if not isinstance(methods, dict) or not methods:
        raise AgentMatrixError("methods must be a non-empty object")
    if not isinstance(scale, dict) or not isinstance(scale.get("min"), int) or not isinstance(scale.get("max"), int):
        raise AgentMatrixError("scale must define integer min and max")

    pending: list[str] = []
    observed: list[str] = []
    for method_name, method in methods.items():
        if not isinstance(method, dict) or method.get("status") not in ALLOWED_STATUS:
            raise AgentMatrixError(f"{method_name} has invalid status")
        entries = method.get("dimensions")
        if not isinstance(entries, dict) or set(entries) != set(dimensions):
            raise AgentMatrixError(f"{method_name} must define every rubric dimension")
        method_has_score = False
        for dimension in dimensions:
            entry = entries[dimension]
            if not isinstance(entry, dict):
                raise AgentMatrixError(f"{method_name}.{dimension} must be an object")
            score = entry.get("score")
            evidence = entry.get("evidence")
            verification = entry.get("verification")
            if score is None:
                if evidence or verification:
                    raise AgentMatrixError(f"{method_name}.{dimension} has evidence but no score")
                continue
            if not isinstance(score, int) or not scale["min"] <= score <= scale["max"]:
                raise AgentMatrixError(f"{method_name}.{dimension} score is outside the configured scale")
            if not isinstance(evidence, list) or not evidence or not all(isinstance(item, str) and item.strip() for item in evidence):
                raise AgentMatrixError(f"{method_name}.{dimension} score requires evidence paths")
            if not isinstance(verification, str) or not verification.strip():
                raise AgentMatrixError(f"{method_name}.{dimension} score requires verification note")
            method_has_score = True
        if method_has_score:
            if method.get("status") != "observed":
                raise AgentMatrixError(f"{method_name} with scores must have observed status")
            observed.append(method_name)
        else:
            pending.append(method_name)
    return {
        "methods": list(methods),
        "pending_methods": pending,
        "observed_methods": observed,
        "ready_for_comparison": bool(observed) and not pending,
        "side_effects": [],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    args = parser.parse_args()
    print(json.dumps(validate_agent_matrix(load_agent_matrix(args.plan)), ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
