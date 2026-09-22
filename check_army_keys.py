import json
import re

with open('gm.html', 'r', encoding='utf-8') as f:
    text = f.read()

m_codex = re.search(r'<script id="codexdata" type="application/json">(.*?)</script>', text, re.DOTALL)
cx_data = json.loads(m_codex.group(1))
unit_keys = {u['unit_key']: u for u in cx_data['units']}

m_map = re.search(r'<script id="mapdata" type="application/json">(.*?)</script>', text, re.DOTALL)
map_data = json.loads(m_map.group(1))

print("=== CHECKING STARTING ARMIES AGAINST CODEX UNITS ===")
for a in map_data.get('armies', []):
    print(f"\nArmy: {a.get('name')} (Faction: {a.get('faction')})")
    print(f"  Army recorded men: {a.get('men')}, recorded upkeep: {a.get('upkeep')}")
    calc_men = 0
    calc_upkeep = 0
    for ukey in a.get('units', []):
        if ukey in unit_keys:
            u = unit_keys[ukey]
            calc_men += u.get('men', 0)
            calc_upkeep += u.get('upkeep', 0)
            print(f"  [OK] {ukey}: {u.get('name')} (men={u.get('men')}, upkeep={u.get('upkeep')})")
        else:
            # Let's search if there is an aliased or similar key
            matches = [k for k in unit_keys if ukey.split('_', 1)[-1] in k or k.endswith(ukey)]
            print(f"  [MISSING!] {ukey} not found in codex! Possible matches: {matches}")
    print(f"  Sum calculated: men={calc_men}, upkeep={calc_upkeep}")
