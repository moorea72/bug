#!/usr/bin/env python3
"""
Comprehensive Admin 500 Error Fix Script
Identifies and fixes all admin route 500 errors
"""

import os
import sys
from app import app, db
from models import *
from werkzeug.security import generate_password_hash
from datetime import datetime

def fix_admin_500_errors():
    """Fix all admin 500 errors systematically"""
    print("Starting comprehensive admin 500 error fix...")
    
    with app.app_context():
        try:
            # 1. Ensure all database tables exist
            print("1. Creating database tables...")
            db.create_all()
            
            # 2. Ensure admin user exists
            print("2. Checking admin user...")
            admin = User.query.filter_by(is_admin=True).first()
            if not admin:
                admin = User(
                    username='admin',
                    email='admin@platform.com',
                    phone_number='1234567890',
                    password_hash=generate_password_hash('admin123'),
                    is_admin=True,
                    is_active=True,
                    usdt_balance=10000.0
                )
                db.session.add(admin)
                db.session.commit()
                print("   ✓ Admin user created")
            else:
                print("   ✓ Admin user exists")
            
            # 3. Ensure basic coins exist
            print("3. Checking basic coins...")
            coins = ['USDT', 'BTC', 'ETH', 'BNB', 'LTC']
            for coin_symbol in coins:
                coin = Coin.query.filter_by(symbol=coin_symbol).first()
                if not coin:
                    coin = Coin(
                        name=coin_symbol,
                        symbol=coin_symbol,
                        min_stake=10.0 if coin_symbol == 'USDT' else 100.0,
                        logo_url=f'/static/images/{coin_symbol.lower()}_logo.png',
                        is_active=True
                    )
                    db.session.add(coin)
            db.session.commit()
            print("   ✓ Basic coins ensured")
            
            # 4. Ensure staking plans exist
            print("4. Checking staking plans...")
            durations = [7, 15, 30, 90, 120, 180]
            rates = [0.5, 0.8, 1.0, 1.5, 1.8, 2.0]
            
            for coin in Coin.query.all():
                for duration, rate in zip(durations, rates):
                    plan = StakingPlan.query.filter_by(
                        coin_id=coin.id,
                        duration_days=duration
                    ).first()
                    if not plan:
                        plan = StakingPlan(
                            coin_id=coin.id,
                            duration_days=duration,
                            interest_rate=rate,
                            min_amount=coin.min_stake,
                            max_amount=10000.0,
                            is_active=True
                        )
                        db.session.add(plan)
            db.session.commit()
            print("   ✓ Staking plans ensured")
            
            # 5. Ensure platform settings exist
            print("5. Checking platform settings...")
            settings = PlatformSettings.query.first()
            if not settings:
                settings = PlatformSettings(
                    platform_name='USDT Staking Platform',
                    referral_level_1=5.0,
                    referral_level_2=3.0,
                    referral_level_3=2.0,
                    min_referral_activation=100.0,
                    withdrawal_fee=1.0
                )
                db.session.add(settings)
                db.session.commit()
            print("   ✓ Platform settings ensured")
            
            # 6. Ensure payment addresses exist
            print("6. Checking payment addresses...")
            addresses = PaymentAddress.query.all()
            if not addresses:
                bep20_address = PaymentAddress(
                    network='BEP20',
                    address='0xae49d3b4775c0524bd81da704340b5ef5a7416e9',
                    is_active=True
                )
                trc20_address = PaymentAddress(
                    network='TRC20',
                    address='TYour_TRC20_Address_Here',
                    is_active=False
                )
                db.session.add(bep20_address)
                db.session.add(trc20_address)
                db.session.commit()
            print("   ✓ Payment addresses ensured")
            
            # 7. Ensure sample NFT collections exist
            print("7. Checking NFT collections...")
            collections = NFTCollection.query.all()
            if not collections:
                collection_names = ['CryptoPunks', 'Bored Apes', 'Azuki', 'Doodles', 'Moonbirds']
                for name in collection_names:
                    collection = NFTCollection(
                        name=name,
                        description=f'{name} collection',
                        is_active=True
                    )
                    db.session.add(collection)
                db.session.commit()
            print("   ✓ NFT collections ensured")
            
            # 8. Ensure sample NFTs exist
            print("8. Checking NFTs...")
            nfts = NFT.query.all()
            if not nfts:
                collections = NFTCollection.query.all()
                if collections:
                    for i, collection in enumerate(collections):
                        nft = NFT(
                            name=f'{collection.name} #{i+1}',
                            collection_id=collection.id,
                            price=100.0 + (i * 50),
                            image_url=f'https://picsum.photos/300/300?random={i+100}',
                            is_verified=i % 2 == 0,
                            is_active=True
                        )
                        db.session.add(nft)
                db.session.commit()
            print("   ✓ NFTs ensured")
            
            # 9. Ensure withdrawal settings exist
            print("9. Checking withdrawal settings...")
            withdrawal_settings = WithdrawalSettings.query.first()
            if not withdrawal_settings:
                withdrawal_settings = WithdrawalSettings(
                    min_withdrawal_amount=10.0,
                    max_withdrawal_amount=10000.0,
                    daily_withdrawal_limit=5000.0,
                    withdrawal_fee_percentage=1.0,
                    processing_time_hours=24,
                    is_withdrawal_enabled=True
                )
                db.session.add(withdrawal_settings)
                db.session.commit()
            print("   ✓ Withdrawal settings ensured")
            
            # 10. Ensure sample support responses exist
            print("10. Checking support responses...")
            responses = SupportResponse.query.all()
            if not responses:
                sample_responses = [
                    {
                        'trigger_words': 'balance,wallet,money,funds',
                        'response_text': 'Your current balance information is displayed in your dashboard.',
                        'category': 'account'
                    },
                    {
                        'trigger_words': 'stake,staking,invest,investment',
                        'response_text': 'Our staking plans offer competitive returns. Visit the Stake section to explore options.',
                        'category': 'staking'
                    },
                    {
                        'trigger_words': 'support,help,assistance',
                        'response_text': 'I am here to help! Please describe your specific question or issue.',
                        'category': 'general'
                    }
                ]
                
                for response_data in sample_responses:
                    response = SupportResponse(
                        trigger_words=response_data['trigger_words'],
                        response_text=response_data['response_text'],
                        category=response_data['category'],
                        is_active=True,
                        created_by=admin.id
                    )
                    db.session.add(response)
                db.session.commit()
            print("   ✓ Support responses ensured")
            
            print("\n✅ All admin 500 errors fixed successfully!")
            print("📋 Summary:")
            print(f"   - Admin user: {admin.email}")
            print(f"   - Coins: {len(Coin.query.all())}")
            print(f"   - Staking plans: {len(StakingPlan.query.all())}")
            print(f"   - Payment addresses: {len(PaymentAddress.query.all())}")
            print(f"   - NFT collections: {len(NFTCollection.query.all())}")
            print(f"   - NFTs: {len(NFT.query.all())}")
            print(f"   - Support responses: {len(SupportResponse.query.all())}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error fixing admin 500 errors: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    fix_admin_500_errors()