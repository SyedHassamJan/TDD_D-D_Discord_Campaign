from PIL import Image
import numpy as np

im_test = Image.open("map_assets_extracted/test.png").convert("RGB")
arr = np.array(im_test)

# Downsample
sub = arr[::4, ::4]
preview = np.zeros((sub.shape[0], sub.shape[1], 3), dtype=np.uint8)

sub_black = (sub[:,:,0]==0) & (sub[:,:,1]==0) & (sub[:,:,2]==0)
sub_dark_red = (sub[:,:,0]==136) & (sub[:,:,1]==0) & (sub[:,:,2]==21)
sub_red = (sub[:,:,0]==237) & (sub[:,:,1]==28) & (sub[:,:,2]==36)
sub_brown = (sub[:,:,0]==185) & (sub[:,:,1]==122) & (sub[:,:,2]==87)

preview[:] = [120, 160, 180] # unpainted terrain/satellite
preview[sub_black] = [0, 0, 0] # black impassible
preview[sub_dark_red] = [136, 0, 21]
preview[sub_red] = [237, 28, 36]
preview[sub_brown] = [185, 122, 87]

Image.fromarray(preview).save("map_assets_extracted/preview_mask.png")
print("Saved preview_mask.png with shape:", preview.shape)
