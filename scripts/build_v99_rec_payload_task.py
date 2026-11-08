"""Build AES-encrypted offline/save payloads for g5-v99-rec-rN payload tasks.

Usage: python build_v99_rec_payload_task.py <plan.json> <task_index>
  plan.json = {"groups": [["predictions/coarse_human->mouse.json", ...], ...]}
Prints the payload JSON path: .tmp-rN-payload.json (ASCII, ready for in-page fetch).
"""

import base64
import hashlib
import json
import os
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
TEMPLATE = (BASE / "scripts" / "g5_v99_rec_payload.py").read_text(encoding="utf-8")


def evp_bytestokey(pw: bytes, salt: bytes, kl=32, il=16):
    d = b""
    prev = b""
    while len(d) < kl + il:
        prev = hashlib.md5(prev + pw + salt).digest()
        d += prev
    return d[:kl], d[kl:kl + il]


def encrypt_openssl(content: str, pw: str) -> str:
    salt = os.urandom(8)
    key, iv = evp_bytestokey(pw.encode(), salt)
    raw = content.encode()
    pad = 16 - len(raw) % 16
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    c = Cipher(algorithms.AES(key), modes.CBC(iv)).encryptor()
    return base64.b64encode(b"Salted__" + salt + c.update(raw + bytes([pad]) * pad) + c.finalize()).decode()


def main():
    plan = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    idx = int(sys.argv[2])
    files = plan["groups"][idx]
    script = TEMPLATE.replace("    # __FILES_PLACEHOLDER__", "    " + json.dumps(files, indent=4).replace("\n", "\n    ") + ",")
    b64 = base64.b64encode(script.encode()).decode()
    shell = ("printf %s '" + b64 + "' | base64 -d > /data/work/g5_v99_rec_r" + str(2 + idx)
             + ".py && /usr/local/bin/python3 /data/work/g5_v99_rec_r" + str(2 + idx) + ".py")
    enc = encrypt_openssl(shell, "stereonote")
    payload = {
        "taskName": f"g5-v99-rec-r{2 + idx}",
        "taskType": "2",
        "shells": [enc],
        "fileParams": [],
        "seting": "0",
        "csFileNmme": "",
        "workspaceId": "user50719-8334_963bb09e53bb44678e2bb3818cf5992d",
        "resource_type": 2,
        "resource_id": "259",
        "projectId": "P20260920085640327",
        "projectName": "heart-course5",
        "imageId": "57362367597d49499e5bc388096a17f1",
        "imageUuid": "57362367597d49499e5bc388096a17f1",
        "imageName": "SATURN--22",
        "computingNameTemp": "1c 4g",
        "cpu": "1",
        "memory": "4",
    }
    out = BASE / f".tmp-r{2 + idx}-payload.json"
    blob = json.dumps(payload)
    assert blob.isascii(), "payload must be ASCII"
    out.write_text(blob, encoding="ascii")
    print(f"task g5-v99-rec-r{2 + idx}: files={len(files)} payload={out.name} ({len(blob)} chars)")
    for f in files:
        print("  -", f)


if __name__ == "__main__":
    main()
