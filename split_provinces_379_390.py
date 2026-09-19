"""Split the disconnected painted islands for Provinces 379 and 390 safely."""
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
PAGES = (ROOT / "gm.html", ROOT / "index.html")
COLOURS = ((233, 30, 99), (0, 121, 107), (255, 152, 0), (121, 85, 72), (3, 169, 244))
SPLITS = {
    "Province_379": {"id": "Osgiliath", "modern": "Osgiliath"},
    "Province_390": {"id": "Province_390_split_1", "modern": "Province 390 — separated tile 1"},
}


def rgb(value: str) -> tuple[int, int, int]:
    return tuple(bytes.fromhex(value[1:]))


def hex_value(value: tuple[int, int, int]) -> str:
    return "#%02x%02x%02x" % value


def components(mask: np.ndarray) -> list[np.ndarray]:
    """Find four-connected areas of exactly one province colour."""
    height, width = mask.shape
    remaining = set(np.flatnonzero(mask).tolist())
    found: list[np.ndarray] = []
    while remaining:
        start = remaining.pop()
        stack, cells = [start], [start]
        while stack:
            point = stack.pop()
            x, y = point % width, point // width
            neighbours = (point - 1 if x else -1, point + 1 if x + 1 < width else -1,
                          point - width if y else -1, point + width if y + 1 < height else -1)
            for other in neighbours:
                if other in remaining:
                    remaining.remove(other)
                    stack.append(other)
                    cells.append(other)
        found.append(np.array(cells, dtype=np.int64))
    return sorted(found, key=len, reverse=True)


def rebuild_adjacency(state: dict, pixels: np.ndarray) -> None:
    codes = ((pixels[:, :, 0].astype(np.uint32) << 16) |
             (pixels[:, :, 1].astype(np.uint32) << 8) | pixels[:, :, 2].astype(np.uint32))
    by_code = {int(province["hex"][1:], 16): province for province in state["provinces"]}
    links: dict[int, set[int]] = defaultdict(set)
    for left, right in ((codes[:, :-1], codes[:, 1:]), (codes[:-1, :], codes[1:, :])):
        mask = (left != 0) & (right != 0) & (left != right)
        for first, second in np.unique(np.stack((np.minimum(left[mask], right[mask]),
                                                  np.maximum(left[mask], right[mask])), axis=1), axis=0):
            links[int(first)].add(int(second))
            links[int(second)].add(int(first))
    for code, province in by_code.items():
        province["adj"] = sorted(by_code[neighbour]["id"] for neighbour in links[code])


def update_embedded_map(state: dict) -> None:
    payload = json.dumps(state, separators=(",", ":"), ensure_ascii=False)
    for page in PAGES:
        text = page.read_text(encoding="utf-8-sig")
        updated, count = re.subn(r'(<script id="mapdata" type="application/json">).*?(</script>)',
                                 lambda m: m.group(1) + payload + m.group(2), text, count=1, flags=re.S)
        if count != 1:
            raise RuntimeError(f"Map data is missing from {page.name}")
        page.write_text(updated, encoding="utf-8")
    encoded = base64.b64encode(MAP.read_bytes()).decode("ascii")
    asset = ROOT / "assets" / "map_assets.js"
    text = asset.read_text(encoding="utf-8")
    updated, count = re.subn(r'const MAP_B64="[^"]*";', f'const MAP_B64="{encoded}";', text, count=1)
    if count != 1:
        raise RuntimeError("Could not update map asset")
    asset.write_text(updated, encoding="utf-8")


def main() -> None:
    state = json.loads(CAMPAIGN.read_text(encoding="utf-8"))
    image = Image.open(MAP).convert("RGB")
    pixels = np.asarray(image).copy()
    used = {tuple(colour) for colour in pixels.reshape(-1, 3)}
    known_ids = {province["id"] for province in state["provinces"]}
    created: list[str] = []

    for source_id, details in SPLITS.items():
        if details["id"] in known_ids:
            raise RuntimeError(f"{details['id']} already exists; refusing to split twice")
        source = next((province for province in state["provinces"] if province["id"] == source_id), None)
        if not source:
            raise RuntimeError(f"Missing {source_id}")
        parts = [part for part in components(np.all(pixels == rgb(source["hex"]), axis=2)) if len(part) >= 100]
        if len(parts) < 2:
            raise RuntimeError(f"{source_id} does not have two substantial disconnected areas")
        replacement = next((colour for colour in COLOURS if colour not in used), None)
        if replacement is None:
            raise RuntimeError("No safe unused province colour is available")
        split = copy.deepcopy(source)
        split.update({"id": details["id"], "modern": details["modern"], "hex": hex_value(replacement), "adj": []})
        # Retain the largest existing island under the original province. Every
        # smaller disconnected painted island becomes the new selectable tile.
        for part in parts[1:]:
            ys, xs = np.divmod(part, pixels.shape[1])
            pixels[ys, xs] = replacement
        state["provinces"].append(split)
        known_ids.add(split["id"])
        used.add(replacement)
        created.append(f"{source_id} -> {split['id']}")

    rebuild_adjacency(state, pixels)
    Image.fromarray(pixels, mode="RGB").save(MAP, format="PNG", optimize=True)
    CAMPAIGN.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    update_embedded_map(state)
    print("Split " + "; ".join(created))


if __name__ == "__main__":
    main()
