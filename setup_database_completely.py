#!/usr/bin/env python3
"""Complete database setup for staking system"""

from app import app, db
from models import User, Coin, StakingPlan, Stake
from werkzeug.security import generate_password_hash
import sys

def setup_database():
    with app.app_context():
        try:
            print("Setting up database completely...")
            
            # Clear all staking data
            Stake.query.delete()
            StakingPlan.query.delete() 
            Coin.query.delete()
            db.session.commit()
            print("✓ Cleared existing data")
            
            # Create USDT coin
            usdt = Coin(
                symbol='USDT',
                name='Tether USD', 
                min_stake=10.0,
                icon_emoji='💰',
                active=True
            )
            db.session.add(usdt)
            db.session.commit()
            print("✓ Created USDT coin")
            
            # Create staking plans for USDT
            plans_data = [
                {'duration': 7, 'rate': 0.5},
                {'duration': 15, 'rate': 0.8}, 
                {'duration': 30, 'rate': 1.2},
                {'duration': 90, 'rate': 1.8}
            ]
            
            for plan_data in plans_data:
                plan = StakingPlan(
                    coin_id=usdt.id,
                    duration_days=plan_data['duration'],
                    interest_rate=plan_data['rate'],
                    active=True
                )
                db.session.add(plan)
                print(f"✓ Added {plan_data['duration']} day plan at {plan_data['rate']}%")
            
            db.session.commit()
            
            # Ensure admin user exists with balance
            admin = User.query.filter_by(email='admin@platform.com').first()
            if not admin:
                admin = User(
                    username='admin',
                    email='admin@platform.com',
                    phone_number='1234567890',
                    is_admin=True,
                    is_active=True
                )
                admin.set_password('admin123')
                admin.generate_referral_code()
                db.session.add(admin)
                print("✓ Created admin user")
            
            # Set admin balance
            admin.usdt_balance = 1000.0
            admin.total_staked = 0.0
            admin.total_earned = 0.0
            admin.referral_bonus = 0.0
            db.session.commit()
            print(f"✓ Set admin balance to {admin.usdt_balance} USDT")
            
            # Verify setup
            coins = Coin.query.count()
            plans = StakingPlan.query.count()
            
            print(f"\nFinal verification:")
            print(f"  Coins: {coins}")
            print(f"  Plans: {plans}")
            print(f"  Admin balance: {admin.usdt_balance}")
            
            if coins > 0 and plans > 0:
                print("\n✅ Database setup successful!")
                return True
            else:
                print("\n❌ Setup failed - missing data")
                return False
                
        except Exception as e:
            print(f"❌ Error during setup: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = setup_database()
    sys.exit(0 if success else 1)