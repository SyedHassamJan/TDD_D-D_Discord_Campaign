with open('index.html', 'r', encoding='utf-8', errors='ignore') as f:
    for idx, line in enumerate(f, 1):
        if 'factions' in line.lower() and len(line) < 500:
            print(f"L{idx}: {line.strip()[:150]}")
        elif 'faction' in line.lower() and ('render' in line or 'list' in line or 'table' in line or 'board' in line) and len(line) < 500:
            print(f"L{idx}: {line.strip()[:150]}")
