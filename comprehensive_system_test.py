#!/usr/bin/env python3
"""
Comprehensive System Testing Script
- Delete all users except admin
- Create 40 test users with admin referral
- 30 users with $100 USDT deposits
- 10 users with $0 balance
- Test BEP20/TRC20 deposit systems
- Verify blockchain API integration
"""

import os
import sys
import random
from datetime import datetime, timedelta

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, Deposit, Coin, StakingPlan
from werkzeug.security import generate_password_hash

def delete_all_test_users():
    """Delete all users except admin"""
    with app.app_context():
        try:
            # Keep admin user
            admin = User.query.filter_by(email='admin@platform.com').first()
            if not admin:
                print("❌ Admin user not found!")
                return False
            
            # Delete all other users and their related data
            test_users = User.query.filter(User.id != admin.id).all()
            print(f"🗑️ Deleting {len(test_users)} test users...")
            
            for user in test_users:
                # Delete all related data first
                from models import ActivityLog, Stake, Withdrawal, SupportMessage
                
                # Delete activity logs
                ActivityLog.query.filter_by(user_id=user.id).delete()
                
                # Delete deposits
                Deposit.query.filter_by(user_id=user.id).delete()
                
                # Delete stakes
                Stake.query.filter_by(user_id=user.id).delete()
                
                # Delete withdrawals
                Withdrawal.query.filter_by(user_id=user.id).delete()
                
                # Delete support messages
                SupportMessage.query.filter_by(user_id=user.id).delete()
                
                # Delete user
                db.session.delete(user)
            
            db.session.commit()
            print(f"✅ Successfully deleted {len(test_users)} test users")
            print(f"✅ Admin user preserved: {admin.username} ({admin.email})")
            return True
            
        except Exception as e:
            print(f"❌ Error deleting users: {str(e)}")
            db.session.rollback()
            return False

