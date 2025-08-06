#!/usr/bin/env python3
"""
Create 25 admin referral users with deposits for testing referral salary commission system
"""

from app import app, db
from models import User, Deposit, Coin, StakingPlan, Stake
from werkzeug.security import generate_password_hash
import uuid
import random
from datetime import datetime, timedelta

def create_admin_referral_users():
    """Create 25 users with referral code 'ADMIN' and various deposits"""
    
    with app.app_context():
        print("Creating admin referral users for testing...")
        
        # Get admin user
        admin = User.query.filter_by(email='admin@platform.com').first()
        if not admin:
            print("Admin user not found, creating...")
            admin = User(
                username='admin',
                email='admin@platform.com',
                phone_number='+1234567890',
                is_admin=True,
                is_active=True,
                usdt_balance=10000.0,
                referral_code='ADMIN'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created")
        
        # Ensure admin has referral code
        if not admin.referral_code:
            admin.referral_code = 'ADMIN'
            db.session.commit()
        
        # Create 25 referral users
        users_created = 0
        
        for i in range(1, 26):
            username = f'refuser{i:02d}'
            email = f'refuser{i:02d}@test.com'
            phone = f'+1555{i:03d}0000'
            
            # Check if user already exists
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                print(f"User {username} already exists, skipping...")
                continue
            
            # Create new user
            user = User(
                username=username,
                email=email,
                phone_number=phone,
                is_admin=False,
                is_active=True,
                usdt_balance=random.uniform(100, 2000),  # Random balance 100-2000 USDT
                referred_by=admin.id,  # Set admin as referrer
                referral_code=str(uuid.uuid4())[:8].upper()
            )
            user.set_password('password123')
            db.session.add(user)
            users_created += 1
            
            # Create deposit for user
            deposit_amount = random.uniform(50, 1000)
            deposit = Deposit(
                user_id=user.id,
                amount=deposit_amount,
                transaction_id=f'TX{uuid.uuid4().hex[:16].upper()}',
                status='approved',
                network='BEP20',
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
            )
            db.session.add(deposit)
            
            # Add some stakes for realistic testing
            if random.choice([True, False]):  # 50% chance of having stakes
                coins = Coin.query.filter_by(active=True).all()
                if coins:
                    coin = random.choice(coins)
                    plans = StakingPlan.query.filter_by(coin_id=coin.id, active=True).all()
                    if plans:
                        plan = random.choice(plans)
                        stake_amount = min(user.usdt_balance * 0.5, random.uniform(50, 500))
                        
                        stake = Stake(
                            user_id=user.id,
                            coin_id=coin.id,
                            plan_id=plan.id,
                            amount=stake_amount,
                            daily_interest=plan.interest_rate,
                            total_return=stake_amount * plan.interest_rate * plan.duration_days / 100,
                            end_date=datetime.utcnow() + timedelta(days=plan.duration_days),
                            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 10))
                        )
                        db.session.add(stake)
                        user.total_staked += stake_amount
                        user.usdt_balance -= stake_amount
        
        # Commit all changes
        db.session.commit()
        
        # Update admin's referral count
        admin_referral_count = User.query.filter_by(referred_by=admin.id).count()
        
        print(f"Successfully created {users_created} admin referral users")
        print(f"Admin now has {admin_referral_count} total referrals")
        
        # Check salary eligibility
        if admin_referral_count >= 6:
            salary_amount = 50 if admin_referral_count < 13 else (110 if admin_referral_count < 25 else 250)
            print(f"Admin is eligible for ${salary_amount}/month salary with {admin_referral_count} referrals")
        else:
            print(f"Admin needs {6 - admin_referral_count} more referrals for salary eligibility")
        
        return {
            'success': True,
            'users_created': users_created,
            'admin_referral_count': admin_referral_count,
            'message': f'Created {users_created} referral users for admin testing'
        }

if __name__ == '__main__':
    result = create_admin_referral_users()
    print(f"Result: {result}")