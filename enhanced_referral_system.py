"""
Enhanced Referral System with 100 USDT Minimum Deposit Requirement
Only referrals with 100+ USDT balance count for commission
"""

from app import db, app
from models import User, Deposit, ActivityLog, PlatformSettings
from sqlalchemy import func

def get_active_referrals_count(user_id):
    """
    Get count of active referrals who have balance >= 100 USDT
    This includes both wallet balance and active stakes
    """
    try:
        active_referrals = 0
        referrals = User.query.filter_by(referred_by=user_id).all()
        
        for referral in referrals:
            # Calculate total balance (wallet + active stakes)
            total_balance = referral.get_total_balance_including_stakes()
            
            if total_balance >= 100:
                active_referrals += 1
        
        return active_referrals
    except Exception as e:
        print(f"Error calculating active referrals: {e}")
        return 0

def calculate_referral_commission(user, deposit_amount):
    """
    Calculate and award referral commission only if:
    1. User makes a deposit of at least 100 USDT 
    2. Commission awarded only ONCE per referral (first time depositing 100+ USDT)
    3. User is only added to referrer's count after 100+ USDT deposit
    """
    if not user.referred_by or deposit_amount < 100:
        return False
    
    try:
        # Get referrer
        referrer = User.query.get(user.referred_by)
        if not referrer:
            return False
        
        # Check if this deposit is >= 100 USDT (minimum requirement)
        if deposit_amount >= 100:
            # Check if commission has already been awarded for this referral
            existing_commission = ActivityLog.query.filter_by(
                user_id=referrer.id,
                action='referral_commission'
            ).filter(ActivityLog.description.like(f'%{user.username}%')).first()
            
            if existing_commission:
                # Commission already awarded, don't award again
                return False
            
            # Get commission settings
            settings = PlatformSettings.get_all_settings()
            level_1_rate = float(settings.get('referral_level_1', 5)) / 100
            level_2_rate = float(settings.get('referral_level_2', 3)) / 100
            level_3_rate = float(settings.get('referral_level_3', 2)) / 100
            
            # Award Level 1 Commission (ONE TIME ONLY)
            commission = deposit_amount * level_1_rate
            referrer.referral_bonus += commission
            
            # Log activity
            activity = ActivityLog(
                user_id=referrer.id,
                action='referral_commission',
                description=f'Level 1 commission (ONE TIME): ${commission:.2f} from {user.username} (Balance: ${total_balance:.2f})'
            )
            db.session.add(activity)
            
            # Award Level 2 Commission
            if referrer.referred_by:
                level_2_user = User.query.get(referrer.referred_by)
                if level_2_user:
                    commission = deposit_amount * level_2_rate
                    level_2_user.referral_bonus += commission
                    
                    activity = ActivityLog(
                        user_id=level_2_user.id,
                        action='referral_commission',
                        description=f'Level 2 commission: ${commission:.2f} from {user.username}'
                    )
                    db.session.add(activity)
                    
                    # Award Level 3 Commission
                    if level_2_user.referred_by:
                        level_3_user = User.query.get(level_2_user.referred_by)
                        if level_3_user:
                            commission = deposit_amount * level_3_rate
                            level_3_user.referral_bonus += commission
                            
                            activity = ActivityLog(
                                user_id=level_3_user.id,
                                action='referral_commission',
                                description=f'Level 3 commission: ${commission:.2f} from {user.username}'
                            )
                            db.session.add(activity)
        
        return True
        
    except Exception as e:
        print(f"Error calculating referral commission: {e}")
        return False

def recalculate_all_referral_commissions():
    """
    Recalculate all referral commissions based on current user balances
    Remove commissions for users with balance < 100 USDT
    """
    try:
        with app.app_context():
            # Reset all referral bonuses
            User.query.update({User.referral_bonus: 0.0})
            
            # Delete all referral commission activity logs
            ActivityLog.query.filter_by(action='referral_commission').delete()
            
            # Get all users with referrals
            users_with_referrals = User.query.filter(User.referred_by.isnot(None)).all()
            
            for user in users_with_referrals:
                # Check if user has 100+ USDT balance
                total_balance = user.get_total_balance_including_stakes()
                
                if total_balance >= 100:
                    # Get user's approved deposits
                    deposits = Deposit.query.filter_by(user_id=user.id, status='approved').all()
                    
                    for deposit in deposits:
                        if deposit.amount >= 100:
                            # Award commission for this deposit
                            calculate_referral_commission(user, deposit.amount)
                            break  # Only first qualifying deposit
            
            db.session.commit()
            print("All referral commissions recalculated successfully")
            
    except Exception as e:
        db.session.rollback()
        print(f"Error recalculating referral commissions: {e}")

def check_and_update_referral_status():
    """
    Check all users and update referral commissions based on current balances
    Commission is awarded only ONCE per referral (first time reaching 100+ USDT)
    Commission is NEVER removed - only referral count is affected by balance changes
    """
    try:
        with app.app_context():
            # Get all users who have been referred
            referred_users = User.query.filter(User.referred_by.isnot(None)).all()
            
            for user in referred_users:
                total_balance = user.get_total_balance_including_stakes()
                
                # Check if user previously qualified for commission
                existing_commission = ActivityLog.query.filter_by(
                    action='referral_commission'
                ).filter(ActivityLog.description.contains(f'from {user.username}')).first()
                
                if total_balance >= 100 and not existing_commission:
                    # Award commission ONLY if not already awarded
                    deposits = Deposit.query.filter_by(user_id=user.id, status='approved').all()
                    for deposit in deposits:
                        if deposit.amount >= 100:
                            calculate_referral_commission(user, deposit.amount)
                            break
                
                # NOTE: Commission is NOT removed when balance drops below 100
                # Only referral count is affected for future calculations
            
            db.session.commit()
            
    except Exception as e:
        db.session.rollback()
        print(f"Error checking referral status: {e}")

def remove_referral_commission(user):
    """
    DO NOT REMOVE COMMISSION - Commission is permanent once awarded
    This function is kept for compatibility but does nothing
    Only referral count is affected by balance changes
    """
    # Commission is NOT removed when balance drops below 100 USDT
    # Only the referral count is affected for future calculations
    print(f"Note: Commission is permanent for {user.username}. Only referral count affected by balance changes.")
    pass

def get_referral_stats(user_id):
    """
    Get detailed referral statistics including active/inactive referrals
    """
    try:
        user = User.query.get(user_id)
        if not user:
            return None
        
        referrals = User.query.filter_by(referred_by=user_id).all()
        
        stats = {
            'total_referrals': len(referrals),
            'active_referrals': 0,
            'inactive_referrals': 0,
            'total_commission': user.referral_bonus,
            'referral_details': []
        }
        
        for referral in referrals:
            total_balance = referral.get_total_balance_including_stakes()
            is_active = total_balance >= 100
            
            if is_active:
                stats['active_referrals'] += 1
            else:
                stats['inactive_referrals'] += 1
            
            stats['referral_details'].append({
                'username': referral.username,
                'total_balance': total_balance,
                'is_active': is_active,
                'joined_date': referral.created_at.strftime('%Y-%m-%d')
            })
        
        return stats
        
    except Exception as e:
        print(f"Error getting referral stats: {e}")
        return None

if __name__ == "__main__":
    # Test the enhanced referral system
    recalculate_all_referral_commissions()