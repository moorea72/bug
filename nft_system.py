"""
Complete NFT Management System
Fresh implementation with proper database structure
"""

from app import app, db
from models import User, NFTCollection, NFT
from werkzeug.security import generate_password_hash
import os
import uuid
from datetime import datetime

def create_fresh_nft_system():
    """Create a completely fresh NFT system"""
    with app.app_context():
        # Drop all existing tables and recreate
        db.drop_all()
        db.create_all()
        print("✓ Fresh database created")
        
        # Create admin user
        admin_user = User(
            username='admin',
            email='admin@platform.com',
            phone_number='+1234567890',
            password_hash=generate_password_hash('admin123'),
            is_admin=True,
            usdt_balance=1000.0
        )
        db.session.add(admin_user)
        print("✓ Admin user created")
        
        # Create NFT collections
        collections = [
            NFTCollection(name='CryptoPunks', symbol='PUNK', description='Original NFT collection'),
            NFTCollection(name='Digital Art', symbol='ART', description='Modern digital artwork'),
            NFTCollection(name='Gaming NFTs', symbol='GAME', description='Gaming collectibles'),
            NFTCollection(name='Abstract Collection', symbol='ABSTRACT', description='Abstract digital art'),
            NFTCollection(name='Cosmic Collection', symbol='COSMIC', description='Space-themed NFTs'),
        ]
        
        for collection in collections:
            db.session.add(collection)
        
        db.session.commit()
        print(f"✓ Created {len(collections)} NFT collections")
        
        # Create sample NFTs
        sample_nfts = [
            {
                'name': 'Cosmic Dragon #1930',
                'collection_id': 1,
                'price': 125.0,
                'is_verified': True
            },
            {
                'name': 'Digital Warrior #2847',
                'collection_id': 2,
                'price': 89.0,
                'is_verified': False
            },
            {
                'name': 'Gaming Legend #5672',
                'collection_id': 3,
                'price': 156.0,
                'is_verified': True
            },
            {
                'name': 'Abstract Mind #3421',
                'collection_id': 4,
                'price': 67.0,
                'is_verified': False
            },
            {
                'name': 'Space Explorer #8901',
                'collection_id': 5,
                'price': 234.0,
                'is_verified': True
            }
        ]
        
        for nft_data in sample_nfts:
            nft = NFT(
                name=nft_data['name'],
                collection_id=nft_data['collection_id'],
                image_url=f'https://picsum.photos/300/300?random={nft_data["collection_id"]}',
                price=nft_data['price'],
                last_sale_price=nft_data['price'] * 0.9,
                unique_id=f"NFT{uuid.uuid4().hex[:8].upper()}",
                is_verified=nft_data['is_verified'],
                rarity=5 if nft_data['is_verified'] else 3,
                description=f"Premium NFT: {nft_data['name']}"
            )
            db.session.add(nft)
        
        db.session.commit()
        print(f"✓ Created {len(sample_nfts)} sample NFTs")
        
        print("\n=== NFT System Ready ===")
        print("Admin credentials:")
        print("Email: admin@platform.com")
        print("Password: admin123")
        print("\nAccess admin NFT panel at: /admin/nfts-enhanced")

if __name__ == "__main__":
    create_fresh_nft_system()