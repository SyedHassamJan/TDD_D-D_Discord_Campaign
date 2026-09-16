"""
Master Fast Sync Pipeline (sync_all.py)
Automates map tiles, factions, unit rosters, and asset separation in 3 seconds.
"""
import os
import sys
import re
import json
import base64
import hashlib
import io
from PIL import Image
import numpy as np

# Set standard encoding for terminal output
sys.stdout.reconfigure(encoding='utf-8')

print("=" * 60)
print("  MASTER SYNC PIPELINE: AUTO-DETECT & SYNC")
print("=" * 60)

FACTIONS_DIR = "Faction Icons"
UNITS_DIR = "Unit Icons"
ASSETS_DIR = "assets"
MAP_EXTRACTED_DIR = "map_assets_extracted"

os.makedirs(ASSETS_DIR, exist_ok=True)

# -------------------------------------------------------------
# 1. AUTO-DETECT FACTIONS & BUILD EMBLEMS.JS
# -------------------------------------------------------------
print("\n[1/4] Scanning Faction Icons...")
faction_emblems = {}
factions_list = []

# Standard color palette for Middle Earth factions if not preset
COLOR_MAP = {
    "Rohan": "#C5A059",
    "Gondor": "#4682B4",
    "Woodland Realm": "#2E7D32",
    "Mordor": "#8B0000",
    "Lothlorien": "#D4AF37",
    "Imraldris": "#4682B4",
    "Lostladen Tribes": "#D27D2D",
    "Dale": "#C8922A",
    "Dol Guldur": "#4A154B",
    "DolGulDur": "#4A154B",
    "Dorwinion": "#9C27B0",
    "Dorvinion": "#9C27B0",
    "Dunland": "#795548",
    "Goblins": "#388E3C",
    "Harad": "#E65100",
    "Isengard": "#F5F5F5",
    "Lindon": "#81C784",
    "Mahud": "#BF360C",
    "Rhun": "#B71C1C",
    "Umbar": "#00838F"
}

hash_to_b64 = {}
name_to_hash = {}

if os.path.exists(FACTIONS_DIR):
    for fn in sorted(os.listdir(FACTIONS_DIR)):
        if fn.lower().endswith(".png"):
            fac_name = os.path.splitext(fn)[0]
            file_path = os.path.join(FACTIONS_DIR, fn)
            
            # Compress to 96x96 PNG (keeps transparency for emblems)
            img = Image.open(file_path).convert("RGBA")
            img = img.resize((96, 96), Image.Resampling.LANCZOS)
            buf = io.BytesIO()
            img.save(buf, format="PNG", optimize=True)
            raw = buf.getvalue()
            
            h = hashlib.md5(raw).hexdigest()
            if h not in hash_to_b64:
                hash_to_b64[h] = base64.b64encode(raw).decode("ascii")
            name_to_hash[fac_name] = h
            
            color = COLOR_MAP.get(fac_name, "#A0A0A0")
            factions_list.append({
                "id": fac_name,
                "name": fac_name,
                "color": color,
                "treasury": 5000,
                "capital": "",
                "zeal": 6
            })
            print(f"  + Registered faction: {fac_name} ({color})")

# Write deduplicated emblems.js — one base64 var per unique image, aliases reference same var
print(f"Writing {ASSETS_DIR}/emblems.js ({len(hash_to_b64)} unique images, {len(name_to_hash)} factions)...")
hash_to_var = {}
emb_lines = ['"use strict";']
for i, (h, b64) in enumerate(hash_to_b64.items()):
    varname = f"_EMB_{i}"
    emb_lines.append(f'const {varname}="data:image/png;base64,{b64}";')
    hash_to_var[h] = varname
emb_lines.append("const EMBLEMS={")
for name, h in name_to_hash.items():
    var = hash_to_var[h]
    emb_lines.append(f'  "{name}":{var},')
    emb_lines.append(f'  "{name.lower()}":{var},')
emb_lines.append("};")
with open(os.path.join(ASSETS_DIR, "emblems.js"), "w", encoding="utf-8") as f:
    f.write("\n".join(emb_lines))
print(f"  emblems.js: {os.path.getsize(os.path.join(ASSETS_DIR, 'emblems.js'))/1024:.0f} KB")

# -------------------------------------------------------------
# 2. AUTO-DETECT UNITS & BUILD CODEX_ICONS.JS & CODEX DATA
# -------------------------------------------------------------
print("\n[2/4] Scanning Unit Icons & Building Codex...")
codex_units = []
codex_icons = {}

