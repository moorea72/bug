from datetime import datetime, timedelta
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import string

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    usdt_balance = db.Column(db.Float, default=0.0)
    total_staked = db.Column(db.Float, default=0.0)
    total_earned = db.Column(db.Float, default=0.0)
    referral_code = db.Column(db.String(20), unique=True, nullable=False)
    referred_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    referral_bonus = db.Column(db.Float, default=0.0)  # Accumulated referral bonuses
    
    # New 2 Friends System  
    two_referral_bonus_claimed = db.Column(db.Boolean, default=False)  # Track if 20 USDT bonus claimed
    stake_commission_eligible = db.Column(db.Boolean, default=False)  # Track if eligible for 2% stake commissions
    
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    profile_picture = db.Column(db.String(255), default='default_animal_1.svg')  # Default avatar
    salary_wallet_address = db.Column(db.String(255), nullable=True)  # Crypto wallet for salary
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    stakes = db.relationship('Stake', backref='user', lazy=True)
    deposits = db.relationship('Deposit', backref='user', lazy=True)
    withdrawals = db.relationship('Withdrawal', backref='user', lazy=True)
    referrals = db.relationship('User', backref=db.backref('referrer', remote_side=[id]))
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if not self.referral_code:
            self.referral_code = self.generate_referral_code()
    
    def generate_referral_code(self):
        """Generate a unique referral code"""
        while True:
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            # Check if code already exists
            if not User.query.filter_by(referral_code=code).first():
                return code
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_referral_tree(self, level=1, max_level=3):
        if level > max_level:
            return []
        
        referrals = []
        direct_referrals = User.query.filter_by(referred_by=self.id).all()
        
        for referral in direct_referrals:
            referral_data = {
                'user': referral,
                'level': level,
                'children': referral.get_referral_tree(level + 1, max_level)
            }
            referrals.append(referral_data)
        
        return referrals
    
    def get_referral_count(self):
        """Get total number of users referred by this user"""
        return User.query.filter_by(referred_by=self.id).count()
    
    def get_referral_bonus_summary(self):
        """COMPLETELY DISABLED - No referral bonus system"""
        return {'total_bonuses': 0, 'bonus_count': 0, 'bonus_details': [], 'referral_count': 0}
    
    def has_two_referrals(self):
        """COMPLETELY DISABLED - No premium benefits"""
        return False
    
    def get_active_referrals_count(self):
        """Get count of referrals who have made deposits"""
        referrals_with_deposits = 0
        for referral in User.query.filter_by(referred_by=self.id).all():
            # Check if referral has any approved deposits
            total_deposits = db.session.query(db.func.sum(Deposit.amount)).filter_by(
                user_id=referral.id,
                status='approved'
            ).scalar() or 0
            
            if total_deposits > 0:
                referrals_with_deposits += 1
                
        return referrals_with_deposits
    
    def get_qualified_referrals_count(self):
        """Get count of referrals who currently maintain 100+ USDT balance (real-time)"""
        qualified_count = 0
        referrals = User.query.filter_by(referred_by=self.id).all()
        
        for referral in referrals:
            # Check if referral currently has 100+ USDT total balance (wallet + active stakes)
            current_balance = referral.get_total_balance_including_stakes()
            
            if current_balance >= 100:
                qualified_count += 1
        
        return qualified_count
    
    def check_and_activate_premium_benefits(self):
        """DISABLED - No premium benefits or bonuses"""
        return False
    
    def get_stake_commission_rate(self):
        """DISABLED - No stake commission"""
        return 0.0
    
    def has_withdrawal_fees(self):
        """All users have standard withdrawal fees"""
        return True
    
    def get_total_balance_including_stakes(self):
        """Get total balance including active stakes"""
        active_stakes = db.session.query(db.func.sum(Stake.amount)).filter_by(
            user_id=self.id,
            status='active'
        ).scalar() or 0
        
        return self.usdt_balance + active_stakes
    
    def is_salary_eligible(self):
        """Check if user is eligible for salary based on active referrals and balance"""
        try:
            # Get user's total balance (wallet + stakes)
            total_balance = self.get_total_balance_including_stakes()
            
            # Get qualified referrals (users with 100+ USDT deposits)
            qualified_referrals = self.get_qualified_referrals_count()
            
            # Check salary plans (7+ referrals with 350+ balance, 13+ with 680+ balance, etc.)
            salary_plans = [
                (7, 350),   # Plan 1: 7 referrals + 350 balance
                (13, 680),  # Plan 2: 13 referrals + 680 balance  
                (27, 960),  # Plan 3: 27 referrals + 960 balance
                (46, 1340)  # Plan 4: 46 referrals + 1340 balance
            ]
            
            for required_referrals, required_balance in salary_plans:
                if qualified_referrals >= required_referrals and total_balance >= required_balance:
                    return True
            
            return False
        except:
            return False

