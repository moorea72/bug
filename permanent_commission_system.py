#!/usr/bin/env python3
"""
Permanent Commission System Implementation
- Commission awarded only ONCE per referral when they first reach 100+ USDT
- Commission remains permanent even if balance drops below 100 USDT
- Only referral count is affected by balance changes (for salary calculation)
- NO commission removal ever
"""

from app import app, db
from models import User, Deposit, ActivityLog, PlatformSettings
from datetime import datetime

class PermanentCommissionSystem:
    """
    Permanent Commission System
    Commission is awarded only once per referral and remains permanent
    """
    
    @staticmethod
    def award_first_time_commission(user, deposit_amount):
        """
        Award commission only if:
        1. User has 100+ USDT balance
        2. Commission has NOT been awarded before for this referral
        """
        if not user.referred_by or deposit_amount < 100:
            return False
        
        try:
            # Check if commission has already been awarded
            existing_commission = ActivityLog.query.filter_by(
                action='referral_commission'
            ).filter(ActivityLog.description.contains(f'from {user.username}')).first()
            
            if existing_commission:
                print(f"Commission already awarded for {user.username} - skipping")
                return False
            
            # Check if user's total balance is >= 100 USDT
            total_balance = user.get_total_balance_including_stakes()
            if total_balance < 100:
                print(f"User {user.username} balance ${total_balance:.2f} < $100 - not eligible")
                return False
            
            # Get referrer
            referrer = User.query.get(user.referred_by)
            if not referrer:
                return False
            
            # Get commission settings
            settings = PlatformSettings.get_all_settings()
            level_1_rate = float(settings.get('referral_level_1', 5)) / 100
            
            # Award Level 1 Commission (PERMANENT)
            commission = deposit_amount * level_1_rate
            referrer.referral_bonus += commission
            
            # Log activity with PERMANENT marker
            activity = ActivityLog(
                user_id=referrer.id,
                action='referral_commission',
                description=f'PERMANENT Commission: ${commission:.2f} from {user.username} (Balance: ${total_balance:.2f}) - NEVER REMOVED',
                timestamp=datetime.utcnow()
            )
            db.session.add(activity)
            
            print(f"✅ PERMANENT commission awarded: ${commission:.2f} to {referrer.username} from {user.username}")
            return True
            
        except Exception as e:
            print(f"Error awarding commission: {e}")
            return False
    
    @staticmethod
    def get_active_referrals_count(user_id):
        """
        Get count of referrals with current balance >= 100 USDT
        This affects salary calculation but NOT commission
        """
        try:
            active_count = 0
            referrals = User.query.filter_by(referred_by=user_id).all()
            
            for referral in referrals:
                total_balance = referral.get_total_balance_including_stakes()
                if total_balance >= 100:
                    active_count += 1
            
            return active_count
            
        except Exception as e:
            print(f"Error counting active referrals: {e}")
            return 0
    
    @staticmethod
    def check_and_award_commission(user):
        """
        Check if user qualifies for commission and award if eligible
        This is called when balance changes
        """
        if not user.referred_by:
            return
        
        total_balance = user.get_total_balance_including_stakes()
        
        # Only award if balance >= 100 and not already awarded
        if total_balance >= 100:
            # Get user's largest approved deposit
            largest_deposit = Deposit.query.filter_by(
                user_id=user.id, 
                status='approved'
            ).order_by(Deposit.amount.desc()).first()
            
            if largest_deposit and largest_deposit.amount >= 100:
                PermanentCommissionSystem.award_first_time_commission(user, largest_deposit.amount)
    
    @staticmethod
    def get_commission_stats(user_id):
        """Get commission statistics for a user"""
        try:
            user = User.query.get(user_id)
            if not user:
                return None
            
            # Count all referrals
            total_referrals = User.query.filter_by(referred_by=user_id).count()
            
            # Count active referrals (balance >= 100)
            active_referrals = PermanentCommissionSystem.get_active_referrals_count(user_id)
            
            # Count referrals with permanent commission
            commission_logs = ActivityLog.query.filter_by(
                user_id=user_id,
                action='referral_commission'
            ).all()
            
            commissioned_referrals = len(commission_logs)
            
            return {
                'total_referrals': total_referrals,
                'active_referrals': active_referrals,
                'commissioned_referrals': commissioned_referrals,
                'total_commission': user.referral_bonus,
                'commission_logs': commission_logs
            }
            
        except Exception as e:
            print(f"Error getting commission stats: {e}")
            return None

# Integration functions for existing system
def award_referral_commission(user, deposit_amount):
    """Integration function - calls permanent commission system"""
    return PermanentCommissionSystem.award_first_time_commission(user, deposit_amount)

def check_and_update_referral_balance(user):
    """Integration function - checks and awards commission if eligible"""
    PermanentCommissionSystem.check_and_award_commission(user)

def get_active_referrals_count(user_id):
    """Integration function - gets active referrals count"""
    return PermanentCommissionSystem.get_active_referrals_count(user_id)

def remove_referral_commission(user):
    """This function does NOTHING - commission is permanent"""
    print(f"⚠️  Commission removal attempted for {user.username} - IGNORED (Commission is permanent)")
    pass

if __name__ == "__main__":
    print("Permanent Commission System loaded successfully!")
    print("Features:")
    print("- Commission awarded only ONCE per referral")
    print("- Commission remains PERMANENT even if balance drops")
    print("- Only referral count is affected by balance changes")
    print("- NO commission removal EVER")