"""Bootstrap CI for the cross-phylum (lamprey <-> mouse) arms.

Source: results/phase-20261022/crossphylum/metrics.json
        .opca.confusion_matrices / .scvi.confusion_matrices  (13-class space)
Output: results/bootstrap-20261030/crossphylum.json
"""
import json
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "results" / "phase-20261022" / "crossphylum" / "metrics.json"
OUT = ROOT / "results" / "bootstrap-20261030"
NB = 1000
RNG = np.random.RandomState(20261030)
ARMS = {"opca": "oPCA", "scvi": "scVI"}
DIRS = ["Lamprey=>Mouse", "Mouse=>Lamprey"]
META = {"Lamprey=>Mouse": "Lamprey->Mouse", "Mouse=>Lamprey": "Mouse->Lamprey"}


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


def pairs_from_conf(conf):
    """Nested form: conf[true_label][pred_label] = count."""
    truth, pred = [], []
    for a, row in conf.items():
        for b, v in row.items():
            if v:
                truth.extend([a] * v)
                pred.extend([b] * v)
    return truth, pred


def main():
    d = json.loads(SRC.read_text(encoding="utf-8"))
    res = {"protocol": f"bootstrap over query cells, {NB} resamples, RandomState(20261030)",
           "source": "results/phase-20261022/crossphylum/metrics.json",
           "scene": "cross-phylum: Lamprey vs Mouse, 13-class intersection, 6222 shared genes",
           "methods": {}}
    for arm, name in ARMS.items():
        res["methods"][name] = {}
        for dr in DIRS:
            conf = d[arm]["confusion_matrices"][dr]
            truth, pred = pairs_from_conf(conf)
            n = len(truth)
            accs, mf1s = [], []
            for _ in range(NB):
                idx = RNG.randint(0, n, n)
                t = [truth[i] for i in idx]
                p = [pred[i] for i in idx]
                accs.append(float(np.mean([a == b for a, b in zip(t, p)])))
                mf1s.append(macro_f1_union(t, p))
            rec = {
                "n_q": n,
                "acc": round(float(np.mean([a == b for a, b in zip(truth, pred)])), 4),
                "mf1": round(macro_f1_union(truth, pred), 4),
                "acc_se": round(float(np.std(accs, ddof=1)), 4),
                "acc_ci95": [round(float(np.percentile(accs, 2.5)), 4),
                             round(float(np.percentile(accs, 97.5)), 4)],
                "mf1_se": round(float(np.std(mf1s, ddof=1)), 4),
                "mf1_ci95": [round(float(np.percentile(mf1s, 2.5)), 4),
                             round(float(np.percentile(mf1s, 97.5)), 4)],
                "majority": round(d[arm]["directions"][META[dr]]["majority"], 4),
            }
            res["methods"][name][META[dr]] = rec
            print(f"{name:6s} {META[dr]:16s} n={n:6d} acc={rec['acc']:.4f}±{rec['acc_se']:.4f} "
                  f"mf1={rec['mf1']:.4f}±{rec['mf1_se']:.4f} majority={rec['majority']:.4f}", flush=True)
    (OUT / "crossphylum.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    print("wrote", OUT / "crossphylum.json")


if __name__ == "__main__":
    main()
