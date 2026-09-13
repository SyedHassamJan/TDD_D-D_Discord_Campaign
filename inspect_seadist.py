with open("index.html", "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

pos = 0
while True:
    pos = text.find("seaDist", pos)
    if pos == -1:
        break
    print("--- Found seaDist at", pos, "---")
    print(text[pos-100:pos+300])
    pos += len("seaDist")
