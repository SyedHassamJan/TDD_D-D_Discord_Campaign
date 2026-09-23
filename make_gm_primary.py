import shutil

# 1. Preserve player view as player.html
shutil.copyfile("index.html", "player.html")
print("Preserved index.html as player.html")

# 2. Read gm.html
with open("gm.html", "r", encoding="utf-8") as f:
    gm_content = f.read()

# Auto-restore GM mode if store has gmOK == '1'
old_target = "function setGM(on){"
if "/* Auto-restore GM */" not in gm_content:
    new_target = "/* Auto-restore GM */\nsetTimeout(function(){try{if(store.get('gmOK')==='1')setGM(true);}catch(e){}},50);\nfunction setGM(on){"
    gm_content = gm_content.replace(old_target, new_target, 1)
    with open("gm.html", "w", encoding="utf-8") as f:
        f.write(gm_content)
    print("Added auto-restore GM to gm.html")

# 3. Overwrite index.html with gm.html content
with open("index.html", "w", encoding="utf-8") as f:
    f.write(gm_content)
print("Overwrote index.html with gm.html content")
