#!/usr/bin/env python3
"""
Comprehensive Support System Test Script
Tests both AI and human support functionality
"""

import sys
import os
sys.path.append('.')

from app import app, db
from models import User, SupportMessage, SupportResponse
from werkzeug.security import generate_password_hash
from datetime import datetime

def test_comprehensive_support():
    """Test comprehensive support system functionality"""
    print("Testing comprehensive support system...")
    
    with app.app_context():
        try:
            # 1. Ensure database tables exist
            print("1. Creating database tables...")
            db.create_all()
            
            # 2. Create test user
            print("2. Creating test user...")
            test_user = User.query.filter_by(email='test@example.com').first()
            if not test_user:
                test_user = User(
                    username='testuser',
                    email='test@example.com',
                    phone_number='9876543210',
                    password_hash=generate_password_hash('password123'),
                    usdt_balance=500.0,
                    is_active=True
                )
                db.session.add(test_user)
                db.session.commit()
            
            # 3. Create admin user
            print("3. Ensuring admin user exists...")
            admin = User.query.filter_by(is_admin=True).first()
            if not admin:
                admin = User(
                    username='admin',
                    email='admin@platform.com',
                    phone_number='1234567890',
                    password_hash=generate_password_hash('admin123'),
                    is_admin=True,
                    is_active=True,
                    usdt_balance=10000.0
                )
                db.session.add(admin)
                db.session.commit()
            
            # 4. Create sample support ticket
            print("4. Creating sample support ticket...")
            existing_ticket = SupportMessage.query.filter_by(user_id=test_user.id).first()
            if not existing_ticket:
                ticket = SupportMessage(
                    user_id=test_user.id,
                    problem_type='account',
                    subject='Test Support Ticket',
                    message='I need help with my account balance verification.',
                    priority='normal',
                    status='open'
                )
                db.session.add(ticket)
                db.session.commit()
                print(f"   ✓ Created ticket: {ticket.subject}")
            
            # 5. Create sample AI responses
            print("5. Creating sample AI responses...")
            sample_responses = [
                {
                    'trigger_words': 'salary,plan,monthly,payment,eligible',
                    'response_text': '''
                    <div class="ai-response">
                        <h4>💰 Salary Information</h4>
                        <p>Our salary plans are based on referrals and balance:</p>
                        <ul>
                            <li>Plan 1: 7 referrals + $350 balance = $50/month</li>
                            <li>Plan 2: 13 referrals + $680 balance = $110/month</li>
                            <li>Plan 3: 27 referrals + $960 balance = $230/month</li>
                            <li>Plan 4: 46 referrals + $1340 balance = $480/month</li>
                        </ul>
                        <p>Payments are processed automatically on the 1st of each month.</p>
                    </div>
                    ''',
                    'category': 'salary',
                    'priority': 10
                },
                {
                    'trigger_words': 'referral,commission,refer,bonus',
                    'response_text': '''
                    <div class="ai-response">
                        <h4>👥 Referral Program</h4>
                        <p>Our referral system offers great benefits:</p>
                        <ul>
                            <li>5% commission on each referral's balance</li>
                            <li>Commission awarded when referral reaches 100+ USDT</li>
                            <li>2+ referrals = Premium benefits</li>
                            <li>No withdrawal fees for premium members</li>
                        </ul>
                        <p>Share your referral code to start earning!</p>
                    </div>
                    ''',
                    'category': 'referral',
                    'priority': 8
                },
                {
                    'trigger_words': 'stake,staking,invest,investment,earnings',
                    'response_text': '''
                    <div class="ai-response">
                        <h4>📊 Staking Information</h4>
                        <p>Our staking platform offers:</p>
                        <ul>
                            <li>Daily returns from 0.5% to 2.0%</li>
                            <li>Multiple duration options (7-180 days)</li>
                            <li>5 different cryptocurrencies</li>
                            <li>Automatic profit calculation</li>
                        </ul>
                        <p>Visit the Stake page to explore available plans.</p>
                    </div>
                    ''',
                    'category': 'staking',
                    'priority': 6
                },
                {
                    'trigger_words': 'balance,wallet,money,funds,account',
                    'response_text': '''
                    <div class="ai-response">
                        <h4>💳 Account Balance</h4>
                        <p>Your balance information includes:</p>
                        <ul>
                            <li>Available balance for trading</li>
                            <li>Total staked amount</li>
                            <li>Current earnings from stakes</li>
                            <li>Referral bonuses</li>
                        </ul>
                        <p>Check your Assets page for detailed information.</p>
                    </div>
                    ''',
                    'category': 'account',
                    'priority': 5
                }
            ]
            
            for response_data in sample_responses:
                existing = SupportResponse.query.filter_by(
                    trigger_words=response_data['trigger_words']
                ).first()
                
                if not existing:
                    response = SupportResponse(
                        trigger_words=response_data['trigger_words'],
                        response_text=response_data['response_text'],
                        category=response_data['category'],
                        priority=response_data['priority'],
                        is_active=True,
                        created_by=admin.id
                    )
                    db.session.add(response)
            
            db.session.commit()
            
            # 6. Test AI response matching
            print("6. Testing AI response matching...")
            test_queries = [
                'What is my salary status?',
                'How do referrals work?',
                'Show me my stake details',
                'What is my balance?',
                'Help me with general question'
            ]
            
            for query in test_queries:
                response = SupportResponse.find_response(query)
                if response:
                    print(f"   ✓ Query: '{query}' → Response: {response.category}")
                else:
                    print(f"   ○ Query: '{query}' → No specific response (will use default)")
            
            print("\n✅ Comprehensive support system test completed successfully!")
            print("📋 Summary:")
            print(f"   - Test user: {test_user.email}")
            print(f"   - Admin user: {admin.email}")
            print(f"   - Support tickets: {len(SupportMessage.query.all())}")
            print(f"   - AI responses: {len(SupportResponse.query.all())}")
            print(f"   - Active AI responses: {len(SupportResponse.query.filter_by(is_active=True).all())}")
            
            print("\n🎯 Available Routes:")
            print("   - User: /support (hybrid AI + human support)")
            print("   - Admin: /admin/support-tickets (ticket management)")
            print("   - Admin: /admin/support-responses (AI response management)")
            print("   - API: /api/ai-support (AI chat endpoint)")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during support system test: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    test_comprehensive_support()