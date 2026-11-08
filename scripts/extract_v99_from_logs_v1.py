"""Extract v99 core provenance files from recovered DCS logs (local, read-only).

Reconstructs candidate byte streams from the slim readout log and verifies
SHA-256 against the container-side sha256.tsv values.  Writes verified files
into results/pilot-v1/saturn-v99/raw/recovered-20261001/.

No network, no DCS calls, no overwrites outside the new directory.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

RAW = Path(r"D:\projects\course5-prep\results\pilot-v1\saturn-v99\raw")
OUT = RAW / "recovered-20261001"

# Targets from container sha256.tsv (recovered in slim log).
TARGETS = {
    "manifest.json": "84267bd78bfe59ac60a22d1727a1f5398561e3e3d7bc53a50e43785fbeff8407",
    "sha256.tsv": "c84dd3780cb0db09f54ef4020a4e1e6ad91aef72433c949079634f6fcc35d687",
    "environment.txt": "2c9dcb5d0ae3a4f707af7d8bc995858f5270e8f02c959458990711a031457039",
    "command.txt": "0e5ee3dc6240be40d2f60f0bb7f93a6a739be2a626e5a6c042dc1700729359d6",
    "v99_mapping_embedded.json": "d92e32aa788672492febe8cd428beac71ba69fd99df68c7f362cba2e553eea4a",
    "metrics.json": "d1081cfd2489bf2afd30af7706fadf2d08b90390c26d38a766ea97b54b3dc261",
}


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def read_lines(path: Path) -> list[bytes]:
    data = path.read_bytes()
    lines = data.split(b"\n")
    if lines and lines[-1] == b"":
        lines.pop()
    return [ln[:-1] if ln.endswith(b"\r") else ln for ln in lines]


def variants(body_lines: list[bytes], *, ends_no_newline: bool | None = None) -> list[tuple[str, bytes]]:
    """Candidate byte streams: lines joined with \n, trailing newline optional."""
    out: list[tuple[str, bytes]] = []
    core = b"\n".join(body_lines)
    if ends_no_newline is not False:
        out.append(("no_trailing_newline", core))
    if ends_no_newline is not True:
        out.append(("trailing_newline", core + b"\n"))
    return out


def try_verify(name: str, cands: list[tuple[str, bytes]], report: dict) -> bytes | None:
    target = TARGETS[name]
    for label, blob in cands:
        if sha(blob) == target:
            report[name] = {"status": "byte_exact", "variant": label, "sha256": target}
            return blob
    report[name] = {
        "status": "content_only_sha_mismatch",
        "variants_tried": [lbl for lbl, _ in cands],
        "target_sha256": target,
        "best_local_sha256": sha(cands[0][1]) if cands else None,
    }
    return None


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    slim_lines = read_lines(RAW / "v99_slim_export_full.txt")
    report: dict = {}

    def find_marker(marker: bytes, start: int = 0) -> int:
        for i in range(start, len(slim_lines)):
            line = slim_lines[i]
            if line == marker or line.startswith(marker) or marker in line:
                return i
        raise SystemExit(f"marker not found: {marker!r}")

    i_manifest = find_marker(b"===MANIFEST===")
    i_sha = find_marker(b"===SHA256===")
    i_env = find_marker(b"===ENV===")
    i_cmd = find_marker(b"===CMD===")
    i_pred = find_marker(b"===PRED_COUNT===")
    i_conf = find_marker(b"===CONF_COUNT===")
    i_sample = find_marker(b"===HM_COARSE_SAMPLE===")

    # manifest: lines between MANIFEST marker and SHA marker; the SHA marker
    # line begins with the manifest closing brace ("}===SHA256===").
    man_lines = list(slim_lines[i_manifest + 1 : i_sha])
    if slim_lines[i_sha].startswith(b"}"):
        man_lines.append(b"}")
    man_cands = variants(man_lines)
    man_blob = try_verify("manifest.json", man_cands, report)

    # sha256.tsv: lines between SHA marker and ENV marker.
    tsv_lines = list(slim_lines[i_sha + 1 : i_env])
    tsv_cands = variants(tsv_lines)
    tsv_blob = try_verify("sha256.tsv", tsv_cands, report)

    # environment.txt: JSON between ENV marker and CMD marker.  Container file
    # embeds the pip freeze block (verified byte-exact with trailing newline).
    env_lines = list(slim_lines[i_env + 1 : i_cmd])
    env_cands = variants(env_lines, ends_no_newline=False)
    env_blob = try_verify("environment.txt", env_cands, report)

    # command.txt: first line after CMD marker.
    cmd_lines = [slim_lines[i_cmd + 1]]
    cmd_cands = variants(cmd_lines)
    cmd_blob = try_verify("command.txt", cmd_cands, report)

    # counts + sample (content-level evidence, no container-side hash target).
    pred_count = slim_lines[i_pred + 1].decode()
    conf_count = slim_lines[i_conf + 1].decode()
    sample_count = slim_lines[i_sample + 1].decode()
    sample_json = b"\n".join(slim_lines[i_sample + 2 :])
    report["_counts"] = {
        "pred_count": pred_count,
        "conf_count": conf_count,
        "hm_coarse_sample_rows": sample_count,
        "sample_bytes": len(sample_json),
    }

    # mapping file already local; verify against target.
    mapping_path = Path(r"D:\projects\course5-prep\scripts\v99_mapping_embedded.json")
    mapping_blob = mapping_path.read_bytes()
    if sha(mapping_blob) == TARGETS["v99_mapping_embedded.json"]:
        report["v99_mapping_embedded.json"] = {
            "status": "byte_exact",
            "variant": "local scripts/v99_mapping_embedded.json",
            "sha256": TARGETS["v99_mapping_embedded.json"],
        }
    else:
        report["v99_mapping_embedded.json"] = {"status": "sha_mismatch"}

    blobs = {
        "manifest.json": man_blob,
        "sha256.tsv": tsv_blob,
        "environment.txt": env_blob,
        "command.txt": cmd_blob,
        "v99_mapping_embedded.json": mapping_blob
        if sha(mapping_blob) == TARGETS["v99_mapping_embedded.json"]
        else None,
    }
    for name, blob in blobs.items():
        dest = OUT / name
        if blob is not None and not dest.exists():
            dest.write_bytes(blob)

    # sha256.tsv parse cross-check: verify our extracted tsv against targets.
    if tsv_blob:
        tsv_map = {}
        for row in tsv_blob.decode().splitlines():
            h, _, fn = row.partition("  ")
            tsv_map[fn.strip()] = h
        report["_tsv_parse"] = {
            "rows": len(tsv_map),
            "core_targets_consistent": all(
                tsv_map.get(k) == v for k, v in TARGETS.items() if k in tsv_map
            ),
        }
        (OUT / "_sha256_map.json").write_text(
            json.dumps(tsv_map, indent=1, ensure_ascii=False), encoding="utf-8"
        )

    (OUT / "_extraction-report.json").write_text(
        json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(report, indent=1, ensure_ascii=False))
    ok = all(
        report[k].get("status") == "byte_exact"
        for k in ("manifest.json", "sha256.tsv", "environment.txt", "command.txt")
    )
    print("CORE_BYTE_EXACT:", ok)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
