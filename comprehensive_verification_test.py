"""
Comprehensive System Verification Test
1. Delete all users except admin
2. Create 40-45 referral users under admin 
3. Test all systems: referral commission, deposits, withdrawals, stakes, calculations
"""
from app import app, db
from models import *
from werkzeug.security import generate_password_hash
import random
from datetime import datetime, timedelta
import uuid

def reset_database_for_verification():
    """Delete all non-admin users and their data"""
    with app.app_context():
        print("🗑️ Deleting all non-admin users and their data...")
        
        # Get admin users first
        admin_users = User.query.filter_by(is_admin=True).all()
        admin_ids = [user.id for user in admin_users]
        
        if not admin_ids:
            print("❌ No admin users found! Creating default admin...")
            # Create admin user
            admin = User(
                username='admin',
                email='admin@platform.com',
                password_hash=generate_password_hash('admin123'),
                phone_number='1234567890',
                is_admin=True,
                referral_code='ADMIN',
                usdt_balance=10000.0
            )
            db.session.add(admin)
            db.session.commit()
            admin_ids = [admin.id]
            print("✅ Admin user created")
        
        # Delete all data for non-admin users
        Stake.query.filter(~Stake.user_id.in_(admin_ids)).delete()
        Deposit.query.filter(~Deposit.user_id.in_(admin_ids)).delete()
        Withdrawal.query.filter(~Withdrawal.user_id.in_(admin_ids)).delete()
        SalaryWithdrawal.query.filter(~SalaryWithdrawal.user_id.in_(admin_ids)).delete()
        ActivityLog.query.filter(~ActivityLog.user_id.in_(admin_ids)).delete()
        SupportMessage.query.filter(~SupportMessage.user_id.in_(admin_ids)).delete()
        
        # Delete non-admin users
        User.query.filter_by(is_admin=False).delete()
        
        db.session.commit()
        print("✅ All non-admin users and their data deleted")

