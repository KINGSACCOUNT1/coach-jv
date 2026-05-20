from rembg import remove
from PIL import Image

# Load the original image
input_path = r"C:\Users\Wisdom Godswill\Desktop\coachjv\static\images\coach-jv.webp"
output_path = r"C:\Users\Wisdom Godswill\Desktop\coachjv\static\images\coach-jv-cutout.png"

print("Loading image...")
input_image = Image.open(input_path)

print("Removing background... (this may take a minute)")
output_image = remove(input_image)

print("Saving cutout image...")
output_image.save(output_path)

print(f"✅ Done! Cutout saved to: {output_path}")
print(f"   Original size: {input_image.size}")
print(f"   Cutout has transparent background (PNG format)")
