from PIL import Image

# Open the PNG cutout
img_path = r"C:\Users\Wisdom Godswill\Desktop\coachjv\static\images\coach-jv-cutout.png"
output_path = r"C:\Users\Wisdom Godswill\Desktop\coachjv\static\images\coach-jv-cutout.webp"

print("Loading PNG cutout image...")
img = Image.open(img_path)

print(f"Original size: {img.size}")
print(f"Original mode: {img.mode}")

# Save as WebP with transparency and high quality
print("Converting to WebP with transparency...")
img.save(output_path, 'WEBP', quality=85, method=6, lossless=False)

# Check file sizes
import os
png_size = os.path.getsize(img_path) / 1024
webp_size = os.path.getsize(output_path) / 1024
reduction = ((png_size - webp_size) / png_size) * 100

print(f"\n✅ Conversion complete!")
print(f"PNG size: {png_size:.2f} KB")
print(f"WebP size: {webp_size:.2f} KB")
print(f"Reduction: {reduction:.1f}% smaller")
print(f"Saved to: {output_path}")
