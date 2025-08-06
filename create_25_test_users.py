#!/usr/bin/env python3
"""
Script to create 25 test users
- 20 users with 100 USDT deposit
- 5 users without deposit
"""

import os
import sys
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, Coin, Deposit

def create_test_users():
    """Create 25 test users with specified deposit amounts"""
    
    with app.app_context():
        print("🚀 Creating 25 test users...")
        
        # Get USDT coin
        usdt_coin = Coin.query.filter_by(symbol='USDT').first()
        if not usdt_coin:
            print("❌ USDT coin not found! Creating USDT coin...")
            usdt_coin = Coin(
                name='Tether USD',
                symbol='USDT',
                logo_url='https://cryptologos.cc/logos/tether-usdt-logo.png',
                min_deposit=10.0,
                is_active=True
            )
            db.session.add(usdt_coin)
            db.session.commit()
            print("✅ USDT coin created")
        
        # User data with Hindi names
        test_users_data = [
            # 20 users with 100 USDT deposit
            {'username': 'rahul_kumar', 'email': 'rahul@test.com', 'phone': '9876543201', 'deposit': 100.0},
            {'username': 'priya_sharma', 'email': 'priya@test.com', 'phone': '9876543202', 'deposit': 100.0},
            {'username': 'amit_singh', 'email': 'amit@test.com', 'phone': '9876543203', 'deposit': 100.0},
            {'username': 'neha_patel', 'email': 'neha@test.com', 'phone': '9876543204', 'deposit': 100.0},
            {'username': 'rohit_gupta', 'email': 'rohit@test.com', 'phone': '9876543205', 'deposit': 100.0},
            {'username': 'kavita_jain', 'email': 'kavita@test.com', 'phone': '9876543206', 'deposit': 100.0},
            {'username': 'suresh_yadav', 'email': 'suresh@test.com', 'phone': '9876543207', 'deposit': 100.0},
            {'username': 'pooja_agarwal', 'email': 'pooja@test.com', 'phone': '9876543208', 'deposit': 100.0},
            {'username': 'vikash_kumar', 'email': 'vikash@test.com', 'phone': '9876543209', 'deposit': 100.0},
            {'username': 'sunita_verma', 'email': 'sunita@test.com', 'phone': '9876543210', 'deposit': 100.0},
            {'username': 'rajesh_pandey', 'email': 'rajesh@test.com', 'phone': '9876543211', 'deposit': 100.0},
            {'username': 'deepika_shah', 'email': 'deepika@test.com', 'phone': '9876543212', 'deposit': 100.0},
            {'username': 'manoj_tiwari', 'email': 'manoj@test.com', 'phone': '9876543213', 'deposit': 100.0},
            {'username': 'ritu_saxena', 'email': 'ritu@test.com', 'phone': '9876543214', 'deposit': 100.0},
            {'username': 'sandeep_mishra', 'email': 'sandeep@test.com', 'phone': '9876543215', 'deposit': 100.0},
            {'username': 'anjali_srivastava', 'email': 'anjali@test.com', 'phone': '9876543216', 'deposit': 100.0},
            {'username': 'ashok_dubey', 'email': 'ashok@test.com', 'phone': '9876543217', 'deposit': 100.0},
            {'username': 'meera_tripathi', 'email': 'meera@test.com', 'phone': '9876543218', 'deposit': 100.0},
            {'username': 'dinesh_pathak', 'email': 'dinesh@test.com', 'phone': '9876543219', 'deposit': 100.0},
            {'username': 'shweta_rastogi', 'email': 'shweta@test.com', 'phone': '9876543220', 'deposit': 100.0},
            
            # 5 users without deposit
            {'username': 'arjun_mehta', 'email': 'arjun@test.com', 'phone': '9876543221', 'deposit': 0.0},
            {'username': 'sonal_bhatia', 'email': 'sonal@test.com', 'phone': '9876543222', 'deposit': 0.0},
            {'username': 'gaurav_khanna', 'email': 'gaurav@test.com', 'phone': '9876543223', 'deposit': 0.0},
            {'username': 'preeti_malhotra', 'email': 'preeti@test.com', 'phone': '9876543224', 'deposit': 0.0},
            {'username': 'ravi_kapoor', 'email': 'ravi@test.com', 'phone': '9876543225', 'deposit': 0.0},
        ]
        
        created_users = []
        created_deposits = []
        
        # Create users
        for user_data in test_users_data:
            # Check if user already exists
            existing_user = User.query.filter_by(username=user_data['username']).first()
            if existing_user:
                print(f"⚠️  User {user_data['username']} already exists, skipping...")
                continue
            
            # Create user
            new_user = User(
                username=user_data['username'],
                email=user_data['email'],
                phone_number=user_data['phone'],
                password_hash=generate_password_hash('password123'),
                usdt_balance=user_data['deposit'],
                is_active=True,
                created_at=datetime.now()
            )
            
            db.session.add(new_user)
            db.session.flush()  # To get user ID
            
            created_users.append(new_user)
            
            # Create deposit record if amount > 0
            if user_data['deposit'] > 0:
                deposit = Deposit(
                    user_id=new_user.id,
                    amount=user_data['deposit'],
                    transaction_id=f"TEST_{user_data['username'].upper()}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    status='approved',
                    blockchain_verified=True,
                    verification_details=f"Test deposit of ${user_data['deposit']} USDT for user {user_data['username']}",
                    created_at=datetime.now() - timedelta(days=1),  # Created yesterday
                    processed_at=datetime.now()
                )
                
                db.session.add(deposit)
                created_deposits.append(deposit)
        
        # Commit all changes
        db.session.commit()
        
        print(f"✅ Successfully created {len(created_users)} test users:")
        print(f"   💰 {len(created_deposits)} users with 100 USDT deposit")
        print(f"   👤 {len(created_users) - len(created_deposits)} users without deposit")
        
        # Show statistics
        print("\n📊 Created Users Summary:")
        for user in created_users:
            deposit_status = f"${user.usdt_balance} USDT" if user.usdt_balance > 0 else "No deposit"
            print(f"   {user.username} ({user.email}) - {deposit_status}")
        
        # Show total platform statistics
        total_users = User.query.count()
        total_deposits = Deposit.query.filter_by(status='approved').count()
        total_deposited = db.session.query(db.func.sum(User.usdt_balance)).scalar() or 0
        
        print(f"\n🎯 Platform Statistics:")
        print(f"   Total Users: {total_users}")
        print(f"   Total Deposits: {total_deposits}")
        print(f"   Total USDT Deposited: ${total_deposited:.2f}")
        
        return True

if __name__ == "__main__":
    try:
        success = create_test_users()
        if success:
            print("\n🎉 Test user creation completed successfully!")
        else:
            print("\n❌ Test user creation failed!")
    except Exception as e:
        print(f"\n❌ Error creating test users: {str(e)}")
        import traceback
        traceback.print_exc()