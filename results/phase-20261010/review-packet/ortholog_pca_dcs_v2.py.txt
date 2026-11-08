"""Ortholog-PCA local recompute with unified scorer and --smoke mode."""
import argparse, csv, hashlib, json, os, sys, time
from pathlib import Path
import numpy as np

# 路径解析（2026-10-11 依 GenPilot 平台实证修正）
#   /data/work 在**离线容器内不可用**（runsamap 当年正是靠 sed 's|/data/work|.|g' 才跑通）；
#   在线容器：/Files 只读可读、/work/{user} 可写。
#   因此三个输入一律走 /Files 真实落点（用户 2026-10-11 已上传并经 sha256 复核），
#   并允许用环境变量覆盖以便 WDL 把输入 cp 到工作目录后改指 ./…
OPCA_H5AD_DIR = Path(os.environ.get("OPCA_H5AD_DIR", "/Files"))
OPCA_ORTH_DIR = Path(os.environ.get("OPCA_ORTH_DIR", "/Files/wheelhouse"))
OPCA_MAPPING = Path(os.environ.get("OPCA_MAPPING",
                                   "/Files/wheelhouse/v99_mapping_embedded.json"))
# 输出必须写可写目录：/Files 只读（fuse ro），/work/{user} 可写
OPCA_OUT_ROOT = Path(os.environ.get(
    "OPCA_OUT_ROOT",
    "/work/%s" % (os.environ.get("USER") or os.environ.get("LOGNAME") or "user50719-8334")))
ORTH_DIR = OPCA_ORTH_DIR
MAPPING_TSV = OPCA_MAPPING
PROTOCOL = "transductive_formal_reassessment"
SEED = 0; K = 15; NPERM = 200; NPCS = 50
MIN_SHARED = 100
PREFIX = {"human": "hu", "mouse": "mo", "zebrafish": "zf"}
SPECIES_FILES = {s: OPCA_H5AD_DIR / f"local_{s}_s.h5ad" for s in ("human", "mouse", "zebrafish")}

def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()

def parse_orthologs():
    groups = {}
    for line in open(Path("/Files/wheelhouse/orth-MGI-HOM.rpt"), encoding="utf-8", errors="replace"):
        f = line.rstrip("\n").split("\t")
        if len(f) < 5 or not f[0].isdigit(): continue
        tax = None; sym = None
        for i in range(len(f) - 1):
            if f[i] in ("9606", "10090"):
                tax = "hu" if f[i] == "9606" else "ms"; sym = f[i+1].strip().upper(); break
        if tax and sym: groups.setdefault(f[0], {}).setdefault(tax, set()).add(sym)
    hm = {}
    for g, d in groups.items():
        if set(d) == {"hu", "ms"} and len(d["hu"]) == 1 and len(d["ms"]) == 1:
            hm[next(iter(d["hu"]))] = next(iter(d["ms"]))
    def zfin(path):
        d = {}
        for line in open(path, encoding="utf-8", errors="replace"):
            f = line.rstrip("\n").split("\t")
            if len(f) < 5: continue
            d.setdefault(f[1].strip().upper(), set()).add(f[3].strip().upper())
        return d
    fh_raw = zfin(Path("/Files/wheelhouse/orth-human-orthos.txt"))
    h2f = {}; f2h = {}
    for fish, hs in fh_raw.items():
        if len(hs) == 1:
            hh = next(iter(hs)); h2f.setdefault(hh, []).append(fish); f2h[fish] = hh
    fh = {h: fl[0] for h, fl in h2f.items() if len(fl) == 1}
    fm_raw = zfin(Path("/Files/wheelhouse/orth-mouse-orthos.txt"))
    m2f = {}; f2m = {}
    for fish, ms in fm_raw.items():
        if len(ms) == 1:
            mm = next(iter(ms)); m2f.setdefault(mm, []).append(fish); f2m[fish] = mm
    fmm = {m: fl[0] for m, fl in m2f.items() if len(fl) == 1}
    return hm, fh, fmm

