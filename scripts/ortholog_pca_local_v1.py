"""Ortholog-PCA local recompute, Gate-2 fixed (v1).

Protocol (frozen, matches docs/wave3-ortholog-pca-manifest-20260930.md):
  normalisation log1p(CPM/100) == normalize_total(1e4)+log1p on the FULL gene
  space before ortholog subsetting; joint PCA-50 (seed 0) over
  source+target on 1:1 shared orthologs; KNN K=15, metric=cosine,
  inverse-distance weighting; 200-permutation RandomState(0) shuffle of query
  predictions (20 in --smoke); mapping table v1 string keys "species|label",
  coarse/fine exclude mapping_status != active on BOTH reference and query
  sides; exact layer keeps every valid truth label.

Hard stops (non-zero exit): missing input, <1000 shared ortholog genes in any
direction, duplicate barcodes/genes, empty/NaN truth labels.

Roles per direction "src->tgt": src = reference (KNN fit), tgt = query.

--smoke writes ONLY results/pilot-v1/ortholog-pca-smoke/ with 120 cells per
species; smoke numbers never enter main tables.  Full mode writes
results/pilot-v1/ortholog-pca-v98/ with manifest, environment, command,
metrics, 18 predictions, 18 confusion, and SHA-256 of every output.
"""
import argparse
import hashlib
import json
import os
import platform
import sys
import time
from pathlib import Path

import numpy as np

BASE = Path(__file__).resolve().parents[1]
ORTH_DIR = BASE / "ortholog"
MAPPING_TSV = BASE / "config" / "heart-celltype-map-v1.tsv"
PROTOCOL = "transductive_formal_reassessment"
SEED = 0
K = 15
NPERM_FULL = 200
NPERM_SMOKE = 20
NPCS = 50
MIN_SHARED = 1000
SMOKE_CELLS = 120
PREFIX = {"human": "hu", "mouse": "mo", "zebrafish": "zf"}
SPECIES_FILES = {s: BASE / f"local_{s}_s.h5ad" for s in ["human", "mouse", "zebrafish"]}
LEVELS = ("exact", "coarse", "fine")


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def die(msg, code=2):
    print(f"HARDSTOP|{msg}", flush=True)
    sys.exit(code)


def parse_orthologs():
    groups = {}
    for line in open(ORTH_DIR / "MGI_HOM_MouseHumanSequence.rpt", encoding="utf-8", errors="replace"):
        f = line.rstrip("\n").split("\t")
        if len(f) < 5 or not f[0].isdigit():
            continue
        tax = None
        sym = None
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

    def one_to_one(raw):
        fwd = {}
        bwd = {}
        for fish, others in raw.items():
            if len(others) == 1:
                o = next(iter(others))
                fwd[fish] = o
                bwd.setdefault(o, []).append(fish)
        return {f: o for f, o in fwd.items() if len(bwd[o]) == 1}

    fh = one_to_one(zfin(ORTH_DIR / "human_orthos.txt"))
    fmm = one_to_one(zfin(ORTH_DIR / "mouse_orthos.txt"))
    return hm, fh, fmm


def freeze_mapping(tsv):
    import csv
    rows = {}
    for row in csv.DictReader(open(tsv, encoding="utf-8-sig", newline=""), delimiter="\t"):
        key = row["source_species"].strip() + "|" + row["source_label"].strip()
        rows[key] = {
            "coarse": row["coarse_level"].strip(),
            "fine": row["fine_mapped_label"].strip(),
            "status": row["mapping_status"].strip(),
        }
    return rows


def layer_labels(spv, tr, mapping, level):
    """Per-cell (labels, included, exclusion_reason) for one label layer.

    exact: every valid truth label is included.  coarse/fine: included only
    when the species|label row exists AND mapping_status == active; layer
    value is coarse_level / fine_mapped_label with unmapped sentinel handling.
    """
    labels = np.empty(len(tr), dtype=object)
    included = np.zeros(len(tr), dtype=bool)
    reason = np.empty(len(tr), dtype=object)
    for i in range(len(tr)):
        sp = spv[i]
        raw = tr[i]
        row = mapping.get(sp + "|" + raw)
        if level == "exact":
            labels[i] = raw
            included[i] = bool(raw)
            reason[i] = "" if raw else "empty_truth"
            continue
        if row is None:
            labels[i] = "unmapped"
            reason[i] = "no_mapping_row"
        elif row["status"] != "active":
            labels[i] = "unmapped"
            reason[i] = "mapping_status:" + row["status"]
        else:
            labels[i] = row[level] if row[level] else "unmapped"
            reason[i] = "" if labels[i] != "unmapped" else "layer_value_unmapped"
        included[i] = reason[i] == ""
    return labels, included, reason


