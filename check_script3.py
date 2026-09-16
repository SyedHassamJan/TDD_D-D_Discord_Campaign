import re

with open('index.html', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

scripts = list(re.finditer(r'<script[^>]*>(.*?)</script>', text, re.DOTALL))
s3 = scripts[2].group(1)

# Find top-level const / var / let in s3
lines = s3.split('\n')
print(f"Script 3 has {len(lines)} lines")
for i, line in enumerate(lines[:50]):
    if any(line.startswith(pfx) for pfx in ['const ', 'let ', 'var ', 'function ']):
        print(f"  Line {i+1}: {line[:100]} (len: {len(line)})")

# Find any line in s3 that is huge (> 100,000 chars)
print("\nHuge lines in Script 3 (> 10,000 chars):")
for i, line in enumerate(lines):
    if len(line) > 10000:
        print(f"  Line {i+1}: starts with {repr(line[:60])} ... length: {len(line):,}")
