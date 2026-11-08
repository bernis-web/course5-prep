"""Parse g5-v99-rec-r1 log into recovered-20261001/ and verify (local, read-only).

Usage: python parse_v99_rec_log_v1.py <r1_log.txt>

Verification performed:
  1. HASHVER lines vs sha256.tsv targets (fresh container hashes) -> tree unchanged
  2. SHATSVB64 -> byte-exact sha256.tsv reconstruction (SHA must equal c84dd378...)
  3. metrics.json text -> SHA vs d1081cfd...
  4. confusion files -> SHA vs recorded hashes; CONFDUP lines assert byte equality
  5. PREDMETA sha vs recorded hashes
  6. (payload tasks land later; this script only reports PREDPLAN)
"""

import base64
import hashlib
import json
import os
import sys
from pathlib import Path

RAW = Path(r"D:\projects\course5-prep\results\pilot-v1\saturn-v99\raw")
OUT = RAW / "recovered-20261001"

# Targets recorded in the container-side sha256.tsv (recovered via slim log).
T = {
    "manifest.json": "84267bd78bfe59ac60a22d1727a1f5398561e3e3d7bc53a50e43785fbeff8407",
    "sha256.tsv": "c84dd3780cb0db09f54ef4020a4e1e6ad91aef72433c949079634f6fcc35d687",
    "environment.txt": "2c9dcb5d0ae3a4f707af7d8bc995858f5270e8f02c959458990711a031457039",
    "command.txt": "0e5ee3dc6240be40d2f60f0bb7f93a6a739be2a626e5a6c042dc1700729359d6",
    "v99_mapping_embedded.json": "d92e32aa788672492febe8cd428beac71ba69fd99df68c7f362cba2e553eea4a",
    "metrics.json": "d1081cfd2489bf2afd30af7706fadf2d08b90390c26d38a766ea97b54b3dc261",
}


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def main():
    log_path = Path(sys.argv[1])
    data = log_path.read_bytes()
    lines = [ln[:-1] if ln.endswith(b"\r") else ln for ln in data.split(b"\n")]
    report = {"log_bytes": len(data), "log_lines": len(lines)}
    problems = []
    OUT.mkdir(parents=True, exist_ok=True)

    hashver = {}
    tsv_b64 = None
    metrics_txt = None
    conf_text = {}
    conf_dup = []
    predmeta = {}
    predplan = {}
    in_metrics = False
    in_conf = None
    in_meta = False

    for ln in lines:
        if ln.startswith(b"===METRICS==="):
            in_metrics = True
            continue
        if ln.startswith(b"===END_METRICS==="):
            in_metrics = False
            continue
        if ln.startswith(b"===CONF|"):
            in_conf = ln.decode().split("|", 1)[1].rsplit("===", 1)[0]
            conf_text[in_conf] = []
            continue
        if ln.startswith(b"===END_CONF==="):
            in_conf = None
            continue
        if ln.startswith(b"===PREDMETA==="):
            in_meta = True
            continue
        if ln.startswith(b"===END===") or ln.startswith(b"===HASHVER==="):
            in_meta = False
            continue
        if in_metrics:
            metrics_txt = (metrics_txt or b"") + ln + b"\n"
            continue
        if in_conf is not None:
            conf_text[in_conf].append(ln)
            continue
        if ln.startswith(b"HASHVER|"):
            _, rel, h, size = ln.decode().split("|")
            hashver[rel] = (h, int(size))
        elif ln.startswith(b"SHATSVB64|"):
            tsv_b64 = ln.decode().split("|", 1)[1]
        elif ln.startswith(b"CONFDUP|"):
            conf_dup.append(ln.decode())
        elif ln.startswith(b"PREDMETA|"):
            parts = ln.decode().split("|")
            predmeta[parts[1]] = (int(parts[2]), parts[3], int(parts[4]), int(parts[5]), float(parts[6]))
        elif ln.startswith(b"PREDPLAN|"):
            parts = ln.decode().split("|")
            predplan[parts[1]] = (int(parts[2]), parts[3])

    report["hashver_count"] = len(hashver)
    report["predmeta_count"] = len(predmeta)
    report["predplan_count"] = len(predplan)
    report["conf_full_count"] = len(conf_text)
    report["conf_dup_count"] = len(conf_dup)

    # 1. recorded tsv targets vs fresh container hashes
    tsv_map = {}
    if tsv_b64:
        tsv_bytes = base64.b64decode(tsv_b64)
        report["sha256_tsv_byte_exact"] = sha_bytes(tsv_bytes) == T["sha256.tsv"]
        (OUT / "sha256.tsv").write_bytes(tsv_bytes)
        for row in tsv_bytes.decode().splitlines():
            h, _, fn = row.partition("  ")
            tsv_map[fn.strip()] = h
    else:
        problems.append("SHATSVB64 missing")
    mism = []
    for fn, (h, size) in hashver.items():
        if fn in tsv_map and tsv_map[fn] != h:
            mism.append(fn)
    report["hashver_vs_tsv_mismatch"] = mism
    report["tree_unchanged_vs_tsv"] = not mism and bool(tsv_map)

    # 2. metrics.json
    if metrics_txt is not None:
        mt = metrics_txt.rstrip(b"\n")
        ok = sha_bytes(mt) == T["metrics.json"]
        ok_nl = sha_bytes(mt + b"\n") == T["metrics.json"]
        report["metrics_json_sha_match"] = bool(ok or ok_nl)
        (OUT / "metrics.json").write_bytes(mt + (b"\n" if ok_nl else b""))
        if not (ok or ok_nl):
            problems.append("metrics.json SHA mismatch")

    # 3. confusion files
    conf_ok = {}
    for name, chunks in conf_text.items():
        blob = b"\n".join(chunks)
        target = tsv_map.get(name)
        m1 = sha_bytes(blob) == target
        m2 = sha_bytes(blob + b"\n") == target
        conf_ok[name] = bool(m1 or m2)
        # v99 容器文件名含 "->"（Linux 合法，Windows 非法）：本地净化为 _to_，
        # 原名→本地名映射记录在报告中保证可追溯。
        local = name.replace(">", "_").replace("__", "_to_") if ">" in name else name
        if ">" in name:
            parts = name.rsplit(".", 1)[0].split("/", 1)
            local = parts[0] + "/" + parts[1].replace("->", "_to_") + "." + name.rsplit(".", 1)[1]
            report.setdefault("local_name_map", {})[name] = local
        dest = OUT / local
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(blob + (b"\n" if m2 and not m1 else b""))
    report["confusion_sha_ok"] = conf_ok
    report["confusion_all_ok"] = all(conf_ok.values()) and len(conf_ok) > 0

    # 4. CONFDUP lines must all be True
    bad_dups = [d for d in conf_dup if not d.endswith("|True")]
    report["confdup_all_true"] = not bad_dups and len(conf_dup) > 0
    if bad_dups:
        problems.append("CONFDUP mismatches: %s" % bad_dups)

    # 5. prediction meta identity
    pm_ok = all(predmeta[k][1] == tsv_map.get(k) for k in predmeta if k in tsv_map)
    report["predmeta_sha_ok"] = pm_ok

    report["predplan"] = {k: v[0] for k, v in sorted(predplan.items())}
    report["predplan_total_b64"] = sum(v[0] for v in predplan.values())
    report["problems"] = problems

    (OUT / "_r1-verification.json").write_text(
        json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "predplan"}, indent=1, ensure_ascii=False))
    print("PREDPLAN b64 sizes:", json.dumps(report["predplan"], indent=1))
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