def main():
    t0 = time.time()
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    smoke = args.smoke
    nperm = NPERM_SMOKE if smoke else NPERM_FULL
    out = BASE / "results" / "pilot-v1" / ("ortholog-pca-smoke" if smoke else "ortholog-pca-v98")
    if smoke and out.exists():
        die("smoke output dir already exists: %s (refusing to overwrite)" % out, 3)
    (out / "predictions").mkdir(parents=True, exist_ok=True)
    (out / "confusion").mkdir(parents=True, exist_ok=True)

    command = " ".join([sys.executable.replace("\\", "/")] + sys.argv)
    inputs = {
        "mapping": str(MAPPING_TSV),
        "orth_human_mouse": str(ORTH_DIR / "MGI_HOM_MouseHumanSequence.rpt"),
        "orth_human_fish": str(ORTH_DIR / "human_orthos.txt"),
        "orth_mouse_fish": str(ORTH_DIR / "mouse_orthos.txt"),
    }
    for sp, p in SPECIES_FILES.items():
        inputs[sp] = str(p)
    for p in inputs.values():
        if not Path(p).exists():
            die("missing input: %s" % p)
    input_sha = {k: sha256_file(v) for k, v in inputs.items()}

    hm, fh, fmm = parse_orthologs()
    mapping = freeze_mapping(MAPPING_TSV)
    print(f"ortholog pairs: hm={len(hm)} fh={len(fh)} fmm={len(fmm)}; mapping rows={len(mapping)}", flush=True)

    import anndata as ad
    import scanpy as sc
    import scipy.sparse as spmod
    import sklearn
    from sklearn.decomposition import PCA
    from sklearn.neighbors import KNeighborsClassifier

    data = {}
    gene_dedup = {}
    for sp in ["human", "mouse", "zebrafish"]:
        a = ad.read_h5ad(str(SPECIES_FILES[sp]))
        if a.obs_names.duplicated().any():
            die(f"{sp}: duplicate obs_names")
        if "cell_type" not in a.obs:
            die(f"{sp}: missing cell_type column")
        ct = a.obs["cell_type"].astype(str).values
        if any((not c) or c.lower() == "nan" for c in ct):
            die(f"{sp}: empty/NaN truth labels")
        sc.pp.normalize_total(a, target_sum=1e4)
        sc.pp.log1p(a)
        X = a.X
        if not spmod.issparse(X):
            X = spmod.csr_matrix(np.asarray(X))
        var_up = [str(v).upper() for v in a.var_names]
        seen = set()
        keep_cols = []
        for i, g in enumerate(var_up):
            if g not in seen:
                seen.add(g)
                keep_cols.append(i)
        dropped = len(var_up) - len(keep_cols)
        if dropped:
            # Deterministic first-occurrence dedup AFTER full-space normalisation,
            # so per-cell normalisation denominators stay protocol-exact.
            X = X[:, keep_cols]
            var_up = [var_up[i] for i in keep_cols]
        bc = np.array([f"{PREFIX[sp]}|{o}" for o in a.obs_names])
        if len(set(bc)) != len(bc):
            die(f"{sp}: duplicate prefixed barcodes")
        if smoke:
            rng = np.random.RandomState(SEED)
            keep = rng.choice(X.shape[0], size=min(SMOKE_CELLS, X.shape[0]), replace=False)
            keep.sort()
            X = X[keep]
            bc = bc[keep]
            ct = ct[keep]
        data[sp] = {"X": X, "var_idx": {g: i for i, g in enumerate(var_up)}, "bc": bc, "ct": ct}
        gene_dedup[sp] = dropped
        print(f"{sp}: {X.shape[0]} cells x {len(var_up)} genes (dropped {dropped} dup symbols)", flush=True)

    MAPS = {("human", "mouse"): hm, ("mouse", "human"): {v: k for k, v in hm.items()},
            ("human", "zebrafish"): fh, ("zebrafish", "human"): {v: k for k, v in fh.items()},
            ("mouse", "zebrafish"): fmm, ("zebrafish", "mouse"): {v: k for k, v in fmm.items()}}

    results = {}
    for (src, tgt), smap in sorted(MAPS.items()):
        d_s, d_t = data[src], data[tgt]
        shared = []
        used_s, used_t = set(), set()
        for su, tu in smap.items():
            if su in d_s["var_idx"] and tu in d_t["var_idx"] and su not in used_s and tu not in used_t:
                shared.append((su, tu))
                used_s.add(su)
                used_t.add(tu)
        if len(shared) < MIN_SHARED:
            die(f"{src}->{tgt}: only {len(shared)} shared 1:1 orthologs (< {MIN_SHARED})")
        idx_s = [d_s["var_idx"][g] for g, _ in shared]
        idx_t = [d_t["var_idx"][t] for _, t in shared]
        Xs = d_s["X"][:, idx_s]
        Xt = d_t["X"][:, idx_t]
        Xs = Xs.toarray() if spmod.issparse(Xs) else np.asarray(Xs)
        Xt = Xt.toarray() if spmod.issparse(Xt) else np.asarray(Xt)
        X_joint = np.vstack([Xs, Xt]).astype(np.float64)
        spv = np.array([src] * Xs.shape[0] + [tgt] * Xt.shape[0])
        tr = np.array(list(d_s["ct"]) + list(d_t["ct"]))
        bcall = np.array(list(d_s["bc"]) + list(d_t["bc"]))
        Z = PCA(n_components=NPCS, random_state=SEED).fit_transform(X_joint)
        m_s, m_t = spv == src, spv == tgt
        dir_res = {}
        for level in LEVELS:
            labels, included, reason = layer_labels(spv, tr, mapping, level)
            ytr, yte = labels[m_s], labels[m_t]
            keep_r, ok = included[m_s], included[m_t]
            knn = KNeighborsClassifier(n_neighbors=K, metric="cosine", weights="distance")
            knn.fit(Z[m_s][keep_r], ytr[keep_r])
            pred_all = knn.predict(Z[m_t])
            proba_all = knn.predict_proba(Z[m_t])
            cls = knn.classes_
            neigh_idx = knn.kneighbors(Z[m_t], n_neighbors=K, return_distance=False)
            # 邻居索引是"该层级剔除 unmapped reference 后的训练子集"的下标，
            # 必须逐层重建对应条码表（Claude Gate 3 审阅发现的错位 bug 修复）。
            bc_ref_kept = bcall[m_s][keep_r]
            pred_ok = pred_all[ok]
            yte_ok = yte[ok]
            acc = float((pred_ok == yte_ok).mean()) if ok.sum() else 0.0
            vals, cnts = np.unique(yte_ok, return_counts=True)
            maj = float(cnts.max() / cnts.sum()) if cnts.sum() else 0.0
            rng = np.random.RandomState(SEED)
            nulls = []
            for _ in range(nperm):
                pp = pred_ok.copy()
                rng.shuffle(pp)
                nulls.append(float((pp == yte_ok).mean()))
            pval = float((np.array(nulls) >= acc).mean()) if ok.sum() else 1.0
            conf = {}
            for t, p in zip(yte_ok, pred_ok):
                key = f"{t}=>{p}"
                conf[key] = conf.get(key, 0) + 1
            proba_cls = {c: j for j, c in enumerate(cls)}
            rows = []
            q_bc = bcall[m_t]
            q_truth = yte
            q_reason = reason[m_t]
            for j in range(len(q_bc)):
                inc = bool(ok[j])
                pr = str(pred_all[j])
                rows.append({
                    "prefixed_barcode": str(q_bc[j]),
                    "direction": f"{src}->{tgt}",
                    "level": level,
                    "truth": str(q_truth[j]),
                    "prediction": pr,
                    "included": inc,
                    "exclusion_reason": str(q_reason[j]),
                    "confidence": round(float(proba_all[j][proba_cls[pr]]), 4) if inc else 0.0,
                    "neighbor_barcodes": [str(x) for x in bc_ref_kept[neigh_idx[j]]],
                })
            name = f"{level}_{src}_to_{tgt}.json"  # ">" is illegal in Windows filenames
            (out / "predictions" / name).write_text(
                json.dumps(rows, ensure_ascii=False), encoding="utf-8")
            (out / "confusion" / name).write_text(
                json.dumps(conf, ensure_ascii=False, sort_keys=True), encoding="utf-8")
            dir_res[level] = {
                "acc": round(acc, 4), "majority": round(maj, 4), "shuffle_p": round(pval, 4),
                "n_ref": int(keep_r.sum()), "n_q": int(ok.sum()),
                "n_q_total": int(len(q_bc)),
                "coverage_q": round(float(ok.mean()), 4), "confusion": conf,
                "n_perm": nperm, "shared_genes": len(shared),
            }
        results[f"{src}->{tgt}"] = dir_res
        print(f"{src}->{tgt} done genes={len(shared)} acc(exact)={dir_res['exact']['acc']}", flush=True)

    (out / "metrics.json").write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "environment.json").write_text(json.dumps({
        "python": platform.python_version(), "platform": platform.platform(),
        "numpy": np.__version__, "anndata": ad.__version__, "scanpy": sc.__version__,
        "sklearn": sklearn.__version__, "command": command,
    }, indent=1), encoding="utf-8")
    (out / "command.txt").write_text(command + "\n", encoding="utf-8")

    outputs = {}
    for p in sorted(out.rglob("*")):
        if p.is_file():
            outputs[str(p.relative_to(out)).replace(os.sep, "/")] = sha256_file(p)
    manifest = {
        "protocol": PROTOCOL,
        "mode": "smoke" if smoke else "full",
        "roles": "src=reference(knn fit) tgt=query",
        "params": {"seed": SEED, "k": K, "npcs": NPCS, "nperm": nperm,
                   "min_shared_genes": MIN_SHARED,
                   "normalisation": "log1p(CPM/100) = normalize_total(1e4)+log1p full-gene-space",
                   "gene_symbol_dedup_dropped": gene_dedup},
        "script_sha256": sha256_file(__file__),
        "inputs": inputs, "input_sha256": input_sha,
        "output_sha256": outputs,
        "note": "manifest.json 自身不在 output_sha256 内（哈希时未生成）",
        "started": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(t0)),
        "finished": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_sec": round(time.time() - t0, 1),
    }
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    print("DONE mode=%s elapsed=%ss" % ("smoke" if smoke else "full", manifest["elapsed_sec"]), flush=True)


if __name__ == "__main__":
    main()
