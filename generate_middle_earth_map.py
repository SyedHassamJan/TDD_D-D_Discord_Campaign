import json
import base64
import os
import re
from PIL import Image
import numpy as np

print("Loading images...")
test_im = Image.open("map_assets_extracted/test.png").convert("RGB")
sat_im = Image.open("map_assets_extracted/Satellite-layer-Middle-earth-V2.png").convert("RGB")
hm_im = Image.open("map_assets_extracted/Heightmap-layer-Middle-earth-V2.png").convert("L")

W, H = test_im.size
print(f"Map size: W={W}, H={H}")

arr_test = np.array(test_im)
arr_hm = np.array(hm_im.resize((W, H), Image.Resampling.BILINEAR))

# Color masks
# Black impassible
c_black = (0, 0, 0)
m_black = (np.max(np.abs(arr_test - c_black), axis=2) <= 5) # clamp near black to black

# 3 Painted provinces
m_p1 = (arr_test[:,:,0] == 136) & (arr_test[:,:,1] == 0) & (arr_test[:,:,2] == 21)   # Dark Red #880015
m_p2 = (arr_test[:,:,0] == 185) & (arr_test[:,:,1] == 122) & (arr_test[:,:,2] == 87) # Brown #b97a57
m_p3 = (arr_test[:,:,0] == 237) & (arr_test[:,:,1] == 28) & (arr_test[:,:,2] == 36)  # Red #ed1c24

# Wilderness: everything else
m_wild = (~m_black) & (~m_p1) & (~m_p2) & (~m_p3)

print("Pixel counts:")
print("  Impassible / Black:", np.sum(m_black))
print("  Near Harad (P1, Dark Red):", np.sum(m_p1))
print("  Harondor (P2, Brown):", np.sum(m_p2))
print("  South Ithilien (P3, Red):", np.sum(m_p3))
print("  Wilderness:", np.sum(m_wild))

# Adjacency calculator
def get_adjacencies(masks):
    adj = {k: set() for k in masks}
    names = list(masks.keys())
    for i in range(len(names)):
        for j in range(i+1, len(names)):
            n1, n2 = names[i], names[j]
            m1, m2 = masks[n1], masks[n2]
            touch = (
                (m1[1:, :] & m2[:-1, :]).any() or
                (m1[:-1, :] & m2[1:, :]).any() or
                (m1[:, 1:] & m2[:, :-1]).any() or
                (m1[:, :-1] & m2[:, 1:]).any()
            )
            if touch:
                adj[n1].add(n2)
                adj[n2].add(n1)
    return {k: sorted(list(v)) for k, v in adj.items()}

prov_masks = {
    "Near Harad": m_p1,
    "Harondor": m_p2,
    "South Ithilien": m_p3,
    "Wilderness": m_wild
}

adj = get_adjacencies(prov_masks)
print("Adjacencies:", adj)

# Check coastal (touches black / water)
def is_coastal(m, m_water):
    return bool(
        (m[1:, :] & m_water[:-1, :]).any() or
        (m[:-1, :] & m_water[1:, :]).any() or
        (m[:, 1:] & m_water[:, :-1]).any() or
        (m[:, :-1] & m_water[:, 1:]).any()
    )

# Compute centroid and elevation
provinces_data = []

defs = [
    {
        "id": "Near Harad",
        "modern": "Near Harad",
        "hex": "#880015",
        "playable": True,
        "owner": "Lostladen Tribes",
        "tier": 2,
        "terrain": "plains",
        "value": 1100,
        "move": 2,
        "garrison": 2000,
        "bld": ["blacksmith", "stables"],
        "mask": m_p1
    },
    {
        "id": "Harondor",
        "modern": "Harondor",
        "hex": "#b97a57",
        "playable": True,
        "owner": "Mordor",
        "tier": 2,
        "terrain": "hills",
        "value": 1400,
        "move": 2,
        "garrison": 2500,
        "bld": ["barracks", "walls"],
        "mask": m_p2
    },
    {
        "id": "South Ithilien",
        "modern": "South Ithilien",
        "hex": "#ed1c24",
        "playable": True,
        "owner": "Gondor",
        "tier": 2,
        "terrain": "forest",
        "value": 1600,
        "move": 2,
        "garrison": 3000,
        "bld": ["archery_range", "walls"],
        "mask": m_p3
    },
    {
        "id": "Wilderness",
        "modern": "Middle-earth Wilds",
        "hex": "#2d3a21",
        "playable": False,
        "owner": None,
        "tier": 0,
        "terrain": "wilderness",
        "value": 0,
        "move": 9,
        "garrison": 0,
        "bld": [],
        "mask": m_wild
    }
]

