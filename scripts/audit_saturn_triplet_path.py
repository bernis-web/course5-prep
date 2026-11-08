"""Statically audit the checked-in SATURN Triplet training path.

This module deliberately parses source with :mod:`ast` instead of importing or
executing SATURN.  It is therefore safe to run when the training environment,
GPU stack, and DCS credentials are unavailable.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "wheelhouse" / "saturn-src" / "train-saturn.py"


class AuditError(ValueError):
    """Raised when the source cannot be audited safely."""


def _function(module: ast.Module, name: str) -> ast.FunctionDef | ast.AsyncFunctionDef | None:
    for node in ast.walk(module):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return node
    return None


def _call_name(node: ast.Call) -> str:
    func = node.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        parts: list[str] = []
        current: ast.AST = func
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        return ".".join(reversed(parts))
    return "<unknown>"


def _literal(node: ast.AST) -> Any:
    try:
        return ast.literal_eval(node)
    except (ValueError, TypeError, SyntaxError):
        return None


def _source_line(lines: list[str], lineno: int | None) -> str:
    if lineno is None or lineno < 1 or lineno > len(lines):
        return ""
    return lines[lineno - 1].strip()


def _evidence(lines: list[str], node: ast.AST) -> dict[str, Any]:
    lineno = getattr(node, "lineno", None)
    return {"line": lineno, "text": _source_line(lines, lineno)}


def _contains_name(node: ast.AST, name: str) -> bool:
    return any(isinstance(item, ast.Name) and item.id == name for item in ast.walk(node))


def _calls(node: ast.AST) -> Iterable[ast.Call]:
    return (item for item in ast.walk(node) if isinstance(item, ast.Call))


def _audit_triplet_miner(module: ast.Module, lines: list[str]) -> dict[str, Any]:
    matches: list[dict[str, Any]] = []
    for node in ast.walk(module):
        if not isinstance(node, ast.Call) or not _call_name(node).endswith("TripletMarginMiner"):
            continue
        keyword = next((item for item in node.keywords if item.arg == "miner_type"), None)
        matches.append(
            {
                **_evidence(lines, node),
                "call": _call_name(node),
                "miner_type": _literal(keyword.value) if keyword else None,
                "miner_type_keyword_present": keyword is not None,
            }
        )
    values = [item["miner_type"] for item in matches if item["miner_type"] is not None]
    return {
        "found": bool(matches),
        "miner_type_values": values,
        "evidence": matches,
    }


def _call_passes_ref_labels(call: ast.Call) -> bool:
    return any(keyword.arg == "ref_labels" for keyword in call.keywords)


def _audit_use_ref_branch(module: ast.Module, lines: list[str]) -> dict[str, Any]:
    train_fn = _function(module, "train")
    branches: list[dict[str, Any]] = []
    if train_fn is not None:
        for node in ast.walk(train_fn):
            if not isinstance(node, ast.If) or not _contains_name(node.test, "use_ref_labels"):
                continue
            true_calls = [call for call in _calls(ast.Module(body=node.body, type_ignores=[])) if _call_name(call) == "mining_func"]
            false_calls = [call for call in _calls(ast.Module(body=node.orelse, type_ignores=[])) if _call_name(call) == "mining_func"]
            branches.append(
                {
                    **_evidence(lines, node),
                    "true_branch_calls": [
                        {**_evidence(lines, call), "passes_ref_labels": _call_passes_ref_labels(call)}
                        for call in true_calls
                    ],
                    "false_branch_calls": [
                        {**_evidence(lines, call), "passes_ref_labels": _call_passes_ref_labels(call)}
                        for call in false_calls
                    ],
                }
            )

    true_calls = [call for branch in branches for call in branch["true_branch_calls"]]
    false_calls = [call for branch in branches for call in branch["false_branch_calls"]]
    return {
        "found": bool(branches),
        "evidence": branches,
        "true_branch_passes_ref_labels": any(call["passes_ref_labels"] for call in true_calls),
        "false_branch_omits_ref_labels": bool(false_calls) and not any(
            call["passes_ref_labels"] for call in false_calls
        ),
    }


def _parent_map(node: ast.AST) -> dict[int, ast.AST]:
    parents: dict[int, ast.AST] = {}
    for parent in ast.walk(node):
        for child in ast.iter_child_nodes(parent):
            parents[id(child)] = parent
    return parents


def _audit_ref_labels_selection(module: ast.Module, lines: list[str]) -> dict[str, Any]:
    function = _function(module, "get_species_triplet_indices")
    if function is None:
        return {
            "function_found": False,
            "parameter_found": False,
            "default_initialization_lines": [],
            "reads_outside_default_initialization": False,
            "participates_in_triplet_selection": False,
            "evidence": [],
        }

    parameter_found = any(
        arg.arg == "ref_labels"
        for arg in (*function.args.posonlyargs, *function.args.args, *function.args.kwonlyargs)
    )
    parents = _parent_map(function)
    init_lines: set[int] = set()
    for node in ast.walk(function):
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        if not any(isinstance(target, ast.Name) and target.id == "ref_labels" for target in targets):
            continue
        if any(isinstance(item, ast.Name) and item.id == "ref_labels" and isinstance(item.ctx, ast.Load) for item in ast.walk(node.value)):
            init_lines.add(getattr(node, "lineno", -1))

    reads: list[dict[str, Any]] = []
    selection_reads: list[dict[str, Any]] = []
    for node in ast.walk(function):
        if not isinstance(node, ast.Name) or node.id != "ref_labels" or not isinstance(node.ctx, ast.Load):
            continue
        if getattr(node, "lineno", -1) in init_lines:
            continue
        parent = parents.get(id(node))
        record = {**_evidence(lines, node), "parent": type(parent).__name__ if parent else None}
        reads.append(record)
        if parent is not None and not isinstance(parent, ast.keyword):
            selection_reads.append(record)

    return {
        "function_found": True,
        "parameter_found": parameter_found,
        "default_initialization_lines": sorted(init_lines),
        "reads_outside_default_initialization": bool(reads),
        "participates_in_triplet_selection": bool(selection_reads),
        "evidence": reads,
        "selection_evidence": selection_reads,
    }


def _audit_macrogenes_output(module: ast.Module, lines: list[str]) -> dict[str, Any]:
    matches: list[dict[str, Any]] = []
    for node in ast.walk(module):
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        for target in targets:
            if not isinstance(target, ast.Subscript):
                continue
            value = target.value
            key = _literal(target.slice)
            if isinstance(value, ast.Attribute) and value.attr == "obsm" and key == "macrogenes":
                matches.append({**_evidence(lines, node), "key": key})
    return {"found": bool(matches), "evidence": matches}


def audit_source(source: Path, ref_source: Path | None = None) -> dict[str, Any]:
    source = Path(source).expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    raw = source.read_bytes()
    text = raw.decode("utf-8")
    try:
        module = ast.parse(text, filename=str(source))
    except SyntaxError as exc:
        raise AuditError(f"cannot parse {source}: {exc}") from exc
    lines = text.splitlines()

    resolved_ref_source = ref_source
    if resolved_ref_source is None:
        candidate = source.parent / "utils" / "loss_and_miner_utils.py"
        if candidate.is_file():
            resolved_ref_source = candidate
    ref_module = module
    ref_lines = lines
    ref_source_record: dict[str, Any] | None = None
    if resolved_ref_source is not None:
        resolved_ref_source = Path(resolved_ref_source).expanduser().resolve()
        if resolved_ref_source != source:
            ref_raw = resolved_ref_source.read_bytes()
            try:
                ref_module = ast.parse(ref_raw.decode("utf-8"), filename=str(resolved_ref_source))
            except (UnicodeDecodeError, SyntaxError) as exc:
                raise AuditError(f"cannot parse supplemental ref-label source {resolved_ref_source}: {exc}") from exc
            ref_lines = ref_raw.decode("utf-8").splitlines()
            ref_source_record = {
                "path": str(resolved_ref_source),
                "sha256": hashlib.sha256(ref_raw).hexdigest(),
                "line_count": len(ref_lines),
            }

    checks = {
        "triplet_miner": _audit_triplet_miner(module, lines),
        "use_ref_labels_branch": _audit_use_ref_branch(module, lines),
        "ref_labels_selection": _audit_ref_labels_selection(ref_module, ref_lines),
        "macrogenes_output": _audit_macrogenes_output(module, lines),
    }
    warnings: list[str] = []
    if not checks["triplet_miner"]["found"]:
        warnings.append("TripletMarginMiner call not found")
    if not checks["use_ref_labels_branch"]["found"]:
        warnings.append("use_ref_labels branch not found in train()")
    if checks["ref_labels_selection"]["function_found"] and not checks["ref_labels_selection"]["participates_in_triplet_selection"]:
        warnings.append("ref_labels is only default-initialized and has no detected triplet-selection use")
    if not checks["macrogenes_output"]["found"]:
        warnings.append('adata.obsm["macrogenes"] output not found')

    return {
        "schema_version": "saturn-triplet-audit-v1",
        "source": {
            "path": str(source),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "line_count": len(lines),
            "supplemental_ref_labels_source": ref_source_record,
        },
        "checks": checks,
        "summary": {"status": "warning" if warnings else "pass", "warnings": warnings},
    }


def format_text(report: dict[str, Any]) -> str:
    checks = report["checks"]
    selection = checks["ref_labels_selection"]
    lines = [
        f"SATURN Triplet path audit: {report['summary']['status']}",
        f"source: {report['source']['path']}",
        f"sha256: {report['source']['sha256']}",
        f"TripletMarginMiner: {checks['triplet_miner']['miner_type_values'] or 'not found'}",
        "use_ref_labels branch: "
        f"found={checks['use_ref_labels_branch']['found']}, "
        f"true_passes={checks['use_ref_labels_branch']['true_branch_passes_ref_labels']}, "
        f"false_omits={checks['use_ref_labels_branch']['false_branch_omits_ref_labels']}",
        "ref_labels selection: "
        f"parameter={selection['parameter_found']}, "
        f"outside_default_init={selection['reads_outside_default_initialization']}, "
        f"participates={selection['participates_in_triplet_selection']}",
        f"macrogenes output: {checks['macrogenes_output']['found']}",
    ]
    for warning in report["summary"]["warnings"]:
        lines.append(f"warning: {warning}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--format", choices=("json", "text"), default="json")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        report = audit_source(args.source)
    except (AuditError, FileNotFoundError, UnicodeDecodeError) as exc:
        payload = json.dumps({"valid": False, "error": str(exc)}, ensure_ascii=False, indent=2)
        print(payload)
        raise SystemExit(2) from exc

    rendered = json.dumps(report, ensure_ascii=False, indent=2) if args.format == "json" else format_text(report)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
