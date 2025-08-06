
#!/usr/bin/env python3
"""
Delete all users except admin and create 10 new users with admin referral
- All 10 users will have 100 USDT deposits
- All referred by admin
"""

from app import app, db
from models import User, Deposit, ActivityLog, Stake, Withdrawal
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import uuid

def delete_old_users_create_admin_referrals():
    """Delete all users except admin and create 10 new users with admin referral"""
    
    with app.app_context():
        print("🚀 Starting user cleanup and creation...")
        
        # Find admin user
        admin = User.query.filter_by(is_admin=True).first()
        if not admin:
            print("❌ Admin user not found!")
            return False
        
        print(f"✅ Admin found: {admin.username} (ID: {admin.id})")
        print(f"✅ Admin referral code: {admin.referral_code}")
        
        # Get all non-admin users
        users_to_delete = User.query.filter(User.id != admin.id).all()
        print(f"🗑️ Found {len(users_to_delete)} users to delete")
        
        # Delete related records first
        for user in users_to_delete:
            # Delete deposits
            Deposit.query.filter_by(user_id=user.id).delete()
            # Delete stakes
            Stake.query.filter_by(user_id=user.id).delete()
            # Delete withdrawals
            Withdrawal.query.filter_by(user_id=user.id).delete()
            # Delete activity logs
            ActivityLog.query.filter_by(user_id=user.id).delete()
        
        # Delete users
        User.query.filter(User.id != admin.id).delete()
        
        # Reset admin referral stats
        admin.referral_bonus = 0.0
        
        db.session.commit()
        print("✅ All old users deleted")
        
        # Create 10 new users with admin referral
        user_profiles = [
            ('user_01', 'user01@test.com', '9876543210'),
            ('user_02', 'user02@test.com', '9876543211'),
            ('user_03', 'user03@test.com', '9876543212'),
            ('user_04', 'user04@test.com', '9876543213'),
            ('user_05', 'user05@test.com', '9876543214'),
            ('user_06', 'user06@test.com', '9876543215'),
            ('user_07', 'user07@test.com', '9876543216'),
            ('user_08', 'user08@test.com', '9876543217'),
            ('user_09', 'user09@test.com', '9876543218'),
            ('user_10', 'user10@test.com', '9876543219'),
        ]
        
        created_users = []
        created_deposits = []
        
        for i, (username, email, phone) in enumerate(user_profiles):
            # Create user with admin referral
            user = User(
                username=username,
                email=email,
                phone_number=phone,
                password_hash=generate_password_hash('password123'),
                usdt_balance=100.0,  # Start with 100 USDT
                referred_by=admin.id,  # All users referred by admin
                is_active=True,
                created_at=datetime.utcnow() - timedelta(days=i+1)  # Stagger creation dates
            )
            
            db.session.add(user)
            db.session.flush()  # Get user ID
            created_users.append(user)
            
            # Create deposit record for 100 USDT
            deposit = Deposit(
                user_id=user.id,
                amount=100.0,
                transaction_id=f"ADMIN_REF_{username.upper()}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{i:02d}",
                status='approved',
                blockchain_verified=True,
                verification_details=f"Admin referral deposit of $100 USDT for {username}",
                created_at=datetime.utcnow() - timedelta(days=i+1),
                processed_at=datetime.utcnow() - timedelta(days=i)
            )
            
            db.session.add(deposit)
            created_deposits.append(deposit)
            
            print(f"✅ Created user: {username} with 100 USDT deposit")
        
        # Calculate and update admin referral bonus (5% of each deposit = 5 USDT per user)
        total_referral_bonus = len(created_users) * 5.0  # 5 USDT per referral
        admin.referral_bonus = total_referral_bonus
        admin.usdt_balance += total_referral_bonus
        
        # Commit all changes
        db.session.commit()
        
        print(f"\n🎉 Successfully completed user creation!")
        print(f"   👥 Created: {len(created_users)} users")
        print(f"   💰 Deposits: {len(created_deposits)} x 100 USDT")
        print(f"   🎯 Admin referral bonus: ${total_referral_bonus} USDT")
        print(f"   📊 Admin new balance: ${admin.usdt_balance} USDT")
        
        # Verify final counts
        total_users = User.query.count()
        admin_referrals = User.query.filter_by(referred_by=admin.id).count()
        total_deposits = Deposit.query.filter_by(status='approved').count()
        
        print(f"\n📈 Final Statistics:")
        print(f"   Total users: {total_users} (1 admin + {admin_referrals} referrals)")
        print(f"   Admin referrals: {admin_referrals}")
        print(f"   Approved deposits: {total_deposits}")
        
        return True

if __name__ == "__main__":
    try:
        success = delete_old_users_create_admin_referrals()
        if success:
            print("\n✅ Script completed successfully!")
        else:
            print("\n❌ Script failed!")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
