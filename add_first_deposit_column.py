"""
Add first_deposit_completed column to user table
"""
from app import app, db
from models import User

def add_first_deposit_column():
    with app.app_context():
        try:
            # Add the new column using raw SQL
            db.engine.execute("ALTER TABLE \"user\" ADD COLUMN first_deposit_completed BOOLEAN DEFAULT FALSE")
            print("✓ Added first_deposit_completed column to user table")
            
            # Update existing users to have first_deposit_completed = False
            db.engine.execute("UPDATE \"user\" SET first_deposit_completed = FALSE WHERE first_deposit_completed IS NULL")
            print("✓ Updated all existing users with first_deposit_completed = FALSE")
            
            return True
            
        except Exception as e:
            if "already exists" in str(e) or "duplicate column" in str(e):
                print("✓ Column first_deposit_completed already exists")
                return True
            else:
                print(f"❌ Error adding column: {e}")
                return False

if __name__ == "__main__":
    success = add_first_deposit_column()
    if success:
        print("✓ Database migration completed successfully")
    else:
        print("❌ Database migration failed")