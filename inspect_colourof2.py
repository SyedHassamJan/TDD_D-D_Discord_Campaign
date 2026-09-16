import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open('index.html', 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

scripts = list(re.finditer(r'<script[^>]*>(.*?)</script>', html, re.DOTALL))
s6 = scripts[5].group(1)
lines = s6.split('\n')

# Show lines 130-145 (colourOf function)
for j in range(130, 145):
    print(f"L{j+1}: {lines[j][:200]}")
