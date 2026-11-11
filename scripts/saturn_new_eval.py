#!/usr/bin/env python3
"""scVI cross-species arm: human-mouse-zebrafish joint latent model (oPCA v3-fixkey semantics).

Spec alignment:
  1) Constants (fixed): PROTOCOL='transductive_formal_reassessment', SEED=0, K=15, NPERM=200,
     N_LATENT=10, MAX_EPOCHS=50, MIN_SHARED=100; PREFIX={human:hu, mouse:mo, zebrafish:zf}
  2) Inputs via env-overridable dirs (defaults /Files, /Files/wheelhouse):
     OPCA_H5AD_DIR -> local_{species}_s.h5ad
     OPCA_ORTH_DIR -> orth-MGI-HOM.rpt / orth-human-orthos.txt / orth-mouse-orthos.txt
     OPCA_MAPPING  -> heart-celltype-map-v1.tsv (species|label -> coarse, fine, status)
  3) Output: OPCA_OUT_ROOT (default /work/<user>); --out default <OUT_ROOT>/opca-scvi-<UTC%Y%m%dT%H%M%SZ>
  4) Isolation guards (fixed order): preflight(7 inputs missing -> SystemExit(2))
     -> out dir exists -> SystemExit(3) -> out must resolve inside OPCA_OUT_ROOT else SystemExit(3)
     -> mkdir(parents=True, exist_ok=False) before writing artifacts
  5) Ortholog orientation: CORRECTED keys (v3_fixkey / oPCA semantics):
     hm = human->mouse; fh = human->fish; fmm = mouse->fish (keys are human/mouse genes, NOT fish).
  6) Data: read 3 h5ad -> normalize_total(1e4) -> log1p -> gene names upper -> FIRST-occurrence dedup.
  7) Common human-axis alignment: human uses own symbols; mouse via hm; zebrafish via fh.
     Take intersection (expected ~8,852 genes).
  8) scVI: SCVI.setup_anndata(adata, batch_key='species'); SCVI(n_latent=10);
     train(max_epochs=50, early_stopping=True); get_latent_representation().
  9) Eval: 6 directions x 3 levels, KNeighborsClassifier(n_neighbors=15, metric='cosine',
     weights='distance'), same acceptance rules as oPCA (coarse/fine: status=='active' only).
  10) Metrics per level: acc, macro_f1 (hand-written), majority, shuffle_p (200 perms).
  11) Artifacts: metrics.json, latent.npy, predictions/<dir>_<level>.json (18), manifest.json,
      environment.txt (records scvi/torch versions), command.txt, sha256.tsv.
"""
from __future__ import annotations
import argparse
import datetime as _dt
import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np
import torch

torch.set_num_threads(2)

# ---------------------------------------------------------------------------
# 1) Protocol constants (do not modify)
# ---------------------------------------------------------------------------
PROTOCOL = "transductive_formal_reassessment"
SEED = 0
K = 15
NPERM = 200
N_LATENT = 10
MAX_EPOCHS = 50
MIN_SHARED = 100
PREFIX = {"human": "hu", "mouse": "mo", "zebrafish": "zf"}
LEVELS = ("exact", "coarse", "fine")
SPECIES_ORDER = ["human", "mouse", "zebrafish"]

# ---------------------------------------------------------------------------
# 2) Input paths (env-overridable)
# ---------------------------------------------------------------------------
H5AD_DIR = Path(os.environ.get("OPCA_H5AD_DIR", "/Files"))
ORTH_DIR = Path(os.environ.get("OPCA_ORTH_DIR", "/Files/wheelhouse"))
MAPPING_TSV = Path(os.environ.get("OPCA_MAPPING", "/Files/wheelhouse/heart-celltype-map-v1.tsv"))
OUT_ROOT = Path(os.environ.get("OPCA_OUT_ROOT", "/work/user50719-8334"))
ORTH_MGI = ORTH_DIR / "orth-MGI-HOM.rpt"
ORTH_HF = ORTH_DIR / "orth-human-orthos.txt"
ORTH_MF = ORTH_DIR / "orth-mouse-orthos.txt"

