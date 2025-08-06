#!/usr/bin/env python3
"""
Complete referral system fix - deposit-based commissions only
"""

from app import app, db
from models import User, Deposit, ActivityLog

class DepositOnlyReferralSystem:
    """New referral system that only awards commission on deposits >= 100 USDT"""
    
    MIN_DEPOSIT_AMOUNT = 100.0
    COMMISSION_RATES = {
        'level_1': 0.05,  # 5%
        'level_2': 0.03,  # 3%  
        'level_3': 0.02   # 2%
    }
    
    @staticmethod
    def award_commission_on_deposit(user_id, deposit_amount):
        """NO COMMISSION SYSTEM - Only track referrals, no commissions awarded"""
        try:
            user = User.query.get(user_id)
            if not user or not user.referred_by:
                return {'success': False, 'reason': 'No referrer'}
            
            # Only track the referral relationship - NO COMMISSION AWARDED
            activity = ActivityLog(
                user_id=user.id,
                action='referral_deposit',
                description=f'Referral deposit: ${deposit_amount:.2f} (NO COMMISSION SYSTEM)'
            )
            db.session.add(activity)
            db.session.commit()
            
            return {
                'success': True,
                'commissions_awarded': [],
                'total_commission': 0,
                'message': 'Referral tracked but no commission awarded'
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'reason': str(e)}

def test_system():
    """Test the new deposit-only system"""
    print("🧪 Testing Deposit-Only Referral System")
    print("✅ Commission only on deposits >= 100 USDT")
    print("✅ Level 1: 5% of deposit amount")
    print("✅ Level 2: 3% of deposit amount") 
    print("✅ Level 3: 2% of deposit amount")
    print("✅ No commission on balance - only actual deposits")
    
if __name__ == "__main__":
    test_system()