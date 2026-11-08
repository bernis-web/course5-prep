# -*- coding: utf-8 -*-
"""Compact content dump: title / subtitle / bullet-lines / tables, per slide."""
import sys, io, json
from pptx import Presentation
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

P = r"D:\projects\course5-prep\results\stage-reports-20261102\课题5第03次汇报_三场景结论与可复现闭环.pptx"
prs = Presentation(P)
out = []
for si, s in enumerate(prs.slides, 1):
    texts, tables = [], []
    for sh in s.shapes:
        if sh.has_table:
            tables.append([[c.text for c in row.cells] for row in sh.table.rows])
        elif sh.has_text_frame and sh.text_frame.text.strip():
            texts.append((round(sh.top/914400, 2), sh.text_frame.text))
    texts.sort()
    rec = {"slide": si, "title": None, "subtitle": None, "bullets": [], "tables": tables,
           "takeaway": None, "footer": None}
    for t, txt in texts:
        if t < 0.9:
            rec["title"] = txt
        elif t < 1.2:
            rec["subtitle"] = txt
        elif t > 7.0 and txt.isdigit():
            pass
        elif t > 7.0:
            rec["footer"] = txt
        elif t > 5.5:
            rec["takeaway"] = txt
        else:
            rec["bullets"].extend(txt.split("\n"))
    out.append(rec)

print(json.dumps(out, ensure_ascii=False, indent=1))
