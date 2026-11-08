# -*- coding: utf-8 -*-
"""Dump school template: master, DEFAULT layout, per-slide shape tree, colors, fonts."""
import sys, io
from pptx import Presentation
from pptx.util import Emu, Pt

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

P = r"D:\projects\course5-prep\results\stage-reports-20261019\课题5第02次汇报_数字来源链_校模板-备注版.pptx"

def emu2in(v):
    if v is None: return None
    return round(v / 914400, 3)

prs = Presentation(P)
print("=== PRESENTATION ===")
print("slide size:", emu2in(prs.slide_width), "x", emu2in(prs.slide_height), "in")
print("num slides:", len(prs.slides))
print("num masters:", len(prs.slide_masters))

for mi, m in enumerate(prs.slide_masters):
    print(f"\n=== MASTER {mi} name={m.name!r} ===")
    print("layouts:", [(l.name, len(l.placeholders)) for l in m.slide_layouts])
    try:
        tx = m.text_styles
        for k in ('title','body','other'):
            st = getattr(tx, k, None)
            if st is not None:
                print(f"  master text_style[{k}]: size={st.font.size and st.font.size.pt} name={st.font.name}")
    except Exception as e:
        print("  text_styles err", e)
    print("  master shapes:")
    for sh in m.shapes:
        print(f"    - {sh.shape_type} name={sh.name!r} L={emu2in(sh.left)} T={emu2in(sh.top)} W={emu2in(sh.width)} H={emu2in(sh.height)}")

for li, l in enumerate(prs.slide_masters[0].slide_layouts):
    print(f"\n=== LAYOUT[{li}] name={l.name!r} ===")
    for sh in l.shapes:
        print(f"    - {sh.shape_type} name={sh.name!r} ph={sh.is_placeholder and sh.placeholder_format.type} L={emu2in(sh.left)} T={emu2in(sh.top)} W={emu2in(sh.width)} H={emu2in(sh.height)}")

for si, s in enumerate(prs.slides, 1):
    print(f"\n=== SLIDE {si} layout={s.slide_layout.name!r} ===")
    for sh in s.shapes:
        info = f"  [{sh.shape_id}] {sh.shape_type} name={sh.name!r}"
        try:
            info += f" ph={sh.placeholder_format.type} idx={sh.placeholder_format.idx}"
        except Exception:
            pass
        info += f" L={emu2in(sh.left)} T={emu2in(sh.top)} W={emu2in(sh.width)} H={emu2in(sh.height)}"
        print(info)
        if sh.has_text_frame:
            for pi, para in enumerate(sh.text_frame.paragraphs):
                runs = []
                for r in para.runs:
                    sz = r.font.size.pt if r.font.size else None
                    col = None
                    try:
                        if r.font.color and r.font.color.type is not None:
                            col = str(r.font.color.rgb) if r.font.color.type == 1 else f"theme:{r.font.color.theme_color}"
                    except Exception:
                        pass
                    runs.append((r.text[:40], r.font.name, sz, r.font.bold, col))
                if runs:
                    print(f"      p{pi} align={para.alignment} lvl={para.level} space_b={para.space_before and para.space_before.pt} space_a={para.space_after and para.space_after.pt} ls={para.line_spacing}")
                    for rr in runs:
                        print(f"         run={rr}")
        if sh.has_table:
            t = sh.table
            print(f"      TABLE rows={len(t.rows)} cols={len(t.columns)} colw={[emu2in(c.width) for c in t.columns]}")
            for ri, row in enumerate(t.rows):
                print(f"        row{ri} h={emu2in(row.height)}")
                for ci, cell in enumerate(row.cells):
                    txt = cell.text.replace("\n"," / ")[:50]
                    sz = None
                    for p in cell.text_frame.paragraphs:
                        for r in p.runs:
                            if r.font.size: sz = r.font.size.pt; break
                        if sz: break
                    print(f"          c{ci} sz={sz} txt={txt!r}")
