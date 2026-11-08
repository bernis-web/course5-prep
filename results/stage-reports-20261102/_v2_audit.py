# -*- coding: utf-8 -*-
"""Audit geometry of the rebuilt deck: textbox widths/positions, table col widths,
estimated vs available width, and orphan-line risk."""
import math
from pptx import Presentation
from pptx.util import Emu

prs = Presentation('_candidate2.pptx')
out = []


def w_of(s, size, mono=False):
    tot = 0.0
    for ch in s:
        c = ord(ch)
        if c >= 0x2E80:
            tot += 1.0
        elif mono:
            tot += 0.55
        elif ch == ' ':
            tot += 0.30
        elif ch.isdigit():
            tot += 0.56
        elif 'A' <= ch <= 'Z':
            tot += 0.66
        elif 'a' <= ch <= 'z':
            tot += 0.53
        elif ch in '±×÷→←↔–—…·¥✓（）「」':
            tot += 0.85
        else:
            tot += 0.50
    return tot * size / 72.0


for i, s in enumerate(prs.slides, 1):
    out.append('=== p%02d  %d shapes' % (i, len(s.shapes)))
    for shp in s.shapes:
        if not shp.has_text_frame:
            continue
        t = shp.text_frame.text
        if not t.strip():
            continue
        x, y = shp.left / 914400, shp.top / 914400
        w, h = shp.width / 914400, shp.height / 914400
        sizes = set()
        for p in shp.text_frame.paragraphs:
            for r in p.runs:
                if r.font.size:
                    sizes.add(round(r.font.size.pt, 1))
        sz = max(sizes) if sizes else 0
        # wrap estimate
        n = 0
        for line in t.split('\n'):
            n += max(1, math.ceil(w_of(line, sz) / w))
        need_h = n * sz * 1.5 / 72.0
        flag = ''
        if need_h > h + 0.05:
            flag += ' OVERFLOW_H(est %.2f > %.2f)' % (need_h, h)
        if w_of(max(t.split('\n'), key=lambda z: w_of(z, sz)), sz) > w + 0.02:
            flag += ' WRAPS'
        out.append('  x=%.2f y=%.2f w=%.2f h=%.2f  sz=%-4s "%s"%s'
                   % (x, y, w, h, sz, t.replace('\n', ' / ')[:46], flag))
open('_v2_audit.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('OK', len(out))
