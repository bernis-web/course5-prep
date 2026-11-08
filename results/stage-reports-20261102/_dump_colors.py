# -*- coding: utf-8 -*-
import sys, io, re
from pptx import Presentation
from lxml import etree
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

P = r"D:\projects\course5-prep\results\stage-reports-20261019\课题5第02次汇报_数字来源链_校模板-备注版.pptx"
prs = Presentation(P)

def srgb(el):
    out = []
    for c in el.iter():
        tag = etree.QName(c).localname
        if tag in ('srgbClr','schemeClr','prstClr','sysClr'):
            out.append((tag, c.get('val')))
    return out

print("### SLIDE BACKGROUND / XML roots")
for si, s in enumerate(prs.slides, 1):
    xml = s._element.xml
    bg = 'p:bg' in xml
    blips = re.findall(r'r:embed="(rId\d+)"', xml)
    print(f"slide{si}: has_bg={bg} embeds={blips}")

print("\n### KEY SHAPE FILLS / LINES")
targets = {
 1: ['Shape 0'],
 2: ['bar-blue','bar-gold','Shape 16','Shape 20'],
 3: ['Shape 5','Shape 8','Shape 11','Shape 15'],
 4: ['Shape 5','Shape 9','Shape 45'],
 6: ['Shape 6','Shape 7'],
}
for si, names in targets.items():
    s = prs.slides[si-1]
    for sh in s.shapes:
        if sh.name in names:
            x = sh._element.xml
            # extract spPr block
            m = re.search(r'<p:spPr>.*?</p:spPr>', x, re.S)
            body = m.group(0) if m else x[:600]
            body = re.sub(r'\s+', ' ', body)
            print(f"\n--- slide{si} {sh.name} ---")
            print(body[:1200])

print("\n### TABLE STYLE (slide 5 table xml head)")
t = None
for sh in prs.slides[4].shapes:
    if sh.has_table: t = sh; break
x = re.sub(r'\s+',' ', t._element.xml)
print(x[:2500])
