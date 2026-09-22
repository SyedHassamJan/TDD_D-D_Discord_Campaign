import json
import re

with open('gm.html', 'r', encoding='utf-8') as f:
    text = f.read()

m_codex = re.search(r'<script id="codexdata" type="application/json">(.*?)</script>', text, re.DOTALL)
cx_data = json.loads(m_codex.group(1))

for fac in ['Gondor', 'Mordor', 'Lostladen Tribes', 'Harad', 'Lostladen']:
    print(f"\n=== Units for {fac} ===")
    units = [u for u in cx_data['units'] if u.get('faction') == fac]
    print(f"Count: {len(units)}")
    for u in units:
        print(f"  key: {u['unit_key']}, name: {u['name']}, men: {u['men']}, cost: {u['cost']}, upkeep: {u['upkeep']}, tier: {u['tier']}")
