"""
Create sample support responses for testing
"""

from app import app, db
from models import SupportResponse, User

def create_sample_responses():
    """Create sample support responses"""
    with app.app_context():
        try:
            # Create tables first
            db.create_all()
            
            # Check if responses already exist
            if SupportResponse.query.count() > 0:
                print("Sample responses already exist!")
                return
            
            # Sample responses
            sample_responses = [
                {
                    'trigger_words': 'account, balance, summary, my account',
                    'response_text': '''### 📊 Account Summary<br><br>
                                       #### Your Current Balance:<br>
                                       • USDT Balance: $500.00<br>
                                       • Active Stakes: 3<br>
                                       • Total Earnings: $125.50<br><br>
                                       💡 **Tip**: Your account is performing well! Consider adding more funds for higher returns.''',
                    'category': 'account',
                    'priority': 10
                },
                {
                    'trigger_words': 'stake, staking, how to stake, investment',
                    'response_text': '''### 🚀 Staking Guide<br><br>
                                       #### How to Start Staking:<br>
                                       • Go to Stake page from bottom menu<br>
                                       • Choose your preferred coin (USDT, BTC, ETH)<br>
                                       • Select duration (7-365 days)<br>
                                       • Enter amount and confirm<br><br>
                                       ✅ **Daily Returns**: 0.5% to 2.0% based on coin and duration''',
                    'category': 'staking',
                    'priority': 8
                },
                {
                    'trigger_words': 'deposit, add money, fund account, how to deposit',
                    'response_text': '''### 💰 Deposit Guide<br><br>
                                       #### Step-by-Step Deposit Process:<br>
                                       • Click Assets → Deposit<br>
                                       • Copy wallet address or scan QR code<br>
                                       • Send USDT (BEP20) to the address<br>
                                       • Enter transaction hash for verification<br><br>
                                       ⚡ **Processing**: Usually within 5-15 minutes after blockchain confirmation''',
                    'category': 'deposit',
                    'priority': 9
                },
                {
                    'trigger_words': 'withdrawal, withdraw, cash out, how to withdraw',
                    'response_text': '''### 💸 Withdrawal Process<br><br>
                                       #### How to Withdraw Funds:<br>
                                       • Go to Assets → Withdraw<br>
                                       • Enter withdrawal amount<br>
                                       • Provide your USDT wallet address<br>
                                       • Submit request for admin approval<br><br>
                                       ⏱️ **Processing Time**: 24-48 hours for manual review''',
                    'category': 'withdrawal',
                    'priority': 7
                },
                {
                    'trigger_words': 'referral, invite friends, bonus, commission',
                    'response_text': '''### 👥 Referral Program<br><br>
                                       #### Your Referral Benefits:<br>
                                       • Level 1: 5% commission<br>
                                       • Level 2: 3% commission<br>
                                       • Level 3: 2% commission<br><br>
                                       🎁 **2-Referral Bonus**: Get $20 + no withdrawal fees + extra 2% staking returns!''',
                    'category': 'referral',
                    'priority': 6
                }
            ]
            
            # Add sample responses
            for response_data in sample_responses:
                response = SupportResponse(
                    trigger_words=response_data['trigger_words'],
                    response_text=response_data['response_text'],
                    category=response_data['category'],
                    priority=response_data['priority'],
                    is_active=True
                )
                db.session.add(response)
            
            db.session.commit()
            print(f"Created {len(sample_responses)} sample support responses!")
            
        except Exception as e:
            print(f"Error creating sample responses: {e}")
            db.session.rollback()

if __name__ == "__main__":
    create_sample_responses()