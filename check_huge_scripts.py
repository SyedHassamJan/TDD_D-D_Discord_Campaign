import re

with open('index.html', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

scripts = list(re.finditer(r'<script[^>]*>(.*?)</script>', text, re.DOTALL))

for idx in [2, 4]: # 0-indexed: 2 is Script 3, 4 is Script 5
    s = scripts[idx]
    content = s.group(1).strip()
    print(f"\n--- Script {idx+1} (Length: {len(content):,} chars) ---")
    print("Start (first 200 chars):")
    print(repr(content[:200]))
    print("End (last 200 chars):")
    print(repr(content[-200:]))
