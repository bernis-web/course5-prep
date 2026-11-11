# -*- coding: utf-8 -*-
import re, zipfile, sys

p = sys.argv[1] if len(sys.argv) > 1 else r"D:\projects\course5-prep\deliverables\课题5-汇报-v5-20261111.pptx"
z = zipfile.ZipFile(p)
for name in z.namelist():
    if not re.match(r"ppt/charts/chart\d+\.xml$", name):
        continue
    x = z.read(name).decode("utf-8")
    print("=" * 70, name)
    # 系列名
    for m in re.finditer(r"<c:ser>.*?</c:ser>", x, re.S):
        blk = m.group(0)
        nm = re.search(r"<c:tx>.*?<c:v>(.*?)</c:v>", blk, re.S)
        cats = re.findall(r"<c:pt idx=\"\d+\"><c:v>(.*?)</c:v></c:pt>", blk, re.S)
        print("  SERIES:", nm.group(1) if nm else "?", "->", cats[:20])
    # 类别
    for m in re.finditer(r"<c:cat>(.*?)</c:cat>", x, re.S):
        cs = re.findall(r"<c:pt idx=\"\d+\"><c:v>(.*?)</c:v></c:pt>", m.group(1), re.S)
        if cs:
            print("  CATEGORIES:", cs)
            break