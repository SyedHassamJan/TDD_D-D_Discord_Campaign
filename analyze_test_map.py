import os
from PIL import Image
from collections import Counter

test_path = os.path.join("map_assets_extracted", "test.png")
height_path = os.path.join("map_assets_extracted", "Heightmap-layer-Middle-earth-V2.png")
sat_path = os.path.join("map_assets_extracted", "Satellite-layer-Middle-earth-V2.png")

im_test = Image.open(test_path)
im_height = Image.open(height_path)
im_sat = Image.open(sat_path)

print(f"test.png: size={im_test.size}, mode={im_test.mode}")
print(f"Heightmap: size={im_height.size}, mode={im_height.mode}")
print(f"Satellite: size={im_sat.size}, mode={im_sat.mode}")

# Check colors in test.png
rgb_test = im_test.convert("RGB")
colors = rgb_test.getcolors(maxcolors=1000000)
if colors is None:
    print("More than 1,000,000 colors! Might have antialiasing or JPEG artifacts or gradients.")
    # Sample down or count unique colors
    data = list(rgb_test.getdata())
    print(f"Total pixels: {len(data)}")
    counts = Counter(data)
    print(f"Unique colors count: {len(counts)}")
    print("Top 30 most frequent colors:")
    for col, cnt in counts.most_common(30):
        hex_col = "#{:02x}{:02x}{:02x}".format(*col)
        print(f"  {hex_col} ({col}): {cnt} pixels ({cnt/len(data)*100:.2f}%)")
else:
    print(f"Unique colors: {len(colors)}")
    colors.sort(key=lambda x: x[0], reverse=True)
    print("Top 30 colors:")
    total_px = im_test.size[0] * im_test.size[1]
    for cnt, col in colors[:30]:
        hex_col = "#{:02x}{:02x}{:02x}".format(*col)
        print(f"  {hex_col} ({col}): {cnt} pixels ({cnt/total_px*100:.2f}%)")
