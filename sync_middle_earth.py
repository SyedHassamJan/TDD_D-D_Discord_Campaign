"""
Full Middle-earth map sync script.
Updates index.html and gm.html with:
  - New MAP_B64 (province color map from test.png)
  - New TERRAIN_B64 (satellite layer as terrain texture)
  - New SHADE_B64 (heightmap as relief shading)
  - New mapdata (campaign.json, replaces old Reconquista data)
  - START_SNAP cleared (remove historical start positions)
  - Map dimensions updated to match new test.png size
  - REALM_OF updated for the 3 new factions
"""
import base64
import re
import json
import os

def b64_img(path, mime="image/png"):
    with open(path, "rb") as f:
        return f"data:{mime};base64," + base64.b64encode(f.read()).decode("ascii")

def raw_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")

print("Encoding assets...")
MAP_B64_VAL    = raw_b64("map_assets_extracted/map_b64.png")
TERRAIN_B64_VAL = raw_b64("map_assets_extracted/terrain_b64.jpg")
SHADE_B64_VAL   = raw_b64("map_assets_extracted/shade_b64.jpg")

print(f"  MAP_B64    length: {len(MAP_B64_VAL)}")
print(f"  TERRAIN_B64 length: {len(TERRAIN_B64_VAL)}")
print(f"  SHADE_B64   length: {len(SHADE_B64_VAL)}")

# Load updated campaign.json
with open("campaign.json", "r", encoding="utf-8") as f:
    camp = json.load(f)

# New mapdata JSON string (compact)
new_mapdata = json.dumps(camp, separators=(",", ":"), ensure_ascii=False)

# New REALM_OF: maps faction IDs and aliases to canonical realm IDs
NEW_REALM_OF = {
    # Gondor
    "Gondor": "Gondor",
    "South Ithilien": "Gondor",
    # Mordor
    "Mordor": "Mordor",
    "Harondor": "Mordor",
    # Lostladen Tribes
    "Lostladen Tribes": "Lostladen Tribes",
    "Near Harad": "Lostladen Tribes",
    "Lostladen": "Lostladen Tribes",
    "Harad": "Lostladen Tribes",
    # Other existing factions (no territory)
    "Dale": "Dale",
    "Dol Guldur": "Dol Guldur",
    "Dorwinion": "Dorwinion",
    "Rhun": "Rhun",
    "Rhûn": "Rhun",
    "Goblins": "Goblins",
    "Rohan": "Rohan",
    "Woodland Realm": "Woodland Realm",
    "Lothlorien": "Lothlorien",
    "Imraldris": "Imraldris",
}

realm_of_js = "const REALM_OF=" + json.dumps(NEW_REALM_OF, separators=(",", ":")) + ";"

# New START_SNAP: just empty provinces and armies
NEW_START_SNAP = {
    "prov": {
        "Near Harad": ["Lostladen Tribes", "", "", 0],
        "Harondor": ["Mordor", "", "", 0],
        "South Ithilien": ["Gondor", "", "", 0],
    },
    "armies": []
}
new_snap_js = "const START_SNAP=" + json.dumps(NEW_START_SNAP, separators=(",", ":")) + ";"

def sync_file(filename):
    if not os.path.exists(filename):
        print(f"  Skipping {filename} (not found)")
        return

    with open(filename, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    orig_len = len(content)
    changes = []

    # 1. Replace MAP_B64
    old_map_b64_match = re.search(r'const MAP_B64="[^"]*";', content)
    if old_map_b64_match:
        content = content.replace(old_map_b64_match.group(0), f'const MAP_B64="{MAP_B64_VAL}";')
        changes.append("MAP_B64")

    # 2. Replace TERRAIN_B64
    old_terrain_match = re.search(r'const TERRAIN_B64="[^"]*";', content)
    if old_terrain_match:
        content = content.replace(old_terrain_match.group(0), f'const TERRAIN_B64="{TERRAIN_B64_VAL}";')
        changes.append("TERRAIN_B64")

    # 3. Replace SHADE_B64
    old_shade_match = re.search(r'const SHADE_B64="[^"]*";', content)
    if old_shade_match:
        content = content.replace(old_shade_match.group(0), f'const SHADE_B64="{SHADE_B64_VAL}";')
        changes.append("SHADE_B64")

    # 4. Replace mapdata script block
    old_mapdata_match = re.search(r'<script id="mapdata" type="application/json">.*?</script>', content, re.DOTALL)
    if old_mapdata_match:
        content = content.replace(
            old_mapdata_match.group(0),
            f'<script id="mapdata" type="application/json">{new_mapdata}</script>'
        )
        changes.append("mapdata")

    # 5. Replace REALM_OF
    old_realm_match = re.search(r'const REALM_OF=\{[^;]+\};', content, re.DOTALL)
    if old_realm_match:
        content = content.replace(old_realm_match.group(0), realm_of_js)
        changes.append("REALM_OF")

    # 6. Replace START_SNAP
    old_snap_match = re.search(r'const START_SNAP=\{.*?\};', content, re.DOTALL)
    if old_snap_match:
        content = content.replace(old_snap_match.group(0), new_snap_js)
        changes.append("START_SNAP")

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"  {filename}: updated {changes}, {orig_len} -> {len(content)} bytes")

print("Syncing index.html...")
sync_file("index.html")

print("Syncing gm.html...")
sync_file("gm.html")

print("\nAll done!")
