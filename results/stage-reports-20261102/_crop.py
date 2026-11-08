# -*- coding: utf-8 -*-
"""只读：把指定区域裁剪放大，便于逐字检查。输出到 _crops/。"""
import os
from PIL import Image

SRC = r"D:\projects\course5-prep\results\stage-reports-20261102\render"
OUT = r"D:\projects\course5-prep\results\stage-reports-20261102\_crops"
os.makedirs(OUT, exist_ok=True)

jobs = [
    ("s02.png", (60, 155, 470, 480), 3, "c02_col1"),
    ("s02.png", (60, 155, 1400, 480), 2, "c02_full"),
    ("s03.png", (60, 160, 1400, 360), 2, "c03_body"),
    ("s15.png", (60, 165, 1400, 330), 2, "c15_body"),
    ("s13.png", (60, 160, 1400, 450), 2, "c13_all"),
    ("s01.png", (60, 150, 1400, 700), 1, "c01_full"),
]

for name, box, scale, out in jobs:
    im = Image.open(os.path.join(SRC, name)).convert("RGB")
    c = im.crop(box)
    if scale != 1:
        c = c.resize((c.width * scale, c.height * scale), Image.LANCZOS)
    p = os.path.join(OUT, out + ".png")
    c.save(p)
    print("wrote", p, c.size)
