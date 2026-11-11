# -*- coding: utf-8 -*-
"""两个 docx 的表格与段落收敛到 v2 权威值。

不改「更正声明」段（那些是故意引用旧值并声明作废的），只改仍被当作现值的表格单元。
"""
from docx import Document
from pathlib import Path

AUTH_OPCA = {"0.1654": "0.1506", "0.1512": "0.2131", "0.2177": "0.2816", "0.4405": "0.4186"}
AUTH_SAT = {"0.1269": "0.1282", "0.1640": "0.1386", "0.3658": "0.4076", "0.3563": "0.2961"}

TARGETS = [
    (r"deliverables\课题5-总交接文档-20261028.docx", 2, {1: AUTH_OPCA, 2: AUTH_SAT}),
    (r"deliverables\课题5-组员汇报说明-小白版-20261110.docx", 4, {1: AUTH_OPCA}),
]

for path, t_idx, col_maps in TARGETS:
    p = Path(path)
    d = Document(str(p))
    tb = d.tables[t_idx]
    n = 0
    for row in tb.rows:
        for ci, mp in col_maps.items():
            if ci >= len(row.cells):
                continue
            cell = row.cells[ci]
            txt = cell.text.strip()
            if txt in mp:
                new = mp[txt]
                for par in cell.paragraphs:
                    if par.runs:
                        par.runs[0].text = new
                        for r in par.runs[1:]:
                            r.text = ""
                n += 1
    print(f"{p.name} 表{t_idx}: 改 {n} 格")
    d.save(str(p))

# 总交接 P67 的 oPCA 鱼向值 + 倍数
p = Path(r"deliverables\课题5-总交接文档-20261028.docx")
d = Document(str(p))
hits = 0
for par in d.paragraphs:
    if "0.4014 vs 0.1654" in par.text:
        for r in par.runs:
            if "0.1654" in r.text:
                r.text = r.text.replace("0.1654", "0.1506").replace("2.4 倍", "约 2.7 倍")
                hits += 1
        if hits == 0:
            full = par.text.replace("0.1654", "0.1506").replace("2.4 倍", "约 2.7 倍")
            par.runs[0].text = full
            for r in par.runs[1:]:
                r.text = ""
            hits += 1
print("P67 修:", hits)
d.save(str(p))