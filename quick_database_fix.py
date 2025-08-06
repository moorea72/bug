#!/usr/bin/env python3
"""Quick database fix for staking system"""
import sys
import os
sys.path.append('.')

try:
    from app import app, db
    from models import User, Coin, StakingPlan

    with app.app_context():
        print("Fixing database...")
        
        # Delete existing coins and plans
        StakingPlan.query.delete()
        Coin.query.delete()
        db.session.commit()
        
        # Add USDT coin
        usdt = Coin(
            symbol='USDT',
            name='Tether USD',
            min_stake=10.0,
            icon_emoji='💰',
            active=True
        )
        db.session.add(usdt)
        db.session.commit()
        
        # Add USDT plans
        plans = [
            StakingPlan(coin_id=usdt.id, duration_days=7, interest_rate=0.5, active=True),
            StakingPlan(coin_id=usdt.id, duration_days=30, interest_rate=1.2, active=True),
            StakingPlan(coin_id=usdt.id, duration_days=90, interest_rate=1.8, active=True)
        ]
        for plan in plans:
            db.session.add(plan)
        db.session.commit()
        
        # Set admin balance
        admin = User.query.filter_by(email='admin@platform.com').first()
        if admin:
            admin.usdt_balance = 1000.0
            db.session.commit()
        
        print("Database setup complete!")
        print(f"Coins: {Coin.query.count()}")
        print(f"Plans: {StakingPlan.query.count()}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()