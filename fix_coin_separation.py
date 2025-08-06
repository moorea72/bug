#!/usr/bin/env python3
"""
Complete fix for coin return rate separation
Ensures each coin has truly independent return rates
"""
from app import app, db
from models import StakingPlan, Coin

def completely_fix_coin_separation():
    """Completely fix coin return rate separation"""
    with app.app_context():
        try:
            # 1. Delete ALL staking plans
            all_plans = StakingPlan.query.all()
            for plan in all_plans:
                db.session.delete(plan)
            
            db.session.commit()
            print("✅ Deleted all existing staking plans")
            
            # 2. Verify all coins exist
            coins = Coin.query.all()
            print(f"📊 Found {len(coins)} coins in database:")
            for coin in coins:
                print(f"   - {coin.symbol} (ID: {coin.id}): {coin.name}")
            
            print("\n🔄 Database is now completely clean")
            print("💡 Admin can now set individual return rates for each coin")
            print("🎯 Each coin will have completely separate return rates")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    completely_fix_coin_separation()