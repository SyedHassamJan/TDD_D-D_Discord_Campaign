from PIL import Image
import numpy as np

im_test = Image.open("map_assets_extracted/test.png").convert("RGB")
im_sat = Image.open("map_assets_extracted/Satellite-layer-Middle-earth-V2.png").convert("RGB")

print("test size:", im_test.size)
print("sat size:", im_sat.size)

# Let's find distinct features like coastlines or inland lakes in test vs sat
# In test.png, where is the sea / coast?
# Let's sample a small patch of satellite in test.png that is completely unpainted
# and find where it matches in im_sat!
patch = im_test.crop((2000, 500, 2200, 700))
patch_np = np.array(patch)

# Let's search in im_sat if there is a match or if resizing sat to 3357x2687 matches perfectly
sat_resized = im_sat.resize((3357, 2687), Image.Resampling.LANCZOS)
sat_resized_patch = np.array(sat_resized.crop((2000, 500, 2200, 700)))

diff = np.abs(patch_np.astype(float) - sat_resized_patch.astype(float))
print("Diff on (2000, 500, 2200, 700) patch:", np.mean(diff), np.max(diff))

# Let's inspect test corner pixels vs sat resized corner pixels
print("Test (2000, 500) RGB:", patch_np[0, 0])
print("Sat resized (2000, 500) RGB:", sat_resized_patch[0, 0])

# What if test.png was scaled with Nearest Neighbor or Bicubic?
for resample, name in [
    (Image.Resampling.NEAREST, "NEAREST"),
    (Image.Resampling.BILINEAR, "BILINEAR"),
    (Image.Resampling.BICUBIC, "BICUBIC"),
    (Image.Resampling.LANCZOS, "LANCZOS")
]:
    sat_res = im_sat.resize((3357, 2687), resample)
    diff = np.abs(patch_np.astype(float) - np.array(sat_res.crop((2000, 500, 2200, 700))).astype(float))
    print(f"Resample {name}: mean diff={np.mean(diff):.2f}")
