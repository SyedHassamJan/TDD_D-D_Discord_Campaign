import re

with open('index.html', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

print(f"Total file size: {len(text):,} chars")

# Find all script tags or large blocks
scripts = list(re.finditer(r'<script[^>]*>(.*?)</script>', text, re.DOTALL))
print(f"Found {len(scripts)} <script> tags:")
for i, s in enumerate(scripts):
    tag = text[s.start():text.find('>', s.start())+1]
    content_len = len(s.group(1))
    print(f"  Script {i+1}: {tag} -> length: {content_len:,} chars")

# Check if there are other huge blocks (style, audio, base64 data URIs)
data_uris = list(re.finditer(r'data:[^"\';\s]+', text))
print(f"Found {len(data_uris)} data URIs:")
# group by mime
mime_lengths = {}
for u in data_uris:
    val = u.group(0)
    mime = val[:30]
    mime_lengths[mime] = mime_lengths.get(mime, 0) + len(val)

for m, l in sorted(mime_lengths.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"  {m}... total chars: {l:,}")
