"""
Simple test user creation
"""
import sys
sys.path.append('.')

from app import app, db
from models import User
from werkzeug.security import generate_password_hash

# Create test users
with app.app_context():
    # Clear existing non-admin users
    User.query.filter_by(is_admin=False).delete()
    
    # Get admin
    admin = User.query.filter_by(is_admin=True).first()
    admin_id = admin.id if admin else 1
    
    # Create 15 users
    users = []
    for i in range(15):
        user = User(
            username=f'testuser{i+1}',
            email=f'test{i+1}@email.com',
            password_hash=generate_password_hash('test123'),
            phone_number=f'987654{i:04d}',
            referral_code=f'TEST{i+1:03d}',
            referred_by=admin_id,
            usdt_balance=500.0 + (i * 50),
            first_deposit_completed=True
        )
        users.append(user)
        db.session.add(user)
    
    db.session.commit()
    print(f"Created {len(users)} test users")