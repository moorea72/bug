#!/usr/bin/env python3
"""
Setup script for Neon PostgreSQL database
"""
import os
import sys
from app import app, db
from models import User, Coin, StakingPlan, Stake, Deposit, Withdrawal, PlatformSettings, ActivityLog, PaymentAddress, ContentSection, SupportMessage, NFT, NFTCollection, UICustomization, PlatformNotice, WithdrawalSettings, SocialMediaLink
from models_enhanced import CoinReturnRate

# Set the database URL for connection
os.environ['DATABASE_URL'] = "postgresql://neondb_owner:npg_4sSItw5JkLZM@ep-falling-firefly-afxbamco-pooler.c-2.us-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def setup_database():
    """Setup Neon PostgreSQL database with all tables"""
    
    print("Setting up Neon PostgreSQL database...")
    
    try:
        # Create all tables
        with app.app_context():
            db.create_all()
            print("✓ Database tables created successfully")
            
            # Add default coins if they don't exist
            if Coin.query.count() == 0:
                coins_data = [
                    {"symbol": "USDT", "name": "Tether USD", "min_stake": 10, "icon_emoji": "💰"},
                    {"symbol": "BTC", "name": "Bitcoin", "min_stake": 250, "icon_emoji": "₿"},
                    {"symbol": "ETH", "name": "Ethereum", "min_stake": 170, "icon_emoji": "Ξ"},
                    {"symbol": "BNB", "name": "Binance Coin", "min_stake": 90, "icon_emoji": "🟡"},
                    {"symbol": "LTC", "name": "Litecoin", "min_stake": 130, "icon_emoji": "Ł"},
                ]
                
                for coin_data in coins_data:
                    coin = Coin(**coin_data)
                    db.session.add(coin)
                
                db.session.commit()
                print("✓ Default coins added")
            
            # Add default staking plans
            if StakingPlan.query.count() == 0:
                coins = Coin.query.all()
                plans_data = [
                    {"duration_days": 7, "interest_rate": 0.5},
                    {"duration_days": 15, "interest_rate": 0.8},
                    {"duration_days": 30, "interest_rate": 1.2},
                    {"duration_days": 90, "interest_rate": 1.6},
                    {"duration_days": 120, "interest_rate": 1.8},
                    {"duration_days": 180, "interest_rate": 2.0},
                ]
                
                for coin in coins:
                    for plan_data in plans_data:
                        plan = StakingPlan(
                            coin_id=coin.id,
                            duration_days=plan_data["duration_days"],
                            interest_rate=plan_data["interest_rate"]
                        )
                        db.session.add(plan)
                
                db.session.commit()
                print("✓ Default staking plans added")
            
            # Create admin user if doesn't exist
            admin = User.query.filter_by(email='admin@platform.com').first()
            if not admin:
                admin = User(
                    username='admin',
                    email='admin@platform.com',
                    phone_number='+1234567890',
                    is_admin=True,
                    usdt_balance=10000.0
                )
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                print("✓ Admin user created")
            
            # Add default platform settings
            if PlatformSettings.query.count() == 0:
                settings = [
                    PlatformSettings(key='site_name', value='USDT Staking Platform'),
                    PlatformSettings(key='min_deposit', value='10'),
                    PlatformSettings(key='min_withdrawal', value='5'),
                    PlatformSettings(key='withdrawal_fee', value='1'),
                    PlatformSettings(key='referral_level_1', value='5'),
                    PlatformSettings(key='min_referral_activation', value='100'),
                ]
                
                for setting in settings:
                    db.session.add(setting)
                
                db.session.commit()
                print("✓ Default platform settings added")
            
            # Add default NFT collections
            if NFTCollection.query.count() == 0:
                collections = [
                    NFTCollection(name='CryptoPunks', description='Original NFT collection'),
                    NFTCollection(name='Bored Apes', description='Popular ape NFTs'),
                    NFTCollection(name='Azuki', description='Anime-style NFTs'),
                    NFTCollection(name='Doodles', description='Colorful character NFTs'),
                    NFTCollection(name='Cool Cats', description='Cat-themed NFTs'),
                ]
                
                for collection in collections:
                    db.session.add(collection)
                
                db.session.commit()
                print("✓ Default NFT collections added")
            
            print("\n🎉 Neon PostgreSQL database setup completed successfully!")
            print("Database URL:", os.environ.get('DATABASE_URL')[:50] + "...")
            print("\nAdmin credentials:")
            print("Email: admin@platform.com")
            print("Password: admin123")
            
    except Exception as e:
        print(f"❌ Database setup failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    setup_database()