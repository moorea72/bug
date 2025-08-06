#!/usr/bin/env python3
"""
Test and fix referral commission system
"""
from app import app, db
from models import User, Deposit, PlatformSettings, ActivityLog
from referral_utils import award_referral_commission
from werkzeug.security import generate_password_hash
import uuid

def test_referral_commission():
    """Test referral commission system"""
    with app.app_context():
        print("Testing referral commission system...")
        
        # Get admin user
        admin = User.query.filter_by(is_admin=True).first()
        if not admin:
            print("No admin user found")
            return
        
        print(f"Admin before: Balance={admin.usdt_balance}, Bonus={admin.referral_bonus}")
        
        # Check if there are test users
        test_users = User.query.filter_by(is_admin=False).all()
        print(f"Found {len(test_users)} test users")
        
        if not test_users:
            print("Creating test users...")
            # Create a test user
            test_user = User(
                username='test_referral_user',
                email='test_referral@email.com',
                phone_number='9999999999',
                password_hash=generate_password_hash('password123'),
                referred_by=admin.id,
                usdt_balance=0.0
            )
            db.session.add(test_user)
            db.session.commit()
            
            # Create deposit for test user
            deposit = Deposit(
                user_id=test_user.id,
                amount=100.0,
                transaction_id=f'TEST_{uuid.uuid4().hex[:8]}',
                status='approved',
                processed_at=datetime.utcnow()
            )
            db.session.add(deposit)
            db.session.commit()
            
            print("Test user and deposit created")
            test_users = [test_user]
        
        # Award commission for each test user
        commissioned_count = 0
        for user in test_users:
            if user.referred_by == admin.id:
                # Reset first to avoid multiple commission issue
                deposits = Deposit.query.filter_by(user_id=user.id).all()
                for deposit in deposits:
                    if deposit.amount >= 100:
                        print(f"Awarding commission for user {user.username}: {deposit.amount} USDT")
                        award_referral_commission(user, deposit.amount)
                        commissioned_count += 1
                        break  # Only first deposit
        
        db.session.commit()
        
        # Check admin after
        admin_after = User.query.filter_by(is_admin=True).first()
        print(f"Admin after: Balance={admin_after.usdt_balance}, Bonus={admin_after.referral_bonus}")
        print(f"Commission awarded for {commissioned_count} users")
        
        # Check platform settings
        settings = PlatformSettings.get_all_settings()
        print(f"Referral Level 1 Rate: {settings.get('referral_level_1', 5)}%")
        
        expected_commission = commissioned_count * 100 * (float(settings.get('referral_level_1', 5)) / 100)
        print(f"Expected commission: {expected_commission}")
        print(f"Actual commission: {admin_after.referral_bonus}")

if __name__ == "__main__":
    test_referral_commission()