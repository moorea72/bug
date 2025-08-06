
#!/usr/bin/env python3
"""
Fix login 500 error by adding missing database columns
"""

from app import app, db
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_missing_columns():
    """Add missing columns to fix login 500 error"""
    with app.app_context():
        try:
            # Add two_friends_bonus_claimed column
            try:
                db.session.execute(text('ALTER TABLE "user" ADD COLUMN two_friends_bonus_claimed BOOLEAN DEFAULT FALSE'))
                logger.info("✅ Added two_friends_bonus_claimed column")
            except Exception as e:
                if "already exists" in str(e).lower():
                    logger.info("ℹ️ two_friends_bonus_claimed column already exists")
                else:
                    logger.error(f"Error adding two_friends_bonus_claimed: {e}")
            
            # Add premium_benefits_active column
            try:
                db.session.execute(text('ALTER TABLE "user" ADD COLUMN premium_benefits_active BOOLEAN DEFAULT FALSE'))
                logger.info("✅ Added premium_benefits_active column")
            except Exception as e:
                if "already exists" in str(e).lower():
                    logger.info("ℹ️ premium_benefits_active column already exists")
                else:
                    logger.error(f"Error adding premium_benefits_active: {e}")
            
            # Add premium_commission column to stake table
            try:
                db.session.execute(text('ALTER TABLE stake ADD COLUMN premium_commission FLOAT DEFAULT 0.0'))
                logger.info("✅ Added premium_commission column to stake table")
            except Exception as e:
                if "already exists" in str(e).lower():
                    logger.info("ℹ️ premium_commission column already exists")
                else:
                    logger.error(f"Error adding premium_commission: {e}")
            
            # Commit all changes
            db.session.commit()
            logger.info("🎉 Database migration completed successfully!")
            
            # Update existing users with default values
            db.session.execute(text('''
                UPDATE "user" SET 
                two_friends_bonus_claimed = FALSE 
                WHERE two_friends_bonus_claimed IS NULL
            '''))
            
            db.session.execute(text('''
                UPDATE "user" SET 
                premium_benefits_active = FALSE 
                WHERE premium_benefits_active IS NULL
            '''))
            
            db.session.commit()
            logger.info("✅ Updated existing users with default values")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error during migration: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = fix_missing_columns()
    if success:
        print("✅ Login 500 error fixed! You can now login successfully.")
    else:
        print("❌ Migration failed. Check the logs above.")
