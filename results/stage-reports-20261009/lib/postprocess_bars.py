# 顶栏后处理：把 pptxgenjs 生成的直角矩形顶栏改为校模板原样的 snip2DiagRect（斜切）+ 蓝条渐变
# 用法: python postprocess_bars.py <pptx路径> [更多路径...]
import re, shutil, sys, zipfile
from pathlib import Path

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
LN_BLUE = '<a:ln w="12700"><a:solidFill><a:srgbClr val="0063B9"/></a:solidFill><a:prstDash val="solid"/></a:ln>'
LN_GOLD = '<a:ln w="12700"><a:solidFill><a:srgbClr val="FFC000"/></a:solidFill><a:prstDash val="solid"/></a:ln>'


def patch_block(x, name, is_blue):
    m = re.search(r'<p:sp>(?:(?!</p:sp>).)*?name="%s"(?:(?!</p:sp>).)*?</p:sp>' % name, x, re.S)
    if not m:
        return x, False
    blk = m.group(0)
    nb = blk.replace(RECT, SNIP)
    if is_blue:
        nb = nb.replace(LN_BLUE, '<a:ln><a:noFill/></a:ln>')
        nb = nb.replace('<a:solidFill><a:srgbClr val="0063B9"/></a:solidFill>', GRAD, 1)
    else:
        nb = nb.replace(LN_GOLD, '<a:ln><a:noFill/></a:ln>')
    return x.replace(blk, nb), True


def process(src):
    src = Path(src)
    zin = zipfile.ZipFile(src)
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
                patched.append((n, ok1 and ok2))
    assert patched and all(ok for _, ok in patched), "bar patch failed: %s" % patched
    tmp = src.with_suffix('.pptx.tmp')
    zout = zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED)
    for i in items:
        zout.writestr(i, data[i.filename])
    zout.close()
    shutil.move(str(tmp), str(src))
    print("patched %d slides: %s" % (len(patched), src.name))


if __name__ == '__main__':
    for p in sys.argv[1:]:
        process(p)