for d in defs:
    m = d["mask"]
    ys, xs = np.where(m)
    px = int(len(xs))
    cx = float(np.round(xs.mean(), 1)) if px > 0 else 0.0
    cy = float(np.round(ys.mean(), 1)) if px > 0 else 0.0
    elev = int(np.round(arr_hm[ys, xs].mean())) if px > 0 else 100
    coastal = is_coastal(m, m_black)

    prov_obj = {
        "id": d["id"],
        "modern": d["modern"],
        "hex": d["hex"],
        "playable": d["playable"],
        "cx": cx,
        "cy": cy,
        "px": px,
        "coastal": coastal,
        "tier": d["tier"],
        "terrain": d["terrain"],
        "value": d["value"],
        "move": d["move"],
        "garrison": d["garrison"],
        "owner": d["owner"],
        "adj": adj.get(d["id"], []),
        "siege": None,
        "elev": elev,
        "bld": d["bld"],
        "upg": None,
        "raid": None,
        "occ": None
    }
    provinces_data.append(prov_obj)
    print(f"Province {d['id']}: cx={cx}, cy={cy}, px={px}, coastal={coastal}, elev={elev}, adj={adj.get(d['id'])}")

# Now generate clean new map_b64.png
out_map = np.zeros((H, W, 3), dtype=np.uint8)
out_map[m_black] = [0, 0, 0]
out_map[m_wild] = [45, 58, 33]   # #2d3a21
out_map[m_p1] = [136, 0, 21]     # #880015
out_map[m_p2] = [185, 122, 87]   # #b97a57
out_map[m_p3] = [237, 28, 36]    # #ed1c24

map_png_path = "map_assets_extracted/map_b64.png"
Image.fromarray(out_map).save(map_png_path, format="PNG", optimize=True)
print(f"Saved {map_png_path}, file size: {os.path.getsize(map_png_path)} bytes")

# Generate terrain_b64.jpg
terrain_jpg_path = "map_assets_extracted/terrain_b64.jpg"
# Resize satellite layer to half-res (1678, 1343) for fast loading, quality 82
sat_resized = sat_im.resize((W // 2, H // 2), Image.Resampling.LANCZOS)
sat_resized.save(terrain_jpg_path, format="JPEG", quality=82, optimize=True)
print(f"Saved {terrain_jpg_path}, file size: {os.path.getsize(terrain_jpg_path)} bytes")

# Generate shade_b64.jpg
shade_jpg_path = "map_assets_extracted/shade_b64.jpg"
# Heightmap resized to half-res (1678, 1343), quality 82
hm_resized = hm_im.resize((W // 2, H // 2), Image.Resampling.BILINEAR)
hm_resized.save(shade_jpg_path, format="JPEG", quality=82, optimize=True)
print(f"Saved {shade_jpg_path}, file size: {os.path.getsize(shade_jpg_path)} bytes")

# Update campaign.json
with open("campaign.json", "r", encoding="utf-8") as f:
    camp = json.load(f)

camp["title"] = "Middle-earth Campaign"
camp["w"] = W
camp["h"] = H
camp["sea"] = "#162838"
camp["rivers"] = []
camp["crossings"] = []
camp["armies"] = []
camp["provinces"] = provinces_data

# Update faction capitals to match their provinces
for fac in camp.get("factions", []):
    if fac["id"] == "Lostladen Tribes":
        fac["capital"] = "Near Harad"
    elif fac["id"] == "Mordor":
        fac["capital"] = "Harondor"
    elif fac["id"] == "Gondor":
        fac["capital"] = "South Ithilien"

with open("campaign.json", "w", encoding="utf-8") as f:
    json.dump(camp, f, indent=2)
print("Updated campaign.json successfully!")
