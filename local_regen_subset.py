import numpy as np, anndata as ad, json

RAW = {'human': 'D:/projects/course5-data/Homo_sapiens_sc.h5ad',
       'mouse': 'D:/projects/course5-data/Mus_musculus_sc.h5ad',
       'zebrafish': 'D:/projects/course5-data/Danio_rerio_sc.h5ad'}

def stratified(a, N, seed, floor):
    rng = np.random.RandomState(seed)
    keep = []
    obs = a.obs
    for ct, grp in obs.groupby('cell_type'):
        k = min(len(grp), max(floor, int(N * len(grp) / a.n_obs)))
        keep += list(rng.choice(grp.index.to_list(), k, replace=False))
    return keep

out = {}
for sp, raw in RAW.items():
    a = ad.read_h5ad(raw)
    a.obs['cell_type'] = a.obs['celltype'].astype(str)
    # stage 1: v60 (3000, floor 50)
    k1 = stratified(a, 3000, 0, 50)
    s1 = a[k1].copy()
    # stage 2: v70 (1500, floor 30)
    k2 = stratified(s1, 1500, 0, 30)
    s2 = s1[k2].copy()
    s2.write_h5ad('D:/projects/course5-prep/local_%s_s.h5ad' % sp)
    vc = s2.obs['cell_type'].value_counts()
    out[sp] = {'n': int(s2.n_obs), 'genes': int(s2.n_vars), 'counts': {kk: int(vv) for kk, vv in vc.items()}}
    print(sp, out[sp]['n'], 'cells', flush=True)
    del a, s1, s2
print('VERIFY_JSON ' + json.dumps(out, ensure_ascii=False))
