# -*- coding: utf-8 -*-
"""Dump shape inventory of the current deck (v1) so the rebuild keeps the school chrome."""
import sys
from pptx import Presentation
from pptx.util import Emu

SRC = '课题5第03次汇报_三场景结论与可复现闭环.pptx'
prs = Presentation(SRC)
out = []
out.append('slide size: %.3f x %.3f in' % (prs.slide_width / 914400, prs.slide_height / 914400))
out.append('layout: %s' % ', '.join(l.name for l in prs.slide_layouts))
for i, s in enumerate(prs.slides, 1):
    out.append('=== slide %d layout=%r  shapes=%d' % (i, s.slide_layout.name, len(s.shapes)))
    bg = s._element.find(
        '{http://schemas.openxmlformats.org/presentationml/2006/main}bg')
    out.append('    has bg: %s  %s' % (bg is not None,
               '' if bg is None else bg.xml[:200].replace('\n', ' ')))
    for shp in s.shapes:
        st = str(shp.shape_type)
        txt = ''
        if shp.has_text_frame:
            txt = shp.text_frame.text.replace('\n', ' | ')[:40]
        ip = ''
        try:
            if shp.shape_type == 13:  # PICTURE
                ip = 'img=%s' % (shp.image.filename,)
        except Exception:
            pass
        out.append('    [%s] %-14s x=%.2f y=%.2f w=%.2f h=%.2f %s %s'
                   % (st.split(' ')[0], shp.name,
                      (shp.left or 0) / 914400, (shp.top or 0) / 914400,
                      (shp.width or 0) / 914400, (shp.height or 0) / 914400,
                      ip, txt))
    if s.has_notes_slide:
        out.append('    NOTES: %s' % s.notes_slide.notes_text_frame.text[:60].replace('\n', ' '))
open('_v2_inventory.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('OK lines=%d' % len(out))