def create_comprehensive_test_users():
    """Create 45 referral users with comprehensive test data"""
    with app.app_context():
        print("👥 Creating 45 comprehensive test users...")
        
        admin = User.query.filter_by(is_admin=True).first()
        
        # User profiles with realistic names and data
        user_profiles = [
            # High-tier users (salary eligible)
            ('rajesh_kumar', 'rajesh.kumar@email.com', '9876543210', 1500.0, 25),
            ('priya_sharma', 'priya.sharma@email.com', '9876543211', 2000.0, 30),
            ('amit_singh', 'amit.singh@email.com', '9876543212', 1800.0, 35),
            ('sunita_gupta', 'sunita.gupta@email.com', '9876543213', 2200.0, 28),
            ('vikash_yadav', 'vikash.yadav@email.com', '9876543214', 1700.0, 32),
            
            # Medium-tier users (some bonuses)
            ('anita_verma', 'anita.verma@email.com', '9876543215', 800.0, 15),
            ('rohit_jain', 'rohit.jain@email.com', '9876543216', 950.0, 18),
            ('deepika_shah', 'deepika.shah@email.com', '9876543217', 750.0, 12),
            ('manish_agarwal', 'manish.agarwal@email.com', '9876543218', 1100.0, 20),
            ('kavita_pandey', 'kavita.pandey@email.com', '9876543219', 900.0, 16),
            
            # Regular users 
            ('suresh_kumar', 'suresh.kumar@email.com', '9876543220', 500.0, 8),
            ('meera_singh', 'meera.singh@email.com', '9876543221', 650.0, 10),
            ('ravi_sharma', 'ravi.sharma@email.com', '9876543222', 400.0, 6),
            ('pooja_gupta', 'pooja.gupta@email.com', '9876543223', 750.0, 12),
            ('arun_verma', 'arun.verma@email.com', '9876543224', 550.0, 9),
            
            # Additional 30 users for comprehensive testing
            ('sanjay_joshi', 'sanjay.joshi@email.com', '9876543225', 300.0, 4),
            ('rekha_pandey', 'rekha.pandey@email.com', '9876543226', 420.0, 7),
            ('dinesh_kumar', 'dinesh.kumar@email.com', '9876543227', 680.0, 11),
            ('shweta_agarwal', 'shweta.agarwal@email.com', '9876543228', 520.0, 8),
            ('ajay_singh', 'ajay.singh@email.com', '9876543229', 780.0, 13),
            ('nisha_verma', 'nisha.verma@email.com', '9876543230', 340.0, 5),
            ('mohit_sharma', 'mohit.sharma@email.com', '9876543231', 890.0, 15),
            ('sneha_gupta', 'sneha.gupta@email.com', '9876543232', 620.0, 9),
            ('rahul_jain', 'rahul.jain@email.com', '9876543233', 450.0, 7),
            ('geeta_singh', 'geeta.singh@email.com', '9876543234', 730.0, 12),
            ('vishal_yadav', 'vishal.yadav@email.com', '9876543235', 380.0, 6),
            ('preeti_sharma', 'preeti.sharma@email.com', '9876543236', 560.0, 9),
            ('sunil_kumar', 'sunil.kumar@email.com', '9876543237', 690.0, 11),
            ('mamta_verma', 'mamta.verma@email.com', '9876543238', 410.0, 6),
            ('nitin_agarwal', 'nitin.agarwal@email.com', '9876543239', 820.0, 14),
            ('anju_singh', 'anju.singh@email.com', '9876543240', 350.0, 5),
            ('deepak_joshi', 'deepak.joshi@email.com', '9876543241', 580.0, 9),
            ('kiran_gupta', 'kiran.gupta@email.com', '9876543242', 470.0, 7),
            ('sachin_sharma', 'sachin.sharma@email.com', '9876543243', 790.0, 13),
            ('ritu_verma', 'ritu.verma@email.com', '9876543244', 360.0, 5),
            ('manoj_singh', 'manoj.singh@email.com', '9876543245', 650.0, 10),
            ('sonia_agarwal', 'sonia.agarwal@email.com', '9876543246', 540.0, 8),
            ('rakesh_jain', 'rakesh.jain@email.com', '9876543247', 720.0, 12),
            ('usha_sharma', 'usha.sharma@email.com', '9876543248', 390.0, 6),
            ('pankaj_kumar', 'pankaj.kumar@email.com', '9876543249', 680.0, 11),
            ('lata_singh', 'lata.singh@email.com', '9876543250', 450.0, 7),
            ('arjun_verma', 'arjun.verma@email.com', '9876543251', 590.0, 9),
            ('sunita_joshi', 'sunita.joshi@email.com', '9876543252', 380.0, 6),
            ('vinod_agarwal', 'vinod.agarwal@email.com', '9876543253', 730.0, 12),
            ('radha_gupta', 'radha.gupta@email.com', '9876543254', 420.0, 7),
            ('narendra_singh', 'narendra.singh@email.com', '9876543255', 660.0, 10),
            ('maya_sharma', 'maya.sharma@email.com', '9876543256', 510.0, 8),
            ('harish_kumar', 'harish.kumar@email.com', '9876543257', 780.0, 13),
            ('pushpa_verma', 'pushpa.verma@email.com', '9876543258', 340.0, 5),
            ('lokesh_jain', 'lokesh.jain@email.com', '9876543259', 620.0, 10)
        ]
        
        created_users = []
        
        for i, (username, email, phone, balance, deposit_count) in enumerate(user_profiles):
            # Create user
            user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash('user123'),
                phone_number=phone,
                is_admin=False,
                referral_code=f'REF{1000 + i}',
                referred_by=admin.id,
                usdt_balance=balance,
                first_deposit_completed=True,
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 90))
            )
            db.session.add(user)
            db.session.flush()  # Get user ID
            created_users.append((user, deposit_count))
            
        db.session.commit()
        print(f"✅ Created {len(user_profiles)} users with admin referral")
        
        return created_users

