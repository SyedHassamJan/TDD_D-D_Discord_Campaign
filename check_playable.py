with open("index.html", "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

import re
matches = re.findall(r'(\w+\.playable[^\n;]+)', text)
for m in set(matches[:20]):
    print("playable check:", m)
