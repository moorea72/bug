# Advanced Admin System - Error-free and Dynamic
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime
from app import app, db
from models import User, Coin, StakingPlan, Stake, Deposit, Withdrawal, PlatformSettings, ActivityLog, PaymentAddress, ContentSection, SupportMessage, NFT, NFTCollection
from utils import admin_required, log_activity
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, BooleanField, SelectField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, NumberRange, Length, Optional
from flask_wtf.file import FileField, FileAllowed

# Advanced Forms
class AdvancedCoinForm(FlaskForm):
    """Advanced coin management form"""
    symbol = StringField('Symbol', validators=[DataRequired(), Length(max=10)])
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    min_stake = FloatField('Minimum Stake', validators=[DataRequired(), NumberRange(min=0)])
    icon_emoji = StringField('Icon Emoji', validators=[Optional(), Length(max=10)])
    daily_return_rate = FloatField('Daily Return Rate (%)', validators=[DataRequired(), NumberRange(min=0, max=20)])
    active = BooleanField('Active', default=True)

class AdvancedStakingPlanForm(FlaskForm):
    """Advanced staking plan form"""
    coin_id = SelectField('Coin', coerce=int, validators=[DataRequired()])
    duration_days = IntegerField('Duration (Days)', validators=[DataRequired(), NumberRange(min=1, max=365)])
    interest_rate = FloatField('Interest Rate (%)', validators=[DataRequired(), NumberRange(min=0, max=20)])
    active = BooleanField('Active', default=True)

class AdvancedUserForm(FlaskForm):
    """Advanced user management form"""
    username = StringField('Username', validators=[DataRequired(), Length(max=64)])
    email = StringField('Email', validators=[DataRequired(), Length(max=120)])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(max=20)])
    usdt_balance = FloatField('USDT Balance', validators=[DataRequired(), NumberRange(min=0)])
    is_admin = BooleanField('Admin Status')
    is_active = BooleanField('Active Status', default=True)

class AdvancedSettingsForm(FlaskForm):
    """Advanced platform settings form"""
    site_name = StringField('Site Name', validators=[DataRequired(), Length(max=100)])
    min_deposit = FloatField('Minimum Deposit', validators=[DataRequired(), NumberRange(min=0)])
    min_withdrawal = FloatField('Minimum Withdrawal', validators=[DataRequired(), NumberRange(min=0)])
    withdrawal_fee = FloatField('Withdrawal Fee (%)', validators=[DataRequired(), NumberRange(min=0, max=10)])
    referral_level_1 = FloatField('Referral Level 1 (%)', validators=[DataRequired(), NumberRange(min=0, max=50)])
    min_referral_activation = FloatField('Min Referral Activation', validators=[DataRequired(), NumberRange(min=0)])

# Advanced Coin Management
@app.route('/admin/advanced/coins')
@login_required
@admin_required
def admin_advanced_coins():
    """Advanced coin management page"""
    coins = Coin.query.all()
    return render_template('admin/advanced/coins.html', coins=coins)

