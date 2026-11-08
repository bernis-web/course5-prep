"""scVI 跨物种臂：三物种联合训练 → 6 方向 × 3 层 macro-F1。

设计依据：docs/plans/scvi-cross-species-design-20261017.md
  - 数据：/Files/local_{human,mouse,zebrafish}_s.h5ad（与 oPCA/SATURN/SAMap 同源）
  - 基因集：1:1 直系同源（修正方向后），与 oPCA 同口径
  - batch_key = species（跨物种批次）
  - 一次训练 + 六方向评估（与 SATURN 同为 transductive）
  - 评估：KNN15 cosine（与 oPCA 完全相同的评分口径）
  - 主指标：macro-F1（coarse 层）

隔离守卫（顺序固定）：
  1) 7 个输入缺失 → exit 2
  2) 输出目录已存在 → exit 3
  3) 输出必须落在 OPCA_OUT_ROOT 内 → exit 3
  4) mkdir(exist_ok=False)

产物：metrics.json / latent.npy / manifest.json / command.txt / environment.txt / sha256.tsv
"""
import csv
import hashlib
import json
import os
import platform
import sys
import time
from pathlib import Path

# BLAS 单线程（防 OOM）
for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np

PROTOCOL = "transductive_formal_reassessment"
SEED = 0
K = 15
NPERM = 200
N_LATENT = 10
MAX_EPOCHS = 50
MIN_SHARED = 100
PREFIX = {"human": "hu", "mouse": "mo", "zebrafish": "zf"}
LEVELS = ("exact", "coarse", "fine")

H5AD_DIR = Path(os.environ.get("OPCA_H5AD_DIR", "/Files"))
ORTH_DIR = Path(os.environ.get("OPCA_ORTH_DIR", "/Files/wheelhouse"))
MAPPING_TSV = Path(os.environ.get("OPCA_MAPPING", "/Files/wheelhouse/heart-celltype-map-v1.tsv"))
ORTH_MGI = Path(os.environ.get("OPCA_ORTH_MGI", str(ORTH_DIR / "orth-MGI-HOM.rpt")))
ORTH_HF = Path(os.environ.get("OPCA_ORTH_HF", str(ORTH_DIR / "orth-human-orthos.txt")))
ORTH_MF = Path(os.environ.get("OPCA_ORTH_MF", str(ORTH_DIR / "orth-mouse-orthos.txt")))
OUT_ROOT = Path(os.environ.get("OPCA_OUT_ROOT", "/work/user50719-8334"))

SPECIES_FILES = {s: H5AD_DIR / f"local_{s}_s.h5ad" for s in ("human", "mouse", "zebrafish")}


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def die(msg, code=2):
    print(f"HARDSTOP|{msg}", flush=True)
    sys.exit(code)


def preflight():
    """7 个输入必须全部存在（在创建任何输出目录之前）。"""
    need = list(SPECIES_FILES.values()) + [ORTH_MGI, ORTH_HF, ORTH_MF, MAPPING_TSV]
    missing = [str(p) for p in need if not p.exists()]
    if missing:
        die("PREFLIGHT_FAIL missing: " + "; ".join(missing))


def resolve_out():
    out = Path(os.environ.get(
        "OPCA_OUT",
        str(OUT_ROOT / ("scvi-cross-" + time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())))))
    out = out.resolve()
    if out.exists():
        die("output dir already exists: %s (refusing to overwrite)" % out, 3)
    try:
        out.relative_to(OUT_ROOT.resolve())
    except ValueError:
        die("output resolves outside OPCA_OUT_ROOT: %s" % out, 3)
    return out


def parse_orthologs():
    """修正方向：fh/fmm 键=人/鼠基因（与 v3_fixkey 同口径）。"""
    groups = {}
    for line in open(ORTH_MGI, encoding="utf-8", errors="replace"):
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

    h2f = {}
    for fish, hs in zfin(ORTH_HF).items():
        if len(hs) == 1:
            h2f.setdefault(next(iter(hs)), []).append(fish)
    fh = {h: fl[0] for h, fl in h2f.items() if len(fl) == 1}

    m2f = {}
    for fish, ms in zfin(ORTH_MF).items():
        if len(ms) == 1:
            m2f.setdefault(next(iter(ms)), []).append(fish)
    fmm = {m: fl[0] for m, fl in m2f.items() if len(fl) == 1}
    return hm, fh, fmm


