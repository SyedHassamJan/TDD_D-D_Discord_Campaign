with open("index.html", "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

print("index.html total length:", len(text))
for name in ["MAP_B64", "TERRAIN_B64", "SHADE_B64", "mapdata", "campaign.json"]:
    pos = 0
    count = 0
    while True:
        pos = text.find(name, pos)
        if pos == -1:
            break
        print(f"Found '{name}' at pos {pos}, preview: {text[pos:pos+60]!r}")
        pos += len(name)
        count += 1
        if count >= 3:
            break
