
"""
Database migration script to create referral_commissions table
Run this once to set up the new referral commission system
"""

from app import app, db
from models import ReferralCommission

def create_referral_commission_table():
    """Create the referral_commissions table"""
    try:
        with app.app_context():
            # Create the table
            db.create_all()
            print("✅ Successfully created referral_commissions table")
            
            # Verify table exists
            tables = db.engine.table_names()
            if 'referral_commissions' in tables:
                print("✅ Table 'referral_commissions' confirmed in database")
            else:
                print("❌ Table 'referral_commissions' not found")
                
            return True
            
    except Exception as e:
        print(f"❌ Error creating table: {str(e)}")
        return False

if __name__ == "__main__":
    print("Creating referral_commissions table...")
    create_referral_commission_table()
