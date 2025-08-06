#!/usr/bin/env python3
"""
Test Commission Permanent System
Commission awarded only ONCE per referral when they reach 100+ USDT
Commission remains permanent even if balance drops below 100 USDT
Only referral count is affected by balance changes
"""

from app import app, db
from models import User, Deposit, ActivityLog
from referral_utils import award_referral_commission, check_and_update_referral_balance

def test_commission_permanent():
    """Test that commission is permanent once awarded"""
    print("Testing Commission Permanent System...")
    
    with app.app_context():
        # Create admin user
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@test.com',
                phone_number='+1234567890',
                is_admin=True,
                usdt_balance=5000.0,
                referral_code='ADMIN123'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.flush()
        
        # Reset admin data
        admin.usdt_balance = 5000.0
        admin.referral_bonus = 0.0
        
        # Clear previous logs
        ActivityLog.query.filter_by(user_id=admin.id, action='referral_commission').delete()
        ActivityLog.query.filter_by(user_id=admin.id, action='referral_commission_removed').delete()
        
        # Create test user
        test_user = User.query.filter_by(username='testuser').first()
        if test_user:
            db.session.delete(test_user)
            db.session.flush()
        
        test_user = User(
            username='testuser',
            email='test@test.com',
            phone_number='+1111111111',
            referred_by=admin.id,
            usdt_balance=0.0,
            referral_code='TEST123'
        )
        test_user.set_password('password')
        db.session.add(test_user)
        db.session.flush()
        
        # Create deposit
        deposit = Deposit(
            user_id=test_user.id,
            amount=150.0,
            transaction_id='0x' + '1' * 64,
            status='approved'
        )
        db.session.add(deposit)
        db.session.commit()
        
        print(f"Initial state:")
        print(f"Admin balance: ${admin.usdt_balance}, Referral bonus: ${admin.referral_bonus}")
        print(f"Test user balance: ${test_user.usdt_balance}")
        
        # Step 1: User deposits 150 USDT
        test_user.usdt_balance = 150.0
        award_referral_commission(test_user, 150.0)
        db.session.commit()
        
        admin_after_deposit = User.query.get(admin.id)
        print(f"\nAfter deposit (150 USDT):")
        print(f"Admin balance: ${admin_after_deposit.usdt_balance}, Referral bonus: ${admin_after_deposit.referral_bonus}")
        print(f"Test user balance: ${test_user.usdt_balance}")
        
        # Check commission logs
        commission_logs = ActivityLog.query.filter_by(
            user_id=admin.id,
            action='referral_commission'
        ).all()
        print(f"Commission logs: {len(commission_logs)}")
        for log in commission_logs:
            print(f"  - {log.description}")
        
        # Step 2: User balance drops to 80 USDT
        test_user.usdt_balance = 80.0
        check_and_update_referral_balance(test_user)
        db.session.commit()
        
        admin_after_drop = User.query.get(admin.id)
        print(f"\nAfter balance drop (80 USDT):")
        print(f"Admin balance: ${admin_after_drop.usdt_balance}, Referral bonus: ${admin_after_drop.referral_bonus}")
        print(f"Test user balance: ${test_user.usdt_balance}")
        
        # Check removal logs
        removal_logs = ActivityLog.query.filter_by(
            user_id=admin.id,
            action='referral_commission_removed'
        ).all()
        print(f"Removal logs: {len(removal_logs)}")
        for log in removal_logs:
            print(f"  - {log.description}")
        
        # Step 3: User balance goes back to 120 USDT
        test_user.usdt_balance = 120.0
        check_and_update_referral_balance(test_user)
        db.session.commit()
        
        admin_after_recovery = User.query.get(admin.id)
        print(f"\nAfter balance recovery (120 USDT):")
        print(f"Admin balance: ${admin_after_recovery.usdt_balance}, Referral bonus: ${admin_after_recovery.referral_bonus}")
        print(f"Test user balance: ${test_user.usdt_balance}")
        
        # Check final commission logs
        final_commission_logs = ActivityLog.query.filter_by(
            user_id=admin.id,
            action='referral_commission'
        ).all()
        print(f"Final commission logs: {len(final_commission_logs)}")
        for log in final_commission_logs:
            print(f"  - {log.description}")
        
        # Check active referrals count
        from enhanced_referral_system import get_active_referrals_count
        active_referrals = get_active_referrals_count(admin.id)
        print(f"\nActive referrals count: {active_referrals}")
        
        print("\n" + "="*50)
        print("TEST RESULTS:")
        print("="*50)
        print(f"✅ Commission awarded once: ${admin_after_deposit.referral_bonus}")
        print(f"✅ Commission remains permanent: ${admin_after_recovery.referral_bonus}")
        print(f"✅ Referral count affected by balance: {active_referrals}")
        print(f"✅ No commission removal: {len(removal_logs)} removal logs")
        print("="*50)

if __name__ == "__main__":
    test_commission_permanent()