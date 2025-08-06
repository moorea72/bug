#!/usr/bin/env python3
"""
Script to populate the database with coins and staking plans
"""
import os
import sys
from app import app, db
from models import Coin, StakingPlan, User
from models_enhanced import CoinReturnRate

def populate_coins():
    """Add coins to the database"""
    
    # Check if coins already exist
    if Coin.query.count() > 0:
        print("Coins already exist in database")
        return
    
    coins_data = [
        {"symbol": "USDT", "name": "Tether USD", "min_stake": 10, "icon_emoji": "💰"},
        {"symbol": "BTC", "name": "Bitcoin", "min_stake": 250, "icon_emoji": "₿"},
        {"symbol": "ETH", "name": "Ethereum", "min_stake": 170, "icon_emoji": "Ξ"},
        {"symbol": "BNB", "name": "Binance Coin", "min_stake": 90, "icon_emoji": "🟡"},
        {"symbol": "LTC", "name": "Litecoin", "min_stake": 130, "icon_emoji": "Ł"},
    ]
    
    for coin_data in coins_data:
        coin = Coin(**coin_data)
        db.session.add(coin)
    
    db.session.commit()
    print("Coins added successfully")

def populate_staking_plans():
    """Add staking plans for each coin"""
    
    # Check if staking plans already exist
    if StakingPlan.query.count() > 0:
        print("Staking plans already exist in database")
        return
    
    coins = Coin.query.all()
    
    # Staking durations and default rates
    plans_data = [
        {"duration_days": 7, "interest_rate": 0.5},
        {"duration_days": 15, "interest_rate": 0.8},
        {"duration_days": 30, "interest_rate": 1.2},
        {"duration_days": 90, "interest_rate": 1.6},
        {"duration_days": 120, "interest_rate": 1.8},
        {"duration_days": 180, "interest_rate": 2.0},
    ]
    
    for coin in coins:
        for plan_data in plans_data:
            plan = StakingPlan(
                coin_id=coin.id,
                duration_days=plan_data["duration_days"],
                interest_rate=plan_data["interest_rate"]
            )
            db.session.add(plan)
    
    db.session.commit()
    print("Staking plans added successfully")

def create_admin_user():
    """Create admin user if doesn't exist"""
    
    admin = User.query.filter_by(email='admin@platform.com').first()
    if admin:
        print("Admin user already exists")
        return
    
    admin = User(
        username='admin',
        email='admin@platform.com',
        phone_number='+1234567890',
        is_admin=True,
        usdt_balance=10000.0  # Give admin some balance for testing
    )
    admin.set_password('admin123')
    
    db.session.add(admin)
    db.session.commit()
    print("Admin user created successfully")

if __name__ == "__main__":
    with app.app_context():
        print("Populating database...")
        populate_coins()
        populate_staking_plans()
        create_admin_user()
        print("Database populated successfully!")
        
        # Show current coins
        coins = Coin.query.all()
        print(f"Total coins: {len(coins)}")
        for coin in coins:
            print(f"- {coin.symbol}: {coin.name} (min: {coin.min_stake})")
        
        # Show total staking plans
        plans = StakingPlan.query.all()
        print(f"Total staking plans: {len(plans)}")