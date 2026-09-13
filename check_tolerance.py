import numpy as np
from PIL import Image

im = Image.open("map_assets_extracted/test.png").convert("RGB")
arr = np.array(im)

# Exact colors
c_black = (0, 0, 0)
c_dr = (136, 0, 21)
c_br = (185, 122, 87)
c_r = (237, 28, 36)

m_black = (arr[:,:,0]==0) & (arr[:,:,1]==0) & (arr[:,:,2]==0)
m_dr = (arr[:,:,0]==136) & (arr[:,:,1]==0) & (arr[:,:,2]==21)
m_br = (arr[:,:,0]==185) & (arr[:,:,1]==122) & (arr[:,:,2]==87)
m_r = (arr[:,:,0]==237) & (arr[:,:,1]==28) & (arr[:,:,2]==36)

print("Exact match counts:")
print("  Black:", np.sum(m_black))
print("  Dark Red:", np.sum(m_dr))
print("  Brown:", np.sum(m_br))
print("  Red:", np.sum(m_r))

# Are there any near-matches (e.g. from slight antialiasing or compression)?
diff_dr = np.max(np.abs(arr - c_dr), axis=2)
diff_br = np.max(np.abs(arr - c_br), axis=2)
diff_r = np.max(np.abs(arr - c_r), axis=2)
diff_k = np.max(np.abs(arr - c_black), axis=2)

print("Near match within tolerance 5 (excluding exact):")
print("  Dark Red near:", np.sum((diff_dr <= 5) & (~m_dr)))
print("  Brown near:", np.sum((diff_br <= 5) & (~m_br)))
print("  Red near:", np.sum((diff_r <= 5) & (~m_r)))
print("  Black near:", np.sum((diff_k <= 5) & (~m_black)))
