from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, FloatField, SelectField, IntegerField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, ValidationError, Optional
from models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    referral_code = StringField('Referral Code (Optional)', validators=[Optional(), Length(max=20)])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Please use a different email address.')

    def validate_phone_number(self, phone_number):
        user = User.query.filter_by(phone_number=phone_number.data).first()
        if user:
            raise ValidationError('Please use a different phone number.')

class StakeForm(FlaskForm):
    coin_id = HiddenField('Coin ID')
    plan_id = HiddenField('Plan ID')
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0.01)])
    submit = SubmitField('Start Staking')

class DepositForm(FlaskForm):
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=1)])
    transaction_id = StringField('Transaction Hash', validators=[DataRequired(), Length(min=64, max=66)])
    screenshot = FileField('Upload Screenshot (Optional)', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    submit = SubmitField('Submit Deposit')

class WithdrawalForm(FlaskForm):
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=1)])
    wallet_address = StringField('Wallet Address', validators=[DataRequired(), Length(min=26, max=62)])
    network = SelectField('Network', choices=[
        ('BEP20', 'BEP20 (BSC)'),
        ('TRC20', 'TRC20 (TRON)'),
        ('ERC20', 'ERC20 (Ethereum)')
    ], validators=[DataRequired()])
    submit = SubmitField('Submit Withdrawal')

class ProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    profile_picture = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')])
    current_password = PasswordField('Current Password (if changing password)')
    new_password = PasswordField('New Password')
    confirm_password = PasswordField('Confirm New Password', validators=[EqualTo('new_password')])
    submit = SubmitField('Update Profile')

class SupportForm(FlaskForm):
    subject = StringField('Subject', validators=[DataRequired(), Length(max=200)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(max=2000)])
    priority = SelectField('Priority', choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ], default='medium')
    submit = SubmitField('Send Message')

class AdminPasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')

# Admin Forms (simplified versions)
class AdminUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone_number = StringField('Phone Number', validators=[DataRequired()])
    usdt_balance = FloatField('USDT Balance', validators=[DataRequired(), NumberRange(min=0)])
    is_admin = BooleanField('Admin Status')
    is_active = BooleanField('Active Status')
    submit = SubmitField('Update User')

class AdminCoinForm(FlaskForm):
    symbol = StringField('Symbol', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    min_stake = FloatField('Minimum Stake', validators=[DataRequired(), NumberRange(min=0)])
    icon_emoji = StringField('Icon Emoji', validators=[Optional()])
    logo_url = StringField('Logo URL', validators=[Optional()])
    logo_file = FileField('Logo File', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')])
    daily_return_rate = FloatField('Daily Return Rate (%)', validators=[Optional(), NumberRange(min=0, max=20)])
    active = BooleanField('Active', default=True)
    submit = SubmitField('Save Coin')

class AdminStakingPlanForm(FlaskForm):
    coin_id = SelectField('Coin', coerce=int, validators=[DataRequired()])
    duration_days = IntegerField('Duration (Days)', validators=[DataRequired()])
    interest_rate = FloatField('Interest Rate (%)', validators=[DataRequired()])
    active = BooleanField('Active', default=True)
    submit = SubmitField('Save Plan')

class AdminSettingsForm(FlaskForm):
    platform_name = StringField('Platform Name', validators=[DataRequired()])
    referral_level_1 = FloatField('Referral Level 1 (%)', validators=[DataRequired(), NumberRange(min=0, max=50)])
    referral_level_2 = FloatField('Referral Level 2 (%)', validators=[DataRequired(), NumberRange(min=0, max=50)])
    referral_level_3 = FloatField('Referral Level 3 (%)', validators=[DataRequired(), NumberRange(min=0, max=50)])
    min_referral_activation = FloatField('Min Referral Activation', validators=[DataRequired(), NumberRange(min=0)])
    withdrawal_fee = FloatField('Withdrawal Fee (%)', validators=[DataRequired(), NumberRange(min=0, max=10)])
    submit = SubmitField('Save Settings')

class AdminPasswordChangeForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')

class AdminPaymentAddressForm(FlaskForm):
    network = SelectField('Network', choices=[('BEP20', 'BEP20'), ('TRC20', 'TRC20')], validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    min_deposit = FloatField('Minimum Deposit', validators=[DataRequired(), NumberRange(min=1)], default=10.0)
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save Address')

class AdminBlockchainSettingsForm(FlaskForm):
    moralis_api_key = StringField('Moralis API Key', validators=[DataRequired()])
    moralis_api_url = StringField('Moralis API URL', validators=[DataRequired()], default="https://deep-index.moralis.io/api/v2.2")
    bscscan_api_key = StringField('BSCScan API Key', validators=[Optional()])
    submit = SubmitField('Save Blockchain Settings')

class AdminContentForm(FlaskForm):
    page_name = StringField('Page Name', validators=[DataRequired()])
    section_name = StringField('Section Name', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    content_type = SelectField('Content Type', choices=[('text', 'Text'), ('html', 'HTML')], default='text')
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save Content')

class SupportMessageForm(FlaskForm):
    subject = StringField('Subject', validators=[DataRequired()])
    message = TextAreaField('Message', validators=[DataRequired()])
    priority = SelectField('Priority', choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], default='medium')
    submit = SubmitField('Send Message')

class AdminSupportReplyForm(FlaskForm):
    admin_reply = TextAreaField('Reply Message', validators=[DataRequired()])
    status = SelectField('Status', choices=[('open', 'Open'), ('replied', 'Replied'), ('closed', 'Closed')], default='replied')
    submit = SubmitField('Send Reply')

class AdminUICustomizationForm(FlaskForm):
    element_type = StringField('Element Type', validators=[DataRequired()])
    element_name = StringField('Element Name', validators=[DataRequired()])
    icon_class = StringField('Icon Class', validators=[Optional()])
    icon_emoji = StringField('Icon Emoji', validators=[Optional()])
    background_color = StringField('Background Color', validators=[Optional()])
    text_color = StringField('Text Color', validators=[Optional()])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save UI Element')

class AdminNFTForm(FlaskForm):
    name = StringField('NFT Name', validators=[DataRequired()])
    collection_id = SelectField('Collection', coerce=int, validators=[DataRequired()])
    icon = StringField('Icon (Emoji)', validators=[Optional()], default='🎨')
    image_url = StringField('Image URL', validators=[Optional()])
    gradient = StringField('Gradient Colors', validators=[Optional()], default='from-purple-400 to-pink-400')
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0)])
    last_sale_price = FloatField('Last Sale Price', validators=[Optional(), NumberRange(min=0)])
    rarity = SelectField('Rarity', choices=[
        ('1', '1 Star - Common'),
        ('2', '2 Stars - Uncommon'),
        ('3', '3 Stars - Rare'),
        ('4', '4 Stars - Epic'),
        ('5', '5 Stars - Legendary')
    ], default='3', coerce=int)
    owner_name = StringField('Owner Name', validators=[Optional()], default='CryptoUser')
    unique_id = StringField('Unique ID', validators=[Optional()])
    is_verified = BooleanField('Verified')
    display_order = IntegerField('Display Order', default=0, validators=[Optional()])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save NFT')

