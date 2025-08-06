"""
Enhanced Deposit System - NO COMMISSION VERSION
Only tracks referral relationships, no monetary rewards
"""

from app import db
from models import User, Deposit, ActivityLog

def process_deposit_with_referral_check(user, amount, transaction_id):
    """
    Process deposit - NO REFERRAL COMMISSION SYSTEM
    """
    try:
        # Add amount to user balance
        user.usdt_balance += amount

        # Log referral relationship but NO COMMISSION
        if user.referred_by:
            log_activity(user.referred_by, 'referral_deposit_tracked_no_commission', 
                       f'Referral deposit tracked: {user.username} deposited ${amount} - NO COMMISSION SYSTEM')

        return True

    except Exception as e:
        print(f"Error processing deposit: {e}")
        return False

def calculate_referral_commission(user_id, deposit_amount):
    """
    DISABLED - No commission calculation
    """
    return {
        'success': False,
        'message': 'Referral commission system disabled',
        'commission_awarded': 0
    }

def process_deposit_bonus(user_id, deposit_amount):
    """
    DISABLED - No bonus processing
    """
    return {
        'success': False,
        'message': 'Referral bonus system disabled',
        'bonus_awarded': 0
    }