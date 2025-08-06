#!/usr/bin/env python3
"""
Fix referral bonus for admin user
"""
from app import app, db
from models import User, Deposit, ActivityLog

def fix_referral_bonus():
    """Fix referral bonus for admin user"""
    with app.app_context():
        print("Fixing referral bonus...")
        
        # Get admin user
        admin = User.query.filter_by(is_admin=True).first()
        if not admin:
            print("Admin user not found!")
            return
        
        # Get all users referred by admin
        referred_users = User.query.filter_by(referred_by=admin.id).all()
        print(f"Found {len(referred_users)} users referred by admin")
        
        # Calculate commission for each referral
        total_commission = 0
        for user in referred_users:
            # Check if user has deposits
            deposits = Deposit.query.filter_by(user_id=user.id).all()
            for deposit in deposits:
                if deposit.amount >= 100:
                    # Award 5% commission
                    commission = deposit.amount * 0.05
                    total_commission += commission
                    print(f"Commission for {user.username}: ${commission:.2f}")
                    break  # Only first deposit
        
        # Update admin referral bonus
        admin.referral_bonus = total_commission
        db.session.commit()
        
        print(f"Total commission awarded: ${total_commission:.2f}")
        print(f"Admin referral bonus updated to: ${admin.referral_bonus:.2f}")

if __name__ == "__main__":
    fix_referral_bonus()