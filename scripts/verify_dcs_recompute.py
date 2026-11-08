"""核对 DCS 全量复算产物 vs 冻结 metrics（任务 W202610110124739）。

用法：
    python scripts/verify_dcs_recompute.py <回收目录>

<回收目录> 应为从平台拉回的 opca-full-<UTC>/ 目录（含 metrics.json / predictions/ / confusion/）。

核对项（与本地 A-smoke 同口径）：
  1) metrics.json 六方向 × exact/coarse/fine 的 acc / majority / shuffle_p / n_q / coverage_q
     与冻结 results/pilot-v1/ortholog-pca-v98/metrics.json 逐格比对（冻结值 round(x,4)）
  2) confusion/ 与 predictions/ 的 18 份文件与冻结件逐字节 SHA 对照
  3) 独立复算：confusion 对角和 == round(acc × n_q)；acc×n_q - 对角和 < 0.5
"""
import hashlib
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
FROZEN = BASE / "results" / "pilot-v1" / "ortholog-pca-v98"
DIRS = ["human->mouse", "mouse->human", "human->zebrafish",
        "mouse->zebrafish", "zebrafish->human", "zebrafish->mouse"]
LEVELS = ["exact", "coarse", "fine"]
FIELDS = ["acc", "majority", "shuffle_p", "n_q", "coverage_q"]
ROUND_DP = 4
TOL = 1e-12


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def diag(conf):
    return sum(n for k, n in conf.items() if k.split("=>")[0] == k.split("=>")[1])


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    got_dir = Path(sys.argv[1])
    if not (got_dir / "metrics.json").is_file():
        print("ERROR: %s/metrics.json not found" % got_dir)
        return 2

    new = json.loads((got_dir / "metrics.json").read_text(encoding="utf-8"))
    fro = json.loads((FROZEN / "metrics.json").read_text(encoding="utf-8"))

    checks = []

    def add(name, ok, detail=""):
        checks.append({"check": name, "ok": bool(ok), "detail": detail})

    for d in DIRS:
        for lv in LEVELS:
            try:
                n = new[d][lv]
                f = fro[d][lv]
            except KeyError as e:
                add("present:%s/%s" % (d, lv), False, repr(e))
                continue
            for fld in FIELDS:
                nv, fv = n.get(fld), f.get(fld)
                if isinstance(fv, float):
                    nvr = round(float(nv), ROUND_DP)
                    add("field:%s/%s/%s" % (d, lv, fld), abs(nvr - fv) <= TOL,
                        "new=%s frozen=%s" % (nvr, fv))
                else:
                    add("field:%s/%s/%s" % (d, lv, fld), nv == fv,
                        "new=%s frozen=%s" % (nv, fv))
            # 独立复算
            dg = diag(n["confusion"])
            nq = n["n_q"]
            add("independent:%s/%s/diag_eq_round_acc_x_nq" % (d, lv),
                abs(round(dg / nq, ROUND_DP) - round(float(n["acc"]), ROUND_DP)) <= TOL,
                "diag=%d n_q=%d acc=%s" % (dg, nq, n["acc"]))
            add("independent:%s/%s/diag_matches_frozen" % (d, lv),
                dg == diag(f["confusion"]),
                "new_diag=%d frozen_diag=%d" % (dg, diag(f["confusion"])))

    # 逐字节对照 18 份 confusion + 18 份 predictions
    byte_same = 0
    byte_diff = []
    for sub in ("confusion", "predictions"):
        gd = got_dir / sub
        fd = FROZEN / sub
        if not gd.is_dir():
            add("dir:%s" % sub, False, "missing %s" % gd)
            continue
        for p in sorted(gd.glob("*.json")):
            fp = fd / p.name
            if not fp.is_file():
                byte_diff.append((str(p.name), "frozen missing"))
                continue
            if sha256_file(p) == sha256_file(fp):
                byte_same += 1
            else:
                byte_diff.append((str(p.name), "sha mismatch"))
    add("byte_identical_files", byte_same == 36 and not byte_diff,
        "same=%d/36 diff=%s" % (byte_same, byte_diff[:5] or "none"))

    npass = sum(1 for c in checks if c["ok"])
    for c in checks:
        if not c["ok"]:
            print("FAIL %s %s" % (c["check"], c["detail"]))
    print("VERIFY|%d/%d|byte_identical=%d/36|dir=%s" % (npass, len(checks), byte_same, got_dir))
    out = got_dir / "verification_dcs.json"
    out.write_text(json.dumps({
        "source_dir": str(got_dir),
        "frozen_metrics_sha256": sha256_file(FROZEN / "metrics.json"),
        "checks": checks,
        "passed": npass,
        "total": len(checks),
        "byte_identical_files": byte_same,
        "failed_checks": [c["check"] for c in checks if not c["ok"]],
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print("wrote", out)
    return 0 if npass == len(checks) else 4


if __name__ == "__main__":
    sys.exit(main())