class Coin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    min_stake = db.Column(db.Float, nullable=False)
    logo_url = db.Column(db.String(500), nullable=True)  # Admin changeable logo
    icon_emoji = db.Column(db.String(10), default='💰')  # Admin changeable icon
    daily_return_rate = db.Column(db.Float, default=1.0)  # Individual coin return rate
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    stakes = db.relationship('Stake', backref='coin', lazy=True)

class StakingPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    duration_days = db.Column(db.Integer, nullable=False)
    interest_rate = db.Column(db.Float, nullable=False)  # Daily interest rate
    coin_id = db.Column(db.Integer, db.ForeignKey('coin.id'), nullable=True)  # Coin-specific plans
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    stakes = db.relationship('Stake', backref='plan', lazy=True)
    coin = db.relationship('Coin', backref='staking_plans', lazy=True)
    
    @property
    def effective_daily_rate(self):
        """Get effective daily rate considering coin-specific multiplier"""
        base_rate = self.interest_rate
        if self.coin and self.coin.daily_return_rate:
            return base_rate * (self.coin.daily_return_rate / 100)
        return base_rate

class Stake(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    coin_id = db.Column(db.Integer, db.ForeignKey('coin.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('staking_plan.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    daily_interest = db.Column(db.Float, nullable=False)
    total_return = db.Column(db.Float, nullable=False)
    premium_commission = db.Column(db.Float, default=0.0)  # 2% commission for premium users
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='active')  # active, completed, cancelled
    withdrawn = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def is_mature(self):
        return datetime.utcnow() >= self.end_date
    
    @property
    def days_remaining(self):
        if self.is_mature:
            return 0
        return (self.end_date - datetime.utcnow()).days
    
    def calculate_current_return(self):
        if self.status == 'cancelled':
            return 0
        
        days_passed = (datetime.utcnow() - self.start_date).days
        if days_passed > self.plan.duration_days:
            days_passed = self.plan.duration_days
        
        base_return = self.amount * self.daily_interest * days_passed / 100
        return base_return + self.premium_commission

class Deposit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    transaction_id = db.Column(db.String(100), unique=True, nullable=False)  # Made unique to prevent duplicates
    screenshot_path = db.Column(db.String(200), nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, verified
    admin_notes = db.Column(db.Text, nullable=True)
    blockchain_verified = db.Column(db.Boolean, default=False)
    verification_details = db.Column(db.Text, nullable=True)  # JSON string with verification details
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime, nullable=True)

class Withdrawal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    fee_amount = db.Column(db.Float, default=0.0)  # Fee charged
    net_amount = db.Column(db.Float, nullable=False)  # Amount after fees
    wallet_address = db.Column(db.String(200), nullable=False)
    network = db.Column(db.String(20), nullable=False)  # BEP20, TRC20
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, completed
    admin_notes = db.Column(db.Text, nullable=True)
    transaction_hash = db.Column(db.String(100), nullable=True)  # Hash after completion
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)

class PlatformSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @staticmethod
    def get_setting(key, default=None):
        setting = PlatformSettings.query.filter_by(key=key).first()
        return setting.value if setting else default
    
    @staticmethod
    def get_all_settings():
        settings = PlatformSettings.query.all()
        return {setting.key: setting.value for setting in settings}
    
    @staticmethod
    def set_setting(key, value, description=None):
        setting = PlatformSettings.query.filter_by(key=key).first()
        if setting:
            setting.value = value
            if description:
                setting.description = description
        else:
            setting = PlatformSettings(key=key, value=value, description=description)
            db.session.add(setting)
        db.session.commit()

class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PaymentAddress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    network = db.Column(db.String(20), nullable=False)  # BEP20, TRC20
    address = db.Column(db.String(200), nullable=False)
    qr_code_path = db.Column(db.Text, nullable=True)
    min_deposit = db.Column(db.Float, default=10.0)  # Minimum deposit amount
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ContentSection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    page_name = db.Column(db.String(50), nullable=False)  # home, stake, assets, profile
    section_name = db.Column(db.String(100), nullable=False)  # hero_title, benefits_text, etc.
    content = db.Column(db.Text, nullable=False)
    content_type = db.Column(db.String(20), default='text')  # text, html
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @staticmethod
    def get_content(page_name, section_name, default_content=""):
        """Get content for a specific page section"""
        content = ContentSection.query.filter_by(
            page_name=page_name, 
            section_name=section_name, 
            is_active=True
        ).first()
        return content.content if content else default_content

    @staticmethod
    def set_content(page_name, section_name, content, content_type='text'):
        """Set or update content for a specific page section"""
        existing = ContentSection.query.filter_by(
            page_name=page_name, 
            section_name=section_name
        ).first()
        
        if existing:
            existing.content = content
            existing.content_type = content_type
            existing.updated_at = datetime.utcnow()
        else:
            new_content = ContentSection(
                page_name=page_name,
                section_name=section_name,
                content=content,
                content_type=content_type
            )
            db.session.add(new_content)
        
        db.session.commit()

class SupportMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    problem_type = db.Column(db.String(50), default='general')  # account, staking, deposits, technical, general
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    admin_reply = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='open')  # open, replied, closed
    priority = db.Column(db.String(20), default='normal')  # low, normal, high, urgent
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    replied_at = db.Column(db.DateTime, nullable=True)
    
    # Relationship
    user = db.relationship('User', backref='support_messages')
    
    def __repr__(self):
        return f'<SupportMessage {self.id}: {self.subject}>'

