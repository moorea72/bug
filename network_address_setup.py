
from app import app, db
from models import PaymentAddress

def setup_network_addresses():
    """Setup proper network addresses for BEP20 and TRC20"""
    with app.app_context():
        # Clear existing addresses
        PaymentAddress.query.delete()
        
        # Add BEP20 address
        bep20_address = PaymentAddress(
            network='BEP20',
            address='0xae49d3b4775c0524bd81da704340b5ef5a7416e9',
            min_deposit=10.0,
            is_active=True
        )
        
        # Add TRC20 address (you need to provide actual TRC20 address)
        trc20_address = PaymentAddress(
            network='TRC20', 
            address='TYourTRC20AddressHere',  # Replace with actual TRC20 address
            min_deposit=10.0,
            is_active=True
        )
        
        db.session.add(bep20_address)
        db.session.add(trc20_address)
        db.session.commit()
        
        print("✅ Network addresses setup completed!")
        print(f"BEP20: {bep20_address.address}")
        print(f"TRC20: {trc20_address.address}")

if __name__ == "__main__":
    setup_network_addresses()
