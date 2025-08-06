"""
Fix ImgBB URLs to use direct image links
Convert page URLs like https://ibb.co/JhMCz2y to direct image URLs
"""

from app import app, db
from models import NFT
import requests

def convert_imgbb_url(page_url):
    """Convert ImgBB page URL to direct image URL"""
    if 'ibb.co/' in page_url:
        # Extract image ID from URL
        image_id = page_url.split('/')[-1]
        
        # Try different formats
        formats = ['.png', '.jpg', '.jpeg', '.gif', '.webp']
        
        for fmt in formats:
            direct_url = f'https://i.ibb.co/{image_id}{fmt}'
            try:
                response = requests.head(direct_url, timeout=5)
                if response.status_code == 200:
                    return direct_url
            except:
                continue
        
        # If no format works, return with .png as default
        return f'https://i.ibb.co/{image_id}.png'
    
    return page_url

def fix_all_nft_urls():
    """Fix all NFT URLs in database"""
    with app.app_context():
        nfts = NFT.query.all()
        updated_count = 0
        
        for nft in nfts:
            if nft.image_url and 'ibb.co/' in nft.image_url and not nft.image_url.startswith('https://i.ibb.co/'):
                old_url = nft.image_url
                new_url = convert_imgbb_url(old_url)
                nft.image_url = new_url
                print(f'Updated {nft.name}:')
                print(f'  Old: {old_url}')
                print(f'  New: {new_url}')
                updated_count += 1
        
        if updated_count > 0:
            db.session.commit()
            print(f'\n✓ Updated {updated_count} NFT image URLs')
        else:
            print('No URLs needed updating')

if __name__ == "__main__":
    fix_all_nft_urls()