# 渲染 + 版式碰撞自检（只读核对用，不写入任何既有目录）
# 用法: python render_and_check.py <pdf> <outdir>
import sys, os
import fitz

def main(pdf, outdir):
    os.makedirs(outdir, exist_ok=True)
    doc = fitz.open(pdf)
    print("PAGES=%d" % doc.page_count)
    problems = []
    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=110)
        p = os.path.join(outdir, "p%02d.png" % (i + 1))
        pix.save(p)
        # 1) 文本是否溢出页面边界
        pw, ph = page.rect.width, page.rect.height
        for b in page.get_text("blocks"):
            x0, y0, x1, y1, txt = b[0], b[1], b[2], b[3], b[4]
            if not txt.strip():
                continue
            if x0 < -1 or y0 < -1 or x1 > pw + 1 or y1 > ph + 1:
                problems.append("p%d OUT_OF_PAGE %r" % (i + 1, txt.strip()[:40]))
        print("p%02d rendered %dx%d" % (i + 1, pix.width, pix.height))
    if problems:
        print("PROBLEMS:")
        for x in problems:
            print("  " + x)
    else:
        print("BOUNDS_CLEAN: no text outside page area")
    doc.close()

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
