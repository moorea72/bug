"""
Automatic Salary Request System
Automatically creates salary requests for eligible users on the 1st of each month
"""
from datetime import datetime, timedelta
from app import app, db
from models import User, SalaryWithdrawal
from salary_system import check_salary_eligibility, create_salary_withdrawal_request, SalaryPlan
from utils import log_activity
import logging

def process_monthly_salary_requests():
    """
    Process automatic salary requests for all eligible users
    Should be called on the 1st of each month
    """
    with app.app_context():
        try:
            # Get all active users with salary wallet addresses
            users = User.query.filter(
                User.is_active == True,
                User.salary_wallet_address.isnot(None)
            ).all()
            
            processed_count = 0
            eligible_count = 0
            
            for user in users:
                # Check if user is eligible for any salary plan
                eligible_plan, active_referrals, total_balance = check_salary_eligibility(user)
                
                if eligible_plan:
                    eligible_count += 1
                    
                    # Check if user already has a salary request for this month
                    current_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                    existing_request = SalaryWithdrawal.query.filter(
                        SalaryWithdrawal.user_id == user.id,
                        SalaryWithdrawal.created_at >= current_month
                    ).first()
                    
                    if not existing_request:
                        # Create automatic salary request
                        salary_request = create_salary_withdrawal_request(user, eligible_plan)
                        
                        if salary_request:
                            processed_count += 1
                            log_activity(user.id, 'automatic_salary_request', 
                                       f'Automatic salary request created for Plan {eligible_plan} - ${SalaryPlan.PLANS[eligible_plan]["monthly_salary"]}')
                            
                            print(f"✓ Created automatic salary request for {user.username} - Plan {eligible_plan}")
                        else:
                            print(f"✗ Failed to create salary request for {user.username}")
                    else:
                        print(f"• User {user.username} already has a salary request for this month")
                else:
                    print(f"• User {user.username} not eligible for any salary plan")
            
            print(f"\n=== Monthly Salary Processing Complete ===")
            print(f"Total users checked: {len(users)}")
            print(f"Eligible users: {eligible_count}")
            print(f"New requests created: {processed_count}")
            
            return processed_count
            
        except Exception as e:
            print(f"Error in automatic salary processing: {str(e)}")
            logging.error(f"Automatic salary processing error: {str(e)}")
            return 0

def check_and_process_monthly_salaries():
    """
    Check if it's the 1st of the month and process salaries automatically
    This function can be called daily by a cron job
    """
    today = datetime.now()
    
    # Check if it's the 1st of the month
    if today.day == 1:
        print(f"🗓️  It's the 1st of {today.strftime('%B %Y')} - Processing automatic salary requests...")
        
        # Also check if we haven't already processed for this month
        current_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Check if any salary requests already exist for this month
        from models import SalaryWithdrawal
        existing_requests = SalaryWithdrawal.query.filter(
            SalaryWithdrawal.created_at >= current_month
        ).count()
        
        if existing_requests > 0:
            print(f"✅ Salary requests already processed for {today.strftime('%B %Y')} ({existing_requests} requests found)")
            return 0
        
        return process_monthly_salary_requests()
    else:
        print(f"📅 Today is {today.strftime('%B %d, %Y')} - Not the 1st of the month")
        return 0

if __name__ == "__main__":
    # For testing - force process salary requests
    print("🔄 Force processing salary requests...")
    count = process_monthly_salary_requests()
    print(f"✅ Processed {count} automatic salary requests")