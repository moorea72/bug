#!/usr/bin/env python3
"""
Fix referral bonus NOW - direct database update
"""
import os
os.environ['DATABASE_URL'] = 'postgresql://neondb_owner:npg_4sSItw5JkLZM@ep-falling-firefly-afxbamco-pooler.c-2.us-west-2.aws.neon.tech/neondb'

from app import app, db
from models import User, Deposit

def fix_referral_now():
    """Fix referral bonus immediately"""
    with app.app_context():
        try:
            # Get admin user
            admin = User.query.filter_by(is_admin=True).first()
            if not admin:
                print("❌ Admin user not found")
                return
                
            print(f"📊 Admin before: Balance={admin.usdt_balance:.2f}, Bonus={admin.referral_bonus:.2f}")
            
            # Get all admin referrals
            admin_referrals = User.query.filter_by(referred_by=admin.id).all()
            print(f"👥 Found {len(admin_referrals)} admin referrals")
            
            # Calculate correct commission
            total_commission = 0
            for user in admin_referrals:
                deposits = Deposit.query.filter_by(user_id=user.id).all()
                for deposit in deposits:
                    if deposit.amount >= 100:
                        commission = deposit.amount * 0.05  # 5% commission
                        total_commission += commission
                        print(f"💰 {user.username}: {deposit.amount} USDT → {commission:.2f} USDT commission")
                        break  # Only first deposit
            
            # Update admin with correct amounts
            admin.referral_bonus = total_commission
            admin.usdt_balance = 10000.0 + total_commission  # Base + commission
            
            db.session.commit()
            
            print(f"✅ Admin after: Balance={admin.usdt_balance:.2f}, Bonus={admin.referral_bonus:.2f}")
            print(f"🎉 Total commission: {total_commission:.2f} USDT from {len(admin_referrals)} referrals")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()

if __name__ == "__main__":
    fix_referral_now()