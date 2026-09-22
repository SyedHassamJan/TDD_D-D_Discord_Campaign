import json
import re

for fname in ['gm.html', 'index.html']:
    with open(fname, 'r', encoding='utf-8') as f:
        text = f.read()

    m = re.search(r'<script id="codexdata" type="application/json">(.*?)</script>', text, re.DOTALL)
    if m:
        data = json.loads(m.group(1))
        print(f"\n=== {fname} Codex Top-Level Keys ===")
        print("Keys:", list(data.keys()))
        if 'units' in data:
            print("len(units):", len(data['units']))
            if data['units']:
                print("First unit:", data['units'][0])
                print("Sample unit with key 'gondor_sword_militia':")
                for u in data['units']:
                    if 'sword_militia' in u.get('unit_key', ''):
                        print(" ", u)
                        break
