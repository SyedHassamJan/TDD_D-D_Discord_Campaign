import json
import re

with open('gm.html', 'r', encoding='utf-8') as f:
    text = f.read()

m_codex = re.search(r'<script id="codexdata" type="application/json">(.*?)</script>', text, re.DOTALL)
cx_data = json.loads(m_codex.group(1))

print("=== Gondor Units ===")
for u in cx_data['units']:
    if u.get('faction') == 'Gondor':
        print(f"{u['unit_key']}: {u['name']} (men={u['men']}, cost={u['cost']}, upkeep={u['upkeep']}, tier={u['tier']})")
