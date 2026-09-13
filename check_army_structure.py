with open("index.html", "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

pos = 0
for _ in range(5):
    pos = text.find("S.armies", pos)
    if pos == -1:
        break
    print("Found S.armies at:", pos)
    print(text[pos:pos+200])
    pos += len("S.armies")
