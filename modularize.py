import os
import re
import shutil

print("=== STARTING CLEAN MODULARIZATION ===")

# 1. Backups
for fn in ['index.html', 'gm.html']:
    bak = fn + '.bak'
    if not os.path.exists(bak):
        print(f"Creating backup: {bak}...")
        shutil.copyfile(fn, bak)
    else:
        print(f"Backup already exists: {bak}")

os.makedirs("assets", exist_ok=True)

# 2. Process index.html first
print("\nReading index.html...")
with open('index.html', 'r', encoding='utf-8', errors='ignore') as f:
    index_text = f.read()

print(f"Original index.html size: {len(index_text):,} bytes")

# Extract MAP_B64, TERRAIN_B64, SHADE_B64
m_map = re.search(r'(const\s+MAP_B64\s*=\s*"[^"]*";)', index_text)
m_terr = re.search(r'(const\s+TERRAIN_B64\s*=\s*"[^"]*";)', index_text)
m_shade = re.search(r'(const\s+SHADE_B64\s*=\s*"[^"]*";)', index_text)

if m_map and m_terr and m_shade:
    print("Writing assets/map_assets.js...")
    with open('assets/map_assets.js', 'w', encoding='utf-8') as f:
        f.write('"use strict";\n')
        f.write(m_map.group(1) + '\n')
        f.write(m_terr.group(1) + '\n')
        f.write(m_shade.group(1) + '\n')
    print("  assets/map_assets.js written successfully.")
else:
    print("WARNING: Could not find map b64 variables in index.html!")

# Extract EMBLEMS
# Matches const EMBLEMS = { ... };
m_emb = re.search(r'(const\s+EMBLEMS\s*=\s*\{.*?\n\s*\};)', index_text, re.DOTALL)
if m_emb:
    print("Writing assets/emblems.js...")
    with open('assets/emblems.js', 'w', encoding='utf-8') as f:
        f.write('"use strict";\n')
        f.write(m_emb.group(1) + '\n')
    print("  assets/emblems.js written successfully.")
else:
    print("WARNING: Could not find EMBLEMS in index.html!")

# Extract CODEX_ICONS
m_codex_icons = re.search(r'(const\s+CODEX_ICONS\s*=\s*\{.*?\n?\s*\};)', index_text, re.DOTALL)
if m_codex_icons:
    print("Writing assets/codex_icons.js...")
    with open('assets/codex_icons.js', 'w', encoding='utf-8') as f:
        f.write('"use strict";\n')
        f.write(m_codex_icons.group(1) + '\n')
    print("  assets/codex_icons.js written successfully.")
else:
    print("WARNING: Could not find CODEX_ICONS in index.html!")

# Function to transform an HTML file
def modularize_html(file_path):
    print(f"\nProcessing {file_path}...")
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        html = f.read()

    orig_size = len(html)
    
    # 1. Replace MAP_B64, TERRAIN_B64, SHADE_B64, EMBLEMS
    # In Script 3, they appear at the top.
    # Replace the declarations of MAP_B64, TERRAIN_B64, SHADE_B64 with nothing
    html = re.sub(r'const\s+MAP_B64\s*=\s*"[^"]*";\s*', '', html)
    html = re.sub(r'const\s+TERRAIN_B64\s*=\s*"[^"]*";\s*', '', html)
    html = re.sub(r'const\s+SHADE_B64\s*=\s*"[^"]*";\s*', '', html)
    html = re.sub(r'const\s+EMBLEMS\s*=\s*\{.*?\n\s*\};\s*', '', html, flags=re.DOTALL)
    
    # Replace CODEX_ICONS script block
    # Look for <script>\s*const CODEX_ICONS\s*=\s*\{.*?\};\s*</script>
    html = re.sub(r'<script>\s*const\s+CODEX_ICONS\s*=\s*\{.*?\n?\s*\};\s*</script>', '', html, flags=re.DOTALL)
    # Also if it's not wrapped in standalone script
    html = re.sub(r'const\s+CODEX_ICONS\s*=\s*\{.*?\n?\s*\};\s*', '', html, flags=re.DOTALL)

    # Now inject the <script src="..."> tags before the main game script!
    # Find the script tag right after <script id="mapdata"...></script>
    # or before the script that has "use strict"
    script_injections = (
        '\n<script src="assets/map_assets.js"></script>\n'
        '<script src="assets/emblems.js"></script>\n'
        '<script src="assets/codex_icons.js"></script>\n'
    )
    
    # We want to insert this before <script> "use strict";
    # or right after </script> of mapdata
    if '<script id="codexdata"' in html:
        # Put it right before codexdata
        idx = html.find('<script id="codexdata"')
        html = html[:idx] + script_injections + html[idx:]
    elif '<script id="mapdata"' in html:
        end_mapdata = html.find('</script>', html.find('<script id="mapdata"')) + len('</script>')
        html = html[:end_mapdata] + script_injections + html[end_mapdata:]
    else:
        # Fallback to right before </head> or <body>
        idx = html.find('</head>')
        if idx != -1:
            html = html[:idx] + script_injections + html[idx:]

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html)
        
    print(f"  {file_path} reduced from {orig_size:,} to {len(html):,} bytes! ({(1 - len(html)/orig_size)*100:.1f}% reduction)")

modularize_html('index.html')
modularize_html('gm.html')

print("\n=== MODULARIZATION COMPLETE ===")
