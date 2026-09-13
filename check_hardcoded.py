with open("index.html", "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

# Check for hardcoded province names
old_provinces = ["Santiago", "Toledo", "Cordoba", "Sevilla", "Granada", "Barcelona"]
for p in old_provinces:
    count = text.count(f'"{p}"') + text.count(f"'{p}'")
    print(f"Occurrences of {p}: {count}")

# Check where mapdata is used
print("Number of mapdata occurrences:", text.count("mapdata"))
