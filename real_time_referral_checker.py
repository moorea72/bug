
#!/usr/bin/env python3
"""
Real-time Referral Balance Checker
- Only referrals with current balance 100+ USDT count as active
- Blue tick only for salary eligible users (not just 2+ referrals)  
- Real-time balance checking includes wallet + active stakes
"""

from app import app, db
from models import User, Stake
from datetime import datetime

def update_all_referral_counts():
    """Update referral counts for all users based on real-time balances"""
    try:
        with app.app_context():
            print(f"🔄 Starting real-time referral count update at {datetime.now()}")
            
            # Get all users who have referrals
            users_with_referrals = User.query.filter(
                User.id.in_(
                    db.session.query(User.referred_by).filter(User.referred_by.isnot(None))
                )
            ).all()
            
            updated_count = 0
            
            for user in users_with_referrals:
                old_count = user.get_qualified_referrals_count()
                
                # Get current referrals with 100+ USDT balance (real-time)
                current_active_referrals = 0
                referrals = User.query.filter_by(referred_by=user.id).all()
                
                for referral in referrals:
                    # Calculate real-time balance (wallet + active stakes)
                    wallet_balance = referral.usdt_balance or 0
                    active_stakes = db.session.query(db.func.sum(Stake.amount)).filter_by(
                        user_id=referral.id,
                        status='active'
                    ).scalar() or 0
                    
                    total_balance = wallet_balance + active_stakes
                    
                    if total_balance >= 100:
                        current_active_referrals += 1
                
                if current_active_referrals != old_count:
                    print(f"   📊 {user.username}: {old_count} → {current_active_referrals} active referrals")
                    updated_count += 1
            
            print(f"✅ Updated {updated_count} users' referral counts based on real-time balances")
            
            # Check salary eligibility changes
            salary_eligible_users = []
            for user in User.query.all():
                if user.is_salary_eligible():
                    salary_eligible_users.append(user.username)
            
            print(f"💰 Current salary eligible users: {len(salary_eligible_users)}")
            for username in salary_eligible_users:
                print(f"   ✅ {username} - Salary eligible (Blue tick)")
            
            return {
                'updated_users': updated_count,
                'salary_eligible_count': len(salary_eligible_users),
                'timestamp': datetime.now().isoformat()
            }
            
    except Exception as e:
        print(f"❌ Error updating referral counts: {e}")
        return {'error': str(e)}

def check_user_referral_status(user_id):
    """Check specific user's referral status with real-time balance"""
    try:
        with app.app_context():
            user = User.query.get(user_id)
            if not user:
                return {'error': 'User not found'}
            
            # Get real-time referral data
            referrals = User.query.filter_by(referred_by=user.id).all()
            active_referrals = []
            inactive_referrals = []
            
            for referral in referrals:
                current_balance = referral.get_total_balance_including_stakes()
                
                referral_data = {
                    'username': referral.username,
                    'balance': current_balance,
                    'wallet': referral.usdt_balance,
                    'stakes': current_balance - referral.usdt_balance,
                    'is_active': current_balance >= 100
                }
                
                if current_balance >= 100:
                    active_referrals.append(referral_data)
                else:
                    inactive_referrals.append(referral_data)
            
            # Check salary eligibility
            is_salary_eligible = user.is_salary_eligible()
            current_balance = user.get_total_balance_including_stakes()
            
            return {
                'user': user.username,
                'total_referrals': len(referrals),
                'active_referrals': len(active_referrals),
                'inactive_referrals': len(inactive_referrals),
                'active_referral_details': active_referrals,
                'inactive_referral_details': inactive_referrals,
                'user_balance': current_balance,
                'is_salary_eligible': is_salary_eligible,
                'blue_tick_eligible': is_salary_eligible,  # Only salary eligible get blue tick
                'timestamp': datetime.now().isoformat()
            }
            
    except Exception as e:
        return {'error': str(e)}

if __name__ == "__main__":
    # Test the real-time referral checker
    result = update_all_referral_counts()
    print(f"\n📋 Final Result: {result}")
