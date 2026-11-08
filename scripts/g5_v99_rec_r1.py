"""g5-v99-rec-r1: read-only recovery readout for /data/work/course5_v99 (in-container).

Prints, within one log window (<100K chars):
  HASHVER   fresh SHA-256 + size of every file under course5_v99/
  SHATSVB64 base64 of sha256.tsv (byte-exact recovery of the index itself)
  METRICS   metrics.json in full
  CONF      each byte-distinct confusion file in full (+ CONFDUP identity lines)
  PREDMETA  per prediction file: bytes, fresh sha256, rows, included, accuracy
  PREDPLAN  per prediction file: reduced-payload b64 length + gzip sha256
            (reduced payload = per-cell barcode/truth/prediction/included/
             confidence/exclusion_reason, neighbor lists dropped)

Writes nothing. Reads only /data/work/course5_v99/.
"""

import base64
import gzip
import hashlib
import io
import json
import os
import sys

ROOT = "/data/work/course5_v99"
W = sys.stdout.write


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


files = []
for dirpath, _, filenames in os.walk(ROOT):
    for fn in filenames:
        files.append(os.path.join(dirpath, fn))
files.sort()

W("===HASHVER===\n")
for p in files:
    rel = os.path.relpath(p, ROOT).replace(os.sep, "/")
    W("HASHVER|%s|%s|%d\n" % (rel, sha(p), os.path.getsize(p)))

W("SHATSVB64|%s\n" % base64.b64encode(open(os.path.join(ROOT, "sha256.tsv"), "rb").read()).decode())

W("===METRICS===\n")
W(open(os.path.join(ROOT, "metrics.json"), "rb").read().decode("utf-8", "replace"))
W("\n===END_METRICS===\n")

h2p = {}
dups = []
for p in files:
    rel = os.path.relpath(p, ROOT).replace(os.sep, "/")
    if not rel.startswith("confusion/"):
        continue
    h = sha(p)
    if h in h2p:
        same = open(p, "rb").read() == open(h2p[h], "rb").read()
        dups.append("CONFDUP|%s|=%s|%s\n" % (rel, os.path.relpath(h2p[h], ROOT).replace(os.sep, "/"), same))
    else:
        h2p[h] = p
        W("===CONF|%s===\n" % rel)
        W(open(p, "rb").read().decode("utf-8", "replace"))
        W("\n===END_CONF===\n")
for d in dups:
    W(d)

W("===PREDMETA===\n")
for p in files:
    rel = os.path.relpath(p, ROOT).replace(os.sep, "/")
    if not rel.startswith("predictions/"):
        continue
    raw = open(p, "rb").read()
    rows = json.loads(raw.decode("utf-8"))
    inc = [r for r in rows if r.get("included")]
    correct = sum(1 for r in inc if r.get("prediction") == r.get("truth"))
    acc = (float(correct) / len(inc)) if inc else 0.0
    compact = [
        [
            r.get("prefixed_barcode"),
            r.get("truth"),
            r.get("prediction"),
            1 if r.get("included") else 0,
            r.get("confidence"),
            r.get("exclusion_reason", ""),
        ]
        for r in rows
    ]
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", compresslevel=9, mtime=0) as g:
        g.write(json.dumps(compact, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))
    gz = buf.getvalue()
    b64 = base64.b64encode(gz).decode()
    W("PREDMETA|%s|%d|%s|%d|%d|%.6f\n" % (rel, len(raw), sha(p), len(rows), len(inc), acc))
    W("PREDPLAN|%s|%d|%s\n" % (rel, len(b64), hashlib.sha256(gz).hexdigest()))

W("===END===\n")
