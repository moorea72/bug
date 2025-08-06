#!/usr/bin/env python3
"""
Add salary_wallet_address column to users table
"""

from app import app, db
from models import User, SalaryWithdrawal

def add_salary_wallet_column():
    """Add salary_wallet_address column to users table"""
    with app.app_context():
        try:
            # Check if column exists
            result = db.session.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='user' AND column_name='salary_wallet_address'
            """)
            
            if result.fetchone() is None:
                # Column doesn't exist, add it
                db.session.execute("""
                    ALTER TABLE "user" 
                    ADD COLUMN salary_wallet_address VARCHAR(255)
                """)
                db.session.commit()
                print("✓ Added salary_wallet_address column to user table")
            else:
                print("✓ salary_wallet_address column already exists")
                
        except Exception as e:
            print(f"✗ Error adding column: {e}")
            db.session.rollback()

def create_salary_tables():
    """Create salary withdrawal table"""
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("✓ Created all database tables")
            
        except Exception as e:
            print(f"✗ Error creating tables: {e}")

if __name__ == '__main__':
    print("Adding salary system database columns...")
    add_salary_wallet_column()
    create_salary_tables()
    print("Database migration completed!")