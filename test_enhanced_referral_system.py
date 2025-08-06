#!/usr/bin/env python3
"""
Test script for Enhanced Referral System
Tests the new balance-based referral commission system
"""

from app import app, db
from models import User, Deposit, ActivityLog, PlatformSettings
from referral_utils import recalculate_all_referral_commissions
from enhanced_referral_system import get_referral_stats

def create_test_scenario():
    """Create test scenario with users and deposits"""
    print("Creating test scenario...")
    
    with app.app_context():
        # Clear existing data
        ActivityLog.query.filter_by(action='referral_commission').delete()
        ActivityLog.query.filter_by(action='referral_commission_removed').delete()
        
        # Create admin user
        admin = User.query.filter_by(is_admin=True).first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@platform.com',
                phone_number='+1234567890',
                is_admin=True,
                usdt_balance=10000.0,
                referral_code='ADMIN123'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.flush()
        
        # Reset admin balance
        admin.usdt_balance = 10000.0
        admin.referral_bonus = 0.0
        
        # Create test users with different balance scenarios
        test_users = []
        
        # User 1: Has 150 USDT balance (qualifies for commission)
        user1 = User.query.filter_by(username='testuser1').first()
        if not user1:
            user1 = User(
                username='testuser1',
                email='test1@test.com',
                phone_number='+1111111111',
                referred_by=admin.id,
                usdt_balance=150.0,
                referral_code='TEST001'
            )
            user1.set_password('password')
            db.session.add(user1)
            db.session.flush()
            
            # Add approved deposit
            deposit1 = Deposit(
                user_id=user1.id,
                amount=150.0,
                transaction_id='0x111111111111111111111111111111111111111111111111111111111111111',
                status='approved'
            )
            db.session.add(deposit1)
        else:
            user1.usdt_balance = 150.0
        
        test_users.append(user1)
        
        # User 2: Has 50 USDT balance (does not qualify)
        user2 = User.query.filter_by(username='testuser2').first()
        if not user2:
            user2 = User(
                username='testuser2',
                email='test2@test.com',
                phone_number='+2222222222',
                referred_by=admin.id,
                usdt_balance=50.0,
                referral_code='TEST002'
            )
            user2.set_password('password')
            db.session.add(user2)
            db.session.flush()
            
            # Add approved deposit
            deposit2 = Deposit(
                user_id=user2.id,
                amount=50.0,
                transaction_id='0x222222222222222222222222222222222222222222222222222222222222222',
                status='approved'
            )
            db.session.add(deposit2)
        else:
            user2.usdt_balance = 50.0
        
        test_users.append(user2)
        
        # User 3: Has 120 USDT balance (qualifies for commission)
        user3 = User.query.filter_by(username='testuser3').first()
        if not user3:
            user3 = User(
                username='testuser3',
                email='test3@test.com',
                phone_number='+3333333333',
                referred_by=admin.id,
                usdt_balance=120.0,
                referral_code='TEST003'
            )
            user3.set_password('password')
            db.session.add(user3)
            db.session.flush()
            
            # Add approved deposit
            deposit3 = Deposit(
                user_id=user3.id,
                amount=120.0,
                transaction_id='0x333333333333333333333333333333333333333333333333333333333333333',
                status='approved'
            )
            db.session.add(deposit3)
        else:
            user3.usdt_balance = 120.0
        
        test_users.append(user3)
        
        db.session.commit()
        
        print(f"Created test scenario with {len(test_users)} users")
        print(f"Admin ID: {admin.id}")
        for i, user in enumerate(test_users, 1):
            print(f"User {i}: {user.username} - Balance: ${user.usdt_balance}")
        
        return admin, test_users

def test_referral_system():
    """Test the enhanced referral system"""
    print("\n" + "="*50)
    print("TESTING ENHANCED REFERRAL SYSTEM")
    print("="*50)
    
    admin, test_users = create_test_scenario()
    
    print(f"\nBefore recalculation:")
    print(f"Admin referral bonus: ${admin.referral_bonus}")
    print(f"Admin active referrals: {admin.get_active_referrals_count()}")
    
    # Test the recalculation
    print("\nRunning referral commission recalculation...")
    recalculate_all_referral_commissions()
    
    # Check results
    admin_after = User.query.get(admin.id)
    
    print(f"\nAfter recalculation:")
    print(f"Admin referral bonus: ${admin_after.referral_bonus}")
    print(f"Admin active referrals: {admin_after.get_active_referrals_count()}")
    
    # Expected: 2 users qualify (150 + 120 = 270 USDT * 5% = 13.5 USDT)
    expected_commission = (150 + 120) * 0.05  # 5% commission
    print(f"Expected commission: ${expected_commission}")
    print(f"Actual commission: ${admin_after.referral_bonus}")
    
    # Check activity logs
    commission_logs = ActivityLog.query.filter_by(
        user_id=admin.id,
        action='referral_commission'
    ).all()
    
    print(f"\nCommission logs ({len(commission_logs)}):")
    for log in commission_logs:
        print(f"- {log.description}")
    
    # Test referral stats
    print(f"\nReferral Statistics:")
    stats = get_referral_stats(admin.id)
    if stats:
        print(f"Total referrals: {stats['total_referrals']}")
        print(f"Active referrals: {stats['active_referrals']}")
        print(f"Inactive referrals: {stats['inactive_referrals']}")
        print(f"Total commission: ${stats['total_commission']}")
        
        print(f"\nReferral details:")
        for detail in stats['referral_details']:
            status = "✅ Active" if detail['is_active'] else "❌ Inactive"
            print(f"- {detail['username']}: ${detail['total_balance']:.2f} - {status}")
    
    return admin_after, test_users

def test_balance_drop_scenario():
    """Test when user balance drops below 100 USDT"""
    print("\n" + "="*50)
    print("TESTING BALANCE DROP SCENARIO")
    print("="*50)
    
    admin, test_users = test_referral_system()
    
    # Find user with balance > 100
    qualifying_user = None
    for user in test_users:
        if user.usdt_balance >= 100:
            qualifying_user = user
            break
    
    if qualifying_user:
        print(f"\nBefore balance drop:")
        print(f"User {qualifying_user.username} balance: ${qualifying_user.usdt_balance}")
        print(f"Admin referral bonus: ${admin.referral_bonus}")
        
        # Simulate balance drop (e.g., withdrawal)
        qualifying_user.usdt_balance = 80.0  # Below 100 USDT
        
        # Check and update referral balance
        from referral_utils import check_and_update_referral_balance
        check_and_update_referral_balance(qualifying_user)
        
        db.session.commit()
        
        # Check results
        admin_after = User.query.get(admin.id)
        print(f"\nAfter balance drop:")
        print(f"User {qualifying_user.username} balance: ${qualifying_user.usdt_balance}")
        print(f"Admin referral bonus: ${admin_after.referral_bonus}")
        print(f"Admin active referrals: {admin_after.get_active_referrals_count()}")
        
        # Check removal logs
        removal_logs = ActivityLog.query.filter_by(
            user_id=admin.id,
            action='referral_commission_removed'
        ).all()
        
        print(f"\nRemoval logs ({len(removal_logs)}):")
        for log in removal_logs:
            print(f"- {log.description}")

if __name__ == "__main__":
    test_referral_system()
    test_balance_drop_scenario()
    print("\n" + "="*50)
    print("TESTING COMPLETE")
    print("="*50)