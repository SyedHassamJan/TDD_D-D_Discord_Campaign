import re
import json
import os

with open("campaign.json", "r", encoding="utf-8") as f:
    camp = json.load(f)

# Compact mapdata
compact_mapdata = json.dumps(camp, separators=(",", ":"), ensure_ascii=False)

# Build START_SNAP
snap_prov = {}
for p in camp.get("provinces", []):
    if not p.get("playable"):
        continue
    occ_by = p.get("occ", {}).get("by", "") if p.get("occ") else ""
    siege_by = p.get("siege", {}).get("by", "") if p.get("siege") else ""
    snap_prov[p["id"]] = [p.get("owner") or "", occ_by, siege_by, p.get("tier", 0)]

snap_armies = []
for a in camp.get("armies", []):
    snap_armies.append([
        a.get("name", ""),
        a.get("faction", ""),
        a.get("at", ""),
        int(a.get("men", 0)),
        1 if a.get("fort") else 0
    ])

snap_js = "const START_SNAP=" + json.dumps({"prov": snap_prov, "armies": snap_armies}, separators=(",", ":"), ensure_ascii=False) + ";"

for fn in ["index.html", "gm.html"]:
    if not os.path.exists(fn):
        continue
    with open(fn, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Update mapdata script
    html = re.sub(
        r'<script id="mapdata" type="application/json">.*?</script>',
        f'<script id="mapdata" type="application/json">{compact_mapdata}</script>',
        html,
        flags=re.DOTALL
    )

    # 2. Update START_SNAP
    html = re.sub(
        r'const START_SNAP\s*=\s*\{.*?\};',
        snap_js,
        html,
        flags=re.DOTALL
    )

    # 3. Allow x.status === 0 for file:// pull if responseText is present
    html = html.replace(
        'if(x.status===200&&x.responseText)',
        'if((x.status===200||(x.status===0&&x.responseText))&&x.responseText)'
    )

    with open(fn, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Successfully synced {fn}")

print("Done! Campaign map data and starting snapshots updated.")
