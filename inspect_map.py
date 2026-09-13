import json
import re

with open("campaign.json", "r", encoding="utf-8") as f:
    camp = json.load(f)

print("Title:", camp.get("title"))
print("Dimensions: w=", camp.get("w"), "h=", camp.get("h"))
print("Sea:", camp.get("sea"))
print("Factions count:", len(camp.get("factions", [])))
for fac in camp.get("factions", []):
    print("  Faction:", fac)

provinces = camp.get("provinces", [])
print(f"Provinces total: {len(provinces)}")
if provinces:
    print("Sample province 0:", json.dumps(provinces[0], indent=2))
    print("Sample province 1:", json.dumps(provinces[1], indent=2))

# Check index.html for map scripts and layers
with open("index.html", "r", encoding="utf-8", errors="ignore") as f:
    head = f.read(50000)

for tag in ["mapdata", "codexdata"]:
    pos = head.find(tag)
    print(f"Tag {tag} found at: {pos}")

# Check image variables
img_vars = re.findall(r'const\s+([A-Za-z0-9_]*B64[A-Za-z0-9_]*)\s*=', head)
print("Base64 constants found:", img_vars)
