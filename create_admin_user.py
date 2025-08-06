#!/usr/bin/env python3

from app import app, db
from models import User, PaymentAddress, Coin, StakingPlan
from werkzeug.security import generate_password_hash
import qrcode
import base64
from io import BytesIO

def generate_qr_code(data):
    """Generate QR code as base64 string"""
    qr = qrcode.QRCode(version=1, box_size=6, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color='black', back_color='white')
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return qr_base64

def setup_complete_database():
    """Setup complete database with admin user, payment addresses, coins and plans"""
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create admin user if not exists
        admin = User.query.filter_by(email='admin@platform.com').first()
        if not admin:
            print('Creating admin user...')
            admin = User(
                username='admin',
                email='admin@platform.com',
                phone_number='1234567890',
                password_hash=generate_password_hash('admin123'),
                is_admin=True,
                usdt_balance=0.0,
                referral_code='ADMIN001'
            )
            db.session.add(admin)
            print('✅ Admin user created')
        
        # Create payment addresses if not exist
        if PaymentAddress.query.count() == 0:
            print('Creating payment addresses...')
            
            # BEP20 address
            bep20_address = '0xae49d3b4775c0524bd81da704340b5ef5a7416e9'
            bep20_qr = generate_qr_code(bep20_address)
            
            bep20_payment = PaymentAddress(
                network='BEP20',
                address=bep20_address,
                qr_code_path=bep20_qr,
                min_deposit=10.0,
                is_active=True
            )
            
            # TRC20 address
            trc20_address = 'TQn9Y2khEsLJW1ChVWFMSMeRDow5KcbLSE'
            trc20_qr = generate_qr_code(trc20_address)
            
            trc20_payment = PaymentAddress(
                network='TRC20',
                address=trc20_address,
                qr_code_path=trc20_qr,
                min_deposit=5.0,
                is_active=True
            )
            
            db.session.add(bep20_payment)
            db.session.add(trc20_payment)
            print('✅ Payment addresses created')
        
        # Create coins if not exist
        if Coin.query.count() == 0:
            print('Creating coins...')
            coins_data = [
                {'symbol': 'USDT', 'name': 'Tether USD', 'min_stake': 10.0, 'icon_emoji': '💰'},
                {'symbol': 'BTC', 'name': 'Bitcoin', 'min_stake': 250.0, 'icon_emoji': '₿'},
                {'symbol': 'ETH', 'name': 'Ethereum', 'min_stake': 170.0, 'icon_emoji': 'Ξ'},
                {'symbol': 'BNB', 'name': 'Binance Coin', 'min_stake': 90.0, 'icon_emoji': '🔶'},
                {'symbol': 'LTC', 'name': 'Litecoin', 'min_stake': 130.0, 'icon_emoji': 'Ł'}
            ]
            
            for coin_data in coins_data:
                coin = Coin(**coin_data)
                db.session.add(coin)
            print('✅ Coins created')
        
        # Create staking plans if not exist
        if StakingPlan.query.count() == 0:
            print('Creating staking plans...')
            coins = Coin.query.all()
            
            durations = [7, 15, 30, 90, 120, 180]
            rates = [0.5, 0.8, 1.2, 1.5, 1.8, 2.0]
            
            for coin in coins:
                for duration, rate in zip(durations, rates):
                    plan = StakingPlan(
                        coin_id=coin.id,
                        duration_days=duration,
                        interest_rate=rate
                    )
                    db.session.add(plan)
            print('✅ Staking plans created')
        
        db.session.commit()
        
        print('\n🎉 Database setup complete!')
        print('\nAdmin Login:')
        print('Email: admin@platform.com')
        print('Password: admin123')
        
        print(f'\nDatabase Summary:')
        print(f'Users: {User.query.count()}')
        print(f'Payment Addresses: {PaymentAddress.query.count()}')
        print(f'Coins: {Coin.query.count()}')
        print(f'Staking Plans: {StakingPlan.query.count()}')

if __name__ == '__main__':
    setup_complete_database()