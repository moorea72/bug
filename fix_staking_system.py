#!/usr/bin/env python3
"""
Fix staking system by ensuring proper database setup and validation
"""
import sys
import os
sys.path.append('.')

from app import app, db
from models import User, Coin, StakingPlan, Stake
from datetime import datetime, timedelta

def fix_staking_system():
    """Fix the staking system completely"""
    
    with app.app_context():
        print("🔧 Fixing staking system...")
        
        # Clear existing data to avoid conflicts
        print("Clearing existing data...")
        Stake.query.delete()
        StakingPlan.query.delete()
        Coin.query.delete()
        db.session.commit()
        
        # Create coins with proper data
        print("Creating coins...")
        coins_data = [
            {'symbol': 'USDT', 'name': 'Tether USD', 'min_stake': 10.0, 'icon_emoji': '💰'},
            {'symbol': 'BTC', 'name': 'Bitcoin', 'min_stake': 250.0, 'icon_emoji': '₿'},
            {'symbol': 'ETH', 'name': 'Ethereum', 'min_stake': 170.0, 'icon_emoji': '⟠'},
            {'symbol': 'BNB', 'name': 'Binance Coin', 'min_stake': 90.0, 'icon_emoji': '🟡'},
            {'symbol': 'LTC', 'name': 'Litecoin', 'min_stake': 130.0, 'icon_emoji': '🪙'}
        ]
        
        for coin_data in coins_data:
            coin = Coin(
                symbol=coin_data['symbol'],
                name=coin_data['name'],
                min_stake=coin_data['min_stake'],
                icon_emoji=coin_data['icon_emoji'],
                active=True
            )
            db.session.add(coin)
            print(f"  ✓ Added {coin_data['symbol']}: {coin_data['name']}")
        
        db.session.commit()
        
        # Create staking plans for each coin
        print("Creating staking plans...")
        coins = Coin.query.all()
        
        # Different plans for different coins
        plans_data = [
            {'duration': 7, 'rate': 0.5},
            {'duration': 15, 'rate': 0.8},
            {'duration': 30, 'rate': 1.2},
            {'duration': 90, 'rate': 1.5},
            {'duration': 120, 'rate': 1.8},
            {'duration': 180, 'rate': 2.0}
        ]
        
        for coin in coins:
            for plan_data in plans_data:
                plan = StakingPlan(
                    coin_id=coin.id,
                    duration_days=plan_data['duration'],
                    interest_rate=plan_data['rate'],
                    active=True
                )
                db.session.add(plan)
                print(f"  ✓ {coin.symbol}: {plan_data['duration']} days at {plan_data['rate']}% daily")
        
        db.session.commit()
        
        # Ensure admin user has sufficient balance
        print("Setting up admin user...")
        admin_user = User.query.filter_by(email='admin@platform.com').first()
        if admin_user:
            if admin_user.usdt_balance < 1000:
                admin_user.usdt_balance = 1000.0
                db.session.commit()
                print(f"  ✓ Admin balance set to {admin_user.usdt_balance} USDT")
            else:
                print(f"  ✓ Admin already has {admin_user.usdt_balance} USDT")
        else:
            print("  ⚠️ Admin user not found")
        
        # Final verification
        print("\n📊 Final verification:")
        print(f"  Coins: {Coin.query.count()}")
        print(f"  Staking plans: {StakingPlan.query.count()}")
        print(f"  Active stakes: {Stake.query.count()}")
        
        # Test coin-plan relationships
        print("\n🔗 Coin-Plan relationships:")
        for coin in coins:
            plans = StakingPlan.query.filter_by(coin_id=coin.id, active=True).all()
            print(f"  {coin.symbol}: {len(plans)} plans")
        
        print("\n✅ Staking system fixed successfully!")
        return True

if __name__ == "__main__":
    try:
        fix_staking_system()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)