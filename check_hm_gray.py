from PIL import Image
import numpy as np

hm = Image.open("map_assets_extracted/Heightmap-layer-Middle-earth-V2.png").convert("RGB")
arr = np.array(hm)

# In the hypsometric heightmap:
# Lowlands: green
# Mid elevations: yellow-green / brown
# High mountains: brown / dark purple / snow white peaks
# Let's inspect RGB of mountain peaks vs plains vs valleys
# e.g. Misty Mountains peak in center top:
peak_sample = arr[200:500, 1000:1500]
print("Peak area R max:", peak_sample[:,:,0].max())
print("Peak area G max:", peak_sample[:,:,1].max())
print("Peak area B max:", peak_sample[:,:,2].max())

# In heightmaps, luminosity L = 0.299*R + 0.587*G + 0.114*B or elevation mapping:
gray = hm.convert("L")
arr_g = np.array(gray)
print("Grayscale min:", arr_g.min(), "max:", arr_g.max(), "mean:", arr_g.mean())

# Let's see what arr_g looks like in the 3 provinces in the south:
# The 3 provinces in test.png (scaled to 2500x2003):
# x in [1200, 1600], y in [1700, 2000]
south_sample = arr_g[int(2003*2200/2687):, int(2500*1600/3357):int(2500*2200/3357)]
print("South sample min/max/mean:", south_sample.min(), south_sample.max(), south_sample.mean())
