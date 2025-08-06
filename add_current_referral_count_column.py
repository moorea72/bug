#!/usr/bin/env python3
"""
Add current_referral_count column to User table
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db

def add_current_referral_count_column():
    """Add current_referral_count column to User table"""
    
    with app.app_context():
        try:
            print("🔧 Adding current_referral_count column to User table...")
            
            # Add the column to the database
            from sqlalchemy import text
            with db.engine.connect() as connection:
                connection.execute(text('ALTER TABLE "user" ADD COLUMN current_referral_count INTEGER DEFAULT 0'))
                connection.commit()
            
            print("✅ Column added successfully!")
            
            # Update all existing users to have 0 as default
            from models import User
            users = User.query.all()
            for user in users:
                if not hasattr(user, 'current_referral_count') or user.current_referral_count is None:
                    user.current_referral_count = 0
            
            db.session.commit()
            
            print(f"✅ Updated {len(users)} users with default value 0")
            return True
            
        except Exception as e:
            if "already exists" in str(e).lower():
                print("✅ Column already exists!")
                return True
            else:
                print(f"❌ Error: {str(e)}")
                return False

if __name__ == "__main__":
    success = add_current_referral_count_column()
    if success:
        print("\n🎉 Database update completed successfully!")
    else:
        print("\n❌ Database update failed!")
        sys.exit(1)