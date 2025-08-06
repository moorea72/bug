"""
Advanced Salary System Implementation
- 4 salary plans with referral and balance requirements
- Direct crypto wallet payments
- Automatic admin approval system
- Progress bars for each plan
- Balance and stake tracking
"""

from datetime import datetime, timedelta
from app import db
from models import User, Deposit, Stake, Withdrawal

class SalaryPlan:
    """Salary plan configuration"""
    PLANS = {
        1: {
            'name': 'Basic Plan',
            'required_referrals': 7,
            'required_balance': 350,
            'monthly_salary': 50,
            'color': 'green'
        },
        2: {
            'name': 'Silver Plan', 
            'required_referrals': 13,
            'required_balance': 680,
            'monthly_salary': 110,
            'color': 'blue'
        },
        3: {
            'name': 'Gold Plan',
            'required_referrals': 27,
            'required_balance': 960,
            'monthly_salary': 230,
            'color': 'yellow'
        },
        4: {
            'name': 'Platinum Plan',
            'required_referrals': 46,
            'required_balance': 1340,
            'monthly_salary': 480,
            'color': 'purple'
        }
    }

def get_user_total_balance(user):
    """Get user's total balance including stakes"""
    wallet_balance = user.usdt_balance
    active_stakes = db.session.query(db.func.sum(Stake.amount)).filter_by(
        user_id=user.id, 
        status='active'
    ).scalar() or 0
    
    return wallet_balance + active_stakes

def get_active_referrals_with_balance(user):
    """Get referrals who have deposited at least 100 USDT"""
    active_referrals = []
    referrals = User.query.filter_by(referred_by=user.id).all()
    
    for referral in referrals:
        total_deposits = db.session.query(db.func.sum(Deposit.amount)).filter_by(
            user_id=referral.id,
            status='approved'
        ).scalar() or 0
        
        if total_deposits >= 100:
            active_referrals.append(referral)
    
    return active_referrals

def check_salary_eligibility(user):
    """Check which salary plan user is eligible for"""
    active_referrals = get_active_referrals_with_balance(user)
    total_balance = get_user_total_balance(user)
    
    eligible_plan = None
    
    # Check from highest to lowest plan
    for plan_id in [4, 3, 2, 1]:
        plan = SalaryPlan.PLANS[plan_id]
        if (len(active_referrals) >= plan['required_referrals'] and 
            total_balance >= plan['required_balance']):
            eligible_plan = plan_id
            break
    
    return eligible_plan, len(active_referrals), total_balance

def get_salary_progress(user):
    """Get progress towards each salary plan"""
    active_referrals = get_active_referrals_with_balance(user)
    total_balance = get_user_total_balance(user)
    
    progress = {}
    
    for plan_id, plan in SalaryPlan.PLANS.items():
        referral_progress = min(100, (len(active_referrals) / plan['required_referrals']) * 100)
        balance_progress = min(100, (total_balance / plan['required_balance']) * 100)
        
        progress[plan_id] = {
            'plan': plan,
            'referral_count': len(active_referrals),
            'total_balance': total_balance,
            'referral_progress': round(referral_progress, 1),
            'balance_progress': round(balance_progress, 1),
            'is_eligible': (len(active_referrals) >= plan['required_referrals'] and 
                          total_balance >= plan['required_balance'])
        }
    
    return progress

def create_salary_withdrawal_request(user, plan_id):
    """Create automatic salary withdrawal request for admin approval"""
    from models import SalaryWithdrawal
    
    plan = SalaryPlan.PLANS[plan_id]
    
    # Check if user already has pending salary request for this month
    current_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    existing_request = SalaryWithdrawal.query.filter_by(
        user_id=user.id,
        status='pending'
    ).filter(
        SalaryWithdrawal.created_at >= current_month
    ).first()
    
    if existing_request:
        return None  # Already has pending request
    
    # Create new salary withdrawal request
    salary_request = SalaryWithdrawal(
        user_id=user.id,
        plan_id=plan_id,
        amount=plan['monthly_salary'],
        wallet_address=user.salary_wallet_address,
        status='pending'
    )
    
    db.session.add(salary_request)
    db.session.commit()
    
    return salary_request