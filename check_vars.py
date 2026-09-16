import re
import os

for filename in ['index.html', 'gm.html']:
    print(f"Checking {filename}...")
    with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
    print(f"  Total length: {len(text)}")
    m1 = re.search(r'const\s+MAP_B64\s*=\s*"([^"]*)";', text)
    m2 = re.search(r'const\s+TERRAIN_B64\s*=\s*"([^"]*)";', text)
    m3 = re.search(r'const\s+SHADE_B64\s*=\s*"([^"]*)";', text)
    
    print(f"  MAP_B64 found: {bool(m1)} (len: {len(m1.group(1)) if m1 else 0})")
    print(f"  TERRAIN_B64 found: {bool(m2)} (len: {len(m2.group(1)) if m2 else 0})")
    print(f"  SHADE_B64 found: {bool(m3)} (len: {len(m3.group(1)) if m3 else 0})")
