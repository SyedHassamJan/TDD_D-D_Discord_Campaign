import json
import re

with open('gm.html', 'r', encoding='utf-8', errors='ignore') as f:
    gm_content = f.read()

print('gm.html size:', len(gm_content))
print('has codexdata in gm.html:', '<script id="codexdata"' in gm_content)
print('has mapdata in gm.html:', '<script id="mapdata"' in gm_content)
print('has EMBLEMS in gm.html:', 'const EMBLEMS' in gm_content)
print('has REALM_OF in gm.html:', 'const REALM_OF' in gm_content)
print('has CODEX_ICONS in gm.html:', 'const CODEX_ICONS' in gm_content)
