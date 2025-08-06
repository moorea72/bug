"""
Referral Utilities - COMPLETELY DISABLED COMMISSION SYSTEM
Only tracks referral relationships without any monetary rewards
"""
from datetime import datetime
from app import db

def award_referral_commission(user, deposit_amount):
    """COMPLETELY DISABLED - No referral commission awarded"""
    print(f"⛔ REFERRAL COMMISSION DISABLED: {user.username} deposit ${deposit_amount} - NO COMMISSION")
    return

def check_and_update_referral_balance(user):
    """DISABLED - No referral balance updates"""
    print(f"Referral commission system disabled for {user.username}")
    pass

def remove_referral_commission(user):
    """DISABLED - No commission to remove"""
    pass

def recalculate_all_referral_commissions():
    """DISABLED - No commission recalculation"""
    from models import User, ActivityLog

    try:
        # Reset all referral bonuses to 0
        User.query.update({User.referral_bonus: 0.0})

        # Delete all referral commission logs
        ActivityLog.query.filter_by(action='referral_commission').delete()
        ActivityLog.query.filter_by(action='referral_bonus').delete()

        db.session.commit()
        print("All referral bonuses reset to 0 - Commission system disabled")

    except Exception as e:
        db.session.rollback()
        print(f"Error resetting referral system: {e}")