"""
OTP Routes for Fast2SMS integration
"""
from flask import render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_required, current_user
from app import app, db
from models import User
from otp_forms import OTPRequestForm, OTPVerifyForm, EnhancedRegistrationForm, QuickSalaryApprovalForm
from fast2sms_service import sms_service, store_otp, verify_otp, clear_otp
from utils import admin_required, log_activity
from werkzeug.security import generate_password_hash
import uuid

@app.route('/send-otp', methods=['POST'])
def send_otp():
    """Send OTP to phone number"""
    try:
        data = request.get_json()
        phone_number = data.get('phone_number')
        
        if not phone_number:
            return jsonify({'success': False, 'message': 'Phone number is required'})
        
        # Clean phone number
        phone_clean = phone_number.replace('+91', '').replace('+', '').replace(' ', '').strip()
        
        # Validate phone number format
        if not phone_clean.isdigit() or len(phone_clean) != 10:
            return jsonify({'success': False, 'message': 'Please enter a valid 10-digit phone number'})
        
        # Check if phone number already exists
        existing_user = User.query.filter_by(phone_number=phone_clean).first()
        if existing_user:
            return jsonify({'success': False, 'message': 'This phone number is already registered. Please use a different number or try to login.'})
        
        # Generate OTP
        otp = sms_service.generate_otp()
        
        # Send OTP via Fast2SMS
        success, message = sms_service.send_otp(phone_clean, otp)
        
        if success:
            # Store OTP in session
            store_otp(phone_clean, otp)
            return jsonify({'success': True, 'message': 'OTP sent successfully to your phone'})
        else:
            # Check if it's a balance issue, sender ID issue, or other error
            if 'balance' in message.lower() or 'HTTP 400' in message:
                print(f"\n{'='*50}")
                print(f"🚨 FAST2SMS OTP BALANCE LOW - MANUAL OTP REQUIRED")
                print(f"📱 Phone: {phone_clean}")
                print(f"🔐 OTP: {otp}")
                print(f"⏰ Valid for 5 minutes")
                print(f"💡 Admin: Please manually send this OTP via SMS")
                print(f"📋 Route: OTP API")
                print(f"{'='*50}\n")
                
                # Store OTP even when SMS fails for manual verification
                store_otp(phone_clean, otp)
                return jsonify({
                    'success': False, 
                    'message': 'Fast2SMS OTP account balance is low. Please recharge account or contact admin.'
                })
            else:
                print(f"\n{'='*50}")
                print(f"🚨 FAST2SMS OTP ERROR - MANUAL OTP REQUIRED")
                print(f"📱 Phone: {phone_clean}")
                print(f"🔐 OTP: {otp}")
                print(f"⏰ Valid for 5 minutes")
                print(f"💡 Admin: Please manually send this OTP via SMS")
                print(f"📋 Route: OTP API")
                print(f"📝 Error: {message}")
                print(f"{'='*50}\n")
                
                # Store OTP for manual verification
                store_otp(phone_clean, otp)
                return jsonify({'success': False, 'message': f'Failed to send OTP via OTP route: {message}'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error sending OTP: {str(e)}'})

@app.route('/verify-otp', methods=['POST'])
def verify_otp_route():
    """Verify OTP entered by user"""
    try:
        data = request.get_json()
        phone_number = data.get('phone_number')
        otp = data.get('otp')
        
        if not phone_number or not otp:
            return jsonify({'success': False, 'message': 'Phone number and OTP are required'})
        
        # Clean phone number
        phone_clean = phone_number.replace('+91', '').replace('+', '').replace(' ', '').strip()
        
        # Verify OTP
        success, message = verify_otp(phone_clean, otp)
        
        return jsonify({'success': success, 'message': message})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error verifying OTP: {str(e)}'})

@app.route('/admin/quick-approve-salary-otp/<int:request_id>', methods=['POST'])
@login_required
@admin_required
def admin_quick_approve_salary_otp(request_id):
    """Quick approve salary request"""
    try:
        from models import SalaryWithdrawal
        salary_request = SalaryWithdrawal.query.get_or_404(request_id)
        
        if salary_request.status != 'pending':
            return jsonify({'success': False, 'message': 'Request already processed'})
        
        data = request.get_json()
        transaction_hash = data.get('transaction_hash')
        
        if not transaction_hash:
            return jsonify({'success': False, 'message': 'Transaction hash is required'})
        
        # Update salary request
        salary_request.status = 'approved'
        salary_request.transaction_hash = transaction_hash
        salary_request.processed_at = datetime.utcnow()
        salary_request.processed_by = current_user.id
        
        db.session.commit()
        
        log_activity(current_user.id, 'salary_quick_approved', 
                    f'Quick approved salary request #{request_id} - TX: {transaction_hash}')
        
        return jsonify({'success': True, 'message': 'Salary request approved successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error approving request: {str(e)}'})

@app.route('/admin/quick-reject-salary-otp/<int:request_id>', methods=['POST'])
@login_required
@admin_required
def admin_quick_reject_salary_otp(request_id):
    """Quick reject salary request"""
    try:
        from models import SalaryWithdrawal
        from datetime import datetime
        
        salary_request = SalaryWithdrawal.query.get_or_404(request_id)
        
        if salary_request.status != 'pending':
            return jsonify({'success': False, 'message': 'Request already processed'})
        
        data = request.get_json()
        reason = data.get('reason', 'Admin rejection')
        
        # Update salary request
        salary_request.status = 'rejected'
        salary_request.admin_notes = reason
        salary_request.processed_at = datetime.utcnow()
        salary_request.processed_by = current_user.id
        
        db.session.commit()
        
        log_activity(current_user.id, 'salary_quick_rejected', 
                    f'Quick rejected salary request #{request_id} - Reason: {reason}')
        
        return jsonify({'success': True, 'message': 'Salary request rejected successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error rejecting request: {str(e)}'})

@app.route('/test-sms')
def test_sms():
    """Test SMS functionality"""
    try:
        # Test OTP
        otp = sms_service.generate_otp()
        success, message = sms_service.send_otp('9055639796', otp)
        
        return jsonify({
            'success': success,
            'message': message,
            'otp': otp if success else None,
            'phone': '9055639796'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'SMS test failed: {str(e)}'})

@app.route('/admin/salary-bulk-approve', methods=['POST'])
@login_required
@admin_required
def admin_salary_bulk_approve():
    """Bulk approve multiple salary requests"""
    try:
        from models import SalaryWithdrawal
        from datetime import datetime
        
        data = request.get_json()
        request_ids = data.get('request_ids', [])
        transaction_hash = data.get('transaction_hash')
        
        if not request_ids or not transaction_hash:
            return jsonify({'success': False, 'message': 'Request IDs and transaction hash are required'})
        
        approved_count = 0
        
        for request_id in request_ids:
            salary_request = SalaryWithdrawal.query.get(request_id)
            if salary_request and salary_request.status == 'pending':
                salary_request.status = 'approved'
                salary_request.transaction_hash = f'{transaction_hash}-{request_id}'
                salary_request.processed_at = datetime.utcnow()
                salary_request.processed_by = current_user.id
                approved_count += 1
        
        db.session.commit()
        
        log_activity(current_user.id, 'salary_bulk_approved', 
                    f'Bulk approved {approved_count} salary requests - TX: {transaction_hash}')
        
        return jsonify({'success': True, 'message': f'{approved_count} salary requests approved successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error in bulk approval: {str(e)}'})