@app.route('/admin/advanced/coins/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_advanced_add_coin():
    """Add new coin with advanced features"""
    form = AdvancedCoinForm()
    
    if form.validate_on_submit():
        try:
            coin = Coin(
                symbol=form.symbol.data.upper(),
                name=form.name.data,
                min_stake=form.min_stake.data,
                icon_emoji=form.icon_emoji.data or '💰',
                daily_return_rate=form.daily_return_rate.data,
                active=form.active.data
            )
            
            db.session.add(coin)
            db.session.commit()
            
            log_activity(current_user.id, 'admin_add_coin', f'Added coin {coin.symbol}')
            flash(f'Coin {coin.symbol} added successfully!', 'success')
            return redirect(url_for('admin_advanced_coins'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding coin: {str(e)}', 'error')
    
    return render_template('admin/advanced/coin_form.html', form=form, title='Add Coin')

@app.route('/admin/advanced/coins/edit/<int:coin_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_advanced_edit_coin(coin_id):
    """Edit coin with advanced features"""
    coin = Coin.query.get_or_404(coin_id)
    form = AdvancedCoinForm(obj=coin)
    
    if form.validate_on_submit():
        try:
            coin.symbol = form.symbol.data.upper()
            coin.name = form.name.data
            coin.min_stake = form.min_stake.data
            coin.icon_emoji = form.icon_emoji.data or '💰'
            coin.daily_return_rate = form.daily_return_rate.data
            coin.active = form.active.data
            
            db.session.commit()
            
            log_activity(current_user.id, 'admin_edit_coin', f'Edited coin {coin.symbol}')
            flash(f'Coin {coin.symbol} updated successfully!', 'success')
            return redirect(url_for('admin_advanced_coins'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating coin: {str(e)}', 'error')
    
    return render_template('admin/advanced/coin_form.html', form=form, coin=coin, title='Edit Coin')

# Advanced Staking Plans Management
@app.route('/admin/advanced/staking-plans')
@login_required
@admin_required
def admin_advanced_staking_plans():
    """Advanced staking plans management"""
    plans = StakingPlan.query.all()
    coins = Coin.query.filter_by(active=True).all()
    return render_template('admin/advanced/staking_plans.html', plans=plans, coins=coins)

@app.route('/admin/advanced/staking-plans/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_advanced_add_staking_plan():
    """Add new staking plan"""
    form = AdvancedStakingPlanForm()
    coins = Coin.query.filter_by(active=True).all()
    form.coin_id.choices = [(coin.id, f"{coin.symbol} - {coin.name}") for coin in coins]
    
    if form.validate_on_submit():
        try:
            plan = StakingPlan(
                coin_id=form.coin_id.data,
                duration_days=form.duration_days.data,
                interest_rate=form.interest_rate.data,
                active=form.active.data
            )
            
            db.session.add(plan)
            db.session.commit()
            
            log_activity(current_user.id, 'admin_add_plan', f'Added staking plan {plan.duration_days} days')
            flash('Staking plan added successfully!', 'success')
            return redirect(url_for('admin_advanced_staking_plans'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding staking plan: {str(e)}', 'error')
    
    return render_template('admin/advanced/staking_plan_form.html', form=form, title='Add Staking Plan')

@app.route('/admin/advanced/staking-plans/edit/<int:plan_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_advanced_edit_staking_plan(plan_id):
    """Edit staking plan"""
    plan = StakingPlan.query.get_or_404(plan_id)
    form = AdvancedStakingPlanForm(obj=plan)
    coins = Coin.query.filter_by(active=True).all()
    form.coin_id.choices = [(coin.id, f"{coin.symbol} - {coin.name}") for coin in coins]
    
    if form.validate_on_submit():
        try:
            plan.coin_id = form.coin_id.data
            plan.duration_days = form.duration_days.data
            plan.interest_rate = form.interest_rate.data
            plan.active = form.active.data
            
            db.session.commit()
            
            log_activity(current_user.id, 'admin_edit_plan', f'Edited staking plan {plan.duration_days} days')
            flash('Staking plan updated successfully!', 'success')
            return redirect(url_for('admin_advanced_staking_plans'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating staking plan: {str(e)}', 'error')
    
    return render_template('admin/advanced/staking_plan_form.html', form=form, plan=plan, title='Edit Staking Plan')

# Advanced User Management
@app.route('/admin/advanced/users')
@login_required
@admin_required
def admin_advanced_users():
    """Advanced user management"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = User.query
    if search:
        query = query.filter(
            (User.username.contains(search)) |
            (User.email.contains(search)) |
            (User.phone_number.contains(search))
        )
    
    users = query.paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/advanced/users.html', users=users, search=search)

@app.route('/admin/advanced/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_advanced_edit_user(user_id):
    """Edit user with advanced features"""
    user = User.query.get_or_404(user_id)
    form = AdvancedUserForm(obj=user)
    
    if form.validate_on_submit():
        try:
            user.username = form.username.data
            user.email = form.email.data
            user.phone_number = form.phone_number.data
            user.usdt_balance = form.usdt_balance.data
            user.is_admin = form.is_admin.data
            user.is_active = form.is_active.data
            
            db.session.commit()
            
            log_activity(current_user.id, 'admin_edit_user', f'Edited user {user.username}')
            flash(f'User {user.username} updated successfully!', 'success')
            return redirect(url_for('admin_advanced_users'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating user: {str(e)}', 'error')
    
    return render_template('admin/advanced/user_form.html', form=form, user=user, title='Edit User')

# Advanced Platform Settings
@app.route('/admin/advanced/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_advanced_settings():
    """Advanced platform settings"""
    form = AdvancedSettingsForm()
    
    # Load current settings
    settings = PlatformSettings.get_all_settings()
    if request.method == 'GET':
        form.site_name.data = settings.get('site_name', 'USDT Staking Platform')
        form.min_deposit.data = float(settings.get('min_deposit', 10))
        form.min_withdrawal.data = float(settings.get('min_withdrawal', 5))
        form.withdrawal_fee.data = float(settings.get('withdrawal_fee', 1))
        form.referral_level_1.data = float(settings.get('referral_level_1', 5))
        form.min_referral_activation.data = float(settings.get('min_referral_activation', 100))
    
    if form.validate_on_submit():
        try:
            # Update all settings
            PlatformSettings.set_setting('site_name', form.site_name.data)
            PlatformSettings.set_setting('min_deposit', str(form.min_deposit.data))
            PlatformSettings.set_setting('min_withdrawal', str(form.min_withdrawal.data))
            PlatformSettings.set_setting('withdrawal_fee', str(form.withdrawal_fee.data))
            PlatformSettings.set_setting('referral_level_1', str(form.referral_level_1.data))
            PlatformSettings.set_setting('min_referral_activation', str(form.min_referral_activation.data))
            
            log_activity(current_user.id, 'admin_update_settings', 'Updated platform settings')
            flash('Platform settings updated successfully!', 'success')
            return redirect(url_for('admin_advanced_settings'))
            
        except Exception as e:
            flash(f'Error updating settings: {str(e)}', 'error')
    
    return render_template('admin/advanced/settings.html', form=form)

# Quick Stats API
@app.route('/admin/advanced/api/stats')
@login_required
@admin_required
def admin_advanced_stats_api():
    """API endpoint for dashboard stats"""
    try:
        stats = {
            'total_users': User.query.count(),
            'active_users': User.query.filter_by(is_active=True).count(),
            'total_stakes': Stake.query.count(),
            'total_deposits': Deposit.query.count(),
            'total_withdrawals': Withdrawal.query.count(),
            'pending_deposits': Deposit.query.filter_by(status='pending').count(),
            'pending_withdrawals': Withdrawal.query.filter_by(status='pending').count(),
            'total_staked_amount': db.session.query(db.func.sum(Stake.amount)).scalar() or 0,
            'platform_balance': db.session.query(db.func.sum(User.usdt_balance)).scalar() or 0
        }
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Batch Operations
@app.route('/admin/advanced/users/batch-action', methods=['POST'])
@login_required
@admin_required
def admin_advanced_batch_user_action():
    """Batch operations on users"""
    try:
        data = request.get_json()
        action = data.get('action')
        user_ids = data.get('user_ids', [])
        
        if not user_ids:
            return jsonify({'error': 'No users selected'}), 400
        
        users = User.query.filter(User.id.in_(user_ids)).all()
        
        if action == 'activate':
            for user in users:
                user.is_active = True
            message = f'Activated {len(users)} users'
        elif action == 'deactivate':
            for user in users:
                if not user.is_admin:  # Don't deactivate admin users
                    user.is_active = False
            message = f'Deactivated {len(users)} users'
        else:
            return jsonify({'error': 'Invalid action'}), 400
        
        db.session.commit()
        log_activity(current_user.id, 'admin_batch_action', message)
        
        return jsonify({'success': True, 'message': message})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500