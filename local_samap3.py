import os
os.environ['NUMBA_NUM_THREADS'] = '4'
import numpy as np, anndata as ad, pandas as pd, json, scipy.sparse as spmod
from sklearn.neighbors import KNeighborsClassifier
from samalg import SAM

BASE = 'D:/projects/course5-prep'
print('step1: build SAM objects', flush=True)
sams = {}
genes = {}
for sid, sp, fn in [('hu', 'human', 'local_human_s.h5ad'), ('ms', 'mouse', 'local_mouse_s.h5ad'), ('zf', 'zebrafish', 'local_zebrafish_s.h5ad')]:
    s = SAM()
    s.load_data(BASE + '/' + fn)
    s.preprocess_data(sum_norm="cell_median", norm="log", thresh_low=0.0, thresh_high=0.96, min_expression=1)
    s.run(preprocessing="StandardScaler", npcs=100, weight_PCs=False, k=20, n_genes=3000, weight_mode='rms')
    sams[sid] = s
    genes[sid] = [g for g in s.adata.var_names]
    print(sid, 'sam genes=', len(genes[sid]), flush=True)

print('step2: ortholog maps', flush=True)
groups = {}
for line in open(BASE + '/ortholog/MGI_HOM_MouseHumanSequence.rpt', encoding='utf-8', errors='replace'):
    f = line.rstrip('\n').split('\t')
    if len(f) < 5 or not f[0].isdigit(): continue
    tax = None; sym = None
    for i in range(len(f) - 1):
        if f[i] in ('9606', '10090'):
            tax = 'hu' if f[i] == '9606' else 'ms'
            sym = f[i + 1].strip()
            break
    if tax and sym: groups.setdefault(f[0], {}).setdefault(tax, set()).add(sym)
hm = {}
for g, d in groups.items():
    if set(d.keys()) == {'hu', 'ms'} and len(d['hu']) == 1 and len(d['ms']) == 1:
        hm[next(iter(d['hu']))] = next(iter(d['ms']))
def zfin(path):
    d = {}
    for line in open(path, encoding='utf-8', errors='replace'):
        f = line.rstrip('\n').split('\t')
        if len(f) < 5: continue
        d.setdefault(f[1].strip(), set()).add(f[3].strip())
    return d
fh_raw = zfin(BASE + '/ortholog/human_orthos.txt')
f2h = {f: next(iter(hs)) for f, hs in fh_raw.items() if len(hs) == 1}
h2f = {}
for f, h in f2h.items(): h2f.setdefault(h, []).append(f)
fh = {h: fl[0] for h, fl in h2f.items() if len(fl) == 1}
fm_raw = zfin(BASE + '/ortholog/mouse_orthos.txt')
f2m = {f: next(iter(ms)) for f, ms in fm_raw.items() if len(ms) == 1}
m2f = {}
for f, m in f2m.items(): m2f.setdefault(m, []).append(f)
fmm = {m: fl[0] for m, fl in m2f.items() if len(fl) == 1}
print('hm=%d fh=%d fmm=%d' % (len(hm), len(fh), len(fmm)), flush=True)

print('step3: gnnm', flush=True)
allg = ['hu_' + g for g in genes['hu']] + ['ms_' + g for g in genes['ms']] + ['zf_' + g for g in genes['zf']]
gidx = {g: i for i, g in enumerate(allg)}
rows = []; cols = []; nedges = 0
for src_map, pa, pb in [(hm, 'hu', 'ms'), (fh, 'hu', 'zf'), (fmm, 'ms', 'zf')]:
    for a, b in src_map.items():
        x = pa + '_' + a; y = pb + '_' + b
        if x in gidx and y in gidx:
            rows.append(gidx[x]); cols.append(gidx[y]); nedges += 1
n = len(allg)
adj = spmod.csr_matrix((np.ones(nedges * 2), (rows + cols, cols + rows)), shape=(n, n))
gnnm = (adj, np.array(allg), {'hu': np.array(['hu_' + g for g in genes['hu']]), 'ms': np.array(['ms_' + g for g in genes['ms']]), 'zf': np.array(['zf_' + g for g in genes['zf']])})
print('graph n=%d edges=%d' % (n, nedges), flush=True)

