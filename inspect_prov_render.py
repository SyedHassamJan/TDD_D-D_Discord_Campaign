with open("index.html", "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

pos = 48001300
print(text[pos:pos+1500])
