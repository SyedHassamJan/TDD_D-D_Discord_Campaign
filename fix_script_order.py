import re

def fix_order(filename):
    print(f"Fixing script order in {filename}...")
    with open(filename, 'r', encoding='utf-8') as f:
        html = f.read()

    # Remove existing injections of assets scripts
    html = re.sub(r'<script\s+src="assets/map_assets\.js"></script>\s*', '', html)
    html = re.sub(r'<script\s+src="assets/emblems\.js"></script>\s*', '', html)
    html = re.sub(r'<script\s+src="assets/codex_icons\.js"></script>\s*', '', html)

    # We want to inject map_assets.js and emblems.js right before the main game script!
    # Main game script has "use strict";\s*const S=JSON.parse(document.getElementById("mapdata")
    target = '<script>\n"use strict";\nconst S=JSON.parse'
    if target not in html:
        # try more flexible regex
        m = re.search(r'<script[^>]*>\s*["\']use strict["\'];\s*const\s+S\s*=', html)
        if m:
            target = m.group(0)
        else:
            print(f"Error: Target main script not found in {filename}!")
            return

    asset_tags = (
        '<script src="assets/map_assets.js"></script>\n'
        '<script src="assets/emblems.js"></script>\n'
        '<script src="assets/codex_icons.js"></script>\n'
    )
    
    html = html.replace(target, asset_tags + target, 1)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"  Successfully reordered scripts in {filename}.")

fix_order('index.html')
fix_order('gm.html')
