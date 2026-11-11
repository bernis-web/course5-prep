import json, sys
p = r"D:\projects\course5-prep\results\bootstrap-20261030\saturn_convention_mapv2.json"
d = json.load(open(p, encoding="utf-8"))

def brief(o, pre="", depth=0):
    if depth > 3:
        return
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(v, dict):
                print(f"{pre}/{k}  (dict keys={list(v.keys())[:12]})")
                brief(v, pre + "/" + k, depth + 1)
            elif isinstance(v, list):
                print(f"{pre}/{k}  (list len={len(v)})")
                if v and not isinstance(v[0], (dict, list)):
                    print(f"    -> {v[:12]}")
                elif v:
                    brief(v[0], pre + "/" + k + "[0]", depth + 1)
            else:
                print(f"{pre}/{k} = {v}")

print("TOP KEYS:", list(d.keys()))
brief(d)