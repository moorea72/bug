# Enhanced models for new features
from app import db
from datetime import datetime

class CoinReturnRate(db.Model):
    """Individual return rates for each coin by duration"""
    __tablename__ = 'coin_return_rates'
    
    id = db.Column(db.Integer, primary_key=True)
    coin_id = db.Column(db.Integer, db.ForeignKey('coin.id'), nullable=False)
    duration_days = db.Column(db.Integer, nullable=False)  # 7, 15, 30, 90, 120, 180, 365
    daily_return_rate = db.Column(db.Float, nullable=False)  # Percentage rate
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    coin = db.relationship('Coin', backref='return_rates')
    
    # Unique constraint to prevent duplicate rates for same coin and duration
    __table_args__ = (db.UniqueConstraint('coin_id', 'duration_days', name='unique_coin_duration'),)

class NFTTradingLimit(db.Model):
    """Daily NFT trading limits for 2025 users"""
    __tablename__ = 'nft_trading_limits'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    nfts_bought = db.Column(db.Integer, default=0)
    nfts_sold = db.Column(db.Integer, default=0)
    daily_limit = db.Column(db.Integer, default=2)  # 2 NFTs per day for 2025 users
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='nft_trading_limits')
    
    # Unique constraint for one record per user per day
    __table_args__ = (db.UniqueConstraint('user_id', 'date', name='unique_user_date'),)

class NFTStake(db.Model):
    """NFT staking for 1.90% returns"""
    __tablename__ = 'nft_stakes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    nft_id = db.Column(db.Integer, db.ForeignKey('nft.id'), nullable=False)
    stake_amount = db.Column(db.Float, nullable=False)  # NFT value when staked
    daily_return_rate = db.Column(db.Float, default=1.90)  # 1.90% daily
    current_earnings = db.Column(db.Float, default=0.0)
    stake_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_reward_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    unlock_date = db.Column(db.DateTime)  # Optional lock period
    
    # Relationships
    user = db.relationship('User', backref='nft_stakes')
    nft = db.relationship('NFT', backref='stakes')

class DepositAPI(db.Model):
    """Configurable deposit verification APIs"""
    __tablename__ = 'deposit_apis'
    
    id = db.Column(db.Integer, primary_key=True)
    api_name = db.Column(db.String(100), nullable=False)
    api_url = db.Column(db.String(500), nullable=False)
    api_key = db.Column(db.String(200))
    network = db.Column(db.String(20), nullable=False)  # BEP20, TRC20, ERC20
    is_active = db.Column(db.Boolean, default=True)
    is_primary = db.Column(db.Boolean, default=False)
    success_rate = db.Column(db.Float, default=0.0)  # Track API reliability
    last_used = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserFeatureAccess(db.Model):
    """Track feature access for different user types"""
    __tablename__ = 'user_feature_access'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    feature_name = db.Column(db.String(100), nullable=False)  # nft_trading, nft_staking, etc.
    is_enabled = db.Column(db.Boolean, default=False)
    daily_limit = db.Column(db.Integer)
    access_level = db.Column(db.String(50), default='basic')  # basic, premium, vip
    granted_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    
    # Relationships
    user = db.relationship('User', backref='feature_access')
    
    # Unique constraint for one feature per user
    __table_args__ = (db.UniqueConstraint('user_id', 'feature_name', name='unique_user_feature'),)