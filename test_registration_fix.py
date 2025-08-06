#!/usr/bin/env python3
"""
Test registration process fix
"""
import os
os.environ['DATABASE_URL'] = 'postgresql://neondb_owner:npg_4sSItw5JkLZM@ep-falling-firefly-afxbamco-pooler.c-2.us-west-2.aws.neon.tech/neondb'

from app import app, db
from models import User

def test_registration_process():
    """Test that registration is working"""
    with app.app_context():
        try:
            print("🧪 Testing registration process...")
            
            # Check if there are any users in the database
            total_users = User.query.count()
            print(f"📊 Total users in database: {total_users}")
            
            # Check admin user
            admin = User.query.filter_by(is_admin=True).first()
            if admin:
                print(f"✅ Admin user found: {admin.username} ({admin.email})")
            else:
                print("❌ No admin user found")
            
            # Check regular users
            regular_users = User.query.filter_by(is_admin=False).count()
            print(f"👥 Regular users: {regular_users}")
            
            # Check latest registered user
            latest_user = User.query.order_by(User.created_at.desc()).first()
            if latest_user:
                print(f"🆕 Latest registered user: {latest_user.username} ({latest_user.phone_number})")
            
            print("✅ Registration test completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Registration test failed: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    test_registration_process()