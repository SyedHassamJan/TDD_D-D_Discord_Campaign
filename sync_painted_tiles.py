"""Sync the supplied painted map into the campaign without duplicating province state.

Black pixels are deliberately left without province records, making them impassable.
"""
from __future__ import annotations

import base64
import copy
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
SOURCE = Path(r"C:\Users\HP840G~1\AppData\Local\Temp\codex-clipboard-4f4b4a3c-fe1a-40ea-9885-006bd69dc623.png")
MAP = ROOT / "map_assets_extracted" / "map_b64.png"
BACKUP = ROOT / "map_assets_extracted" / "map_b64.prepaint-sync-backup.png"
CAMPAIGN = ROOT / "campaign.json"
BLACK = (0, 0, 0)


def rgb_hex(rgb: tuple[int, int, int]) -> str:
    return "#%02x%02x%02x" % rgb


def main_palette(image: Image.Image) -> list[tuple[int, int, int]]:
    """Only large flat paint colours are tiles; fringe colours are anti-aliasing."""
    counts = image.getcolors(image.width * image.height)
    return [rgb for count, rgb in counts if rgb != BLACK and count >= 500]


def sync() -> None:
    print("Loading painted map…", flush=True)
    if not SOURCE.exists():
        raise FileNotFoundError(f"Painted-map source is missing: {SOURCE}")
    new = Image.open(SOURCE).convert("RGB")
    old = Image.open(MAP).convert("RGB")
    if new.size != old.size:
        raise ValueError(f"Map dimensions differ: new={new.size}, current={old.size}")

    palette = main_palette(new)
    if not palette:
        raise ValueError("No painted tile colours were found")
    palette_set = set(palette)
    print(f"Found {len(palette)} painted tile colours; normalising edges…", flush=True)

    state = json.loads(CAMPAIGN.read_text(encoding="utf-8"))
    old_by_rgb = {tuple(bytes.fromhex(p["hex"][1:])): p for p in state["provinces"]}

    # Canonicalise all edge anti-aliasing to a tile's flat paint colour. This keeps
    # the canvas selectable by exact colour while preserving literal black barriers.
    cache: dict[tuple[int, int, int], tuple[int, int, int]] = {BLACK: BLACK}

    def canonical(rgb: tuple[int, int, int]) -> tuple[int, int, int]:
        result = cache.get(rgb)
        if result is None:
            result = min(palette, key=lambda c: sum((rgb[i] - c[i]) ** 2 for i in range(3)))
            cache[rgb] = result
        return result

    src = new.tobytes()
    previous = old.tobytes()
    output = bytearray(len(src))
    overlaps: dict[tuple[int, int, int], Counter[str]] = defaultdict(Counter)
    for i in range(0, len(src), 3):
        colour = canonical((src[i], src[i + 1], src[i + 2]))
        output[i:i + 3] = bytes(colour)
        old_record = old_by_rgb.get((previous[i], previous[i + 1], previous[i + 2]))
        if colour != BLACK and old_record:
            overlaps[colour][old_record["id"]] += 1
    print("Migrating province records…", flush=True)

    old_by_id = {p["id"]: p for p in state["provinces"]}
    best_old = {
        colour: counts.most_common(1)[0][0]
        for colour, counts in overlaps.items()
        if counts
    }
    # A pre-existing province can only keep its full record on one new tile.
    # Other split pieces receive the same owner but no duplicated buildings/queues.
    winner: dict[str, tuple[int, int, int]] = {}
    for colour, old_id in best_old.items():
        previous_winner = winner.get(old_id)
        if previous_winner is None or overlaps[colour][old_id] > overlaps[previous_winner][old_id]:
            winner[old_id] = colour

    used_ids: set[str] = set()
    next_id = 1

    def fresh_id() -> str:
        nonlocal next_id
        while True:
            candidate = f"Province_{next_id}"
            next_id += 1
            if candidate not in old_by_id and candidate not in used_ids:
                return candidate

    records: list[dict] = []
    record_for_colour: dict[tuple[int, int, int], dict] = {}
    for colour in palette:
        source_id = best_old.get(colour)
        source_record = old_by_id.get(source_id) if source_id else None
        if source_record and winner.get(source_id) == colour:
            record = copy.deepcopy(source_record)
        else:
            record_id = fresh_id()
            inherited_owner = source_record.get("owner", "") if source_record else ""
            record = {
                "id": record_id,
                "modern": record_id.replace("_", " "),
                "hex": rgb_hex(colour),
                "playable": True,
                "owner": inherited_owner,
                "tier": 2,
                "terrain": "plains",
                "value": 1000,
                "move": 2,
                "garrison": 1500,
                "bld": [],
                "adj": [],
            }
        record["hex"] = rgb_hex(colour)
        record["playable"] = True
        record["adj"] = []
        used_ids.add(record["id"])
        records.append(record)
        record_for_colour[colour] = record

    # Build movement links only where coloured tiles directly touch. Black pixels
    # are absent from this graph, so painted impassable regions block movement.
    width, height = new.size
    pixels = np.frombuffer(output, dtype=np.uint8).reshape(height, width, 3)
    codes = (
        (pixels[:, :, 0].astype(np.uint32) << 16)
        | (pixels[:, :, 1].astype(np.uint32) << 8)
        | pixels[:, :, 2].astype(np.uint32)
    )
    code_to_colour = {(r << 16) | (g << 8) | b: (r, g, b) for r, g, b in palette}
    neighbours: dict[tuple[int, int, int], set[tuple[int, int, int]]] = defaultdict(set)
    print("Rebuilding movement links…", flush=True)
    for left, right in ((codes[:, :-1], codes[:, 1:]), (codes[:-1, :], codes[1:, :])):
        mask = (left != 0) & (right != 0) & (left != right)
        low = np.minimum(left[mask], right[mask])
        high = np.maximum(left[mask], right[mask])
        for a_code, b_code in np.unique(np.stack((low, high), axis=1), axis=0):
            a, b = code_to_colour[int(a_code)], code_to_colour[int(b_code)]
            neighbours[a].add(b)
            neighbours[b].add(a)
    for colour, record in record_for_colour.items():
        record["adj"] = sorted(record_for_colour[n]["id"] for n in neighbours[colour])

    if not BACKUP.exists():
        old.save(BACKUP, format="PNG")
    out_image = Image.frombytes("RGB", new.size, bytes(output))
    out_image.save(MAP, format="PNG", optimize=True)
    state["provinces"] = records
    payload = json.dumps(state, separators=(",", ":"), ensure_ascii=False)
    CAMPAIGN.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for page in (ROOT / "gm.html", ROOT / "index.html"):
        text = page.read_text(encoding="utf-8")
        text, changed = re.subn(
            r'(<script id="mapdata" type="application/json">).*?(</script>)',
            lambda m: m.group(1) + payload + m.group(2),
            text,
            count=1,
            flags=re.DOTALL,
        )
        if changed != 1:
            raise RuntimeError(f"Could not update mapdata in {page.name}")
        page.write_text(text, encoding="utf-8")
    encoded = base64.b64encode(MAP.read_bytes()).decode("ascii")
    asset = ROOT / "assets" / "map_assets.js"
    text = asset.read_text(encoding="utf-8")
    text, changed = re.subn(r'const MAP_B64="[^"]*";', f'const MAP_B64="{encoded}";', text, count=1)
    if changed != 1:
        raise RuntimeError("Could not update MAP_B64")
    asset.write_text(text, encoding="utf-8")

    preserved = [p for p in records if p.get("owner")]
    print(f"Synced {len(records)} playable tiles; black regions are impassable.")
    print(f"Preserved ownership on {len(preserved)} tiles: {', '.join(f'{p['id']}={p['owner']}' for p in preserved) or 'none'}")
    print(f"Built {sum(len(p['adj']) for p in records) // 2} movement links.")


if __name__ == "__main__":
    sync()
