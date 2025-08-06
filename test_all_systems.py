#!/usr/bin/env python3
"""
Test all platform systems - Login, Referral, Balance, Withdrawal
"""

from app import app, db
from models import User, Deposit, Withdrawal, Stake, Coin, StakingPlan, PlatformSettings
from referral_utils import award_referral_commission
from salary_system import check_salary_eligibility, get_salary_progress
from datetime import datetime

def test_all_systems():
    """Test login, referral, balance, withdrawal systems"""
    with app.app_context():
        print("=== Testing All Platform Systems ===")
        
        # Test 1: Login System
        print("\n1. Testing Login System...")
        test_user = User.query.filter_by(email='pankajmanmar13@gmail.com').first()
        if test_user:
            print(f"✓ User found: {test_user.username}")
            print(f"  - Balance: ${test_user.usdt_balance}")
            print(f"  - Total Staked: ${test_user.total_staked}")
            print(f"  - Referral Bonus: ${test_user.referral_bonus}")
        else:
            print("✗ User not found")
        
        # Test 2: Referral System
        print("\n2. Testing Referral System...")
        if test_user:
            referral_count = test_user.get_referral_count()
            active_referrals = test_user.get_active_referrals_count()
            print(f"  - Total Referrals: {referral_count}")
            print(f"  - Active Referrals (100+ deposit): {active_referrals}")
            print(f"  - Has 2+ referrals bonus: {test_user.has_two_referrals()}")
        
        # Test 3: Balance System
        print("\n3. Testing Balance System...")
        if test_user:
            total_balance = test_user.get_total_balance_including_stakes()
            print(f"  - Wallet Balance: ${test_user.usdt_balance}")
            print(f"  - Total Balance (including stakes): ${total_balance}")
            
            # Check deposits
            deposits = Deposit.query.filter_by(user_id=test_user.id).all()
            print(f"  - Total Deposits: {len(deposits)}")
            for deposit in deposits[-3:]:  # Show last 3
                print(f"    - ${deposit.amount} ({deposit.status}) - {deposit.created_at.strftime('%Y-%m-%d')}")
        
        # Test 4: Withdrawal System
        print("\n4. Testing Withdrawal System...")
        if test_user:
            withdrawals = Withdrawal.query.filter_by(user_id=test_user.id).all()
            print(f"  - Total Withdrawals: {len(withdrawals)}")
            for withdrawal in withdrawals[-3:]:  # Show last 3
                print(f"    - ${withdrawal.amount} ({withdrawal.status}) - {withdrawal.created_at.strftime('%Y-%m-%d')}")
            
            # Check withdrawal fee eligibility
            has_bonus = test_user.has_two_referrals()
            print(f"  - Fee Waiver Eligible: {has_bonus}")
        
        # Test 5: Staking System
        print("\n5. Testing Staking System...")
        if test_user:
            stakes = Stake.query.filter_by(user_id=test_user.id).all()
            print(f"  - Total Stakes: {len(stakes)}")
            for stake in stakes[-3:]:  # Show last 3
                current_return = stake.calculate_current_return()
                print(f"    - ${stake.amount} {stake.coin.symbol} ({stake.status}) - Earnings: ${current_return:.2f}")
        
        # Test 6: Salary System
        print("\n6. Testing Salary System...")
        if test_user:
            eligible_plan, active_refs, total_bal = check_salary_eligibility(test_user)
            progress = get_salary_progress(test_user)
            print(f"  - Eligible Plan: {eligible_plan}")
            print(f"  - Active Referrals: {active_refs}")
            print(f"  - Total Balance: ${total_bal}")
            
            if eligible_plan:
                from salary_system import SalaryPlan
                plan = SalaryPlan.PLANS[eligible_plan]
                print(f"  - Monthly Salary: ${plan['monthly_salary']}")
        
        # Test 7: Database Tables
        print("\n7. Testing Database Tables...")
        print(f"  - Users: {User.query.count()}")
        print(f"  - Deposits: {Deposit.query.count()}")
        print(f"  - Withdrawals: {Withdrawal.query.count()}")
        print(f"  - Stakes: {Stake.query.count()}")
        print(f"  - Coins: {Coin.query.count()}")
        print(f"  - Staking Plans: {StakingPlan.query.count()}")
        
        # Test 8: Platform Settings
        print("\n8. Testing Platform Settings...")
        settings = PlatformSettings.get_all_settings()
        print(f"  - Referral Level 1: {settings.get('referral_level_1', 'Not Set')}%")
        print(f"  - Min Referral Activation: ${settings.get('min_referral_activation', 'Not Set')}")
        print(f"  - Withdrawal Fee: {settings.get('withdrawal_fee', 'Not Set')}%")
        
        print("\n=== All Systems Test Complete ===")

if __name__ == '__main__':
    test_all_systems()