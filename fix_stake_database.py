#!/usr/bin/env python3
"""
Fix stake page by ensuring database has coins and staking plans
"""
import sys
import os
sys.path.append('.')

from app import app, db
from models import Coin, StakingPlan, User
from models_enhanced import CoinReturnRate

def fix_stake_database():
    """Populate database with coins and staking plans for stake page"""
    
    with app.app_context():
        print("=== FIXING STAKE DATABASE ===")
        
        # Clear existing data to avoid conflicts
        print("Clearing existing data...")
        CoinReturnRate.query.delete()
        StakingPlan.query.delete()
        Coin.query.delete()
        db.session.commit()
        
        # Create coins with proper data
        coins_data = [
            {
                'symbol': 'USDT',
                'name': 'Tether USD',
                'min_stake': 10.0,
                'icon_emoji': '💰',
                'active': True
            },
            {
                'symbol': 'BTC',
                'name': 'Bitcoin',
                'min_stake': 250.0,
                'icon_emoji': '₿',
                'active': True
            },
            {
                'symbol': 'ETH',
                'name': 'Ethereum',
                'min_stake': 170.0,
                'icon_emoji': '⟠',
                'active': True
            },
            {
                'symbol': 'BNB',
                'name': 'Binance Coin',
                'min_stake': 90.0,
                'icon_emoji': '🟡',
                'active': True
            },
            {
                'symbol': 'LTC',
                'name': 'Litecoin',
                'min_stake': 130.0,
                'icon_emoji': '🪙',
                'active': True
            }
        ]
        
        print("Creating coins...")
        for coin_data in coins_data:
            coin = Coin(
                symbol=coin_data['symbol'],
                name=coin_data['name'],
                min_stake=coin_data['min_stake'],
                icon_emoji=coin_data['icon_emoji'],
                active=coin_data['active']
            )
            db.session.add(coin)
            print(f"  - Added {coin_data['symbol']}: {coin_data['name']}")
        
        db.session.commit()
        
        # Get created coins
        coins = Coin.query.all()
        coin_map = {coin.symbol: coin for coin in coins}
        
        # Create staking plans for each coin with different durations
        durations_and_rates = [
            (7, 0.5),    # 7 days, 0.5% daily
            (15, 0.8),   # 15 days, 0.8% daily  
            (30, 1.2),   # 30 days, 1.2% daily
            (90, 1.5),   # 90 days, 1.5% daily
            (120, 1.8),  # 120 days, 1.8% daily
            (180, 2.0),  # 180 days, 2.0% daily
        ]
        
        print("Creating staking plans...")
        for coin in coins:
            for duration_days, interest_rate in durations_and_rates:
                plan = StakingPlan(
                    coin_id=coin.id,
                    duration_days=duration_days,
                    interest_rate=interest_rate,
                    active=True
                )
                db.session.add(plan)
                print(f"  - {coin.symbol}: {duration_days} days at {interest_rate}% daily")
        
        db.session.commit()
        
        # Create coin return rates for enhanced management
        print("Creating coin return rates...")
        for coin in coins:
            # Set different rates based on coin type
            if coin.symbol == 'USDT':
                rates = [0.5, 0.8, 1.2, 1.5, 1.8, 2.0, 2.5]
            elif coin.symbol == 'BTC':
                rates = [0.4, 0.7, 1.0, 1.3, 1.6, 1.9, 2.2]
            elif coin.symbol == 'ETH':
                rates = [0.6, 0.9, 1.3, 1.6, 1.9, 2.2, 2.5]
            elif coin.symbol == 'BNB':
                rates = [0.7, 1.0, 1.4, 1.7, 2.0, 2.3, 2.6]
            elif coin.symbol == 'LTC':
                rates = [0.5, 0.8, 1.1, 1.4, 1.7, 2.0, 2.3]
            else:
                rates = [0.5, 0.8, 1.2, 1.5, 1.8, 2.0, 2.5]
            
            coin_rate = CoinReturnRate(
                coin_id=coin.id,
                rate_7_days=rates[0],
                rate_15_days=rates[1],
                rate_30_days=rates[2],
                rate_90_days=rates[3],
                rate_120_days=rates[4],
                rate_180_days=rates[5],
                rate_365_days=rates[6] if len(rates) > 6 else rates[5],
                is_active=True
            )
            db.session.add(coin_rate)
            print(f"  - {coin.symbol}: Rates set from {rates[0]}% to {rates[-1]}%")
        
        db.session.commit()
        
        # Verify database state
        print("\n=== VERIFICATION ===")
        coins = Coin.query.all()
        print(f"Total coins: {len(coins)}")
        
        plans = StakingPlan.query.all()
        print(f"Total staking plans: {len(plans)}")
        
        rates = CoinReturnRate.query.all()
        print(f"Total coin return rates: {len(rates)}")
        
        print("\n=== COINS DETAILS ===")
        for coin in coins:
            coin_plans = StakingPlan.query.filter_by(coin_id=coin.id, active=True).all()
            print(f"{coin.symbol} ({coin.name}): {len(coin_plans)} plans, min stake: {coin.min_stake}")
        
        print("\n✅ Database successfully populated for stake page!")
        return True

if __name__ == "__main__":
    try:
        fix_stake_database()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)