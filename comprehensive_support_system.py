#!/usr/bin/env python3
"""
Comprehensive Support System Implementation
- Human support tickets with admin response system
- AI support with intelligent responses
- Admin support ticket management
- User can choose between AI or Human support
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import app, db
from models import User, SupportMessage, SupportResponse, Stake, Deposit, Withdrawal, Coin, StakingPlan
from datetime import datetime, timedelta
from functools import wraps
import json

support_bp = Blueprint('support', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_user_salary_info(user):
    """Get user's salary eligibility information"""
    referral_count = len([r for r in user.referrals if r.usdt_balance + sum(s.amount for s in r.stakes if s.status == 'active') >= 100])
    total_balance = user.usdt_balance + sum(s.amount for s in user.stakes if s.status == 'active')
    
    salary_plans = [
        {'plan': 'Plan 1', 'referrals_needed': 7, 'balance_needed': 350, 'monthly_salary': 50},
        {'plan': 'Plan 2', 'referrals_needed': 13, 'balance_needed': 680, 'monthly_salary': 110},
        {'plan': 'Plan 3', 'referrals_needed': 27, 'balance_needed': 960, 'monthly_salary': 230},
        {'plan': 'Plan 4', 'referrals_needed': 46, 'balance_needed': 1340, 'monthly_salary': 480}
    ]
    
    eligible_plans = []
    for plan in salary_plans:
        if referral_count >= plan['referrals_needed'] and total_balance >= plan['balance_needed']:
            eligible_plans.append(plan)
    
    return {
        'current_referrals': referral_count,
        'current_balance': total_balance,
        'eligible_plans': eligible_plans,
        'all_plans': salary_plans
    }

def get_user_referral_info(user):
    """Get user's referral commission information"""
    referrals = user.referrals
    total_commission = 0
    
    for referral in referrals:
        if referral.usdt_balance + sum(s.amount for s in referral.stakes if s.status == 'active') >= 100:
            total_commission += referral.usdt_balance * 0.05  # 5% commission
    
    return {
        'total_referrals': len(referrals),
        'active_referrals': len([r for r in referrals if r.usdt_balance + sum(s.amount for s in r.stakes if s.status == 'active') >= 100]),
        'total_commission': total_commission,
        'commission_rate': '5%'
    }

def get_user_stake_info(user):
    """Get user's stake information"""
    stakes = user.stakes
    stake_info = []
    
    for stake in stakes:
        unlock_date = stake.created_at + timedelta(days=stake.plan.duration_days)
        days_remaining = (unlock_date - datetime.utcnow()).days
        
        stake_info.append({
            'coin': stake.coin.symbol,
            'amount': stake.amount,
            'duration': stake.plan.duration_days,
            'daily_rate': stake.plan.interest_rate,
            'current_earnings': stake.calculate_current_return(),
            'unlock_date': unlock_date.strftime('%Y-%m-%d'),
            'days_remaining': max(0, days_remaining),
            'status': stake.status
        })
    
    return stake_info

