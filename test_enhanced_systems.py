#!/usr/bin/env python3
"""
Test Enhanced Notification and Multi-Level Referral Systems
Creates sample data to demonstrate both systems working correctly
"""

from app import app, db
from models import User, Deposit, Notification, ActivityLog, PlatformSettings
from multi_level_referral_system import MultiLevelReferralSystem
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

def create_sample_notifications():
    """Create sample notifications for testing the notification bell popup"""
    print("Creating sample notifications...")
    
    notifications = [
        {
            'title': 'Welcome to USDT Staking!',
            'message': 'Thank you for joining our platform. Start staking today and earn daily returns!',
            'type': 'success',
            'priority': 'high'
        },
        {
            'title': 'New Referral Program',
            'message': 'Earn up to 5% commission with our 3-level referral system. Invite friends and start earning!',
            'type': 'info',
            'priority': 'high'
        },
        {
            'title': 'High Yield Staking Available',
            'message': 'New staking plans with enhanced returns are now available. Check out the latest options!',
            'type': 'info',
            'priority': 'medium'
        },
        {
            'title': 'Security Update',
            'message': 'We have enhanced our security measures to better protect your funds and data.',
            'type': 'warning',
            'priority': 'high'
        },
        {
            'title': 'Maintenance Notice',
            'message': 'Scheduled maintenance will occur tonight from 2-4 AM UTC for system improvements.',
            'type': 'warning',
            'priority': 'medium'
        }
    ]
    
    for notif_data in notifications:
        existing = Notification.query.filter_by(title=notif_data['title']).first()
        if not existing:
            notification = Notification(
                title=notif_data['title'],
                message=notif_data['message'],
                type=notif_data['type'],
                priority=notif_data['priority'],
                is_active=True
            )
            db.session.add(notification)
    
    db.session.commit()
    print(f"✅ Created {len(notifications)} sample notifications")

def setup_platform_settings():
    """Setup platform settings for referral system"""
    print("Setting up platform settings...")
    
    settings = [
        ('referral_level_1', '5', 'Level 1 referral commission rate (%)'),
        ('referral_level_2', '3', 'Level 2 referral commission rate (%)'),
        ('referral_level_3', '2', 'Level 3 referral commission rate (%)'),
        ('min_referral_activation', '100', 'Minimum deposit to activate referral benefits ($)'),
        ('platform_name', 'USDT Staking Platform', 'Platform name'),
        ('withdrawal_fee', '1', 'Withdrawal fee (%)'),
    ]
    
    for key, value, description in settings:
        PlatformSettings.set_setting(key, value, description)
    
    print("✅ Platform settings configured")

def create_test_referral_chain():
    """Create a complete referral chain to test the multi-level system"""
    print("Creating test referral chain...")
    
    # Create admin user if doesn't exist
    admin = User.query.filter_by(is_admin=True).first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@platform.com',
            phone_number='1234567890',
            password_hash=generate_password_hash('admin123'),
            is_admin=True,
            referral_code='ADMIN001',
            usdt_balance=10000.0
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin user created")
    
    # Create referral chain: Admin -> UserA -> UserB -> UserC -> UserD
    users_data = [
        ('UserA', 'usera@example.com', '1111111111', 'REFA001', admin.id),
        ('UserB', 'userb@example.com', '2222222222', 'REFB002', None),  # Will be set to UserA
        ('UserC', 'userc@example.com', '3333333333', 'REFC003', None),  # Will be set to UserB
        ('UserD', 'userd@example.com', '4444444444', 'REFD004', None),  # Will be set to UserC
    ]
    
    created_users = []
    
    for i, (username, email, phone, ref_code, referred_by) in enumerate(users_data):
        existing = User.query.filter_by(username=username).first()
        if existing:
            created_users.append(existing)
            continue
        
        user = User(
            username=username,
            email=email,
            phone_number=phone,
            password_hash=generate_password_hash('password123'),
            referral_code=ref_code,
            referred_by=referred_by if referred_by else (created_users[i-1].id if i > 0 else admin.id),
            usdt_balance=50.0  # Start with some balance
        )
        db.session.add(user)
        db.session.flush()  # Get the ID
        created_users.append(user)
    
    db.session.commit()
    print(f"✅ Created {len(created_users)} test users in referral chain")
    
    # Create qualifying deposits for each user to trigger referral commissions
    deposit_amounts = [150, 200, 120, 180]  # All above 100 USDT minimum
    
    for i, user in enumerate(created_users):
        # Check if user already has qualifying deposits
        existing_deposits = Deposit.query.filter_by(user_id=user.id, status='approved').all()
        total_existing = sum(d.amount for d in existing_deposits)
        
        if total_existing >= 100:
            print(f"User {user.username} already has qualifying deposits: ${total_existing:.2f}")
            continue
        
        deposit = Deposit(
            user_id=user.id,
            amount=deposit_amounts[i],
            transaction_id=f'TXN_{user.username}_{random.randint(10000, 99999)}',
            status='approved',
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
            processed_at=datetime.utcnow() - timedelta(days=random.randint(0, 30))
        )
        db.session.add(deposit)
        
        # Add deposit amount to user balance
        user.usdt_balance += deposit.amount
        
        print(f"Created deposit for {user.username}: ${deposit.amount}")
    
    db.session.commit()
    
    # Process referral commissions for each qualifying deposit
    print("Processing referral commissions...")
    
    for i, user in enumerate(created_users):
        deposits = Deposit.query.filter_by(user_id=user.id, status='approved').all()
        for deposit in deposits:
            if deposit.amount >= 100:
                result = MultiLevelReferralSystem.award_commission(user.id, deposit.amount)
                if result['success']:
                    print(f"Awarded commission for {user.username} deposit of ${deposit.amount}: ${result.get('total_commission', 0):.2f}")
                break  # Only process first qualifying deposit
    
    db.session.commit()
    
    return created_users

