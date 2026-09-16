"""
Find the paintMap function in index.html main game script.
"""
import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open('index.html', 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

scripts = list(re.finditer(r'<script[^>]*>(.*?)</script>', html, re.DOTALL))
s6 = scripts[5].group(1)
lines = s6.split('\n')

# Find paintMap function
for i, line in enumerate(lines):
    if 'function paintMap' in line or ('paintMap' in line and '{' in line):
        # Print surrounding context
        start = max(0, i)
        end = min(len(lines), i + 80)
        for j in range(start, end):
            print(f"L{j+1}: {lines[j][:160]}")
        break
