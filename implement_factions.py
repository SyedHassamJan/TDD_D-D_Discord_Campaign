import os
import json
import base64
import re
import subprocess
import sys

print("=== STARTING FACTION AND ROSTER INJECTION ===")

# 1. Configuration for new factions
NEW_FACTIONS = [
    {
        "id": "Rohan",
        "name": "Rohan",
        "color": "#C5A059",
        "treasury": 5000,
        "capital": "Edoras",
        "zeal": 6,
        "folder": "Rohan",
        "emblem_file": "Faction Icons/Rohan.png",
        "aliases": ["Rohan", "rohan"]
    },
    {
        "id": "Woodland Realm",
        "name": "Woodland Realm",
        "color": "#2E7D32",
        "treasury": 5000,
        "capital": "Thranduil's Halls",
        "zeal": 5,
        "folder": "Woodland Realm",
        "emblem_file": "Faction Icons/Lindon.png", # Lindon elven emblem for Woodland Realm
        "aliases": ["Woodland Realm", "Woodland_Realm", "woodland realm", "Silvan Elves"]
    },
    {
        "id": "Mordor",
        "name": "Mordor",
        "color": "#8B0000",
        "treasury": 5000,
        "capital": "Barad-dûr",
        "zeal": 9,
        "folder": "Mordor",
        "emblem_file": "Faction Icons/Mordor.png",
        "aliases": ["Mordor", "mordor"]
    },
    {
        "id": "Lothlorien",
        "name": "Lothlorien",
        "color": "#D4AF37",
        "treasury": 5000,
        "capital": "Caras Galadhon",
        "zeal": 6,
        "folder": "Lothlorien",
        "emblem_file": "Faction Icons/Lothlorien.png",
        "aliases": ["Lothlorien", "Lothlórien", "lothlorien"]
    },
    {
        "id": "Imraldris",
        "name": "Imraldris",
        "color": "#4682B4",
        "treasury": 5000,
        "capital": "Rivendell",
        "zeal": 6,
        "folder": "Imraldris",
        "emblem_file": "Faction Icons/Imraldris.png",
        "aliases": ["Imraldris", "Imladris", "imraldris", "imladris"]
    },
    {
        "id": "Lostladen Tribes",
        "name": "Lostladen Tribes",
        "color": "#D27D2D",
        "treasury": 5000,
        "capital": "Umbar",
        "zeal": 6,
        "folder": "Lostladen Tribes",
        "emblem_file": "Faction Icons/Harad.png",
        "aliases": ["Lostladen Tribes", "Lostladen", "Harad", "Umbar", "Mahud"]
    }
]

# Additional emblems to register
EXTRA_EMBLEMS = {
    "Harad": "Faction Icons/Harad.png",
    "Umbar": "Faction Icons/Umbar.png",
    "Mahud": "Faction Icons/Mahud.png",
    "Imladris": "Faction Icons/Imraldris.png",
    "Lothlórien": "Faction Icons/Lothlorien.png",
}

# Helper to encode image to base64
def to_b64_uri(file_path):
    if not os.path.exists(file_path):
        print(f"Warning: File not found {file_path}")
        return None
    with open(file_path, "rb") as img_f:
        data = base64.b64encode(img_f.read()).decode("ascii")
    return f"data:image/png;base64,{data}"

# Clean name and parse unit properties
def clean_unit_name(filename):
    name = filename
    # Strip extension
    name = re.sub(r'(?i)\.png$', '', name)
    name = re.sub(r'(?i)png$', '', name)
    name = re.sub(r'(?i)_UC\d*$', '', name)
    name = re.sub(r'(?i)UC\d*$', '', name)
    # Strip leading digits and underscores (e.g., 01_, 02_)
    name = re.sub(r'^\d+_', '', name)
    # Strip faction prefix codes if present
    name = re.sub(r'^(roh|wr|mor|har)_', '', name, flags=re.I)
    # Replace underscores and dashes with spaces, clean double spaces
    name = name.replace('_', ' ').replace('-', ' ')
    name = re.sub(r'\s+', ' ', name).strip()
    # Title-case each word nicely
    words = [w.capitalize() if not (w.lower() in ['of', 'the', 'and', 'at', 'in']) else w.lower() for w in name.split(' ')]
    if words:
        words[0] = words[0].capitalize()
    return " ".join(words)

def clean_unit_key(fac_id, filename):
    name = filename
    name = re.sub(r'(?i)\.png$', '', name)
    name = re.sub(r'(?i)png$', '', name)
    name = re.sub(r'(?i)_UC\d*$', '', name)
    name = re.sub(r'^\d+_', '', name)
    fac_prefix = fac_id.lower().replace(' ', '_')
    key_body = re.sub(r'[^a-zA-Z0-9]+', '_', name.lower()).strip('_')
    # If key_body already starts with faction code (e.g. roh_, wr_, mor_, har_), simplify
    for pfx in ['roh_', 'wr_', 'mor_', 'har_']:
        if key_body.startswith(pfx):
            key_body = key_body[len(pfx):]
    return f"{fac_prefix}_{key_body}"

