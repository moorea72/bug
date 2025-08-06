
#!/usr/bin/env python3
"""
Remove specific deposit transaction ID from the database
"""

from app import app, db
from models import Deposit

def remove_specific_transaction():
    """Remove specific transaction ID from deposits table"""
    target_tx_id = "0x862f87f5950e63d0676ed72bf3e4c5bbf5d91ed64ad9ec5c2b78d3f4d41f19e6"
    
    try:
        with app.app_context():
            print(f"🔍 Searching for transaction ID: {target_tx_id}")
            
            # Find the deposit with this transaction ID
            deposit = Deposit.query.filter_by(transaction_id=target_tx_id).first()
            
            if not deposit:
                print("❌ Transaction ID not found in database")
                return
            
            print(f"✅ Found deposit:")
            print(f"   - Deposit ID: {deposit.id}")
            print(f"   - User ID: {deposit.user_id}")
            print(f"   - Amount: ${deposit.amount}")
            print(f"   - Status: {deposit.status}")
            print(f"   - Created: {deposit.created_at}")
            
            # Clear the transaction ID
            print(f"🗑️  Removing transaction ID...")
            deposit.transaction_id = None
            
            # Commit changes
            db.session.commit()
            
            print("✅ Transaction ID successfully removed!")
            print(f"📊 Deposit #{deposit.id} still exists but transaction_id is now NULL")
            
            # Verify the change
            updated_deposit = Deposit.query.get(deposit.id)
            if updated_deposit.transaction_id is None:
                print("🔍 Verification: Transaction ID successfully cleared")
            else:
                print("⚠️  Warning: Transaction ID was not cleared properly")
                
    except Exception as e:
        print(f"❌ Error removing transaction ID: {str(e)}")
        db.session.rollback()

if __name__ == "__main__":
    remove_specific_transaction()
