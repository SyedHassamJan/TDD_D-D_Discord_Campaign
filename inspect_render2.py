"""
Inspect how the province canvas rendering works in index.html.
Looks for the province fill / color painting logic.
"""
import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open('index.html', 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

# Find every line that touches 'fillStyle' or 'provColor' or 'owner' in the context of drawing
scripts = list(re.finditer(r'<script[^>]*>(.*?)</script>', html, re.DOTALL))
for i, s in enumerate(scripts):
    body = s.group(1)
    # Only look in the main game script (has 'use strict')
    if '"use strict"' not in body and "'use strict'" not in body:
        continue
    lines = body.split('\n')
    for ln_num, line in enumerate(lines, 1):
        if any(kw in line for kw in ['fillStyle', 'provColor', 'owner', 'faction', 'drawProv', 'paintProv', 'REALM_OF']):
            if len(line.strip()) > 3:
                print(f"Script#{i+1} L{ln_num}: {line.strip()[:120]}")
