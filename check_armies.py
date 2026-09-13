import json

with open("campaign.json", "r", encoding="utf-8") as f:
    camp = json.load(f)

armies = camp.get("armies", [])
print(f"Total armies: {len(armies)}")
if armies:
    print("Sample army 0:", json.dumps(armies[0], indent=2))
