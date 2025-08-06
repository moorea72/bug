
"""
Routes for 2 Friends Premium Benefits System
"""

from flask import jsonify, request
from flask_login import login_required, current_user
from app import app, db
from models import User, Deposit, ActivityLog
from two_friends_system import TwoFriendsSystem

@app.route('/api/referral/progress')
@login_required
def get_referral_progress():
    """Get user's progress towards premium benefits"""
    try:
        progress = TwoFriendsSystem.get_user_referral_progress(current_user.id)
        
        if progress is None:
            return jsonify({'success': False, 'message': 'Error fetching progress'})
        
        return jsonify({
            'success': True,
            'progress': progress
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/referral/check-premium')
@login_required
def check_premium_status():
    """Check and update user's premium status"""
    try:
        is_premium = TwoFriendsSystem.check_user_premium_eligibility(current_user.id)
        
        return jsonify({
            'success': True,
            'is_premium': is_premium,
            'bonus_claimed': current_user.two_friends_bonus_claimed,
            'premium_benefits': {
                'no_withdrawal_fees': is_premium,
                'stake_commission': '2%' if is_premium else '0%',
                'bonus_amount': '20 USDT' if current_user.two_friends_bonus_claimed else 'Not claimed'
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/admin/update-premium-status', methods=['POST'])
@login_required
def admin_update_premium_status():
    """Admin route to update all users' premium status"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    try:
        updated_count = TwoFriendsSystem.update_all_premium_status()
        
        return jsonify({
            'success': True,
            'message': f'Updated premium status for {updated_count} users',
            'updated_count': updated_count
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/referral/stats')
@login_required
def get_referral_stats():
    """Get detailed referral statistics"""
    try:
        referrals = User.query.filter_by(referred_by=current_user.id).all()
        
        stats = {
            'total_referrals': len(referrals),
            'qualified_referrals': 0,
            'pending_referrals': 0,
            'referral_details': []
        }
        
        for referral in referrals:
            # Calculate total deposits
            total_deposits = db.session.query(db.func.sum(Deposit.amount)).filter_by(
                user_id=referral.id,
                status='approved'
            ).scalar() or 0
            
            is_qualified = total_deposits >= 100
            
            if is_qualified:
                stats['qualified_referrals'] += 1
            else:
                stats['pending_referrals'] += 1
            
            stats['referral_details'].append({
                'username': referral.username,
                'total_deposits': total_deposits,
                'is_qualified': is_qualified,
                'joined_date': referral.created_at.strftime('%Y-%m-%d'),
                'status': 'Qualified' if is_qualified else f'Needs ${100 - total_deposits:.2f} more'
            })
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