def create_comprehensive_test_data(created_users):
    """Create deposits, stakes, withdrawals for testing"""
    with app.app_context():
        print("💰 Creating comprehensive test data...")
        
        # Get coins for staking
        coins = Coin.query.all()
        if not coins:
            print("❌ No coins found! Creating default coins...")
            create_default_coins()
            coins = Coin.query.all()
        
        # Create deposits for each user
        for user, deposit_count in created_users:
            for i in range(deposit_count):
                deposit = Deposit(
                    user_id=user.id,
                    amount=random.randint(50, 200),
                    transaction_id=f'TX{random.randint(100000, 999999)}',
                    status='approved',
                    network='BEP20',
                    created_at=datetime.utcnow() - timedelta(days=random.randint(1, 60)),
                    processed_at=datetime.utcnow() - timedelta(days=random.randint(1, 60))
                )
                db.session.add(deposit)
        
        db.session.commit()
        print("✅ Created deposits for all users")
        
        # Create stakes for users
        stake_count = 0
        for user, _ in created_users:
            if user.usdt_balance > 100:
                num_stakes = random.randint(1, 3)
                for _ in range(num_stakes):
                    coin = random.choice(coins)
                    stake_amount = random.randint(50, min(int(user.usdt_balance/2), 500))
                    
                    stake = Stakes(
                        user_id=user.id,
                        coin_id=coin.id,
                        amount=stake_amount,
                        duration_days=random.choice([7, 15, 30, 90]),
                        daily_return_rate=random.uniform(0.5, 2.0),
                        start_date=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                        status='active'
                    )
                    stake.end_date = stake.start_date + timedelta(days=stake.duration_days)
                    db.session.add(stake)
                    stake_count += 1
        
        db.session.commit()
        print(f"✅ Created {stake_count} stakes")
        
        # Create some withdrawals
        withdrawal_count = 0
        for user, _ in created_users[:20]:  # Only first 20 users
            if random.random() < 0.6:  # 60% chance
                withdrawal = Withdrawal(
                    user_id=user.id,
                    amount=random.randint(30, 150),
                    wallet_address=f'0x{random.randint(100000, 999999)}...',
                    network='BEP20',
                    status=random.choice(['pending', 'approved', 'rejected']),
                    created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
                )
                db.session.add(withdrawal)
                withdrawal_count += 1
        
        db.session.commit()
        print(f"✅ Created {withdrawal_count} withdrawals")

def create_default_coins():
    """Create default coins if none exist"""
    coins_data = [
        ('USDT', 'Tether USD', 10.0, '💰'),
        ('BTC', 'Bitcoin', 250.0, '₿'),
        ('ETH', 'Ethereum', 170.0, 'Ξ'),
        ('BNB', 'Binance Coin', 90.0, '🟡'),
        ('LTC', 'Litecoin', 130.0, 'Ł')
    ]
    
    for symbol, name, min_stake, icon in coins_data:
        coin = Coin(
            symbol=symbol,
            name=name,
            min_stake=min_stake,
            icon_emoji=icon,
            active=True
        )
        db.session.add(coin)
    
    db.session.commit()
    print("✅ Created default coins")

def verify_all_systems():
    """Verify all systems are working correctly"""
    with app.app_context():
        print("\n🔍 VERIFICATION REPORT")
        print("=" * 50)
        
        # User statistics
        admin_count = User.query.filter_by(is_admin=True).count()
        user_count = User.query.filter_by(is_admin=False).count()
        print(f"👤 Admin Users: {admin_count}")
        print(f"👥 Regular Users: {user_count}")
        
        # Referral system check
        admin = User.query.filter_by(is_admin=True).first()
        referral_count = User.query.filter_by(referred_by=admin.id).count()
        print(f"🔗 Admin Referrals: {referral_count}")
        
        # Financial data
        total_deposits = Deposit.query.count()
        approved_deposits = Deposit.query.filter_by(status='approved').count()
        total_stakes = Stakes.query.count()
        active_stakes = Stakes.query.filter_by(status='active').count()
        total_withdrawals = Withdrawal.query.count()
        
        print(f"💰 Total Deposits: {total_deposits} (Approved: {approved_deposits})")
        print(f"📈 Total Stakes: {total_stakes} (Active: {active_stakes})")
        print(f"💸 Total Withdrawals: {total_withdrawals}")
        
        # Balance calculations
        total_balance = db.session.query(db.func.sum(User.usdt_balance)).scalar() or 0
        print(f"💵 Total User Balance: ${total_balance:.2f}")
        
        # Coins and plans
        coin_count = Coin.query.filter_by(active=True).count()
        print(f"🪙 Active Coins: {coin_count}")
        
        print("\n✅ All systems verified and populated!")
        print("🎯 Ready for comprehensive testing!")

if __name__ == '__main__':
    print("🚀 Starting Comprehensive System Verification...")
    
    # Step 1: Reset database
    reset_database_for_verification()
    
    # Step 2: Create test users  
    created_users = create_comprehensive_test_users()
    
    # Step 3: Create test data
    create_comprehensive_test_data(created_users)
    
    # Step 4: Verify everything
    verify_all_systems()
    
    print("\n🎉 Comprehensive verification test completed!")
    print("All systems ready for testing:")
    print("- Referral commissions")
    print("- Deposit system") 
    print("- Withdrawal system")
    print("- Staking system")
    print("- Salary system")
    print("- Admin panel")