#!/usr/bin/env python3
"""
Fix database schema issues - add missing columns
"""

from app import app, db
from sqlalchemy import text

def fix_database_schema():
    """Fix all database schema issues"""
    with app.app_context():
        try:
            # Check if salary_wallet_address column exists
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='user' AND column_name='salary_wallet_address'
            """))
            
            if result.fetchone() is None:
                # Column doesn't exist, add it
                db.session.execute(text("""
                    ALTER TABLE "user" 
                    ADD COLUMN salary_wallet_address VARCHAR(255)
                """))
                db.session.commit()
                print("✓ Added salary_wallet_address column to user table")
            else:
                print("✓ salary_wallet_address column already exists")
                
            # Ensure all tables exist
            db.create_all()
            print("✓ Ensured all database tables exist")
            
        except Exception as e:
            print(f"✗ Error fixing database schema: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    print("Fixing database schema...")
    fix_database_schema()
    print("Database schema fixed!")