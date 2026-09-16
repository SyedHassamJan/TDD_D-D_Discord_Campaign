"""
Extract the core province rendering function from index.html (Script#6, the main game script).
"""
import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open('index.html', 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

scripts = list(re.finditer(r'<script[^>]*>(.*?)</script>', html, re.DOTALL))
# Script#6 is index 5
s6 = scripts[5].group(1)
lines = s6.split('\n')

# Show lines around 1748 (the fillStyle for province tiers)
start = max(0, 1700)
end = min(len(lines), 1830)
for i in range(start, end):
    print(f"L{i+1}: {lines[i][:140]}")
