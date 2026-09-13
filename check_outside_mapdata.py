with open("index.html", "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

# remove script id="mapdata"
import re
text_no_mapdata = re.sub(r'<script id="mapdata"[^>]*>.*?</script>', '', text, flags=re.DOTALL)
old_provinces = ["Santiago", "Toledo", "Sevilla", "Granada", "Barcelona"]
for p in old_provinces:
    count = text_no_mapdata.count(f'"{p}"') + text_no_mapdata.count(f"'{p}'")
    print(f"Occurrences of {p} outside mapdata: {count}")
