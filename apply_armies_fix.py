import json
import re
import os

# 1. Update campaign.json starting armies
with open('campaign.json', 'r', encoding='utf-8') as f:
    camp_data = json.load(f)

camp_data['armies'] = [
    {
        "name": "Host of South Ithilien",
        "faction": "Gondor",
        "at": "South Ithilien",
        "men": 480,
        "order": None,
        "units": [
            "gondor_gondor_sword_militia",
            "gondor_aor_ringlovale_men_at_arms",
            "gondor_aor_pelagir_marines",
            "gondor_aor_ithilien_rangers"
        ],
        "xp": [0, 1, 0, 2],
        "upkeep": 1725.0
    },
    {
        "name": "Host of Harondor",
        "faction": "Mordor",
        "at": "Harondor",
        "men": 300,
        "order": None,
        "units": [
            "mordor_mordor_orc_warband",
            "mordor_nazgul",
            "mordor_gothmog"
        ],
        "xp": [0, 0, 1],
        "upkeep": 1862.5
    },
    {
        "name": "Host of Near Harad",
        "faction": "Lostladen Tribes",
        "at": "Near Harad",
        "men": 340,
        "order": None,
        "units": [
            "lostladen_tribes_aor_corsair_marines",
            "lostladen_tribes_camel_riders",
            "lostladen_tribes_aor_mahud_spearmen"
        ],
        "xp": [0, 0, 0],
        "upkeep": 1175.0
    }
]

# Set settlement value to 850 for all default tier 2 provinces (Level 3 Fortified City Small in spreadsheet)
for p in camp_data['provinces']:
    if p.get('playable') and p.get('tier') == 2 and p.get('value') == 1000:
        p['value'] = 850

with open('campaign.json', 'w', encoding='utf-8') as f:
    json.dump(camp_data, f, indent=2, ensure_ascii=False)
print("Updated campaign.json armies and province values.")

# 2. Update mapdata in index.html and gm.html
for fname in ['index.html', 'gm.html']:
    with open(fname, 'r', encoding='utf-8') as f:
        content = f.read()

    m = re.search(r'<script id="mapdata" type="application/json">(.*?)</script>', content, re.DOTALL)
    if m:
        html_mapdata = json.loads(m.group(1))
        html_mapdata['armies'] = camp_data['armies']
        for p in html_mapdata['provinces']:
            if p.get('playable') and p.get('tier') == 2 and p.get('value') == 1000:
                p['value'] = 850
        
        new_mapdata_str = json.dumps(html_mapdata, separators=(',', ':'), ensure_ascii=False)
        content = content[:m.start(1)] + new_mapdata_str + content[m.end(1):]

    with open(fname, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Updated mapdata in {fname}.")
