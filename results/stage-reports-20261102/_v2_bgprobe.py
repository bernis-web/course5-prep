# -*- coding: utf-8 -*-
import zipfile, re
SRC = '课题5第03次汇报_三场景结论与可复现闭环.pptx'
z = zipfile.ZipFile(SRC)
x = z.read('ppt/slides/slide1.xml').decode('utf-8')
out = []
out.append('len=%d' % len(x))
out.append('bg? %s' % ('<p:bg' in x))
out.append('blip? %s' % ('blip' in x))
out.append('rel ids: %s' % re.findall(r'r:(?:embed|id)="([^"]+)"', x))
out.append('---- rels')
out.append(z.read('ppt/slides/_rels/slide1.xml.rels').decode('utf-8'))
out.append('---- first 1200 chars of slide1.xml')
out.append(x[:1200])
out.append('---- slide4 rels')
out.append(z.read('ppt/slides/_rels/slide4.xml.rels').decode('utf-8'))
open('_v2_bgprobe.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('ok')
