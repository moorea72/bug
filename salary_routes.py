"""
Routes for salary system
"""
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import app, db
from models import User, SalaryWithdrawal
from salary_forms import SalaryWalletForm, AdminSalaryApprovalForm
from salary_system import get_salary_progress, check_salary_eligibility, create_salary_withdrawal_request, SalaryPlan
from utils import admin_required, log_activity
from datetime import datetime

@app.route('/salary-dashboard')
@login_required
def salary_dashboard():
    """Main salary dashboard for users"""
    progress = get_salary_progress(current_user)
    eligible_plan, active_referrals, total_balance = check_salary_eligibility(current_user)
    
    # Get user's recent salary withdrawals
    recent_withdrawals = SalaryWithdrawal.query.filter_by(user_id=current_user.id)\
                                               .order_by(SalaryWithdrawal.created_at.desc())\
                                               .limit(5).all()
    
    return render_template('salary_dashboard.html',
                         progress=progress,
                         eligible_plan=eligible_plan,
                         active_referrals=active_referrals,
                         total_balance=total_balance,
                         recent_withdrawals=recent_withdrawals,
                         salary_plans=SalaryPlan.PLANS)

@app.route('/set-salary-wallet', methods=['GET', 'POST'])
@login_required
def set_salary_wallet():
    """Set or update salary wallet address"""
    form = SalaryWalletForm()
    
    if form.validate_on_submit():
        # Only allow setting once, no editing
        if current_user.salary_wallet_address:
            flash('Salary wallet address can only be set once and cannot be changed.', 'error')
            return redirect(url_for('salary_dashboard'))
        
        current_user.salary_wallet_address = form.wallet_address.data
        db.session.commit()
        
        log_activity(current_user.id, 'salary_wallet_set', f'Set salary wallet: {form.wallet_address.data}')
        flash('Salary wallet address saved successfully!', 'success')
        return redirect(url_for('salary_dashboard'))
    
    # Pre-fill form if address exists
    if current_user.salary_wallet_address and request.method == 'GET':
        form.wallet_address.data = current_user.salary_wallet_address
    
    return render_template('set_salary_wallet.html', form=form)

@app.route('/request-salary-payment')
@login_required
def request_salary_payment():
    """Request salary payment (automatic if eligible)"""
    if not current_user.salary_wallet_address:
        flash('Please set your salary wallet address first.', 'error')
        return redirect(url_for('set_salary_wallet'))
    
    eligible_plan, active_referrals, total_balance = check_salary_eligibility(current_user)
    
    if not eligible_plan:
        flash('You are not eligible for any salary plan. Check requirements.', 'error')
        return redirect(url_for('salary_dashboard'))
    
    # Create automatic salary withdrawal request
    salary_request = create_salary_withdrawal_request(current_user, eligible_plan)
    
    if salary_request:
        flash(f'Salary payment request submitted! Plan {eligible_plan} - ${SalaryPlan.PLANS[eligible_plan]["monthly_salary"]} will be processed by admin within 1 day.', 'success')
        log_activity(current_user.id, 'salary_request', f'Requested salary payment for Plan {eligible_plan}')
    else:
        flash('You already have a pending salary request for this month.', 'warning')
    
    return redirect(url_for('salary_dashboard'))

# Admin Routes
@app.route('/admin/salary-dashboard')
@login_required
@admin_required
def admin_salary_dashboard():
    """Main admin salary dashboard"""
    from datetime import datetime, timedelta
    
    pending_requests = SalaryWithdrawal.query.filter_by(status='pending')\
                                            .order_by(SalaryWithdrawal.created_at.desc()).all()
    
    processed_requests = SalaryWithdrawal.query.filter(SalaryWithdrawal.status.in_(['approved', 'rejected']))\
                                              .order_by(SalaryWithdrawal.processed_at.desc())\
                                              .limit(20).all()
    
    # Get this month's paid requests
    current_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    paid_this_month = SalaryWithdrawal.query.filter(
        SalaryWithdrawal.status == 'approved',
        SalaryWithdrawal.processed_at >= current_month
    ).all()
    
    return render_template('admin/salary_dashboard.html',
                         pending_requests=pending_requests,
                         processed_requests=processed_requests,
                         paid_this_month=paid_this_month,
                         salary_plans=SalaryPlan.PLANS)

