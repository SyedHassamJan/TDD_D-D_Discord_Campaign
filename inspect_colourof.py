"""
Find the colourOf function in index.html main game script.
"""
import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open('index.html', 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

scripts = list(re.finditer(r'<script[^>]*>(.*?)</script>', html, re.DOTALL))
s6 = scripts[5].group(1)
lines = s6.split('\n')

for i, line in enumerate(lines):
    if 'colourOf' in line or 'colorOf' in line or 'NEUTRAL' in line or 'UNCLAIMED' in line:
        print(f"L{i+1}: {lines[i][:200]}")
