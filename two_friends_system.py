
"""
2 Friends Premium Benefits System
- No referral commissions (completely removed)
- Users get premium benefits after referring 2 friends with 100+ USDT deposits
- Premium benefits: 20 USDT bonus, no withdrawal fees, 2% commission on stakes
"""

from app import app, db
from models import User, Deposit, Stake, ActivityLog
from datetime import datetime

class TwoFriendsSystem:
    """Manages the 2 Friends premium benefits system"""
    
    @staticmethod
    def check_user_premium_eligibility(user_id):
        """Check if user qualifies for premium benefits"""
        try:
            user = User.query.get(user_id)
            if not user:
                return False
            
            # Check if user has 2 qualified referrals
            qualified_referrals = user.get_qualified_referrals_count()
            
            if qualified_referrals >= 2:
                # Activate premium benefits if not already active
                if not user.premium_benefits_active:
                    user.check_and_activate_premium_benefits()
                return True
            else:
                # Deactivate premium if user no longer qualifies
                if user.premium_benefits_active and qualified_referrals < 2:
                    user.premium_benefits_active = False
                    db.session.commit()
                return False
                
        except Exception as e:
            print(f"Error checking premium eligibility: {e}")
            return False
    
    @staticmethod
    def process_stake_commission(stake_id):
        """Process 2% commission for premium users on stakes"""
        try:
            stake = Stake.query.get(stake_id)
            if not stake or not stake.user:
                return False
            
            user = stake.user
            
            # Check if user has premium benefits
            if user.premium_benefits_active:
                # Calculate 2% commission
                commission = stake.amount * 0.02
                stake.premium_commission = commission
                
                # Add commission to user balance
                user.usdt_balance += commission
                
                # Log the commission
                activity = ActivityLog(
                    user_id=user.id,
                    action='premium_stake_commission',
                    description=f'Premium stake commission: ${commission:.2f} on ${stake.amount:.2f} stake'
                )
                db.session.add(activity)
                db.session.commit()
                
                return True
            
            return False
            
        except Exception as e:
            print(f"Error processing stake commission: {e}")
            return False
    
    @staticmethod
    def calculate_withdrawal_fee(user_id, amount):
        """Calculate withdrawal fee (0 for premium users)"""
        try:
            user = User.query.get(user_id)
            if not user:
                return amount * 0.01  # Default 1% fee
            
            if user.premium_benefits_active:
                return 0.0  # No fees for premium users
            else:
                return amount * 0.01  # 1% fee for regular users
                
        except Exception as e:
            print(f"Error calculating withdrawal fee: {e}")
            return amount * 0.01
    
    @staticmethod
    def update_all_premium_status():
        """Update premium status for all users based on their referrals"""
        try:
            users = User.query.all()
            updated_count = 0
            
            for user in users:
                old_status = user.premium_benefits_active
                TwoFriendsSystem.check_user_premium_eligibility(user.id)
                
                if user.premium_benefits_active != old_status:
                    updated_count += 1
            
            print(f"Updated premium status for {updated_count} users")
            return updated_count
            
        except Exception as e:
            print(f"Error updating premium status: {e}")
            return 0
    
    @staticmethod
    def get_user_referral_progress(user_id):
        """Get user's progress towards premium benefits"""
        try:
            user = User.query.get(user_id)
            if not user:
                return None
            
            qualified_referrals = user.get_qualified_referrals_count()
            total_referrals = user.get_referral_count()
            
            progress = {
                'total_referrals': total_referrals,
                'qualified_referrals': qualified_referrals,
                'progress_percentage': min(100, (qualified_referrals / 2) * 100),
                'premium_active': user.premium_benefits_active,
                'bonus_claimed': user.two_friends_bonus_claimed,
                'referrals_needed': max(0, 2 - qualified_referrals)
            }
            
            return progress
            
        except Exception as e:
            print(f"Error getting referral progress: {e}")
            return None

# Helper functions for integration
def check_and_update_user_premium(user_id):
    """Check and update user's premium status"""
    return TwoFriendsSystem.check_user_premium_eligibility(user_id)

def process_deposit_premium_check(user_id, deposit_amount):
    """Check if deposit affects premium status for referrer"""
    try:
        user = User.query.get(user_id)
        if not user or not user.referred_by:
            return
        
        # Check if this deposit qualifies the user (100+ USDT)
        if deposit_amount >= 100:
            # Check referrer's premium status
            TwoFriendsSystem.check_user_premium_eligibility(user.referred_by)
            
    except Exception as e:
        print(f"Error processing deposit premium check: {e}")

if __name__ == "__main__":
    with app.app_context():
        print("Testing 2 Friends Premium System...")
        
        # Update all users' premium status
        updated = TwoFriendsSystem.update_all_premium_status()
        print(f"Updated {updated} users")
        
        # Test user progress
        admin = User.query.filter_by(username='admin').first()
        if admin:
            progress = TwoFriendsSystem.get_user_referral_progress(admin.id)
            print(f"Admin progress: {progress}")