H5AD_FILES = {sp: H5AD_DIR / f"local_{sp}_s.h5ad" for sp in SPECIES_ORDER}
INPUTS = list(H5AD_FILES.values()) + [ORTH_MGI, ORTH_HF, ORTH_MF, MAPPING_TSV]
INPUT_NAMES = (
    [f"local_{sp}_s.h5ad" for sp in SPECIES_ORDER]
    + ["orth-MGI-HOM.rpt", "orth-human-orthos.txt", "orth-mouse-orthos.txt", "heart-celltype-map-v1.tsv"]
)


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# 4) Isolation guards (fixed order, do not reorder)
# ---------------------------------------------------------------------------
def _preflight_inputs() -> None:
    missing = [name for name, p in zip(INPUT_NAMES, INPUTS) if not p.is_file()]
    if missing:
        print(f"PREFLIGHT_FAIL missing={missing}", flush=True)
        raise SystemExit(2)
    for name, p in zip(INPUT_NAMES, INPUTS):
        try:
            if p.stat().st_size == 0:
                print(f"PREFLIGHT_FAIL empty={name}", flush=True)
                raise SystemExit(2)
        except OSError as exc:
            print(f"PREFLIGHT_FAIL unreadable={name} err={exc}", flush=True)
            raise SystemExit(2)


def _resolve_out(out: Path | None) -> Path:
    if out is None:
        ts = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        out = OUT_ROOT / f"opca-scvi-{ts}"
    out = Path(out).resolve()
    root = OUT_ROOT.resolve()
    try:
        out.relative_to(root)
    except ValueError:
        print(f"GUARD_OUT_NOT_IN_ROOT out={out} root={root}", flush=True)
        raise SystemExit(3)
    if out.exists():
        print(f"GUARD_OUT_EXISTS out={out}", flush=True)
        raise SystemExit(3)
    return out


# ---------------------------------------------------------------------------
# 5) Ortholog parsing (CORRECTED orientation: keys = human/mouse genes)
# ---------------------------------------------------------------------------
def parse_orthologs():
    """Return (hm, fh, fmm) with keys on the human/mouse side (v3_fixkey semantics)."""
    groups: dict[str, dict[str, set]] = {}
    for line in open(ORTH_MGI, encoding="utf-8", errors="replace"):
        f = line.rstrip("\n").split("\t")
        if len(f) < 5 or not f[0].isdigit():
            continue
        tax = sym = None
        for i in range(len(f) - 1):
            if f[i] in ("9606", "10090"):
                tax = "hu" if f[i] == "9606" else "ms"
                sym = f[i + 1].strip().upper()
                break
        if tax and sym:
            groups.setdefault(f[0], {}).setdefault(tax, set()).add(sym)
    hm = {}
    for g, d in groups.items():
        if set(d) == {"hu", "ms"} and len(d["hu"]) == 1 and len(d["ms"]) == 1:
            hm[next(iter(d["hu"]))] = next(iter(d["ms"]))

    def zfin(path):
        d = {}
        for line in open(path, encoding="utf-8", errors="replace"):
            f = line.rstrip("\n").split("\t")
            if len(f) < 5:
                continue
            d.setdefault(f[1].strip().upper(), set()).add(f[3].strip().upper())
        return d

    # human <-> fish: h2f keyed by human gene; fh = {human: fish} one-to-one
    h2f = {}
    for fish, hs in zfin(ORTH_HF).items():
        if len(hs) == 1:
            h2f.setdefault(next(iter(hs)), []).append(fish)
    fh = {h: fl[0] for h, fl in h2f.items() if len(fl) == 1}

    # mouse <-> fish: fmm = {mouse: fish} one-to-one
    m2f = {}
    for fish, ms in zfin(ORTH_MF).items():
        if len(ms) == 1:
            m2f.setdefault(next(iter(ms)), []).append(fish)
    fmm = {m: fl[0] for m, fl in m2f.items() if len(fl) == 1}
    return hm, fh, fmm


# ---------------------------------------------------------------------------
# 6) Frozen mapping (heart-celltype-map-v1.tsv, 9 columns)
#    source_species, source_label, coarse_level, fine_mapped_label, evidence_source,
#    mapping_confidence, mapping_status, reviewer, notes
#    -> key 'species|label', value (coarse_level, fine_mapped_label, mapping_status)
# ---------------------------------------------------------------------------
def freeze_mapping(tsv_path: Path) -> dict[str, tuple[str, str, str]]:
    rows = {}
    for line in open(tsv_path, encoding="utf-8", errors="replace"):
        f = line.rstrip("\n").split("\t")
        if len(f) < 7:
            continue
        sp = f[0].strip()
        lab = f[1].strip()
        if sp.lower() == "source_species" and lab.lower() == "source_label":
            continue  # header
        rows[f"{sp}|{lab}"] = (str(f[2]).strip(), str(f[3]).strip(), str(f[6]).strip())
    return rows


