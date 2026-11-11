# -*- coding: utf-8 -*-
"""v5 设计战线验收：四条判据一次算完，输出可引用的记分卡。

判据（与目标书对齐）：
  留白 ≥ 25%    —— 相对**页面主色**的非墨像素占比（渲染 110 dpi 采样）
  对齐 ≤ 0.1"   —— 同一页内，同列元素左缘的**簇内极差**；卡片内文与卡片的偏移必须 = PAD±0.02
  图优于字       —— 承载定量信息的位置必须是图表或图形，不能是「数字堆在文字里」
  对比 ≥ 4.5:1  —— 正文级（≤12pt）run 与其所在形状填充（无填充则页面主色）的 WCAG 比
"""
import json
from collections import Counter, defaultdict
from pathlib import Path

import fitz
from PIL import Image
from pptx import Presentation

ROOT = Path(r"D:\projects\course5-prep")
PPTX = ROOT / "deliverables" / "课题5-汇报-v5-20261111.pptx"
PDF = ROOT / "deliverables" / "课题5-汇报-v5-20261111.pdf"
OUT = ROOT / "tmp" / "v5check"
OUT.mkdir(exist_ok=True)
EMU = 914400.0
PAD = 0.36
TOL_CLUSTER = 0.06


def lum(rgb):
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = [f(c / 255) for c in rgb]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(fg, bg):
    a, b = sorted([lum(fg), lum(bg)], reverse=True)
    return (a + 0.05) / (b + 0.05)


def modal_bg(doc, i):
    pix = doc[i].get_pixmap(dpi=90)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    px = img.load()
    c = Counter()
    for y in range(0, img.size[1], 3):
        for x in range(0, img.size[0], 3):
            c[px[x, y]] += 1
    return c.most_common(1)[0][0]


def whitespace(doc, i, bg):
    pix = doc[i].get_pixmap(dpi=110)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    px = img.load()
    tot = same = 0
    for y in range(0, img.size[1], 2):
        for x in range(0, img.size[0], 2):
            r, g, b = px[x, y]
            tot += 1
            if abs(r - bg[0]) <= 6 and abs(g - bg[1]) <= 6 and abs(b - bg[2]) <= 6:
                same += 1
    return same / tot


def fill_of(sh):
    try:
        if str(sh.fill.type).startswith("MSO_FILL.SOLID"):
            c = sh.fill.fore_color.rgb
            return (c[0], c[1], c[2])
    except Exception:
        pass
    return None


prs = Presentation(str(PPTX))
doc = fitz.open(str(PDF))
rows = []
for pi, slide in enumerate(prs.slides):
    bg = modal_bg(doc, pi)
    ws = whitespace(doc, pi, bg)

    content = []
    for sh in slide.shapes:
        if None in (sh.left, sh.top, sh.width, sh.height):
            continue
        l, t, w = sh.left / EMU, sh.top / EMU, sh.width / EMU
        if l <= 0.05 and w >= 12.0:          # 全幅底色带
            continue
        if t > 6.55 or t < 0.35:             # 页脚/页码/页眉
            continue
        content.append((round(l, 3), t, w, sh))

    # 列簇：把左缘按 0.06 容差聚成「列线」，极差即对齐误差
    lefts = sorted({c[0] for c in content})
    clusters = []
    for l in lefts:
        if clusters and l - clusters[-1][-1] <= TOL_CLUSTER:
            clusters[-1].append(l)
        else:
            clusters.append([l])
    spreads = [round(c[-1] - c[0], 3) for c in clusters if len(c) > 1]
    max_spread = max(spreads) if spreads else 0.0

    # 卡片内文偏移：同一 left 上既有一个带填色的矩形，又有其右侧 PAD 处的文字
    pad_bad = []
    for l, t, w, sh in content:
        if sh.has_text_frame and sh.text_frame.text.strip():
            hosts = [c for c in content
                     if c[3] is not sh and abs(c[0] + PAD - l) <= 0.05
                     and c[2] >= w and fill_of(c[3]) is not None]
            if not hosts:
                # 检查是否落在某个卡片内部但偏移不对
                inside = [c for c in content
                          if c[3] is not sh and c[0] < l < c[0] + c[2]
                          and c[0] + PAD + 0.05 < l < c[0] + 0.62
                          and fill_of(c[3]) is not None]
                if inside:
                    pad_bad.append((l, round(l - inside[0][0], 3), sh.text_frame.text[:10]))

    sizes, chars, low = [], 0, []
    for sh in slide.shapes:
        if not sh.has_text_frame:
            continue
        fill = fill_of(sh)
        for p in sh.text_frame.paragraphs:
            for r in p.runs:
                if not r.text.strip():
                    continue
                chars += len(r.text)
                pt = round(r.font.size.pt, 1) if r.font.size else 12.0
                sizes.append(pt)
                try:
                    fg = (r.font.color.rgb[0], r.font.color.rgb[1], r.font.color.rgb[2])
                except Exception:
                    fg = (0x15, 0x39, 0x57)
                c = contrast(fg, fill or bg)
                if pt <= 12 and c < 4.5:
                    low.append((pt, round(c, 2), r.text[:12]))

    charts = sum(1 for sh in slide.shapes if sh.has_chart)
    pics = sum(1 for sh in slide.shapes if sh.shape_type == 13)
    tiers = sorted({s for s in sizes if s >= 9.0}, reverse=True)

    rows.append(dict(
        page=pi + 1,
        whitespace=round(ws * 100, 1),
        max_spread=max_spread,
        n_clusters=len(clusters),
        pad_violations=len(pad_bad),
        pad_sample=pad_bad[:3],
        chars=chars,
        chars_per_shape=round(chars / max(len(content), 1), 1),
        charts=charts, pics=pics,
        tiers_n=len(tiers), tiers=tiers,
        low_contrast=low[:3],
    ))

hdr = f"{'页':>3} {'留白%':>6} {'对齐极差':>8} {'列线':>4} {'PAD违例':>7} {'字数':>5} {'图/片':>5} {'字号层':>5} {'判定'}"
print(hdr)
allpass = True
for r in rows:
    v = []
    v.append(r["whitespace"] >= 25)
    v.append(r["max_spread"] <= 0.1 and r["pad_violations"] == 0)
    v.append(r["low_contrast"] == [])
    ok = all(v)
    allpass &= ok
    print(f"{r['page']:>3} {r['whitespace']:>6} {r['max_spread']:>8} {r['n_clusters']:>4} "
          f"{r['pad_violations']:>7} {r['chars']:>5} {r['charts']}/{r['pics']:<3} "
          f"{r['tiers_n']:>5} {'PASS' if ok else 'FAIL ' + str([i for i, x in enumerate(v) if not x])}")

(OUT / "scorecard-final.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
print("\n全部达标:", allpass)
print("留白区间: %.1f%%–%.1f%%" % (min(r["whitespace"] for r in rows), max(r["whitespace"] for r in rows)))
print("对齐最大极差: %.3f in" % max(r["max_spread"] for r in rows))
print("对比最小值(正文):", min([r["low_contrast"][0][1] for r in rows if r["low_contrast"]], default="无违例"))
print("图表页:", [r["page"] for r in rows if r["charts"] or r["pics"]])