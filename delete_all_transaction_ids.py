
#!/usr/bin/env python3
"""
Delete all deposit transaction IDs from the database
"""

from app import app, db
from models import Deposit

def delete_all_transaction_ids():
    """Delete all transaction IDs from deposits table"""
    try:
        with app.app_context():
            print("🗑️  Deleting all deposit transaction IDs...")
            
            # Get all deposits
            deposits = Deposit.query.all()
            total_deposits = len(deposits)
            
            print(f"Found {total_deposits} deposits in database")
            
            if total_deposits == 0:
                print("No deposits found in database")
                return
            
            # Clear all transaction IDs
            updated_count = 0
            for deposit in deposits:
                if deposit.transaction_id:
                    print(f"Clearing transaction ID for deposit #{deposit.id}: {deposit.transaction_id}")
                    deposit.transaction_id = None
                    updated_count += 1
            
            # Commit changes
            db.session.commit()
            
            print(f"✅ Successfully cleared {updated_count} transaction IDs")
            print(f"📊 Total deposits: {total_deposits}")
            print(f"🔄 Updated deposits: {updated_count}")
            print(f"⚡ Remaining deposits: {total_deposits - updated_count}")
            
            # Verify the changes
            remaining_with_tx_ids = Deposit.query.filter(Deposit.transaction_id.isnot(None)).count()
            print(f"🔍 Verification: {remaining_with_tx_ids} deposits still have transaction IDs")
            
            if remaining_with_tx_ids == 0:
                print("✅ All transaction IDs successfully deleted!")
            else:
                print(f"⚠️  Warning: {remaining_with_tx_ids} deposits still have transaction IDs")
                
    except Exception as e:
        print(f"❌ Error deleting transaction IDs: {str(e)}")
        db.session.rollback()

if __name__ == "__main__":
    delete_all_transaction_ids()
