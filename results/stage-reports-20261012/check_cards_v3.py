# 卡片内文字溢出检测：对比渲染文本块与源 pptx 中 roundRect 卡片的下沿
# 思路：从 pptx 读卡片几何（EMU→pt），从 PDF 读文本块，判断是否有文本块超出其所属卡片下沿 > 2pt
import sys, zipfile, re
import fitz

NS = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
EMU_PER_PT = 12700.0
EMU_PER_IN = 914400.0

def card_rects(pptx_path):
    z = zipfile.ZipFile(pptx_path)
    out = {}
    for n in z.namelist():
        if not re.match(r'ppt/slides/slide\d+\.xml$', n):
            continue
        x = z.read(n).decode('utf-8')
        idx = int(re.search(r'slide(\d+)\.xml', n).group(1))
        rects = []
        # 每个 <p:sp> 块；只看 prstGeom=roundRect 的卡片
        for blk in re.findall(r'<p:sp>.*?</p:sp>', x, re.S):
            if 'roundRect' not in blk:
                continue
            off = re.search(r'<a:off x="(-?\d+)" y="(-?\d+)"/>', blk)
            ext = re.search(r'<a:ext cx="(\d+)" cy="(\d+)"/>', blk)
            if not (off and ext):
                continue
            x0 = int(off.group(1)) / EMU_PER_PT
            y0 = int(off.group(2)) / EMU_PER_PT
            cx = int(ext.group(1)) / EMU_PER_PT
            cy = int(ext.group(2)) / EMU_PER_PT
            rects.append((x0, y0, x0 + cx, y0 + cy))
        out[idx] = rects
    return out

def main(pptx_path, pdf_path):
    cards = card_rects(pptx_path)
    doc = fitz.open(pdf_path)
    # PDF 页面尺寸(pt) 与 pptx 幻灯片尺寸(pt) 的缩放比
    page = doc[0]
    scale = page.rect.width / 960.0
    issues = []
    for i, p in enumerate(doc):
        idx = i + 1
        for b in p.get_text('blocks'):
            x0, y0, x1, y1, txt = b[0] / scale, b[1] / scale, b[2] / scale, b[3] / scale, b[4]
            if not txt.strip():
                continue
            for (cx0, cy0, cx1, cy1) in cards.get(idx, []):
                # 文本块水平落在卡片内且纵向起点在卡片内 → 检查下沿溢出
                if x0 >= cx0 - 3 and x1 <= cx1 + 14 and y0 >= cy0 - 2 and y0 < cy1:
                    if y1 > cy1 + 3:
                        issues.append((idx, round(y1 - cy1, 1), txt.strip()[:45].replace('\n', ' / ')))
                    break
    doc.close()
    if issues:
        print("CARD_OVERFLOW %d 处:" % len(issues))
        for i, d, t in issues:
            print("  p%d 超出卡片下沿 %.1fpt | %s" % (i, d, t))
    else:
        print("CARD_CLEAN: 无卡片内文字溢出")

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