print('step4: SAMAP', flush=True)
from samap.mapping import SAMAP
sm = SAMAP(sams, keys={'hu': 'cell_type', 'ms': 'cell_type', 'zf': 'cell_type'}, gnnm=gnnm)
print('init ok', flush=True)
sm.run(NUMITERS=3, ncpus=4, umap=False)
print('run done', flush=True)
jsam = sm.samap
try:
    jsam.run()
except Exception as e:
    print('jsam.run err:', str(e)[:200], flush=True)
jd = jsam.adata
emb = np.asarray(jd.obsm['X_pca'])
raw_sp = jd.obs['species'].astype(str).values if 'species' in jd.obs.columns else np.array(['NA'] * jd.n_obs)
spv = np.array([{'hu': 'human', 'ms': 'mouse', 'zf': 'zebrafish'}.get(s, s) for s in raw_sp])
print('species_counts=' + json.dumps({k: int(v) for k, v in pd.Series(spv).value_counts().items()}), flush=True)
tmap = {}
for sid, fn in [('hu', 'local_human_s.h5ad'), ('ms', 'local_mouse_s.h5ad'), ('zf', 'local_zebrafish_s.h5ad')]:
    b = ad.read_h5ad(BASE + '/' + fn, backed='r')
    for o, c in zip(map(str, b.obs_names), b.obs['cell_type'].astype(str).values):
        tmap[sid + '|' + o] = c
    b.file.close()
tr = np.array([tmap.get(s + '|' + str(o), 'NA') for s, o in zip(raw_sp, jd.obs_names)])
print('truth NA=' + str(int((tr == 'NA').sum())), flush=True)
outad = ad.AnnData(obs=pd.DataFrame({'species': spv, 'cell_type': tr}, index=[s + '|' + str(o) for s, o in zip(raw_sp, jd.obs_names)]))
outad.obsm['X_samap_pca'] = emb
outad.write_h5ad(BASE + '/local_samap3_emb.h5ad')
print('SAVED', flush=True)
mp = pd.read_csv(BASE + '/config/heart-celltype-map-v1.tsv', sep='\t')
mmap = {}
for _, r in mp.iterrows():
    mmap[(str(r['source_species']), str(r['source_label']))] = (str(r['coarse_level']), str(r['fine_mapped_label']))
coarse = np.array([mmap.get((s, t), ('NA', 'NA'))[0] for s, t in zip(spv, tr)])
fine = np.array([mmap.get((s, t), ('NA', 'NA'))[1] for s, t in zip(spv, tr)])
fine_active = fine != 'unmapped'
res = {}
for space, labels in [('exact', tr), ('coarse', coarse), ('fine', fine)]:
    sec = {}
    for src in ['human', 'mouse', 'zebrafish']:
        for tgt in ['human', 'mouse', 'zebrafish']:
            if src == tgt: continue
            m_s = spv == src; m_t = spv == tgt
            ytr = labels[m_s]; yte = labels[m_t]
            keep = ytr != 'unmapped'; ok = yte != 'unmapped'
            knn = KNeighborsClassifier(n_neighbors=15, weights='distance')
            knn.fit(emb[m_s][keep], ytr[keep])
            pred = knn.predict(emb[m_t])
            acc = float((pred[ok] == yte[ok]).mean()) if ok.sum() else None
            vals, cnts = np.unique(yte[ok], return_counts=True)
            maj = float(cnts.max() / cnts.sum()) if cnts.sum() else None
            rng = np.random.RandomState(0); accs = []
            for _ in range(200):
                pp = pred[ok].copy(); rng.shuffle(pp); accs.append(float((pp == yte[ok]).mean()))
            pval = float((np.array(accs) >= acc).mean())
            sec[src + '>' + tgt] = {'acc': round(acc, 4), 'majority': round(maj, 4), 'shuffle_p': round(pval, 4), 'coverage_q': round(float(ok.mean()), 4), 'n_excluded_q': int((~ok).sum())}
            if space == 'coarse':
                import json as _json
                with open(BASE + '/local_samap3_pred_' + src + '_' + tgt + '.json', 'w') as pf:
                    _json.dump({'barcodes': [str(b) for b in np.array(jd.obs_names)[m_t][ok]], 'truth': yte[ok].tolist(), 'pred': pred[ok].tolist()}, pf)
    res[space] = sec
print('SAMAP3_EVAL ' + json.dumps(res, indent=1), flush=True)
