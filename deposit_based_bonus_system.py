"""
Deposit-Based Fixed Bonus System
Fixed one-time bonuses based on referral deposit amounts:
- 100 USDT deposit = 7 USDT bonus
- 150 USDT deposit = 11 USDT bonus
- 250 USDT deposit = 22 USDT bonus

Completely replaces multi-level commission system.
"""

from app import db, app
from models import User, Deposit, ActivityLog
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DepositBasedBonusSystem:
    """Fixed bonus system based on referral deposit amounts"""
    
    # Bonus tiers based on deposit amounts
    BONUS_TIERS = {
        100: 7.0,   # 100 USDT deposit = 7 USDT bonus
        150: 11.0,  # 150 USDT deposit = 11 USDT bonus  
        250: 22.0   # 250 USDT deposit = 22 USDT bonus
    }
    
    @staticmethod
    def calculate_bonus_for_deposit(deposit_amount):
        """
        Calculate bonus amount based on deposit tier
        Returns the highest applicable bonus
        """
        bonus_amount = 0
        
        # Find the highest tier that the deposit qualifies for
        for tier_amount, bonus in sorted(DepositBasedBonusSystem.BONUS_TIERS.items(), reverse=True):
            if deposit_amount >= tier_amount:
                bonus_amount = bonus
                break
        
        return bonus_amount
    
    @staticmethod
    def process_referral_bonus(referrer_id, referral_user_id, deposit_amount):
        """
        Process one-time referral bonus based on deposit amount
        Only award bonus once per referral user
        """
        try:
            referrer = User.query.get(referrer_id)
            referral_user = User.query.get(referral_user_id)
            
            if not referrer or not referral_user:
                return {'success': False, 'message': 'Invalid user IDs'}
            
            # Check if bonus already awarded for this referral
            existing_bonus = ActivityLog.query.filter(
                ActivityLog.user_id == referrer_id,
                ActivityLog.action == 'referral_deposit_bonus',
                ActivityLog.description.contains(f'Referral: {referral_user.username}')
            ).first()
            
            if existing_bonus:
                logger.info(f"Bonus already awarded for referral {referral_user.username}")
                return {'success': False, 'message': 'Bonus already awarded for this referral'}
            
            # Calculate bonus based on deposit amount
            bonus_amount = DepositBasedBonusSystem.calculate_bonus_for_deposit(deposit_amount)
            
            if bonus_amount <= 0:
                logger.info(f"No bonus tier matched for deposit amount: {deposit_amount}")
                return {'success': False, 'message': 'Deposit amount does not qualify for bonus'}
            
            # Award bonus to referrer
            referrer.usdt_balance += bonus_amount
            
            # Log the bonus activity
            activity_log = ActivityLog(
                user_id=referrer_id,
                action='referral_deposit_bonus',
                description=f'Referral deposit bonus: ${bonus_amount} USDT for {referral_user.username} depositing ${deposit_amount} USDT'
            )
            db.session.add(activity_log)
            
            # Log for referral user too
            referral_activity = ActivityLog(
                user_id=referral_user_id,
                action='deposit_generated_bonus',
                description=f'Your ${deposit_amount} USDT deposit generated ${bonus_amount} USDT bonus for your referrer {referrer.username}'
            )
            db.session.add(referral_activity)
            
            db.session.commit()
            
            logger.info(f"Awarded ${bonus_amount} USDT bonus to {referrer.username} for {referral_user.username}'s ${deposit_amount} USDT deposit")
            
            return {
                'success': True, 
                'bonus_amount': bonus_amount,
                'tier_amount': deposit_amount,
                'message': f'${bonus_amount} USDT bonus awarded'
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error processing referral bonus: {e}")
            return {'success': False, 'message': f'Error: {str(e)}'}
    
    @staticmethod
    def get_referral_bonus_summary(user_id):
        """
        Get summary of all referral bonuses earned by a user
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return None
            
            # Get all referral bonus activities
            bonus_activities = ActivityLog.query.filter(
                ActivityLog.user_id == user_id,
                ActivityLog.action == 'referral_deposit_bonus'
            ).order_by(ActivityLog.created_at.desc()).all()
            
            total_bonuses = 0
            bonus_details = []
            
            for activity in bonus_activities:
                # Extract bonus amount from description
                description = activity.description
                if '$' in description and 'USDT' in description:
                    try:
                        # Extract amount between $ and space
                        bonus_str = description.split('$')[1].split(' ')[0]
                        bonus_amount = float(bonus_str)
                        total_bonuses += bonus_amount
                        
                        bonus_details.append({
                            'date': activity.created_at,
                            'amount': bonus_amount,
                            'description': description
                        })
                    except:
                        pass
            
            return {
                'total_bonuses': total_bonuses,
                'bonus_count': len(bonus_details),
                'bonus_details': bonus_details,
                'referral_count': User.query.filter_by(referred_by=user_id).count()
            }
            
        except Exception as e:
            logger.error(f"Error getting bonus summary: {e}")
            return None
    
    @staticmethod
    def get_available_bonus_tiers():
        """
        Get all available bonus tiers for display
        """
        return DepositBasedBonusSystem.BONUS_TIERS

# Main function to process deposit with new bonus system
def process_deposit_with_bonus_system(user, deposit_amount, transaction_hash):
    """
    Process deposit and apply fixed bonus system
    """
    try:
        # Create deposit record
        deposit = Deposit(
            user_id=user.id,
            amount=deposit_amount,
            transaction_id=transaction_hash,
            status='approved',
            verified_at=datetime.utcnow()
        )
        db.session.add(deposit)
        
        # Update user balance
        user.usdt_balance += deposit_amount
        
        # Check for referral bonus if user has referrer
        bonus_result = None
        if user.referred_by:
            bonus_result = DepositBasedBonusSystem.process_referral_bonus(
                user.referred_by, user.id, deposit_amount
            )
        
        # Log the deposit
        deposit_log = ActivityLog(
            user_id=user.id,
            action='deposit_approved',
            description=f'Deposit approved: ${deposit_amount} USDT (Transaction: {transaction_hash})'
        )
        db.session.add(deposit_log)
        
        db.session.commit()
        
        return {
            'success': True,
            'deposit_amount': deposit_amount,
            'bonus_result': bonus_result
        }
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error processing deposit: {e}")
        return {'success': False, 'message': str(e)}