from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Build a composite preview showing the final map result
test_im = Image.open("map_assets_extracted/test.png").convert("RGB")
sat_im = Image.open("map_assets_extracted/Satellite-layer-Middle-earth-V2.png").convert("RGB")
hm_im = Image.open("map_assets_extracted/Heightmap-layer-Middle-earth-V2.png").convert("L")

W, H = test_im.size
arr_test = np.array(test_im)

# Masks
m_black = (arr_test[:,:,0] <= 5) & (arr_test[:,:,1] <= 5) & (arr_test[:,:,2] <= 5)
m_p1 = (arr_test[:,:,0] == 136) & (arr_test[:,:,1] == 0) & (arr_test[:,:,2] == 21)   # Near Harad
m_p2 = (arr_test[:,:,0] == 185) & (arr_test[:,:,1] == 122) & (arr_test[:,:,2] == 87) # Harondor
m_p3 = (arr_test[:,:,0] == 237) & (arr_test[:,:,1] == 28) & (arr_test[:,:,2] == 36)  # South Ithilien

# Build satellite composite at half scale for preview
sat_resized = sat_im.resize((W, H), Image.Resampling.BILINEAR)
hm_resized = hm_im.resize((W, H), Image.Resampling.BILINEAR)
arr_sat = np.array(sat_resized)
arr_hm = np.array(hm_resized)

# Composite: satellite base, heightmap relief (multiply), faction colors blended
out = arr_sat.astype(float)

# Apply heightmap relief (multiply blend)
shade_norm = arr_hm.astype(float) / 255.0
shade_norm = 0.45 + 1.10 * shade_norm  # range: ~0.45 to 1.55
out = np.clip(out * shade_norm[:, :, np.newaxis], 0, 255)

# Apply faction colors as overlays (60% faction color, 40% satellite)
faction_colors = {
    "Near Harad": (136, 0, 21, m_p1, "Lostladen Tribes"),
    "Harondor": (185, 122, 87, m_p2, "Mordor"),
    "South Ithilien": (237, 28, 36, m_p3, "Gondor"),
}

for name, (r, g, b, m, owner) in faction_colors.items():
    out[m, 0] = np.clip(out[m, 0] * 0.4 + r * 0.6, 0, 255)
    out[m, 1] = np.clip(out[m, 1] * 0.4 + g * 0.6, 0, 255)
    out[m, 2] = np.clip(out[m, 2] * 0.4 + b * 0.6, 0, 255)

# Black = void/sea
out[m_black] = [15, 28, 42]

# Borders: darken pixels adjacent to two different provinces
prov_map = np.zeros((H, W), dtype=np.int8) - 1
prov_map[m_p1] = 1
prov_map[m_p2] = 2
prov_map[m_p3] = 3
for dy, dx in [(-1,0),(1,0),(0,-1),(0,1)]:
    shifted = np.roll(np.roll(prov_map, dy, axis=0), dx, axis=1)
    border = (prov_map >= 0) & (shifted >= 0) & (prov_map != shifted)
    out[border] = np.clip(out[border] * 0.5, 0, 255)

out_img = Image.fromarray(out.astype(np.uint8))

# Scale down for preview
preview_w = 1200
scale = preview_w / W
preview_h = int(H * scale)
out_img = out_img.resize((preview_w, preview_h), Image.Resampling.LANCZOS)

# Add labels for each province
draw = ImageDraw.Draw(out_img)

labels = [
    ("Near Harad", 1794.3, 2635.6, "Lostladen Tribes", (255, 220, 120)),
    ("Harondor", 1960.6, 2480.5, "Mordor", (200, 140, 100)),
    ("South Ithilien", 2100.9, 2324.0, "Gondor", (180, 200, 255)),
]

for (name, cx, cy, owner, color) in labels:
    px = int(cx * scale)
    py = int(cy * scale)
    # Draw a cross marker
    draw.ellipse([px-6, py-6, px+6, py+6], fill=color, outline=(0,0,0))
    # Draw text with shadow
    for dx, dy in [(-1,-1),(1,-1),(-1,1),(1,1)]:
        draw.text((px+10+dx, py-8+dy), f"{name}\n({owner})", fill=(0,0,0))
    draw.text((px+10, py-8), f"{name}\n({owner})", fill=color)

out_img.save("map_assets_extracted/final_map_preview.jpg", quality=88, optimize=True)
print("Saved map_assets_extracted/final_map_preview.jpg")
print(f"Size: {out_img.size}")