def freeze_mapping(tsv):
    rows = {}
    for row in csv.DictReader(open(tsv, encoding="utf-8-sig", newline=""), delimiter="\t"):
        key = row["source_species"].strip() + "|" + row["source_label"].strip()
        rows[key] = (row["coarse_level"].strip(), row["fine_mapped_label"].strip(), row["mapping_status"].strip())
    return rows

def _preflight_inputs():
    """隔离层预检：在创建任何输出目录之前完成（缺失即停止，不留空目录）。"""
    missing = []
    for sp in ("human", "mouse", "zebrafish"):
        f = SPECIES_FILES[sp]
        if not f.is_file():
            missing.append(str(f))
    for f in (Path("/Files/wheelhouse/orth-MGI-HOM.rpt"),
              Path("/Files/wheelhouse/orth-human-orthos.txt"),
              Path("/Files/wheelhouse/orth-mouse-orthos.txt")):
        if not f.is_file():
            missing.append(str(f))
    if not MAPPING_TSV.is_file():
        missing.append(str(MAPPING_TSV))
    if missing:
        print("ERROR: missing required inputs:", missing, flush=True)
        raise SystemExit(2)
    files = [SPECIES_FILES[s] for s in ("human", "mouse", "zebrafish")] + [
             Path("/Files/wheelhouse/orth-MGI-HOM.rpt"),
             Path("/Files/wheelhouse/orth-human-orthos.txt"),
             Path("/Files/wheelhouse/orth-mouse-orthos.txt"),
             MAPPING_TSV]
    return {str(f): sha256_file(f) for f in files}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--out", default=None,
                    help="isolated output dir (default <OPCA_OUT_ROOT>/opca-full-<UTC stamp>)")
    args = ap.parse_args()
    tag = "smoke" if args.smoke else "full"

    # ---- isolation guard: preflight -> refuse existing dir -> then create ----
    input_sha = _preflight_inputs()
    if args.out:
        out = Path(args.out)
    else:
        stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        out = OPCA_OUT_ROOT / ("opca-full-%s" % stamp)
    if out.exists():
        print("ERROR: output dir already exists: %s (refusing to overwrite)" % out, flush=True)
        raise SystemExit(3)
    # 输出必须落在可写的隔离根下（默认 /work/{user}；/Files 只读，不可作为输出）
    if not str(out.resolve()).startswith(str(OPCA_OUT_ROOT.resolve())):
        print("ERROR: output must resolve under %s: %s" % (OPCA_OUT_ROOT, out), flush=True)
        raise SystemExit(3)

    hm, fh, fmm = parse_orthologs()
    mapping = freeze_mapping(MAPPING_TSV)
    out.mkdir(parents=True, exist_ok=False)
    (out / "command.txt").write_text(" ".join(sys.argv) + chr(10), encoding="utf-8")
    (out / "environment.txt").write_text(json.dumps({
        "task": "ortholog_pca_dcs_isolated_full",
        "protocol": PROTOCOL, "seed": SEED, "k": K, "nperm": NPERM, "npcs": NPCS,
        "script_sha256": sha256_file(__file__),
        "input_sha256": input_sha,
        "out_dir": str(out),
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"ortholog pairs: hm={len(hm)} fh={len(fh)} fmm={len(fmm)}", flush=True)

    import anndata as ad
    import scanpy as sc
    from sklearn.decomposition import PCA
    from sklearn.neighbors import KNeighborsClassifier

    data = {}
    for sp in ("human", "mouse", "zebrafish"):
        path = str(SPECIES_FILES[sp])
        a = ad.read_h5ad(path)
        sc.pp.normalize_total(a, target_sum=1e4)
        sc.pp.log1p(a)
        X = a.X
        from scipy import sparse as spmod
        X = X.toarray() if spmod.issparse(X) else np.asarray(X, dtype=np.float64)
        var_up = [str(v).upper() for v in a.var_names]
        bc = [f"{PREFIX[sp]}|{o}" for o in a.obs_names]
        ct = a.obs["cell_type"].astype(str).values
        data[sp] = {"X": X, "var_up": var_up, "var_set": set(var_up),
                     "var_idx": {g: i for i, g in enumerate(var_up)},
                     "bc": bc, "ct": ct}
        print(f"{sp}: {X.shape[0]} cells × {len(var_up)} genes", flush=True)

    MAPS = {("human","mouse"): hm, ("mouse","human"): {v:k for k,v in hm.items()},
            ("human","zebrafish"): fh, ("zebrafish","human"): {v:k for k,v in fh.items()},
            ("mouse","zebrafish"): fmm, ("zebrafish","mouse"): {v:k for k,v in fmm.items()}}

    results = {}
    for (src, tgt), smap in sorted(MAPS.items()):
        d_s = data[src]; d_t = data[tgt]
        shared = []; used_s = set(); used_t = set()
        for su, tu in smap.items():
            if su in d_s["var_set"] and tu in d_t["var_set"] and su not in used_s and tu not in used_t:
                shared.append((su, tu)); used_s.add(su); used_t.add(tu)
        print(f"{src}->{tgt}: shared_genes={len(shared)}", flush=True)
        if len(shared) < MIN_SHARED:
            print(f"SKIP: {src}->{tgt} only {len(shared)} shared genes", flush=True)
            continue
        idx_s = [d_s["var_idx"][g] for g, _ in shared]
        idx_t = [d_t["var_idx"][t] for _, t in shared]
        Xs = d_s["X"][:, idx_s]; Xt = d_t["X"][:, idx_t]
        spv = np.array([src] * Xs.shape[0] + [tgt] * Xt.shape[0])
        tr = np.array(list(d_s["ct"]) + list(d_t["ct"]))
        bc = np.array(list(d_s["bc"]) + list(d_t["bc"]))
        Z = PCA(n_components=NPCS, random_state=SEED).fit_transform(X)
        dir_res = {}
        for space in ("exact", "coarse", "fine"):
            if space == "exact": labels = tr
            elif space == "coarse": labels = np.array([mapping.get((s,t),("unmapped",))[0] for s,t in zip(spv,tr)])
            else: labels = np.array([mapping.get((s,t),("unmapped","unmapped"))[1] for s,t in zip(spv,tr)])
            m_s = spv==src; m_t = spv==tgt
            ytr = labels[m_s]; yte = labels[m_t]
            keep_r = ytr!="unmapped"; ok = yte!="unmapped"
            knn = KNeighborsClassifier(n_neighbors=K, weights="distance")
            knn.fit(Z[m_s][keep_r], ytr[keep_r])
            pred = knn.predict(Z[m_t]); pred_ok = pred[ok]
            acc = float((pred_ok == yte[ok]).mean()) if ok.sum() else 0.0
            vals, cnts = np.unique(yte[ok], return_counts=True)
            maj = float(cnts.max()/cnts.sum()) if cnts.sum() else 0.0
            rng = np.random.RandomState(SEED); nulls = []
            for _ in range(NPERM):
                pp = pred_ok.copy(); rng.shuffle(pp)
                nulls.append(float((pp == yte[ok]).mean()))
            pval = float((np.array(nulls) >= acc).mean()) if ok.sum() else 1.0
            conf = {}
            for t, p in zip(yte[ok], pred_ok):
                k3 = f"{t}=>{p}"; conf[k3] = conf.get(k3, 0) + 1
            dir_res[space] = {"acc": round(acc,4), "majority": round(maj,4), "shuffle_p": round(pval,4),
                              "n_ref": int(keep_r.sum()), "n_q": int(ok.sum()),
                              "coverage_q": round(float(ok.mean()),4) if m_t.sum() else 1.0,
                              "confusion": conf}
        results[src+"->"+tgt] = dir_res
        print(f"{src}->{tgt} done", flush=True)
    (out / "metrics.json").write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    print("DONE", flush=True)

if __name__ == "__main__":
    main()
