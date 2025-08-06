#!/usr/bin/env python3
"""
Fix admin password and check deposit system
"""
from app import app, db
from models import User, Deposit
from werkzeug.security import generate_password_hash

def fix_admin_password():
    """Fix admin password and check user"""
    
    with app.app_context():
        print("Checking admin user...")
        
        # Find admin user
        admin = User.query.filter_by(email='admin@platform.com').first()
        
        if admin:
            print(f"✓ Admin user found: {admin.username} ({admin.email})")
            print(f"  - Is Admin: {admin.is_admin}")
            print(f"  - Is Active: {admin.is_active}")
            
            # Reset password to admin123
            admin.set_password('admin123')
            db.session.commit()
            print("✓ Admin password reset to: admin123")
            
        else:
            print("❌ Admin user not found. Creating new admin...")
            
            # Create new admin user
            admin = User(
                username='admin',
                email='admin@platform.com',
                phone_number='+1234567890',
                is_admin=True,
                is_active=True,
                usdt_balance=10000.0
            )
            admin.set_password('admin123')
            
            db.session.add(admin)
            db.session.commit()
            print("✓ New admin user created")
        
        # Check duplicate transaction IDs in deposits
        print("\nChecking deposit system...")
        
        # Get all deposits with their transaction IDs
        deposits = Deposit.query.all()
        transaction_ids = [d.transaction_id for d in deposits]
        duplicates = [tid for tid in set(transaction_ids) if transaction_ids.count(tid) > 1]
        
        if duplicates:
            print(f"⚠️  Found duplicate transaction IDs: {duplicates}")
        else:
            print("✓ No duplicate transaction IDs found")
        
        print(f"✓ Total deposits in database: {len(deposits)}")
        
        # Show admin login details
        print("\n🔑 Admin Login Details:")
        print("Email: admin@platform.com")
        print("Password: admin123")
        print("Login URL: /login")

if __name__ == "__main__":
    fix_admin_password()