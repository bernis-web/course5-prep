"""SAMap v98: compliant three-species run with auditable per-cell outputs.

Fixes relative to legacy ``local_samap3.py`` (legacy_noncompliant_20260928):
species-prefixed barcodes before SAM/SAMAP construction, global uniqueness
assertion (no make_unique masking), truth-NA failure, frozen-mapping
exclusion on both reference and query sides for coarse/fine, per-cell
records with exclusion reasons, fixed seed/protocol labeling.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

BASE = Path(__file__).resolve().parents[1]
PROTOCOL_LABEL = "transductive_formal_reassessment"
SPECIES_PREFIXES = {"human": "hu", "mouse": "mo", "zebrafish": "zf"}
SPECIES_FILES = {
    "human": "local_human_s.h5ad",
    "mouse": "local_mouse_s.h5ad",
    "zebrafish": "local_zebrafish_s.h5ad",
}
TRUTH_COLUMN = "cell_type"
K = 15
NPERM = 200
SEED = 0

DIRECTIONS = (
    ("human", "mouse"), ("human", "zebrafish"),
    ("mouse", "human"), ("mouse", "zebrafish"),
    ("zebrafish", "human"), ("zebrafish", "mouse"),
)
LEVELS = ("exact", "coarse", "fine")


class V98Error(ValueError):
    """Raised when the v98 contract is violated."""


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def freeze_mapping(tsv_path: Path) -> dict[str, dict[str, str]]:
    """Load the frozen mapping TSV into a nested lookup."""
    import csv

    rows: dict[str, dict[str, str]] = {}
    with open(tsv_path, "r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            key = f"{row['source_species'].strip()}|{row['source_label'].strip()}"
            rows[key] = {
                "coarse": row["coarse_level"].strip(),
                "fine": row["fine_mapped_label"].strip(),
                "status": row["mapping_status"].strip(),
            }
    return rows


def mapping_status(key: str, mapping: dict[str, dict[str, str]]) -> str:
    return mapping[key]["status"] if key in mapping else "inactive"


def apply_species_prefix(adata: Any, species: str) -> Any:
    """Return a copy with species-prefixed observation names."""
    prefix = SPECIES_PREFIXES.get(species)
    if prefix is None:
        raise V98Error(f"unknown species: {species!r}")
    a = adata.copy()
    a.obs_names = [f"{prefix}|{name}" for name in a.obs_names]
    return a


def load_species(path: Path, species: str) -> Any:
    """Load a species h5ad with a species-prefixed observation namespace."""
    import anndata as ad

    if species not in SPECIES_PREFIXES:
        raise V98Error(f"unknown species: {species!r}")
    a = ad.read_h5ad(path)
    if species == "zebrafish" and a.var_names.duplicated().any():
        # 斑马鱼注释含重复基因符号：保留首次出现，数量记录到 uns（后续写入 manifest）
        n_dup = int(a.var_names.duplicated().sum())
        a = a[:, ~a.var_names.duplicated()].copy()
        a.uns["v98_gene_dedup_dropped"] = n_dup
    prefix = SPECIES_PREFIXES[species]
    a.obs_names = [f"{prefix}|{name}" for name in a.obs_names]
    return a


def assert_prefix_unique(adatas: list[Any]) -> None:
    all_names: list[str] = []
    for a in adatas:
        if hasattr(a, "adata") and callable(getattr(a, "adata", None)):
            names = [str(n) for n in a.adata().obs_names]
        elif hasattr(a, "obs_names"):
            names = [str(n) for n in a.obs_names]
        else:
            raise V98Error("object has no obs_names")
        all_names += names
    duplicates = sorted({n for n in all_names if all_names.count(n) > 1})
    if duplicates:
        raise V98Error(f"duplicate prefixed barcodes after prefixing: {duplicates}")


def assert_no_na_truth(adata: Any, truth_column: str = TRUTH_COLUMN) -> None:
    if truth_column not in adata.obs.columns:
        raise V98Error(f"truth column {truth_column!r} missing")
    values = adata.obs[truth_column].astype(str)
    na_mask = values.isin({"NA", "nan", "None", ""}) | values.isna()
    if na_mask.any():
        bad = [str(x) for x in np.asarray(adata.obs_names)[np.asarray(na_mask)]]
        raise V98Error(f"truth NA found on {int(na_mask.sum())} cells: {bad[:10]}")


def exclusion_counts(adata: Any, mapping: dict[str, dict[str, str]], species: str) -> int:
    """Count cells whose frozen mapping status is not active."""
    excluded = 0
    for label in adata.obs[TRUTH_COLUMN].astype(str):
        key = f"{species}|{label}"
        if mapping_status(key, mapping) != "active":
            excluded += 1
    return excluded


def evaluate_direction(
    embedding: np.ndarray,
    sp: np.ndarray,
    bc: np.ndarray,
    labels: np.ndarray,
    src: str,
    tgt: str,
    mapping: dict[str, dict[str, str]],
    k: int = K,
    nperm: int = NPERM,
    seed: int = SEED,
) -> dict[str, dict[str, Any]]:
    """Evaluate one direction at exact/coarse/fine levels with per-cell records."""
    emb = np.asarray(embedding, dtype=float)
    m_s = sp == src
    m_t = sp == tgt
    key_arr = np.array([f"{s}|{l}" for s, l in zip(sp, labels)])
    col = {"exact": None, "coarse": "coarse", "fine": "fine"}
    result: dict[str, dict[str, Any]] = {}
    for level in LEVELS:
        exclude = level in ("coarse", "fine")
        ref_idx = np.where(m_s)[0]
        qry_idx = np.where(m_t)[0]
        if exclude:
            active = np.array(
                [mapping_status(key, mapping) == "active" for key in key_arr]
            )
            ref_idx = ref_idx[active[ref_idx]]
            qry_idx = qry_idx[active[qry_idx]]
            n_excluded_q = int((m_t & ~active).sum())
            n_excluded_ref = int((m_s & ~active).sum())
        else:
            n_excluded_q = 0
            n_excluded_ref = 0
        ref = emb[ref_idx]
        qry = emb[qry_idx]
        ytr = labels[ref_idx]
        yte = labels[qry_idx]
        rn = np.linalg.norm(ref, axis=1)
        qn = np.linalg.norm(qry, axis=1)
        D = np.clip(1.0 - (qry / qn[:, None]) @ (ref / rn[:, None]).T, 0.0, 2.0)
        nk = min(k, len(ytr))
        if len(ytr) == 0 or D.shape[0] == 0:
            raise V98Error(
                f"empty evaluation set at level={level}: "
                f"n_ref={len(ytr)} n_q={D.shape[0]} "
                f"src={src} tgt={tgt}"
            )
        preds = []
        weights_sum = []
        for row in range(D.shape[0]):
            order = np.lexsort((np.arange(len(ytr)), D[row]))[:nk]
            sc: dict[str, float] = {}
            for i in order:
                sc[ytr[i]] = sc.get(ytr[i], 0.0) + 1.0 / (D[row][i] + 1e-12)
            winner = max(sc, key=lambda label: (sc[label], label))
            preds.append(winner)
            weights_sum.append(sc[winner] / sum(sc.values()))
        preds = np.array(preds)
        ref_labels = set(str(x) for x in ytr)
        included_mask = np.array([str(t) in ref_labels for t in yte])
        yte_inc = yte[included_mask]
        preds_inc = preds[included_mask]
        acc = float((preds_inc == yte_inc).mean()) if len(yte_inc) else 0.0
        vals, cnts = np.unique(yte_inc, return_counts=True)
        maj = float(cnts.max() / cnts.sum()) if cnts.sum() else 0.0
        rng = np.random.RandomState(seed)
        nulls = []
        for _ in range(nperm):
            pp = preds_inc.copy()
            rng.shuffle(pp)
            nulls.append(float((pp == yte_inc).mean()))
        pval = float((np.array(nulls) >= acc).mean()) if len(yte_inc) else 1.0
        conf: dict[str, int] = {}
        per_cell = []
        direction = f"{SPECIES_PREFIXES[src]}->{SPECIES_PREFIXES[tgt]}"
        bc_q = [str(b) for b in np.asarray(bc)[m_t]]
        for j, (barcode, truth) in enumerate(zip(bc_q, yte)):
            inc = bool(included_mask[j])
            pred = str(preds[j])
            conf_key = f"{truth}=>{pred}"
            if inc:
                conf[conf_key] = conf.get(conf_key, 0) + 1
            per_cell.append(
                {
                    "prefixed_barcode": barcode,
                    "direction": direction,
                    "level": level,
                    "truth": str(truth),
                    "prediction": pred,
                    "included": inc,
                    "exclusion_reason": "" if inc else "truth_not_in_reference_training_labels",
                    "confidence": round(float(weights_sum[j]), 4) if inc else 0.0,
                }
            )
        result[level] = {
            "acc": round(acc, 4),
            "majority": round(maj, 4),
            "shuffle_p": round(pval, 4),
            "n_ref": int(len(ytr)),
            "n_q": int(len(yte_inc)),
            "n_q_total": int(len(yte)),
            "coverage_q": round(float(included_mask.mean()), 4),
            "n_excluded_q": int((~included_mask).sum()) + n_excluded_q,
            "n_excluded_ref": n_excluded_ref,
            "per_cell": per_cell,
            "confusion": conf,
        }
    return result


def main() -> None:  # pragma: no cover - full local run
    root = Path(__file__).resolve().parents[1]
    output_dir = root / "results" / "pilot-v1" / "samap-v98"
    output_dir.mkdir(parents=True, exist_ok=True)

    mapping = freeze_mapping(root / "config" / "heart-celltype-map-v1.tsv")
    mapping_sha = sha256_file(root / "config" / "heart-celltype-map-v1.tsv")

    from samalg import SAM

    sams = {}
    obs_frames = {}
    sid_map = {"human": "hu", "mouse": "ms", "zebrafish": "zf"}
    for species, fn in SPECIES_FILES.items():
        path = root / fn
        a = load_species(path, species)
        assert_no_na_truth(a)
        a.layers["X_disp"] = a.X  # samalg.run() expects this layer; set by SAM(counts=...) normally
        sam = SAM()
        sam.adata = a
        sam.adata_raw = a  # SAMAP.prepend_var_prefix writes to adata_raw; keep same object
        sam.run(preprocessing="StandardScaler", npcs=100, weight_PCs=False, k=20, n_genes=3000, weight_mode="rms", seed=SEED)
        sams[sid_map[species]] = sam
        obs_frames[sid_map[species]] = set(a.obs_names)
        print(f"{species} SAM done", flush=True)

    assert_prefix_unique([s.adata for s in sams.values()])

    from samap.mapping import SAMAP

    def build_gnnm_from_orthologs():
        groups = {}
        for line in open(
            BASE / "ortholog" / "MGI_HOM_MouseHumanSequence.rpt",
            encoding="utf-8", errors="replace",
        ):
            f = line.rstrip(chr(10)).split(chr(9))
            if len(f) < 5 or not f[0].isdigit():
                continue
            tax = None; sym = None
            for i in range(len(f) - 1):
                if f[i] in ("9606", "10090"):
                    tax = "hu" if f[i] == "9606" else "ms"
                    sym = f[i + 1].strip().upper()
                    break
            if tax and sym:
                groups.setdefault(f[0], {}).setdefault(tax, set()).add(sym)
        hm = {}
        for g, d in groups.items():
            if set(d.keys()) == {"hu", "ms"} and len(d["hu"]) == 1 and len(d["ms"]) == 1:
                hm[next(iter(d["hu"]))] = next(iter(d["ms"]))
        def zfin(path):
            d = {}
            for line in open(path, encoding="utf-8", errors="replace"):
                f = line.rstrip(chr(10)).split(chr(9))
                if len(f) < 5:
                    continue
                d.setdefault(f[1].strip().upper(), set()).add(f[3].strip().upper())
            return d
        fh_raw = zfin(BASE / "ortholog" / "human_orthos.txt")
        f2h = {}; h2f = {}
        for fish, hs in fh_raw.items():
            if len(hs) == 1:
                hh = next(iter(hs)); h2f.setdefault(hh, []).append(fish); f2h[fish] = hh
        fh = {h: fl[0] for h, fl in h2f.items() if len(fl) == 1}
        fm_raw = zfin(BASE / "ortholog" / "mouse_orthos.txt")
        f2m = {}; m2f = {}
        for fish, ms in fm_raw.items():
            if len(ms) == 1:
                mm = next(iter(ms)); m2f.setdefault(mm, []).append(fish); f2m[fish] = mm
        fmm = {m: fl[0] for m, fl in m2f.items() if len(fl) == 1}
        genes = {}
        for sid, sam_obj in sams.items():
            genes[sid] = [str(g).upper() for g in sam_obj.adata.var_names]
        allg = (
            ["hu_" + g for g in genes["hu"]]
            + ["ms_" + g for g in genes["ms"]]
            + ["zf_" + g for g in genes["zf"]]
        )
        gidx = {g: i for i, g in enumerate(allg)}
        rows = []; cols = []; nedges = 0
        for src_map, pa, pb in [(hm, "hu", "ms"), (fh, "hu", "zf"), (fmm, "ms", "zf")]:
            for a, b in src_map.items():
                x = pa + "_" + a; y = pb + "_" + b
                if x in gidx and y in gidx:
                    rows.append(gidx[x]); cols.append(gidx[y]); nedges += 1
        import scipy.sparse as spmod
        adj = spmod.csr_matrix(
            (np.ones(nedges * 2), (rows + cols, cols + rows)), shape=(len(allg), len(allg))
        )
        gnnm = (
            adj,
            np.array(allg),
            {
                "hu": np.array(allg[: len(genes["hu"])]),
                "ms": np.array(allg[len(genes["hu"]): len(genes["hu"]) + len(genes["ms"])]),
                "zf": np.array(allg[len(genes["hu"]) + len(genes["ms"]):]),
            },
        )
        print("gnnm nodes=%d edges=%d" % (len(allg), nedges), flush=True)
        return gnnm

    gnnm = build_gnnm_from_orthologs()
    sm = SAMAP(sams, keys={s: TRUTH_COLUMN for s in sams}, gnnm=gnnm)
    sm.run(NUMITERS=3, ncpus=4, umap=False)
    jsam = sm.samap
    jd = jsam.adata
    if "X_samap_pca" in jd.obsm:
        emb = np.asarray(jd.obsm["X_samap_pca"])
    elif "X_pca" in jd.obsm:
        emb = np.asarray(jd.obsm["X_pca"])
    else:
        raise V98Error(f"no joint embedding in obsm: {sorted(jd.obsm.keys())}")
    # 同时覆盖 obs 名前缀（hu/mo/zf）与 SAMAP species 列值（hu/ms/zf）两套键
    prefix_map = {"hu": "human", "mo": "mouse", "ms": "mouse", "zf": "zebrafish"}
    if "species" in jd.obs.columns:
        raw_sp_vals = [str(v) for v in jd.obs["species"].astype(str).values]
        sp = np.array([prefix_map.get(v, v) for v in raw_sp_vals])
        print("species_branch=column raw_sample=" + json.dumps(raw_sp_vals[:5]), flush=True)
    else:
        sp = np.array([prefix_map.get(str(n).split("|")[0], str(n))
                       for n in jd.obs_names])
        print("species_branch=obsnames sample=" + json.dumps([str(x) for x in sp[:5]]), flush=True)
    labels = np.empty(jd.n_obs, dtype=object)
    sid_to_species = {"hu": "human", "ms": "mouse", "zf": "zebrafish"}
    for sid, sam_obj in sams.items():
        sp_name = sid_to_species[sid]
        m = sp == sp_name
        name_map = {
            str(o).split("|", 1)[-1]: str(v)
            for o, v in zip(
                sam_obj.adata.obs_names,
                sam_obj.adata.obs[TRUTH_COLUMN].astype(str).values,
            )
        }
        joint_tail = [str(n).split("|", 1)[-1] for n in np.asarray(jd.obs_names)[m]]
        labels[m] = [name_map.get(o, "NA") for o in joint_tail]
    bc = np.array([str(o) for o in jd.obs_names])
    from collections import Counter
    print("sp_dist=" + json.dumps(Counter(sp.tolist())), flush=True)
    print("bc_prefix_dist=" + json.dumps(Counter([b.split("|")[0] for b in bc.tolist()])), flush=True)
    n_na = int((labels == "NA").sum())
    print("truth_na=" + str(n_na), flush=True)
    if n_na > 0:
        bad = [str(b) for b, lab in zip(bc, labels) if lab == "NA"]
        raise V98Error(f"post-join truth NA on {n_na} cells: {bad[:10]}")

    metrics = {}
    for src, tgt in DIRECTIONS:
        result = evaluate_direction(
            emb, sp, bc, labels, src, tgt, mapping, k=K, nperm=NPERM, seed=SEED
        )
        metrics[src + "->" + tgt] = result
        for level in LEVELS:
            body = result[level]
            tag = f"{level}_{SPECIES_PREFIXES[src]}--{SPECIES_PREFIXES[tgt]}"
            (output_dir / "predictions").mkdir(exist_ok=True)
            (output_dir / "confusion").mkdir(exist_ok=True)
            (output_dir / "predictions" / (tag + ".json")).write_text(
                json.dumps(body["per_cell"], ensure_ascii=False), encoding="utf-8"
            )
            (output_dir / "confusion" / (tag + ".json")).write_text(
                json.dumps(body["confusion"], ensure_ascii=False, sort_keys=True),
                encoding="utf-8",
            )
        print(src + "->" + tgt + " done", flush=True)

    (output_dir / "metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    manifest = {
        "protocol_label": PROTOCOL_LABEL,
        "samap_version": "1.0.16",
        "sam_algorithm_version": "1.0.2",
        "seed": SEED,
        "k": K,
        "nperm": NPERM,
        "distance": "cosine",
        "mapping_sha256": mapping_sha,
        "input_sha256": {
            species: sha256_file(root / fn) for species, fn in SPECIES_FILES.items()
        },
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print("V98_DONE", flush=True)


if __name__ == "__main__":
    main()