def deduce_unit_stats(fac_id, unit_name, filename):
    fn = filename.lower()
    nm = unit_name.lower()
    
    # Defaults
    category = "infantry"
    category_name = "Infantry"
    u_class = "inf_mel"
    class_name = "Melee Infantry"
    tier = "2"
    men = 120
    cost = 600
    upkeep = 180
    is_missile = False
    is_mounted = False
    
    # Check Command / Heroes
    if any(h in fn or h in nm for h in ['king', 'legolas', 'elrond', 'haldir', 'gothmog', 'the nine', 'the_nine', 'eorl', 'lord', 'hero', 'retinue']):
        u_class = "com"
        class_name = "Command"
        tier = "4"
        men = 60
        cost = 1400
        upkeep = 420
        if any(m in fn or m in nm for m in ['rider', 'horse', 'mounted', 'camel']):
            category = "cavalry"
            category_name = "Cavalry"
            is_mounted = True
    # Check Cavalry
    elif any(c in fn or c in nm for c in ['rider', 'horse', 'cavalry', 'mounted', 'knight', 'eored', 'lancer', 'camel', 'outrider']):
        category = "cavalry"
        category_name = "Cavalry"
        is_mounted = True
        if any(m in fn or m in nm for m in ['archer', 'skirmish', 'bow']):
            u_class = "cav_mis"
            class_name = "Missile Cavalry"
            is_missile = True
            men = 80
            cost = 850
            upkeep = 255
            tier = "2"
        else:
            u_class = "cav_shk"
            class_name = "Shock Cavalry"
            men = 80
            cost = 950
            upkeep = 285
            tier = "2"
    # Check Missile Infantry
    elif any(m in fn or m in nm for m in ['archer', 'bow', 'marksman', 'skirmish', 'tracker', 'slings', 'ranger', 'firespitter']):
        u_class = "inf_mis"
        class_name = "Missile Infantry"
        is_missile = True
        men = 120
        cost = 650
        upkeep = 195
        tier = "2"
    # Check Pike
    elif any(p in fn or p in nm for p in ['pike', 'phalanx']):
        u_class = "inf_pik"
        class_name = "Pike Infantry"
        men = 150
        cost = 600
        upkeep = 180
        tier = "2"
    # Check Spear / Guard
    elif any(s in fn or s in nm for s in ['spear', 'warden', 'guard', 'sentinel']):
        u_class = "inf_spr"
        class_name = "Spear Infantry"
        men = 150
        cost = 620
        upkeep = 185
        tier = "2"
    # Melee Infantry
    else:
        u_class = "inf_mel"
        class_name = "Melee Infantry"
        if 'rabble' in fn or 'pillager' in fn:
            tier = "1"
            cost = 450
            upkeep = 135
            men = 150
        else:
            tier = "2"
            cost = 580
            upkeep = 175
            men = 120
            
    # Extra flavor stats
    record = {
        "unit_key": "",
        "name": unit_name,
        "class": u_class,
        "category": category,
        "class_name": class_name,
        "category_name": category_name,
        "tier": tier,
        "men": men,
        "cost": cost,
        "upkeep": upkeep,
        "factions": [fac_id],
        "has_icon": True,
        "is_missile": is_missile,
        "is_mounted": is_mounted,
        "period": "Early",
        "training_level": "trained" if tier != "1" else "untrained",
        "description_short": f"Unit of {fac_id}: {unit_name}",
        "strengths_weaknesses": "",
        "faction_source": "custom_battle_permissions",
        "melee_attack": 12 if tier in ["3", "4"] else 9,
        "melee_defence": 13 if tier in ["3", "4"] else 10,
        "charge_bonus": 24 if is_mounted else (12 if tier in ["3", "4"] else 8),
        "armour_value": 11 if tier in ["3", "4"] else 7,
        "morale": 14 if tier == "4" else (11 if tier == "3" else 9)
    }
    if is_missile:
        record["missile_range"] = 160
        record["missile_damage"] = 38
        record["ammo"] = 24
        record["accuracy"] = 35
        
    return record

# Build units and icon dictionary
generated_units = []
new_icons = {}
new_emblems = {}
seen_keys = set()

# Process faction emblems
for fac in NEW_FACTIONS:
    emb_uri = to_b64_uri(fac["emblem_file"])
    if emb_uri:
        new_emblems[fac["id"]] = emb_uri
        for alias in fac["aliases"]:
            new_emblems[alias] = emb_uri