class AdminNoticeForm(FlaskForm):
    page_location = SelectField('Page Location', choices=[
        ('global', 'Global (All Pages)'),
        ('home', 'Home Page'), 
        ('stake', 'Stake Page'),
        ('assets', 'Assets Page'),
        ('profile', 'Profile Page')
    ], default='global', validators=[DataRequired()])
    title = StringField('Title', validators=[DataRequired()])
    message = TextAreaField('Message', validators=[DataRequired()])
    notice_type = SelectField('Type', choices=[('info', 'Info'), ('warning', 'Warning'), ('error', 'Error'), ('success', 'Success')], default='info')
    display_order = IntegerField('Display Order', default=0, validators=[NumberRange(min=0)])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save Notice')

class AdminWithdrawalSettingsForm(FlaskForm):
    min_withdrawal = FloatField('Minimum Withdrawal', validators=[DataRequired(), NumberRange(min=0)])
    max_withdrawal = FloatField('Maximum Withdrawal', validators=[DataRequired(), NumberRange(min=1)])
    processing_fee = FloatField('Processing Fee (%)', validators=[DataRequired(), NumberRange(min=0, max=100)])
    daily_limit = FloatField('Daily Limit', validators=[DataRequired(), NumberRange(min=0)])
    auto_approval_limit = FloatField('Auto Approval Limit', validators=[Optional(), NumberRange(min=0)])
    require_admin_approval = BooleanField('Require Admin Approval')
    processing_time_hours = IntegerField('Processing Time (Hours)', validators=[Optional(), NumberRange(min=1, max=168)])
    is_maintenance_mode = BooleanField('Maintenance Mode')
    maintenance_message = TextAreaField('Maintenance Message', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Save Settings')

class AdminWithdrawalApprovalForm(FlaskForm):
    status = SelectField('Status', choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed')
    ], validators=[DataRequired()])
    admin_notes = TextAreaField('Admin Notes', validators=[Optional()])
    transaction_hash = StringField('Transaction Hash (for completed)', validators=[Optional()])
    submit = SubmitField('Update Status')

class AdminSocialMediaForm(FlaskForm):
    platform = StringField('Platform', validators=[DataRequired()])
    display_text = StringField('Display Text', validators=[DataRequired()])
    url = StringField('URL', validators=[DataRequired()])
    icon_class = StringField('Icon Class', validators=[DataRequired()])
    display_order = IntegerField('Display Order', default=0)
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save Social Media Link')

class AdminSupportResponseForm(FlaskForm):
    trigger_words = StringField('Trigger Words', validators=[DataRequired()], description='Comma-separated keywords')
    category = SelectField('Category', choices=[
        ('general', 'General'),
        ('account', 'Account'),
        ('staking', 'Staking'),
        ('referral', 'Referral'),
        ('salary', 'Salary'),
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal')
    ], default='general')
    response_text = TextAreaField('Response Text', validators=[DataRequired()], render_kw={"rows": 8})
    priority = IntegerField('Priority', validators=[DataRequired(), NumberRange(min=0, max=100)], default=0)
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save Response')

# Admin Notification Form
class AdminNotificationForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    message = TextAreaField('Message', validators=[DataRequired()], render_kw={"rows": 4})
    type = SelectField('Type', choices=[
        ('info', 'Info'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error')
    ], default='info')
    priority = SelectField('Priority', choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ], default='medium')
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Send Notification')