def get_ai_response(message, user):
    """Get AI response based on user message"""
    message_lower = message.lower()
    
    # Salary information
    if any(word in message_lower for word in ['salary', 'plan', 'monthly', 'payment']):
        salary_info = get_user_salary_info(user)
        response = f"""
        <div class="ai-response">
            <h4>💰 Your Salary Eligibility Status</h4>
            <p><strong>Current Referrals:</strong> {salary_info['current_referrals']}</p>
            <p><strong>Current Balance:</strong> ${salary_info['current_balance']:.2f} USDT</p>
            
            <h5>📋 Salary Plans Available:</h5>
            <ul>
        """
        
        for plan in salary_info['all_plans']:
            eligible = plan in salary_info['eligible_plans']
            status = "✅ ELIGIBLE" if eligible else "❌ Not Eligible"
            response += f"""
                <li>
                    <strong>{plan['plan']}</strong> - ${plan['monthly_salary']}/month {status}<br>
                    Requires: {plan['referrals_needed']} referrals + ${plan['balance_needed']} balance
                </li>
            """
        
        response += """
            </ul>
            <p><em>Salary is paid automatically on the 1st of each month for eligible users.</em></p>
        </div>
        """
        return response
    
    # Referral information
    elif any(word in message_lower for word in ['referral', 'commission', 'refer']):
        referral_info = get_user_referral_info(user)
        response = f"""
        <div class="ai-response">
            <h4>👥 Your Referral Information</h4>
            <p><strong>Total Referrals:</strong> {referral_info['total_referrals']}</p>
            <p><strong>Active Referrals:</strong> {referral_info['active_referrals']} (with 100+ USDT balance)</p>
            <p><strong>Commission Rate:</strong> {referral_info['commission_rate']} per referral</p>
            <p><strong>Total Commission Earned:</strong> ${referral_info['total_commission']:.2f} USDT</p>
            
            <h5>📋 Referral Benefits:</h5>
            <ul>
                <li>Earn 5% commission on each referral's balance</li>
                <li>Commission awarded when referral reaches 100+ USDT</li>
                <li>Commission remains permanent even if balance drops</li>
                <li>2+ referrals = Premium benefits (no withdrawal fees)</li>
            </ul>
        </div>
        """
        return response
    
    # Stake information
    elif any(word in message_lower for word in ['stake', 'investment', 'unlock', 'earnings']):
        stake_info = get_user_stake_info(user)
        response = f"""
        <div class="ai-response">
            <h4>📊 Your Staking Information</h4>
        """
        
        if stake_info:
            response += "<h5>🎯 Active Stakes:</h5><ul>"
            for stake in stake_info:
                response += f"""
                    <li>
                        <strong>{stake['coin']}</strong> - ${stake['amount']:.2f}<br>
                        Duration: {stake['duration']} days | Daily: {stake['daily_rate']}%<br>
                        Current Earnings: ${stake['current_earnings']:.2f}<br>
                        Unlock Date: {stake['unlock_date']} ({stake['days_remaining']} days remaining)<br>
                        Status: {stake['status']}
                    </li>
                """
            response += "</ul>"
        else:
            response += "<p>You don't have any active stakes currently.</p>"
        
        response += """
            <h5>📋 Staking Benefits:</h5>
            <ul>
                <li>Daily returns from 0.5% to 2.0%</li>
                <li>Multiple duration options (7-180 days)</li>
                <li>Automatic profit calculation</li>
                <li>Early unlock available after 50% duration</li>
            </ul>
        </div>
        """
        return response
    
    # Balance information
    elif any(word in message_lower for word in ['balance', 'wallet', 'money', 'funds']):
        total_staked = sum(s.amount for s in user.stakes if s.status == 'active')
        total_earnings = sum(s.calculate_current_return() for s in user.stakes if s.status == 'active')
        response = f"""
        <div class="ai-response">
            <h4>💳 Your Account Balance</h4>
            <p><strong>Available Balance:</strong> ${user.usdt_balance:.2f} USDT</p>
            <p><strong>Total Staked:</strong> ${total_staked:.2f} USDT</p>
            <p><strong>Current Earnings:</strong> ${total_earnings:.2f} USDT</p>
            <p><strong>Total Portfolio:</strong> ${user.usdt_balance + total_staked + total_earnings:.2f} USDT</p>
            
            <h5>📋 Account Summary:</h5>
            <ul>
                <li>Referral Bonus: ${user.referral_bonus:.2f} USDT</li>
                <li>Total Earned: ${user.total_earned:.2f} USDT</li>
                <li>Active Stakes: {len([s for s in user.stakes if s.status == 'active'])}</li>
                <li>Premium Member: {'Yes' if user.has_two_referrals() else 'No'}</li>
            </ul>
        </div>
        """
        return response
    
    # Default response for other queries
    else:
        return """
        <div class="ai-response">
            <h4>🤖 AI Assistant</h4>
            <p>I can help you with information about:</p>
            <ul>
                <li><strong>Salary</strong> - Check your eligibility and plans</li>
                <li><strong>Referrals</strong> - View commission and benefits</li>
                <li><strong>Stakes</strong> - Check your investments and earnings</li>
                <li><strong>Balance</strong> - View your account details</li>
            </ul>
            <p>Try asking: "What's my salary status?" or "Show my stake details"</p>
        </div>
        """

# Register the blueprint
app.register_blueprint(support_bp)

print("Comprehensive Support System Blueprint Created Successfully!")