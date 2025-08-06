#!/usr/bin/env python3
"""
Add missing referral_bonus column to User table
"""

from app import app, db
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_referral_bonus_column():
    """Add the missing referral_bonus column"""
    with app.app_context():
        try:
            # Add referral_bonus column if it doesn't exist
            db.session.execute(text("""
                ALTER TABLE "user" 
                ADD COLUMN IF NOT EXISTS referral_bonus FLOAT DEFAULT 0.0
            """))
            logger.info("Added referral_bonus column")
            
            db.session.commit()
            logger.info("✓ Successfully added referral_bonus column")
            
        except Exception as e:
            logger.error(f"Error adding column: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    add_referral_bonus_column()