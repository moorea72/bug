#!/usr/bin/env python3
"""
Add columns for simple referral system
"""

from app import app, db
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_simple_referral_columns():
    """Add the new columns needed for simple referral system"""
    with app.app_context():
        try:
            # Add two_referral_bonus_claimed column
            db.session.execute(text("""
                ALTER TABLE "user" 
                ADD COLUMN IF NOT EXISTS two_referral_bonus_claimed BOOLEAN DEFAULT FALSE
            """))
            logger.info("Added two_referral_bonus_claimed column")
            
            # Add stake_commission_eligible column
            db.session.execute(text("""
                ALTER TABLE "user" 
                ADD COLUMN IF NOT EXISTS stake_commission_eligible BOOLEAN DEFAULT FALSE
            """))
            logger.info("Added stake_commission_eligible column")
            
            db.session.commit()
            logger.info("✓ Successfully added all simple referral system columns")
            
        except Exception as e:
            logger.error(f"Error adding columns: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    add_simple_referral_columns()