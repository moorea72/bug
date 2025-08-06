"""
Verification routes for testing all systems
"""
from flask import jsonify, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import app, db
from models import *
from utils import admin_required
from werkzeug.security import generate_password_hash
import random
from datetime import datetime, timedelta

@app.route('/admin/setup-verification-data')
@login_required
@admin_required
def setup_verification_data():
    """Setup comprehensive test data for verification"""
    try:
        # Delete all non-admin users and their data
        User.query.filter_by(is_admin=False).delete()
        Stakes.query.delete()
        Deposit.query.delete() 
        Withdrawal.query.delete()
        SalaryWithdrawal.query.delete()
        
        # Get admin
        admin = User.query.filter_by(is_admin=True).first()
        
        # Create 25 test users with admin referral
        test_users = []
        for i in range(25):
            user = User(
                username=f'testuser{i+1:02d}',
                email=f'test{i+1:02d}@email.com',
                password_hash=generate_password_hash('test123'),
                phone_number=f'98765{i+1:05d}',
                referral_code=f'TEST{i+1:03d}',
                referred_by=admin.id,
                usdt_balance=random.randint(200, 1500),
                first_deposit_completed=True,
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 60))
            )
            test_users.append(user)
            db.session.add(user)
        
        db.session.flush()
        
        # Create deposits for users
        for user in test_users:
            num_deposits = random.randint(3, 15)
            for j in range(num_deposits):
                deposit = Deposit(
                    user_id=user.id,
                    amount=random.randint(50, 300),
                    transaction_id=f'TX{random.randint(100000, 999999)}',
                    status='approved',
                    network='BEP20',
                    created_at=datetime.utcnow() - timedelta(days=random.randint(1, 50)),
                    processed_at=datetime.utcnow() - timedelta(days=random.randint(1, 50))
                )
                db.session.add(deposit)
        
        # Create stakes for users
        coins = Coin.query.filter_by(active=True).all()
        if coins:
            for user in test_users:
                if random.random() < 0.8:  # 80% have stakes
                    num_stakes = random.randint(1, 4)
                    for _ in range(num_stakes):
                        coin = random.choice(coins)
                        stake_amount = random.randint(50, min(int(user.usdt_balance/3), 400))
                        
                        stake = Stakes(
                            user_id=user.id,
                            coin_id=coin.id,
                            amount=stake_amount,
                            duration_days=random.choice([7, 15, 30, 90, 120, 180]),
                            daily_return_rate=random.uniform(0.5, 2.5),
                            start_date=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                            status='active'
                        )
                        stake.end_date = stake.start_date + timedelta(days=stake.duration_days)
                        db.session.add(stake)
        
        # Create some withdrawals
        for user in test_users[:15]:  # First 15 users
            if random.random() < 0.6:
                withdrawal = Withdrawal(
                    user_id=user.id,
                    amount=random.randint(30, 200),
                    wallet_address=f'0x{random.randint(100000000, 999999999):x}',
                    network='BEP20',
                    status=random.choice(['pending', 'approved', 'rejected']),
                    created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
                )
                db.session.add(withdrawal)
        
        db.session.commit()
        
        # Get statistics
        user_count = User.query.filter_by(is_admin=False).count()
        referral_count = User.query.filter_by(referred_by=admin.id).count()
        deposit_count = Deposit.query.count()
        stake_count = Stakes.query.count()
        withdrawal_count = Withdrawal.query.count()
        
        flash(f'✅ Verification data created: {user_count} users, {referral_count} referrals, {deposit_count} deposits, {stake_count} stakes, {withdrawal_count} withdrawals', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error creating verification data: {str(e)}', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/verification-report')
@login_required
@admin_required
def verification_report():
    """Display comprehensive verification report"""
    
    # User statistics
    admin_count = User.query.filter_by(is_admin=True).count()
    user_count = User.query.filter_by(is_admin=False).count()
    
    # Referral statistics
    admin = User.query.filter_by(is_admin=True).first()
    referral_count = User.query.filter_by(referred_by=admin.id).count() if admin else 0
    
    # Financial statistics
    total_deposits = Deposit.query.count()
    approved_deposits = Deposit.query.filter_by(status='approved').count()
    pending_deposits = Deposit.query.filter_by(status='pending').count()
    
    total_stakes = Stakes.query.count()
    active_stakes = Stakes.query.filter_by(status='active').count()
    completed_stakes = Stakes.query.filter_by(status='completed').count()
    
    total_withdrawals = Withdrawal.query.count()
    pending_withdrawals = Withdrawal.query.filter_by(status='pending').count()
    approved_withdrawals = Withdrawal.query.filter_by(status='approved').count()
    
    # Balance calculations
    total_balance = db.session.query(db.func.sum(User.usdt_balance)).scalar() or 0
    total_stake_amount = db.session.query(db.func.sum(Stakes.amount)).filter_by(status='active').scalar() or 0
    
    # Coin statistics
    coin_count = Coin.query.filter_by(active=True).count()
    
    # Salary eligibility
    users_with_salary_eligibility = []
    for user in User.query.filter_by(is_admin=False).all():
        referral_count = User.query.filter_by(referred_by=user.id).count()
        total_balance = user.usdt_balance + (db.session.query(db.func.sum(Stakes.amount)).filter_by(user_id=user.id, status='active').scalar() or 0)
        
        # Check salary plan eligibility
        if referral_count >= 7 and total_balance >= 350:
            plan = 1 if referral_count < 13 else 2 if referral_count < 27 else 3 if referral_count < 46 else 4
            users_with_salary_eligibility.append((user, plan, referral_count, total_balance))
    
    stats = {
        'admin_count': admin_count,
        'user_count': user_count,
        'referral_count': referral_count,
        'total_deposits': total_deposits,
        'approved_deposits': approved_deposits,
        'pending_deposits': pending_deposits,
        'total_stakes': total_stakes,
        'active_stakes': active_stakes,
        'completed_stakes': completed_stakes,
        'total_withdrawals': total_withdrawals,
        'pending_withdrawals': pending_withdrawals,
        'approved_withdrawals': approved_withdrawals,
        'total_balance': total_balance,
        'total_stake_amount': total_stake_amount,
        'coin_count': coin_count,
        'salary_eligible_count': len(users_with_salary_eligibility),
        'salary_eligible_users': users_with_salary_eligibility
    }
    
    return render_template('admin/verification_report.html', stats=stats)