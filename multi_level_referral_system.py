"""
Multi-Level Referral System with 100 USDT Minimum Requirement
Implements 3-level commission structure:
- Level 1: 5% commission
- Level 2: 3% commission  
- Level 3: 2% commission

Requirements:
- Only users with 100+ USDT deposits are counted as active referrals
- Commission only triggered on deposits of 100+ USDT
- One-time commission per referral (not recurring)
- Prevents farming and abuse
"""

from app import db, app
from models import User, Deposit, ActivityLog, PlatformSettings
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MultiLevelReferralSystem:
    """Enhanced referral system with strict validation and abuse prevention"""
    
    # Commission rates for each level
    COMMISSION_RATES = {
        'level_1': 0.05,  # 5%
        'level_2': 0.03,  # 3%
        'level_3': 0.02   # 2%
    }
    
    # Minimum deposit amount to trigger referral benefits
    MIN_DEPOSIT_AMOUNT = 100.0
    
    @staticmethod
    def is_eligible_referral(user_id):
        """
        Check if a user is eligible to be counted as an active referral
        Must have deposited more than 100 USDT total
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
            return total_deposits >= MultiLevelReferralSystem.MIN_DEPOSIT_AMOUNT
            
        except Exception as e:
            logger.error(f"Error checking referral eligibility: {e}")
            return False
    
    @staticmethod
    def has_commission_been_awarded(referrer_id, referee_id):
        """
        Check if commission has already been awarded for this specific referral
        Prevents duplicate commission payments
        """
        try:
            referee = User.query.get(referee_id)
            if not referee:
                return True  # Treat as already awarded to prevent errors
            
            existing_commission = ActivityLog.query.filter_by(
                user_id=referrer_id,
                action='referral_commission'
            ).filter(ActivityLog.description.contains(f'from {referee.username}')).first()
            
            return existing_commission is not None
            
        except Exception as e:
            logger.error(f"Error checking commission history: {e}")
            return True  # Err on the side of caution
    
    @staticmethod
    def award_commission(user_id, deposit_amount):
        """
        Award multi-level referral commission ONLY on deposits >= 100 USDT
        Commission calculated on deposit amount, not total balance
        
        Args:
            user_id: ID of user making the deposit
            deposit_amount: Amount of the deposit in USDT
            
        Returns:
            dict: Results of commission awards
        """
        try:
            # Only award commission for deposits >= 100 USDT
            if deposit_amount < MultiLevelReferralSystem.MIN_DEPOSIT_AMOUNT:
                logger.info(f"Deposit amount ${deposit_amount} below minimum ${MultiLevelReferralSystem.MIN_DEPOSIT_AMOUNT}")
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
            
            # Award Level 1 Commission
            level_1_user = User.query.get(user.referred_by)
            if level_1_user and not MultiLevelReferralSystem.has_commission_been_awarded(level_1_user.id, user.id):
                commission = deposit_amount * MultiLevelReferralSystem.COMMISSION_RATES['level_1']
                level_1_user.referral_bonus += commission
                
                # Log the commission
                activity = ActivityLog(
                    user_id=level_1_user.id,
                    action='referral_commission',
                    description=f'Level 1 commission: ${commission:.2f} from {user.username} (Deposit: ${deposit_amount:.2f})'
                )
                db.session.add(activity)
                
                results['commissions_awarded'].append({
                    'level': 1,
                    'user': level_1_user.username,
                    'amount': commission
                })
                results['total_commission'] += commission
                
                logger.info(f"Level 1 commission awarded: ${commission:.2f} to {level_1_user.username}")
                
                # Award Level 2 Commission
                if level_1_user.referred_by:
                    level_2_user = User.query.get(level_1_user.referred_by)
                    if level_2_user and not MultiLevelReferralSystem.has_commission_been_awarded(level_2_user.id, user.id):
                        commission = deposit_amount * MultiLevelReferralSystem.COMMISSION_RATES['level_2']
                        level_2_user.referral_bonus += commission
                        
                        activity = ActivityLog(
                            user_id=level_2_user.id,
                            action='referral_commission',
                            description=f'Level 2 commission: ${commission:.2f} from {user.username} (Deposit: ${deposit_amount:.2f})'
                        )
                        db.session.add(activity)
                        
                        results['commissions_awarded'].append({
                            'level': 2,
                            'user': level_2_user.username,
                            'amount': commission
                        })
                        results['total_commission'] += commission
                        
                        logger.info(f"Level 2 commission awarded: ${commission:.2f} to {level_2_user.username}")
                        
                        # Award Level 3 Commission
                        if level_2_user.referred_by:
                            level_3_user = User.query.get(level_2_user.referred_by)
                            if level_3_user and not MultiLevelReferralSystem.has_commission_been_awarded(level_3_user.id, user.id):
                                commission = deposit_amount * MultiLevelReferralSystem.COMMISSION_RATES['level_3']
                                level_3_user.referral_bonus += commission
                                
                                activity = ActivityLog(
                                    user_id=level_3_user.id,
                                    action='referral_commission',
                                    description=f'Level 3 commission: ${commission:.2f} from {user.username} (Deposit: ${deposit_amount:.2f})'
                                )
                                db.session.add(activity)
                                
                                results['commissions_awarded'].append({
                                    'level': 3,
                                    'user': level_3_user.username,
                                    'amount': commission
                                })
                                results['total_commission'] += commission
                                
                                logger.info(f"Level 3 commission awarded: ${commission:.2f} to {level_3_user.username}")
            
            # Commit all changes
            db.session.commit()
            
            logger.info(f"Total commission awarded: ${results['total_commission']:.2f}")
            return results
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error awarding referral commission: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_active_referrals_count(user_id):
        """
        Get count of active referrals for a user (referrals with 100+ USDT deposits)
        """
        try:
            referrals = User.query.filter_by(referred_by=user_id).all()
            active_count = 0
            
            for referral in referrals:
                if MultiLevelReferralSystem.is_eligible_referral(referral.id):
                    active_count += 1
            
            return active_count
            
        except Exception as e:
            logger.error(f"Error getting active referrals count: {e}")
            return 0
    
    @staticmethod
    def get_referral_tree_with_commissions(user_id, max_depth=3):
        """
        Get complete referral tree with commission information
        """
        try:
            def build_tree(user_id, current_depth=1):
                if current_depth > max_depth:
                    return []
                
                referrals = User.query.filter_by(referred_by=user_id).all()
                tree = []
                
                for referral in referrals:
                    # Get commission information
                    commission_logs = ActivityLog.query.filter_by(
                        user_id=user_id,
                        action='referral_commission'
                    ).filter(ActivityLog.description.contains(f'from {referral.username}')).all()
                    
                    total_commission = sum(
                        float(log.description.split('$')[1].split(' ')[0]) 
                        for log in commission_logs 
                        if '$' in log.description
                    )
                    
                    referral_data = {
                        'user': {
                            'id': referral.id,
                            'username': referral.username,
                            'email': referral.email,
                            'balance': referral.usdt_balance,
                            'total_deposits': sum(d.amount for d in referral.deposits if d.status == 'approved'),
                            'is_eligible': MultiLevelReferralSystem.is_eligible_referral(referral.id)
                        },
                        'level': current_depth,
                        'commission_earned': total_commission,
                        'children': build_tree(referral.id, current_depth + 1)
                    }
                    tree.append(referral_data)
                
                return tree
            
            return build_tree(user_id)
            
        except Exception as e:
            logger.error(f"Error building referral tree: {e}")
            return []
    
    @staticmethod
    def validate_and_recalculate_all_commissions():
        """
        Validate and recalculate all referral commissions
        Use for fixing any inconsistencies
        """
        try:
            logger.info("Starting comprehensive referral commission validation...")
            
            # Get all users with approved deposits >= 100 USDT
            eligible_users = []
            all_users = User.query.filter(User.referred_by.isnot(None)).all()
            
            for user in all_users:
                if MultiLevelReferralSystem.is_eligible_referral(user.id):
                    eligible_users.append(user)
            
            logger.info(f"Found {len(eligible_users)} eligible referral users")
            
            # Reset all referral bonuses to recalculate
            # User.query.update({User.referral_bonus: 0})
            
            # Award commissions for each eligible user
            total_recalculated = 0
            for user in eligible_users:
                # Get their first qualifying deposit
                first_deposit = Deposit.query.filter_by(
                    user_id=user.id,
                    status='approved'
                ).filter(Deposit.amount >= MultiLevelReferralSystem.MIN_DEPOSIT_AMOUNT).first()
                
                if first_deposit:
                    result = MultiLevelReferralSystem.award_commission(user.id, first_deposit.amount)
                    if result['success']:
                        total_recalculated += result['total_commission']
            
            logger.info(f"Recalculation complete. Total commission: ${total_recalculated:.2f}")
            return {'success': True, 'total_recalculated': total_recalculated}
            
        except Exception as e:
            logger.error(f"Error in commission recalculation: {e}")
            return {'success': False, 'error': str(e)}

# Convenience functions for integration
def process_deposit_referral_commission(user_id, deposit_amount):
    """Process referral commission when deposit is approved"""
    return MultiLevelReferralSystem.award_commission(user_id, deposit_amount)

def get_user_active_referrals(user_id):
    """Get count of user's active referrals"""
    return MultiLevelReferralSystem.get_active_referrals_count(user_id)

def get_user_referral_tree(user_id):
    """Get user's complete referral tree with commissions"""
    return MultiLevelReferralSystem.get_referral_tree_with_commissions(user_id)

# Example usage:
if __name__ == "__main__":
    with app.app_context():
        # Test the referral system
        print("Testing Multi-Level Referral System...")
        
        # Example: Award commission for user deposit
        # result = process_deposit_referral_commission(user_id=5, deposit_amount=150)
        # print(f"Commission result: {result}")
        
        # Get active referrals for a user
        # active_count = get_user_active_referrals(user_id=1)
        # print(f"Active referrals: {active_count}")