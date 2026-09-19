"""Build the campaign roster from the Dawnless Days CSV source of truth."""
from __future__ import annotations

import csv
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).parent
SOURCE = Path(os.environ.get("DAWNLESS_DAYS_CSV", ROOT / "dawnless_days.csv"))
if not SOURCE.exists():
    SOURCE = Path(r"D:\downlaods\dawnless_days.csv")
PAGES = [ROOT / "gm.html", ROOT / "index.html"]

# The map uses these display names/ids.  Keeping them canonical means a roster
# can be selected for recruitment even when its faction has no banner yet.
FACTION_NAMES = {
    "khand": "Khand", "woodland realm": "Woodland Realm", "rohan": "Rohan",
    "rhurrim": "Rhurrim", "rhudaur": "Rhudaur", "rachrohir": "Rachrohir",
    "mordor": "Mordor", "lothlorien": "Lothlorien",
    "lostladen tribes": "Lostladen Tribes", "lindon": "Lindon",
    "khazad-dum": "Khazad-dum", "isengard": "Isengard", "iron hills": "Iron Hills",
    "imladris": "Imraldris", "gundabad": "Gundabad", "gondor": "Gondor",
    "goblin": "Goblins", "ered mithirin": "Ered Mithrin", "ered luin": "Ered Luin",
    "erebor": "Erebor", "dunleding tribes": "Dunlendings", "dorwinion": "Dorwinion",
    "dol guldor": "Dol Gul Dur", "dol amroth": "Dol Amroth", "dale": "Dale",
    "anduin vale": "Anduin Vale", "corsairs of umbar": "Umbar",
}

PALETTE = ["#7A5C2E", "#2E7D32", "#C5A059", "#7C3030", "#6D5A7B", "#904A28",
           "#8B0000", "#D4AF37", "#D27D2D", "#81C784", "#747474", "#E5E5E5",
           "#A46F35", "#4682B4", "#3E5B31", "#607D3B", "#388E3C", "#67839A",
           "#899B8D", "#BB8B2C", "#795548", "#9C27B0", "#4A154B", "#4E86B8"]

# The campaign has spun these regional hosts out of their former umbrella
# factions.  The source CSV remains authoritative for their values; this only
# decides which in-game banner recruits each named unit.
ROSTER_REALMS = {
    "(aor)-balcoth nobles": "Balcoth",
    "(aor)-balcoth raiders": "Balcoth",
    "(aor)-balcoth spears": "Balcoth",
    "(aor)-haerrim infantry": "Haerrim",
    "(aor)-haerrim outriders": "Haerrim",
    "(aor)-feredrim rangers": "Feredrim",
    "(aor)-feredrim woodsmen": "Feredrim",
    "(aor)-carrock wardens": "Beorings",
    "(aor)-pass sentries": "Beorings",
    "(aor)-beoring warroirs": "Beorings",
    "(aor)-eotheod footmen": "Eotheod",
    "(aor)-eotheod cavalry": "Eotheod",
    "(aor)-eotheod nobles": "Eotheod",
    "(aor)-eotheod lancers": "Eotheod",
    "(aor)-eotheod horse archers": "Eotheod",
    "(aor)-eotheod outriders": "Eotheod",
    "(aor)-woodland axemen": "GreenWood",
    "(aor)-greenwood rangers": "GreenWood",
    "(aor)-stoor shirrifs": "GreenWood",
    "(aor)-warlord's pillagers": "Drudain",
    "(aor)-warlord's champions": "Drudain",
    "(aor)-warlord's crossbows": "Drudain",
    "(aor)-warlord cavalry": "Drudain",
    "(mercs)-orthanc servants": "Northern Endwaith",
    "elder spears": "Southern Endwaith",
    "elder riders": "Southern Endwaith",
}

# This requested name is not present in Dawnless Days.  Its standard Tier 2
# missile-infantry price/upkeep mirrors the nearest existing woodland troop.
CUSTOM_UNITS = [
    {"faction": "GreenWood", "name": "GreenWood Foresters", "tier": 2,
     "cost": 925, "upkeep": 462.5, "class": "inf_mis",
     "class_name": "Missile Infantry", "category": "infantry",
     "category_name": "Infantry", "men": 120, "missile": True, "mounted": False},
]


def key_for(faction: str, name: str, seen: set[str]) -> str:
    base = re.sub(r"[^a-z0-9]+", "_", f"{faction}_{name}".lower()).strip("_")
    key, suffix = base, 2
    while key in seen:
        key = f"{base}_{suffix}"
        suffix += 1
    seen.add(key)
    return key


