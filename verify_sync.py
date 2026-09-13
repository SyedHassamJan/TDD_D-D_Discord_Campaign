import re, json

with open("index.html", "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

# Check mapdata is correct
m = re.search(r'<script id="mapdata" type="application/json">(.*?)</script>', text, re.DOTALL)
if m:
    try:
        data = json.loads(m.group(1))
        print("mapdata title:", data.get("title"))
        print("mapdata w/h:", data.get("w"), data.get("h"))
        print("mapdata provinces count:", len(data.get("provinces", [])))
        for p in data.get("provinces", []):
            print(f"  Province: {p['id']} hex={p['hex']} owner={p['owner']} playable={p['playable']} adj={p.get('adj')}")
        print("mapdata factions count:", len(data.get("factions", [])))
        print("mapdata armies:", data.get("armies"))
    except Exception as e:
        print("Error parsing mapdata:", e)
else:
    print("No mapdata found!")

# Check REALM_OF
m2 = re.search(r'const REALM_OF=(\{[^;]+\});', text)
if m2:
    realm_of = json.loads(m2.group(1))
    print("\nREALM_OF:")
    for k, v in realm_of.items():
        print(f"  {k}: {v}")
else:
    print("No REALM_OF found!")

# Check START_SNAP
m3 = re.search(r'const START_SNAP=(\{.*?\});', text, re.DOTALL)
if m3:
    snap = json.loads(m3.group(1))
    print("\nSTART_SNAP.prov:", snap.get("prov"))
    print("START_SNAP.armies:", snap.get("armies"))
else:
    print("No START_SNAP found!")

# Check MAP_B64 is set
m4 = re.search(r'const MAP_B64="([^"]{1,50})', text)
if m4:
    print("\nMAP_B64 starts with:", m4.group(1)[:30], "...")
