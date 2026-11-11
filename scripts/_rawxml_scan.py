# -*- coding: utf-8 -*-
"""原始 XML 扫描：docx/pptx 内部所有 part（含图表缓存、文本框、备注），
补 structured 抽取漏掉的 chart / txbx。"""
import json, re, zipfile
from pathlib import Path

ROOT = Path(r"D:\projects\course5-prep")
EX = {"node_modules", ".venv39", "wheelhouse", "tmp", ".git", "__pycache__", ".pytest_cache",
      ".tmp-segs", ".tmp-dcs-chrome-profile", "_asr"}
PATS = [
    ("V01", r"0\.4147"), ("V02", r"0\.4010"), ("V03", r"0\.2479"), ("V04", r"0\.4021"),
    ("V05", r"0\.6500|0\.65(?![0-9])"), ("V06", r"0\.6510|0\.651(?![0-9])"),
    ("V07", r"0\.4560"), ("V08", r"0\.4588"), ("V09", r"0\.0428"), ("V10", r"0\.1882"),
    ("V11", r"0\.1940"), ("V12", r"865\s*个|>865<|\b865\b"),
    ("V13", r"459\s*[-–—~至]\s*1309"), ("V14", r"29\s*[-–—~至]\s*87\s*%"),
    ("X25", r"0\.3658|0\.3563|0\.1269|0\.1640"),
]
CP = [(i, re.compile(p)) for i, p in PATS]

def excluded(p):
    if set(p.parts) & EX: return True
    low = str(p).lower()
    return any(x in low for x in ("\\node_modules\\", "\\.venv39\\", "\\wheelhouse\\", "\\tmp\\"))

out = []
for p in ROOT.rglob("*"):
    if p.suffix.lower() not in (".docx", ".pptx") or not p.is_file() or excluded(p):
        continue
    try:
        z = zipfile.ZipFile(p)
    except Exception as e:
        print("ZIPERR", p, e); continue
    parts = {}
    for name in z.namelist():
        if not name.endswith((".xml", ".rels")):
            continue
        try:
            raw = z.read(name).decode("utf-8", errors="replace")
        except Exception:
            continue
        ids = sorted({i for i, rx in CP if rx.search(raw)})
        if ids:
            # 粗定位：对 slide 取编号
            parts[name] = ids
    if parts:
        out.append({"file": str(p.relative_to(ROOT)), "parts": parts})

dst = ROOT / "results" / "audit-consistency-20261111" / "hits-rawxml.json"
dst.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print("files with raw-xml hits:", len(out))
for o in out:
    chartish = [k for k in o["parts"] if "chart" in k]
    print(f"{o['file']}")
    for k, ids in o["parts"].items():
        tag = " [CHART]" if "chart" in k else ""
        print(f"    {k}{tag}: {','.join(ids)}")