def freeze_mapping(tsv):
    rows = {}
    for row in csv.DictReader(open(tsv, encoding="utf-8-sig", newline=""), delimiter="\t"):
        key = row["source_species"].strip() + "|" + row["source_label"].strip()
        rows[key] = (row["coarse_level"].strip(),
                     row["fine_mapped_label"].strip(),
                     row["mapping_status"].strip())
    return rows


def layer_labels(spv, tr, mapping, level):
    """与 oPCA 完全一致的标签层逻辑。"""
    labels = np.empty(len(tr), dtype=object)
    included = np.zeros(len(tr), dtype=bool)
    reason = np.empty(len(tr), dtype=object)
    for i in range(len(tr)):
        row = mapping.get(spv[i] + "|" + tr[i])
        if level == "exact":
            labels[i] = tr[i]
            included[i] = bool(tr[i])
            reason[i] = "" if tr[i] else "empty_truth"
            continue
        if row is None:
            labels[i] = "unmapped"
            reason[i] = "no_mapping_row"
        elif row[2] != "active":
            labels[i] = "unmapped"
            reason[i] = "mapping_status:" + row[2]
        else:
            idx = 0 if level == "coarse" else 1
            labels[i] = row[idx] if row[idx] else "unmapped"
            reason[i] = "" if labels[i] != "unmapped" else "layer_value_unmapped"
        included[i] = reason[i] == ""
    return labels, included, reason


def macro_f1(y_true, y_pred):
    labels = sorted(set(y_true) | set(y_pred))
    f1s = []
    for lab in labels:
        tp = sum(1 for t, p in zip(y_true, y_pred) if t == lab and p == lab)
        fp = sum(1 for t, p in zip(y_true, y_pred) if t != lab and p == lab)
        fn = sum(1 for t, p in zip(y_true, y_pred) if t == lab and p != lab)
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec = tp / (tp + fn) if (tp + fn) else 0.0
        f1s.append(2 * prec * rec / (prec + rec) if (prec + rec) else 0.0)
    return float(np.mean(f1s)) if f1s else 0.0


