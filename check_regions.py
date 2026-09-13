import numpy as np
from PIL import Image

im = Image.open("map_assets_extracted/test.png").convert("RGB")
arr = np.array(im)

c1 = (136, 0, 21)   # Dark Red #880015
c2 = (185, 122, 87) # Brown #b97a57
c3 = (237, 28, 36)  # Red #ed1c24

m1 = (arr[:,:,0]==c1[0]) & (arr[:,:,1]==c1[1]) & (arr[:,:,2]==c1[2])
m2 = (arr[:,:,0]==c2[0]) & (arr[:,:,1]==c2[1]) & (arr[:,:,2]==c2[2])
m3 = (arr[:,:,0]==c3[0]) & (arr[:,:,1]==c3[1]) & (arr[:,:,2]==c3[2])
m_black = (arr[:,:,0]==0) & (arr[:,:,1]==0) & (arr[:,:,2]==0)
m_other = (~m1) & (~m2) & (~m3) & (~m_black)

def border_touch(m_a, m_b):
    up = np.sum(m_a[1:, :] & m_b[:-1, :])
    down = np.sum(m_a[:-1, :] & m_b[1:, :])
    left = np.sum(m_a[:, 1:] & m_b[:, :-1])
    right = np.sum(m_a[:, :-1] & m_b[:, 1:])
    return up + down + left + right

print("Touch 1 (Dark Red) and 2 (Brown):", border_touch(m1, m2))
print("Touch 2 (Brown) and 3 (Red):", border_touch(m2, m3))
print("Touch 1 (Dark Red) and 3 (Red):", border_touch(m1, m3))
print("Touch 1 and black:", border_touch(m1, m_black))
print("Touch 2 and black:", border_touch(m2, m_black))
print("Touch 3 and black:", border_touch(m3, m_black))
print("Touch 1 and other:", border_touch(m1, m_other))
print("Touch 2 and other:", border_touch(m2, m_other))
print("Touch 3 and other:", border_touch(m3, m_other))
