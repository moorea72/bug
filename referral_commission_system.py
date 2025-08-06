"""
Referral Deposit Commission System - USDT Based (One-Time Only)

Commission Tiers (One-time only):
- $50 – $199.99 USDT → Referrer gets $7 USDT
- $200 – $299.99 USDT → Referrer gets $15 USDT  
- $300+ USDT → Referrer gets $26 USDT

Rules:
- Only direct referrer is eligible
- Commission based on first-ever deposit only
- No repeated commissions on subsequent deposits
"""

from app import db
from models import User, Deposit, ActivityLog, ReferralCommission
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReferralCommissionSystem:
    """One-time referral deposit commission system"""

    # Commission tiers based on first deposit amount
    COMMISSION_TIERS = {
        'tier_1': {'min': 50, 'max': 199.99, 'commission': 7},
        'tier_2': {'min': 200, 'max': 299.99, 'commission': 15},
        'tier_3': {'min': 300, 'max': float('inf'), 'commission': 26}
    }

    @staticmethod
    def process_first_deposit_commission(user_id, deposit_amount):
        """
        AUTOMATIC commission processing for first-time deposit by referred user
        Returns: dict with success status and details
        """
        try:
            # Get the user who made the deposit
            user = User.query.get(user_id)
            if not user or not user.referred_by:
                logger.info(f"AUTOMATIC: User {user_id} has no referrer - skipping commission")
                return {'success': False, 'reason': 'No referrer'}

            # Check if commission has already been given for this user
            if ReferralCommissionSystem.has_commission_been_given(user_id):
                logger.info(f"AUTOMATIC: Commission already given for user {user_id} - skipping")
                return {'success': False, 'reason': 'Commission already given'}

            # Get the referrer
            referrer = User.query.get(user.referred_by)
            if not referrer:
                logger.info(f"AUTOMATIC: Referrer not found for user {user_id}")
                return {'success': False, 'reason': 'Referrer not found'}

            # Determine commission amount based on deposit
            commission_amount = ReferralCommissionSystem.calculate_commission(deposit_amount)

            if commission_amount == 0:
                logger.info(f"AUTOMATIC: Deposit amount ${deposit_amount} too low for commission (minimum $50)")
                return {'success': False, 'reason': 'Deposit below minimum threshold ($50 USDT)'}

            # AUTOMATIC: Award commission to referrer
            referrer.usdt_balance += commission_amount
            referrer.referral_bonus += commission_amount

            # Create commission record in ReferralCommission table
            commission_record = ReferralCommission(
                referrer_id=referrer.id,
                referred_user_id=user.id,
                commission_amount_usdt=commission_amount,
                deposit_amount=deposit_amount
            )
            db.session.add(commission_record)

            # Log the automatic commission activity
            activity = ActivityLog(
                user_id=referrer.id,
                action='auto_referral_commission',
                description=f'AUTOMATIC Referral Commission: ${commission_amount} USDT from {user.username} first deposit (${deposit_amount} USDT) - Instant Processing'
            )
            db.session.add(activity)

            # Log for the referred user too
            referred_activity = ActivityLog(
                user_id=user.id,
                action='auto_generated_commission',
                description=f'AUTOMATIC: Generated ${commission_amount} USDT commission for referrer {referrer.username} on first deposit'
            )
            db.session.add(referred_activity)

            db.session.commit()

            logger.info(f"AUTOMATIC COMMISSION AWARDED: ${commission_amount} USDT to {referrer.username} from {user.username} (${deposit_amount} deposit)")

            return {
                'success': True,
                'commission_amount': commission_amount,
                'referrer': referrer.username,
                'referred_user': user.username,
                'deposit_amount': deposit_amount,
                'automatic': True
            }

        except Exception as e:
            db.session.rollback()
            logger.error(f"AUTOMATIC COMMISSION ERROR: {str(e)}")
            return {'success': False, 'reason': str(e)}

    @staticmethod
    def calculate_commission(deposit_amount):
        """Calculate commission based on deposit amount"""
        for tier_name, tier_data in ReferralCommissionSystem.COMMISSION_TIERS.items():
            if tier_data['min'] <= deposit_amount <= tier_data['max']:
                return tier_data['commission']
        return 0

    @staticmethod
    def has_commission_been_given(user_id):
        """Check if commission has already been given for this user"""
        return ReferralCommission.query.filter_by(referred_user_id=user_id).first() is not None

    @staticmethod
    def get_referrer_commission_stats(referrer_id):
        """Get commission statistics for a referrer"""
        commissions = ReferralCommission.query.filter_by(referrer_id=referrer_id).all()

        stats = {
            'total_commissions': len(commissions),
            'total_amount': sum(c.commission_amount_usdt for c in commissions),
            'commissions': []
        }

        for commission in commissions:
            referred_user = User.query.get(commission.referred_user_id)
            stats['commissions'].append({
                'referred_user': referred_user.username if referred_user else 'Unknown',
                'commission_amount': commission.commission_amount_usdt,
                'deposit_amount': commission.deposit_amount,
                'date': commission.created_at.strftime('%Y-%m-%d %H:%M')
            })

        return stats

    @staticmethod
    def get_system_stats():
        """Get overall system statistics"""
        total_commissions = ReferralCommission.query.count()
        total_amount = db.session.query(db.func.sum(ReferralCommission.commission_amount_usdt)).scalar() or 0

        # Count by tiers
        tier_stats = {}
        for tier_name, tier_data in ReferralCommissionSystem.COMMISSION_TIERS.items():
            count = ReferralCommission.query.filter_by(commission_amount_usdt=tier_data['commission']).count()
            tier_stats[tier_name] = {
                'count': count,
                'commission_amount': tier_data['commission'],
                'total_paid': count * tier_data['commission']
            }

        return {
            'total_commissions': total_commissions,
            'total_amount_paid': total_amount,
            'tier_breakdown': tier_stats
        }

# Integration function to be called when deposit is approved
def process_deposit_commission(user_id, deposit_amount):
    """Main function to process deposit commission - call this when deposit is approved"""
    return ReferralCommissionSystem.process_first_deposit_commission(user_id, deposit_amount)