def main():
    t0 = time.time()
    preflight()
    out = resolve_out()
    (out / "predictions").mkdir(parents=True, exist_ok=False)

    inputs = dict(SPECIES_FILES)
    inputs.update({"orth_mgi": ORTH_MGI, "orth_hf": ORTH_HF, "orth_mf": ORTH_MF, "mapping": MAPPING_TSV})
    input_sha = {k: sha256_file(str(v)) for k, v in inputs.items()}

    hm, fh, fmm = parse_orthologs()
    mapping = freeze_mapping(MAPPING_TSV)
    print(f"ortholog pairs: hm={len(hm)} fh={len(fh)} fmm={len(fmm)}; mapping rows={len(mapping)}", flush=True)

    import anndata as ad
    import scanpy as sc
    import scipy.sparse as spmod
    from sklearn.neighbors import KNeighborsClassifier

    # ---- 1. 读数据 + 归一化（与 oPCA 同口径：全基因空间 normalize+log1p）----
    data = {}
    for sp in ("human", "mouse", "zebrafish"):
        a = ad.read_h5ad(str(SPECIES_FILES[sp]))
        if "cell_type" not in a.obs:
            die(f"{sp}: missing cell_type")
        sc.pp.normalize_total(a, target_sum=1e4)
        sc.pp.log1p(a)
        X = a.X
        if not spmod.issparse(X):
            X = spmod.csr_matrix(np.asarray(X))
        var_up = [str(v).upper() for v in a.var_names]
        # 首现去重（与 v3_fixkey 同口径）
        seen = set(); keep = []
        for i, g in enumerate(var_up):
            if g not in seen:
                seen.add(g); keep.append(i)
        if len(keep) != len(var_up):
            X = X[:, keep]
            var_up = [var_up[i] for i in keep]
        data[sp] = {
            "X": X,
            "var_idx": {g: i for i, g in enumerate(var_up)},
            "bc": np.array([f"{PREFIX[sp]}|{o}" for o in a.obs_names]),
            "ct": a.obs["cell_type"].astype(str).values,
        }
        print(f"{sp}: {X.shape[0]} cells x {len(var_up)} genes", flush=True)

    # ---- 2. 三物种投影到共同同源基因轴（按 human 基因为锚）----
    # 每个方向需要不同基因集；scVI 只能训练一次，故用"三物种共同可映射"的并集基因轴：
    # 取 human 基因作为轴，把 mouse/zebrafish 通过同源映射对齐到 human 基因名。
    anchor = sorted(set(data["human"]["var_idx"].keys()))
    # zebrafish -> human 反查
    f2h = {v: k for k, v in fh.items()}
    m2h = {v: k for k, v in hm.items()}
    axes = {}
    for sp in ("human", "mouse", "zebrafish"):
        if sp == "human":
            axes[sp] = [(g, g) for g in anchor if g in data["human"]["var_idx"]]
        elif sp == "mouse":
            axes[sp] = [(h, m) for h, m in hm.items() if h in data["human"]["var_idx"] and m in data["mouse"]["var_idx"]]
        else:
            axes[sp] = [(h, f) for f, h in fh.items() if h in data["human"]["var_idx"] and f in data["zebrafish"]["var_idx"]]
        print(f"{sp}: mappable to human axis = {len(axes[sp])}", flush=True)

    common = set(h for h, _ in axes["mouse"]) & set(h for h, _ in axes["zebrafish"]) & set(data["human"]["var_idx"])
    axis = sorted(common)
    print(f"common axis (3 species) = {len(axis)}", flush=True)
    if len(axis) < MIN_SHARED:
        die(f"common axis too small: {len(axis)} < {MIN_SHARED}", 4)

    mats = {}
    for sp in ("human", "mouse", "zebrafish"):
        if sp == "human":
            cols = [data["human"]["var_idx"][g] for g in axis]
            mats[sp] = data["human"]["X"][:, cols]
        else:
            pairs = dict(axes[sp])
            cols = [data[sp]["var_idx"][pairs[g]] for g in axis]
            mats[sp] = data[sp]["X"][:, cols]
        mats[sp] = mats[sp].toarray() if spmod.issparse(mats[sp]) else np.asarray(mats[sp])
        print(f"{sp} matrix: {mats[sp].shape}", flush=True)

    # ---- 3. 拼成联合矩阵，species 作 batch ----
    X_all = np.vstack([mats["human"], mats["mouse"], mats["zebrafish"]]).astype(np.float32)
    spv = np.array(["human"] * mats["human"].shape[0]
                   + ["mouse"] * mats["mouse"].shape[0]
                   + ["zebrafish"] * mats["zebrafish"].shape[0])
    ct_all = np.concatenate([data[s]["ct"] for s in ("human", "mouse", "zebrafish")])
    bc_all = np.concatenate([data[s]["bc"] for s in ("human", "mouse", "zebrafish")])
    print(f"joint matrix: {X_all.shape}", flush=True)

    # ---- 4. scVI 训练 ----
    import scvi
    adata = ad.AnnData(X=X_all)
    adata.obs["species"] = spv
    adata.var_names = axis
    scvi.model.SCVI.setup_anndata(adata, batch_key="species")
    model = scvi.model.SCVI(adata, n_latent=N_LATENT)
    model.train(max_epochs=MAX_EPOCHS, early_stopping=True, verbose=False)
    Z = model.get_latent_representation()
    print(f"latent: {Z.shape}", flush=True)
    np.save(out / "latent.npy", Z)

    # ---- 5. 六方向 × 三层评估（与 oPCA 完全相同的 KNN 口径）----
    MAPS = {
        ("human", "mouse"): hm, ("mouse", "human"): {v: k for k, v in hm.items()},
        ("human", "zebrafish"): fh, ("zebrafish", "human"): {v: k for k, v in fh.items()},
        ("mouse", "zebrafish"): fmm, ("zebrafish", "mouse"): {v: k for k, v in fmm.items()},
    }
    results = {}
    for (src, tgt), _smap in sorted(MAPS.items()):
        m_s, m_t = spv == src, spv == tgt
        dir_res = {}
        for level in LEVELS:
            labels, included, reason = layer_labels(spv, ct_all, mapping, level)
            ytr, yte = labels[m_s], labels[m_t]
            keep_r, ok = included[m_s], included[m_t]
            if keep_r.sum() == 0 or ok.sum() == 0:
                dir_res[level] = {"acc": 0.0, "macro_f1": 0.0, "majority": 0.0,
                                  "shuffle_p": 1.0, "n_ref": int(keep_r.sum()),
                                  "n_q": int(ok.sum()), "n_q_total": int(len(yte)),
                                  "coverage_q": 0.0, "confusion": {}, "n_perm": NPERM}
                continue
            knn = KNeighborsClassifier(n_neighbors=K, metric="cosine", weights="distance")
            knn.fit(Z[m_s][keep_r], ytr[keep_r])
            pred_all = knn.predict(Z[m_t])
            proba_all = knn.predict_proba(Z[m_t])
            cls = knn.classes_
            pred_ok, yte_ok = pred_all[ok], yte[ok]
            acc = float((pred_ok == yte_ok).mean())
            mf1 = macro_f1(list(yte_ok), list(pred_ok))
            vals, cnts = np.unique(yte_ok, return_counts=True)
            maj = float(cnts.max() / cnts.sum()) if cnts.sum() else 0.0
            rng = np.random.RandomState(SEED)
            nulls = []
            for _ in range(NPERM):
                pp = pred_ok.copy(); rng.shuffle(pp)
                nulls.append(float((pp == yte_ok).mean()))
            pval = float((np.array(nulls) >= acc).mean())
            conf = {}
            for t, p in zip(yte_ok, pred_ok):
                conf[f"{t}=>{p}"] = conf.get(f"{t}=>{p}", 0) + 1
            proba_cls = {c: j for j, c in enumerate(cls)}
            rows = []
            q_bc, q_reason = bc_all[m_t], reason[m_t]
            for j in range(len(q_bc)):
                inc = bool(ok[j])
                pr = str(pred_all[j])
                rows.append({
                    "prefixed_barcode": str(q_bc[j]), "direction": f"{src}->{tgt}",
                    "level": level, "truth": str(yte[j]), "prediction": pr,
                    "included": inc, "exclusion_reason": str(q_reason[j]),
                    "confidence": round(float(proba_all[j][proba_cls[pr]]), 4) if inc else 0.0,
                })
            (out / "predictions" / f"{level}_{src}_to_{tgt}.json").write_text(
                json.dumps(rows, ensure_ascii=False), encoding="utf-8")
            dir_res[level] = {
                "acc": round(acc, 4), "macro_f1": round(mf1, 4),
                "majority": round(maj, 4), "shuffle_p": round(pval, 4),
                "n_ref": int(keep_r.sum()), "n_q": int(ok.sum()),
                "n_q_total": int(len(yte)), "coverage_q": round(float(ok.mean()), 4),
                "confusion": conf, "n_perm": NPERM, "shared_genes": len(axis),
            }
        results[f"{src}->{tgt}"] = dir_res
        print(f"{src}->{tgt} done  macroF1(coarse)={dir_res['coarse']['macro_f1']}", flush=True)

    (out / "metrics.json").write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "environment.txt").write_text(json.dumps({
        "python": platform.python_version(), "platform": platform.platform(),
        "numpy": np.__version__, "anndata": ad.__version__, "scanpy": sc.__version__,
        "scvi": scvi.__version__,
        "params": {"n_latent": N_LATENT, "max_epochs": MAX_EPOCHS, "batch_key": "species",
                   "seed": SEED, "k": K, "nperm": NPERM, "common_axis": len(axis)},
    }, indent=1), encoding="utf-8")
    (out / "command.txt").write_text(" ".join([sys.executable] + sys.argv) + "\n", encoding="utf-8")

    outputs = {}
    for p in sorted(out.rglob("*")):
        if p.is_file() and p.name != "sha256.tsv":
            outputs[str(p.relative_to(out)).replace(os.sep, "/")] = sha256_file(p)
    manifest = {
        "protocol": PROTOCOL, "method": "scVI_cross_species",
        "variant": "joint training (3 species, batch_key=species) + 6-direction KNN eval",
        "params": {"n_latent": N_LATENT, "max_epochs": MAX_EPOCHS, "seed": SEED,
                   "k": K, "nperm": NPERM, "common_axis_genes": len(axis)},
        "script_sha256": sha256_file(__file__),
        "input_sha256": input_sha, "output_sha256": outputs,
        "started": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(t0)),
        "finished": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_sec": round(time.time() - t0, 1),
    }
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    with open(out / "sha256.tsv", "w", encoding="utf-8", newline="\n") as fh:
        for p in sorted(out.rglob("*")):
            if p.is_file() and p.name != "sha256.tsv":
                fh.write(f"{sha256_file(p)}  {str(p.relative_to(out)).replace(os.sep, '/')}\n")
    print(f"DONE elapsed={manifest['elapsed_sec']}s out={out}", flush=True)


if __name__ == "__main__":
    main()
