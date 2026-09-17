"""Split the disconnected pieces of Province_455 into separate selectable tiles."""
from __future__ import annotations

import base64
import copy
import json
import re
from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
MAP = ROOT / "map_assets_extracted" / "map_b64.png"
CAMPAIGN = ROOT / "campaign.json"
TARGET = "Province_455"


def hex_rgb(value: str) -> tuple[int, int, int]:
    return tuple(bytes.fromhex(value[1:]))


def rgb_hex(value: tuple[int, int, int]) -> str:
    return "#%02x%02x%02x" % value


def components(mask: np.ndarray) -> list[np.ndarray]:
    """Return four-connected components for one tile colour."""
    height, width = mask.shape
    remaining = set(np.flatnonzero(mask).tolist())
    found: list[np.ndarray] = []
    while remaining:
        start = remaining.pop()
        stack = [start]
        cells = [start]
        while stack:
            point = stack.pop()
            x, y = point % width, point // width
            for other in (
                point - 1 if x else -1,
                point + 1 if x + 1 < width else -1,
                point - width if y else -1,
                point + width if y + 1 < height else -1,
            ):
                if other in remaining:
                    remaining.remove(other)
                    stack.append(other)
                    cells.append(other)
        found.append(np.array(cells, dtype=np.int64))
    return sorted(found, key=len, reverse=True)


def update_mapdata(state: dict) -> None:
    payload = json.dumps(state, separators=(",", ":"), ensure_ascii=False)
    for page in (ROOT / "gm.html", ROOT / "index.html"):
        text = page.read_text(encoding="utf-8")
        text, changed = re.subn(
            r'(<script id="mapdata" type="application/json">).*?(</script>)',
            lambda m: m.group(1) + payload + m.group(2), text, count=1, flags=re.DOTALL
        )
        if changed != 1:
            raise RuntimeError(f"Could not update {page.name}")
        page.write_text(text, encoding="utf-8")
    encoded = base64.b64encode(MAP.read_bytes()).decode("ascii")
    asset = ROOT / "assets" / "map_assets.js"
    text = asset.read_text(encoding="utf-8")
    text, changed = re.subn(r'const MAP_B64="[^"]*";', f'const MAP_B64="{encoded}";', text, count=1)
    if changed != 1:
        raise RuntimeError("Could not update MAP_B64")
    asset.write_text(text, encoding="utf-8")


def rebuild_adjacency(state: dict, pixels: np.ndarray) -> None:
    height, width, _ = pixels.shape
    codes = (
        (pixels[:, :, 0].astype(np.uint32) << 16)
        | (pixels[:, :, 1].astype(np.uint32) << 8)
        | pixels[:, :, 2].astype(np.uint32)
    )
    by_code = {int(p["hex"][1:], 16): p for p in state["provinces"]}
    links: dict[int, set[int]] = defaultdict(set)
    for left, right in ((codes[:, :-1], codes[:, 1:]), (codes[:-1, :], codes[1:, :])):
        mask = (left != 0) & (right != 0) & (left != right)
        low = np.minimum(left[mask], right[mask])
        high = np.maximum(left[mask], right[mask])
        for first, second in np.unique(np.stack((low, high), axis=1), axis=0):
            links[int(first)].add(int(second))
            links[int(second)].add(int(first))
    for code, province in by_code.items():
        province["adj"] = sorted(by_code[neighbour]["id"] for neighbour in links[code])


def main() -> None:
    state = json.loads(CAMPAIGN.read_text(encoding="utf-8"))
    original = next((p for p in state["provinces"] if p["id"] == TARGET), None)
    if not original:
        raise RuntimeError(f"{TARGET} is not in the current campaign")
    image = Image.open(MAP).convert("RGB")
    pixels = np.asarray(image).copy()
    colour = hex_rgb(original["hex"])
    parts = components(np.all(pixels == colour, axis=2))
    real_parts = [part for part in parts if len(part) >= 100]
    if len(real_parts) < 2:
        raise RuntimeError(f"{TARGET} has no second substantial disconnected component")
    used = {tuple(rgb) for rgb in pixels.reshape(-1, 3)}
    replacement = next(c for c in ((63, 81, 181), (156, 39, 176), (0, 150, 136)) if c not in used)
    split = copy.deepcopy(original)
    existing = {p["id"] for p in state["provinces"]}
    number = 1
    while f"Province_455_split_{number}" in existing:
        number += 1
    split["id"] = f"Province_455_split_{number}"
    split["modern"] = f"Province 455 — separated tile {number}"
    split["hex"] = rgb_hex(replacement)
    split["adj"] = []
    # Largest piece remains Province_455; every other meaningful island is independent.
    for part in real_parts[1:]:
        ys, xs = np.divmod(part, pixels.shape[1])
        pixels[ys, xs] = replacement
    # A two-pixel artefact was also sharing the yellow colour. It is not a tile;
    # make it impassable instead of accidentally producing a third province.
    for part in parts:
        if len(part) < 100:
            ys, xs = np.divmod(part, pixels.shape[1])
            pixels[ys, xs] = (0, 0, 0)
    state["provinces"].append(split)
    rebuild_adjacency(state, pixels)
    Image.fromarray(pixels, mode="RGB").save(MAP, format="PNG", optimize=True)
    CAMPAIGN.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    update_mapdata(state)
    print(f"Split {TARGET}: {len(real_parts)} separate painted areas; created {split['id']} ({split['hex']}).")


if __name__ == "__main__":
    main()
