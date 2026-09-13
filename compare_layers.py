import numpy as np
from PIL import Image

im_test = Image.open("map_assets_extracted/test.png").convert("RGB")
arr_test = np.array(im_test)
im_sat = Image.open("map_assets_extracted/Satellite-layer-Middle-earth-V2.png").convert("RGB")

print("test shape:", arr_test.shape) # (2687, 3357, 3)
print("sat size:", im_sat.size) # (2500, 2003)

# Notice: 3357 x 2687 vs 2500 x 2003
# 3357 / 2500 = 1.3428
# 2687 / 2003 = 1.3414877...
# They are ALMOST EXACTLY a 1.3415 ratio! Or test.png is a scaled version of Satellite-layer!
# Let's test resizing im_sat to (3357, 2687) and comparing with arr_test where arr_test is NOT black or painted!

im_sat_resized = im_sat.resize((3357, 2687), Image.Resampling.BILINEAR)
arr_sat = np.array(im_sat_resized)

# Let's find where arr_test is black or painted:
c_dark_red = (136, 0, 21)
c_red = (237, 28, 36)
c_brown = (185, 122, 87)

mask_dark_red = (arr_test[:,:,0] == 136) & (arr_test[:,:,1] == 0) & (arr_test[:,:,2] == 21)
mask_red = (arr_test[:,:,0] == 237) & (arr_test[:,:,1] == 28) & (arr_test[:,:,2] == 36)
mask_brown = (arr_test[:,:,0] == 185) & (arr_test[:,:,1] == 122) & (arr_test[:,:,2] == 87)
mask_black = (arr_test[:,:,0] == 0) & (arr_test[:,:,1] == 0) & (arr_test[:,:,2] == 0)

painted_mask = mask_dark_red | mask_red | mask_brown | mask_black
unpainted_mask = ~painted_mask

print(f"Unpainted pixels: {np.sum(unpainted_mask)} ({np.sum(unpainted_mask)/unpainted_mask.size*100:.2f}%)")

# Compare unpainted pixels with satellite image
diff = np.abs(arr_test[unpainted_mask].astype(int) - arr_sat[unpainted_mask].astype(int))
mean_diff = np.mean(diff)
print(f"Mean difference between test unpainted pixels and resized satellite image: {mean_diff:.2f}")

# Also check coordinates (bounding box and centroid) of the 3 painted regions
for name, m in [("Dark Red", mask_dark_red), ("Red", mask_red), ("Brown", mask_brown)]:
    ys, xs = np.where(m)
    if len(xs) > 0:
        print(f"{name}: count={len(xs)}, bounds=(x:[{xs.min()}, {xs.max()}], y:[{ys.min()}, {ys.max()}]), center=({xs.mean():.1f}, {ys.mean():.1f})")

# Where is black located?
ys_b, xs_b = np.where(mask_black)
print(f"Black: count={len(xs_b)}, bounds=(x:[{xs_b.min()}, {xs_b.max()}], y:[{ys_b.min()}, {ys_b.max()}])")
