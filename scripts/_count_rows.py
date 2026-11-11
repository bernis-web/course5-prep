# -*- coding: utf-8 -*-
p = r"D:\projects\course5-prep\docs\reports\audit-consistency-20261111.md"
lines = open(p, encoding="utf-8").read().splitlines()
i2 = next(i for i, l in enumerate(lines) if l.startswith("### 1.2"))
i3 = next(i for i, l in enumerate(lines) if l.startswith("### 1.3"))
sec = lines[i2:i3]
rows = [l for l in sec if l.startswith("| ") and "`" in l]
print("1.2 rows:", len(rows))
i1 = next(i for i, l in enumerate(lines) if l.startswith("### 1.1"))
s1 = lines[i1:i2]
r1 = [l for l in s1 if l.startswith("| ") and l.count("|") >= 6]
print("1.1 rows (excl header):", len(r1) - 2)
i4 = next(i for i, l in enumerate(lines) if l.startswith("### 1.3"))
i_end = next(i for i, l in enumerate(lines) if l.startswith("## 二"))
print("1.3 rows:", len([l for l in lines[i4:i_end] if l.startswith("| ") and "`" in l]))
print("total lines:", len(lines))