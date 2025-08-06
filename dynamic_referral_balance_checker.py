#!/usr/bin/env python3
"""
Dynamic Referral Balance Checker System
- Referrals only count when user has 100+ USDT balance
- Commission awarded only ONCE per referral (permanent)
- Referral count dynamically changes based on current balance
- If balance drops below 100, removed from referral count (but commission stays)
- If balance goes back above 100, added back to referral count (no new commission)
"""

import os
import sys
from datetime import datetime
from sqlalchemy import func

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, Deposit, ActivityLog

class DynamicReferralChecker:
    
    @staticmethod
    def get_user_total_balance(user):
        """Get user's total balance including wallet + active stakes"""
        wallet_balance = user.usdt_balance or 0.0
        
        # Get active stakes total
        from models import Stake
        active_stakes = db.session.query(func.sum(Stake.amount)).filter(
            Stake.user_id == user.id,
            Stake.status == 'active'
        ).scalar() or 0.0
        
        return wallet_balance + active_stakes
    
    @staticmethod
    def check_referral_eligibility(user):
        """Check if user is eligible for referral count (100+ USDT balance)"""
        total_balance = DynamicReferralChecker.get_user_total_balance(user)
        return total_balance >= 100.0
    
    @staticmethod
    def has_commission_been_awarded(referrer_id, referred_user_id):
        """Check if commission has already been awarded for this referral"""
        commission_log = ActivityLog.query.filter(
            ActivityLog.user_id == referrer_id,
            ActivityLog.action == 'referral_commission_permanent',
            ActivityLog.description.contains(f'user_id:{referred_user_id}')
        ).first()
        
        return commission_log is not None
    
    @staticmethod
    def award_one_time_commission(referrer, referred_user):
        """Award commission only once per referral (permanent)"""
        # Check if commission already awarded
        if DynamicReferralChecker.has_commission_been_awarded(referrer.id, referred_user.id):
            return False, "Commission already awarded"
        
        # Award 5 USDT commission (permanent)
        commission_amount = 5.0
        referrer.referral_bonus += commission_amount
        referrer.usdt_balance += commission_amount
        
        # Log permanent commission
        commission_log = ActivityLog(
            user_id=referrer.id,
            action='referral_commission_permanent',
            description=f'PERMANENT commission ${commission_amount} from {referred_user.username} (user_id:{referred_user.id}) - NEVER REMOVED'
        )
        db.session.add(commission_log)
        
        return True, f"Commission ${commission_amount} awarded permanently"
    
    @staticmethod
    def update_all_referral_counts():
        """Update referral counts for all users based on current balances"""
        with app.app_context():
            print("🔄 Updating all referral counts based on current balances...")
            
            # Get all users who have been referred
            referred_users = User.query.filter(User.referred_by.isnot(None)).all()
            
            # Reset all referral counts (but keep bonuses)
            all_users = User.query.all()
            for user in all_users:
                user.current_referral_count = 0
            
            stats = {
                'total_referred_users': len(referred_users),
                'eligible_referrals': 0,
                'ineligible_referrals': 0,
                'new_commissions': 0,
                'total_commission_awarded': 0.0
            }
            
            # Check each referred user's current balance
            for referred_user in referred_users:
                referrer = User.query.get(referred_user.referred_by)
                if not referrer:
                    continue
                
                total_balance = DynamicReferralChecker.get_user_total_balance(referred_user)
                is_eligible = total_balance >= 100.0
                
                if is_eligible:
                    # Add to referral count
                    referrer.current_referral_count = (referrer.current_referral_count or 0) + 1
                    stats['eligible_referrals'] += 1
                    
                    # Check if commission should be awarded (first time only)
                    commissioned, message = DynamicReferralChecker.award_one_time_commission(referrer, referred_user)
                    if commissioned:
                        stats['new_commissions'] += 1
                        stats['total_commission_awarded'] += 5.0
                    
                    print(f"   ✅ {referred_user.username} (${total_balance:.2f}) -> {referrer.username} | {message}")
                else:
                    # Not eligible for referral count
                    stats['ineligible_referrals'] += 1
                    print(f"   ❌ {referred_user.username} (${total_balance:.2f}) -> {referrer.username} | Below 100 USDT")
            
            # Commit all changes
            db.session.commit()
            
            print(f"\n📊 Dynamic Referral Update Summary:")
            print(f"   Total referred users: {stats['total_referred_users']}")
            print(f"   ✅ Eligible referrals (100+ USDT): {stats['eligible_referrals']}")
            print(f"   ❌ Ineligible referrals (<100 USDT): {stats['ineligible_referrals']}")
            print(f"   💰 New commissions awarded: {stats['new_commissions']}")
            print(f"   💵 Total commission amount: ${stats['total_commission_awarded']:.2f}")
            
            # Show updated referrer statistics
            print(f"\n👥 Updated Referrer Statistics:")
            referrers = User.query.filter(User.current_referral_count > 0).all()
            for referrer in referrers:
                print(f"   {referrer.username}: {referrer.current_referral_count} active referrals, ${referrer.referral_bonus:.2f} total commission")
            
            return stats

    @staticmethod
    def check_single_user_referral_status(user_id):
        """Check referral status for a single user (for real-time updates)"""
        user = User.query.get(user_id)
        if not user or not user.referred_by:
            return None
        
        referrer = User.query.get(user.referred_by)
        if not referrer:
            return None
        
        total_balance = DynamicReferralChecker.get_user_total_balance(user)
        is_eligible = total_balance >= 100.0
        has_commission = DynamicReferralChecker.has_commission_been_awarded(referrer.id, user.id)
        
        return {
            'user': user.username,
            'referrer': referrer.username,
            'total_balance': total_balance,
            'is_eligible': is_eligible,
            'has_commission': has_commission,
            'commission_due': is_eligible and not has_commission
        }

def main():
    """Run dynamic referral balance checker"""
    try:
        stats = DynamicReferralChecker.update_all_referral_counts()
        
        print("\n🎉 Dynamic referral system updated successfully!")
        print("📋 System Rules:")
        print("   • Referrals count only when user has 100+ USDT balance")
        print("   • Commission awarded only ONCE per referral (permanent)")
        print("   • Referral count changes dynamically based on current balance")
        print("   • Commission never removed, even if balance drops below 100")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)