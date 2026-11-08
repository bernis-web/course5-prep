"""DCS v99 provenance readout: read-only evidence recovery + unified re-scoring.

Runs inside the DCS container.  Reads only whitelisted paths under
``/data/work``, writes only under ``/data/work/course5_v99/``.  No training,
no deletion, no network.  Self-records command, hashes and environment.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

import numpy as np

PROTOCOL_LABEL = "transductive_formal_reassessment"
ALLOWED_OUTPUT_ROOT = "/data/work/course5_v99"
EXPECTED_EMBEDDING_SHAPE = (4606, 1000)
FINAL_ANNADATA_PATH = (
    "/data/work/saturn_out_real3_h/saturn_results/"
    "test256_data_human_saturn_input_hvg_mouse_saturn_input_hvg_"
    "zebrafish_saturn_input_hvg_org_human_seed_0.h5ad"
)
WHITELIST_READS = (
    FINAL_ANNADATA_PATH,
    "/data/work/prep_real_v60.py",
    "/data/work/eval_v72.py",
    "/data/work/g5-provenance-v95-command.txt",
    "/data/work/g5-provenance-v96-command.txt",
    "/data/work/dcs_provenance_v95.py",
    "/data/work/dcs_provenance_v96_readout.py",
)
TREE_HASH_ROOTS = ("/data/work/saturn-src",)

SPECIES_PREFIXES = {"human": "hu", "mouse": "mo", "zebrafish": "zf"}
DIRECTIONS = (
    ("human", "mouse"), ("human", "zebrafish"),
    ("mouse", "human"), ("mouse", "zebrafish"),
    ("zebrafish", "human"), ("zebrafish", "mouse"),
)
LEVELS = ("exact", "coarse", "fine")


class ProvenanceError(ValueError):
    """Raised when the v99 readout contract is violated."""


def output_path(rel: str, root: str = ALLOWED_OUTPUT_ROOT) -> Path:
    """Resolve an output path strictly under the allowed root (virtual POSIX)."""
    import posixpath

    if not str(root).startswith("/data/work/"):
        raise ValueError(f"output root outside allowed tree: {root}")
    base = posixpath.normpath(root)
    target = posixpath.normpath(posixpath.join(base, rel))
    if target != base and not target.startswith(base + "/"):
        raise ValueError(f"output path escapes allowed root: {rel}")
    return Path(target)


def ensure_output_root(root: str = ALLOWED_OUTPUT_ROOT) -> Path:
    path = Path(root)
    path.mkdir(parents=True, exist_ok=True)
    return path


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def candidate_hashes(candidates: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Hash existing candidates; record missing ones without failing.

    Values may be file-path strings or pre-built dicts (passed through).
    """
    out: dict[str, dict[str, Any]] = {}
    for name, path in candidates.items():
        if isinstance(path, dict):
            out[name] = path
            continue
        if os.path.isfile(path):
            out[name] = {
                "path": path,
                "sha256": sha256_file(path),
                "bytes": os.path.getsize(path),
            }
        else:
            out[name] = {"path": path, "missing": True}
    return out


def hash_tree(root: str) -> dict[str, str]:
    """SHA-256 every file under root, keyed by forward-slash relative path."""
    out: dict[str, str] = {}
    base = Path(root)
    if not base.is_dir():
        return out
    for path in sorted(base.rglob("*")):
        if path.is_file():
            rel = path.relative_to(base).as_posix()
            out[rel] = sha256_file(path)
    return out


def check_embedding_shape(shape: tuple) -> None:
    if tuple(shape) != EXPECTED_EMBEDDING_SHAPE:
        raise ProvenanceError(
            f"obsm['macrogenes'] shape {tuple(shape)} != {EXPECTED_EMBEDDING_SHAPE}"
        )


def resolve_mapping(mapping: dict[str, list]) -> dict[str, list]:
    """Normalize mapping rows; keys absent from the mapping become inactive."""
    out = {}
    for key, value in mapping.items():
        out[key] = [str(value[0]), str(value[1]), str(value[2])]
    return out


def mapping_status(key: str, mapping: dict[str, list]) -> str:
    if key in mapping:
        return mapping[key][2]
    return "inactive"


