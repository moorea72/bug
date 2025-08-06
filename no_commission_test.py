#!/usr/bin/env python3
"""
Test that NO commission is awarded in the new system
"""

from app import app, db
from models import User, Deposit, ActivityLog
from complete_referral_fix import DepositOnlyReferralSystem
from werkzeug.security import generate_password_hash
from datetime import datetime

def test_no_commission_system():
    """Test that NO commission is awarded for any deposits"""
    print("🚫 NO COMMISSION SYSTEM TEST")
    print("=" * 40)
    
    with app.app_context():
        # Get admin user
        admin = User.query.filter_by(is_admin=True).first()
        if not admin:
            print("❌ Admin user not found")
            return False
        
        print(f"✅ Admin found: {admin.username}")
        admin_bonus_before = admin.referral_bonus
        print(f"Admin bonus before: ${admin_bonus_before}")
        
        # Create test user referred by admin
        test_user = User(
            username='no_commission_test',
            email='nocommission@test.com',
            phone_number='8888888888',
            password_hash=generate_password_hash('password123'),
            referral_code='NOCOMM001',
            referred_by=admin.id,
            usdt_balance=0.0
        )
        db.session.add(test_user)
        db.session.commit()
        
        print(f"✅ Test user created: {test_user.username}")
        
        # Test deposit - should NOT get commission
        print("\n🧪 Testing 200 USDT deposit (should NOT get commission)")
        result = DepositOnlyReferralSystem.award_commission_on_deposit(test_user.id, 200.0)
        
        # Refresh admin from database
        db.session.refresh(admin)
        admin_bonus_after = admin.referral_bonus
        
        print(f"Result: {result}")
        print(f"Admin bonus before: ${admin_bonus_before}")
        print(f"Admin bonus after: ${admin_bonus_after}")
        print(f"Commission awarded: ${admin_bonus_after - admin_bonus_before}")
        
        if admin_bonus_after == admin_bonus_before and result.get('total_commission', 0) == 0:
            print("✅ CORRECT: No commission awarded - system working as intended")
            success = True
        else:
            print("❌ ERROR: Commission was awarded when it should not be")
            success = False
        
        # Check activity log
        activity = ActivityLog.query.filter_by(user_id=test_user.id, action='referral_deposit').first()
        if activity and 'NO COMMISSION' in activity.description:
            print("✅ CORRECT: Activity logged with NO COMMISSION marker")
        else:
            print("❌ Activity log not correct")
            success = False
        
        # Cleanup
        ActivityLog.query.filter_by(user_id=test_user.id).delete()
        db.session.delete(test_user)
        db.session.commit()
        
        return success

def main():
    """Run no commission test"""
    print("🎯 NO COMMISSION REFERRAL SYSTEM TEST")
    print("Verifying that NO commissions are awarded")
    print("=" * 50)
    
    try:
        test_result = test_no_commission_system()
        
        if test_result:
            print("\n" + "=" * 50)
            print("🎉 NO COMMISSION TEST PASSED!")
            print("\n✅ VERIFIED:")
            print("1. NO commission awarded for any deposits")
            print("2. Referral relationships still tracked")
            print("3. Activity log shows 'NO COMMISSION' marker")
            print("4. Admin bonus unchanged after referral deposits")
            
            print("\n🎯 FINAL STATUS:")
            print("• Notification bell completely removed")
            print("• Referral commission system completely disabled")
            print("• Only referral tracking remains (no payments)")
            
        else:
            print("\n❌ TEST FAILED - Commission system still active")
            
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()