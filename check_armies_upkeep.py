import json
import re

for fname in ['campaign.json', 'index.html', 'gm.html']:
    if fname.endswith('.json'):
        with open(fname, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        with open(fname, 'r', encoding='utf-8') as f:
            content = f.read()
        m = re.search(r'<script id="mapdata" type="application/json">(.*?)</script>', content, re.DOTALL)
        data = json.loads(m.group(1)) if m else {}
    
    armies = data.get('armies', [])
    print(f"\n=== {fname} Armies ({len(armies)}) ===")
    for a in armies:
        print(f"  Name: {a.get('name')}, Faction: {a.get('faction')}, At: {a.get('at')}, Men: {a.get('men')}, Upkeep: {a.get('upkeep')}, Units: {len(a.get('units', [])) if isinstance(a.get('units'), list) else 'No units array'}")
        if isinstance(a.get('units'), list) and a.get('units'):
            print(f"    Units list: {a.get('units')}")
