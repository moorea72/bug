
"""
Admin routes for managing referral commission system
"""

from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required
from app import app
from models import User, ReferralCommission
from utils import admin_required
from referral_commission_system import ReferralCommissionSystem

@app.route('/admin/referral-commissions')
@login_required
@admin_required
def admin_referral_commissions():
    """View all referral commissions"""
    # Get filter parameters
    user_filter = request.args.get('user', '')
    
    # Base query
    query = ReferralCommission.query
    
    # Apply user filter if provided
    if user_filter:
        users = User.query.filter(User.username.contains(user_filter)).all()
        user_ids = [u.id for u in users]
        query = query.filter(ReferralCommission.referrer_id.in_(user_ids))
    
    # Get commissions with pagination
    page = request.args.get('page', 1, type=int)
    commissions = query.order_by(ReferralCommission.created_at.desc()).paginate(
        page=page, per_page=50, error_out=False
    )
    
    # Get system statistics
    system_stats = ReferralCommissionSystem.get_system_stats()
    
    return render_template('admin/referral_commissions.html', 
                         commissions=commissions, 
                         system_stats=system_stats,
                         user_filter=user_filter)

@app.route('/admin/referral-commissions/user/<int:user_id>')
@login_required
@admin_required
def admin_user_referral_commissions(user_id):
    """View referral commissions for specific user"""
    user = User.query.get_or_404(user_id)
    stats = ReferralCommissionSystem.get_referrer_commission_stats(user_id)
    
    return render_template('admin/user_referral_commissions.html', 
                         user=user, 
                         stats=stats)

@app.route('/api/admin/referral-commission-stats')
@login_required
@admin_required
def api_referral_commission_stats():
    """API endpoint for referral commission statistics"""
    stats = ReferralCommissionSystem.get_system_stats()
    return jsonify(stats)
