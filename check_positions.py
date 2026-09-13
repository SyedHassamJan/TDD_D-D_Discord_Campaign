with open("index.html", "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

import re
text_no_mapdata = re.sub(r'<script id="mapdata"[^>]*>.*?</script>', '', text, flags=re.DOTALL)
for p in ["Santiago", "Toledo"]:
    pos = 0
    while True:
        pos = text_no_mapdata.find(f'"{p}"', pos)
        if pos == -1:
            break
        print(f"Found {p} at {pos}: {text_no_mapdata[pos-50:pos+100]!r}")
        pos += len(p)
