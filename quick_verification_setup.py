"""
Quick verification setup - create test data for comprehensive testing
"""
from app import app, db
from models import *
from werkzeug.security import generate_password_hash
import random
from datetime import datetime, timedelta

def setup_verification_data():
    with app.app_context():
        print("Setting up verification data...")
        
        # Ensure admin exists
        admin = User.query.filter_by(email='admin@platform.com').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@platform.com',
                password_hash=generate_password_hash('admin123'),
                phone_number='1234567890',
                is_admin=True,
                referral_code='ADMIN',
                usdt_balance=10000.0
            )
            db.session.add(admin)
            db.session.commit()
        
        # Delete existing non-admin users
        User.query.filter_by(is_admin=False).delete()
        db.session.commit()
        
        # Create 10 test users quickly
        for i in range(10):
            user = User(
                username=f'user{i+1}',
                email=f'user{i+1}@test.com',
                password_hash=generate_password_hash('user123'),
                phone_number=f'987654321{i}',
                referral_code=f'REF{1000+i}',
                referred_by=admin.id,
                usdt_balance=random.randint(100, 1000),
                first_deposit_completed=True
            )
            db.session.add(user)
        
        db.session.commit()
        print("✅ Created 10 test users with admin referral")
        
        # Verify
        user_count = User.query.filter_by(is_admin=False).count()
        referral_count = User.query.filter_by(referred_by=admin.id).count()
        
        print(f"Total users: {user_count}")
        print(f"Admin referrals: {referral_count}")
        print("Ready for testing!")

if __name__ == '__main__':
    setup_verification_data()