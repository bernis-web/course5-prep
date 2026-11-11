# -*- coding: utf-8 -*-
"""全仓 pptx 图表缓存扫描：python-pptx 读不到缓存，只能直接解 chart XML。

目的：找出历史幻灯里**仍然排在图表里**的作废数字（0.65 / 0.4560 / 0.4147 / 459 等），
因为这些缓存不会随正文修订而更新，是文档一致性最容易漏的一片。
"""
import re
import zipfile
from pathlib import Path

ROOT = Path(r"D:\projects\course5-prep")
STALE = {
    "0.6500": "错口径 SATURN 鼠→斑马鱼", "0.6510": "错口径 SATURN 斑马鱼→鼠",
    "0.4560": "公平口径 SATURN", "0.4588": "公平口径 SATURN",
    "0.4147": "v1 映射 SATURN accuracy", "0.4010": "v1 映射 SATURN accuracy",
    "0.2479": "v1 映射 SATURN accuracy", "0.4021": "v1 映射 SATURN accuracy",
    "0.1269": "第 2.5 代 SATURN", "0.1640": "第 2.5 代 SATURN",
    "0.3658": "第 2.5 代 SATURN", "0.3563": "第 2.5 代 SATURN",
    "0.1654": "v1 冻结 oPCA", "0.1512": "v1 冻结 oPCA",
    "0.2177": "v1 冻结 oPCA", "0.4405": "v1 冻结 oPCA",
    "0.0428": "虚高量", "0.1882": "虚高量", "0.1940": "虚高量",
    "459": "旧分母", "1309": "旧分母",
}

rows = []
for pptx in sorted(ROOT.rglob("*.pptx")):
    if "~$" in pptx.name or ".bak" in pptx.name:
        continue
    try:
        z = zipfile.ZipFile(pptx)
    except Exception as e:
        rows.append((pptx, "打不开", str(e)[:40], []))
        continue
    charts = [n for n in z.namelist() if re.match(r"ppt/charts/chart\d+\.xml$", n)]
    if not charts:
        continue
    for ch in charts:
        x = z.read(ch).decode("utf-8", errors="ignore")
        vals = re.findall(r"<c:v>(-?[0-9.]+)</c:v>", x)
        hits = sorted({v for v in vals if v in STALE})
        if hits:
            rows.append((pptx.relative_to(ROOT), ch, f"{len(vals)} 个缓存值", hits))

print(f"=== 命中 {len(rows)} 个图表 ===\n")
for p, ch, info, hits in rows:
    print(f"{p}  [{ch}]  {info}")
    for h in hits:
        print(f"    {h}  ← {STALE[h]}")
print("\n判定规则：命中不等于错——若该页明确标注「旧/错口径」用于对照，属正常；")
print("未标注而在正文当作现值的，必须重出该页。")