import struct
import os

def get_jpeg_size(filepath):
    with open(filepath, 'rb') as f:
        f.seek(2)
        b = f.read(1)
        while b:
            while b != b'\xff':
                b = f.read(1)
            while b == b'\xff':
                b = f.read(1)
            if 0xc0 <= ord(b) <= 0xc3:
                f.read(3)
                h, w = struct.unpack(">HH", f.read(4))
                return w, h
            else:
                l = struct.unpack(">H", f.read(2))[0]
                f.read(l - 2)
            b = f.read(1)
    return None

for name in ["shade_b64.jpg", "terrain_b64.jpg"]:
    p = os.path.join("map_assets_extracted", name)
    print(f"{name}: {get_jpeg_size(p)}")
