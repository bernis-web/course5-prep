# -*- coding: utf-8 -*-
"""扫描老师七条意见回应 docx 里的作废数字，段落与表格都过一遍。"""
import re
import sys
from docx import Document

P = r"D:\projects\course5-prep\deliverables\课题5-老师七条意见回应-20261030.docx"
STALE = ["0.6510", "0.6500", "0.4560", "0.4588", "0.4147", "0.4010", "0.2479", "0.4021",
         "0.1269", "0.1640", "0.3658", "0.3563", "0.1654", "0.1512", "0.2177", "0.4405",
         "0.0428", "0.1882", "0.1940", "0.2633", "0.2005", "0.1713", "0.0709",
         "459", "1309", "300 倍", "865", "11–13", "11-13", "0.65"]

d = Document(P)
hits = 0
print("=== 段落 ===")
for i, p in enumerate(d.paragraphs):
    t = p.text
    found = [s for s in STALE if s in t]
    if found:
        hits += len(found)
        print(f"[P{i}] {found} :: {t[:150]}")
print("=== 表格 ===")
for ti, tb in enumerate(d.tables):
    for ri, row in enumerate(tb.rows):
        for ci, cell in enumerate(row.cells):
            t = cell.text
            found = [s for s in STALE if s in t]
            if found:
                hits += len(found)
                print(f"[T{ti} r{ri} c{ci}] {found} :: {t[:100]}")
print("总命中:", hits)
print("段落数", len(d.paragraphs), "表格数", len(d.tables))