#!/usr/bin/env python3
"""
Manual referral commission fix
"""
from app import app, db
from models import User, Deposit, ActivityLog

def manual_referral_fix():
    """Manually fix referral commission"""
    with app.app_context():
        try:
            print("Manually fixing referral commission...")
            
            # Get admin user
            admin = User.query.filter_by(is_admin=True).first()
            print(f"Admin found: {admin.username if admin else 'None'}")
            
            if not admin:
                return
            
            # Get all non-admin users (referrals)
            referrals = User.query.filter_by(is_admin=False).all()
            print(f"Found {len(referrals)} referral users")
            
            # Calculate total commission (5% of all deposits)
            total_commission = 0
            for user in referrals:
                deposits = Deposit.query.filter_by(user_id=user.id).all()
                for deposit in deposits:
                    if deposit.amount >= 100:
                        commission = deposit.amount * 0.05  # 5% commission
                        total_commission += commission
                        print(f"Commission for {user.username}: ${commission:.2f}")
                        break  # Only first deposit
            
            # Update admin referral bonus directly
            admin.referral_bonus = total_commission
            db.session.commit()
            
            print(f"Total commission set: ${total_commission:.2f}")
            print(f"Admin referral bonus updated to: ${admin.referral_bonus:.2f}")
            
        except Exception as e:
            print(f"Error: {e}")
            db.session.rollback()

if __name__ == "__main__":
    manual_referral_fix()