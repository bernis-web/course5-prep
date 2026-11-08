# 后处理：将校模板版 PPT 的两条顶栏从直角矩形改为模板原样的 snip2DiagRect（斜切）
# 蓝条加模板渐变（002060→004592→0063B9→0076D2, 80°），金条保持 FFC000，边线改为无
import re, shutil, zipfile, sys
from pathlib import Path

SRC = Path("results/report-02-metric-lineage-20261008/课题5第二阶段汇报_数字来源链_校模板版.pptx")

SNIP = ('<a:prstGeom prst="snip2DiagRect"><a:avLst>'
        '<a:gd name="adj1" fmla="val 0"/><a:gd name="adj2" fmla="val 50000"/>'
        '</a:avLst></a:prstGeom>')
RECT = '<a:prstGeom prst="rect"><a:avLst></a:avLst></a:prstGeom>'
GRAD = ('<a:gradFill><a:gsLst>'
        '<a:gs pos="0"><a:srgbClr val="002060"/></a:gs>'
        '<a:gs pos="26000"><a:srgbClr val="004592"/></a:gs>'
        '<a:gs pos="57000"><a:srgbClr val="0063B9"/></a:gs>'
        '<a:gs pos="100000"><a:srgbClr val="0076D2"/></a:gs>'
        '</a:gsLst><a:lin ang="4800000" scaled="0"/></a:gradFill>')

def patch_block(x, name, is_blue):
    m = re.search(r'<p:sp>(?:(?!</p:sp>).)*?name="%s"(?:(?!</p:sp>).)*?</p:sp>' % name, x, re.S)
    if not m:
        return x, False
    blk = m.group(0)
    nb = blk.replace(RECT, SNIP)
    if is_blue:
        # 先替换线条（精确匹配含 prstDash 的完整 ln），再只替换第一处 solidFill（形状填充）
        nb = nb.replace('<a:ln w="12700"><a:solidFill><a:srgbClr val="0063B9"/></a:solidFill><a:prstDash val="solid"/></a:ln>',
                        '<a:ln><a:noFill/></a:ln>')
        nb = nb.replace('<a:solidFill><a:srgbClr val="0063B9"/></a:solidFill>', GRAD, 1)
    else:
        nb = nb.replace('<a:ln w="12700"><a:solidFill><a:srgbClr val="FFC000"/></a:solidFill><a:prstDash val="solid"/></a:ln>',
                        '<a:ln><a:noFill/></a:ln>')
    return x.replace(blk, nb), True

zin = zipfile.ZipFile(SRC)
items = zin.infolist()
data = {i.filename: zin.read(i.filename) for i in items}
zin.close()

patched = []
for n in list(data):
    if re.match(r'ppt/slides/slide\d+\.xml$', n):
        x = data[n].decode('utf-8')
        if 'name="bar-blue"' in x:
            x, ok1 = patch_block(x, 'bar-blue', True)
            x, ok2 = patch_block(x, 'bar-gold', False)
            data[n] = x.encode('utf-8')
            patched.append((n, ok1, ok2))

print("patched slides:", patched)
assert all(a and b for _, a, b in patched) and len(patched) == 7, "expected 7 content slides patched"

tmp = SRC.with_suffix('.pptx.tmp')
zout = zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED)
for i in items:
    zout.writestr(i, data[i.filename])
zout.close()
shutil.move(str(tmp), str(SRC))
print("done:", SRC.stat().st_size, "bytes")
