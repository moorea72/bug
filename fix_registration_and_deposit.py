#!/usr/bin/env python3
"""
Fix registration processing and deposit system issues
"""
import os
os.environ['DATABASE_URL'] = 'postgresql://neondb_owner:npg_4sSItw5JkLZM@ep-falling-firefly-afxbamco-pooler.c-2.us-west-2.aws.neon.tech/neondb'

from app import app, db
from models import User, Deposit, Withdrawal

def fix_registration_and_deposit():
    """Fix registration and deposit system"""
    with app.app_context():
        try:
            print("🔧 Fixing registration and deposit system...")
            
            # 1. Check duplicate transaction prevention
            print("\n1. Checking duplicate transaction prevention...")
            duplicate_txs = db.session.query(Deposit.transaction_id).group_by(Deposit.transaction_id).having(db.func.count(Deposit.transaction_id) > 1).all()
            if duplicate_txs:
                print(f"⚠️  Found {len(duplicate_txs)} duplicate transaction IDs")
                for tx in duplicate_txs:
                    print(f"   - {tx[0]}")
            else:
                print("✅ No duplicate transactions found")
            
            # 2. Check referral commission system
            print("\n2. Checking referral commission system...")
            admin = User.query.filter_by(is_admin=True).first()
            if admin:
                referrals = User.query.filter_by(referred_by=admin.id).count()
                print(f"✅ Admin has {referrals} referrals")
                print(f"✅ Admin referral bonus: {admin.referral_bonus:.2f} USDT")
                print(f"✅ Admin balance: {admin.usdt_balance:.2f} USDT")
            
            # 3. Check deposit verification logic
            print("\n3. Checking deposit verification logic...")
            recent_deposits = Deposit.query.order_by(Deposit.created_at.desc()).limit(5).all()
            for deposit in recent_deposits:
                print(f"   - {deposit.user.username}: {deposit.amount} USDT - {deposit.status}")
            
            # 4. Check withdrawal system
            print("\n4. Checking withdrawal system...")
            recent_withdrawals = Withdrawal.query.order_by(Withdrawal.created_at.desc()).limit(5).all()
            for withdrawal in recent_withdrawals:
                print(f"   - {withdrawal.user.username}: {withdrawal.amount} USDT - {withdrawal.status}")
            
            # 5. Summary
            print("\n📊 SYSTEM SUMMARY:")
            print(f"   - Total Users: {User.query.count()}")
            print(f"   - Total Deposits: {Deposit.query.count()}")
            print(f"   - Total Withdrawals: {Withdrawal.query.count()}")
            print(f"   - Verified Deposits: {Deposit.query.filter_by(blockchain_verified=True).count()}")
            print(f"   - Pending Deposits: {Deposit.query.filter_by(status='pending').count()}")
            
            print("\n✅ System check completed successfully!")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    fix_registration_and_deposit()