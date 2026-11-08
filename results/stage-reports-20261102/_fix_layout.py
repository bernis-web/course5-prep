# -*- coding: utf-8 -*-
"""
第 03 次汇报 PPT 排版修复（只改版式：列宽 / 文本块位置 / 段间距 / 段内字号统一）。
不动任何文字、数字、配色、字体族。

用法：
    python _fix_layout.py            # 真改
    python _fix_layout.py --dry-run  # 只打印将要改什么
"""
import sys
from pptx import Presentation
from pptx.util import Inches, Pt

PPTX = r"D:\projects\course5-prep\results\stage-reports-20261102\课题5第03次汇报_三场景结论与可复现闭环.pptx"
EMU = 914400.0
DRY = "--dry-run" in sys.argv

# ---- 修复计划 -------------------------------------------------------------
# (slide_no, shape_name) -> 属性
BODY_FIX = {
    # 页: (新 top(in), 新 space_after(pt), 段内字号统一为(pt) 或 None 不动)
    1:  (2.65, 22.0, 15.5),   # 封面：正文块下移 + 拉开段间距，消除底部 2.8in 空洞
    3:  (2.20, 18.0, 15.5),   # para0 原本 14pt，与 para1/2 的 15.5pt 不统一
    12: (2.20, 18.0, 15.5),   # para0/para1 原本 14pt
    14: (1.50, 13.0, 15.5),   # para0/para4 原本 14pt，位置不动
    15: (2.65, 22.0, 15.5),   # para2 原本 14pt + 底部空洞
}

# 第 2 页表格列宽（in）：把「产物」列过宽的 0.78in 让给内容更长的「我们做了什么」列
S2_COLS = [3.55, 4.85, 3.50]

prs = Presentation(PPTX)
log = []

for idx, slide in enumerate(prs.slides, 1):
    for sh in slide.shapes:
        # --- 表格列宽 ---
        if idx == 2 and sh.has_table:
            tbl = sh.table
            old = [round(c.width / EMU, 3) for c in tbl.columns]
            assert abs(sum(old) - 11.90) < 0.02, old
            for ci, w in enumerate(S2_COLS):
                tbl.columns[ci].width = Inches(w)
            log.append("s2  table cols %s -> %s" % (old, S2_COLS))

        # --- 正文块 ---
        if idx in BODY_FIX and sh.has_text_frame and sh.name == "TextBox 4":
            top, sa, size = BODY_FIX[idx]
            old_top = round(sh.top / EMU, 3)
            sh.top = Inches(top)
            log.append("s%-2d TextBox 4 top %.2f -> %.2f" % (idx, old_top, top))
            for pi, para in enumerate(sh.text_frame.paragraphs):
                old_sa = (para.space_after / 12700.0) if para.space_after else None
                if sa is not None:
                    para.space_after = Pt(sa)
                if old_sa != sa:
                    log.append("     para%d space_after %s -> %s" % (pi, old_sa, sa))
                if size is not None:
                    for r in para.runs:
                        old_sz = (r.font.size / 12700.0) if r.font.size else None
                        if old_sz != size:
                            log.append("     para%d run size %s -> %s" % (pi, old_sz, size))
                        r.font.size = Pt(size)

print("\n".join(log) if log else "(nothing to do)")

if not DRY:
    prs.save(PPTX)
    import os
    print("\nSAVED %s (%d bytes)" % (PPTX, os.path.getsize(PPTX)))
else:
    print("\n[dry-run] not saved")
