"""Build (but do NOT submit) the AES payload for the SAMap v98 DCS run.

Pre-submission preparation only — Phase 6 requires explicit user approval.
Run:  python build_samap_v98_dcs_payload.py
Out:  .tmp-samap-v98-payload.json + printed task spec summary.
"""

import base64
import hashlib
import json
import os
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
SCRIPT = BASE / "scripts" / "run_samap_compliant_v98_dcs.py"
MAPPING = BASE / "scripts" / "v99_mapping_embedded.json"


def evp_bytestokey(pw: bytes, salt: bytes, kl=32, il=16):
    d = b""
    prev = b""
    while len(d) < kl + il:
        prev = hashlib.md5(prev + pw + salt).digest()
        d += prev
    return d[:kl], d[kl:kl + il]


def encrypt_openssl(content: str, pw: str) -> str:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    salt = os.urandom(8)
    key, iv = evp_bytestokey(pw.encode(), salt)
    raw = content.encode()
    pad = 16 - len(raw) % 16
    c = Cipher(algorithms.AES(key), modes.CBC(iv)).encryptor()
    return base64.b64encode(b"Salted__" + salt + c.update(raw + bytes([pad]) * pad) + c.finalize()).decode()


def main():
    script_b64 = base64.b64encode(SCRIPT.read_bytes()).decode()
    mapping_sha = hashlib.sha256(MAPPING.read_bytes()).hexdigest()
    script_sha = hashlib.sha256(SCRIPT.read_bytes()).hexdigest()
    # 映射文件已在容器 /Files/wheelhouse/（早前上传，SHA d92e32aa…）：任务内校验后运行，不重复上传。
    shell = (
        "printf %s '" + script_b64 + "' | base64 -d > /data/work/run_samap_compliant_v98_dcs.py"
        + " && echo MAPPING_SHA_EXPECT=" + mapping_sha
        + " && sha256sum /Files/wheelhouse/v99_mapping_embedded.json"
        + " && echo SCRIPT_SHA=" + script_sha
        + " && /usr/local/bin/python3 /data/work/run_samap_compliant_v98_dcs.py"
    )
    enc = encrypt_openssl(shell, "stereonote")
    payload = {
        "taskName": "g5-samap-v98-compliant",
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
    blob = json.dumps(payload)
    assert blob.isascii()
    out = BASE / ".tmp-samap-v98-payload.json"
    out.write_text(blob, encoding="ascii")
    print("payload built (NOT submitted):", out.name, len(blob), "chars")
    print("taskName       :", payload["taskName"])
    print("script sha256  :", script_sha)
    print("mapping sha256 :", mapping_sha)
    print("resource       : 1c 4g (259), SATURN--22")
    print("inputs assumed present in container:")
    print("  /data/work/human_saturn_input_s.h5ad")
    print("  /data/work/mouse_saturn_input_s.h5ad")
    print("  /data/work/zebrafish_saturn_input_s.h5ad")
    print("  /Files/wheelhouse/orth-MGI-HOM.rpt / orth-human-orthos.txt / orth-mouse-orthos.txt")


if __name__ == "__main__":
    main()
