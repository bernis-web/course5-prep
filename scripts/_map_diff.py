import csv, collections, json, re
p1 = r"D:\projects\course5-prep\config\heart-celltype-map-v1.tsv"
p2 = r"D:\projects\course5-prep\config\heart-celltype-map-v2.tsv"
p3 = r"D:\projects\course5-prep\config\heart-celltype-map-v2-proposal.tsv"

def load(p):
    with open(p, encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))

v1, v2, vp = load(p1), load(p2), load(p3)
print("rows v1/v2/proposal:", len(v1), len(v2), len(vp))
print("v2 status:", dict(collections.Counter(r["mapping_status"] for r in v2)))
print("v2 coarse:", dict(collections.Counter(r["coarse_level"] for r in v2)))
print("v2 species:", dict(collections.Counter(r["source_species"] for r in v2)))
print("v1 status:", dict(collections.Counter(r["mapping_status"] for r in v1)))
# 差异
k = lambda r: (r["source_species"], r["source_label"])
m1 = {k(r): r for r in v1}
m2 = {k(r): r for r in v2}
diff = [kk for kk in m2 if kk in m1 and (m1[kk]["coarse_level"] != m2[kk]["coarse_level"] or m1[kk]["fine_mapped_label"] != m2[kk]["fine_mapped_label"] or m1[kk]["mapping_status"] != m2[kk]["mapping_status"])]
print("changed rows:", len(diff))
for kk in diff:
    print("  ", kk, "| v1:", m1[kk]["coarse_level"], m1[kk]["fine_mapped_label"], m1[kk]["mapping_status"],
          "| v2:", m2[kk]["coarse_level"], m2[kk]["fine_mapped_label"], m2[kk]["mapping_status"])
only1 = [x for x in m1 if x not in m2]
only2 = [x for x in m2 if x not in m1]
print("only v1:", only1)
print("only v2:", only2)
print("Orthers rows v1:", [(r["source_species"], r["coarse_level"], r["mapping_status"]) for r in v1 if "rther" in r["source_label"]])
print("Orthers rows v2:", [(r["source_species"], r["coarse_level"], r["mapping_status"]) for r in v2 if "rther" in r["source_label"]])