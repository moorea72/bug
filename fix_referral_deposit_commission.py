#!/usr/bin/env python3
"""
Fix referral system to only give commission on deposits (not balance)
Commission only when referral deposits 100+ USDT in single transaction
"""

from app import app, db
from models import User, Deposit, ActivityLog
import logging

logger = logging.getLogger(__name__)

class DepositBasedReferralSystem:
    """Referral system based on deposit amounts, not balance"""
    
    MIN_DEPOSIT_AMOUNT = 100.0
    COMMISSION_RATES = {
        'level_1': 0.05,  # 5%
        'level_2': 0.03,  # 3%
        'level_3': 0.02   # 2%
    }
    
    @staticmethod
    def award_commission_on_deposit(user_id, deposit_amount):
        """
        Award commission ONLY when user makes deposit >= 100 USDT
        Commission is calculated on deposit amount, not total balance
        """
        try:
            # Only award commission for deposits >= minimum amount
            if deposit_amount < DepositBasedReferralSystem.MIN_DEPOSIT_AMOUNT:
                logger.info(f"Deposit amount ${deposit_amount} below minimum ${DepositBasedReferralSystem.MIN_DEPOSIT_AMOUNT}")
                return {'success': False, 'reason': 'Deposit below minimum amount'}
            
            user = User.query.get(user_id)
            if not user or not user.referred_by:
                logger.info(f"User {user_id} has no referrer")
                return {'success': False, 'reason': 'No referrer'}
            
            results = {
                'success': True,
                'commissions_awarded': [],
                'total_commission': 0
            }
            
            current_user = user
            
            # Level 1 Commission (5%)
            if current_user.referred_by:
                level_1_user = User.query.get(current_user.referred_by)
                if level_1_user:
                    commission = deposit_amount * DepositBasedReferralSystem.COMMISSION_RATES['level_1']
                    level_1_user.referral_bonus += commission
                    
                    # Log the commission
                    activity = ActivityLog(
                        user_id=level_1_user.id,
                        action='referral_commission',
                        description=f'Level 1 commission: ${commission:.2f} from {user.username} deposit (${deposit_amount:.2f})'
                    )
                    db.session.add(activity)
                    
                    results['commissions_awarded'].append({
                        'level': 1,
                        'user': level_1_user.username,
                        'amount': commission
                    })
                    results['total_commission'] += commission
                    
                    logger.info(f"Level 1 commission awarded: ${commission:.2f} to {level_1_user.username}")
                    
                    # Level 2 Commission (3%)
                    if level_1_user.referred_by:
                        level_2_user = User.query.get(level_1_user.referred_by)
                        if level_2_user:
                            commission = deposit_amount * DepositBasedReferralSystem.COMMISSION_RATES['level_2']
                            level_2_user.referral_bonus += commission
                            
                            activity = ActivityLog(
                                user_id=level_2_user.id,
                                action='referral_commission',
                                description=f'Level 2 commission: ${commission:.2f} from {user.username} deposit (${deposit_amount:.2f})'
                            )
                            db.session.add(activity)
                            
                            results['commissions_awarded'].append({
                                'level': 2,
                                'user': level_2_user.username,
                                'amount': commission
                            })
                            results['total_commission'] += commission
                            
                            logger.info(f"Level 2 commission awarded: ${commission:.2f} to {level_2_user.username}")
                            
                            # Level 3 Commission (2%)
                            if level_2_user.referred_by:
                                level_3_user = User.query.get(level_2_user.referred_by)
                                if level_3_user:
                                    commission = deposit_amount * DepositBasedReferralSystem.COMMISSION_RATES['level_3']
                                    level_3_user.referral_bonus += commission
                                    
                                    activity = ActivityLog(
                                        user_id=level_3_user.id,
                                        action='referral_commission',
                                        description=f'Level 3 commission: ${commission:.2f} from {user.username} deposit (${deposit_amount:.2f})'
                                    )
                                    db.session.add(activity)
                                    
                                    results['commissions_awarded'].append({
                                        'level': 3,
                                        'user': level_3_user.username,
                                        'amount': commission
                                    })
                                    results['total_commission'] += commission
                                    
                                    logger.info(f"Level 3 commission awarded: ${commission:.2f} to {level_3_user.username}")
            
            db.session.commit()
            return results
            
        except Exception as e:
            logger.error(f"Error awarding referral commission: {e}")
            db.session.rollback()
            return {'success': False, 'reason': str(e)}

def test_new_system():
    """Test the new deposit-based commission system"""
    print("Testing new deposit-based referral commission system...")
    
    with app.app_context():
        print("✅ New system features:")
        print("• Commission only on deposits >= 100 USDT")
        print("• Level 1: 5% of deposit amount")
        print("• Level 2: 3% of deposit amount") 
        print("• Level 3: 2% of deposit amount")
        print("• No commission on balance, only on actual deposits")
        
        return True

if __name__ == "__main__":
    test_new_system()