def deduce_stats(fac_id, unit_name, filename):
    fn = filename.lower()
    nm = unit_name.lower()
    cat, cat_n = "infantry", "Infantry"
    u_cls, cls_n = "inf_mel", "Melee Infantry"
    tier = "2"
    men, cost, upkeep = 120, 600, 180
    is_mis = False
    is_mou = False

    if any(h in fn or h in nm for h in ['king', 'legolas', 'elrond', 'haldir', 'gothmog', 'the nine', 'eorl', 'lord', 'hero']):
        u_cls, cls_n = "com", "Command"
        tier = "4"
        men, cost, upkeep = 60, 1400, 420
        if any(m in fn or m in nm for m in ['rider', 'horse', 'mounted']):
            cat, cat_n = "cavalry", "Cavalry"
            is_mou = True
    elif any(c in fn or c in nm for c in ['rider', 'horse', 'cavalry', 'mounted', 'knight', 'eored', 'lancer']):
        cat, cat_n = "cavalry", "Cavalry"
        is_mou = True
        if any(m in fn or m in nm for m in ['archer', 'skirmish', 'bow']):
            u_cls, cls_n = "cav_mis", "Missile Cavalry"
            is_mis = True
            men, cost, upkeep = 80, 850, 255
        else:
            u_cls, cls_n = "cav_shk", "Shock Cavalry"
            men, cost, upkeep = 80, 950, 285
    elif any(m in fn or m in nm for m in ['archer', 'bow', 'marksman', 'skirmish', 'tracker', 'ranger']):
        u_cls, cls_n = "inf_mis", "Missile Infantry"
        is_mis = True
        men, cost, upkeep = 120, 650, 195
    elif any(p in fn or p in nm for p in ['pike', 'phalanx']):
        u_cls, cls_n = "inf_pik", "Pike Infantry"
        men, cost, upkeep = 150, 600, 180
    elif any(s in fn or s in nm for s in ['spear', 'warden', 'guard', 'sentinel']):
        u_cls, cls_n = "inf_spr", "Spear Infantry"
        men, cost, upkeep = 140, 550, 165

    return {
        "cat": cat, "cat_n": cat_n, "cls": u_cls, "cls_n": cls_n,
        "tier": tier, "men": men, "cost": cost, "upkeep": upkeep,
        "is_mis": is_mis, "is_mou": is_mou
    }

if os.path.exists(UNITS_DIR):
    for fac_dir in sorted(os.listdir(UNITS_DIR)):
        fac_path = os.path.join(UNITS_DIR, fac_dir)
        if not os.path.isdir(fac_path):
            continue
        unit_files = [f for f in os.listdir(fac_path) if f.lower().endswith(".png")]
        for u_fn in unit_files:
            clean_name = re.sub(r'(?i)\.png$', '', u_fn)
            clean_name = re.sub(r'(?i)_UC\d*$', '', clean_name)
            clean_name = re.sub(r'^\d+_', '', clean_name).replace('_', ' ').replace('-', ' ').strip().title()
            u_key = f"{fac_dir.lower().replace(' ', '_')}_{re.sub(r'[^a-zA-Z0-9]+', '_', clean_name.lower())}"
            
            u_path = os.path.join(fac_path, u_fn)
            # Compress unit icon to 64x64 JPEG for fast loading
            img = Image.open(u_path).convert("RGB")
            img = img.resize((64, 64), Image.Resampling.LANCZOS)
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=75, optimize=True)
            u_b64 = base64.b64encode(buf.getvalue()).decode("ascii")
            codex_icons[u_key] = f"data:image/jpeg;base64,{u_b64}"
            
            st = deduce_stats(fac_dir, clean_name, u_fn)
            codex_units.append({
                "faction": fac_dir,
                "unit_key": u_key,
                "name": clean_name,
                "category": st["cat"],
                "category_name": st["cat_n"],
                "class": st["cls"],
                "class_name": st["cls_n"],
                "tier": st["tier"],
                "men": st["men"],
                "cost": st["cost"],
                "upkeep": st["upkeep"],
                "missile": st["is_mis"],
                "mounted": st["is_mou"]
            })
        print(f"  + Roster for '{fac_dir}': {len(unit_files)} units processed.")

print(f"Writing {ASSETS_DIR}/codex_icons.js ({len(codex_icons)} icons)...")
with open(os.path.join(ASSETS_DIR, "codex_icons.js"), "w", encoding="utf-8") as f:
    f.write('"use strict";\nconst CODEX_ICONS = {\n')
    for k, v in codex_icons.items():
        f.write(f'  "{k}": "{v}",\n')
    f.write('};\n')

# -------------------------------------------------------------
# 3. AUTO-DETECT TILES & SYNC CAMPAIGN.JSON
# -------------------------------------------------------------
print("\n[3/4] Checking Province Map & Tiles...")
map_png = os.path.join(MAP_EXTRACTED_DIR, "map_b64.png")
if not os.path.exists(map_png):
    # fallback to test.png if map_b64.png doesn't exist
    map_png = os.path.join(MAP_EXTRACTED_DIR, "test.png")

