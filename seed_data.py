#!/usr/bin/env python3
"""
Seed data script for the NFT staking platform.
This script populates the database with initial data including:
- Admin user
- Sample coins with customizable logos
- Staking plans with different durations and returns
- NFT collections and NFTs
- Platform notices (including market-based returns notice)
"""

from app import app, db
from models import (
    User, Coin, StakingPlan, NFT, NFTCollection, 
    PlatformNotice, UICustomization, PlatformSettings
)
from werkzeug.security import generate_password_hash
import random

def seed_database():
    """Seed the database with initial data"""
    with app.app_context():
        # Create admin user
        admin_user = User.query.filter_by(email='admin@platform.com').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@platform.com',
                phone_number='+1234567890',
                password_hash=generate_password_hash('admin123'),
                is_admin=True,
                usdt_balance=10000.0
            )
            db.session.add(admin_user)
            print("✓ Admin user created")

        # Create sample coins with logos
        coins_data = [
            {
                'symbol': 'USDT',
                'name': 'Tether',
                'min_stake': 10.0,
                'icon_emoji': '₮',
                'logo_url': 'https://cryptologos.cc/logos/tether-usdt-logo.png'
            },
            {
                'symbol': 'BTC',
                'name': 'Bitcoin',
                'min_stake': 250.0,
                'icon_emoji': '₿',
                'logo_url': 'https://cryptologos.cc/logos/bitcoin-btc-logo.png'
            },
            {
                'symbol': 'ETH',
                'name': 'Ethereum',
                'min_stake': 170.0,
                'icon_emoji': '⧫',
                'logo_url': 'https://cryptologos.cc/logos/ethereum-eth-logo.png'
            },
            {
                'symbol': 'BNB',
                'name': 'Binance Coin',
                'min_stake': 90.0,
                'icon_emoji': '🟡',
                'logo_url': 'https://cryptologos.cc/logos/binance-coin-bnb-logo.png'
            },
            {
                'symbol': 'LTC',
                'name': 'Litecoin',
                'min_stake': 130.0,
                'icon_emoji': 'Ł',
                'logo_url': 'https://cryptologos.cc/logos/litecoin-ltc-logo.png'
            }
        ]

        for coin_data in coins_data:
            coin = Coin.query.filter_by(symbol=coin_data['symbol']).first()
            if not coin:
                coin = Coin(**coin_data)
                db.session.add(coin)
                print(f"✓ Coin {coin_data['symbol']} created")

        # Create staking plans with different durations and returns
        staking_plans = [
            {'duration_days': 7, 'interest_rate': 0.5},
            {'duration_days': 15, 'interest_rate': 0.75},
            {'duration_days': 30, 'interest_rate': 1.0},
            {'duration_days': 90, 'interest_rate': 1.5},
            {'duration_days': 120, 'interest_rate': 1.75},
            {'duration_days': 180, 'interest_rate': 2.0}
        ]

        for plan_data in staking_plans:
            plan = StakingPlan.query.filter_by(
                duration_days=plan_data['duration_days'],
                interest_rate=plan_data['interest_rate']
            ).first()
            if not plan:
                plan = StakingPlan(**plan_data)
                db.session.add(plan)
                print(f"✓ Staking plan {plan_data['duration_days']} days created")

        # Create NFT collections
        collections_data = [
            {'name': 'CryptoPunks', 'symbol': 'PUNK', 'description': 'The original CryptoPunks collection'},
            {'name': 'Legendary Heroes', 'symbol': 'HERO', 'description': 'Epic heroes from different realms'},
            {'name': 'Cyber Warriors', 'symbol': 'CYBER', 'description': 'Futuristic cyber warriors'},
            {'name': 'Fantasy Realm', 'symbol': 'FANT', 'description': 'Magical creatures from fantasy worlds'},
            {'name': 'Space Odyssey', 'symbol': 'SPACE', 'description': 'Intergalactic space adventures'}
        ]

        for collection_data in collections_data:
            collection = NFTCollection.query.filter_by(name=collection_data['name']).first()
            if not collection:
                collection = NFTCollection(**collection_data)
                db.session.add(collection)
                print(f"✓ NFT collection {collection_data['name']} created")

        # Commit collections first to get IDs
        db.session.commit()

        # Create sample NFTs
        nfts_data = [
            {'name': 'Mosu #1930', 'icon': '🎭', 'gradient': 'from-purple-600 to-pink-600', 'price': 750.0, 'owner': 'CryptoPunks', 'unique_id': '1930', 'verified': True, 'rarity': 5},
            {'name': 'Alien #2847', 'icon': '👽', 'gradient': 'from-green-500 to-blue-500', 'price': 680.0, 'owner': 'CryptoPunks', 'unique_id': '2847', 'verified': True, 'rarity': 5},
            {'name': 'Punk #5672', 'icon': '🎨', 'gradient': 'from-red-500 to-orange-500', 'price': 520.0, 'owner': 'CryptoPunks', 'unique_id': '5672', 'verified': True, 'rarity': 4},
            {'name': 'Zombie #3421', 'icon': '🧟', 'gradient': 'from-gray-600 to-green-600', 'price': 450.0, 'owner': 'CryptoPunks', 'unique_id': '3421', 'verified': False, 'rarity': 4},
            {'name': 'Ape #8901', 'icon': '🦍', 'gradient': 'from-brown-500 to-yellow-500', 'price': 380.0, 'owner': 'CryptoPunks', 'unique_id': '8901', 'verified': False, 'rarity': 3},
            {'name': 'Dragon Warrior', 'icon': '🐉', 'gradient': 'from-red-600 to-orange-600', 'price': 650.0, 'owner': 'LegendaryHero', 'unique_id': 'DW001', 'verified': True, 'rarity': 5},
            {'name': 'Cyber Samurai', 'icon': '⚔️', 'gradient': 'from-blue-600 to-purple-600', 'price': 420.0, 'owner': 'CyberWarrior', 'unique_id': 'CS001', 'verified': False, 'rarity': 4},
            {'name': 'Phoenix Guardian', 'icon': '🔥', 'gradient': 'from-orange-500 to-red-500', 'price': 580.0, 'owner': 'FantasyRealm', 'unique_id': 'PG001', 'verified': True, 'rarity': 5}
        ]

        collections = NFTCollection.query.all()
        for i, nft_data in enumerate(nfts_data):
            nft = NFT.query.filter_by(unique_id=nft_data['unique_id']).first()
            if not nft:
                nft = NFT(
                    name=nft_data['name'],
                    collection_id=collections[i % len(collections)].id,
                    icon=nft_data['icon'],
                    image_url=f'https://picsum.photos/300/300?random={i+100}',
                    gradient=nft_data['gradient'],
                    price=nft_data['price'],
                    last_sale_price=nft_data['price'] * 0.9,
                    rarity=nft_data['rarity'],
                    owner_name=nft_data['owner'],
                    unique_id=nft_data['unique_id'],
                    is_verified=nft_data['verified'],
                    display_order=i
                )
                db.session.add(nft)
                print(f"✓ NFT {nft_data['name']} created")

        # Create platform notices
        notices_data = [
            {
                'page_location': 'home',
                'title': 'Market-Based Returns Notice',
                'message': 'Our staking returns are dynamically adjusted based on real market conditions. We do not use any third-party applications or external automated systems. All returns are calculated internally by our platform.',
                'notice_type': 'info',
                'display_order': 1
            },
            {
                'page_location': 'home',
                'title': 'Security Update',
                'message': 'We have implemented advanced blockchain verification for all deposits. Your funds are now more secure than ever with real-time transaction verification.',
                'notice_type': 'success',
                'display_order': 2
            },
            {
                'page_location': 'stake',
                'title': 'Bonus Interest Available',
                'message': 'Users with 2 or more referrals receive an additional 2% daily interest on all stakes plus waived withdrawal fees!',
                'notice_type': 'success',
                'display_order': 1
            }
        ]

        for notice_data in notices_data:
            notice = PlatformNotice.query.filter_by(
                page_location=notice_data['page_location'],
                title=notice_data['title']
            ).first()
            if not notice:
                notice = PlatformNotice(**notice_data)
                db.session.add(notice)
                print(f"✓ Notice '{notice_data['title']}' created")

        # Create UI customizations
        ui_customizations = [
            {'element_type': 'nav_icon', 'element_name': 'home', 'icon_emoji': '🏠', 'is_active': True},
            {'element_type': 'nav_icon', 'element_name': 'stake', 'icon_emoji': '💰', 'is_active': True},
            {'element_type': 'nav_icon', 'element_name': 'assets', 'icon_emoji': '💎', 'is_active': True},
            {'element_type': 'nav_icon', 'element_name': 'nfts', 'icon_emoji': '🎨', 'is_active': True},
            {'element_type': 'nav_icon', 'element_name': 'profile', 'icon_emoji': '👤', 'is_active': True},
            {'element_type': 'feature_icon', 'element_name': 'security', 'icon_class': 'fas fa-shield-alt', 'is_active': True},
            {'element_type': 'feature_icon', 'element_name': 'returns', 'icon_class': 'fas fa-chart-line', 'is_active': True}
        ]

        for ui_data in ui_customizations:
            ui_element = UICustomization.query.filter_by(
                element_type=ui_data['element_type'],
                element_name=ui_data['element_name']
            ).first()
            if not ui_element:
                ui_element = UICustomization(**ui_data)
                db.session.add(ui_element)
                print(f"✓ UI customization {ui_data['element_type']}:{ui_data['element_name']} created")

        # Create platform settings
        platform_settings = [
            {'key': 'platform_name', 'value': 'USDT Staking Platform', 'description': 'Platform name'},
            {'key': 'referral_level_1', 'value': '5.0', 'description': 'Level 1 referral percentage'},
            {'key': 'referral_level_2', 'value': '3.0', 'description': 'Level 2 referral percentage'},
            {'key': 'referral_level_3', 'value': '1.0', 'description': 'Level 3 referral percentage'},
            {'key': 'withdrawal_fee', 'value': '1.0', 'description': 'Withdrawal fee percentage'},
            {'key': 'min_referral_activation', 'value': '10.0', 'description': 'Minimum amount to activate referral'}
        ]

        for setting_data in platform_settings:
            setting = PlatformSettings.query.filter_by(key=setting_data['key']).first()
            if not setting:
                setting = PlatformSettings(**setting_data)
                db.session.add(setting)
                print(f"✓ Platform setting {setting_data['key']} created")

        # Commit all changes
        db.session.commit()
        print("\n✅ Database seeded successfully!")
        print("Admin credentials: admin@platform.com / admin123")
        print("Access admin panel at: /adminaccess")

if __name__ == '__main__':
    seed_database()