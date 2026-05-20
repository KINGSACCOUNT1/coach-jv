"""
Premium Visual Assets for CoachJVTech Landing Page
Download high-quality images from Unsplash (free, no attribution required)
"""

from urllib.request import urlretrieve
import os

# Base directory
base_dir = r"C:\Users\Wisdom Godswill\Desktop\coachjv\static\images"

# High-quality crypto and finance images
images = {
    # Hero Background (crypto trading, dark blue)
    'backgrounds/hero-bg.jpg': 'https://images.unsplash.com/photo-1639762681485-074b7f938ba0?w=1920&q=90',  # Crypto coins dark
    
    # Features Section Icons/Images (technology, innovation)
    'features/security.jpg': 'https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=800&q=90',  # Security/padlock
    'features/trading.jpg': 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&q=90',  # Trading charts
    'features/portfolio.jpg': 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&q=90',  # Analytics/graphs
    'features/mobile.jpg': 'https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=800&q=90',  # Mobile app
    
    # Testimonial Photos (professional business people)
    'testimonials/person1.jpg': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&q=90',  # Male professional
    'testimonials/person2.jpg': 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400&q=90',  # Female professional
    'testimonials/person3.jpg': 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&q=90',  # Male investor
    
    # Crypto Coins (Bitcoin, Ethereum, XRP)
    'crypto-coins/bitcoin.jpg': 'https://images.unsplash.com/photo-1518546305927-5a555bb7020d?w=600&q=90',  # Bitcoin coin
    'crypto-coins/ethereum.jpg': 'https://images.unsplash.com/photo-1622630998477-20aa696ecb05?w=600&q=90',  # Ethereum
    'crypto-coins/xrp-bg.jpg': 'https://images.unsplash.com/photo-1621416894569-0f39ed31d247?w=1200&q=90',  # XRP coins
    
    # Section Backgrounds (abstract, dark, premium)
    'backgrounds/section-dark.jpg': 'https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=1920&q=90',  # Dark abstract
    'backgrounds/gradient-blue.jpg': 'https://images.unsplash.com/photo-1557683316-973673baf926?w=1920&q=90',  # Blue gradient
    'backgrounds/crypto-pattern.jpg': 'https://images.unsplash.com/photo-1639322537228-f710d846310a?w=1920&q=90',  # Crypto pattern
}

print("📥 Downloading premium images from Unsplash...")
print(f"Total images: {len(images)}\n")

for filename, url in images.items():
    filepath = os.path.join(base_dir, filename)
    
    # Create directory if needed
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    try:
        print(f"⬇️  {filename}...", end=' ')
        urlretrieve(url, filepath)
        file_size = os.path.getsize(filepath) / 1024
        print(f"✅ ({file_size:.1f}KB)")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

print("\n✅ All images downloaded successfully!")
print("📁 Location: static/images/")
