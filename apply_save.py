"""
Apply GM Exported Save (apply_save.py)
Takes the JSON exported from GM mode and permanently sets it as the starting map state (START_SNAP) in index.html and gm.html.
"""
import os
import sys
import re
import json

SAVE_FILE = "save.json"

if not os.path.exists(SAVE_FILE):
    print(f"Error: {SAVE_FILE} not found!")
    print("In GM mode (gm.html), click 'Export' and paste the output into save.json, then re-run this script.")
    sys.exit(1)

with open(SAVE_FILE, "r", encoding="utf-8") as f:
    snap_data = json.load(f)

snap_js = "const START_SNAP=" + json.dumps(snap_data, separators=(",", ":"), ensure_ascii=False) + ";"

for fn in ["index.html", "gm.html"]:
    if not os.path.exists(fn):
        continue
    with open(fn, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    # Replace START_SNAP
    html = re.sub(r'const START_SNAP\s*=\s*\{.*?\};', snap_js, html, flags=re.DOTALL)

    with open(fn, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Applied starting snapshot to {fn}.")

print("\nDone! All painted factions are now permanently locked in.")