def knn_eval(
    m_s,
    m_t,
    emb,
    labels,
    key_arr,
    mapping: dict[str, list],
    level: str,
    k: int = 15,
    nperm: int = 200,
    seed: int = 0,
) -> dict[str, Any]:
    """Cosine kNN with inverted-distance voting; per-level exclusion rules."""
    emb = np.asarray(emb, dtype=float)
    labels = np.asarray(labels)
    key_arr = np.asarray(key_arr)
    m_s = np.asarray(m_s, dtype=bool)
    m_t = np.asarray(m_t, dtype=bool)
    col = 0 if level == "coarse" else 1
    ref_idx = np.where(m_s)[0]
    qry_idx = np.where(m_t)[0]
    if level in ("coarse", "fine"):
        active = np.array([mapping_status(key, mapping) == "active" for key in key_arr])
        ref_idx = ref_idx[active[ref_idx]]
        qry_idx = qry_idx[active[qry_idx]]
    ref = emb[ref_idx]
    qry = emb[qry_idx]
    ytr = labels[ref_idx]
    yte = labels[qry_idx]
    rn = np.linalg.norm(ref, axis=1)
    qn = np.linalg.norm(qry, axis=1)
    D = np.clip(1.0 - (qry / qn[:, None]) @ (ref / rn[:, None]).T, 0.0, 2.0)
    nk = min(k, len(ytr))
    preds = []
    for row in range(D.shape[0]):
        order = np.lexsort((np.arange(len(ytr)), D[row]))[:nk]
        sc = {}
        for i in order:
            sc[ytr[i]] = sc.get(ytr[i], 0.0) + 1.0 / (D[row][i] + 1e-12)
        preds.append(max(sc, key=lambda label: (sc[label], label)))
    preds = np.array(preds)
    acc = float((preds == yte).mean()) if len(yte) else 0.0
    vals, cnts = np.unique(yte, return_counts=True)
    maj = float(cnts.max() / cnts.sum()) if cnts.sum() else 0.0
    rng = np.random.RandomState(seed)
    nulls = []
    for _ in range(nperm):
        pp = preds.copy()
        rng.shuffle(pp)
        if not isinstance(pp == yte, np.ndarray):
            debug = {
                "pp_type": str(type(pp)), "pp_dtype": str(pp.dtype), "pp_shape": list(pp.shape),
                "yte_type": str(type(yte)), "yte_dtype": str(yte.dtype), "yte_shape": list(yte.shape),
                "labels_type": str(type(labels)), "labels_dtype": str(labels.dtype),
                "level": level, "m_s_true": int(m_s.sum()), "m_t_true": int(m_t.sum()),
            }
            raise ProvenanceError("scalar comparison: " + json.dumps(debug))
        nulls.append(float((pp == yte).mean()))
    pval = float((np.array(nulls) >= acc).mean()) if len(yte) else 1.0
    conf = {}
    for t, p in zip(yte, preds):
        key = f"{t}=>{p}"
        conf[key] = conf.get(key, 0) + 1
    return {
        "acc": round(acc, 4),
        "majority": round(maj, 4),
        "shuffle_p": round(pval, 4),
        "n_ref": int(len(ytr)),
        "n_q": int(len(yte)),
        "n_excluded_ref": int(m_s.sum() - len(ytr)) if level != "exact" else 0,
        "n_excluded_q": int(m_t.sum() - len(yte)) if level != "exact" else 0,
        "confusion": conf,
    }


def per_cell_records(
    spv: np.ndarray,
    bcv: np.ndarray,
    labels: np.ndarray,
    emb: np.ndarray,
    src: str,
    tgt: str,
    level: str,
    k: int = 15,
    nperm: int = 200,
    seed: int = 0,
) -> list[dict[str, Any]]:
    """Per-cell prediction records for one direction/level (all cells, exact truth)."""
    spv = np.asarray(spv)
    labels = np.asarray(labels)
    bcv = np.asarray(bcv)
    emb = np.asarray(emb, dtype=float)
    ref = emb[spv == src]
    qry = emb[spv == tgt]
    ytr = labels[spv == src]
    yte = labels[spv == tgt]
    bc_r = bcv[spv == src]
    bc_q = bcv[spv == tgt]
    rn = np.linalg.norm(ref, axis=1)
    qn = np.linalg.norm(qry, axis=1)
    D = np.clip(1.0 - (qry / qn[:, None]) @ (ref / rn[:, None]).T, 0.0, 2.0)
    nk = min(k, len(ytr))
    direction = f"{SPECIES_PREFIXES[src]}->{SPECIES_PREFIXES[tgt]}"
    records = []
    for row in range(D.shape[0]):
        order = np.lexsort((np.arange(len(ytr)), D[row]))[:nk]
        sc: dict[str, float] = {}
        for i in order:
            sc[ytr[i]] = sc.get(ytr[i], 0.0) + 1.0 / (D[row][i] + 1e-12)
        top = max(sc, key=lambda label: (sc[label], label))
        records.append(
            {
                "prefixed_barcode": str(bc_q[row]),
                "direction": direction,
                "level": level,
                "truth": str(yte[row]),
                "prediction": top,
                "included": True,
                "exclusion_reason": "",
                "confidence": round(sc[top] / sum(sc.values()), 4) if sc else 0.0,
                "neighbor_barcodes": [str(bc_r[i]) for i in order],
            }
        )
    return records


