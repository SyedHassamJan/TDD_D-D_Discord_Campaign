import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open('gm.html', 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

scripts = list(re.finditer(r'<script([^>]*)>(.*?)</script>', html, re.DOTALL))
print(f"Total scripts in gm.html: {len(scripts)}")
for i, m in enumerate(scripts):
    attrs = m.group(1).strip()
    body = m.group(2).strip()[:80].replace('\n', ' ')
    print(f"Script #{i+1}: <script {attrs}> -> {body}...")

# Also check if MAP_B64 is still defined inline anywhere
if 'const MAP_B64=' in html:
    print("\nWARNING: MAP_B64 still defined inline in gm.html!")
else:
    print("\nOK: MAP_B64 not inline in gm.html (correctly in assets/)")

# Check TERRAIN_B64 and SHADE_B64
if 'const TERRAIN_B64=' in html:
    print("WARNING: TERRAIN_B64 still inline!")
else:
    print("OK: TERRAIN_B64 in assets/")

if 'const SHADE_B64=' in html:
    print("WARNING: SHADE_B64 still inline!")
else:
    print("OK: SHADE_B64 in assets/")

# Check S.w and S.h match the actual map dimensions in mapdata
m = re.search(r'"w"\s*:\s*(\d+),\s*"h"\s*:\s*(\d+)', html)
if m:
    print(f"\nMap dimensions in mapdata: w={m.group(1)}, h={m.group(2)}")