@app.route('/admin/salary-requests')
@login_required
@admin_required
def admin_salary_requests():
    """Admin view of all salary withdrawal requests"""
    pending_requests = SalaryWithdrawal.query.filter_by(status='pending')\
                                            .order_by(SalaryWithdrawal.created_at.desc()).all()
    
    processed_requests = SalaryWithdrawal.query.filter(SalaryWithdrawal.status.in_(['approved', 'rejected']))\
                                              .order_by(SalaryWithdrawal.processed_at.desc())\
                                              .limit(20).all()
    
    return render_template('admin/salary_requests.html',
                         pending_requests=pending_requests,
                         processed_requests=processed_requests,
                         salary_plans=SalaryPlan.PLANS)

@app.route('/admin/salary-requests/<int:request_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_process_salary_request(request_id):
    """Process individual salary request"""
    salary_request = SalaryWithdrawal.query.get_or_404(request_id)
    form = AdminSalaryApprovalForm()
    
    if form.validate_on_submit():
        salary_request.status = form.status.data
        salary_request.transaction_hash = form.transaction_hash.data
        salary_request.admin_notes = form.admin_notes.data
        salary_request.processed_at = datetime.utcnow()
        salary_request.processed_by = current_user.id
        
        db.session.commit()
        
        log_activity(current_user.id, 'salary_processed', 
                    f'Processed salary request #{request_id} - Status: {form.status.data}')
        
        flash(f'Salary request {form.status.data} successfully!', 'success')
        return redirect(url_for('admin_salary_requests'))
    
    return render_template('admin/process_salary_request.html',
                         salary_request=salary_request,
                         form=form,
                         salary_plans=SalaryPlan.PLANS)

@app.route('/admin/salary-requests/<int:request_id>/quick-approve', methods=['POST'])
@login_required
@admin_required
def admin_quick_approve_salary(request_id):
    """Quick approve salary request"""
    try:
        data = request.get_json()
        transaction_hash = data.get('transaction_hash')
        
        if not transaction_hash:
            return jsonify({'success': False, 'message': 'Transaction hash is required'})
        
        salary_request = SalaryWithdrawal.query.get_or_404(request_id)
        
        if salary_request.status != 'pending':
            return jsonify({'success': False, 'message': 'Request is not pending'})
        
        salary_request.status = 'approved'
        salary_request.transaction_hash = transaction_hash
        salary_request.processed_at = datetime.utcnow()
        salary_request.processed_by = current_user.id
        salary_request.admin_notes = 'Quick approved via dashboard'
        
        db.session.commit()
        
        log_activity(current_user.id, 'salary_quick_approved', 
                    f'Quick approved salary request #{request_id} - TX: {transaction_hash}')
        
        return jsonify({'success': True, 'message': 'Salary request approved successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/admin/salary-requests/<int:request_id>/quick-reject', methods=['POST'])
@login_required
@admin_required
def admin_quick_reject_salary(request_id):
    """Quick reject salary request"""
    try:
        salary_request = SalaryWithdrawal.query.get_or_404(request_id)
        
        if salary_request.status != 'pending':
            return jsonify({'success': False, 'message': 'Request is not pending'})
        
        salary_request.status = 'rejected'
        salary_request.processed_at = datetime.utcnow()
        salary_request.processed_by = current_user.id
        salary_request.admin_notes = 'Quick rejected via dashboard'
        
        db.session.commit()
        
        log_activity(current_user.id, 'salary_quick_rejected', 
                    f'Quick rejected salary request #{request_id}')
        
        return jsonify({'success': True, 'message': 'Salary request rejected'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/api/salary-progress')
@login_required
def api_salary_progress():
    """API endpoint for real-time salary progress"""
    progress = get_salary_progress(current_user)
    eligible_plan, active_referrals, total_balance = check_salary_eligibility(current_user)
    
    return jsonify({
        'progress': progress,
        'eligible_plan': eligible_plan,
        'active_referrals': active_referrals,
        'total_balance': total_balance,
        'has_wallet': bool(current_user.salary_wallet_address)
    })