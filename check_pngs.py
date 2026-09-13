import struct
import os

def get_png_info(filepath):
    if not os.path.exists(filepath):
        return "File not found"
    with open(filepath, "rb") as f:
        sig = f.read(8)
        if sig != b"\x89PNG\r\n\x1a\n":
            return f"Not a PNG (sig={sig!r})"
        length, chunk_type = struct.unpack(">I4s", f.read(8))
        if chunk_type == b"IHDR":
            w, h, depth, color_type, comp, filt, inter = struct.unpack(">IIBBBBB", f.read(13))
            return f"Width: {w}, Height: {h}, BitDepth: {depth}, ColorType: {color_type}"
    return "Unknown"

for name in ["test.png", "Heightmap-layer-Middle-earth-V2.png", "Satellite-layer-Middle-earth-V2.png", "map_b64.png"]:
    p = os.path.join("map_assets_extracted", name)
    print(f"{name}: {get_png_info(p)}")
