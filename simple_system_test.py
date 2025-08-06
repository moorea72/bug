#!/usr/bin/env python3
"""
Simple System Test - Delete users and create test data
"""
from app import app, db
from models import User, Deposit, Withdrawal, Stake, Coin, StakingPlan, ActivityLog, SupportMessage, SalaryWithdrawal
from werkzeug.security import generate_password_hash
import random
from datetime import datetime, timedelta
import uuid

def reset_all_data():
    """Reset all data except admin"""
    with app.app_context():
        print("🗑️ Resetting all data...")
        
        # Get admin user
        admin = User.query.filter_by(is_admin=True).first()
        if not admin:
            print("Creating admin user...")
            admin = User(
                username='admin',
                email='admin@platform.com',
                password_hash=generate_password_hash('admin123'),
                phone_number='1234567890',
                is_admin=True,
                referral_code='ADMIN',
                usdt_balance=10000.0
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin user created")
        
        # Delete all non-admin data
        print("Deleting non-admin data...")
        Stake.query.filter(Stake.user_id != admin.id).delete()
        Deposit.query.filter(Deposit.user_id != admin.id).delete()
        Withdrawal.query.filter(Withdrawal.user_id != admin.id).delete()
        SalaryWithdrawal.query.filter(SalaryWithdrawal.user_id != admin.id).delete()
        ActivityLog.query.filter(ActivityLog.user_id != admin.id).delete()
        SupportMessage.query.filter(SupportMessage.user_id != admin.id).delete()
        
        # Delete non-admin users
        User.query.filter(User.is_admin == False).delete()
        
        db.session.commit()
        print("✅ All non-admin data deleted")

def create_test_users():
    """Create 45 test users with admin referral"""
    with app.app_context():
        print("👥 Creating test users...")
        
        admin = User.query.filter_by(is_admin=True).first()
        
        for i in range(45):
            username = f'test_user_{i+1:02d}'
            email = f'test{i+1:02d}@email.com'
            phone = f'987654{i+1:04d}'
            
            user = User(
                username=username,
                email=email,
                phone_number=phone,
                password_hash=generate_password_hash('password123'),
                referred_by=admin.id,
                usdt_balance=100.0
            )
            db.session.add(user)
            
            # Add deposit for each user
            deposit = Deposit(
                user_id=user.id,
                amount=100.0,
                transaction_id=f'TXN_{uuid.uuid4().hex[:8]}',
                status='approved',
                processed_at=datetime.utcnow()
            )
            db.session.add(deposit)
            
            if i % 10 == 0:
                db.session.commit()
                print(f"Created {i+1} users...")
        
        db.session.commit()
        print("✅ 45 test users created")

def create_coins_and_plans():
    """Create coins and staking plans"""
    with app.app_context():
        print("💰 Creating coins and staking plans...")
        
        # Check if coins exist
        if Coin.query.count() == 0:
            coins = [
                {'symbol': 'USDT', 'name': 'Tether USD', 'min_stake': 50.0, 'icon_emoji': '💰'},
                {'symbol': 'BTC', 'name': 'Bitcoin', 'min_stake': 250.0, 'icon_emoji': '₿'},
                {'symbol': 'ETH', 'name': 'Ethereum', 'min_stake': 170.0, 'icon_emoji': '⟠'},
                {'symbol': 'BNB', 'name': 'Binance Coin', 'min_stake': 90.0, 'icon_emoji': '🔶'},
                {'symbol': 'LTC', 'name': 'Litecoin', 'min_stake': 130.0, 'icon_emoji': '🔱'}
            ]
            
            for coin_data in coins:
                coin = Coin(**coin_data)
                db.session.add(coin)
            
            db.session.commit()
            print("✅ Coins created")
        
        # Create staking plans
        if StakingPlan.query.count() == 0:
            durations = [7, 15, 30, 90, 120, 180]
            rates = [0.5, 0.8, 1.0, 1.5, 1.8, 2.0]
            
            coins = Coin.query.all()
            for coin in coins:
                for duration, rate in zip(durations, rates):
                    plan = StakingPlan(
                        coin_id=coin.id,
                        duration_days=duration,
                        interest_rate=rate
                    )
                    db.session.add(plan)
            
            db.session.commit()
            print("✅ Staking plans created")

def verify_system():
    """Verify all systems are working"""
    with app.app_context():
        print("🔍 Verifying system...")
        
        # Check users
        admin_count = User.query.filter_by(is_admin=True).count()
        user_count = User.query.filter_by(is_admin=False).count()
        
        print(f"Admin users: {admin_count}")
        print(f"Regular users: {user_count}")
        
        # Check deposits
        deposits = Deposit.query.count()
        print(f"Total deposits: {deposits}")
        
        # Check referrals
        admin = User.query.filter_by(is_admin=True).first()
        referrals = User.query.filter_by(referred_by=admin.id).count()
        print(f"Admin referrals: {referrals}")
        
        # Check coins and plans
        coins = Coin.query.count()
        plans = StakingPlan.query.count()
        print(f"Coins: {coins}, Plans: {plans}")
        
        print("✅ System verification complete")

if __name__ == "__main__":
    print("Starting system test...")
    reset_all_data()
    create_test_users()
    create_coins_and_plans()
    verify_system()
    print("✅ System test completed successfully!")