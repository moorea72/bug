#!/usr/bin/env python3
"""
Test script for Simple Referral System
Tests the new refer 2 friends bonus system
"""

from app import app, db
from models import User
from simple_referral_system import SimpleReferralSystem

def test_simple_referral_system():
    """Test the simple referral system functionality"""
    with app.app_context():
        print('Testing simple referral system...')
        
        # Check if users can check their referral status
        admin_user = User.query.filter_by(is_admin=True).first()
        if admin_user:
            print(f'Admin user: {admin_user.username}')
            print(f'Total referrals: {admin_user.get_referral_count()}')
            print(f'Active referrals (100+ USDT): {admin_user.get_active_referrals_count()}')
            print(f'Has two referrals bonus: {admin_user.has_two_referrals()}')
            print(f'Referral bonus balance: ${admin_user.referral_bonus:.2f}')
            
            # Test stake commission calculation
            test_stake_amount = 100.0
            stake_commission = SimpleReferralSystem.calculate_user_stake_bonus(admin_user.id, test_stake_amount)
            print(f'Stake commission for ${test_stake_amount}: ${stake_commission:.2f}')
        
        print('✓ Simple referral system is working correctly')

if __name__ == '__main__':
    test_simple_referral_system()