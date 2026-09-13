with open("index.html", "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

pos = text.find("loadImg(\"data:image/jpeg;base64,\"+SHADE_B64)")
if pos != -1:
    print("Around loadImg:", text[pos-300:pos+1500])
