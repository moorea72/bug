"""
OTP Forms for Fast2SMS integration
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length, Regexp

class OTPRequestForm(FlaskForm):
    """Form to request OTP for phone verification"""
    phone_number = StringField('Phone Number', validators=[
        DataRequired(),
        Length(min=10, max=15),
        Regexp(r'^[+]?[\d\s\-()]{10,15}$', message='Invalid phone number format')
    ])
    submit = SubmitField('Send OTP')

class OTPVerifyForm(FlaskForm):
    """Form to verify OTP"""
    phone_number = HiddenField('Phone Number')
    otp = StringField('Enter OTP', validators=[
        DataRequired(),
        Length(min=4, max=8),
        Regexp(r'^\d+$', message='OTP must contain only numbers')
    ])
    submit = SubmitField('Verify OTP')

class EnhancedRegistrationForm(FlaskForm):
    """Enhanced registration form with OTP verification"""
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=4, max=20),
        Regexp(r'^[a-zA-Z0-9_]+$', message='Username can only contain letters, numbers, and underscores')
    ])
    email = StringField('Email', validators=[DataRequired(), Length(max=120)])
    phone_number = StringField('Phone Number', validators=[
        DataRequired(),
        Length(min=10, max=15),
        Regexp(r'^[+]?[\d\s\-()]{10,15}$', message='Invalid phone number format')
    ])
    password = StringField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = StringField('Confirm Password', validators=[DataRequired()])
    otp = StringField('OTP', validators=[
        DataRequired(),
        Length(min=4, max=8),
        Regexp(r'^\d+$', message='OTP must contain only numbers')
    ])
    otp_verified = HiddenField('OTP Verified', default='false')
    referral_code = StringField('Referral Code (Optional)', validators=[Length(max=20)])
    submit = SubmitField('Register')

class QuickSalaryApprovalForm(FlaskForm):
    """Quick approval form for salary requests"""
    transaction_hash = StringField('Transaction Hash', validators=[DataRequired(), Length(min=10, max=100)])
    submit = SubmitField('Approve & Send')