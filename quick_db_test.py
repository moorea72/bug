#!/usr/bin/env python3
"""
Quick test for database connection and setup
"""
from app import app, db
from models import User, Coin, StakingPlan
import os

def quick_test():
    """Quick database test"""
    print("Testing database connection...")
    print(f"Database URL: {os.environ.get('DATABASE_URL', 'Not set')}")
    
    try:
        with app.app_context():
            # Test database connection
            db.create_all()
            print("✓ Database connection successful!")
            
            # Check if tables exist
            tables = db.engine.table_names()
            print(f"✓ Tables found: {len(tables)}")
            
            # Check coins
            coins = Coin.query.all()
            print(f"✓ Coins in database: {len(coins)}")
            
            # Check users
            users = User.query.all()
            print(f"✓ Users in database: {len(users)}")
            
            # Check staking plans
            plans = StakingPlan.query.all()
            print(f"✓ Staking plans in database: {len(plans)}")
            
            return True
            
    except Exception as e:
        print(f"❌ Database test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = quick_test()
    if success:
        print("\n🎉 Database is working properly!")
    else:
        print("\n❌ Database has issues!")