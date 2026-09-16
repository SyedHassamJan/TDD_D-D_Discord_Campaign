import re

for fn in ['index.html', 'gm.html']:
    print(f"\nChecking {fn}...")
    with open(fn, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find where assets scripts are included
    idx_map_js = content.find('assets/map_assets.js')
    idx_emb_js = content.find('assets/emblems.js')
    idx_codex_js = content.find('assets/codex_icons.js')
    
    # Find where main game script starts (e.g. S=JSON.parse)
    idx_main = content.find('JSON.parse(document.getElementById("mapdata")')
    
    print(f"  map_assets.js at: {idx_map_js}")
    print(f"  emblems.js at: {idx_emb_js}")
    print(f"  codex_icons.js at: {idx_codex_js}")
    print(f"  main game script at: {idx_main}")
    
    if idx_map_js != -1 and idx_main != -1 and idx_map_js < idx_main:
        print("  => OK: Asset scripts load BEFORE main game script!")
    else:
        print("  => ISSUE: Order check failed!")
