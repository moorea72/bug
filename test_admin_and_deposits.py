#!/usr/bin/env python3
"""
Test admin login and deposit system functionality
"""
from app import app, db
from models import User, Deposit
import requests

def test_admin_and_deposits():
    """Test admin login and deposit duplicate prevention"""
    
    print("Testing admin login and deposit system...")
    
    with app.app_context():
        # Test 1: Check admin user
        admin = User.query.filter_by(email='admin@platform.com').first()
        if admin:
            print(f"✓ Admin user exists: {admin.email}")
            print(f"  - Username: {admin.username}")
            print(f"  - Is Admin: {admin.is_admin}")
            print(f"  - Is Active: {admin.is_active}")
            
            # Test password
            password_test = admin.check_password('admin123')
            print(f"  - Password check: {password_test}")
        else:
            print("❌ Admin user not found")
        
        # Test 2: Check deposit duplicate prevention
        print("\nChecking deposit system...")
        
        # Get all deposits
        deposits = Deposit.query.all()
        print(f"✓ Total deposits: {len(deposits)}")
        
        # Check for duplicates
        transaction_ids = [d.transaction_id for d in deposits]
        unique_ids = set(transaction_ids)
        
        if len(transaction_ids) == len(unique_ids):
            print("✓ No duplicate transaction IDs found")
        else:
            duplicates = [tid for tid in unique_ids if transaction_ids.count(tid) > 1]
            print(f"⚠️  Duplicate transaction IDs: {duplicates}")
        
        # Test 3: Check recent activity
        verified_deposits = Deposit.query.filter_by(status='verified').count()
        rejected_deposits = Deposit.query.filter_by(status='rejected').count()
        pending_deposits = Deposit.query.filter_by(status='pending').count()
        
        print(f"✓ Verified deposits: {verified_deposits}")
        print(f"✓ Rejected deposits: {rejected_deposits}")
        print(f"✓ Pending deposits: {pending_deposits}")
        
        # Test 4: Admin credentials summary
        print("\n🔑 Admin Login Information:")
        print("Email: admin@platform.com")
        print("Password: admin123")
        print("Login URL: http://localhost:5000/login")
        
        return True

if __name__ == "__main__":
    test_admin_and_deposits()