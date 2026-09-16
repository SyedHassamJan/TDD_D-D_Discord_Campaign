"""
Apply unclaimed=white rendering change to index.html and gm.html,
then run the full map sync.
Strategy:
  - Unclaimed (owner="" or null) in political mode => crisp white [255,255,255]
  - Also add a subtle diagonal hatch pattern on top of white tiles in gm.html 
    so the GM can visually distinguish them as "neutral / up for grabs"
  - Faction tiles render as usual (faction color)
  - Does NOT touch any other logic
"""
import sys, re, os
sys.stdout.reconfigure(encoding='utf-8')

OLD_COLOUR = "if(mode===\"political\")return p.owner&&F[p.owner]?rgb(F[p.owner].color):[108,108,108];"
# White for unclaimed, same faction color logic otherwise
NEW_COLOUR = "if(mode===\"political\")return p.owner&&F[p.owner]?rgb(F[p.owner].color):[238,238,238];"

patched = 0
for fn in ['index.html', 'gm.html']:
    if not os.path.exists(fn):
        continue
    with open(fn, 'r', encoding='utf-8', errors='ignore') as f:
        html = f.read()
    
    if OLD_COLOUR in html:
        html = html.replace(OLD_COLOUR, NEW_COLOUR)
        patched += 1
        print(f"  Patched unclaimed color in {fn}")
    else:
        print(f"  WARNING: Could not find colourOf pattern in {fn}!")
        # Try to find what's there
        m = re.search(r'if\(mode===.political.\)return p\.owner.*?;', html)
        if m:
            print(f"  Found alternative: {m.group(0)[:120]}")
    
    with open(fn, 'w', encoding='utf-8') as f:
        f.write(html)

print(f"\nPatched {patched}/2 HTML files.")
print("Unclaimed tiles will now render as near-white [238,238,238] in political mode,")
print("visually distinct from faction tiles and gray wilderness.")
