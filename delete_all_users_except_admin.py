#!/usr/bin/env python3
"""
Delete all users except admin as requested
"""

from app import app, db
from models import User, Deposit, ActivityLog, Stake, Withdrawal

def delete_all_users_except_admin():
    """Delete all users except admin"""
    print("🗑️ Deleting all users except admin...")
    
    with app.app_context():
        # Find admin user
        admin = User.query.filter_by(is_admin=True).first()
        if not admin:
            print("❌ Admin user not found!")
            return False
        
        print(f"✅ Admin found: {admin.username} (ID: {admin.id})")
        
        # Get all non-admin users
        users_to_delete = User.query.filter(User.id != admin.id).all()
        print(f"Found {len(users_to_delete)} users to delete")
        
        # Delete related records first
        for user in users_to_delete:
            print(f"Deleting records for user: {user.username}")
            
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
        admin.current_referral_count = 0
        
        db.session.commit()
        
        print(f"✅ All users deleted except admin")
        print(f"✅ Admin referral stats reset")
        
        return True

if __name__ == "__main__":
    delete_all_users_except_admin()