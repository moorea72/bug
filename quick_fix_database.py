#!/usr/bin/env python3
from app import app, db
from models import Coin, StakingPlan

def quick_setup():
    with app.app_context():
        # Check if coins exist
        if Coin.query.count() == 0:
            # Create basic coins
            coins = [
                Coin(symbol='USDT', name='Tether USD', min_stake=10.0, icon_emoji='💰', active=True),
                Coin(symbol='BTC', name='Bitcoin', min_stake=250.0, icon_emoji='₿', active=True),
                Coin(symbol='ETH', name='Ethereum', min_stake=170.0, icon_emoji='⟠', active=True)
            ]
            
            for coin in coins:
                db.session.add(coin)
                
            db.session.commit()
            
            # Get the USDT coin and create plans
            usdt = Coin.query.filter_by(symbol='USDT').first()
            if usdt:
                plans = [
                    StakingPlan(coin_id=usdt.id, duration_days=7, interest_rate=0.5, active=True),
                    StakingPlan(coin_id=usdt.id, duration_days=30, interest_rate=1.2, active=True),
                    StakingPlan(coin_id=usdt.id, duration_days=90, interest_rate=1.8, active=True)
                ]
                
                for plan in plans:
                    db.session.add(plan)
                    
                db.session.commit()
                
            print("✅ Database setup completed!")
            return True
        else:
            print("ℹ️ Database already has coins")
            return True

if __name__ == "__main__":
    quick_setup()