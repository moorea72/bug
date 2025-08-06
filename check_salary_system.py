#!/usr/bin/env python3
"""
Check salary system status and process automatic salary requests
"""

from app import app
from models import *
from salary_system import *
from automatic_salary_system import *

def check_salary_system_status():
    """Check and process salary system"""
    with app.app_context():
        print('=== Checking Salary System Status ===')
        
        # Check if there are any salary requests
        pending_requests = SalaryWithdrawal.query.filter_by(status='pending').all()
        print(f'Pending salary requests: {len(pending_requests)}')
        
        # Check eligible users
        users = User.query.filter(User.is_active == True).all()
        eligible_users = []
        
        for user in users:
            eligible_plan, active_referrals, total_balance = check_salary_eligibility(user)
            if eligible_plan and user.salary_wallet_address:
                eligible_users.append((user, eligible_plan, active_referrals, total_balance))
        
        print(f'Eligible users with wallet addresses: {len(eligible_users)}')
        
        # Show details for eligible users
        for user, plan, refs, balance in eligible_users:
            print(f'- {user.username}: Plan {plan}, {refs} referrals, ${balance} balance')
        
        # Try to process automatic salary requests
        if eligible_users:
            print('\n=== Processing Automatic Salary Requests ===')
            processed = process_monthly_salary_requests()
            print(f'New salary requests created: {processed}')
        
        # Show pending requests after processing
        pending_after = SalaryWithdrawal.query.filter_by(status='pending').all()
        print(f'\nPending salary requests after processing: {len(pending_after)}')
        
        for req in pending_after:
            print(f'- Request #{req.id}: {req.user.username} - ${req.amount} (Plan {req.plan_id})')

if __name__ == '__main__':
    check_salary_system_status()