def compact_summary(metrics: dict, predictions: dict) -> str:
    """Build a stdout-safe compact summary guaranteed under 20 KB."""
    slim = {}
    for direction, levels in metrics.items():
        slim[direction] = {}
        for level, block in levels.items():
            if not isinstance(block, dict):
                slim[direction][level] = block
                continue
            slim[direction][level] = {
                key: block.get(key)
                for key in ("acc", "majority", "shuffle_p", "n_ref", "n_q",
                            "n_excluded_ref", "n_excluded_q", "coverage_q")
                if key in block
            }
    text = json.dumps({"protocol": PROTOCOL_LABEL, "metrics": slim}, ensure_ascii=False)
    if len(text) >= 20 * 1024:
        text = json.dumps({"protocol": PROTOCOL_LABEL, "metrics": "truncated; see metrics.json"})
    return text


def notebook_fallback_text(payload: dict) -> str:
    """Text .ipynb carrying the payload as source cells (fallback carrier)."""
    cells = []
    for name, value in payload.items():
        cells.append(
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [f"# {name}\n", json.dumps(value, ensure_ascii=False, indent=1)],
            }
        )
    nb = {
        "cells": cells,
        "metadata": {"kernelspec": {"name": "python3", "display_name": "Python 3"}},
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    return json.dumps(nb, ensure_ascii=False, indent=1)


def self_header(script_path: str = __file__) -> dict[str, Any]:
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    now_bj = now_utc.astimezone(datetime.timezone(datetime.timedelta(hours=8)))
    return {
        "utc": now_utc.isoformat(),
        "beijing": now_bj.isoformat(),
        "command": " ".join(sys.argv),
        "script_sha256": sha256_file(script_path) if os.path.isfile(script_path) else None,
        "python_version": sys.version,
        "protocol_label": PROTOCOL_LABEL,
    }


def main() -> None:  # pragma: no cover - executed only inside DCS
    import argparse

    import anndata as ad

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", default=ALLOWED_OUTPUT_ROOT)
    args = parser.parse_args()
    root = ensure_output_root(args.output_root)

    header = self_header(sys.argv[0] if sys.argv else __file__)
    (root / "environment.txt").write_text(
        json.dumps(header, ensure_ascii=False, indent=1) + "\n"
        + "pip_freeze_begin\n",
        encoding="utf-8",
    )
    try:
        import pip

        from pip._internal.operations import freeze as _fz

        freeze = sorted(_fz.freeze())
    except Exception:
        freeze = ["pip_freeze_unavailable"]
    with (root / "environment.txt").open("a", encoding="utf-8") as handle:
        handle.write("\n".join(freeze) + "\n")
    (root / "command.txt").write_text(" ".join(sys.argv) + "\n", encoding="utf-8")

    cands = {name: p for name, p in (("final_anndata", FINAL_ANNADATA_PATH),)}
    for path in WHITELIST_READS[1:]:
        cands[Path(path).name] = path
    tree = hash_tree(TREE_HASH_ROOTS[0])
    (root / "saturn_src_tree_sha256.tsv").write_text(
        "\n".join(f"{v}  {k}" for k, v in sorted(tree.items())) + "\n",
        encoding="utf-8",
    )
    cands["saturn_src_tree_file_count"] = {"files": len(tree), "note": "per-file hashes in saturn_src_tree_sha256.tsv"}
    hashes = candidate_hashes(cands)
    (root / "candidate_hashes.json").write_text(
        json.dumps(hashes, ensure_ascii=False, indent=1), encoding="utf-8"
    )

    adata = ad.read_h5ad(FINAL_ANNADATA_PATH)
    check_embedding_shape(adata.obsm["macrogenes"].shape)
    emb = np.asarray(adata.obsm["macrogenes"], dtype=np.float64)
    sp = np.array([str(v) for v in adata.obs["species"]])
    labels = np.array([str(v) for v in adata.obs["ref_labels"]])
    bc = np.array([str(v) for v in adata.obs_names])
    pre = {"human": "hu", "mouse": "mo", "zebrafish": "zf"}
    pbc = np.array([pre[s] + "|" + b for s, b in zip(sp, bc)])
    if len(set(pbc)) != len(pbc):
        raise ProvenanceError("duplicate prefixed barcodes")

    counts = {s: int((sp == s).sum()) for s in set(sp)}
    if counts != {"human": 1528, "mouse": 1535, "zebrafish": 1543}:
        raise ProvenanceError(f"species counts mismatch: {counts}")

    mp_path = Path("/data/work/v97_out/READY.json")
    mapping = json.loads(
        (Path(__file__).parent / "v99_mapping_embedded.json").read_text(encoding="utf-8")
    ) if (Path(__file__).parent / "v99_mapping_embedded.json").is_file() else json.loads(
        os.environ.get("V99_MAPPING_JSON", "{}")
    )
    if not mapping:
        raise ProvenanceError(
            "frozen mapping not found; embed v99_mapping_embedded.json next to the script"
        )
    mapping = resolve_mapping(mapping)

    (root / "predictions").mkdir(exist_ok=True)
    (root / "confusion").mkdir(exist_ok=True)
    (root / "roles").mkdir(exist_ok=True)

    metrics: dict[str, Any] = {}
    predictions_index: dict[str, Any] = {}
    for src, tgt in DIRECTIONS:
        m_s = sp == src
        m_t = sp == tgt
        metrics[src + "->" + tgt] = {}
        predictions_index[src + "->" + tgt] = {}
        for level in LEVELS:
            key_arr = np.array([s + "|" + l for s, l in zip(sp, labels)])
            result = knn_eval(
                m_s, m_t, emb, labels, key_arr, mapping, level, k=15, nperm=200, seed=0
            )
            metrics[src + "->" + tgt][level] = result
            records = per_cell_records(
                sp, pbc, labels, emb, src, tgt, level, k=15, nperm=0, seed=0
            )
            pred_file = root / "predictions" / f"{level}_{src}->{tgt}.json"
            pred_file.write_text(
                json.dumps(records, ensure_ascii=False, indent=1), encoding="utf-8"
            )
            conf_file = root / "confusion" / f"{level}_{src}->{tgt}.json"
            conf_file.write_text(
                json.dumps(result["confusion"], ensure_ascii=False, indent=1, sort_keys=True),
                encoding="utf-8",
            )
            predictions_index[src + "->" + tgt][level] = {
                "n_records": len(records),
                "file": str(pred_file),
            }

    manifest = {
        "protocol_label": PROTOCOL_LABEL,
        "source": FINAL_ANNADATA_PATH,
        "source_sha256": hashes["final_anndata"]["sha256"],
        "representation": "obsm/macrogenes",
        "shape": list(EXPECTED_EMBEDDING_SHAPE),
        "species_counts": counts,
        "k": 15,
        "distance": "cosine",
        "nperm": 200,
        "seed": 0,
        "header": header,
        "candidate_hashes": hashes,
        "predictions_index": predictions_index,
    }
    (root / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    (root / "metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=1), encoding="utf-8"
    )

    sha_lines = []
    for path in sorted(root.rglob("*")):
        if path.is_file():
            rel = path.relative_to(root).as_posix()
            sha_lines.append(f"{sha256_file(path)}  {rel}")
    (root / "sha256.tsv").write_text("\n".join(sha_lines) + "\n", encoding="utf-8")

    payload = {"metrics": metrics, "candidate_hashes": hashes}
    (root / "course5_v99_readout.ipynb").write_text(
        notebook_fallback_text(payload), encoding="utf-8"
    )

    print(compact_summary(metrics, predictions_index))


if __name__ == "__main__":
    main()
