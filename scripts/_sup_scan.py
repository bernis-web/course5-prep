# -*- coding: utf-8 -*-
"""补充扫描：0.65x / 0.6500 的简写形态（0.65、0.651）、以及 459/1309 单独出现。"""
import json, os, re
from pathlib import Path

ROOT = Path(r"D:\projects\course5-prep")
EX = {"node_modules", ".venv39", "wheelhouse", "tmp", ".git", "__pycache__", ".pytest_cache",
      ".tmp-segs", ".tmp-dcs-chrome-profile", "_asr"}
PATS = {
    "X65": re.compile(r"0\.65(?!\d)"),          # 0.65 简写
    "X651": re.compile(r"0\.651(?!\d)"),        # 0.651
    "X6 5": re.compile(r"\b0\.6(?:49|50)\d?\b"),
}
def excluded(p):
    if set(p.parts) & EX: return True
    low = str(p).lower()
    return any(x in low for x in ("\\node_modules\\", "\\.venv39\\", "\\wheelhouse\\", "\\tmp\\"))

rows = []
for p in ROOT.rglob("*.md"):
    if excluded(p): continue
    try: txt = p.read_text(encoding="utf-8", errors="replace")
    except Exception: continue
    for i, line in enumerate(txt.splitlines(), 1):
        ids = [k for k, rx in PATS.items() if rx.search(line)]
        if ids:
            rows.append({"file": str(p.relative_to(ROOT)), "line": i, "ids": ids, "text": line.strip()[:260]})
out = ROOT / "results" / "audit-consistency-20261111" / "supplement-0.65.json"
out.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
print("hits:", len(rows))
for r in rows:
    print(f"{r['file']}:{r['line']}  {','.join(r['ids'])}  {r['text'][:160]}")