#!/usr/bin/env python3
"""
Test simple registration system
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User
from forms import RegisterForm

def test_simple_registration():
    """Test the simple registration process"""
    print("Testing simple registration...")
    
    with app.app_context():
        # Create test form data
        test_data = {
            'username': 'testuser123',
            'email': 'test@example.com', 
            'phone_number': '9876543210',
            'password': 'password123',
            'password2': 'password123',
            'referral_code': ''
        }
        
        # Check for existing users
        existing_user = User.query.filter(
            (User.username == test_data['username']) | 
            (User.email == test_data['email']) |
            (User.phone_number == test_data['phone_number'])
        ).first()
        
        if existing_user:
            print(f"Deleting existing test user: {existing_user.username}")
            db.session.delete(existing_user)
            db.session.commit()
        
        # Create new user
        try:
            user = User(
                username=test_data['username'],
                email=test_data['email'],
                phone_number=test_data['phone_number'],
                referred_by=None
            )
            user.set_password(test_data['password'])
            
            db.session.add(user)
            db.session.commit()
            
            print(f"✅ User '{user.username}' created successfully!")
            print(f"   Email: {user.email}")
            print(f"   Phone: {user.phone_number}")
            print(f"   Referral Code: {user.referral_code}")
            print(f"   Balance: {user.usdt_balance}")
            
            # Verify user can be retrieved
            found_user = User.query.filter_by(username=test_data['username']).first()
            if found_user:
                print(f"✅ User can be retrieved from database")
                return True
            else:
                print("❌ User not found after creation")
                return False
                
        except Exception as e:
            print(f"❌ Registration failed: {str(e)}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    success = test_simple_registration()
    if success:
        print("\n🎉 Simple registration system working correctly!")
    else:
        print("\n💥 Registration system has issues")