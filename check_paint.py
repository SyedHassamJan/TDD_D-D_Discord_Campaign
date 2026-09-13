from PIL import Image
import numpy as np

im_test = Image.open("map_assets_extracted/test.png")
im_sat = Image.open("map_assets_extracted/Satellite-layer-Middle-earth-V2.png")

print("test.png info:", im_test.size, im_test.mode)

# Check alpha channel of test.png
if im_test.mode == "RGBA":
    r, g, b, a = im_test.split()
    extrema_a = a.getextrema()
    print("Alpha min/max:", extrema_a)
    # Check transparent pixels
    a_arr = np.array(a)
    trans = np.sum(a_arr == 0)
    print(f"Completely transparent pixels: {trans} / {a_arr.size} ({trans/a_arr.size*100:.2f}%)")

# Let's inspect where MS Paint colors or black lines are
# Let's find distinct solid color regions or what painted areas exist!
rgb = im_test.convert("RGB")
arr = np.array(rgb)

# Check black pixels (0,0,0)
black_mask = (arr[:,:,0] == 0) & (arr[:,:,1] == 0) & (arr[:,:,2] == 0)
print(f"Black pixels: {np.sum(black_mask)} ({np.sum(black_mask)/black_mask.size*100:.2f}%)")

# Check MS Paint palette colors:
# MS paint standard colors:
# (136, 0, 21) Dark red #880015
# (237, 28, 36) Red #ed1c24
# (255, 127, 39) Orange #ff7f27
# (255, 242, 0) Yellow #fff200
# (34, 177, 76) Green #22b14c
# (0, 162, 232) Turquoise #00a2e8
# (63, 72, 204) Indigo #3f48cc
# (163, 73, 164) Purple #a349a4
# (185, 122, 87) Brown #b97a57
# (255, 174, 201) Pink #ffaec9
# (255, 201, 14) Light yellow #ffc90e
# (181, 230, 29) Lime #b5e61d
# (153, 217, 234) Light turquoise #99d9ea
# (112, 146, 190) Blue gray #7092be
# (200, 191, 231) Lavender #c8bfe7
paint_colors = [
    (136, 0, 21),
    (237, 28, 36),
    (255, 127, 39),
    (255, 242, 0),
    (34, 177, 76),
    (0, 162, 232),
    (63, 72, 204),
    (163, 73, 164),
    (185, 122, 87),
    (255, 174, 201),
    (255, 201, 14),
    (181, 230, 29),
    (153, 217, 234),
    (112, 146, 190),
    (200, 191, 231),
    (255, 255, 255),
]

for c in paint_colors:
    mask = (arr[:,:,0] == c[0]) & (arr[:,:,1] == c[1]) & (arr[:,:,2] == c[2])
    count = np.sum(mask)
    if count > 0:
        hex_c = "#{:02x}{:02x}{:02x}".format(*c)
        print(f"Paint color {hex_c} {c}: {count} pixels ({count/black_mask.size*100:.2f}%)")
