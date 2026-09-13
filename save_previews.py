from PIL import Image

hm = Image.open("map_assets_extracted/Heightmap-layer-Middle-earth-V2.png")
sat = Image.open("map_assets_extracted/Satellite-layer-Middle-earth-V2.png")

hm.resize((600, 480)).convert("RGB").save("map_assets_extracted/preview_hm.jpg", quality=80)
sat.resize((600, 480)).convert("RGB").save("map_assets_extracted/preview_sat.jpg", quality=80)
print("Saved preview_hm.jpg and preview_sat.jpg")
