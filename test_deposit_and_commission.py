
#!/usr/bin/env python3
"""
Test script to verify deposit approval and referral commission system
"""

from app import app, db
from models import User, Deposit, ReferralCommission, ActivityLog
from werkzeug.security import generate_password_hash
import uuid

def test_deposit_system():
    """Test deposit approval and commission system"""
    with app.app_context():
        print("🧪 Testing Deposit & Commission System")
        print("=" * 50)
        
        # Get admin user
        admin = User.query.filter_by(is_admin=True).first()
        if not admin:
            print("❌ Admin user not found")
            return
        
        print(f"✅ Admin found: {admin.username}")
        print(f"Current admin balance: ${admin.usdt_balance:.2f}")
        print(f"Current referral bonus: ${admin.referral_bonus:.2f}")
        
        # Create test user referred by admin
        test_username = f"test_user_{uuid.uuid4().hex[:8]}"
        test_user = User(
            username=test_username,
            email=f"{test_username}@test.com",
            phone_number=f"99{uuid.uuid4().hex[:8]}",
            password_hash=generate_password_hash('password123'),
            referral_code=f"TEST{uuid.uuid4().hex[:6].upper()}",
            referred_by=admin.id,
            usdt_balance=0.0
        )
        db.session.add(test_user)
        db.session.commit()
        
        print(f"✅ Test user created: {test_user.username}")
        print(f"Test user balance: ${test_user.usdt_balance:.2f}")
        
        # Create test deposit
        deposit = Deposit(
            user_id=test_user.id,
            amount=150.0,
            transaction_id=f"0x{uuid.uuid4().hex}",
            status='pending'
        )
        db.session.add(deposit)
        db.session.commit()
        
        print(f"✅ Test deposit created: ${deposit.amount} USDT")
        
        # Simulate admin approval
        from referral_commission_system import process_deposit_commission
        
        # Update deposit status
        deposit.status = 'approved'
        deposit.processed_at = datetime.utcnow()
        
        # Add to user balance
        test_user.usdt_balance += deposit.amount
        
        # Process commission
        commission_result = process_deposit_commission(test_user.id, deposit.amount)
        
        db.session.commit()
        
        # Check results
        updated_admin = User.query.get(admin.id)
        updated_user = User.query.get(test_user.id)
        
        print("\n📊 RESULTS:")
        print(f"User balance after deposit: ${updated_user.usdt_balance:.2f}")
        print(f"Admin balance after commission: ${updated_admin.usdt_balance:.2f}")
        print(f"Admin referral bonus after commission: ${updated_admin.referral_bonus:.2f}")
        print(f"Commission result: {commission_result}")
        
        # Check commission record
        commission_record = ReferralCommission.query.filter_by(referred_user_id=test_user.id).first()
        if commission_record:
            print(f"✅ Commission record created: ${commission_record.commission_amount_usdt} USDT")
        else:
            print("❌ No commission record found")
        
        # Clean up
        db.session.delete(test_user)
        db.session.delete(deposit)
        if commission_record:
            db.session.delete(commission_record)
        db.session.commit()
        
        print("\n✅ Test completed and cleaned up")

if __name__ == "__main__":
    test_deposit_system()
