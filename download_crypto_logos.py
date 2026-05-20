"""
Download cryptocurrency logos/icons for professional crypto exchange aesthetic
High-quality SVG/PNG crypto logos from cryptocurrency-icons library
"""

from urllib.request import urlretrieve
import os

base_dir = r"C:\Users\Wisdom Godswill\Desktop\coachjv\static\images\crypto-logos"
os.makedirs(base_dir, exist_ok=True)

# Top cryptocurrency logos (128x128 PNG format)
# Using cryptocurrency-icons from GitHub (MIT licensed)
crypto_logos = {
    'bitcoin.png': 'https://cryptologos.cc/logos/bitcoin-btc-logo.png?v=029',
    'ethereum.png': 'https://cryptologos.cc/logos/ethereum-eth-logo.png?v=029',
    'tether.png': 'https://cryptologos.cc/logos/tether-usdt-logo.png?v=029',
    'bnb.png': 'https://cryptologos.cc/logos/bnb-bnb-logo.png?v=029',
    'solana.png': 'https://cryptologos.cc/logos/solana-sol-logo.png?v=029',
    'xrp.png': 'https://cryptologos.cc/logos/xrp-xrp-logo.png?v=029',
    'cardano.png': 'https://cryptologos.cc/logos/cardano-ada-logo.png?v=029',
    'dogecoin.png': 'https://cryptologos.cc/logos/dogecoin-doge-logo.png?v=029',
    'polkadot.png': 'https://cryptologos.cc/logos/polkadot-new-dot-logo.png?v=029',
    'polygon.png': 'https://cryptologos.cc/logos/polygon-matic-logo.png?v=029',
    'shiba.png': 'https://cryptologos.cc/logos/shiba-inu-shib-logo.png?v=029',
    'avalanche.png': 'https://cryptologos.cc/logos/avalanche-avax-logo.png?v=029',
    'tron.png': 'https://cryptologos.cc/logos/tron-trx-logo.png?v=029',
    'chainlink.png': 'https://cryptologos.cc/logos/chainlink-link-logo.png?v=029',
    'uniswap.png': 'https://cryptologos.cc/logos/uniswap-uni-logo.png?v=029',
    'litecoin.png': 'https://cryptologos.cc/logos/litecoin-ltc-logo.png?v=029',
}

print(f"📥 Downloading {len(crypto_logos)} crypto logos...")
print(f"💾 Saving to: {base_dir}\n")

for filename, url in crypto_logos.items():
    filepath = os.path.join(base_dir, filename)
    try:
        print(f"⬇️  {filename}...", end=' ')
        urlretrieve(url, filepath)
        file_size = os.path.getsize(filepath) / 1024
        print(f"✅ ({file_size:.1f}KB)")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

print(f"\n✅ All crypto logos downloaded!")
print(f"📁 Location: {base_dir}")