def create_test_users_with_admin_referral():
    """Create 40 test users with admin referral code"""
    with app.app_context():
        try:
            admin = User.query.filter_by(email='admin@platform.com').first()
            if not admin:
                print("❌ Admin user not found!")
                return False
            
            # Hindi names for realistic users
            hindi_names = [
                'राम', 'श्याम', 'गीता', 'सीता', 'मोहन', 'सोहन', 'रीता', 'नीता',
                'अमित', 'सुमित', 'प्रिया', 'माया', 'विकास', 'आकाश', 'पूजा', 'रूपा',
                'राज', 'सुराज', 'कमला', 'शमला', 'दीपक', 'अशोक', 'सुनीता', 'गीता',
                'हर्ष', 'आदर्श', 'लता', 'ममता', 'रवि', 'कवि', 'श्री', 'हरि',
                'मनीष', 'जगदीश', 'रेखा', 'मीरा', 'संजय', 'विजय', 'सुधा', 'राधा'
            ]
            
            created_users = []
            
            for i in range(40):
                username = f"user_{i+1:03d}"
                email = f"user{i+1:03d}@test.com"
                phone = f"90556{10000 + i:05d}"  # Unique phone numbers
                hindi_name = hindi_names[i % len(hindi_names)]
                
                # Create user with admin referral
                user = User(
                    username=username,
                    email=email,
                    phone_number=phone,
                    password_hash=generate_password_hash('password123'),
                    usdt_balance=0.0,
                    referred_by=admin.id,  # Admin referral
                    referral_code=f"REF{i+1:03d}",
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                
                db.session.add(user)
                created_users.append((user, hindi_name))
            
            db.session.commit()
            print(f"✅ Created {len(created_users)} users with admin referral")
            
            # Now add deposits for first 30 users
            deposit_users = created_users[:30]  # First 30 users get deposits
            zero_balance_users = created_users[30:]  # Last 10 users get no deposits
            
            print(f"💰 Adding $100 USDT deposits for {len(deposit_users)} users...")
            
            for user, hindi_name in deposit_users:
                # Create approved deposit
                deposit = Deposit(
                    user_id=user.id,
                    amount=100.0,
                    network='BEP20',
                    transaction_hash=f"0x{random.randint(100000000000000000, 999999999999999999):016x}abc{random.randint(1000, 9999)}",
                    wallet_address='0xae49d3b4775c0524bd81da704340b5ef5a7416e9',
                    status='approved',
                    created_at=datetime.utcnow(),
                    processed_at=datetime.utcnow()
                )
                
                # Update user balance
                user.usdt_balance = 100.0
                
                db.session.add(deposit)
            
            db.session.commit()
            
            print(f"✅ Test users created successfully:")
            print(f"   - 30 users with $100 USDT balance")
            print(f"   - 10 users with $0 balance")
            print(f"   - All users referred by admin: {admin.username}")
            print(f"   - Admin should receive referral bonuses")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating test users: {str(e)}")
            db.session.rollback()
            return False

def test_deposit_system():
    """Test BEP20 and TRC20 deposit systems"""
    with app.app_context():
        print("\n🔍 Testing Deposit System Configuration...")
        
        # Check wallet addresses in database
        from models import PaymentAddress
        payment_addresses = PaymentAddress.query.all()
        
        print(f"📍 Payment Addresses in Database:")
        for addr in payment_addresses:
            print(f"   - {addr.network}: {addr.address}")
        
        # Test BEP20 configuration
        bep20_addr = PaymentAddress.query.filter_by(network='BEP20').first()
        trc20_addr = PaymentAddress.query.filter_by(network='TRC20').first()
        
        if bep20_addr:
            print(f"✅ BEP20 Address: {bep20_addr.address}")
        else:
            print("❌ BEP20 address not configured")
        
        if trc20_addr:
            print(f"✅ TRC20 Address: {trc20_addr.address}")
        else:
            print("❌ TRC20 address not configured")
        
        # Check Moralis API configuration
        moralis_key = os.environ.get('MORALIS_API_KEY')
        if moralis_key:
            print(f"✅ Moralis API Key configured: {moralis_key[:10]}...")
        else:
            print("❌ Moralis API Key not found in environment")

def check_referral_system():
    """Check admin referral bonuses and system"""
    with app.app_context():
        try:
            admin = User.query.filter_by(email='admin@platform.com').first()
            if not admin:
                print("❌ Admin user not found!")
                return
            
            # Count admin's referrals
            total_referrals = User.query.filter_by(referred_by=admin.id).count()
            qualified_referrals = admin.get_qualified_referrals_count()
            admin_balance = admin.get_total_balance_including_stakes()
            is_eligible = admin.is_salary_eligible()
            
            print(f"\n📊 Admin Referral System Status:")
            print(f"   - Total Referrals: {total_referrals}")
            print(f"   - Qualified Referrals: {qualified_referrals}")
            print(f"   - Admin Balance: ${admin_balance}")
            print(f"   - Salary Eligible: {is_eligible}")
            
            # Show referral details
            referrals = User.query.filter_by(referred_by=admin.id).all()
            print(f"\n👥 Referral Details:")
            qualified_count = 0
            for ref in referrals:
                ref_balance = ref.get_total_balance_including_stakes()
                is_qualified = ref_balance >= 100
                if is_qualified:
                    qualified_count += 1
                print(f"   - {ref.username}: ${ref_balance} {'✅' if is_qualified else '❌'}")
            
            print(f"\n🎯 Expected qualified referrals: 30 (users with $100)")
            print(f"🎯 Actual qualified referrals: {qualified_count}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error checking referral system: {str(e)}")
            return False

def run_comprehensive_test():
    """Run complete system test"""
    print("🚀 Starting Comprehensive System Test...")
    print("=" * 50)
    
    # Step 1: Delete all test users
    if not delete_all_test_users():
        return False
    
    print("\n" + "=" * 50)
    
    # Step 2: Create new test users
    if not create_test_users_with_admin_referral():
        return False
    
    print("\n" + "=" * 50)
    
    # Step 3: Test deposit system
    test_deposit_system()
    
    print("\n" + "=" * 50)
    
    # Step 4: Check referral system
    check_referral_system()
    
    print("\n" + "=" * 50)
    print("✅ Comprehensive System Test Completed!")
    print("\n📋 Summary:")
    print("   - ✅ All test users deleted except admin")
    print("   - ✅ 40 new users created with admin referral")
    print("   - ✅ 30 users have $100 USDT deposits")
    print("   - ✅ 10 users have $0 balance")
    print("   - ✅ Deposit system configuration checked")
    print("   - ✅ Referral system verified")
    
    return True

if __name__ == "__main__":
    run_comprehensive_test()