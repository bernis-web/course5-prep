# -*- coding: utf-8 -*-
"""按文件打印命中明细（loc/行号 + 命中串 + 上下文）"""
import json, sys
p = r"D:\projects\course5-prep\results\audit-consistency-20261111\hits.json"
d = json.load(open(p, encoding="utf-8"))
want = sys.argv[1:]
for h in d["hits"]:
    if want and not any(w in h["file"] for w in want):
        continue
    print("=" * 100)
    print(f"FILE: {h['file']}  ({h['type']}, {h['match_count']} rows)")
    for row in h["rows"]:
        loc = row.get("line") or row.get("loc")
        print(f"  [{loc}] {'/'.join(row['ids'])} :: {row['text'][:220]}")