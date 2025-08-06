"""
Monthly Salary Scheduler
Automatically process salary requests on the 1st of each month
"""
import schedule
import time
from datetime import datetime
from automatic_salary_system import process_monthly_salary_requests
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def monthly_salary_job():
    """Job to run on the 1st of each month"""
    try:
        print(f"🗓️  Monthly salary processing started at {datetime.now()}")
        count = process_monthly_salary_requests()
        print(f"✅ Monthly salary processing completed - {count} requests processed")
        logging.info(f"Monthly salary processing completed - {count} requests processed")
    except Exception as e:
        print(f"❌ Error in monthly salary processing: {str(e)}")
        logging.error(f"Monthly salary processing error: {str(e)}")

def start_scheduler():
    """Start the monthly scheduler"""
    # Schedule the job to run on the 1st of each month at 00:01 AM
    schedule.every().month.at("00:01").do(monthly_salary_job)
    
    print("📅 Monthly salary scheduler started")
    print("🔄 Waiting for the 1st of each month at 00:01 AM...")
    
    while True:
        schedule.run_pending()
        time.sleep(3600)  # Check every hour

if __name__ == "__main__":
    start_scheduler()