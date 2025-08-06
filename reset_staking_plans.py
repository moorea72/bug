#!/usr/bin/env python3
"""
Reset staking plans database - Remove all coin-specific staking plans
This fixes the duplicate return rates issue
"""
from app import app, db
from models import StakingPlan

def reset_coin_staking_plans():
    """Remove all coin-specific staking plans to fix duplicates"""
    with app.app_context():
        try:
            # Delete all coin-specific staking plans (where coin_id is not None)
            deleted_count = StakingPlan.query.filter(StakingPlan.coin_id.isnot(None)).delete()
            db.session.commit()
            
            print(f"✅ Successfully deleted {deleted_count} coin-specific staking plans")
            print("🔄 Admin can now set fresh return rates for each coin individually")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error resetting staking plans: {str(e)}")

if __name__ == "__main__":
    reset_coin_staking_plans()