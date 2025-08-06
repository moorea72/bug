#!/usr/bin/env python3
"""
Setup salary system database
"""

import os
from app import app, db

def setup_salary_system():
    """Setup salary system database"""
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("✓ Database tables created successfully")
            
            # Check if admin user exists
            from models import User
            admin = User.query.filter_by(email='admin@platform.com').first()
            if not admin:
                print("! Admin user not found, creating...")
                admin = User(
                    username='admin',
                    email='admin@platform.com',
                    phone_number='1234567890',
                    is_admin=True
                )
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                print("✓ Admin user created")
            
            print("✓ Salary system setup completed!")
            
        except Exception as e:
            print(f"✗ Error: {e}")
            db.session.rollback()

if __name__ == '__main__':
    setup_salary_system()