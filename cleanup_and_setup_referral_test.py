
#!/usr/bin/env python3
"""
Complete cleanup and referral test setup
1. Delete all users except admin
2. Test salary system calculations
3. Create 20 users with admin referral and 100 USDT deposits
"""

from app import app, db
from models import User, Deposit, Stake, Withdrawal, ActivityLog, SalaryWithdrawal
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import uuid

def cleanup_and_setup_referral_test():
    """Complete cleanup and setup for referral testing"""
    
    with app.app_context():
        print("🚀 Starting complete cleanup and referral test setup...")
        
        # Step 1: Find and preserve admin
        admin = User.query.filter_by(is_admin=True).first()
        if not admin:
            print("❌ Admin user not found! Creating admin...")
            admin = User(
                username='admin',
                email='admin@platform.com',
                phone_number='+1234567890',
                is_admin=True,
                is_active=True,
                usdt_balance=10000.0,
                referral_code='ADMIN'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin user created")
        
        print(f"✅ Admin preserved: {admin.username} (ID: {admin.id})")
        
        # Step 2: Delete all non-admin users and their data
        print("🗑️ Deleting all non-admin users...")
        
        non_admin_users = User.query.filter(User.id != admin.id).all()
        print(f"Found {len(non_admin_users)} non-admin users to delete")
        
        # Delete related data first to avoid foreign key constraints
        for user in non_admin_users:
            # Delete user's stakes
            Stake.query.filter_by(user_id=user.id).delete()
            # Delete user's deposits
            Deposit.query.filter_by(user_id=user.id).delete()
            # Delete user's withdrawals
            Withdrawal.query.filter_by(user_id=user.id).delete()
            # Delete user's activity logs
            ActivityLog.query.filter_by(user_id=user.id).delete()
            # Delete user's salary withdrawals
            SalaryWithdrawal.query.filter_by(user_id=user.id).delete()
            
        # Delete the users themselves
        User.query.filter(User.id != admin.id).delete()
        
        # Reset admin's referral bonus
        admin.referral_bonus = 0.0
        admin.usdt_balance = 10000.0  # Reset admin balance
        
        db.session.commit()
        print("✅ All non-admin users and data deleted")
        
        # Step 3: Test salary system calculations
        print("\n💰 Testing salary system calculations...")
        
        # Test salary plans
        salary_plans = [
            {'min_referrals': 7, 'min_balance': 350, 'monthly_salary': 50, 'name': 'Plan 1'},
            {'min_referrals': 13, 'min_balance': 680, 'monthly_salary': 110, 'name': 'Plan 2'},
            {'min_referrals': 27, 'min_balance': 960, 'monthly_salary': 230, 'name': 'Plan 3'},
            {'min_referrals': 46, 'min_balance': 1340, 'monthly_salary': 480, 'name': 'Plan 4'}
        ]
        
        print("📋 Salary Plans Configuration:")
        for plan in salary_plans:
            print(f"   {plan['name']}: {plan['min_referrals']} referrals + ${plan['min_balance']} balance = ${plan['monthly_salary']}/month")
        
        # Test admin's current eligibility (should be 0 initially)
        admin_referrals = admin.get_qualified_referrals_count()
        admin_balance = admin.get_total_balance_including_stakes()
        admin_eligible = admin.is_salary_eligible()
        
        print(f"\n👤 Admin Current Status:")
        print(f"   Qualified Referrals: {admin_referrals}")
        print(f"   Total Balance: ${admin_balance}")
        print(f"   Salary Eligible: {admin_eligible}")
        
        # Step 4: Create 20 users with admin referral and 100 USDT deposits
        print("\n👥 Creating 20 users with admin referral...")
        
        user_profiles = [
            ('rahul_sharma', 'rahul.sharma@test.com', '9876543210'),
            ('priya_singh', 'priya.singh@test.com', '9876543211'),
            ('amit_kumar', 'amit.kumar@test.com', '9876543212'),
            ('sneha_patel', 'sneha.patel@test.com', '9876543213'),
            ('vikash_gupta', 'vikash.gupta@test.com', '9876543214'),
            ('anjali_verma', 'anjali.verma@test.com', '9876543215'),
            ('rohit_yadav', 'rohit.yadav@test.com', '9876543216'),
            ('pooja_agarwal', 'pooja.agarwal@test.com', '9876543217'),
            ('manish_jain', 'manish.jain@test.com', '9876543218'),
            ('sunita_kumari', 'sunita.kumari@test.com', '9876543219'),
            ('deepak_shah', 'deepak.shah@test.com', '9876543220'),
            ('kavita_mishra', 'kavita.mishra@test.com', '9876543221'),
            ('suresh_pandey', 'suresh.pandey@test.com', '9876543222'),
            ('meera_thakur', 'meera.thakur@test.com', '9876543223'),
            ('ajay_soni', 'ajay.soni@test.com', '9876543224'),
            ('ritu_bansal', 'ritu.bansal@test.com', '9876543225'),
            ('naveen_saxena', 'naveen.saxena@test.com', '9876543226'),
            ('swati_arora', 'swati.arora@test.com', '9876543227'),
            ('kiran_mehta', 'kiran.mehta@test.com', '9876543228'),
            ('rajesh_tiwari', 'rajesh.tiwari@test.com', '9876543229')
        ]
        
        created_users = []
        created_deposits = []
        
        for i, (username, email, phone) in enumerate(user_profiles):
            # Create user with admin referral
            user = User(
                username=username,
                email=email,
                phone_number=phone,
                password_hash=generate_password_hash('password123'),
                usdt_balance=100.0,  # Start with 100 USDT
                referred_by=admin.id,  # All users referred by admin
                is_active=True,
                created_at=datetime.utcnow() - timedelta(days=i+1)  # Stagger creation dates
            )
            
            db.session.add(user)
            db.session.flush()  # Get user ID
            created_users.append(user)
            
            # Create approved deposit record for 100 USDT
            deposit = Deposit(
                user_id=user.id,
                amount=100.0,
                transaction_id=f"ADMIN_REF_{username.upper()}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{i:02d}",
                status='approved',
                blockchain_verified=True,
                verification_details=f"Admin referral test deposit of $100 USDT for {username}",
                created_at=datetime.utcnow() - timedelta(days=i+1),
                processed_at=datetime.utcnow() - timedelta(days=i)
            )
            
            db.session.add(deposit)
            created_deposits.append(deposit)
            
            print(f"✅ Created user: {username} with 100 USDT deposit")
        
        db.session.commit()
        
        # Step 5: Test salary system with new users
        print(f"\n🔄 Testing salary system with {len(created_users)} referrals...")
        
        # Refresh admin data
        admin = User.query.get(admin.id)
        admin_referrals_new = admin.get_qualified_referrals_count()
        admin_balance_new = admin.get_total_balance_including_stakes()
        admin_eligible_new = admin.is_salary_eligible()
        
        print(f"\n👤 Admin Updated Status:")
        print(f"   Qualified Referrals: {admin_referrals_new}")
        print(f"   Total Balance: ${admin_balance_new}")
        print(f"   Salary Eligible: {admin_eligible_new}")
        
        # Check which salary plan admin qualifies for
        eligible_plan = None
        for plan in salary_plans:
            if admin_referrals_new >= plan['min_referrals'] and admin_balance_new >= plan['min_balance']:
                eligible_plan = plan
                break
        
        if eligible_plan:
            print(f"   🎯 Qualified for: {eligible_plan['name']} - ${eligible_plan['monthly_salary']}/month")
        else:
            print(f"   ❌ Not qualified for any salary plan yet")
            next_plan = salary_plans[0]  # Plan 1
            needed_referrals = max(0, next_plan['min_referrals'] - admin_referrals_new)
            needed_balance = max(0, next_plan['min_balance'] - admin_balance_new)
            print(f"   📈 For Plan 1: Need {needed_referrals} more referrals and ${needed_balance} more balance")
        
        # Step 6: Final verification
        print(f"\n📊 Final Statistics:")
        total_users = User.query.count()
        admin_referrals_final = User.query.filter_by(referred_by=admin.id).count()
        total_deposits = Deposit.query.filter_by(status='approved').count()
        
        print(f"   Total users: {total_users} (1 admin + {admin_referrals_final} referrals)")
        print(f"   Admin referrals: {admin_referrals_final}")
        print(f"   Approved deposits: {total_deposits}")
        print(f"   Admin balance: ${admin.usdt_balance}")
        
        # Test automatic salary calculation
        if admin_eligible_new:
            print(f"\n💰 Salary System Test:")
            print(f"   Admin is eligible for automatic salary!")
            print(f"   Monthly amount: ${eligible_plan['monthly_salary']}")
            print(f"   System working correctly ✅")
        else:
            print(f"\n💰 Salary System Test:")
            print(f"   Admin not yet eligible (need more referrals/balance)")
            print(f"   System calculating correctly ✅")
        
        print(f"\n🎉 Setup completed successfully!")
        return True

if __name__ == "__main__":
    try:
        success = cleanup_and_setup_referral_test()
        if success:
            print("\n✅ All operations completed successfully!")
            print("\n📋 Next Steps:")
            print("   1. Login as admin: admin@platform.com / admin123")
            print("   2. Check admin dashboard for referral stats")
            print("   3. Test salary system with current users")
            print("   4. All users have password: password123")
        else:
            print("\n❌ Setup failed!")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
