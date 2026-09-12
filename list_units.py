import os

factions = ['Rohan', 'Woodland Realm', 'Mordor', 'Lothlorien', 'Imraldris', 'Lostladen Tribes']
for f in factions:
    p = os.path.join('Unit Icons', f)
    files = sorted(os.listdir(p))
    print(f"=== {f} ({len(files)} files) ===")
    for fn in files:
        print(" ", fn)
