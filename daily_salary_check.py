
#!/usr/bin/env python3
"""
Daily Salary Check Script
Run this daily to automatically process salary requests on the 1st of each month
"""

from app import app
from automatic_salary_system import check_and_process_monthly_salaries
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('salary_processing.log'),
        logging.StreamHandler()
    ]
)

def daily_salary_check():
    """Run daily salary check"""
    with app.app_context():
        try:
            print("🤖 Starting daily salary check...")
            count = check_and_process_monthly_salaries()
            
            if count > 0:
                logging.info(f"✅ Processed {count} automatic salary requests")
                print(f"✅ SUCCESS: {count} salary requests processed")
            else:
                logging.info("📅 No salary processing needed today")
                print("📅 No salary processing needed today")
                
            return count
            
        except Exception as e:
            logging.error(f"❌ Error in daily salary check: {str(e)}")
            print(f"❌ ERROR: {str(e)}")
            return 0

if __name__ == "__main__":
    daily_salary_check()
