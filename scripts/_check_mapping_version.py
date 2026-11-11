"""核对 scVI 那次用的映射表版本：按 sha256 比对 config/ 下各版本

为什么要核：SATURN 臂若用 v2 而 scVI 臂用 v1，两边的「粗类」定义就不同，
macro-F1 不可比，等于白做。
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "results" / "phase-20261019" / "scvi-cross-species" / "manifest.json"


def main() -> int:
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    want = m["mapping_sha256"]
    print("scVI 记录的 mapping_sha256:", want)
    hit = None
    for p in sorted((ROOT / "config").glob("heart-celltype-map-*.tsv")):
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        mark = "  <== 匹配" if h == want else ""
        print(f"  {p.name}: {h}{mark}")
        if h == want:
            hit = p.name
    print()
    if hit:
        print(f"结论：scVI 用的是 {hit}，SATURN 臂必须用同一个")
    else:
        print("结论：config/ 下没有任何版本与 scVI 记录一致——两边口径本就不同")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())