#!/usr/bin/env python3
"""
Fix referral system to only count referrals after 100+ USDT deposit
- Referrals only count when referred user deposits 100+ USDT
- Commission only awarded after 100+ USDT deposit
- Existing referrals updated based on current deposit amounts
"""

import os
import sys
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, Deposit

def fix_referral_100_usdt_requirement():
    """Update referral system to require 100+ USDT deposit"""
    
    with app.app_context():
        print("🔧 Fixing referral system to require 100+ USDT deposit...")
        
        # Get all users who have been referred by someone
        referred_users = User.query.filter(User.referred_by.isnot(None)).all()
        
        print(f"📊 Found {len(referred_users)} referred users to check...")
        
        # Reset all referral bonuses to 0 first
        all_users = User.query.all()
        for user in all_users:
            user.referral_bonus = 0.0
        
        # Track changes
        valid_referrals = 0
        invalid_referrals = 0
        commission_awarded = 0.0
        
        for referred_user in referred_users:
            # Check if this user has deposited 100+ USDT
            total_deposits = db.session.query(db.func.sum(Deposit.amount)).filter(
                Deposit.user_id == referred_user.id,
                Deposit.status == 'approved'
            ).scalar() or 0.0
            
            # Also check current balance
            current_balance = referred_user.usdt_balance or 0.0
            total_value = total_deposits  # Use only actual deposits for referral qualification
            
            referrer = User.query.get(referred_user.referred_by)
            if referrer:
                if total_value >= 100.0:
                    # Valid referral - award commission
                    referrer.referral_bonus += 5.0  # 5 USDT per valid referral
                    valid_referrals += 1
                    commission_awarded += 5.0
                    print(f"   ✅ Valid referral: {referred_user.username} (${total_value:.2f}) -> {referrer.username}")
                else:
                    # Invalid referral - not enough deposit
                    invalid_referrals += 1
                    print(f"   ❌ Invalid referral: {referred_user.username} (${total_value:.2f}) -> {referrer.username}")
        
        # Update user balances with new referral bonuses
        for user in all_users:
            if user.referral_bonus > 0:
                # Add referral bonus to actual balance
                user.usdt_balance = (user.usdt_balance or 0.0) + user.referral_bonus
        
        # Commit all changes
        db.session.commit()
        
        print(f"\n📊 Referral System Update Summary:")
        print(f"   ✅ Valid referrals (100+ USDT): {valid_referrals}")
        print(f"   ❌ Invalid referrals (<100 USDT): {invalid_referrals}")
        print(f"   💰 Total commission awarded: ${commission_awarded:.2f}")
        
        # Show updated referrer statistics
        print(f"\n👥 Updated Referrer Statistics:")
        referrers = User.query.filter(User.referral_bonus > 0).all()
        for referrer in referrers:
            valid_refs = User.query.join(Deposit, User.id == Deposit.user_id).filter(
                User.referred_by == referrer.id,
                Deposit.status == 'approved'
            ).group_by(User.id).having(db.func.sum(Deposit.amount) >= 100).count()
            
            print(f"   {referrer.username}: {valid_refs} valid referrals, ${referrer.referral_bonus:.2f} bonus")
        
        return True

if __name__ == "__main__":
    try:
        success = fix_referral_100_usdt_requirement()
        if success:
            print("\n🎉 Referral system updated successfully!")
            print("💡 Now only referrals with 100+ USDT deposits count and receive commission.")
        else:
            print("\n❌ Referral system update failed!")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()