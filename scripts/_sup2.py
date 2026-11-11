# -*- coding: utf-8 -*-
"""补充扫描 2：PDF（交付物孪生件）+ CSV/XLSX（素材）"""
import json, re
from pathlib import Path

ROOT = Path(r"D:\projects\course5-prep")
EX = {"node_modules", ".venv39", "wheelhouse", "tmp", ".git", "__pycache__"}
PATS = [
    ("V01", r"0\.4147"), ("V02", r"0\.4010"), ("V03", r"0\.2479"), ("V04", r"0\.4021"),
    ("V05", r"0\.6500|0\.65(?!\d)"), ("V06", r"0\.6510|0\.651(?!\d)"),
    ("V07", r"0\.4560"), ("V08", r"0\.4588"), ("V09", r"0\.0428"), ("V10", r"0\.1882"),
    ("V11", r"0\.1940"), ("V12", r"865\s*个|\b865\b"),
    ("V13", r"459\s*[-–—~至]\s*1309"), ("V14", r"29\s*[-–—~至]\s*87\s*%"),
    ("X25", r"0\.3658|0\.3563|0\.1269|0\.1640"),
]
CP = [(i, re.compile(p)) for i, p in PATS]

def scan(text, label):
    rows = []
    for ln, line in enumerate(text.splitlines(), 1):
        ids = [i for i, rx in CP if rx.search(line)]
        if ids:
            rows.append({"loc": f"{label}:{ln}", "ids": ids, "text": line.strip()[:220]})
    return rows

out = []

def add(p, rows):
    if rows:
        out.append({"file": str(p.relative_to(ROOT)), "rows": rows})

for p in list(ROOT.rglob("*.pdf")) + list(ROOT.rglob("*.csv")) + list(ROOT.rglob("*.xlsx")):
    if set(p.parts) & EX or "\\tmp\\" in str(p).lower():
        continue
    try:
        if p.suffix.lower() == ".pdf":
            from pypdf import PdfReader
            r = PdfReader(str(p))
            rows = []
            for pi, page in enumerate(r.pages, 1):
                rows += scan(page.extract_text() or "", f"p{pi}")
            add(p, rows)
        elif p.suffix.lower() == ".csv":
            txt = p.read_text(encoding="utf-8", errors="replace")
            add(p, scan(txt, "L"))
        else:
            import openpyxl
            wb = openpyxl.load_workbook(str(p), data_only=True)
            rows = []
            for ws in wb.worksheets:
                for ri, row in enumerate(ws.iter_rows(values_only=True), 1):
                    tc = " | ".join(str(c) for c in row if c is not None)
                    ids = [i for i, rx in CP if rx.search(tc)]
                    if ids:
                        rows.append({"loc": f"{ws.title}!r{ri}", "ids": ids, "text": tc[:220]})
            add(p, rows)
    except Exception as e:
        print("ERR", p, e)

dst = ROOT / "results" / "audit-consistency-20261111" / "hits-pdf-csv.json"
dst.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print("files with hits:", len(out))
for o in out:
    ids = sorted({i for r in o["rows"] for i in r["ids"]})
    print(f"{o['file']}\t{len(o['rows'])}\t{','.join(ids)}")