for emb_key, emb_path in EXTRA_EMBLEMS.items():
    emb_uri = to_b64_uri(emb_path)
    if emb_uri:
        new_emblems[emb_key] = emb_uri

print(f"Loaded {len(new_emblems)} emblems.")

# Process units
for fac in NEW_FACTIONS:
    dir_path = os.path.join("Unit Icons", fac["folder"])
    if not os.path.exists(dir_path):
        print(f"Directory missing: {dir_path}")
        continue
    files = sorted(os.listdir(dir_path))
    fac_unit_count = 0
    for fn in files:
        if not fn.lower().endswith('.png'):
            continue
        full_img_path = os.path.join(dir_path, fn)
        unit_name = clean_unit_name(fn)
        base_key = clean_unit_key(fac["id"], fn)
        key = base_key
        counter = 2
        while key in seen_keys:
            key = f"{base_key}_{counter}"
            counter += 1
        seen_keys.add(key)
        
        # Base64
        uri = to_b64_uri(full_img_path)
        new_icons[key] = uri
        
        # Unit stats record
        u_rec = deduce_unit_stats(fac["id"], unit_name, fn)
        u_rec["unit_key"] = key
        # Add faction aliases
        if fac["id"] == "Imraldris":
            u_rec["factions"] = ["Imraldris", "Imladris"]
        elif fac["id"] == "Lostladen Tribes":
            u_rec["factions"] = ["Lostladen Tribes", "Harad", "Umbar", "Mahud"]
        else:
            u_rec["factions"] = [fac["id"]]
            
        generated_units.append(u_rec)
        fac_unit_count += 1
        
    print(f"Faction '{fac['id']}': generated {fac_unit_count} units.")

print(f"Total units generated: {len(generated_units)}")

# 2. Update campaign.json
print("\nUpdating campaign.json...")
with open("campaign.json", "r", encoding="utf-8") as f:
    camp_data = json.load(f)

existing_fac_ids = {f.get("id") for f in camp_data.get("factions", [])}
camp_order = camp_data.setdefault("order", [])

for fac in NEW_FACTIONS:
    if fac["id"] not in existing_fac_ids:
        camp_data["factions"].append({
            "id": fac["id"],
            "name": fac["name"],
            "color": fac["color"],
            "treasury": fac["treasury"],
            "capital": fac["capital"],
            "zeal": fac["zeal"]
        })
        existing_fac_ids.add(fac["id"])
    if fac["id"] not in camp_order:
        camp_order.append(fac["id"])

with open("campaign.json", "w", encoding="utf-8") as f:
    json.dump(camp_data, f, indent=2, ensure_ascii=False)
print("campaign.json updated successfully.")

