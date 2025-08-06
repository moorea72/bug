#!/usr/bin/env python3
"""
Simple test to create admin referral users
"""

from app import app, db
from models import User, Deposit
import uuid
import random

with app.app_context():
    # Get admin user
    admin = User.query.filter_by(email='admin@platform.com').first()
    
    if not admin:
        print("Admin user not found")
        exit()
    
    print(f"Admin user found: {admin.username}")
    print(f"Admin referral code: {admin.referral_code}")
    
    # Create 5 test users first
    for i in range(1, 6):
        username = f'testref{i:02d}'
        email = f'testref{i:02d}@test.com'
        phone = f'+155500{i:02d}'
        
        # Check if user exists
        existing = User.query.filter_by(username=username).first()
        if existing:
            print(f"User {username} already exists")
            continue
        
        # Create user
        user = User(
            username=username,
            email=email,
            phone_number=phone,
            is_admin=False,
            is_active=True,
            usdt_balance=500.0,
            referred_by=admin.id,
            referral_code=str(uuid.uuid4())[:8].upper()
        )
        user.set_password('test123')
        db.session.add(user)
        db.session.flush()
        
        print(f"Created user: {username} with ID: {user.id}")
        
        # Create deposit
        deposit = Deposit(
            user_id=user.id,
            amount=100.0,
            transaction_id=f'TEST{i:02d}',
            status='approved',
            blockchain_verified=True
        )
        db.session.add(deposit)
        print(f"Created deposit for {username}")
    
    db.session.commit()
    print("All users created successfully")
    
    # Check final referral count
    referral_count = User.query.filter_by(referred_by=admin.id).count()
    print(f"Admin now has {referral_count} referrals")