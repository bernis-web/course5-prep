#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
去掉 PPT 里对外的期次标识（内部知道是第几次就行，观众不需要）。
只改这几个字串，其余一字不动。
"""
import os, re, sys
from pptx import Presentation

BASE = r"D:\projects\course5-prep\results\stage-reports-20261102"
SRC = os.path.join(BASE, "课题5第03次汇报_三场景结论与可复现闭环.pptx")
DST = os.path.join(BASE, "课题5-三场景结论与可复现闭环.pptx")

# 按顺序替换：先换长的，避免残留
RULES = [
    (r'第\s*3\s*次汇报（老师七条意见之后的重做）\s*[｜|]\s*', ''),
    (r'[｜|]\s*第\s*3\s*次汇报（老师七条意见之后的重做）', ''),
    (r'（老师七条意见之后的重做）', ''),
    (r'\s*[·・]\s*第\s*3\s*次汇报\s*[·・]\s*', ' · '),
    (r'第\s*3\s*次汇报\s*[·・]\s*', ''),
    (r'\s*[·・]\s*第\s*3\s*次汇报', ''),
    (r'第\s*3\s*次汇报', ''),
    (r'课题\s*5\s*[｜|]\s*XenoTransfer', '课题 5 · XenoTransfer'),
]

def clean(s):
    out = s
    for pat, rep in RULES:
        out = re.sub(pat, rep, out)
    out = re.sub(r'\s{2,}', ' ', out).strip(' ·｜|')
    # 恢复正常间距
    out = out.replace('课题 5·', '课题 5 · ').replace('·XenoTransfer', ' · XenoTransfer')
    return out

def main():
    prs = Presentation(SRC)
    changed = []

    for si, slide in enumerate(prs.slides, 1):
        for shape in slide.shapes:
            if not shape.has_text_frame:
                continue
            for para in shape.text_frame.paragraphs:
                full = ''.join(r.text for r in para.runs)
                if not full or '次汇报' not in full and '重做' not in full:
                    continue
                new = clean(full)
                if new == full:
                    continue
                changed.append((si, full, new))
                if para.runs:
                    para.runs[0].text = new
                    for r in para.runs[1:]:
                        r.text = ''

    prs.save(DST)
    print('写出:', DST)
    print('大小: %.2f MB' % (os.path.getsize(DST) / 1048576))
    print('改动 %d 处:' % len(changed))
    for si, old, new in changed:
        print('  第%2d页' % si)
        print('    改前: %s' % old)
        print('    改后: %s' % new)

if __name__ == '__main__':
    main()
