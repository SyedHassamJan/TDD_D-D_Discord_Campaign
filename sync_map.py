import base64
import re
import os

MAP_PATH = os.path.join("map_assets_extracted", "map_b64.png")

if not os.path.exists(MAP_PATH):
    print(f"Error: {MAP_PATH} not found!")
    exit(1)

print(f"Reading edited {MAP_PATH}...")
with open(MAP_PATH, "rb") as f:
    new_b64 = base64.b64encode(f.read()).decode("ascii")

for fn in ["index.html", "gm.html"]:
    if not os.path.exists(fn):
        continue
    with open(fn, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Replace MAP_B64
    content = re.sub(
        r'const MAP_B64="[^"]*";',
        f'const MAP_B64="{new_b64}";',
        content
    )

    with open(fn, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Updated {fn} with new province map.")

print("\nDone! Refresh your browser to see your changes on the map.")
