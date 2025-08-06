"""
Admin Support Response Management System
Allows admins to add, edit, and manage support responses
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from models import SupportResponse, User
from functools import wraps

support_responses_bp = Blueprint('support_responses', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@support_responses_bp.route('/admin/support-responses')
@login_required
@admin_required
def admin_support_responses():
    """Admin page to manage support responses"""
    responses = SupportResponse.query.all()
    return render_template('admin/support_responses.html', responses=responses)

@support_responses_bp.route('/admin/support-responses/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_support_response():
    """Add new support response"""
    if request.method == 'POST':
        trigger_words = request.form.get('trigger_words')
        response_text = request.form.get('response_text')
        category = request.form.get('category', 'general')
        is_active = 'is_active' in request.form
        
        if trigger_words and response_text:
            new_response = SupportResponse(
                trigger_words=trigger_words,
                response_text=response_text,
                category=category,
                is_active=is_active,
                created_by=current_user.id
            )
            
            try:
                db.session.add(new_response)
                db.session.commit()
                flash('Support response added successfully!', 'success')
                return redirect(url_for('support_responses.admin_support_responses'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error adding response: {str(e)}', 'error')
        else:
            flash('Please fill all required fields.', 'error')
    
    return render_template('admin/support_response_form.html')

@support_responses_bp.route('/admin/support-responses/edit/<int:response_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_support_response(response_id):
    """Edit existing support response"""
    response = SupportResponse.query.get_or_404(response_id)
    
    if request.method == 'POST':
        response.trigger_words = request.form.get('trigger_words')
        response.response_text = request.form.get('response_text')
        response.category = request.form.get('category', 'general')
        response.is_active = 'is_active' in request.form
        
        try:
            db.session.commit()
            flash('Support response updated successfully!', 'success')
            return redirect(url_for('support_responses.admin_support_responses'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating response: {str(e)}', 'error')
    
    return render_template('admin/support_response_form.html', response=response)

@support_responses_bp.route('/admin/support-responses/delete/<int:response_id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_support_response(response_id):
    """Delete support response"""
    response = SupportResponse.query.get_or_404(response_id)
    
    try:
        db.session.delete(response)
        db.session.commit()
        flash('Support response deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting response: {str(e)}', 'error')
    
    return redirect(url_for('support_responses.admin_support_responses'))

@support_responses_bp.route('/api/support-response')
def get_support_response():
    """API endpoint to get support response based on user message"""
    message = request.args.get('message', '').lower()
    
    # Special case for human support
    if any(word in message for word in ['human support', 'human help', 'live support', 'talk to human']):
        return jsonify({
            'response': """### 🤝 Connect with Human Support Team<br><br>
                          For personalized assistance, please contact our support team:<br><br>
                          📱 **Telegram Support Bot**: <a href="https://t.me/YourSupportBot" target="_blank" class="text-blue-600 font-semibold">@YourSupportBot</a><br>
                          ⚡ **Instant Response**: Available 24/7<br>
                          👥 **Live Chat**: Direct connection to support agents<br><br>
                          Click the link above to get immediate assistance from our human support team!""",
            'category': 'human_support'
        })
    
    # Find matching response from database
    responses = SupportResponse.query.filter_by(is_active=True).all()
    
    for response in responses:
        trigger_words = [word.strip().lower() for word in response.trigger_words.split(',')]
        if any(trigger in message for trigger in trigger_words):
            return jsonify({
                'response': response.response_text,
                'category': response.category
            })
    
    # Default response if no match found
    return jsonify({
        'response': """### 🤖 AI Assistant Ready to Help<br><br>
                      I can help you with:<br>
                      • Account analysis and summaries<br>
                      • Staking performance reviews<br>
                      • Deposit and withdrawal guidance<br>
                      • Investment strategy optimization<br><br>
                      Try asking specific questions about your account or type "human support" for live assistance!""",
        'category': 'default'
    })