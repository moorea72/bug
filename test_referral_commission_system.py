
"""
Test script for the Referral Commission System
"""

from app import app, db
from models import User, Deposit, ReferralCommission
from referral_commission_system import ReferralCommissionSystem, process_deposit_commission
from werkzeug.security import generate_password_hash
import uuid

def test_referral_commission_system():
    """Test the referral commission system"""
    with app.app_context():
        print("🧪 Testing Referral Commission System")
        
        # Create test users
        print("\n1. Creating test users...")
        
        # Create referrer
        referrer = User(
            username='referrer_test',
            email='referrer@test.com',
            phone_number='+1234567890',
            password_hash=generate_password_hash('password'),
            referral_code=str(uuid.uuid4())[:8].upper(),
            usdt_balance=0.0
        )
        db.session.add(referrer)
        db.session.flush()
        
        # Create referred users
        referred_users = []
        test_deposits = [75, 250, 350, 25]  # Different deposit amounts to test tiers
        
        for i, deposit_amount in enumerate(test_deposits):
            user = User(
                username=f'referred_user_{i+1}',
                email=f'referred{i+1}@test.com',
                phone_number=f'+123456789{i+1}',
                password_hash=generate_password_hash('password'),
                referral_code=str(uuid.uuid4())[:8].upper(),
                referred_by=referrer.id,
                usdt_balance=0.0
            )
            db.session.add(user)
            db.session.flush()
            referred_users.append((user, deposit_amount))
        
        db.session.commit()
        print(f"✅ Created referrer and {len(referred_users)} referred users")
        
        # Test commission calculations
        print("\n2. Testing commission calculations...")
        for deposit_amount in [25, 75, 150, 250, 350]:
            commission = ReferralCommissionSystem.calculate_commission(deposit_amount)
            print(f"   Deposit ${deposit_amount} → Commission ${commission}")
        
        # Test commission processing
        print("\n3. Testing commission processing...")
        initial_balance = referrer.usdt_balance
        
        for user, deposit_amount in referred_users:
            print(f"\n   Processing deposit of ${deposit_amount} for {user.username}...")
            
            result = process_deposit_commission(user.id, deposit_amount)
            
            if result['success']:
                print(f"   ✅ Commission awarded: ${result['commission_amount']} USDT")
            else:
                print(f"   ❌ No commission: {result['reason']}")
            
            # Try to process again (should fail - one-time only)
            result2 = process_deposit_commission(user.id, deposit_amount * 2)
            if not result2['success']:
                print(f"   ✅ Duplicate commission prevented: {result2['reason']}")
        
        # Check final results
        db.session.refresh(referrer)
        print(f"\n4. Final Results:")
        print(f"   Referrer initial balance: ${initial_balance}")
        print(f"   Referrer final balance: ${referrer.usdt_balance}")
        print(f"   Total commission earned: ${referrer.usdt_balance - initial_balance}")
        
        # Check commission records
        commissions = ReferralCommission.query.filter_by(referrer_id=referrer.id).all()
        print(f"   Commission records created: {len(commissions)}")
        
        for commission in commissions:
            print(f"   - User {commission.referred_user_id}: ${commission.deposit_amount} deposit → ${commission.commission_amount_usdt} commission")
        
        # Test system statistics
        print("\n5. System Statistics:")
        stats = ReferralCommissionSystem.get_system_stats()
        print(f"   Total commissions paid: {stats['total_commissions']}")
        print(f"   Total amount paid: ${stats['total_amount_paid']}")
        
        for tier_name, tier_stats in stats['tier_breakdown'].items():
            print(f"   {tier_name}: {tier_stats['count']} commissions, ${tier_stats['total_paid']} total")
        
        # Cleanup test data
        print("\n6. Cleaning up test data...")
        ReferralCommission.query.filter_by(referrer_id=referrer.id).delete()
        for user, _ in referred_users:
            db.session.delete(user)
        db.session.delete(referrer)
        db.session.commit()
        print("✅ Test data cleaned up")
        
        print("\n🎉 Referral Commission System test completed successfully!")

if __name__ == "__main__":
    test_referral_commission_system()
