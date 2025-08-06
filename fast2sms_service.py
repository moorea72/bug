"""
Fast2SMS Service for OTP and SMS functionality
"""
import requests
import random
import string
from datetime import datetime, timedelta
from app import app, db
from models import User
import logging

class Fast2SMSService:
    def __init__(self):
        self.api_key = "bQCHHRp6caGutWSk7O8QYOQKpxFNzq1C5zeii6MKBt4ArExXxWuTWg80SfNQ"
        self.base_url = "https://www.fast2sms.com/dev/bulkV2"
        self.sender_id = "USDT"  # Default sender ID

    def generate_otp(self, length=6):
        """Generate random OTP"""
        return ''.join(random.choices(string.digits, k=length))

    def send_otp(self, phone_number, otp):
        """Send OTP via Fast2SMS OTP route (0.20 Rs per SMS)"""
        try:
            # Clean phone number - remove +91 if present
            phone = phone_number.replace('+91', '').replace('+', '').replace(' ', '')

            # Ensure 10 digit number for Indian phones
            if len(phone) == 10 and phone.isdigit():
                phone_clean = phone
            else:
                return False, "Please enter a valid 10-digit phone number"

            # Use OTP route as requested by user
            params = {
                'authorization': self.api_key,
                'route': 'otp',
                'variables_values': otp,
                'flash': '0',
                'numbers': phone_clean
            }

            print(f"🔄 Sending OTP {otp} to {phone_clean} via OTP route...")

            # Send OTP request
            response = requests.get(self.base_url, params=params, timeout=15)

            print(f"OTP API Response Status: {response.status_code}")
            print(f"OTP API Response Text: {response.text}")

            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"OTP API Response JSON: {result}")
                    
                    # Check for success
                    if result.get('return') == True:
                        print(f"✓ OTP sent successfully via OTP route to {phone_clean}")
                        store_otp(phone_clean, otp)
                        return True, "OTP sent successfully to your phone"
                    else:
                        error_msg = result.get('message', 'Unknown error')
                        print(f"✗ OTP route failed: {error_msg}")
                        
                        # Handle specific OTP errors
                        if 'wallet balance' in error_msg.lower() or 'balance' in error_msg.lower():
                            return False, "Fast2SMS account has insufficient balance. Please recharge your Fast2SMS account to send OTP."
                        elif 'dnd' in error_msg.lower():
                            return False, "Your phone number is in DND list. Please try with a different number."
                        else:
                            return False, f"OTP SMS failed: {error_msg}. Please try again later."
                        
                except ValueError as json_error:
                    # If JSON parsing fails, check response text
                    print(f"✗ OTP JSON parsing failed: {json_error}")
                    response_text = response.text.lower()
                    if 'sms sent successfully' in response_text or 'success' in response_text:
                        print(f"✓ OTP sent successfully to {phone_clean} (text response)")
                        store_otp(phone_clean, otp)
                        return True, "OTP sent successfully to your phone"
                    else:
                        return False, "Failed to send OTP SMS - Invalid response format"
            else:
                print(f"✗ OTP HTTP Error: {response.status_code}")
                print(f"Response body: {response.text}")
                return False, f"Failed to send OTP SMS: HTTP {response.status_code}"

        except Exception as e:
            print(f"✗ Exception sending OTP: {str(e)}")
            logging.error(f"Fast2SMS Error: {str(e)}")
            return False, f"Failed to send OTP: {str(e)}"
    

    
    def _handle_otp_failure(self, phone_number, error_message):
        """Handle OTP sending failure with proper error messaging"""
        print(f"✗ OTP sending failed for {phone_number}: {error_message}")
        return False, f"Failed to send OTP: {error_message}. Please try again."

    def send_welcome_sms(self, phone_number, username):
        """Send welcome SMS to new users"""
        try:
            phone = phone_number.replace('+91', '').replace('+', '').replace(' ', '')

            message = f"Welcome to USDT Staking Platform, {username}! Your account is now active. Start earning with crypto staking today!"

            params = {
                'authorization': self.api_key,
                'route': 'dlt',
                'sender_id': self.sender_id,
                'message': message,
                'variables_values': '',
                'flash': '0',
                'numbers': phone,
                'schedule_time': ''
            }

            response = requests.get(self.base_url, params=params, timeout=10)

            if response.status_code == 200:
                result = response.json()
                return result.get('return', False)

            return False

        except Exception as e:
            logging.error(f"Welcome SMS Error: {str(e)}")
            return False

    def verify_otp(self, phone_number, otp):
        """Verify OTP for a phone number"""
        try:
            # Clean phone number
            phone_clean = phone_number.replace('+91', '').replace('+', '').replace(' ', '').strip()

            from flask import session
            stored_data = session.get(f'otp_{phone_clean}')
            if not stored_data:
                return False, 'OTP expired or not found'

            stored_otp = stored_data.get('otp')
            expiry_time = stored_data.get('expiry')

            if datetime.now() > expiry_time:
                # Clean up expired OTP
                session.pop(f'otp_{phone_clean}', None)
                return False, 'OTP has expired'

            if str(stored_otp) == str(otp):
                # Don't clean up immediately - let registration handle it
                return True, 'OTP verified successfully'
            else:
                return False, 'Invalid OTP'

        except Exception as e:
            return False, f'Error verifying OTP: {str(e)}'

# Global instance
sms_service = Fast2SMSService()

def store_otp(phone_number, otp, extended=False):
    """Store OTP in session for verification"""
    from flask import session
    expiry_minutes = 5  # Standard 5 minute validity
    
    session[f'otp_{phone_number}'] = {
        'otp': otp,
        'timestamp': datetime.now().isoformat(),
        'verified': False,
        'expiry': (datetime.now() + timedelta(minutes=expiry_minutes)).isoformat()
    }
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=15)  # Session lasts 15 minutes
    
    print(f"✓ OTP stored for {phone_number}: {otp} (expires in {expiry_minutes} minutes)")

def verify_otp(phone_number, entered_otp):
    """Verify OTP entered by user"""
    from flask import session
    # Clean phone number
    phone_clean = phone_number.replace('+91', '').replace('+', '').replace(' ', '').strip()

    otp_data = session.get(f'otp_{phone_clean}')

    if not otp_data:
        return False, "OTP not found or expired"

    # Check if OTP is expired (5 minutes)
    otp_time = datetime.fromisoformat(otp_data['timestamp'])
    if datetime.now() - otp_time > timedelta(minutes=5):
        # Clear expired OTP
        session.pop(f'otp_{phone_clean}', None)
        return False, "OTP expired"

    # Verify OTP
    if otp_data['otp'] == entered_otp:
        # Mark as verified
        otp_data['verified'] = True
        session[f'otp_{phone_clean}'] = otp_data
        return True, "OTP verified successfully"
    else:
        return False, "Invalid OTP"

def clear_otp(phone_number):
    """Clear OTP from session after successful registration"""
    from flask import session
     # Clean phone number
    phone_clean = phone_number.replace('+91', '').replace('+', '').replace(' ', '').strip()
    session.pop(f'otp_{phone_clean}', None)