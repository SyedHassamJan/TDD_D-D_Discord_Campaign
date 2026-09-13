from PIL import Image
import numpy as np

hm = Image.open("map_assets_extracted/Heightmap-layer-Middle-earth-V2.png")
print("Heightmap size:", hm.size, "mode:", hm.mode)

hm_rgb = hm.convert("RGB")
arr_hm = np.array(hm_rgb)
print("Heightmap min/max/mean R:", arr_hm[:,:,0].min(), arr_hm[:,:,0].max(), arr_hm[:,:,0].mean())
print("Heightmap min/max/mean G:", arr_hm[:,:,1].min(), arr_hm[:,:,1].max(), arr_hm[:,:,1].mean())
print("Heightmap min/max/mean B:", arr_hm[:,:,2].min(), arr_hm[:,:,2].max(), arr_hm[:,:,2].mean())

# Check original shade_b64.jpg for comparison
orig_sh = Image.open("map_assets_extracted/shade_b64.jpg")
print("Orig shade size:", orig_sh.size, "mode:", orig_sh.mode)
arr_orig_sh = np.array(orig_sh)
print("Orig shade min/max/mean:", arr_orig_sh.min(), arr_orig_sh.max(), arr_orig_sh.mean())

# Check sat layer
sat = Image.open("map_assets_extracted/Satellite-layer-Middle-earth-V2.png")
print("Satellite size:", sat.size, "mode:", sat.mode)