if os.path.exists(map_png):
    print(f"  Reading map image from {map_png}...")
    im = Image.open(map_png).convert("RGB")
    W, H = im.size
    arr = np.array(im)
    
    # Check existing campaign.json to preserve any existing custom names
    camp = {}
    if os.path.exists("campaign.json"):
        with open("campaign.json", "r", encoding="utf-8") as f:
            camp = json.load(f)
    
    existing_provinces = {p.get("hex", "").lower(): p for p in camp.get("provinces", [])}
    
    # Find unique colors
    colors, counts = np.unique(arr.reshape(-1, 3), axis=0, return_counts=True)
    detected_provinces = []
    
    # Exclude black/near-black impassable lines (<= 15 RGB)
    tile_id = 1
    for c, cnt in zip(colors, counts):
        if np.max(c) <= 15:
            continue # Impassable borders / ocean
        if cnt < 200:
            continue # Noise / antialiasing speckles
            
        hex_c = "#{:02x}{:02x}{:02x}".format(*c).lower()
        
        # Check if already defined
        if hex_c in existing_provinces:
            p = existing_provinces[hex_c]
        else:
            p = {
                "id": f"Province_{tile_id}",
                "modern": f"Province {tile_id}",
                "hex": hex_c,
                "playable": True,
                "owner": "", # Empty = Neutral Gray
                "tier": 2,
                "terrain": "plains",
                "value": 1000,
                "move": 2,
                "garrison": 1500,
                "bld": [],
                "adj": []
            }
            tile_id += 1
            
        detected_provinces.append(p)
        
    print(f"  Detected {len(detected_provinces)} playable tiles (all unassigned start as neutral gray)!")
    
    camp["w"] = W
    camp["h"] = H
    camp["provinces"] = detected_provinces
    if factions_list:
        camp["factions"] = factions_list
        
    with open("campaign.json", "w", encoding="utf-8") as f:
        json.dump(camp, f, indent=2, ensure_ascii=False)
    print("  Saved updated campaign.json.")
    
    # Also update map_assets.js
    with open(map_png, "rb") as f:
        new_map_b64 = base64.b64encode(f.read()).decode("ascii")
        
    # Auto-detect satellite / terrain layer
    terr_b64 = ""
    for candidate in ["terrain_b64.jpg", "terrain_b64.png", "Satellite-layer-Middle-earth-V2.png", "Satellite-layer-Middle-earth-V2.jpg"]:
        c_path = os.path.join(MAP_EXTRACTED_DIR, candidate)
        if os.path.exists(c_path):
            # If PNG, convert to high-quality compressed JPEG for lightning-fast loading
            if candidate.lower().endswith(".png"):
                opt_jpg = os.path.join(MAP_EXTRACTED_DIR, "terrain_b64.jpg")
                Image.open(c_path).convert("RGB").save(opt_jpg, quality=85)
                c_path = opt_jpg
            with open(c_path, "rb") as f:
                terr_b64 = base64.b64encode(f.read()).decode("ascii")
            print(f"  Loaded terrain layer from {candidate}.")
            break

    # Auto-detect heightmap / shading layer
    shade_b64 = ""
    for candidate in ["shade_b64.jpg", "shade_b64.png", "Heightmap-layer-Middle-earth-V2.png", "Heightmap-layer-Middle-earth-V2.jpg"]:
        c_path = os.path.join(MAP_EXTRACTED_DIR, candidate)
        if os.path.exists(c_path):
            if candidate.lower().endswith(".png"):
                opt_jpg = os.path.join(MAP_EXTRACTED_DIR, "shade_b64.jpg")
                Image.open(c_path).convert("L").save(opt_jpg, quality=85)
                c_path = opt_jpg
            with open(c_path, "rb") as f:
                shade_b64 = base64.b64encode(f.read()).decode("ascii")
            print(f"  Loaded heightmap/shade layer from {candidate}.")
            break

    with open(os.path.join(ASSETS_DIR, "map_assets.js"), "w", encoding="utf-8") as f:
        f.write('"use strict";\n')
        f.write(f'const MAP_B64="{new_map_b64}";\n')
        if terr_b64:
            f.write(f'const TERRAIN_B64="{terr_b64}";\n')
        if shade_b64:
            f.write(f'const SHADE_B64="{shade_b64}";\n')
    print("  Updated assets/map_assets.js.")

# -------------------------------------------------------------
# 4. INJECT COMPACT JSON INTO INDEX.HTML & GM.HTML
# -------------------------------------------------------------
print("\n[4/4] Syncing index.html and gm.html...")

compact_mapdata = json.dumps(camp, separators=(",", ":"), ensure_ascii=False)
codex_obj = {
    "campaign": "Middle-earth",
    "cap": 20,
    "factions": [{"name": f["id"]} for f in factions_list],
    "units": codex_units
}
compact_codex = json.dumps(codex_obj, separators=(",", ":"), ensure_ascii=False)

for fn in ["index.html", "gm.html"]:
    if not os.path.exists(fn):
        continue
    with open(fn, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()
        
    # Replace mapdata
    html = re.sub(
        r'<script id="mapdata" type="application/json">.*?</script>',
        f'<script id="mapdata" type="application/json">{compact_mapdata}</script>',
        html,
        flags=re.DOTALL
    )
    
    # Replace codexdata
    html = re.sub(
        r'<script id="codexdata" type="application/json">.*?</script>',
        f'<script id="codexdata" type="application/json">{compact_codex}</script>',
        html,
        flags=re.DOTALL
    )
    
    with open(fn, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  Synced {fn} successfully.")

print("\n" + "=" * 60)
print("  SYNC COMPLETE! ALL TILES & FACTIONS ARE READY.")
print("  Open gm.html to paint territories with the claim brush.")
print("=" * 60)
