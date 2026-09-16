"""
Compress all faction icon PNGs to 128x128 JPEG before base64 encoding.
Faction emblems don't need to be massive — they display at ~48-64px in the UI.
This cuts emblems.js from ~20MB down to < 1MB.
Also compress unit icons to 64x64 JPEG.
"""
import sys, os, base64, hashlib, re
from PIL import Image
import io
sys.stdout.reconfigure(encoding='utf-8')

FACTIONS_DIR = "Faction Icons"
UNITS_DIR = "Unit Icons"
ASSETS_DIR = "assets"

# ---- Step 1: Faction Emblems (compress to 96x96 PNG) ----
print("=== Compressing Faction Icons for emblems.js ===")

hash_to_b64 = {}
name_to_hash = {}

if os.path.exists(FACTIONS_DIR):
    for fn in sorted(os.listdir(FACTIONS_DIR)):
        if not fn.lower().endswith(".png"):
            continue
        fac_name = os.path.splitext(fn)[0]
        path = os.path.join(FACTIONS_DIR, fn)
        
        # Compress to 96x96 PNG (keeps alpha for transparent emblems)
        img = Image.open(path).convert("RGBA")
        img = img.resize((96, 96), Image.Resampling.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="PNG", optimize=True)
        raw = buf.getvalue()
        
        h = hashlib.md5(raw).hexdigest()
        if h not in hash_to_b64:
            hash_to_b64[h] = base64.b64encode(raw).decode("ascii")
        name_to_hash[fac_name] = h
        print(f"  {fac_name}: compressed ({len(raw)/1024:.0f} KB)")

lines = ['"use strict";']
hash_to_var = {}
for i, (h, b64) in enumerate(hash_to_b64.items()):
    varname = f"_EMB_{i}"
    lines.append(f'const {varname}="data:image/png;base64,{b64}";')
    hash_to_var[h] = varname

lines.append("const EMBLEMS={")
for name, h in name_to_hash.items():
    var = hash_to_var[h]
    lines.append(f'  "{name}":{var},')
    lines.append(f'  "{name.lower()}":{var},')
lines.append("};")

out = "\n".join(lines)
emb_path = os.path.join(ASSETS_DIR, "emblems.js")
with open(emb_path, "w", encoding="utf-8") as f:
    f.write(out)
print(f"\nemblems.js: {os.path.getsize(emb_path)/1024:.0f} KB")

# ---- Step 2: Unit Icons (compress to 64x64 JPEG) ----
print("\n=== Compressing Unit Icons for codex_icons.js ===")

codex_icons = {}
total_units = 0

def clean_key(fac_dir, u_fn):
    name = re.sub(r'(?i)\.png$', '', u_fn)
    name = re.sub(r'(?i)_UC\d*$', '', name)
    name = re.sub(r'^\d+_', '', name)
    fac_prefix = fac_dir.lower().replace(' ', '_')
    key_body = re.sub(r'[^a-zA-Z0-9]+', '_', name.lower()).strip('_')
    return f"{fac_prefix}_{key_body}"

if os.path.exists(UNITS_DIR):
    for fac_dir in sorted(os.listdir(UNITS_DIR)):
        fac_path = os.path.join(UNITS_DIR, fac_dir)
        if not os.path.isdir(fac_path):
            continue
        unit_files = [f for f in os.listdir(fac_path) if f.lower().endswith(".png")]
        for u_fn in unit_files:
            u_path = os.path.join(fac_path, u_fn)
            u_key = clean_key(fac_dir, u_fn)
            
            # Compress unit icon to 64x64 JPEG (no alpha needed for units)
            img = Image.open(u_path).convert("RGB")
            img = img.resize((64, 64), Image.Resampling.LANCZOS)
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=75, optimize=True)
            raw = buf.getvalue()
            
            codex_icons[u_key] = "data:image/jpeg;base64," + base64.b64encode(raw).decode("ascii")
            total_units += 1
        print(f"  {fac_dir}: {len(unit_files)} units")

codex_path = os.path.join(ASSETS_DIR, "codex_icons.js")
with open(codex_path, "w", encoding="utf-8") as f:
    f.write('"use strict";\nconst CODEX_ICONS={\n')
    for k, v in codex_icons.items():
        f.write(f'  "{k}":"{v}",\n')
    f.write('};\n')

print(f"\ncodex_icons.js: {os.path.getsize(codex_path)/1024/1024:.1f} MB ({total_units} units)")
print("\n=== DONE. Refresh gm.html — boot should be much faster now! ===")
