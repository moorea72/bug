"""
Simple Referral System - No Multi-Level Commissions
Only "Refer 2 Friends" Bonus System

Features:
- Track users who refer 2 friends with 100+ USDT deposits each
- One-time 20 USDT bonus when achieving 2 referrals
- No withdrawal fees for life for users with 2+ referrals  
- 2% commission on every stake for users with 2+ referrals

No more multi-level commission structure (5%, 3%, 2%)
"""

from app import db, app
from models import User, Deposit, ActivityLog
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleReferralSystem:
    """Simple referral system focused only on 'refer 2 friends' bonus"""
    
    # Minimum deposit amount to count as active referral
    MIN_DEPOSIT_AMOUNT = 100.0
    
    # One-time bonus for completing 2 referrals
    TWO_REFERRAL_BONUS = 20.0
    
    # Stake commission for users with 2+ referrals
    STAKE_COMMISSION_RATE = 0.02  # 2%
    
    @staticmethod
    def is_eligible_referral(user_id):
        """
        Check if a user is eligible to be counted as an active referral
        Must have deposited 100+ USDT total
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return False
            
            # Get total approved deposits
            total_deposits = db.session.query(db.func.sum(Deposit.amount)).filter_by(
                user_id=user_id,
                status='approved'
            ).scalar() or 0
            
            logger.info(f"User {user.username} total deposits: ${total_deposits}")
            return total_deposits >= SimpleReferralSystem.MIN_DEPOSIT_AMOUNT
            
        except Exception as e:
            logger.error(f"Error checking referral eligibility: {e}")
            return False
    
    @staticmethod
    def get_active_referrals_count(user_id):
        """
        Get count of active referrals for a user (referrals with 100+ USDT deposits)
        """
        try:
            referrals = User.query.filter_by(referred_by=user_id).all()
            active_count = 0
            
            for referral in referrals:
                if SimpleReferralSystem.is_eligible_referral(referral.id):
                    active_count += 1
            
            return active_count
            
        except Exception as e:
            logger.error(f"Error getting active referrals count: {e}")
            return 0
    
    @staticmethod
    def check_and_award_two_referral_bonus(user_id):
        """
        Check if user has completed 2 referrals and award 20 USDT bonus if eligible
        This should be called when a deposit is approved
        """
        try:
            user = User.query.get(user_id)
            if not user or not user.referred_by:
                return {'success': False, 'reason': 'No referrer'}
            
            # Check if this user now makes their referrer eligible for bonus
            referrer = User.query.get(user.referred_by)
            if not referrer:
                return {'success': False, 'reason': 'Referrer not found'}
            
            # Check if referrer already claimed the bonus
            if referrer.two_referral_bonus_claimed:
                return {'success': False, 'reason': 'Bonus already claimed'}
            
            # Count active referrals
            active_referrals = SimpleReferralSystem.get_active_referrals_count(referrer.id)
            
            if active_referrals >= 2:
                # Award the 20 USDT bonus
                referrer.usdt_balance += SimpleReferralSystem.TWO_REFERRAL_BONUS
                referrer.two_referral_bonus_claimed = True
                
                # Log the bonus
                activity = ActivityLog(
                    user_id=referrer.id,
                    action='two_referral_bonus',
                    description=f'Two referral bonus: ${SimpleReferralSystem.TWO_REFERRAL_BONUS:.2f} - Premium benefits unlocked!'
                )
                db.session.add(activity)
                db.session.commit()
                
                logger.info(f"Two referral bonus awarded to {referrer.username}: ${SimpleReferralSystem.TWO_REFERRAL_BONUS}")
                
                return {
                    'success': True,
                    'referrer': referrer.username,
                    'bonus_amount': SimpleReferralSystem.TWO_REFERRAL_BONUS,
                    'active_referrals': active_referrals
                }
            
            return {'success': False, 'reason': f'Only {active_referrals} active referrals (need 2)'}
            
        except Exception as e:
            logger.error(f"Error checking two referral bonus: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def calculate_stake_commission(user_id, stake_amount):
        """
        Calculate 2% commission on stakes for users with 2+ referrals
        Returns the commission amount to be added to user balance
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return 0
            
            # Check if user has 2+ referrals
            if user.has_two_referrals():
                commission = stake_amount * SimpleReferralSystem.STAKE_COMMISSION_RATE
                logger.info(f"Stake commission for {user.username}: ${commission:.2f} on ${stake_amount} stake")
                return commission
            
            return 0
            
        except Exception as e:
            logger.error(f"Error calculating stake commission: {e}")
            return 0
    
    @staticmethod
    def is_withdrawal_fee_exempt(user_id):
        """
        Check if user is exempt from withdrawal fees (has 2+ referrals)
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return False
            
            return user.has_two_referrals()
            
        except Exception as e:
            logger.error(f"Error checking withdrawal fee exemption: {e}")
            return False
    
    @staticmethod
    def get_user_referral_status(user_id):
        """
        Get complete referral status for a user
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return None
            
            active_referrals = SimpleReferralSystem.get_active_referrals_count(user_id)
            has_premium = user.has_two_referrals()
            
            return {
                'user_id': user_id,
                'username': user.username,
                'referral_code': user.referral_code,
                'active_referrals': active_referrals,
                'has_premium_benefits': has_premium,
                'bonus_claimed': user.two_referral_bonus_claimed,
                'withdrawal_fee_exempt': has_premium,
                'stake_commission_eligible': has_premium
            }
            
        except Exception as e:
            logger.error(f"Error getting referral status: {e}")
            return None

# Convenience functions for integration
def process_deposit_referral_check(user_id, deposit_amount):
    """Process referral check when deposit is approved"""
    if deposit_amount >= SimpleReferralSystem.MIN_DEPOSIT_AMOUNT:
        return SimpleReferralSystem.check_and_award_two_referral_bonus(user_id)
    return {'success': False, 'reason': 'Deposit below minimum amount'}

def get_user_referral_benefits(user_id):
    """Get user's referral benefits status"""
    return SimpleReferralSystem.get_user_referral_status(user_id)

def calculate_user_stake_bonus(user_id, stake_amount):
    """Calculate stake commission for user"""
    return SimpleReferralSystem.calculate_stake_commission(user_id, stake_amount)

def is_user_withdrawal_fee_exempt(user_id):
    """Check if user is exempt from withdrawal fees"""
    return SimpleReferralSystem.is_withdrawal_fee_exempt(user_id)

# Example usage:
if __name__ == "__main__":
    with app.app_context():
        print("Testing Simple Referral System...")
        
        # Example: Check referral status for user
        # status = get_user_referral_benefits(user_id=1)
        # print(f"Referral status: {status}")
        
        # Example: Process deposit and check for bonus
        # result = process_deposit_referral_check(user_id=5, deposit_amount=150)
        # print(f"Bonus result: {result}")