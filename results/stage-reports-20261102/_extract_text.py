# -*- coding: utf-8 -*-
"""Extract every text string from the delivered 15-page deck, in reading order."""
import sys, io, json
from pptx import Presentation
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

P = r"D:\projects\course5-prep\results\stage-reports-20261102\课题5第03次汇报_三场景结论与可复现闭环.pptx"
prs = Presentation(P)
out = []
for si, s in enumerate(prs.slides, 1):
    page = {"slide": si, "texts": [], "tables": []}
    for sh in s.shapes:
        if sh.has_table:
            t = sh.table
            page["tables"].append([[c.text for c in row.cells] for row in t.rows])
        elif sh.has_text_frame:
            txt = sh.text_frame.text
            if txt.strip():
                page["texts"].append({
                    "text": txt,
                    "t": round(sh.top/914400, 2), "l": round(sh.left/914400, 2),
                    "w": round(sh.width/914400, 2), "h": round(sh.height/914400, 2),
                    "sizes": sorted({r.font.size.pt for p in sh.text_frame.paragraphs
                                     for r in p.runs if r.font.size}),
                })
    out.append(page)

print(json.dumps(out, ensure_ascii=False, indent=1))
