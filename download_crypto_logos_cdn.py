"""
Download cryptocurrency logos from CDN (no restrictions)
Using jsdelivr CDN with cryptocurrency-icons package
"""

from urllib.request import urlretrieve
import os

base_dir = r"C:\Users\Wisdom Godswill\Desktop\coachjv\static\images\crypto-logos"
os.makedirs(base_dir, exist_ok=True)

# Using jsdelivr CDN for cryptocurrency icons (128x128 PNG)
base_url = "https://cdn.jsdelivr.net/npm/cryptocurrency-icons@0.18.1/128/color/"

crypto_logos = [
    'btc.png',   # Bitcoin
    'eth.png',   # Ethereum
    'usdt.png',  # Tether
    'bnb.png',   # BNB
    'sol.png',   # Solana
    'xrp.png',   # XRP
    'ada.png',   # Cardano
    'doge.png',  # Dogecoin
    'dot.png',   # Polkadot
    'matic.png', # Polygon
    'shib.png',  # Shiba Inu
    'avax.png',  # Avalanche
    'trx.png',   # Tron
    'link.png',  # Chainlink
    'uni.png',   # Uniswap
    'ltc.png',   # Litecoin
    'etc.png',   # Ethereum Classic
    'bch.png',   # Bitcoin Cash
    'xlm.png',   # Stellar
    'atom.png',  # Cosmos
]

print(f"📥 Downloading {len(crypto_logos)} crypto logos from CDN...")
print(f"💾 Saving to: {base_dir}\n")

for filename in crypto_logos:
    url = base_url + filename
    filepath = os.path.join(base_dir, filename)
    try:
        print(f"⬇️  {filename}...", end=' ')
        urlretrieve(url, filepath)
        file_size = os.path.getsize(filepath) / 1024
        print(f"✅ ({file_size:.1f}KB)")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

print(f"\n✅ Crypto logos downloaded!")
print(f"📁 Location: {base_dir}")
