import json
import re
import os

with open('index.html', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

out = []

m = re.search(r'<script id="codexdata" type="application/json">(.*?)</script>', content, re.DOTALL)
if m:
    data = json.loads(m.group(1))
    out.append(f"Codex factions: {data.get('factions')}")
    out.append(f"Codex total units: {len(data.get('units', []))}")

m2 = re.search(r'const EMBLEMS\s*=\s*(\{.*?\n\s*\});', content, re.DOTALL)
if m2:
    # extract keys
    keys = re.findall(r'"([^"]+)":', m2.group(1))
    out.append(f"EMBLEMS keys: {keys}")

m3 = re.search(r'const REALM_OF\s*=\s*(\{.*?\n\s*\});', content, re.DOTALL)
if m3:
    out.append(f"REALM_OF:\n{m3.group(0)}")

# Check files in Unit Icons for each target faction
target_factions = ['Rohan', 'Woodland Realm', 'Mordor', 'Lothlorien', 'Imraldris', 'Lostladen Tribes']
for tf in target_factions:
    dir_path = os.path.join('Unit Icons', tf)
    if os.path.exists(dir_path):
        files = os.listdir(dir_path)
        out.append(f"\nFaction '{tf}' ({len(files)} files):")
        for fn in files[:10]:
            out.append(f"  {fn}")
        if len(files) > 10:
            out.append(f"  ... and {len(files) - 10} more")

with open('inspect_summary.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))

print("Saved inspect_summary.txt")