# 3. Helper to update HTML files (index.html, gm.html)
def update_html_file(file_path):
    print(f"\nProcessing {file_path}...")
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    # A. Update <script id="mapdata" type="application/json">
    def update_mapdata(match):
        raw_json = match.group(1)
        try:
            mdata = json.loads(raw_json)
            m_facs = mdata.get("factions", [])
            m_ids = {x.get("id") for x in m_facs}
            m_order = mdata.setdefault("order", [])
            for fac in NEW_FACTIONS:
                if fac["id"] not in m_ids:
                    m_facs.append({
                        "id": fac["id"],
                        "name": fac["name"],
                        "color": fac["color"],
                        "treasury": fac["treasury"],
                        "capital": fac["capital"],
                        "zeal": fac["zeal"]
                    })
                    m_ids.add(fac["id"])
                if fac["id"] not in m_order:
                    m_order.append(fac["id"])
            return f'<script id="mapdata" type="application/json">{json.dumps(mdata, ensure_ascii=False)}</script>'
        except Exception as e:
            print(f"Error parsing mapdata in {file_path}: {e}")
            return match.group(0)

    html = re.sub(r'<script id="mapdata" type="application/json">(.*?)</script>', update_mapdata, html, flags=re.DOTALL)

    # B. Update EMBLEMS
    # Locate const EMBLEMS = { ... };
    m_emb = re.search(r'const EMBLEMS\s*=\s*(\{.*?\n\s*\});', html, re.DOTALL)
    if m_emb:
        emb_block = m_emb.group(1)
        # Parse existing key-value pairs
        # We can construct the JS entries for new emblems
        inject_entries = []
        for k, v in new_emblems.items():
            if f'"{k}"' not in emb_block:
                inject_entries.append(f'  "{k}": "{v}",\n')
        if inject_entries:
            # Insert right after the opening brace '{'
            new_emb_block = "const EMBLEMS={\n" + "".join(inject_entries) + emb_block[emb_block.find("{")+1:]
            html = html[:m_emb.start()] + new_emb_block + html[m_emb.end():]
            print(f"Injected {len(inject_entries)} emblems into EMBLEMS in {file_path}.")

    # C. Update REALM_OF
    m_ro = re.search(r'const REALM_OF\s*=\s*(\{.*?\});', html, re.DOTALL)
    if m_ro:
        ro_block = m_ro.group(1)
        new_mappings = {
            "Rohan": "Rohan",
            "Woodland Realm": "Woodland Realm",
            "Mordor": "Mordor",
            "Lothlorien": "Lothlorien",
            "Lothlórien": "Lothlorien",
            "Imraldris": "Imraldris",
            "Imladris": "Imraldris",
            "Lostladen Tribes": "Lostladen Tribes",
            "Lostladen": "Lostladen Tribes",
            "Harad": "Lostladen Tribes",
            "Umbar": "Lostladen Tribes",
            "Mahud": "Lostladen Tribes"
        }
        ro_inject = []
        for k, v in new_mappings.items():
            if f'"{k}"' not in ro_block:
                ro_inject.append(f'"{k}":"{v}"')
        if ro_inject:
            # Insert right before the closing brace '}'
            idx = ro_block.rfind("}")
            updated_ro = "const REALM_OF=" + ro_block[:idx] + ("," if len(ro_block) > 2 else "") + ",".join(ro_inject) + "};"
            html = html[:m_ro.start()] + updated_ro + html[m_ro.end():]
            print(f"Updated REALM_OF in {file_path} with {len(ro_inject)} mappings.")

    # D. Update <script id="codexdata" type="application/json">
    m_cx = re.search(r'<script id="codexdata" type="application/json">(.*?)</script>', html, re.DOTALL)
    if m_cx:
        try:
            cx_data = json.loads(m_cx.group(1))
            cx_facs = cx_data.setdefault("factions", [])
            cx_fac_names = {f["name"] for f in cx_facs if "name" in f}
            
            for fac in NEW_FACTIONS:
                if fac["id"] not in cx_fac_names:
                    cx_facs.append({"name": fac["id"]})
                    cx_fac_names.add(fac["id"])
                    
            existing_unit_keys = {u["unit_key"] for u in cx_data.setdefault("units", [])}
            added_u_count = 0
            for u in generated_units:
                if u["unit_key"] not in existing_unit_keys:
                    cx_data["units"].append(u)
                    existing_unit_keys.add(u["unit_key"])
                    added_u_count += 1
                    
            new_cx_json = json.dumps(cx_data, ensure_ascii=False)
            html = html[:m_cx.start()] + f'<script id="codexdata" type="application/json">{new_cx_json}</script>' + html[m_cx.end():]
            print(f"Appended {added_u_count} units and {len(NEW_FACTIONS)} factions to codexdata in {file_path}.")
        except Exception as e:
            print(f"Error updating codexdata in {file_path}: {e}")

    # E. Update CODEX_ICONS
    m_ci = re.search(r'const CODEX_ICONS\s*=\s*(\{.*?\n\s*\});', html, re.DOTALL)
    if m_ci:
        ci_block = m_ci.group(1)
        ci_inject = []
        for uk, uri in new_icons.items():
            if f'"{uk}"' not in ci_block:
                ci_inject.append(f'  "{uk}": "{uri}",\n')
        if ci_inject:
            new_ci_block = "const CODEX_ICONS={\n" + "".join(ci_inject) + ci_block[ci_block.find("{")+1:]
            html = html[:m_ci.start()] + new_ci_block + html[m_ci.end():]
            print(f"Injected {len(ci_inject)} unit icons into CODEX_ICONS in {file_path}.")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Successfully saved {file_path}.")

# Execute update on index.html and gm.html
update_html_file("index.html")
if os.path.exists("gm.html"):
    update_html_file("gm.html")

print("\n=== VERIFYING JSON INTEGRITY ===")
with open("campaign.json", "r", encoding="utf-8") as f:
    c = json.load(f)
    print(f"campaign.json OK. Factions: {[fac['id'] for fac in c['factions']]}")

with open("index.html", "r", encoding="utf-8", errors="ignore") as f:
    h = f.read()
    m_cx = re.search(r'<script id="codexdata" type="application/json">(.*?)</script>', h, re.DOTALL)
    cxd = json.loads(m_cx.group(1))
    print(f"index.html codexdata OK. Total units: {len(cxd['units'])}, Factions: {[fac['name'] for fac in cxd['factions']]}")

print("\n=== COMMITTING AND PUSHING VIA GIT ===")
try:
    subprocess.run(["git", "add", "-A"], check=True)
    subprocess.run(["git", "status"], check=True)
    subprocess.run(["git", "commit", "-m", "Add Rohan, Woodland Realm, Mordor, Lothlorien, Imraldris, and Lostladen Tribes rosters, icons, and emblems"], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print("=== GIT COMMIT & PUSH COMPLETE ===")
except Exception as e:
    print(f"Git execution: {e}")

print("\n=== ALL COMPLETE ===")
