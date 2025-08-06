from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import app, db
from models import (User, Notification, UserNotificationView, SalaryPlan, 
                   SupportResponse, Coin, StakingPlan, SupportTicket, SupportTicketReply)
from forms_admin import (NotificationForm, SalaryPlanForm, SupportResponseForm,
                        SupportTicketForm, SupportTicketReplyForm)
from datetime import datetime
import json
from flask import jsonify

# Admin access decorator
def admin_required(f):
    def comprehensive_admin_decorator(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    comprehensive_admin_decorator.__name__ = f.__name__
    return comprehensive_admin_decorator

@app.route('/admin/comprehensive')
@login_required
@admin_required
def admin_comprehensive():
    """Main admin dashboard with comprehensive overview"""
    # Get statistics
    total_users = User.query.count()
    total_notifications = Notification.query.filter_by(is_active=True).count()
    total_salary_plans = SalaryPlan.query.filter_by(is_active=True).count()
    total_support_responses = SupportResponse.query.filter_by(is_active=True).count()
    open_tickets = SupportTicket.query.filter_by(status='open').count()
    
    # Recent activities
    recent_notifications = Notification.query.order_by(Notification.created_at.desc()).limit(5).all()
    recent_tickets = SupportTicket.query.order_by(SupportTicket.created_at.desc()).limit(5).all()
    
    stats = {
        'total_users': total_users,
        'total_notifications': total_notifications,
        'total_salary_plans': total_salary_plans,
        'total_support_responses': total_support_responses,
        'open_tickets': open_tickets
    }
    
    return render_template('admin/comprehensive_dashboard.html', 
                         stats=stats, 
                         recent_notifications=recent_notifications,
                         recent_tickets=recent_tickets)

# Notification Management - All routes moved to routes.py to avoid duplication

# Salary Plan Management
@app.route('/admin/salary-plans')
@login_required
@admin_required
def admin_salary_plans():
    """Manage salary plans"""
    salary_plans = SalaryPlan.query.order_by(SalaryPlan.created_at.desc()).all()
    return render_template('admin/salary_plans.html', salary_plans=salary_plans)

@app.route('/admin/salary-plans/create', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_create_salary_plan():
    """Create new salary plan"""
    form = SalaryPlanForm()
    if form.validate_on_submit():
        salary_plan = SalaryPlan(
            plan_name=form.plan_name.data,
            referrals_required=form.referrals_required.data,
            balance_required=form.balance_required.data,
            monthly_salary=form.monthly_salary.data,
            is_active=form.is_active.data
        )
        db.session.add(salary_plan)
        db.session.commit()
        flash('Salary plan created successfully', 'success')
        return redirect(url_for('admin_salary_plans'))
    
    return render_template('admin/create_salary_plan.html', form=form)

@app.route('/admin/salary-plans/<int:plan_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_salary_plan(plan_id):
    """Edit salary plan"""
    salary_plan = SalaryPlan.query.get_or_404(plan_id)
    form = SalaryPlanForm(obj=salary_plan)
    
    if form.validate_on_submit():
        salary_plan.plan_name = form.plan_name.data
        salary_plan.referrals_required = form.referrals_required.data
        salary_plan.balance_required = form.balance_required.data
        salary_plan.monthly_salary = form.monthly_salary.data
        salary_plan.is_active = form.is_active.data
        salary_plan.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Salary plan updated successfully', 'success')
        return redirect(url_for('admin_salary_plans'))
    
    return render_template('admin/edit_salary_plan.html', form=form, salary_plan=salary_plan)

@app.route('/admin/salary-plans/<int:plan_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_salary_plan(plan_id):
    """Delete salary plan"""
    salary_plan = SalaryPlan.query.get_or_404(plan_id)
    db.session.delete(salary_plan)
    db.session.commit()
    flash('Salary plan deleted successfully', 'success')
    return redirect(url_for('admin_salary_plans'))

# Support Response Management
@app.route('/admin/support-responses')
@login_required
@admin_required
def admin_support_responses():
    """Manage support responses"""
    support_responses = SupportResponse.query.order_by(SupportResponse.priority.desc(), SupportResponse.created_at.desc()).all()
    return render_template('admin/support_responses.html', support_responses=support_responses)

@app.route('/admin/support-responses/create', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_create_support_response():
    """Create new support response"""
    form = SupportResponseForm()
    if form.validate_on_submit():
        support_response = SupportResponse(
            trigger_words=form.trigger_words.data,
            response_text=form.response_text.data,
            category=form.category.data,
            priority=form.priority.data,
            is_active=form.is_active.data,
            created_by=current_user.id
        )
        db.session.add(support_response)
        db.session.commit()
        flash('Support response created successfully', 'success')
        return redirect(url_for('admin_support_responses'))
    
    return render_template('admin/create_support_response.html', form=form)

@app.route('/admin/support-responses/<int:response_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_support_response(response_id):
    """Edit support response"""
    support_response = SupportResponse.query.get_or_404(response_id)
    form = SupportResponseForm(obj=support_response)
    
    if form.validate_on_submit():
        support_response.trigger_words = form.trigger_words.data
        support_response.response_text = form.response_text.data
        support_response.category = form.category.data
        support_response.priority = form.priority.data
        support_response.is_active = form.is_active.data
        support_response.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Support response updated successfully', 'success')
        return redirect(url_for('admin_support_responses'))
    
    return render_template('admin/edit_support_response.html', form=form, support_response=support_response)

@app.route('/admin/support-responses/<int:response_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_support_response(response_id):
    """Delete support response"""
    support_response = SupportResponse.query.get_or_404(response_id)
    db.session.delete(support_response)
    db.session.commit()
    flash('Support response deleted successfully', 'success')
    return redirect(url_for('admin_support_responses'))

# API Routes for Notification System
@app.route('/api/notifications')
@login_required
def api_notifications():
    """Get user notifications"""
    # Get unread notifications for current user
    viewed_notifications = db.session.query(UserNotificationView.notification_id).filter_by(
        user_id=current_user.id
    ).subquery()
    
    unread_notifications = Notification.query.filter(
        Notification.is_active == True,
        ~Notification.id.in_(viewed_notifications)
    ).order_by(Notification.created_at.desc()).limit(10).all()
    
    unread_count = len(unread_notifications)
    
    notifications_data = []
    for notification in unread_notifications:
        notifications_data.append(notification.to_dict())
    
    return jsonify({
        'notifications': notifications_data,
        'unread_count': unread_count
    })

@app.route('/api/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def api_mark_notification_read(notification_id):
    """Mark notification as read"""
    notification = Notification.query.get_or_404(notification_id)
    
    # Check if already viewed
    existing_view = UserNotificationView.query.filter_by(
        user_id=current_user.id,
        notification_id=notification_id
    ).first()
    
    if not existing_view:
        view = UserNotificationView(
            user_id=current_user.id,
            notification_id=notification_id
        )
        db.session.add(view)
        
        # Update view count
        notification.view_count += 1
        db.session.commit()
    
    return jsonify({'success': True})