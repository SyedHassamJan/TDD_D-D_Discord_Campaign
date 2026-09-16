import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open('index.html', 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

scripts = list(re.finditer(r'<script[^>]*>(.*?)</script>', html, re.DOTALL))
s6 = scripts[5].group(1)
lines = s6.split('\n')

# Find boot function
for i, line in enumerate(lines):
    if 'function boot' in line or 'boot()' in line or 'SURVEYING' in line or 'setTimeout(boot' in line:
        print(f"L{i+1}: {lines[i][:200]}")

# Also show the img.onload / boot trigger area
print("\n\n--- img.onload area (how boot is triggered) ---")
for i, line in enumerate(lines):
    if 'img.onload' in line or 'img.src' in line or 'mapImg' in line or 'MAP_B64' in line:
        start = max(0, i-2)
        end = min(len(lines), i+10)
        for j in range(start, end):
            print(f"L{j+1}: {lines[j][:200]}")
        break
