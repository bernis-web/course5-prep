#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
从「定稿文件渲染出的全页图」重新生成验收证据：
灰度版 / 缩略版 / 两张总览 contact。
避免证据图与实际交付物不一致（旧图曾带已删期次标识）。
"""
import os, glob
from PIL import Image, ImageDraw, ImageFont

BASE = r"D:\projects\course5-prep\results\stage-reports-20261102"
SRC = os.path.join(BASE, "render", "v2f")       # 定稿渲染
OUT = os.path.join(BASE, "render", "v2")        # 证据目录
GRAY = os.path.join(OUT, "gray")
THUMB = os.path.join(OUT, "thumb")
for d in (OUT, GRAY, THUMB):
    os.makedirs(d, exist_ok=True)

pages = sorted(glob.glob(os.path.join(SRC, "s*.png")))
pages = [p for p in pages if os.path.basename(p)[1:3].isdigit()]
print("页面:", len(pages))

# 1. 灰度 + 缩略
grays, thumbs = [], []
for p in pages:
    n = os.path.basename(p)
    im = Image.open(p).convert("RGB")
    g = im.convert("L").convert("RGB")
    g.save(os.path.join(GRAY, n))
    grays.append(g)
    t = im.resize((im.width // 4, im.height // 4), Image.LANCZOS)
    t.save(os.path.join(THUMB, n))
    thumbs.append(t)

# 2. 总览图
def contact(imgs, cols, pad, out_path, label=True):
    if not imgs:
        return
    w, h = imgs[0].size
    rows = (len(imgs) + cols - 1) // cols
    W = cols * w + (cols + 1) * pad
    H = rows * h + (rows + 1) * pad
    sheet = Image.new("RGB", (W, H), (232, 232, 232))
    for i, im in enumerate(imgs):
        r, c = divmod(i, cols)
        x = pad + c * (w + pad)
        y = pad + r * (h + pad)
        sheet.paste(im, (x, y))
        if label:
            d = ImageDraw.Draw(sheet)
            d.rectangle([x, y, x + 46, y + 22], fill=(20, 20, 20))
            d.text((x + 14, y + 5), "%02d" % (i + 1), fill=(255, 255, 255))
    sheet.save(out_path)
    print("写出", os.path.basename(out_path), sheet.size)

contact(thumbs, 3, 14,
        os.path.join(OUT, "_contact.png"))
gray_thumbs = [Image.open(os.path.join(GRAY, os.path.basename(p))).convert("RGB").resize(
    (thumbs[0].width, thumbs[0].height), Image.LANCZOS) for p in pages]
contact(gray_thumbs, 3, 14, os.path.join(OUT, "_contact_gray.png"))
print("完成")
