with open("index.html", "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

pos = 0
while True:
    pos = text.find("terrainImg", pos)
    if pos == -1:
        break
    print("--- Found terrainImg at", pos, "---")
    print(text[pos-100:pos+300])
    pos += len("terrainImg")

pos = 0
while True:
    pos = text.find("shadeData", pos)
    if pos == -1:
        break
    print("--- Found shadeData at", pos, "---")
    print(text[pos-100:pos+300])
    pos += len("shadeData")
