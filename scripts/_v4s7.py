# -*- coding: utf-8 -*-
from pptx import Presentation

p = r"D:\projects\course5-prep\deliverables\课题5-汇报-v4-20261111.pptx"
prs = Presentation(p)
print("slides:", len(prs.slides))
s = prs.slides[6]
for sh in s.shapes:
    t = ""
    if sh.has_text_frame:
        t = sh.text_frame.text.replace("\n", " / ")[:200]
    print("- type=%s name=%r table=%s chart=%s text=%r" % (
        sh.shape_type, sh.name, getattr(sh, "has_table", None), getattr(sh, "has_chart", None), t))
print("--- notes ---")
if s.has_notes_slide:
    print(s.notes_slide.notes_text_frame.text[:400])