"""g5-v99-rec-rN: print reduced prediction payloads for assigned files (in-container).

For each prediction file name given via the FILES constant (module-level list
injected into the uploaded copy), prints:

  PREDPAYLOAD|<name>|<gzip_sha256>|<b64>
  PREDEND

where b64 = base64(gzip9(json compact rows)) exactly as PREDPLAN described in
the R1 readout.  Read-only.  Total stdout per task must stay < 85K chars; the
caller groups files accordingly from R1's PREDPLAN sizes.
"""

import base64
import gzip
import hashlib
import io
import json
import os
import sys

ROOT = "/data/work/course5_v99"
FILES = [
    # __FILES_PLACEHOLDER__
]


def main():
    W = sys.stdout.write
    for name in FILES:
        p = os.path.join(ROOT, name)
        raw = open(p, "rb").read()
        rows = json.loads(raw.decode("utf-8"))
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
        W("PREDPAYLOAD|%s|%s|%s\n" % (name, hashlib.sha256(gz).hexdigest(), b64))
        W("PREDEND|%s\n" % name)
    W("===END===\n")


if __name__ == "__main__":
    main()
