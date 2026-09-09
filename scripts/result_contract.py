"""Validate comparable metrics and resource records for one benchmark run."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


PROXY_KBET = "chi2_neighborhood_proxy"


class ResultContractError(ValueError):
    """Raised when metrics or resource usage cannot support comparison."""


def _number(value: Any, name: str, minimum: float | None = None, maximum: float | None = None) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ResultContractError(f"{name} must be numeric")
    numeric = float(value)
    if minimum is not None and numeric < minimum:
        raise ResultContractError(f"{name} must be >= {minimum}")
    if maximum is not None and numeric > maximum:
        raise ResultContractError(f"{name} must be <= {maximum}")
    return numeric


def _required_object(parent: dict[str, Any], name: str) -> dict[str, Any]:
    value = parent.get(name)
    if not isinstance(value, dict):
        raise ResultContractError(f"{name} must be an object")
    return value


def validate_result(metrics: dict[str, Any], resources: dict[str, Any], stage: str = "final") -> dict[str, Any]:
    """Validate fixed scientific and resource fields without modifying inputs."""
    if stage not in {"smoke", "final"}:
        raise ResultContractError("stage must be 'smoke' or 'final'")
    if not isinstance(metrics, dict) or not isinstance(resources, dict):
        raise ResultContractError("metrics and resources must be objects")

    labels = _required_object(metrics, "label_transfer")
    embedding = _required_object(metrics, "embedding")
    macro_f1 = _number(labels.get("macro_f1"), "label_transfer.macro_f1", 0.0, 1.0)
    silhouette = _number(embedding.get("silhouette"), "embedding.silhouette", -1.0, 1.0)
    ilisi = _number(embedding.get("ilisi"), "embedding.ilisi", 1.0)
    kbet_rate = _number(embedding.get("kbet_rejection_rate"), "embedding.kbet_rejection_rate", 0.0, 1.0)
    kbet_method = embedding.get("kbet_method")
    if not isinstance(kbet_method, str) or not kbet_method.strip():
        raise ResultContractError("embedding.kbet_method must be a non-empty string")
    if stage == "final" and kbet_method == PROXY_KBET:
        raise ResultContractError("final results cannot use the chi-square kBET proxy")

    wall_time = _number(resources.get("wall_time_seconds"), "wall_time_seconds", 0.0)
    peak_memory = _number(resources.get("peak_memory_gb"), "peak_memory_gb", 0.0)
    gpu_count = resources.get("gpu_count")
    if isinstance(gpu_count, bool) or not isinstance(gpu_count, int) or gpu_count < 0:
        raise ResultContractError("gpu_count must be an integer >= 0")
    gpu_name = resources.get("gpu_name")
    if not isinstance(gpu_name, str) or not gpu_name.strip():
        raise ResultContractError("gpu_name must be a non-empty string")
    cost = _number(resources.get("cost_cny"), "cost_cny", 0.0)
    cost_source = resources.get("cost_source")
    if not isinstance(cost_source, str) or not cost_source.strip():
        raise ResultContractError("cost_source must be a non-empty string")

    return {
        "valid": True,
        "stage": stage,
        "macro_f1": macro_f1,
        "silhouette": silhouette,
        "ilisi": ilisi,
        "kbet_rejection_rate": kbet_rate,
        "kbet_method": kbet_method,
        "wall_time_seconds": wall_time,
        "peak_memory_gb": peak_memory,
        "gpu_count": gpu_count,
        "gpu_name": gpu_name,
        "cost_cny": cost,
        "cost_source": cost_source,
        "side_effects": [],
    }


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ResultContractError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ResultContractError(f"JSON root must be an object: {path}")
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("metrics", type=Path)
    parser.add_argument("resources", type=Path)
    parser.add_argument("--stage", choices=("smoke", "final"), default="final")
    args = parser.parse_args()
    try:
        result = validate_result(_read_json(args.metrics), _read_json(args.resources), stage=args.stage)
    except (ResultContractError, FileNotFoundError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, ensure_ascii=True, indent=2))
        raise SystemExit(2) from exc
    print(json.dumps(result, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
