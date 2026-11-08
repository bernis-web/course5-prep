"""Ortholog-PCA v98: DCS container run, all paths hardcoded for platform."""
import hashlib, json, os, sys
from pathlib import Path
import numpy as np

ORTH_DIR = Path("/Files/wheelhouse")
OUTPUT_DIR = Path("/data/work/ortholog_pca_v98_results")
MAPPING_JSON = Path("/Files/wheelhouse/v99_mapping_embedded.json")
PROTOCOL = "transductive_formal_reassessment"
SEED = 0; K = 15; NPERM = 200; NPCS = 50

SPECIES_FILES = {
    "human": Path("/data/work/human_saturn_input_s.h5ad"),
    "mouse": Path("/data/work/mouse_saturn_input_s.h5ad"),
    "zebrafish": Path("/data/work/zebrafish_saturn_input_s.h5ad"),
}

def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()

def parse_orthologs():
    groups = {}
    for line in open(ORTH_DIR / "orth-MGI-HOM.rpt", encoding="utf-8", errors="replace"):
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
    fh_raw = zfin(ORTH_DIR / "orth-human-orthos.txt")
    f2h = {}; h2f = {}
    for fish, hs in fh_raw.items():
        if len(hs) == 1:
            hh = next(iter(hs)); h2f.setdefault(hh, []).append(fish); f2h[fish] = hh
    fh = {h: fl[0] for h, fl in h2f.items() if len(fl) == 1}
    fm_raw = zfin(ORTH_DIR / "orth-mouse-orthos.txt")
    f2m = {}; m2f = {}
    for fish, ms in fm_raw.items():
        if len(ms) == 1:
            mm = next(iter(ms)); m2f.setdefault(mm, []).append(fish); f2m[fish] = mm
    fmm = {m: fl[0] for m, fl in m2f.items() if len(fl) == 1}
    return hm, fh, fmm

def freeze_mapping(json_path):
    rows_raw = json.loads(Path(json_path).read_text(encoding="utf-8"))
    rows = {}
    for key, vals in rows_raw.items():
        rows[key] = (vals[0].strip(), vals[1].strip(), vals[2].strip())
    return rows

def main():
    import anndata as ad, scanpy as sc
    import scipy.sparse as spmod
    from sklearn.decomposition import PCA
    from sklearn.neighbors import KNeighborsClassifier

    header = {
        "protocol": PROTOCOL, "seed": SEED, "k": K, "npcs": NPCS, "nperm": NPERM,
        "script_sha256": sha256_file(__file__),
        "mapping_sha256": sha256_file(str(MAPPING_JSON)),
    }
    print("header=" + json.dumps(header), flush=True)

    hm, fh, fmm = parse_orthologs()
    mapping = freeze_mapping(MAPPING_JSON)
    print(f"ortholog pairs: hm={len(hm)} fh={len(fh)} fmm={len(fmm)}", flush=True)

    data = {}
    for sp in ["human", "mouse", "zebrafish"]:
        path = SPECIES_FILES[sp]
        a = ad.read_h5ad(str(path))
        sc.pp.normalize_total(a, target_sum=1e4)
        sc.pp.log1p(a)
        X = a.X
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
                              "coverage_q": round(float(ok.mean()),4), "confusion": conf}
        results[src+"->"+tgt] = dir_res
        print(f"{src}->{tgt} done", flush=True)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "metrics.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    (OUTPUT_DIR / "sha256.tsv").write_text(
        "\n".join(f"{sha256_file(OUTPUT_DIR / f)}  {f}" for f in os.listdir(OUTPUT_DIR) if (OUTPUT_DIR / f).is_file()),
        encoding="utf-8")
    print("DONE", flush=True)

if __name__ == "__main__":
    main()
