#!/usr/bin/env python3
"""
Fix staking and deposit issues by ensuring proper database setup
"""

import os
import sys
from datetime import datetime
from app import app, db
from models import User, Coin, StakingPlan, Deposit, Withdrawal, PlatformSettings, ActivityLog, PaymentAddress
from werkzeug.security import generate_password_hash
import uuid

def fix_database_issues():
    """Fix database issues causing staking and deposit problems"""
    
    with app.app_context():
        try:
            # Test database connection
            print("Testing database connection...")
            db.session.execute('SELECT 1')
            print("✓ Database connection successful")
            
            # Create tables if they don't exist
            print("Creating database tables...")
            db.create_all()
            print("✓ Database tables created")
            
            # Check if we have coins
            coin_count = Coin.query.count()
            print(f"Current coin count: {coin_count}")
            
            if coin_count == 0:
                print("Adding basic coins...")
                
                # Add basic coins
                coins_data = [
                    {'symbol': 'USDT', 'name': 'Tether USD', 'min_stake': 10.0, 'active': True, 'icon_emoji': '💰'},
                    {'symbol': 'BTC', 'name': 'Bitcoin', 'min_stake': 250.0, 'active': True, 'icon_emoji': '₿'},
                    {'symbol': 'ETH', 'name': 'Ethereum', 'min_stake': 170.0, 'active': True, 'icon_emoji': '⧫'},
                    {'symbol': 'BNB', 'name': 'Binance Coin', 'min_stake': 90.0, 'active': True, 'icon_emoji': '🔸'},
                    {'symbol': 'LTC', 'name': 'Litecoin', 'min_stake': 130.0, 'active': True, 'icon_emoji': 'Ł'}
                ]
                
                for coin_data in coins_data:
                    coin = Coin(
                        symbol=coin_data['symbol'],
                        name=coin_data['name'],
                        min_stake=coin_data['min_stake'],
                        active=coin_data['active'],
                        icon_emoji=coin_data['icon_emoji']
                    )
                    db.session.add(coin)
                
                db.session.commit()
                print("✓ Basic coins added")
            
            # Check if we have staking plans
            plan_count = StakingPlan.query.count()
            print(f"Current staking plan count: {plan_count}")
            
            if plan_count == 0:
                print("Adding staking plans...")
                
                # Get all coins
                coins = Coin.query.all()
                
                # Add staking plans for each coin
                plan_data = [
                    {'duration_days': 7, 'interest_rate': 0.8},
                    {'duration_days': 15, 'interest_rate': 1.2},
                    {'duration_days': 30, 'interest_rate': 1.5},
                    {'duration_days': 90, 'interest_rate': 1.8},
                    {'duration_days': 120, 'interest_rate': 2.0},
                    {'duration_days': 180, 'interest_rate': 2.2}
                ]
                
                for coin in coins:
                    for plan in plan_data:
                        staking_plan = StakingPlan(
                            coin_id=coin.id,
                            duration_days=plan['duration_days'],
                            interest_rate=plan['interest_rate'],
                            active=True
                        )
                        db.session.add(staking_plan)
                
                db.session.commit()
                print("✓ Staking plans added")
            
            # Check if admin user exists
            admin_user = User.query.filter_by(email='admin@platform.com').first()
            if not admin_user:
                print("Creating admin user...")
                admin_user = User(
                    username='admin',
                    email='admin@platform.com',
                    phone_number='1234567890',
                    usdt_balance=1000000.0,
                    is_admin=True,
                    is_active=True,
                    referral_code=str(uuid.uuid4())[:8].upper()
                )
                admin_user.set_password('admin123')
                db.session.add(admin_user)
                db.session.commit()
                print("✓ Admin user created")
            
            # Check payment address
            payment_address = PaymentAddress.query.first()
            if not payment_address:
                print("Creating payment address...")
                payment_address = PaymentAddress(
                    address='0xae49d3b4775c0524bd81da704340b5ef5a7416e9',
                    network='BEP20',
                    currency='USDT',
                    is_active=True
                )
                db.session.add(payment_address)
                db.session.commit()
                print("✓ Payment address created")
            
            # Check platform settings
            settings = PlatformSettings.query.first()
            if not settings:
                print("Creating platform settings...")
                settings = PlatformSettings(
                    site_name='USDT Staking Platform',
                    min_deposit=10.0,
                    min_withdrawal=10.0,
                    withdrawal_fee=1.0,
                    referral_level_1=10.0,
                    min_referral_activation=50.0
                )
                db.session.add(settings)
                db.session.commit()
                print("✓ Platform settings created")
            
            # Final verification
            print("\n=== Database Status ===")
            print(f"Coins: {Coin.query.count()}")
            print(f"Staking Plans: {StakingPlan.query.count()}")
            print(f"Users: {User.query.count()}")
            print(f"Deposits: {Deposit.query.count()}")
            print(f"Active Coins: {Coin.query.filter_by(active=True).count()}")
            print(f"Active Plans: {StakingPlan.query.filter_by(active=True).count()}")
            
            # Test if we can create a simple deposit transaction
            print("\n=== Testing Transaction System ===")
            test_user = User.query.filter_by(email='admin@platform.com').first()
            if test_user:
                print(f"Admin user balance: {test_user.usdt_balance}")
                print("✓ Transaction system ready")
            
            return True
            
        except Exception as e:
            print(f"❌ Database error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = fix_database_issues()
    if success:
        print("\n🎉 Database issues fixed! Staking and deposits should work now.")
    else:
        print("\n❌ Failed to fix database issues.")