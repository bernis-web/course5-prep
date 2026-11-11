# -*- coding: utf-8 -*-
"""打印指定 docx 的指定表格全部单元格，用于判断「作废值在表里的角色」。"""
import sys
from docx import Document

p = sys.argv[1]
tables = [int(x) for x in sys.argv[2:]] if len(sys.argv) > 2 else None
doc = Document(p)
print("tables:", len(doc.tables))
for ti, t in enumerate(doc.tables, 1):
    if tables and ti not in tables:
        continue
    print("=" * 80, f"TABLE {ti}  rows={len(t.rows)} cols={len(t.columns)}")
    for ri, row in enumerate(t.rows, 1):
        cells = [c.text.strip().replace("\n", " ") for c in row.cells]
        print(f"  r{ri}: " + " ‖ ".join(cells))