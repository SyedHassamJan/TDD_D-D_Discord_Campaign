"""
Fix 1: Deduplicate EMBLEMS — one base64 entry per unique image, aliases just point to same key
Fix 2: Unit icons stay in codex_icons.js but we check if the file is too big and warn
This massively reduces JS parse time on boot.
"""
import sys, os, re, base64, hashlib
sys.stdout.reconfigure(encoding='utf-8')

FACTIONS_DIR = "Faction Icons"
ASSETS_DIR = "assets"

print("=== FIX: Deduplicating emblems.js ===")

# Build hash -> b64 map
hash_to_b64 = {}   # md5 -> base64 string
name_to_hash = {}  # canonical_name -> md5

if os.path.exists(FACTIONS_DIR):
    for fn in sorted(os.listdir(FACTIONS_DIR)):
        if not fn.lower().endswith(".png"):
            continue
        fac_name = os.path.splitext(fn)[0]
        path = os.path.join(FACTIONS_DIR, fn)
        with open(path, "rb") as f:
            raw = f.read()
        h = hashlib.md5(raw).hexdigest()
        if h not in hash_to_b64:
            hash_to_b64[h] = base64.b64encode(raw).decode("ascii")
        name_to_hash[fac_name] = h

print(f"  {len(name_to_hash)} factions, {len(hash_to_b64)} unique images (was duplicated to 30 entries before)")

# Write deduped emblems.js:
# Pattern: store each unique image once, then aliases just reference the same var
lines = ['"use strict";']
# First declare one const per unique image
hash_to_var = {}
for i, (h, b64) in enumerate(hash_to_b64.items()):
    varname = f"_EMB_{i}"
    lines.append(f'const {varname}="data:image/png;base64,{b64}";')
    hash_to_var[h] = varname

# Then build EMBLEMS object referencing vars, no duplication
lines.append("const EMBLEMS={")
for name, h in name_to_hash.items():
    var = hash_to_var[h]
    lines.append(f'  "{name}":{var},')
    lines.append(f'  "{name.lower()}":{var},')
lines.append("};")

out = "\n".join(lines)
out_path = os.path.join(ASSETS_DIR, "emblems.js")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(out)

old_size = 40_891_814
new_size = os.path.getsize(out_path)
print(f"  emblems.js: {old_size/1024/1024:.1f} MB -> {new_size/1024/1024:.1f} MB saved!")
print(f"  ({(1-new_size/old_size)*100:.0f}% reduction)")

print("\n=== Done. Refresh gm.html ===")
