#!/usr/bin/env python3
"""Quick user cleanup and creation"""

import os
import sys
import random
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, Deposit
from werkzeug.security import generate_password_hash

def quick_cleanup_and_create():
    with app.app_context():
        try:
            # Find admin
            admin = User.query.filter_by(email='admin@platform.com').first()
            if not admin:
                print("Admin not found!")
                return False
            
            print(f"Admin found: {admin.username}")
            
            # Count existing users
            all_users = User.query.all()
            test_users = [u for u in all_users if u.id != admin.id]
            print(f"Found {len(test_users)} test users to delete")
            
            # Simple deletion using raw SQL to avoid FK constraints
            if test_users:
                # Get user IDs
                user_ids = [str(u.id) for u in test_users]
                user_ids_str = ','.join(user_ids)
                
                # Delete related data first
                from sqlalchemy import text
                db.session.execute(text(f"DELETE FROM activity_log WHERE user_id IN ({user_ids_str})"))
                db.session.execute(text(f"DELETE FROM deposit WHERE user_id IN ({user_ids_str})"))
                db.session.execute(text(f"DELETE FROM stake WHERE user_id IN ({user_ids_str})"))
                db.session.execute(text(f"DELETE FROM withdrawal WHERE user_id IN ({user_ids_str})"))
                db.session.execute(text(f"DELETE FROM support_message WHERE user_id IN ({user_ids_str})"))
                
                # Delete users
                db.session.execute(text(f"DELETE FROM \"user\" WHERE id IN ({user_ids_str})"))
                
                db.session.commit()
                print(f"Deleted {len(test_users)} users successfully")
            
            # Create 40 new users
            print("Creating 40 new test users...")
            
            for i in range(40):
                username = f"testuser_{i+1:03d}"
                email = f"test{i+1:03d}@example.com"
                phone = f"90556{20000 + i:05d}"
                
                user = User(
                    username=username,
                    email=email,
                    phone_number=phone,
                    password_hash=generate_password_hash('password123'),
                    usdt_balance=100.0 if i < 30 else 0.0,  # First 30 get $100
                    referred_by=admin.id,
                    referral_code=f"TEST{i+1:03d}",
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                
                db.session.add(user)
                
                # Add deposit for first 30 users
                if i < 30:
                    deposit = Deposit(
                        user_id=user.id,
                        amount=100.0,
                        network='BEP20',
                        transaction_hash=f"0x{random.randint(100000000000000000, 999999999999999999):016x}",
                        wallet_address='0xae49d3b4775c0524bd81da704340b5ef5a7416e9',
                        status='approved',
                        created_at=datetime.utcnow(),
                        processed_at=datetime.utcnow()
                    )
                    db.session.add(deposit)
            
            db.session.commit()
            
            # Verify results
            total_users = User.query.count()
            admin_referrals = User.query.filter_by(referred_by=admin.id).count()
            
            print(f"✅ Success!")
            print(f"Total users: {total_users}")
            print(f"Admin referrals: {admin_referrals}")
            print(f"Admin qualified referrals: {admin.get_qualified_referrals_count()}")
            
            return True
            
        except Exception as e:
            print(f"Error: {str(e)}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    quick_cleanup_and_create()