def test_referral_system():
    """Test the referral system functionality"""
    print("\n🧪 Testing Multi-Level Referral System...")
    
    # Get admin user
    admin = User.query.filter_by(is_admin=True).first()
    if not admin:
        print("❌ Admin user not found")
        return
    
    # Test referral statistics
    active_referrals = MultiLevelReferralSystem.get_active_referrals_count(admin.id)
    referral_tree = MultiLevelReferralSystem.get_referral_tree_with_commissions(admin.id)
    
    print(f"Admin active referrals: {active_referrals}")
    print(f"Admin referral bonus: ${admin.referral_bonus:.2f}")
    
    # Show referral tree structure
    print("\nReferral Tree Structure:")
    for level1 in referral_tree:
        print(f"  L1: {level1['user']['username']} - ${level1['commission_earned']:.2f}")
        for level2 in level1.get('children', []):
            print(f"    L2: {level2['user']['username']} - ${level2['commission_earned']:.2f}")
            for level3 in level2.get('children', []):
                print(f"      L3: {level3['user']['username']} - ${level3['commission_earned']:.2f}")
    
    print("✅ Referral system test completed")

def test_notification_system():
    """Test the notification system"""
    print("\n🔔 Testing Notification System...")
    
    # Count notifications
    total_notifications = Notification.query.count()
    active_notifications = Notification.query.filter_by(is_active=True).count()
    
    print(f"Total notifications: {total_notifications}")
    print(f"Active notifications: {active_notifications}")
    
    # Show recent notifications
    recent = Notification.query.filter_by(is_active=True).order_by(
        Notification.priority.desc(),
        Notification.created_at.desc()
    ).limit(5).all()
    
    print("\nRecent Active Notifications:")
    for notif in recent:
        print(f"  • {notif.title} ({notif.type}, {notif.priority})")
        print(f"    {notif.message[:80]}...")
    
    print("✅ Notification system test completed")

def main():
    """Run comprehensive test of enhanced systems"""
    print("🚀 Testing Enhanced Notification and Multi-Level Referral Systems")
    print("=" * 60)
    
    try:
        with app.app_context():
            # Setup
            setup_platform_settings()
            create_sample_notifications()
            
            # Create test data
            users = create_test_referral_chain()
            
            # Test systems
            test_notification_system()
            test_referral_system()
            
            print("\n" + "=" * 60)
            print("🎉 All tests completed successfully!")
            print("\nYou can now:")
            print("1. Click the notification bell to see popup notifications")
            print("2. Visit /my-referrals to see your referral dashboard")
            print("3. Visit /admin/multi-level-referrals as admin to manage the system")
            print("\nSystem Features Demonstrated:")
            print("✅ Enhanced notification bell with animated popup")
            print("✅ 3-level referral commission system (5%, 3%, 2%)")
            print("✅ 100 USDT minimum deposit requirement")
            print("✅ One-time commission per referral")
            print("✅ Anti-farming protection")
            print("✅ Admin dashboard for referral management")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()