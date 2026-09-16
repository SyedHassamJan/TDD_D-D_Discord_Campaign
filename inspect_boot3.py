import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open('index.html', 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

scripts = list(re.finditer(r'<script[^>]*>(.*?)</script>', html, re.DOTALL))
s6 = scripts[5].group(1)
lines = s6.split('\n')

# Show img.src=MAP_B64 and surrounding lines 38-100
for j in range(37, 100):
    print(f"L{j+1}: {lines[j][:180]}")
