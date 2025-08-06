# Enhanced forms for new admin functionality
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, FloatField, IntegerField, BooleanField, SelectField, TextAreaField
from wtforms.validators import DataRequired, NumberRange, Length, Optional

class AdminCoinStakingPlanForm(FlaskForm):
    """Form for managing coin-specific staking plans"""
    coin_id = SelectField('Coin', coerce=int, validators=[DataRequired()])
    duration_days = IntegerField('Duration (Days)', validators=[DataRequired(), NumberRange(min=1, max=365)])
    daily_return_rate = FloatField('Daily Return Rate (%)', validators=[DataRequired(), NumberRange(min=0.1, max=10.0)])
    min_amount = FloatField('Minimum Amount', validators=[Optional(), NumberRange(min=0)])
    max_amount = FloatField('Maximum Amount', validators=[Optional(), NumberRange(min=1)])
    active = BooleanField('Active', default=True)

class AdminDepositAPIForm(FlaskForm):
    """Form for managing deposit verification APIs"""
    api_name = StringField('API Name', validators=[DataRequired(), Length(max=100)])
    api_url = StringField('API URL', validators=[DataRequired(), Length(max=500)])
    api_key = StringField('API Key', validators=[Optional(), Length(max=200)])
    network = SelectField('Network', choices=[
        ('BEP20', 'BEP20 (BSC)'),
        ('TRC20', 'TRC20 (TRON)'),
        ('ERC20', 'ERC20 (Ethereum)')
    ], validators=[DataRequired()])
    is_active = BooleanField('Active', default=True)
    is_primary = BooleanField('Primary API', default=False)

class AdminNFTEnhancedForm(FlaskForm):
    """Simple NFT management form"""
    collection_id = SelectField('Collection', coerce=int, validators=[DataRequired()])
    name = StringField('NFT Name', validators=[DataRequired(), Length(max=100)])
    image_file = FileField('Upload Photo', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Only image files allowed!')])
    price = FloatField('Price (USDT)', validators=[DataRequired(), NumberRange(min=0)])
    is_verified = BooleanField('Verified (Blue Tick)', default=False)
    blue_tick_file = FileField('Blue Tick PNG', validators=[FileAllowed(['png'], 'Only PNG files allowed!')])
    is_active = BooleanField('Active', default=True)

class AdminCoinReturnRateForm(FlaskForm):
    """Form for setting individual coin return rates by duration"""
    # Different rates for different durations
    rate_7_days = FloatField('7 Days Rate (%)', validators=[Optional(), NumberRange(min=0, max=10)])
    rate_15_days = FloatField('15 Days Rate (%)', validators=[Optional(), NumberRange(min=0, max=10)])
    rate_30_days = FloatField('30 Days Rate (%)', validators=[Optional(), NumberRange(min=0, max=10)])
    rate_90_days = FloatField('90 Days Rate (%)', validators=[Optional(), NumberRange(min=0, max=10)])
    rate_120_days = FloatField('120 Days Rate (%)', validators=[Optional(), NumberRange(min=0, max=10)])
    rate_180_days = FloatField('180 Days Rate (%)', validators=[Optional(), NumberRange(min=0, max=10)])
    rate_365_days = FloatField('365 Days Rate (%)', validators=[Optional(), NumberRange(min=0, max=10)])
    
    is_active = BooleanField('Active', default=True)