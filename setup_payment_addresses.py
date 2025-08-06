#!/usr/bin/env python3

from app import app, db
from models import PaymentAddress
import qrcode
import base64
from io import BytesIO

def generate_qr_code(data):
    """Generate QR code as base64 string"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color='black', back_color='white')
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return qr_base64

def setup_payment_addresses():
    """Setup default payment addresses"""
    with app.app_context():
        # Check if payment addresses exist
        existing_count = PaymentAddress.query.count()
        print(f"Found {existing_count} existing payment addresses")
        
        if existing_count == 0:
            print("Adding default payment addresses...")
            
            # Add BEP20 address
            bep20_address = '0xae49d3b4775c0524bd81da704340b5ef5a7416e9'
            bep20_qr = generate_qr_code(bep20_address)
            
            bep20_payment = PaymentAddress(
                network='BEP20',
                address=bep20_address,
                qr_code_path=bep20_qr,
                min_deposit=10.0,
                is_active=True
            )
            
            # Add TRC20 address
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
            db.session.commit()
            
            print("✅ Payment addresses added successfully!")
            print(f"BEP20: {bep20_address}")
            print(f"TRC20: {trc20_address}")
        else:
            print("Payment addresses already exist")
            
        # List all addresses
        addresses = PaymentAddress.query.all()
        for addr in addresses:
            print(f"📝 {addr.network}: {addr.address[:20]}... (Active: {addr.is_active})")

if __name__ == '__main__':
    setup_payment_addresses()