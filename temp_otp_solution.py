"""
Temporary OTP Solution for Fast2SMS Balance Issue
This provides admin interface to manually send OTP when balance is low
"""
from flask import render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_required, current_user
from app import app, db
from models import User
from fast2sms_service import sms_service, store_otp
from utils import admin_required
import random
import string

@app.route('/admin/send-manual-otp', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_manual_otp():
    """Admin interface to manually send OTP when Fast2SMS balance is low"""
    if request.method == 'POST':
        phone_number = request.form.get('phone_number')
        
        if not phone_number:
            flash('Phone number is required', 'error')
            return redirect(url_for('admin_manual_otp'))
        
        # Clean phone number
        phone_clean = phone_number.replace('+91', '').replace('+', '').replace(' ', '').strip()
        
        # Generate OTP
        otp = ''.join(random.choices(string.digits, k=6))
        
        # Store OTP in session
        store_otp(phone_clean, otp)
        
        flash(f'OTP {otp} generated for {phone_clean}. Please manually send this to user.', 'success')
        return redirect(url_for('admin_manual_otp'))
    
    return render_template('admin/manual_otp.html')

@app.route('/admin/check-pending-otps')
@login_required  
@admin_required
def admin_check_pending_otps():
    """Check all pending OTPs in session"""
    pending_otps = []
    
    # Get all OTP sessions
    for key in session.keys():
        if key.startswith('otp_'):
            phone = key.replace('otp_', '')
            otp_data = session[key]
            pending_otps.append({
                'phone': phone,
                'otp': otp_data.get('otp'),
                'timestamp': otp_data.get('timestamp')
            })
    
    return jsonify({'pending_otps': pending_otps})