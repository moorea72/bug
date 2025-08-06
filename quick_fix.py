#!/usr/bin/env python3
"""Quick fix for staking and deposit issues"""

import os
import sys
from datetime import datetime

# Add the current directory to the path to import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app, db
    from models import User, Coin, StakingPlan
    print("✓ Modules imported successfully")
    
    with app.app_context():
        # Test database connection
        try:
            coin_count = Coin.query.count()
            plan_count = StakingPlan.query.count()
            user_count = User.query.count()
            print(f"Database status: {coin_count} coins, {plan_count} plans, {user_count} users")
            
            # If no coins, add basic ones
            if coin_count == 0:
                print("Adding basic coins...")
                coins = [
                    Coin(symbol='USDT', name='Tether USD', min_stake=10.0, active=True, icon_emoji='💰'),
                    Coin(symbol='BTC', name='Bitcoin', min_stake=250.0, active=True, icon_emoji='₿'),
                    Coin(symbol='ETH', name='Ethereum', min_stake=170.0, active=True, icon_emoji='⧫'),
                    Coin(symbol='BNB', name='Binance Coin', min_stake=90.0, active=True, icon_emoji='🔸'),
                    Coin(symbol='LTC', name='Litecoin', min_stake=130.0, active=True, icon_emoji='Ł')
                ]
                for coin in coins:
                    db.session.add(coin)
                db.session.commit()
                print("✓ Coins added")
            
            # If no plans, add basic ones
            if plan_count == 0:
                print("Adding staking plans...")
                coins = Coin.query.all()
                for coin in coins:
                    plans = [
                        StakingPlan(coin_id=coin.id, duration_days=7, interest_rate=0.8, active=True),
                        StakingPlan(coin_id=coin.id, duration_days=15, interest_rate=1.2, active=True),
                        StakingPlan(coin_id=coin.id, duration_days=30, interest_rate=1.5, active=True),
                        StakingPlan(coin_id=coin.id, duration_days=90, interest_rate=1.8, active=True),
                        StakingPlan(coin_id=coin.id, duration_days=120, interest_rate=2.0, active=True),
                        StakingPlan(coin_id=coin.id, duration_days=180, interest_rate=2.2, active=True)
                    ]
                    for plan in plans:
                        db.session.add(plan)
                db.session.commit()
                print("✓ Plans added")
            
            # Final count
            final_coins = Coin.query.count()
            final_plans = StakingPlan.query.count()
            print(f"Final status: {final_coins} coins, {final_plans} plans")
            
        except Exception as e:
            print(f"Database error: {e}")
            import traceback
            traceback.print_exc()
            
except Exception as e:
    print(f"Import error: {e}")
    import traceback
    traceback.print_exc()