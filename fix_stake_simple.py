#!/usr/bin/env python3
"""
Simple fix for stake functionality
"""
import sys
import os
sys.path.append('.')

from app import app, db
from models import User, Coin, StakingPlan, Stake
from datetime import datetime, timedelta

def fix_stake_simple():
    """Fix stake functionality with simple setup"""
    
    with app.app_context():
        print("🔧 Fixing stake functionality...")
        
        # Clear existing conflicting data
        print("Clearing existing data...")
        Stake.query.delete()
        StakingPlan.query.delete() 
        Coin.query.delete()
        db.session.commit()
        
        # Create basic coins
        print("Creating coins...")
        coins_data = [
            {'symbol': 'USDT', 'name': 'Tether USD', 'min_stake': 10.0, 'icon_emoji': '💰'},
            {'symbol': 'BTC', 'name': 'Bitcoin', 'min_stake': 250.0, 'icon_emoji': '₿'},
            {'symbol': 'ETH', 'name': 'Ethereum', 'min_stake': 170.0, 'icon_emoji': '⟠'},
            {'symbol': 'BNB', 'name': 'Binance Coin', 'min_stake': 90.0, 'icon_emoji': '🟡'},
            {'symbol': 'LTC', 'name': 'Litecoin', 'min_stake': 130.0, 'icon_emoji': '🪙'}
        ]
        
        created_coins = []
        for coin_data in coins_data:
            coin = Coin(
                symbol=coin_data['symbol'],
                name=coin_data['name'],
                min_stake=coin_data['min_stake'],
                icon_emoji=coin_data['icon_emoji'],
                active=True
            )
            db.session.add(coin)
            created_coins.append(coin)
            print(f"  ✓ Added {coin_data['symbol']}")
        
        db.session.commit()
        
        # Get coin IDs after commit
        coins = Coin.query.all()
        
        # Create staking plans for each coin
        print("Creating staking plans...")
        plan_durations = [
            (7, 0.5),    # 7 days, 0.5% daily
            (15, 0.8),   # 15 days, 0.8% daily
            (30, 1.2),   # 30 days, 1.2% daily
            (90, 1.5),   # 90 days, 1.5% daily
            (120, 1.8),  # 120 days, 1.8% daily
            (180, 2.0),  # 180 days, 2.0% daily
        ]
        
        for coin in coins:
            for duration, rate in plan_durations:
                plan = StakingPlan(
                    coin_id=coin.id,
                    duration_days=duration,
                    interest_rate=rate,
                    active=True
                )
                db.session.add(plan)
                print(f"  ✓ {coin.symbol}: {duration} days at {rate}% daily")
        
        db.session.commit()
        
        # Ensure admin user has balance
        print("Setting up admin user...")
        admin_user = User.query.filter_by(email='admin@platform.com').first()
        if admin_user:
            admin_user.usdt_balance = 10000.0
            db.session.commit()
            print(f"  ✓ Admin balance set to $10,000")
        
        # Show summary
        coin_count = Coin.query.count()
        plan_count = StakingPlan.query.count()
        print(f"\n✅ Setup complete!")
        print(f"   - Coins: {coin_count}")
        print(f"   - Staking Plans: {plan_count}")
        print(f"   - Admin balance updated")
        
        return True

if __name__ == '__main__':
    fix_stake_simple()