# Enhanced Support Chat System
class SupportChat(db.Model):
    __tablename__ = 'support_chats'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    sender_type = db.Column(db.String(10), nullable=False)  # 'user' or 'admin'
    admin_reply = db.Column(db.Text, nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    auto_response_sent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)  # Auto-delete after 24 hours
    
    # Relationships
    user = db.relationship('User', backref='support_chats')
    
    def __init__(self, **kwargs):
        super(SupportChat, self).__init__(**kwargs)
        # Set expiry to 24 hours from creation
        if not hasattr(self, 'expires_at') or not self.expires_at:
            self.expires_at = datetime.utcnow() + timedelta(hours=24)
    
    @classmethod
    def cleanup_expired_chats(cls):
        """Remove chats older than 24 hours"""
        try:
            expired_chats = cls.query.filter(cls.expires_at <= datetime.utcnow()).all()
            count = len(expired_chats)
            for chat in expired_chats:
                db.session.delete(chat)
            db.session.commit()
            return count
        except Exception as e:
            print(f"Error cleaning up expired chats: {e}")
            return 0
    
    def __repr__(self):
        return f'<SupportChat {self.id}: {self.sender_type} message>'

class NFTCollection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    symbol = db.Column(db.String(10), nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    nfts = db.relationship('NFT', backref='collection', lazy=True)

    def __repr__(self):
        return f'<NFTCollection {self.name}>'

class NFT(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    collection_id = db.Column(db.Integer, db.ForeignKey('nft_collection.id'), nullable=False)
    icon = db.Column(db.String(10), default='🎨')  # Emoji icon
    image_url = db.Column(db.String(500), nullable=False)  # Image URL
    gradient = db.Column(db.String(100), default='from-blue-500 to-purple-600')  # CSS gradient classes
    price = db.Column(db.Float, nullable=False)
    last_sale_price = db.Column(db.Float, nullable=True)
    rarity = db.Column(db.Integer, default=3)  # 1-5 stars
    owner_name = db.Column(db.String(50), default='CryptoOwner')
    unique_id = db.Column(db.String(20), unique=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    blue_tick_url = db.Column(db.String(500), nullable=True)  # Blue tick PNG URL
    description = db.Column(db.Text, nullable=True)  # NFT description
    is_active = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<NFT {self.name} - #{self.unique_id}>'

class SalaryWithdrawal(db.Model):
    """Salary withdrawal requests for admin approval"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    plan_id = db.Column(db.Integer, nullable=False)  # 1-4 for salary plans
    amount = db.Column(db.Float, nullable=False)
    wallet_address = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    transaction_hash = db.Column(db.String(255), nullable=True)  # Admin fills after payment
    admin_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime, nullable=True)
    processed_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='salary_withdrawals')
    processed_by_admin = db.relationship('User', foreign_keys=[processed_by])
    
    def __repr__(self):
        return f'<SalaryWithdrawal {self.id}: ${self.amount} to {self.user.username}>'

class UICustomization(db.Model):
    """Admin-customizable UI elements like icons, colors, etc."""
    id = db.Column(db.Integer, primary_key=True)
    element_type = db.Column(db.String(50), nullable=False)  # 'nav_icon', 'coin_icon', 'feature_icon', etc.
    element_name = db.Column(db.String(100), nullable=False)  # 'home', 'stake', 'assets', etc.
    icon_class = db.Column(db.String(100), nullable=True)  # Font Awesome class
    icon_emoji = db.Column(db.String(10), nullable=True)  # Emoji alternative
    background_color = db.Column(db.String(50), nullable=True)  # Background color
    text_color = db.Column(db.String(50), nullable=True)  # Text color
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @staticmethod
    def get_icon(element_type, element_name, default_icon='fas fa-circle'):
        """Get icon for a specific UI element"""
        ui_element = UICustomization.query.filter_by(
            element_type=element_type, 
            element_name=element_name, 
            is_active=True
        ).first()
        
        if ui_element:
            return ui_element.icon_emoji or ui_element.icon_class or default_icon
        return default_icon

    def __repr__(self):
        return f'<UICustomization {self.element_type}:{self.element_name}>'

class PlatformNotice(db.Model):
    """Admin-manageable notices and announcements"""
    id = db.Column(db.Integer, primary_key=True)
    page_location = db.Column(db.String(50), nullable=False)  # 'home', 'stake', 'global'
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notice_type = db.Column(db.String(20), default='info')  # 'info', 'warning', 'success', 'error'
    is_active = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @staticmethod
    def get_notices(page_location='global'):
        """Get active notices for a specific page"""
        return PlatformNotice.query.filter_by(
            page_location=page_location, 
            is_active=True
        ).order_by(PlatformNotice.display_order, PlatformNotice.created_at.desc()).all()

    def __repr__(self):
        return f'<PlatformNotice {self.page_location}:{self.title}>'

class WithdrawalSettings(db.Model):
    """Admin-configurable withdrawal settings"""
    id = db.Column(db.Integer, primary_key=True)
    min_withdrawal = db.Column(db.Float, default=10.0)
    max_withdrawal = db.Column(db.Float, default=50000.0)
    daily_limit = db.Column(db.Float, default=10000.0)
    processing_fee = db.Column(db.Float, default=1.0)  # Percentage fee
    auto_approval_limit = db.Column(db.Float, default=100.0)  # Auto approve under this amount
    require_admin_approval = db.Column(db.Boolean, default=True)
    processing_time_hours = db.Column(db.Integer, default=24)
    allowed_networks = db.Column(db.String(200), default='BEP20,TRC20')  # Comma separated
    is_maintenance_mode = db.Column(db.Boolean, default=False)
    maintenance_message = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @staticmethod
    def get_settings():
        """Get current withdrawal settings or create default"""
        settings = WithdrawalSettings.query.first()
        if not settings:
            settings = WithdrawalSettings()
            db.session.add(settings)
            db.session.commit()
        return settings
    
    def __repr__(self):
        return f'<WithdrawalSettings min:{self.min_withdrawal} max:{self.max_withdrawal}>'

class SocialMediaLink(db.Model):
    """Admin-configurable social media links for footer"""
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(50), nullable=False)  # telegram, twitter, discord, etc.
    icon_class = db.Column(db.String(100), nullable=False)  # Font Awesome class
    url = db.Column(db.String(500), nullable=False)
    display_text = db.Column(db.String(100), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @staticmethod
    def get_active_links():
        """Get all active social media links ordered by display_order"""
        return SocialMediaLink.query.filter_by(is_active=True).order_by(
            SocialMediaLink.display_order, 
            SocialMediaLink.created_at
        ).all()
    
    def __repr__(self):
        return f'<SocialMediaLink {self.platform}:{self.url}>'

class ReferralCommission(db.Model):
    """One-time referral deposit commissions"""
    __tablename__ = 'referral_commissions'
    
    id = db.Column(db.Integer, primary_key=True)
    referrer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    referred_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    commission_amount_usdt = db.Column(db.Float, nullable=False)  # Commission amount in USDT
    deposit_amount = db.Column(db.Float, nullable=False)  # Original deposit amount that triggered commission
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    referrer = db.relationship('User', foreign_keys=[referrer_id], backref='earned_commissions')
    referred_user = db.relationship('User', foreign_keys=[referred_user_id], backref='generated_commissions')
    
    # Unique constraint to ensure only one commission per referred user
    __table_args__ = (db.UniqueConstraint('referred_user_id', name='unique_referred_user_commission'),)
    
    def __repr__(self):
        return f'<ReferralCommission ${self.commission_amount_usdt} for user {self.referred_user_id}>'

class SupportResponse(db.Model):
    """Admin-managed support responses for AI chat system"""
    id = db.Column(db.Integer, primary_key=True)
    trigger_words = db.Column(db.Text, nullable=False)  # Comma-separated trigger words
    response_text = db.Column(db.Text, nullable=False)  # HTML formatted response
    category = db.Column(db.String(50), default='general')  # general, account, staking, etc.
    is_active = db.Column(db.Boolean, default=True)
    priority = db.Column(db.Integer, default=0)  # Higher priority = checked first
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_trigger_list(self):
        """Get list of trigger words"""
        return [word.strip().lower() for word in self.trigger_words.split(',') if word.strip()]
    
    @staticmethod
    def find_response(message):
        """Find matching response for user message"""
        message_lower = message.lower()
        
        # Get active responses ordered by priority
        responses = SupportResponse.query.filter_by(is_active=True).order_by(
            SupportResponse.priority.desc(),
            SupportResponse.created_at.desc()
        ).all()
        
        for response in responses:
            triggers = response.get_trigger_list()
            if any(trigger in message_lower for trigger in triggers):
                return response
        
        return None
    
    def __repr__(self):
        return f'<SupportResponse {self.category}:{self.trigger_words[:30]}>'

# Notification System Models
class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), default='info')  # info, success, warning, error
    priority = db.Column(db.String(20), default='medium')  # low, medium, high
    is_active = db.Column(db.Boolean, default=True)
    view_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_icon(self):
        icons = {
            'info': 'fas fa-info-circle',
            'success': 'fas fa-check-circle',
            'warning': 'fas fa-exclamation-triangle',
            'error': 'fas fa-times-circle'
        }
        return icons.get(self.type, 'fas fa-bell')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'type': self.type,
            'priority': self.priority,
            'icon': self.get_icon(),
            'time': self.created_at.strftime('%Y-%m-%d %H:%M')
        }

class UserNotificationView(db.Model):
    __tablename__ = 'user_notification_views'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    notification_id = db.Column(db.Integer, db.ForeignKey('notifications.id'), nullable=False)
    viewed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='notification_views')
    notification = db.relationship('Notification', backref='user_views')

# Salary Plan Model  
class SalaryPlan(db.Model):
    __tablename__ = 'salary_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    plan_name = db.Column(db.String(100), nullable=False)
    referrals_required = db.Column(db.Integer, nullable=False, default=0)
    balance_required = db.Column(db.Float, nullable=False, default=0.0)
    monthly_salary = db.Column(db.Float, nullable=False, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<SalaryPlan {self.plan_name}: {self.referrals_required} refs, ${self.monthly_salary}/month>'

# Support Ticket System Models
class SupportTicket(db.Model):
    __tablename__ = 'support_tickets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    category = db.Column(db.String(50), default='general')
    status = db.Column(db.String(20), default='open')  # open, in_progress, resolved, closed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='support_tickets')
    
    def __repr__(self):
        return f'<SupportTicket {self.title} by {self.user.username}>'

class SupportTicketReply(db.Model):
    __tablename__ = 'support_ticket_replies'
    
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('support_tickets.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_admin_reply = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    ticket = db.relationship('SupportTicket', backref='replies')
    user = db.relationship('User', backref='ticket_replies')
    
    def __repr__(self):
        return f'<SupportTicketReply to ticket {self.ticket_id} by {self.user.username}>'