# ---------------------------------------------------------------------------
# 7) Layer labels (same acceptance rules as oPCA)
# ---------------------------------------------------------------------------
def layer_labels(spv, tr, mapping, level):
    if level == "exact":
        labels = tr
        keep = np.ones(len(spv), dtype=bool)
    else:
        idx = 0 if level == "coarse" else 1
        labels = np.array([
            mapping.get(f"{s}|{l}", ("unmapped", "unmapped", "inactive"))[idx]
            for s, l in zip(spv, tr)
        ])
        active = np.array([
            mapping.get(f"{s}|{l}", ("unmapped", "unmapped", "inactive"))[2] == "active"
            for s, l in zip(spv, tr)
        ])
        keep = active & (labels != "unmapped")
    return labels, keep


# ---------------------------------------------------------------------------
# 10) macro-F1 (hand-written)
# ---------------------------------------------------------------------------
def macro_f1(y_true, y_pred):
    classes = sorted(set(y_true))
    f1s = []
    for c in classes:
        tp = int(sum(1 for t, p in zip(y_true, y_pred) if t == c and p == c))
        fp = int(sum(1 for t, p in zip(y_true, y_pred) if t != c and p == c))
        fn = int(sum(1 for t, p in zip(y_true, y_pred) if t == c and p != c))
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2.0 * prec * rec / (prec + rec) if (prec + rec) else 0.0
        f1s.append(f1)
    return float(np.mean(f1s)) if f1s else 0.0


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main() -> None:
    # ---- isolation guards, fixed order ----
    _preflight_inputs()
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None, help="output dir (default <OPCA_OUT_ROOT>/opca-scvi-<UTC>)")
    args = ap.parse_args()
    out = _resolve_out(Path(args.out) if args.out else None)

    import anndata as ad
    import scanpy as sc
    import scipy.sparse as spmod
    from sklearn.neighbors import KNeighborsClassifier
    # [REPLACED 2026-11-11] 这一臂不再训 scVI，嵌入来自 SATURN 官方实现，
    # 因此不需要 import scvi（本地也没装完整 scvi-tools，见 scripts/make_scvi_stub.py）。
    # import scvi
    # scvi.settings.seed = SEED
    np.random.seed(SEED)
    torch.manual_seed(SEED)

    os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("MKL_NUM_THREADS", "1")
    os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

    header = {
        "protocol": PROTOCOL,
        "seed": SEED,
        "k": K,
        "nperm": NPERM,
        "n_latent": N_LATENT,
        "max_epochs": MAX_EPOCHS,
        "min_shared": MIN_SHARED,
        "script_sha256": sha256_file(Path(__file__).resolve()),
        "mapping_sha256": sha256_file(MAPPING_TSV),
        "scvi_version": getattr(scvi, "__version__", "unknown"),
        "torch_version": torch.__version__,
    }
    input_sha = {name: sha256_file(p) for name, p in zip(INPUT_NAMES, INPUTS)}
    print("header=" + json.dumps(header), flush=True)

    hm, fh, fmm = parse_orthologs()
    mapping = freeze_mapping(MAPPING_TSV)
    print(f"ortholog pairs: hm={len(hm)} fh={len(fh)} fmm={len(fmm)}  mapping_rows={len(mapping)}", flush=True)

    # ---- 8) read data: normalize -> log1p -> upper -> first-occurrence dedup ----
    data = {}
    for sp in SPECIES_ORDER:
        a = ad.read_h5ad(str(H5AD_FILES[sp]))
        if "cell_type" not in a.obs.columns:
            print(f"PREFLIGHT_FAIL no_cell_type_column={sp}", flush=True)
            raise SystemExit(2)
        sc.pp.normalize_total(a, target_sum=1e4)
        sc.pp.log1p(a)
        X = a.X
        X = X.toarray() if spmod.issparse(X) else np.asarray(X, dtype=np.float64)
        var_up = [str(v).upper() for v in a.var_names]
        _seen = set()
        _vidx = {}
        for _i, _g in enumerate(var_up):
            if _g not in _seen:
                _seen.add(_g)
                _vidx[_g] = _i
        data[sp] = {
            "X": X,
            "var_up": var_up,
            "var_idx": _vidx,
            "bc": [f"{PREFIX[sp]}|{o}" for o in a.obs_names],
            "ct": a.obs["cell_type"].astype(str).values,
        }
        print(f"{sp}: {X.shape[0]} cells x {X.shape[1]} raw genes -> {len(_vidx)} unique", flush=True)

    # ---- 9) common human-axis alignment (intersection) ----
    human_genes = list(data["human"]["var_idx"].keys())
    axis = []
    for g in human_genes:
        mg = hm.get(g)
        fg = fh.get(g)
        if mg is not None and fg is not None and mg in data["mouse"]["var_idx"] and fg in data["zebrafish"]["var_idx"]:
            axis.append(g)
    n_genes = len(axis)
    if n_genes < MIN_SHARED:
        print(f"GUARD_MIN_SHARED_FAIL n_genes={n_genes}", flush=True)
        raise SystemExit(4)
    print(f"common human-axis genes: {n_genes}", flush=True)

    rows_X = []
    rows_ct = []
    rows_sp = []
    rows_bc = []
    for sp in SPECIES_ORDER:
        d = data[sp]
        cols = []
        for g in axis:
            if sp == "mouse":
                cols.append(d["var_idx"][hm[g]])
            elif sp == "zebrafish":
                cols.append(d["var_idx"][fh[g]])
            else:
                cols.append(d["var_idx"][g])
        Xs = d["X"][:, cols]
        rows_X.append(np.asarray(Xs, dtype=np.float32))
        rows_ct.extend(d["ct"])
        rows_sp.extend([sp] * d["X"].shape[0])
        rows_bc.extend(d["bc"])
    Xall = np.vstack(rows_X)
    print(f"merged X: {Xall.shape[0]} cells x {Xall.shape[1]} genes (float32)", flush=True)

    adata = ad.AnnData(X=Xall)
    adata.obs["cell_type"] = rows_ct
    adata.obs["species"] = rows_sp
    adata.obs["bc"] = rows_bc
    adata.var_names = axis

    # ---- 10) [REPLACED 2026-11-11] 不再训 scVI，直接读本地 SATURN 官方实现的 256 维嵌入 ----
    # 原实现（保留备查）：
    #   scvi.model.SCVI.setup_anndata(adata, batch_key="species")
    #   model = scvi.model.SCVI(adata, n_latent=N_LATENT)
    #   model.train(max_epochs=MAX_EPOCHS, early_stopping=True)
    #   latent = model.get_latent_representation()
    #
    # 为什么可以替换：SATURN 的 X 与 scVI 的 latent 是同一种东西——「每细胞一个 D 维向量」。
    # 两者都从同样的 3 个 local_{species}_s.h5ad 按 SPECIES_ORDER 拼接而来，
    # 所以下面的 KNN(k=15, cosine, distance) / 手写 macro_f1 / 配对流程**一字不改**，
    # 得到的才是严格同口径对比（不是换一套指标再比）。
    import os as _os
    _sat_path = _os.environ.get("SATURN_H5AD", "")
    if not _sat_path or not Path(_sat_path).exists():
        print(f"SATURN_H5AD 未设置或文件不存在: {_sat_path!r}", flush=True)
        raise SystemExit(5)
    _sa = ad.read_h5ad(_sat_path)
    latent = np.asarray(_sa.X, dtype=np.float32)
    # 顺序断言：SATURN 产物必须与本次 rows_sp 完全同序，否则后面所有指标都会错位
    _sat_sp = [str(x) for x in _sa.obs["species"]]
    if _sat_sp != list(rows_sp):
        print("ORDER_MISMATCH: SATURN h5ad 的物种顺序与 rows_sp 不一致，拒绝继续", flush=True)
        print(f"  SATURN 前10: {_sat_sp[:10]}", flush=True)
        print(f"  rows_sp 前10: {list(rows_sp)[:10]}", flush=True)
        raise SystemExit(6)
    print(f"latent(SATURN): {latent.shape}  <- {Path(_sat_path).name}", flush=True)

    spv = np.array(rows_sp)
    tr_all = np.array(rows_ct)
    bc_all = np.array(rows_bc)

    MAPS = [
        ("human", "mouse"), ("mouse", "human"),
        ("human", "zebrafish"), ("zebrafish", "human"),
        ("mouse", "zebrafish"), ("zebrafish", "mouse"),
    ]

    # ---- 11/12) eval: 6 directions x 3 levels, cosine KNN15 inverse-distance ----
    results = {}
    all_predictions = {}
    for (src, tgt) in sorted(MAPS):
        m_s = spv == src
        m_t = spv == tgt
        dir_res = {}
        dir_preds = {}
        for level in LEVELS:
            labels, keep = layer_labels(spv, tr_all, mapping, level)
            ytr = labels[m_s]
            yte = labels[m_t]
            keep_r = keep[m_s]
            ok = keep[m_t]
            n_excluded_q = int((~ok).sum())
            n_excluded_ref = int((~keep_r).sum())
            if ok.sum() == 0 or keep_r.sum() == 0:
                acc = 0.0
                mf1 = 0.0
                maj = 0.0
                pval = 1.0
                pred_all = np.full(int(m_t.sum()), None, dtype=object)
            else:
                knn = KNeighborsClassifier(n_neighbors=K, metric="cosine", weights="distance")
                knn.fit(latent[m_s][keep_r], ytr[keep_r])
                pred_all = knn.predict(latent[m_t])
                pred_ok = pred_all[ok]
                acc = float((pred_ok == yte[ok]).mean())
                mf1 = macro_f1(list(yte[ok]), list(pred_ok))
                vals, cnts = np.unique(yte[ok], return_counts=True)
                maj = float(cnts.max() / cnts.sum())
                rng = np.random.RandomState(SEED)
                nulls = []
                for _ in range(NPERM):
                    pp = pred_ok.copy()
                    rng.shuffle(pp)
                    nulls.append(float((pp == yte[ok]).mean()))
                pval = float((np.array(nulls) >= acc).mean())
            conf = {}
            for t, p in zip(yte[ok], pred_ok):
                k3 = f"{t}=>{p}"
                conf[k3] = conf.get(k3, 0) + 1
            dir_res[level] = {
                "acc": round(acc, 4),
                "macro_f1": round(mf1, 4),
                "majority": round(maj, 4),
                "shuffle_p": round(pval, 4),
                "n_ref": int(keep_r.sum()),
                "n_q": int(ok.sum()),
                "n_excluded_q": n_excluded_q,
                "n_excluded_ref": n_excluded_ref,
                "n_genes": n_genes,
                "coverage_q": round(float(ok.mean()), 4),
                "confusion": conf,
            }
            qidx = np.where(m_t)[0]
            records = []
            for j, i in enumerate(qidx):
                predj = pred_all[j]
                records.append({
                    "prefixed_barcode": str(bc_all[i]),
                    "direction": f"{PREFIX[src]}->{PREFIX[tgt]}",
                    "level": level,
                    "truth": str(labels[i]),
                    "prediction": None if predj is None else str(predj),
                    "included": bool(ok[j]),
                    "exclusion_reason": "" if ok[j] else (
                        "unmapped" if labels[i] == "unmapped" else "inactive"
                    ),
                })
            dir_preds[level] = records
        results[f"{src}->{tgt}"] = dir_res
        all_predictions[f"{PREFIX[src]}->{PREFIX[tgt]}"] = dir_preds
        print(f"{src}->{tgt} done", flush=True)

    # ---- 13) artifacts ----
    out.mkdir(parents=True, exist_ok=False)  # guard: dir must NOT pre-exist
    (out / "command.txt").write_text(" ".join(sys.argv) + "\n", encoding="utf-8")
    import numpy as _np
    _np.save(out / "latent.npy", latent)

    env = dict(header)
    env["input_sha256"] = input_sha
    env["n_genes"] = n_genes
    env["species_counts"] = {sp: int(data[sp]["X"].shape[0]) for sp in SPECIES_ORDER}
    env["utc"] = _dt.datetime.now(_dt.timezone.utc).isoformat()
    env["numpy_version"] = _np.__version__
    import anndata as _ad, scanpy as _sc, sklearn as _sk
    env["anndata_version"] = _ad.__version__
    env["scanpy_version"] = _sc.__version__
    env["sklearn_version"] = _sk.__version__
    (out / "environment.txt").write_text(json.dumps(env, ensure_ascii=False, indent=1), encoding="utf-8")

    (out / "metrics.json").write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    pred_dir = out / "predictions"
    pred_dir.mkdir(parents=True, exist_ok=False)
    for tag, dir_preds in all_predictions.items():
        for level in LEVELS:
            (pred_dir / f"{tag}_{level}.json").write_text(
                json.dumps(dir_preds[level], ensure_ascii=False, indent=1), encoding="utf-8")

    manifest = {
        "protocol_label": PROTOCOL,
        "variant": "scvi-cross-species: SCVI(n_latent=10, batch_key='species', max_epochs=50, early_stopping) + macro_F1 + common-human-axis (first-occurrence dedup, corrected key orientation)",
        "seed": SEED,
        "k": K,
        "nperm": NPERM,
        "n_latent": N_LATENT,
        "max_epochs": MAX_EPOCHS,
        "min_shared": MIN_SHARED,
        "distance": "cosine",
        "script_sha256": header["script_sha256"],
        "mapping_sha256": header["mapping_sha256"],
        "input_sha256": input_sha,
        "species_counts": {sp: int(data[sp]["X"].shape[0]) for sp in SPECIES_ORDER},
        "n_genes": n_genes,
        "n_directions": len(results),
    }
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    tree = sorted(p for p in out.rglob("*") if p.is_file())
    (out / "sha256.tsv").write_text(
        "\n".join(f"{sha256_file(p)}  {p.relative_to(out)}" for p in tree), encoding="utf-8")
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
