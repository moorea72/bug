"""
Test NFT upload functionality with ImgBB
"""

import os
os.environ['IMGBB_API_KEY'] = '8f8ec31fde8a226663f6f8edef74f6da'

from app import app, db
from models import NFT, NFTCollection
from imgbb_upload import imgbb_uploader
from PIL import Image
import io

def test_nft_creation():
    """Test creating NFT with ImgBB image upload"""
    with app.app_context():
        # Create a test image
        test_image = Image.new('RGB', (300, 300), color='blue')
        img_buffer = io.BytesIO()
        test_image.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        # Upload to ImgBB
        print("Uploading test image to ImgBB...")
        result = imgbb_uploader.upload_image(img_buffer, 'test_nft_crypto_punk')
        
        if result['success']:
            print(f"✓ Image uploaded successfully!")
            print(f"URL: {result['url']}")
            
            # Create NFT in database
            collection = NFTCollection.query.first()
            if collection:
                nft = NFT(
                    name="Test Crypto Punk #9999",
                    collection_id=collection.id,
                    image_url=result['url'],
                    price=199.50,
                    last_sale_price=179.50,
                    unique_id="TEST9999",
                    is_verified=True,
                    rarity=5,
                    description="Test NFT with ImgBB integration",
                    is_active=True
                )
                
                db.session.add(nft)
                db.session.commit()
                print(f"✓ NFT created successfully with ID: {nft.id}")
                print(f"✓ Image URL stored: {nft.image_url}")
                
                return True
        else:
            print(f"✗ Upload failed: {result['error']}")
            return False

if __name__ == "__main__":
    test_nft_creation()