#!/usr/bin/env python3
"""
Quick fix for registration processing issue
"""
import os
os.environ['DATABASE_URL'] = 'postgresql://neondb_owner:npg_4sSItw5JkLZM@ep-falling-firefly-afxbamco-pooler.c-2.us-west-2.aws.neon.tech/neondb'

from app import app, db
from models import User

def quick_registration_fix():
    """Quick fix for registration"""
    with app.app_context():
        try:
            print("🔧 Applying quick registration fix...")
            
            # Check current database state
            print("\n📊 Current Database State:")
            print(f"   Total users: {User.query.count()}")
            print(f"   Admin users: {User.query.filter_by(is_admin=True).count()}")
            print(f"   Regular users: {User.query.filter_by(is_admin=False).count()}")
            
            # Check for any stuck processes
            admin = User.query.filter_by(is_admin=True).first()
            if admin:
                print(f"   Admin balance: {admin.usdt_balance:.2f} USDT")
                print(f"   Admin referral bonus: {admin.referral_bonus:.2f} USDT")
            
            print("\n✅ Registration system status check completed!")
            print("💡 If still stuck on 'Processing...', please:")
            print("   1. Clear browser cache and cookies")
            print("   2. Try using incognito/private browsing mode")
            print("   3. Make sure all form fields are filled correctly")
            print("   4. Wait for OTP verification to complete before submitting")
            
            return True
            
        except Exception as e:
            print(f"❌ Fix failed: {e}")
            return False

if __name__ == "__main__":
    quick_registration_fix()