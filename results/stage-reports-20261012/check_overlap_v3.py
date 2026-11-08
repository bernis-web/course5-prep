# 版式重叠自检：检测同一页上"底部结论条"与"卡片/表格"的纵向重叠
import sys, zipfile, re
import fitz

EMU_PER_PT = 12700.0

def shapes(pptx_path):
    z = zipfile.ZipFile(pptx_path)
    res = {}
    for n in z.namelist():
        if not re.match(r'ppt/slides/slide\d+\.xml$', n):
            continue
        x = z.read(n).decode('utf-8')
        idx = int(re.search(r'slide(\d+)\.xml', n).group(1))
        items = []
        for blk in re.findall(r'<p:sp>.*?</p:sp>', x, re.S):
            geom = re.search(r'prstGeom prst="(\w+)"', blk)
            off = re.search(r'<a:off x="(-?\d+)" y="(-?\d+)"/>', blk)
            ext = re.search(r'<a:ext cx="(\d+)" cy="(\d+)"/>', blk)
            if not (geom and off and ext):
                continue
            kind = geom.group(1)
            x0 = int(off.group(1)) / EMU_PER_PT
            y0 = int(off.group(2)) / EMU_PER_PT
            w = int(ext.group(1)) / EMU_PER_PT
            h = int(ext.group(2)) / EMU_PER_PT
            items.append((kind, x0, y0, w, h))
        res[idx] = items
    return res

def main(pptx_path, pdf_path):
    sh = shapes(pptx_path)
    doc = fitz.open(pdf_path)
    print("slides in pptx: %d, pages in pdf: %d" % (len(sh), doc.page_count))
    problems = []
    for i, page in enumerate(doc):
        idx = i + 1
        items = sh.get(idx, [])
        # 找出真正的"通栏结论条"：宽度 == 版面宽（13.333in）且 y>2.0
        # 卡片最宽 12.1in，故用 13.0in 阈值严格区分
        bands = [it for it in items if it[0] == 'rect' and it[3] >= 13.0 and it[2] > 2.0]
        others = []
        for it in items:
            k, x, y, w, h = it
            if it in bands:
                continue
            if k in ('roundRect', 'rect') and y > 1.5:
                others.append(it)
        for b in bands:
            _, bx, by, bw, bh = b
            for o in others:
                _, ox, oy, ow, oh = o
                if o[3] >= 13.0:   # 跳过其他通栏条
                    continue
                # 水平有交集且纵向重叠
                if ox < bx + bw and ox + ow > bx:
                    if oy < by + bh - 0.02 and oy + oh > by + 0.02:
                        problems.append((idx, 'band@%.2f-%.2f 与 shape(%s)@%.2f-%.2f 重叠' %
                                         (by, by + bh, o[0], oy, oy + oh)))
    doc.close()
    if problems:
        print("OVERLAP %d 处:" % len(problems))
        for p in problems:
            print("  p%d %s" % (p[0], p[1]))
    else:
        print("OVERLAP_CLEAN: 底部结论条与卡片/表格无重叠")

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
