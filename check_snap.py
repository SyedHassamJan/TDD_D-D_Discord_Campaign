with open("index.html", "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

pos = text.find("const START_SNAP=")
if pos != -1:
    print(text[pos:pos+300])
