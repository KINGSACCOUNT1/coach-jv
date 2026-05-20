from PIL import Image

# Open the image
img_path = r"C:\Users\Wisdom Godswill\Desktop\coachjv\static\images\coach-jv-cutout.png"
img = Image.open(img_path)

print(f"Image mode: {img.mode}")
print(f"Image size: {img.size}")
print(f"Has transparency: {'A' in img.mode or 'transparency' in img.info}")

# Convert to RGBA if not already
if img.mode != 'RGBA':
    img = img.convert('RGBA')
    print("Converted to RGBA")

# Get the pixel data
pixels = img.load()
width, height = img.size

# Remove any light gray/white pixels that should be transparent
cleaned = False
for y in range(height):
    for x in range(width):
        r, g, b, a = pixels[x, y]
        # If pixel is very light (near white) and not fully opaque, make it fully transparent
        if r > 240 and g > 240 and b > 240:
            pixels[x, y] = (255, 255, 255, 0)  # Fully transparent white
            cleaned = True

if cleaned:
    img.save(img_path)
    print("✅ Cleaned up white background - image saved with full transparency")
else:
    print("✅ Image already has clean transparency")
