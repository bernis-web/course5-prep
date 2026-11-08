"""Bootstrap CI + per-class recall for all four methods, in the AUTHORITATIVE
coarse (union) label space.

Every method's per-cell truth/prediction is pushed through
config/heart-celltype-map-v1.tsv exactly like scripts/unified_coarse_macro_f1.py:
  species + source_label -> coarse_level, only mapping_status == active is kept.

Before bootstrapping, point estimates are compared to
results/phase-20261017/unified-coarse-macro-f1/unified-coarse-macro-f1.json and
the run ABORTS on any mismatch -- so a CI can only be attached to numbers that
already match the frozen table.

Output: results/bootstrap-20261030/bootstrap.json
"""
import csv
import gzip
import json
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "bootstrap-20261030"
MAP_TSV = ROOT / "config" / "heart-celltype-map-v1.tsv"
SCVI_FROZEN = ROOT / "results" / "phase-20261019" / "scvi-cross-species" / "recomputed_union.json"
OPCA_FIXKEY = ROOT / "results" / "phase-20261010" / "opca-fixkey-recovered-20261015" / "metrics.json"
UNIFIED = ROOT / "results" / "phase-20261017" / "unified-coarse-macro-f1" / "unified-coarse-macro-f1.json"


def expect(method, dr):
    """Authoritative macro-F1 / n for each (method, direction), from the frozen files.

    oPCA  -> FIXKEY run (v3_fixkey, corrected zebrafish mapping orientation)
    scVI  -> recomputed_union.json (union recount on the platform predictions)
    SATURN, SAMap -> unified-coarse-macro-f1.json (remapped into coarse union space)
    """
    if method == "ortholog_pca":
        d = json.loads(OPCA_FIXKEY.read_text(encoding="utf-8"))[dr]["coarse"]
        return round(macro_f1_union(
            [k.split("=>")[0] for k, v in d["confusion"].items() for _ in range(v)],
            [k.split("=>")[1] for k, v in d["confusion"].items() for _ in range(v)]), 4), d["n_q"]
    if method == "scVI":
        d = json.loads(SCVI_FROZEN.read_text(encoding="utf-8"))[dr + "|coarse"]
        return d["macro_f1_union"], d["n"]
    d = json.loads(UNIFIED.read_text(encoding="utf-8"))[dr][method]
    return d["macro_f1"], d["n"]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    mapping = load_mapping()
    res = {"protocol": f"bootstrap over query cells, {NB} resamples, RandomState(20261030)",
           "label_space": "coarse / union (active rows only, per unified_coarse_macro_f1.py)",
           "note": "CI = sampling dispersion of the query set; not seed/parameter dispersion (see results/stability-20261030)",
           "frozen_sources": {
               "ortholog_pca": str(OPCA_FIXKEY.relative_to(ROOT)).replace("\\", "/"),
               "scVI": str(SCVI_FROZEN.relative_to(ROOT)).replace("\\", "/"),
               "saturn_v99": str(UNIFIED.relative_to(ROOT)).replace("\\", "/"),
               "samap": str(UNIFIED.relative_to(ROOT)).replace("\\", "/")},
           "methods": {}}
    mismatch = []
    for m, fn in LOADERS.items():
        res["methods"][m] = {}
        for dr in DIRS:
            try:
                pairs = fn(dr, mapping)
            except Exception as e:
                res["methods"][m][dr] = {"error": str(e)}
                print(f"{m:13s} {dr:18s} ERROR {e}", flush=True)
                continue
            if pairs is None:
                res["methods"][m][dr] = {"status": "file_missing"}
                continue
            if len(pairs) < 30:
                res["methods"][m][dr] = {"status": "insufficient_cells", "n_q": len(pairs)}
                continue
            truth = [p[0] for p in pairs]
            pred = [p[1] for p in pairs]
            r = boot(truth, pred)
            fz_mf1, fz_n = expect(m, dr)
            r["frozen_mf1"] = fz_mf1
            r["frozen_n"] = fz_n
            r["matches_frozen"] = (abs(r["mf1"] - fz_mf1) < 5e-4 and r["n_q"] == fz_n)
            if not r["matches_frozen"]:
                mismatch.append((m, dr, r["mf1"], fz_mf1, r["n_q"], fz_n))
            tc, ok = Counter(), Counter()
            for a, b in pairs:
                tc[a] += 1
                if a == b:
                    ok[a] += 1
            r["per_class"] = {c: {"recall": round(ok[c] / n, 4), "n": n, "correct": ok[c]}
                              for c, n in tc.most_common()}
            res["methods"][m][dr] = r
            print(f"{m:13s} {dr:18s} n={r['n_q']:5d} acc={r['acc']:.4f}±{r['acc_se']:.4f} "
                  f"mf1={r['mf1']:.4f} frozen={fz_mf1:.4f} {'OK' if r['matches_frozen'] else 'MISMATCH'}",
                  flush=True)
    res["opca_v98_vs_fixkey"] = opca_v98_vs_fixkey()
    res["mismatches"] = mismatch
    (OUT / "bootstrap.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"\nwrote {OUT/'bootstrap.json'}  mismatches={len(mismatch)}", flush=True)
    for x in mismatch:
        print("  MISMATCH", x, flush=True)
NB = 1000
RNG = np.random.RandomState(20261030)

DIRS = ["human->mouse", "mouse->human", "human->zebrafish",
        "zebrafish->human", "mouse->zebrafish", "zebrafish->mouse"]
SRC = {"human->mouse": ("human", "mouse"), "mouse->human": ("mouse", "human"),
       "human->zebrafish": ("human", "zebrafish"), "zebrafish->human": ("zebrafish", "human"),
       "mouse->zebrafish": ("mouse", "zebrafish"), "zebrafish->mouse": ("zebrafish", "mouse")}
SCVI_TAG = {"human->mouse": "coarse_hu_to_mo", "mouse->human": "coarse_mo_to_hu",
            "human->zebrafish": "coarse_hu_to_zf", "zebrafish->human": "coarse_zf_to_hu",
            "mouse->zebrafish": "coarse_mo_to_zf", "zebrafish->mouse": "coarse_zf_to_mo"}
SATURN_TAG = {"human->mouse": "p6_coarse_human_to_mouse", "mouse->human": "p1_coarse_mouse_to_human",
              "human->zebrafish": "p3_coarse_human_to_zebrafish",
              "zebrafish->human": "p2_coarse_zebrafish_to_human",
              "mouse->zebrafish": "p5_coarse_mouse_to_zebrafish",
              "zebrafish->mouse": "p4_coarse_zebrafish_to_mouse"}
SAMAP_TAG = {"human->mouse": "hu--mo", "mouse->human": "mo--hu",
             "human->zebrafish": "hu--zf", "zebrafish->human": "zf--hu",
             "mouse->zebrafish": "mo--zf", "zebrafish->mouse": "zf--mo"}


def load_mapping():
    m = {}
    for row in csv.DictReader(open(MAP_TSV, encoding="utf-8-sig", newline=""), delimiter="\t"):
        m[(row["source_species"].strip(), row["source_label"].strip())] = (
            row["coarse_level"].strip(), row["mapping_status"].strip())
    return m


def to_coarse(sp, label, mapping):
    hit = mapping.get((sp, str(label).strip()))
    if not hit:
        return None
    coarse, status = hit
    if status != "active" or not coarse:
        return None
    return coarse


def pairs_opca(dr, mapping):
    """FIXKEY variant (v3_fixkey) -- the only oPCA run with per-cell predictions on disk.

    NOTE: the handoff table's four fish directions still carry the older v98
    (known-inverted-mapping) values; FIXKEY supersedes them.  The delta is
    reported in this file under `opca_v98_vs_fixkey`.
    """
    f = ROOT / "results" / "stability-20261030" / "runs" / "seed-0" / "predictions" / (f"coarse_{dr.replace('->', '_to_')}.json")
    rows = json.loads(f.read_text(encoding="utf-8"))
    return [(r["truth"], r["prediction"]) for r in rows if r["included"]]


def opca_v98_vs_fixkey():
    """Documented divergence: pilot-v1/v98 (buggy) vs v3_fixkey (corrected)."""
    v98 = json.loads((ROOT / "results" / "pilot-v1" / "ortholog-pca-v98" / "metrics.json").read_text(encoding="utf-8"))
    fk = json.loads((ROOT / "results" / "phase-20261010" / "opca-fixkey-recovered-20261015" / "metrics.json").read_text(encoding="utf-8"))
    out = {}
    for dr in DIRS:
        a, b = v98[dr]["coarse"], fk[dr]["coarse"]
        out[dr] = {
            "v98_acc": a["acc"], "v98_mf1": round(macro_f1_union(
                [k.split("=>")[0] for k, v in a["confusion"].items() for _ in range(v)],
                [k.split("=>")[1] for k, v in a["confusion"].items() for _ in range(v)]), 4),
            "fixkey_acc": b["acc"], "fixkey_mf1": round(macro_f1_union(
                [k.split("=>")[0] for k, v in b["confusion"].items() for _ in range(v)],
                [k.split("=>")[1] for k, v in b["confusion"].items() for _ in range(v)]), 4),
        }
    return out


def pairs_scvi(dr, mapping):
    f = ROOT / "results" / "phase-20261019" / "scvi-cross-species" / "predictions" / (SCVI_TAG[dr] + ".json")
    rows = json.loads(f.read_text(encoding="utf-8"))
    out = []
    for r in rows:
        if not r.get("included", True):
            continue
        t, p = r["truth"], r["prediction"]
        if t in ("unmapped", "", None) or p in ("unmapped", "", None):
            continue
        out.append((t, p))
    return out


def pairs_saturn(dr, mapping):
    """Same path as scripts/unified_coarse_macro_f1.py: confusion(remapped).

    The recovered per-cell payloads under .../payloads only carry the cells the
    platform exported as `included == 1` (796 rows for mouse->human), whereas the
    frozen table was built from the raw-label confusion matrix (857 cells).
    To keep the bootstrap attached to the published n, we rebuild from confusion.
    """
    src, tgt = SRC[dr]
    cp = ROOT / "results" / "pilot-v1" / "saturn-v99" / "raw" / "recovered-20261001" / "confusion" / (f"coarse_{src}_to_{tgt}.json")
    conf = json.loads(cp.read_text(encoding="utf-8"))
    out = []
    for k, v in conf.items():
        t_raw, p_raw = k.split("=>")
        t = to_coarse(src, t_raw, mapping)
        p = to_coarse(tgt, p_raw, mapping)
        if t and p:
            out.extend([(t, p)] * v)
    return out


def pairs_samap(dr, mapping):
    f = ROOT / "results" / "pilot-v1" / "samap-v98" / "wdl-run" / "extracted" / (f"coarse_{SAMAP_TAG[dr]}.json")
    if not f.exists():
        return None
    d = json.loads(f.read_text(encoding="utf-8"))
    cells = d.get("per_cell") or []
    src, tgt = SRC[dr]
    out = []
    for r in cells:
        t = to_coarse(src, r.get("truth"), mapping)
        p = to_coarse(tgt, r.get("prediction"), mapping)
        if t and p:
            out.append((t, p))
    return out


LOADERS = {"ortholog_pca": pairs_opca, "scVI": pairs_scvi,
           "saturn_v99": pairs_saturn, "samap": pairs_samap}


def macro_f1_union(truth, pred):
    t, p, tp = Counter(), Counter(), Counter()
    for a, b in zip(truth, pred):
        t[a] += 1
        p[b] += 1
        if a == b:
            tp[a] += 1
    fs = []
    for c in set(t) | set(p):
        pr = tp[c] / p[c] if p[c] else 0.0
        rc = tp[c] / t[c] if t[c] else 0.0
        fs.append(2 * pr * rc / (pr + rc) if (pr + rc) else 0.0)
    return sum(fs) / len(fs) if fs else 0.0


def boot(truth, pred):
    n = len(truth)
    accs, mf1s = [], []
    for _ in range(NB):
        idx = RNG.randint(0, n, n)
        tt = [truth[i] for i in idx]
        pp = [pred[i] for i in idx]
        accs.append(float(np.mean([a == b for a, b in zip(tt, pp)])))
        mf1s.append(macro_f1_union(tt, pp))
    return {
        "n_q": n,
        "acc": round(float(np.mean([a == b for a, b in zip(truth, pred)])), 4),
        "mf1": round(macro_f1_union(truth, pred), 4),
        "acc_se": round(float(np.std(accs, ddof=1)), 4),
        "acc_ci95": [round(float(np.percentile(accs, 2.5)), 4), round(float(np.percentile(accs, 97.5)), 4)],
        "mf1_se": round(float(np.std(mf1s, ddof=1)), 4),
        "mf1_ci95": [round(float(np.percentile(mf1s, 2.5)), 4), round(float(np.percentile(mf1s, 97.5)), 4)],
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    mapping = load_mapping()
    res = {"protocol": f"bootstrap over query cells, {NB} resamples, RandomState(20261030)",
           "label_space": "coarse / union (active rows only, per unified_coarse_macro_f1.py)",
           "note": "CI = sampling dispersion of the query set; not seed/parameter dispersion (see results/stability-20261030)",
           "frozen_sources": {
               "ortholog_pca": str(OPCA_FIXKEY.relative_to(ROOT)).replace("\\", "/"),
               "scVI": str(SCVI_FROZEN.relative_to(ROOT)).replace("\\", "/"),
               "saturn_v99": str(UNIFIED.relative_to(ROOT)).replace("\\", "/"),
               "samap": str(UNIFIED.relative_to(ROOT)).replace("\\", "/")},
           "methods": {}}
    mismatch = []
    for m, fn in LOADERS.items():
        res["methods"][m] = {}
        for dr in DIRS:
            try:
                pairs = fn(dr, mapping)
            except Exception as e:
                res["methods"][m][dr] = {"error": str(e)}
                print(f"{m:13s} {dr:18s} ERROR {e}", flush=True)
                continue
            if pairs is None:
                res["methods"][m][dr] = {"status": "file_missing"}
                continue
            if len(pairs) < 30:
                res["methods"][m][dr] = {"status": "insufficient_cells", "n_q": len(pairs)}
                continue
            truth = [p[0] for p in pairs]
            pred = [p[1] for p in pairs]
            r = boot(truth, pred)
            fz_mf1, fz_n = expect(m, dr)
            r["frozen_mf1"] = fz_mf1
            r["frozen_n"] = fz_n
            r["matches_frozen"] = (abs(r["mf1"] - fz_mf1) < 5e-4 and r["n_q"] == fz_n)
            if not r["matches_frozen"]:
                mismatch.append((m, dr, r["mf1"], fz_mf1, r["n_q"], fz_n))
            tc, ok = Counter(), Counter()
            for a, b in pairs:
                tc[a] += 1
                if a == b:
                    ok[a] += 1
            r["per_class"] = {c: {"recall": round(ok[c] / tc[c], 4), "n": tc[c], "correct": ok[c]}
                              for c in tc}
            res["methods"][m][dr] = r
            print(f"{m:13s} {dr:18s} n={r['n_q']:5d} acc={r['acc']:.4f}±{r['acc_se']:.4f} "
                  f"mf1={r['mf1']:.4f} frozen={fz_mf1:.4f} {'OK' if r['matches_frozen'] else 'MISMATCH'}",
                  flush=True)
    res["opca_v98_vs_fixkey"] = opca_v98_vs_fixkey()
    res["mismatches"] = mismatch
    (OUT / "bootstrap.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"\nwrote {OUT/'bootstrap.json'}  mismatches={len(mismatch)}", flush=True)
    if mismatch:
        for x in mismatch:
            print("  MISMATCH", x, flush=True)
        raise SystemExit(2)


if __name__ == "__main__":
    main()
