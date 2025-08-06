#!/usr/bin/env python3
"""
Add 8-9 dummy NFTs for easy admin editing
"""
import os
os.environ.setdefault('DATABASE_URL', 'postgresql://neondb_owner:npg_4sSItw5JkLZM@ep-falling-firefly-afxbamco-pooler.c-2.us-west-2.aws.neon.tech/neondb')

from app import app, db
from models import NFT, NFTCollection
import uuid

def add_dummy_nfts():
    """Add dummy NFTs to database"""
    
    with app.app_context():
        # Check if collections exist
        collections = NFTCollection.query.all()
        if not collections:
            # Create sample collections
            collections_data = [
                {'name': 'CryptoPunks', 'description': 'Original NFT collection'},
                {'name': 'Bored Apes', 'description': 'Popular ape collection'}, 
                {'name': 'Mutant Apes', 'description': 'Mutant versions'},
                {'name': 'Azuki', 'description': 'Anime-style collection'},
                {'name': 'Cool Cats', 'description': 'Cool cat NFTs'}
            ]
            
            for col_data in collections_data:
                collection = NFTCollection(
                    name=col_data['name'],
                    description=col_data['description']
                )
                db.session.add(collection)
            
            db.session.commit()
            collections = NFTCollection.query.all()
            print(f"Created {len(collections)} collections")
        
        # Delete existing NFTs to start fresh
        NFT.query.delete()
        db.session.commit()
        
        # NFT dummy data
        nft_data = [
            {
                'name': 'Crypto Punk #1024',
                'price': 125.50,
                'collection_id': 1,
                'is_verified': True,
                'image_url': 'https://picsum.photos/300/300?random=1024'
            },
            {
                'name': 'Bored Ape #5672',
                'price': 89.99,
                'collection_id': 2,
                'is_verified': True,
                'image_url': 'https://picsum.photos/300/300?random=5672'
            },
            {
                'name': 'Mutant Ape #3847',
                'price': 67.25,
                'collection_id': 3,
                'is_verified': False,
                'image_url': 'https://picsum.photos/300/300?random=3847'
            },
            {
                'name': 'Azuki #2156',
                'price': 156.75,
                'collection_id': 4,
                'is_verified': True,
                'image_url': 'https://picsum.photos/300/300?random=2156'
            },
            {
                'name': 'Cool Cat #7892',
                'price': 45.80,
                'collection_id': 5,
                'is_verified': False,
                'image_url': 'https://picsum.photos/300/300?random=7892'
            },
            {
                'name': 'Crypto Punk #8341',
                'price': 234.99,
                'collection_id': 1,
                'is_verified': True,
                'image_url': 'https://picsum.photos/300/300?random=8341'
            },
            {
                'name': 'Bored Ape #1967',
                'price': 178.25,
                'collection_id': 2,
                'is_verified': True,
                'image_url': 'https://picsum.photos/300/300?random=1967'
            },
            {
                'name': 'Azuki #4523',
                'price': 99.50,
                'collection_id': 4,
                'is_verified': False,
                'image_url': 'https://picsum.photos/300/300?random=4523'
            },
            {
                'name': 'Cool Cat #6784',
                'price': 73.40,
                'collection_id': 5,
                'is_verified': True,
                'image_url': 'https://picsum.photos/300/300?random=6784'
            }
        ]
        
        # Add NFTs to database
        for i, nft_info in enumerate(nft_data):
            nft = NFT(
                name=nft_info['name'],
                collection_id=nft_info['collection_id'],
                image_url=nft_info['image_url'],
                price=nft_info['price'],
                last_sale_price=nft_info['price'] * 0.85,  # 15% less than current
                unique_id=f"NFT{uuid.uuid4().hex[:6].upper()}",
                is_verified=nft_info['is_verified'],
                rarity=5 if nft_info['is_verified'] else 3,
                description=f"Premium NFT: {nft_info['name']}",
                owner_name=f"User{1000 + i}",
                is_active=True,
                display_order=i
            )
            
            db.session.add(nft)
        
        db.session.commit()
        
        # Verify NFTs were added
        nft_count = NFT.query.count()
        print(f"✓ Added {nft_count} dummy NFTs successfully")
        
        # List all NFTs
        nfts = NFT.query.all()
        for nft in nfts:
            print(f"  - {nft.name} (${nft.price}) - Verified: {nft.is_verified}")
        
        return True

if __name__ == "__main__":
    add_dummy_nfts()