def unit_shape(name: str, tier: int, cost: float) -> dict:
    low = name.lower()
    artillery = any(x in low for x in ("onager", "trebuchet", "ballista", "scorpio"))
    hero = tier == 4 and any(x in low for x in ("king", "prince", "lord", "sauron", "nazgul", "witch", "theoden", "eomer", "boromir", "balin", "gimli", "gloin", "dain", "imrahil", "khamul", "arbelzagar", "vinelord", "erkenbrand", "winfried", "theodred", "khahar", "khavar", "tuff"))
    cavalry = any(x in low for x in ("rider", "riders", "knight", "knights", "cavalry", "horse", "warg", "cataphract", "chariot", "camel", "mumak", "out rider", "outrider", "eored", "patroller"))
    missile = any(x in low for x in ("archer", "archers", "bow", "crossbow", "crossbows", "hunter", "hunters", "ranger", "rangers", "marksmen", "marksman", "slinger", "slingers", "scout", "scouts", "lookout", "thrower", "trackers"))
    pike = "pike" in low
    spear = any(x in low for x in ("spear", "spears", "halberd", "halberds", "glaive", "glaives", "sentinel", "sentinels", "warden", "wardens"))
    if artillery:
        category, category_name, cls, class_name, men = "artillery", "Artillery", "art", "Artillery", 40
    elif hero:
        category, category_name, cls, class_name, men = "infantry", "Infantry", "com", "Command", 60
    elif cavalry and missile:
        category, category_name, cls, class_name, men = "cavalry", "Cavalry", "cav_mis", "Missile Cavalry", 80
    elif cavalry:
        category, category_name, cls, class_name, men = "cavalry", "Cavalry", "cav_shk", "Shock Cavalry", 80
    elif missile:
        category, category_name, cls, class_name, men = "infantry", "Infantry", "inf_mis", "Missile Infantry", 120
    elif pike:
        category, category_name, cls, class_name, men = "infantry", "Infantry", "inf_pik", "Pike Infantry", 150
    elif spear:
        category, category_name, cls, class_name, men = "infantry", "Infantry", "inf_spr", "Spear Infantry", 140
    else:
        category, category_name, cls, class_name, men = "infantry", "Infantry", "inf_mel", "Melee Infantry", 120
    return {"category": category, "category_name": category_name, "class": cls,
            "class_name": class_name, "men": men, "missile": missile, "mounted": cavalry,
            # Dawnless Days roster: every unit pays exactly half of its
            # recruitment cost as its base seasonal upkeep.  Keep .5 values
            # intact so odd-numbered costs match the source CSV precisely.
            "upkeep": cost * 0.50}


def parse_roster() -> tuple[list[dict], list[str]]:
    seen: set[str] = set()
    relocated_seen: set[tuple[str, str]] = set()
    units: list[dict] = []
    factions: list[str] = []
    with SOURCE.open(encoding="utf-8-sig", newline="") as source:
        for row in csv.DictReader(source):
            raw_faction = (row.get("Faction") or "").strip()
            name = (row.get("Unit") or "").strip()
            if not raw_faction or not name:
                continue
            status = (row.get("Status") or "").strip()
            if status:
                name = f"({status})-{name}"
            relocated_faction = ROSTER_REALMS.get(name.lower())
            faction = relocated_faction or FACTION_NAMES.get(raw_faction.lower(), raw_faction)
            # A few CSV entries exist under more than one old umbrella realm.
            # Their new regional roster needs one card per requested unit.
            relocated_key = (faction, name.casefold())
            if relocated_faction and relocated_key in relocated_seen:
                continue
            if relocated_faction:
                relocated_seen.add(relocated_key)
            if faction not in factions:
                factions.append(faction)
            tier = int((row.get("Tier") or "T4").strip().removeprefix("T"))
            cost_text = (row.get("Cost") or "").strip()
            upkeep_text = (row.get("Upkeep") or "").strip()
            # The source contains one Rhurrim mercenary row without a price.
            # Do not create a free unit when no authoritative value is supplied.
            if not cost_text or not upkeep_text:
                continue
            cost = float(cost_text)
            upkeep = float(upkeep_text)
            if cost.is_integer():
                cost = int(cost)
            shape = unit_shape(name, tier, cost)
            shape["upkeep"] = upkeep
            units.append({"faction": faction, "unit_key": key_for(faction, name, seen), "name": name,
                          "tier": str(tier), "cost": cost, **shape})
    for unit in CUSTOM_UNITS:
        faction = unit["faction"]
        if faction not in factions:
            factions.append(faction)
        units.append({"faction": faction, "unit_key": key_for(faction, unit["name"], seen),
                      "name": unit["name"], "tier": str(unit["tier"]), "cost": unit["cost"],
                      "upkeep": unit["upkeep"], "class": unit["class"],
                      "class_name": unit["class_name"], "category": unit["category"],
                      "category_name": unit["category_name"], "men": unit["men"],
                      "missile": unit["missile"], "mounted": unit["mounted"]})
    return units, factions


def replace_block(text: str, block_id: str, value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    pattern = rf'(<script id="{block_id}" type="application/json">).*?(</script>)'
    updated, count = re.subn(pattern, lambda m: m.group(1) + payload + m.group(2), text, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError(f"Could not find {block_id} in page")
    return updated


def main() -> None:
    units, faction_names = parse_roster()
    if len(units) < 500:
        raise RuntimeError(f"Parsed only {len(units)} units; refusing to replace roster")
    codex = {"cap": 20, "factions": [{"name": name} for name in faction_names], "units": units}

    for page in PAGES:
        text = page.read_text(encoding="utf-8")
        text = replace_block(text, "codexdata", codex)
        page.write_text(text, encoding="utf-8")
    print(f"Installed {len(units)} units across {len(faction_names)} factions.")


if __name__ == "__main__":
    main()
