#!/usr/bin/env python3
"""
Script to delete recently created test users and create 25 new users with admin referral
- 20 users with 100 USDT deposit
- 5 users without deposit
- All users referred by admin
"""

import os
import sys
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, Coin, Deposit

def delete_test_users_and_create_with_admin_referral():
    """Delete test users and create 25 new users with admin referral"""
    
    with app.app_context():
        print("🚀 Deleting test users and creating 25 new users with admin referral...")
        
        # Get admin user
        admin_user = User.query.filter_by(is_admin=True).first()
        if not admin_user:
            print("❌ Admin user not found!")
            return False
        
        print(f"✅ Found admin user: {admin_user.username} (ID: {admin_user.id})")
        print(f"✅ Admin referral code: {admin_user.referral_code}")
        
        # Delete recently created test users (created today)
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Find test users created today
        test_users = User.query.filter(
            User.created_at >= today_start,
            User.is_admin == False
        ).all()
        
        print(f"🗑️ Found {len(test_users)} test users to delete...")
        
        # Delete their deposits first
        for user in test_users:
            deposits = Deposit.query.filter_by(user_id=user.id).all()
            for deposit in deposits:
                db.session.delete(deposit)
            print(f"   Deleted user: {user.username}")
            db.session.delete(user)
        
        db.session.commit()
        print("✅ Test users deleted successfully")
        
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
        
        # User data with Hindi names - all will be referred by admin
        test_users_data = [
            # 20 users with 100 USDT deposit
            {'username': 'rahul_singh', 'email': 'rahul.singh@test.com', 'phone': '9876543301', 'deposit': 100.0},
            {'username': 'priya_kumari', 'email': 'priya.kumari@test.com', 'phone': '9876543302', 'deposit': 100.0},
            {'username': 'amit_sharma', 'email': 'amit.sharma@test.com', 'phone': '9876543303', 'deposit': 100.0},
            {'username': 'neha_gupta', 'email': 'neha.gupta@test.com', 'phone': '9876543304', 'deposit': 100.0},
            {'username': 'rohit_patel', 'email': 'rohit.patel@test.com', 'phone': '9876543305', 'deposit': 100.0},
            {'username': 'kavita_yadav', 'email': 'kavita.yadav@test.com', 'phone': '9876543306', 'deposit': 100.0},
            {'username': 'suresh_kumar', 'email': 'suresh.kumar@test.com', 'phone': '9876543307', 'deposit': 100.0},
            {'username': 'pooja_singh', 'email': 'pooja.singh@test.com', 'phone': '9876543308', 'deposit': 100.0},
            {'username': 'vikash_gupta', 'email': 'vikash.gupta@test.com', 'phone': '9876543309', 'deposit': 100.0},
            {'username': 'sunita_sharma', 'email': 'sunita.sharma@test.com', 'phone': '9876543310', 'deposit': 100.0},
            {'username': 'rajesh_kumar', 'email': 'rajesh.kumar@test.com', 'phone': '9876543311', 'deposit': 100.0},
            {'username': 'deepika_patel', 'email': 'deepika.patel@test.com', 'phone': '9876543312', 'deposit': 100.0},
            {'username': 'manoj_singh', 'email': 'manoj.singh@test.com', 'phone': '9876543313', 'deposit': 100.0},
            {'username': 'ritu_kumari', 'email': 'ritu.kumari@test.com', 'phone': '9876543314', 'deposit': 100.0},
            {'username': 'sandeep_gupta', 'email': 'sandeep.gupta@test.com', 'phone': '9876543315', 'deposit': 100.0},
            {'username': 'anjali_sharma', 'email': 'anjali.sharma@test.com', 'phone': '9876543316', 'deposit': 100.0},
            {'username': 'ashok_kumar', 'email': 'ashok.kumar@test.com', 'phone': '9876543317', 'deposit': 100.0},
            {'username': 'meera_singh', 'email': 'meera.singh@test.com', 'phone': '9876543318', 'deposit': 100.0},
            {'username': 'dinesh_patel', 'email': 'dinesh.patel@test.com', 'phone': '9876543319', 'deposit': 100.0},
            {'username': 'shweta_gupta', 'email': 'shweta.gupta@test.com', 'phone': '9876543320', 'deposit': 100.0},
            
            # 5 users without deposit
            {'username': 'arjun_singh', 'email': 'arjun.singh@test.com', 'phone': '9876543321', 'deposit': 0.0},
            {'username': 'sonal_kumari', 'email': 'sonal.kumari@test.com', 'phone': '9876543322', 'deposit': 0.0},
            {'username': 'gaurav_sharma', 'email': 'gaurav.sharma@test.com', 'phone': '9876543323', 'deposit': 0.0},
            {'username': 'preeti_patel', 'email': 'preeti.patel@test.com', 'phone': '9876543324', 'deposit': 0.0},
            {'username': 'ravi_gupta', 'email': 'ravi.gupta@test.com', 'phone': '9876543325', 'deposit': 0.0},
        ]
        
        created_users = []
        created_deposits = []
        
        # Create users with admin referral
        for user_data in test_users_data:
            # Create user with admin referral
            new_user = User(
                username=user_data['username'],
                email=user_data['email'],
                phone_number=user_data['phone'],
                password_hash=generate_password_hash('password123'),
                usdt_balance=user_data['deposit'],
                referred_by=admin_user.id,  # All users referred by admin
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
                    transaction_id=f"ADMIN_REF_{user_data['username'].upper()}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    status='approved',
                    blockchain_verified=True,
                    verification_details=f"Test deposit of ${user_data['deposit']} USDT for admin referral {user_data['username']}",
                    created_at=datetime.now() - timedelta(days=1),  # Created yesterday
                    processed_at=datetime.now()
                )
                
                db.session.add(deposit)
                created_deposits.append(deposit)
        
        # Update admin's referral bonus (each referral = 5 USDT commission)
        admin_user.referral_bonus += len(created_users) * 5.0
        admin_user.usdt_balance += len(created_users) * 5.0
        
        # Commit all changes
        db.session.commit()
        
        print(f"✅ Successfully created {len(created_users)} users with admin referral:")
        print(f"   💰 {len(created_deposits)} users with 100 USDT deposit")
        print(f"   👤 {len(created_users) - len(created_deposits)} users without deposit")
        print(f"   🎯 Admin referral bonus: ${len(created_users) * 5.0} USDT")
        
        # Show admin referral statistics
        total_admin_referrals = User.query.filter_by(referred_by=admin_user.id).count()
        print(f"   📊 Total admin referrals: {total_admin_referrals}")
        
        # Show statistics
        print("\n📊 Created Users Summary:")
        for user in created_users:
            deposit_status = f"${user.usdt_balance} USDT" if user.usdt_balance > 0 else "No deposit"
            print(f"   {user.username} ({user.email}) - {deposit_status} - Referred by Admin")
        
        # Show total platform statistics
        total_users = User.query.count()
        total_deposits = Deposit.query.filter_by(status='approved').count()
        total_deposited = db.session.query(db.func.sum(User.usdt_balance)).scalar() or 0
        
        print(f"\n🎯 Platform Statistics:")
        print(f"   Total Users: {total_users}")
        print(f"   Total Approved Deposits: {total_deposits}")
        print(f"   Total USDT in Platform: ${total_deposited:.2f}")
        print(f"   Admin Balance: ${admin_user.usdt_balance:.2f}")
        print(f"   Admin Referral Bonus: ${admin_user.referral_bonus:.2f}")
        
        return True

if __name__ == "__main__":
    try:
        success = delete_test_users_and_create_with_admin_referral()
        if success:
            print("\n🎉 User creation with admin referral completed successfully!")
        else:
            print("\n❌ User creation failed!")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()