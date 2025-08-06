import os
import random
import uuid
from datetime import datetime, timedelta
from flask import render_template, redirect, url_for, flash, request, jsonify, send_file
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
import qrcode
import io
import base64
from app import app, db
from models import User, Coin, StakingPlan, Stake, Deposit, Withdrawal, PlatformSettings, ActivityLog, PaymentAddress, ContentSection, SupportMessage, NFT, NFTCollection, UICustomization, PlatformNotice, WithdrawalSettings, SocialMediaLink, SupportResponse, Notification, UserNotificationView
from models_enhanced import CoinReturnRate
from forms import LoginForm, RegisterForm, StakeForm, DepositForm, WithdrawalForm, AdminUserForm, AdminCoinForm, AdminStakingPlanForm, AdminSettingsForm, AdminPasswordChangeForm, AdminPaymentAddressForm, AdminContentForm, SupportMessageForm, AdminSupportReplyForm, AdminUICustomizationForm, AdminNFTForm, AdminNoticeForm, AdminWithdrawalSettingsForm, AdminWithdrawalApprovalForm, AdminSocialMediaForm, ProfileForm, AdminSupportResponseForm
from enhanced_forms import AdminCoinReturnRateForm
from utils import log_activity, generate_qr_code, admin_required
# OTP system removed - using simple registration

# Public routes
@app.route('/test')
def test():
    return render_template('test.html')

# Test route removed - using main register route

@app.route('/fix-all-bugs')
def fix_all_bugs():
    """Run comprehensive bug fix"""
    from comprehensive_bug_fix import comprehensive_bug_fix
    success = comprehensive_bug_fix()
    if success:
        return jsonify({'success': True, 'message': 'All bugs fixed successfully!'})
    else:
        return jsonify({'success': False, 'message': 'Some issues encountered during fix'})

@app.route('/process-automatic-salaries')
@login_required
@admin_required
def process_automatic_salaries():
    """Process automatic salary requests for all eligible users (Admin only)"""
    try:
        from automatic_salary_system import process_monthly_salary_requests
        count = process_monthly_salary_requests()
        flash(f'Successfully processed {count} automatic salary requests', 'success')
        return redirect(url_for('admin_salary_requests'))
    except Exception as e:
        flash(f'Error processing automatic salary requests: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/check-and-process-daily-salaries')
def check_and_process_daily_salaries():
    """Daily check for salary processing (can be called by cron or manually)"""
    try:
        from automatic_salary_system import check_and_process_monthly_salaries
        count = check_and_process_monthly_salaries()
        return jsonify({
            'success': True,
            'processed_count': count,
            'message': f'Daily check completed. Processed {count} salary requests.' if count > 0 else 'Not the 1st of month - no processing needed.'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error in daily salary check'
        })

@app.route('/test-automatic-salaries')
def test_automatic_salaries():
    """Test automatic salary system (Public for testing)"""
    try:
        from automatic_salary_system import process_monthly_salary_requests
        count = process_monthly_salary_requests()
        return jsonify({
            'success': True,
            'processed_count': count,
            'message': f'Successfully processed {count} automatic salary requests'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error processing automatic salary requests'
        })

@app.route('/comprehensive-system-test')
def comprehensive_system_test():
    """Comprehensive system test - Delete users, create 45 referrals, test all features"""
    try:
        result = {
            'success': True,
            'steps': [],
            'errors': []
        }
        
        # Step 1: Reset database
        result['steps'].append('Step 1: Resetting database...')
        
        # Get admin user
        admin = User.query.filter_by(is_admin=True).first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@platform.com',
                password_hash=generate_password_hash('admin123'),
                phone_number='1234567890',
                is_admin=True,
                referral_code='ADMIN',
                usdt_balance=10000.0
            )
            db.session.add(admin)
            db.session.commit()
            result['steps'].append('✅ Admin user created')
        
        # Delete non-admin data with proper foreign key handling
        admin_id = admin.id
        
        # Get all non-admin user IDs first
        non_admin_users = User.query.filter(User.is_admin == False).all()
        non_admin_ids = [user.id for user in non_admin_users]
        
        if non_admin_ids:
            # Delete all related data first
            Stake.query.filter(Stake.user_id.in_(non_admin_ids)).delete()
            Deposit.query.filter(Deposit.user_id.in_(non_admin_ids)).delete()
            Withdrawal.query.filter(Withdrawal.user_id.in_(non_admin_ids)).delete()
            ActivityLog.query.filter(ActivityLog.user_id.in_(non_admin_ids)).delete()
            SupportMessage.query.filter(SupportMessage.user_id.in_(non_admin_ids)).delete()
            
            # Now delete the users
            User.query.filter(User.is_admin == False).delete()
            
        db.session.commit()
        result['steps'].append('✅ Non-admin data deleted')
        
        # Step 2: Create 45 test users
        result['steps'].append('Step 2: Creating 45 test users...')
        
        for i in range(45):
            username = f'test_user_{i+1:02d}'
            email = f'test{i+1:02d}@email.com'
            phone = f'987654{i+1:04d}'
            
            user = User(
                username=username,
                email=email,
                phone_number=phone,
                password_hash=generate_password_hash('password123'),
                referred_by=admin.id,
                usdt_balance=100.0
            )
            db.session.add(user)
            db.session.flush()  # Get the user ID before creating deposit
            
            # Add approved deposit for each user
            deposit = Deposit(
                user_id=user.id,
                amount=100.0,
                transaction_id=f'TXN_{uuid.uuid4().hex[:8]}',
                status='approved',
                processed_at=datetime.utcnow()
            )
            db.session.add(deposit)
            
            if i % 10 == 0:
                db.session.commit()
        
        db.session.commit()
        result['steps'].append('✅ 45 test users created with 100 USDT each')
        
        # Step 3: Create coins if not exist
        result['steps'].append('Step 3: Setting up coins and staking plans...')
        
        if Coin.query.count() == 0:
            coins = [
                {'symbol': 'USDT', 'name': 'Tether USD', 'min_stake': 50.0, 'icon_emoji': '💰'},
                {'symbol': 'BTC', 'name': 'Bitcoin', 'min_stake': 250.0, 'icon_emoji': '₿'},
                {'symbol': 'ETH', 'name': 'Ethereum', 'min_stake': 170.0, 'icon_emoji': '⟠'},
                {'symbol': 'BNB', 'name': 'Binance Coin', 'min_stake': 90.0, 'icon_emoji': '🔶'},
                {'symbol': 'LTC', 'name': 'Litecoin', 'min_stake': 130.0, 'icon_emoji': '🔱'}
            ]
            
            for coin_data in coins:
                coin = Coin(**coin_data)
                db.session.add(coin)
            
            db.session.commit()
            result['steps'].append('✅ Coins created')
        
        # Create staking plans
        if StakingPlan.query.count() == 0:
            durations = [7, 15, 30, 90, 120, 180]
            rates = [0.5, 0.8, 1.0, 1.5, 1.8, 2.0]
            
            coins = Coin.query.all()
            for coin in coins:
                for duration, rate in zip(durations, rates):
                    plan = StakingPlan(
                        coin_id=coin.id,
                        duration_days=duration,
                        interest_rate=rate
                    )
                    db.session.add(plan)
            
            db.session.commit()
            result['steps'].append('✅ Staking plans created')
        
        # Step 4: Verify system
        result['steps'].append('Step 4: Verifying system...')
        
        admin_count = User.query.filter_by(is_admin=True).count()
        user_count = User.query.filter_by(is_admin=False).count()
        deposits_count = Deposit.query.count()
        referrals_count = User.query.filter_by(referred_by=admin.id).count()
        coins_count = Coin.query.count()
        plans_count = StakingPlan.query.count()
        
        result['verification'] = {
            'admin_users': admin_count,
            'regular_users': user_count,
            'total_deposits': deposits_count,
            'admin_referrals': referrals_count,
            'coins': coins_count,
            'staking_plans': plans_count
        }
        
        result['steps'].append('✅ System verification completed')
        result['message'] = 'Comprehensive system test completed successfully!'
        
        # Step 5: Award referral commissions manually for test data
        result['steps'].append('Step 5: Processing referral commissions...')
        
        # Process referral commissions for all test users
        from referral_utils import award_referral_commission
        test_users = User.query.filter_by(is_admin=False).all()
        
        for user in test_users:
            if user.referred_by:
                # Award commission for the 100 USDT deposit
                award_referral_commission(user, 100.0)
        
        db.session.commit()
        result['steps'].append('✅ Referral commissions processed')
        
        # Final verification
        admin_updated = User.query.filter_by(is_admin=True).first()
        result['verification']['admin_referral_bonus'] = admin_updated.referral_bonus
        result['verification']['admin_balance'] = admin_updated.usdt_balance
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error during comprehensive system test'
        })

@app.route('/fix-referral-commission')
def fix_referral_commission():
    """Fix referral commission for existing test users"""
    try:
        admin = User.query.filter_by(is_admin=True).first()
        if not admin:
            return jsonify({'error': 'Admin user not found'})
        
        # Get all test users
        test_users = User.query.filter_by(is_admin=False).all()
        if not test_users:
            return jsonify({'error': 'No test users found'})
        
        # Reset admin referral bonus for clean test
        original_bonus = admin.referral_bonus
        admin.referral_bonus = 0
        db.session.commit()
        
        # Award commission for each test user
        from referral_utils import award_referral_commission
        commissioned_users = 0
        
        for user in test_users:
            if user.referred_by == admin.id:
                # Check if user has a deposit
                deposit = Deposit.query.filter_by(user_id=user.id).first()
                if deposit:
                    # Award commission for the deposit
                    award_referral_commission(user, deposit.amount)
                    commissioned_users += 1
        
        db.session.commit()
        
        # Get updated admin
        admin_updated = User.query.filter_by(is_admin=True).first()
        
        return jsonify({
            'success': True,
            'commissioned_users': commissioned_users,
            'original_bonus': original_bonus,
            'new_bonus': admin_updated.referral_bonus,
            'commission_earned': admin_updated.referral_bonus - original_bonus,
            'test_users_count': len(test_users),
            'message': f'Referral commission fixed! {commissioned_users} users processed'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error fixing referral commission'
        })

@app.route('/manual-fix-referral-bonus')
def manual_fix_referral_bonus():
    """Manually fix referral bonus for admin"""
    try:
        # Get admin user
        admin = User.query.filter_by(is_admin=True).first()
        if not admin:
            return jsonify({'error': 'Admin user not found'})
        
        # Get all non-admin users (referrals)
        referrals = User.query.filter_by(is_admin=False).all()
        admin_referrals = [user for user in referrals if user.referred_by == admin.id]
        
        # Calculate total commission (5% of all deposits >= 100 USDT)
        total_commission = 0
        commission_details = []
        
        for user in admin_referrals:
            # Each referral with 100 USDT deposit gives 5 USDT commission
            deposits = Deposit.query.filter_by(user_id=user.id).all()
            for deposit in deposits:
                if deposit.amount >= 100:
                    commission = deposit.amount * 0.05  # 5% commission
                    total_commission += commission
                    commission_details.append({
                        'user': user.username,
                        'deposit': deposit.amount,
                        'commission': commission
                    })
                    break  # Only first deposit
        
        # Reset admin bonus and balance first
        old_bonus = admin.referral_bonus
        old_balance = admin.usdt_balance
        
        # Update admin referral bonus AND add to balance
        admin.referral_bonus = total_commission
        admin.usdt_balance = 10000.0 + total_commission  # Reset to 10000 + commission
        db.session.commit()
        
        return jsonify({
            'success': True,
            'admin_referrals_count': len(admin_referrals),
            'total_referrals_count': len(referrals),
            'total_commission': total_commission,
            'commission_details': commission_details,
            'old_bonus': old_bonus,
            'new_bonus': admin.referral_bonus,
            'old_balance': old_balance,
            'new_balance': admin.usdt_balance,
            'message': f'Referral bonus fixed! {len(admin_referrals)} referrals = ${total_commission:.2f} commission'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error fixing referral bonus'
        })

@app.route('/calculate-correct-commission')
def calculate_correct_commission():
    """Calculate and show correct commission calculation"""
    try:
        # Get admin user
        admin = User.query.filter_by(is_admin=True).first()
        if not admin:
            return jsonify({'error': 'Admin user not found'})
        
        # Get all admin referrals
        admin_referrals = User.query.filter_by(referred_by=admin.id).all()
        
        # Calculate commission for each referral
        commission_breakdown = []
        total_commission = 0
        
        for user in admin_referrals:
            deposits = Deposit.query.filter_by(user_id=user.id).all()
            user_commission = 0
            for deposit in deposits:
                if deposit.amount >= 100:
                    commission = deposit.amount * 0.05  # 5% commission
                    user_commission += commission
                    total_commission += commission
                    commission_breakdown.append({
                        'username': user.username,
                        'deposit_amount': deposit.amount,
                        'commission': commission
                    })
                    break  # Only first deposit
        
        # Update admin balance and bonus
        admin.referral_bonus = total_commission
        admin.usdt_balance = 10000.0 + total_commission  # Reset base + commission
        db.session.commit()
        
        return jsonify({
            'success': True,
            'admin_referrals_count': len(admin_referrals),
            'total_commission': total_commission,
            'commission_breakdown': commission_breakdown,
            'admin_new_balance': admin.usdt_balance,
            'admin_new_bonus': admin.referral_bonus,
            'calculation': f'{len(admin_referrals)} referrals × 100 USDT × 5% = {total_commission:.2f} USDT',
            'message': 'Referral commission calculated and updated successfully!'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error calculating commission'
        })

@app.route('/create-admin-referrals')
def create_admin_referrals():
    """Create admin referral users with deposits for testing"""
    try:
        # Get admin user
        admin = User.query.filter_by(email='admin@platform.com').first()
        if not admin:
            return jsonify({'success': False, 'error': 'Admin user not found'})
        
        # Ensure admin has referral code
        if not admin.referral_code:
            admin.referral_code = 'ADMIN'
            db.session.commit()
        
        # Create 10 referral users (reduced for stability)
        users_created = 0
        
        for i in range(1, 11):
            username = f'refuser{i:02d}'
            email = f'refuser{i:02d}@test.com'
            phone = f'+1555{i:03d}0000'
            
            # Check if user already exists
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                continue
            
            # Create new user
            user = User(
                username=username,
                email=email,
                phone_number=phone,
                is_admin=False,
                is_active=True,
                usdt_balance=500.0,
                referred_by=admin.id,
                referral_code=str(uuid.uuid4())[:8].upper()
            )
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()  # Commit to get user.id
            users_created += 1
            
            # Create deposit for user
            deposit = Deposit(
                user_id=user.id,
                amount=100.0,
                transaction_id=f'TEST{i:02d}',
                status='approved',
                blockchain_verified=True
            )
            db.session.add(deposit)
            db.session.commit()
        
        # Get final count
        admin_referral_count = User.query.filter_by(referred_by=admin.id).count()
        
        return jsonify({
            'success': True,
            'users_created': users_created,
            'admin_referral_count': admin_referral_count,
            'message': f'Created {users_created} referral users for admin testing'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/setup-database')
def setup_database():
    """Setup database with coins and individual staking plans"""
    try:
        # Clear existing data
        Stake.query.delete()
        StakingPlan.query.delete()
        Coin.query.delete()
        db.session.commit()
        
        # Create multiple coins
        coins_data = [
            {'symbol': 'USDT', 'name': 'Tether USD', 'min_stake': 10.0, 'icon_emoji': '💰'},
            {'symbol': 'BTC', 'name': 'Bitcoin', 'min_stake': 250.0, 'icon_emoji': '₿'},
            {'symbol': 'ETH', 'name': 'Ethereum', 'min_stake': 170.0, 'icon_emoji': '⟠'},
            {'symbol': 'BNB', 'name': 'Binance Coin', 'min_stake': 90.0, 'icon_emoji': '🟡'},
            {'symbol': 'LTC', 'name': 'Litecoin', 'min_stake': 130.0, 'icon_emoji': '🪙'}
        ]
        
        created_coins = []
        for coin_data in coins_data:
            coin = Coin(
                symbol=coin_data['symbol'],
                name=coin_data['name'],
                min_stake=coin_data['min_stake'],
                icon_emoji=coin_data['icon_emoji'],
                active=True
            )
            db.session.add(coin)
            created_coins.append(coin)
        
        db.session.commit()
        
        # Create individual plans for each coin with different rates
        coin_specific_rates = {
            'USDT': [0.5, 0.8, 1.2, 1.5, 1.8, 2.0],
            'BTC': [0.4, 0.7, 1.0, 1.3, 1.6, 1.9],
            'ETH': [0.6, 0.9, 1.3, 1.6, 1.9, 2.2],
            'BNB': [0.7, 1.0, 1.4, 1.7, 2.0, 2.3],
            'LTC': [0.5, 0.8, 1.1, 1.4, 1.7, 2.0]
        }
        
        durations = [7, 15, 30, 90, 120, 180]
        total_plans = 0
        
        for coin in created_coins:
            rates = coin_specific_rates.get(coin.symbol, [0.5, 0.8, 1.2, 1.5, 1.8, 2.0])
            
            for i, duration in enumerate(durations):
                rate = rates[i] if i < len(rates) else rates[-1]
                plan = StakingPlan(coin_id=coin.id, duration_days=duration, interest_rate=rate, active=True)
                db.session.add(plan)
                total_plans += 1
        
        db.session.commit()
        
        # Set admin balance
        admin = User.query.filter_by(email='admin@platform.com').first()
        if admin:
            admin.usdt_balance = 10000.0
            db.session.commit()
        
        return f"✅ Database setup complete! Coins: {len(created_coins)}, Plans: {total_plans}"
        
    except Exception as e:
        return f"❌ Error: {str(e)}"

@app.route('/setup-nfts')
def setup_nfts():
    """Setup dummy NFTs for admin editing"""
    try:
        # Clear existing NFTs first
        NFT.query.delete()
        db.session.commit()
        
        # Clear existing collections
        NFTCollection.query.delete()
        db.session.commit()
        
        # Create fresh collections
        collections_data = [
            {'name': 'CryptoPunks', 'symbol': 'PUNK', 'description': 'Original NFT collection'},
            {'name': 'Bored Apes', 'symbol': 'BAYC', 'description': 'Popular ape collection'}, 
            {'name': 'Mutant Apes', 'symbol': 'MAYC', 'description': 'Mutant versions'},
            {'name': 'Azuki', 'symbol': 'AZUKI', 'description': 'Anime-style collection'},
            {'name': 'Cool Cats', 'symbol': 'COOL', 'description': 'Cool cat NFTs'},
            {'name': 'Art Blocks', 'symbol': 'ART', 'description': 'Generative art NFTs'},
            {'name': 'Doodles', 'symbol': 'DOODLE', 'description': 'Colorful character NFTs'},
            {'name': 'CloneX', 'symbol': 'CLONE', 'description': 'Futuristic avatar NFTs'}
        ]
        
        for col_data in collections_data:
            collection = NFTCollection(
                name=col_data['name'],
                symbol=col_data['symbol'],
                description=col_data['description']
            )
            db.session.add(collection)
        
        db.session.commit()
        
        # Get fresh collection IDs
        collections = NFTCollection.query.all()
        collection_map = {col.symbol: col.id for col in collections}
        
        # Add 15 dummy NFTs for better display
        nft_data = [
            {'name': 'Crypto Punk #1024', 'price': 125.50, 'collection': 'PUNK', 'verified': True, 'icon': '🎭'},
            {'name': 'Bored Ape #5672', 'price': 89.99, 'collection': 'BAYC', 'verified': True, 'icon': '🦍'},
            {'name': 'Mutant Ape #3847', 'price': 67.25, 'collection': 'MAYC', 'verified': False, 'icon': '🧪'},
            {'name': 'Azuki #2156', 'price': 156.75, 'collection': 'AZUKI', 'verified': True, 'icon': '⚡'},
            {'name': 'Cool Cat #7892', 'price': 45.80, 'collection': 'COOL', 'verified': False, 'icon': '😸'},
            {'name': 'Crypto Punk #8341', 'price': 234.99, 'collection': 'PUNK', 'verified': True, 'icon': '👑'},
            {'name': 'Bored Ape #1967', 'price': 178.25, 'collection': 'BAYC', 'verified': True, 'icon': '🚀'},
            {'name': 'Azuki #4523', 'price': 99.50, 'collection': 'AZUKI', 'verified': False, 'icon': '🌸'},
            {'name': 'Cool Cat #6784', 'price': 73.40, 'collection': 'COOL', 'verified': True, 'icon': '🎯'},
            {'name': 'Art Block #9876', 'price': 145.30, 'collection': 'ART', 'verified': True, 'icon': '🎨'},
            {'name': 'Doodle #5432', 'price': 88.75, 'collection': 'DOODLE', 'verified': False, 'icon': '🌈'},
            {'name': 'CloneX #2109', 'price': 195.60, 'collection': 'CLONE', 'verified': True, 'icon': '🤖'},
            {'name': 'Art Block #3456', 'price': 112.25, 'collection': 'ART', 'verified': False, 'icon': '🔥'},
            {'name': 'Doodle #7890', 'price': 76.90, 'collection': 'DOODLE', 'verified': True, 'icon': '💎'},
            {'name': 'CloneX #4567', 'price': 203.40, 'collection': 'CLONE', 'verified': False, 'icon': '⭐'}
        ]
        
        gradients = [
            'from-blue-500 to-purple-600',
            'from-red-500 to-orange-500',
            'from-green-500 to-blue-500',
            'from-purple-600 to-pink-600',
            'from-yellow-400 to-orange-500',
            'from-indigo-500 to-purple-500',
            'from-pink-500 to-red-500',
            'from-cyan-500 to-blue-500'
        ]
        
        import uuid
        for i, data in enumerate(nft_data):
            nft = NFT(
                name=data['name'],
                collection_id=collection_map[data['collection']],
                icon=data['icon'],
                image_url=f'https://picsum.photos/300/300?random={2000+i}',
                gradient=gradients[i % len(gradients)],
                price=data['price'],
                last_sale_price=data['price'] * 0.85,
                unique_id=f'NFT{uuid.uuid4().hex[:6].upper()}',
                is_verified=data['verified'],
                rarity=5 if data['verified'] else (3 + (i % 3)),
                description=f'Premium NFT: {data["name"]}',
                owner_name=f'Collector{1000 + i}',
                is_active=True,
                display_order=i
            )
            db.session.add(nft)
        
        db.session.commit()
        
        # Verify count
        nft_count = NFT.query.count()
        collection_count = NFTCollection.query.count()
        
        return jsonify({
            'success': True,
            'status': f'Successfully added {nft_count} NFTs and {collection_count} collections',
            'nft_count': nft_count,
            'collection_count': collection_count,
            'message': 'NFTs are now ready to display on /nfts page'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'status': 'Failed to setup NFTs'
        })

@app.route('/debug-admin')
def debug_admin():
    """Debug route to check admin user and create if needed"""
    try:
        # Check if admin exists
        admin = User.query.filter_by(email='admin@platform.com').first()
        
        if admin:
            # Reset admin password to ensure it works
            admin.set_password('admin123')
            admin.is_admin = True
            admin.is_active = True
            db.session.commit()
            
            return jsonify({
                'status': 'Admin user found and updated',
                'email': admin.email,
                'username': admin.username,
                'is_admin': admin.is_admin,
                'is_active': admin.is_active,
                'password_reset': 'admin123'
            })
        else:
            # Create new admin user
            admin = User(
                username='admin',
                email='admin@platform.com',
                phone_number='+1234567890',
                is_admin=True,
                is_active=True,
                usdt_balance=10000.0
            )
            admin.set_password('admin123')
            
            db.session.add(admin)
            db.session.commit()
            
            return jsonify({
                'status': 'New admin user created',
                'email': admin.email,
                'username': admin.username,
                'is_admin': admin.is_admin,
                'is_active': admin.is_active,
                'password': 'admin123'
            })
            
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'Failed to create/update admin user'
        })

@app.route('/fix-database')
def fix_database():
    """Fix staking and deposit database issues"""
    try:
        # Check current database status
        coin_count = Coin.query.count()
        plan_count = StakingPlan.query.count()
        user_count = User.query.count()
        
        result = {
            'initial_status': f'Found {coin_count} coins, {plan_count} plans, {user_count} users',
            'actions_taken': []
        }
        
        # Add coins if missing
        if coin_count == 0:
            coins_data = [
                {'symbol': 'USDT', 'name': 'Tether USD', 'min_stake': 10.0, 'icon_emoji': '💰'},
                {'symbol': 'BTC', 'name': 'Bitcoin', 'min_stake': 250.0, 'icon_emoji': '₿'},
                {'symbol': 'ETH', 'name': 'Ethereum', 'min_stake': 170.0, 'icon_emoji': '⧫'},
                {'symbol': 'BNB', 'name': 'Binance Coin', 'min_stake': 90.0, 'icon_emoji': '🔸'},
                {'symbol': 'LTC', 'name': 'Litecoin', 'min_stake': 130.0, 'icon_emoji': 'Ł'}
            ]
            
            for coin_data in coins_data:
                coin = Coin(
                    symbol=coin_data['symbol'],
                    name=coin_data['name'],
                    min_stake=coin_data['min_stake'],
                    active=True,
                    icon_emoji=coin_data['icon_emoji']
                )
                db.session.add(coin)
            
            db.session.commit()
            result['actions_taken'].append('Added 5 basic coins')
        
        # Add staking plans if missing
        if plan_count == 0:
            coins = Coin.query.all()
            plan_data = [
                {'duration_days': 7, 'interest_rate': 0.8},
                {'duration_days': 15, 'interest_rate': 1.2},
                {'duration_days': 30, 'interest_rate': 1.5},
                {'duration_days': 90, 'interest_rate': 1.8},
                {'duration_days': 120, 'interest_rate': 2.0},
                {'duration_days': 180, 'interest_rate': 2.2}
            ]
            
            for coin in coins:
                for plan in plan_data:
                    staking_plan = StakingPlan(
                        coin_id=coin.id,
                        duration_days=plan['duration_days'],
                        interest_rate=plan['interest_rate'],
                        active=True
                    )
                    db.session.add(staking_plan)
            
            db.session.commit()
            result['actions_taken'].append(f'Added {len(plan_data)} staking plans for each coin')
        
        # Ensure admin user exists
        admin = User.query.filter_by(email='admin@platform.com').first()
        if not admin:
            import uuid
            admin = User(
                username='admin',
                email='admin@platform.com',
                phone_number='+1234567890',
                is_admin=True,
                is_active=True,
                usdt_balance=10000.0,
                referral_code=str(uuid.uuid4())[:8].upper()
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            result['actions_taken'].append('Created admin user')
        
        # Add payment address if missing
        payment_address = PaymentAddress.query.first()
        if not payment_address:
            payment_address = PaymentAddress(
                address='0xae49d3b4775c0524bd81da704340b5ef5a7416e9',
                network='BEP20',
                is_active=True
            )
            db.session.add(payment_address)
            db.session.commit()
            result['actions_taken'].append('Added payment address')
        
        # Final status
        final_coins = Coin.query.count()
        final_plans = StakingPlan.query.count()
        final_users = User.query.count()
        
        result['final_status'] = f'Database now has {final_coins} coins, {final_plans} plans, {final_users} users'
        result['success'] = True
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False,
            'message': 'Failed to fix database'
        })

@app.route('/test-staking-system')
def test_staking_system():
    """Test the staking system functionality"""
    try:
        # Check coins and plans
        coins = Coin.query.filter_by(active=True).all()
        
        result = {
            'coins_count': len(coins),
            'coins': [],
            'plans_by_coin': {}
        }
        
        for coin in coins:
            coin_data = {
                'id': coin.id,
                'symbol': coin.symbol,
                'name': coin.name,
                'min_stake': coin.min_stake,
                'active': coin.active
            }
            result['coins'].append(coin_data)
            
            # Get plans for this coin
            plans = StakingPlan.query.filter_by(coin_id=coin.id, active=True).all()
            result['plans_by_coin'][coin.id] = []
            
            for plan in plans:
                plan_data = {
                    'id': plan.id,
                    'duration_days': plan.duration_days,
                    'interest_rate': plan.interest_rate,
                    'active': plan.active
                }
                result['plans_by_coin'][coin.id].append(plan_data)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        })



@app.route('/test-verification')
def test_verification():
    """Debug route to test blockchain verification with Moralis API"""
    try:
        import os
        from blockchain_utils import blockchain_verifier
        
        # Test with your specific transaction
        test_tx = "0xacfbad4b2a73d02ac6cbd54729fcebb1343c2fb3e8bc8edf958c4e1410709e10"
        test_amount = 39.0
        
        # Test API key first
        api_key = os.environ.get('BSCSCAN_API_KEY', 'NOT_FOUND')
        
        result = blockchain_verifier.verify_usdt_transaction(
            test_tx, 
            test_amount, 
            blockchain_verifier.wallet_address
        )
        
        return jsonify({
            'verification_result': result,
            'wallet_address': blockchain_verifier.wallet_address,
            'usdt_contract': blockchain_verifier.usdt_contract,
            'tx_hash_format_check': blockchain_verifier._is_valid_tx_format(test_tx),
            'test_tx': test_tx,
            'test_amount': test_amount,
            'api_key_length': len(api_key) if api_key != 'NOT_FOUND' else 0,
            'api_key_available': api_key != 'NOT_FOUND'
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'wallet_address': getattr(blockchain_verifier, 'wallet_address', 'Not loaded') if 'blockchain_verifier' in locals() else 'Not loaded'
        })

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    else:
        return redirect(url_for('register'))

@app.route('/landing-simple')
def landing_simple():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    settings = PlatformSettings.get_all_settings()
    return render_template('index_simple.html', settings=settings)

@app.route('/home')
@login_required
def home():
    user_stats = {
        'usdt_balance': current_user.usdt_balance,
        'total_staked': current_user.total_staked,
        'total_earned': current_user.total_earned,
        'referral_bonus': current_user.referral_bonus
    }
    
    # Get recent activities
    recent_stakes = Stake.query.filter_by(user_id=current_user.id).order_by(Stake.created_at.desc()).limit(5).all()
    
    # Get notices for home page
    notices = PlatformNotice.get_notices('home')
    
    return render_template('home.html', user_stats=user_stats, recent_stakes=recent_stakes, notices=notices)

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        # Debug: Check if user exists and print info
        if user:
            print(f"DEBUG: User found - {user.email}, is_admin: {user.is_admin}, is_active: {user.is_active}")
            password_check = user.check_password(form.password.data)
            print(f"DEBUG: Password check result: {password_check}")
            
            if password_check and user.is_active:
                login_user(user)
                log_activity(user.id, 'login', f'User {user.username} logged in')
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('home'))
            else:
                if not password_check:
                    flash('Invalid password', 'error')
                else:
                    flash('Account is not active', 'error')
        else:
            print(f"DEBUG: No user found with email: {form.email.data}")
            flash('Invalid email or password', 'error')
    
    return render_template('auth/login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = RegisterForm()
    
    if form.validate_on_submit():
        try:
            print("DEBUG: Registration POST request received")
            
            # Get form data from FlaskForm
            username = form.username.data.strip()
            email = form.email.data.strip().lower()
            phone_number = form.phone_number.data.strip()
            password = form.password.data
            referral_code = form.referral_code.data.strip().upper() if form.referral_code.data else None
            
            print(f"DEBUG: Form data - username: {username}, email: {email}, phone: {phone_number}")
            
            # Handle referral code
            referrer = None
            if referral_code:
                referrer = User.query.filter_by(referral_code=referral_code).first()
                if not referrer:
                    flash('Invalid referral code. Please check and try again.', 'error')
                    return render_template('auth/register_premium.html', form=form)
                print(f"DEBUG: Valid referrer found: {referrer.username}")
            
            print("DEBUG: Creating new user...")
            
            # Generate unique referral code
            import uuid
            new_referral_code = str(uuid.uuid4())[:8].upper()
            
            # Ensure referral code is unique
            while User.query.filter_by(referral_code=new_referral_code).first():
                new_referral_code = str(uuid.uuid4())[:8].upper()
            
            # Create new user
            user = User(
                username=username,
                email=email,
                phone_number=phone_number,
                referred_by=referrer.id if referrer else None,
                referral_code=new_referral_code,
                is_active=True,
                usdt_balance=0.0
            )
            user.set_password(password)
            
            # Add user to database
            db.session.add(user)
            db.session.flush()  # Get user ID
            
            # Referral relationship tracked but NO COMMISSION given
            if referrer:
                print(f"DEBUG: Referral relationship established with {referrer.username} - NO COMMISSION")
                
                # Log referral activity without any bonus
                log_activity(referrer.id, 'referral_tracked_no_commission', f'Referral relationship established with {username} - NO COMMISSION SYSTEM')
            
            # Commit all changes
            db.session.commit()
            print("DEBUG: User created successfully")
            
            # Log successful registration
            log_activity(user.id, 'register', f'User {username} registered successfully')
            
            flash('Registration successful! You can now login with your credentials.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            print(f"DEBUG: Registration error: {str(e)}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            flash('Registration failed due to system error. Please try again.', 'error')
            return render_template('auth/register_premium.html', form=form)
    
    print("DEBUG: Showing registration form")
    return render_template('auth/register_premium.html', form=form)



@app.route('/logout')
@login_required
def logout():
    log_activity(current_user.id, 'logout', f'User {current_user.username} logged out')
    logout_user()
    return redirect(url_for('index'))

# Staking routes
@app.route('/stake-simple', methods=['GET', 'POST'])
@login_required
def stake_simple():
    form = StakeForm()
    
    # Don't populate choices for hidden fields - they will be set by frontend
    # form.coin_id.choices = [(c.id, f"{c.symbol} - {c.name}") for c in Coin.query.filter_by(active=True).all()]
    # form.plan_id.choices = []
    
    if form.validate_on_submit():
        print(f"DEBUG: Simple form validation passed!")
        
        # Get form data directly - no duplicates in simple form
        coin_id = int(form.coin_id.data) if form.coin_id.data else None
        plan_id = int(form.plan_id.data) if form.plan_id.data else None
        
        print(f"DEBUG: Form values - coin_id: {coin_id}, plan_id: {plan_id}, amount: {form.amount.data}")
        
        if not coin_id or not plan_id:
            flash('Please select a coin and plan first', 'error')
            print(f"DEBUG: Missing selection - coin_id: {coin_id}, plan_id: {plan_id}")
            return redirect(url_for('stake'))
        
        coin = Coin.query.get(coin_id)
        plan = StakingPlan.query.get(plan_id)
        
        if not coin or not plan:
            flash('Invalid coin or plan selection', 'error')
            return redirect(url_for('stake'))
        
        if form.amount.data < coin.min_stake:
            flash(f'Minimum stake for {coin.symbol} is {coin.min_stake} USDT', 'error')
        elif form.amount.data > current_user.usdt_balance:
            flash('Insufficient balance', 'error')
        else:
            # Create stake
            end_date = datetime.utcnow() + timedelta(days=plan.duration_days)
            
            # Use standard daily interest rate (no bonus interest)
            daily_interest = plan.interest_rate
            total_return = form.amount.data * daily_interest * plan.duration_days / 100
            
            stake = Stake(
                user_id=current_user.id,
                coin_id=coin.id,
                plan_id=plan.id,
                amount=form.amount.data,
                daily_interest=daily_interest,
                total_return=total_return,
                end_date=end_date
            )
            
            # Calculate 2% instant commission for users with 2+ referrals (separate from stake returns)
            stake_commission = 0
            commission_applied = False
            if current_user.has_two_referrals():
                from simple_referral_system import calculate_user_stake_bonus
                stake_commission = calculate_user_stake_bonus(current_user.id, form.amount.data)
                if stake_commission > 0:
                    current_user.usdt_balance += stake_commission
                    commission_applied = True
                    
                    # Log the commission
                    log_activity(current_user.id, 'stake_commission', 
                               f'2% stake commission: ${stake_commission:.2f} on ${form.amount.data} stake')
            
            if commission_applied:
                flash(f'2% stake commission earned: ${stake_commission:.2f} USDT! Premium benefits active.', 'success')
            
            # Update user balance
            current_user.usdt_balance -= form.amount.data
            current_user.total_staked += form.amount.data
            
            db.session.add(stake)
            db.session.commit()
            
            log_activity(current_user.id, 'stake', f'Staked {form.amount.data} USDT in {coin.symbol} for {plan.duration_days} days')
            flash('Stake created successfully!', 'success')
            print(f"DEBUG: Stake created successfully for user {current_user.id}")
            return redirect(url_for('stake_simple'))
    else:
        if request.method == 'POST':
            print(f"DEBUG: Form validation failed - errors: {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'{field}: {error}', 'error')
    
    # Get user stakes
    user_stakes = Stake.query.filter_by(user_id=current_user.id).order_by(Stake.created_at.desc()).all()
    
    # Get coins and organize plans by coin for proper separation
    coins = Coin.query.filter_by(active=True).all()
    
    # Group plans by coin_id and convert to serializable format
    coin_plans = {}
    for coin in coins:
        # Get only plans specific to this coin (not global plans)
        coin_specific_plans = StakingPlan.query.filter_by(coin_id=coin.id, active=True).all()
        # Convert to dict format for JSON serialization
        coin_plans[coin.id] = [
            {
                'id': plan.id,
                'duration_days': plan.duration_days,
                'interest_rate': plan.interest_rate
            }
            for plan in coin_specific_plans
        ]
    
    return render_template('stake_simple.html', form=form, user_stakes=user_stakes, coins=coins, coin_plans=coin_plans)

@app.route('/stake', methods=['GET', 'POST'])
@login_required  
def stake():
    """Main stake page with original UI"""
    form = StakeForm()
    
    if form.validate_on_submit():
        print(f"DEBUG: Form validation passed!")
        
        # Get form data directly with better validation
        try:
            coin_id = int(form.coin_id.data) if form.coin_id.data and form.coin_id.data.strip() else None
            plan_id = int(form.plan_id.data) if form.plan_id.data and form.plan_id.data.strip() else None
        except (ValueError, TypeError):
            coin_id = None
            plan_id = None
        
        print(f"DEBUG: Form values - coin_id: {coin_id}, plan_id: {plan_id}, amount: {form.amount.data}")
        print(f"DEBUG: Raw form data - coin_id: '{form.coin_id.data}', plan_id: '{form.plan_id.data}'")
        
        if not coin_id or not plan_id:
            flash('Please select a coin and plan first', 'error')
            print(f"DEBUG: Missing selection - coin_id: {coin_id}, plan_id: {plan_id}")
            return redirect(url_for('stake'))
        
        coin = Coin.query.get(coin_id)
        plan = StakingPlan.query.get(plan_id)
        
        if not coin or not plan:
            flash('Invalid coin or plan selection', 'error')
            return redirect(url_for('stake'))
        
        if form.amount.data < coin.min_stake:
            flash(f'Minimum stake for {coin.symbol} is {coin.min_stake} USDT', 'error')
        elif form.amount.data > current_user.usdt_balance:
            flash('Insufficient balance', 'error')
        else:
            # Create stake
            end_date = datetime.utcnow() + timedelta(days=plan.duration_days)
            
            # Use standard daily interest rate (no bonus interest)
            daily_interest = plan.interest_rate
            total_return = form.amount.data * daily_interest * plan.duration_days / 100
            
            stake = Stake(
                user_id=current_user.id,
                coin_id=coin.id,
                plan_id=plan.id,
                amount=form.amount.data,
                daily_interest=daily_interest,
                total_return=total_return,
                end_date=end_date
            )
            
            # Calculate 2% instant commission for users with 2+ referrals (separate from stake returns)
            stake_commission = 0
            commission_applied = False
            if current_user.has_two_referrals():
                from simple_referral_system import calculate_user_stake_bonus
                stake_commission = calculate_user_stake_bonus(current_user.id, form.amount.data)
                if stake_commission > 0:
                    current_user.usdt_balance += stake_commission
                    commission_applied = True
                    
                    # Log the commission
                    log_activity(current_user.id, 'stake_commission', 
                               f'2% stake commission: ${stake_commission:.2f} on ${form.amount.data} stake')
            
            if commission_applied:
                flash(f'2% stake commission earned: ${stake_commission:.2f} USDT! Premium benefits active.', 'success')
            
            # Update user balance
            current_user.usdt_balance -= form.amount.data
            current_user.total_staked += form.amount.data
            
            db.session.add(stake)
            db.session.commit()
            
            log_activity(current_user.id, 'stake', f'Staked {form.amount.data} USDT in {coin.symbol} for {plan.duration_days} days')
            flash('Stake created successfully!', 'success')
            print(f"DEBUG: Stake created successfully for user {current_user.id}")
            return redirect(url_for('stake'))
    else:
        if request.method == 'POST':
            print(f"DEBUG: Form validation failed - errors: {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'{field}: {error}', 'error')
    
    # Get user stakes
    user_stakes = Stake.query.filter_by(user_id=current_user.id).order_by(Stake.created_at.desc()).all()
    
    # Get coins and organize plans by coin for proper separation
    coins = Coin.query.filter_by(active=True).all()
    
    # Group plans by coin_id and convert to serializable format
    coin_plans = {}
    for coin in coins:
        # Get only plans specific to this coin (not global plans)
        coin_specific_plans = StakingPlan.query.filter_by(coin_id=coin.id, active=True).all()
        # Convert to dict format for JSON serialization
        coin_plans[coin.id] = [
            {
                'id': plan.id,
                'duration_days': plan.duration_days,
                'interest_rate': plan.interest_rate
            }
            for plan in coin_specific_plans
        ]
    
    return render_template('stake_fixed.html', form=form, user_stakes=user_stakes, coins=coins, coin_plans=coin_plans, datetime=datetime)

@app.route('/api/coin-plans/<int:coin_id>')
@login_required
def api_coin_plans(coin_id):
    """API endpoint to get plans for specific coin only"""
    coin = Coin.query.get_or_404(coin_id)
    plans = StakingPlan.query.filter_by(coin_id=coin_id, active=True).all()
    
    plans_data = []
    for plan in plans:
        plans_data.append({
            'id': plan.id,
            'duration_days': plan.duration_days,
            'interest_rate': plan.interest_rate,
            'display_text': f"{plan.duration_days} days - {plan.interest_rate}% daily"
        })
    
    return jsonify({
        'coin_id': coin_id,
        'coin_symbol': coin.symbol,
        'plans': plans_data
    })

@app.route('/cancel_stake/<int:stake_id>')
@login_required
def cancel_stake(stake_id):
    stake = Stake.query.get_or_404(stake_id)
    
    if stake.user_id != current_user.id:
        flash('Unauthorized action', 'error')
        return redirect(url_for('stake'))
    
    if stake.status != 'active':
        flash('Stake cannot be cancelled', 'error')
        return redirect(url_for('stake'))
    
    # Cancel stake and return principal
    stake.status = 'cancelled'
    current_user.usdt_balance += stake.amount
    current_user.total_staked -= stake.amount
    
    # Check and update referral status after balance change
    from referral_utils import check_and_update_referral_balance
    check_and_update_referral_balance(current_user)
    
    db.session.commit()
    
    log_activity(current_user.id, 'cancel_stake', f'Cancelled stake #{stake.id}')
    flash('Stake cancelled successfully. Principal amount returned.', 'success')
    return redirect(url_for('stake'))

@app.route('/withdraw_stake/<int:stake_id>')
@login_required
def withdraw_stake(stake_id):
    stake = Stake.query.get_or_404(stake_id)
    
    if stake.user_id != current_user.id:
        flash('Unauthorized action', 'error')
        return redirect(url_for('stake'))
    
    if not stake.is_mature or stake.withdrawn:
        flash('Stake not ready for withdrawal', 'error')
        return redirect(url_for('stake'))
    
    # Calculate final return
    current_return = stake.calculate_current_return()
    total_amount = stake.amount + current_return
    
    # Update user balance
    current_user.usdt_balance += total_amount
    current_user.total_earned += current_return
    current_user.total_staked -= stake.amount
    
    stake.status = 'completed'
    stake.withdrawn = True
    
    # Check and update referral status after balance change
    from referral_utils import check_and_update_referral_balance
    check_and_update_referral_balance(current_user)
    
    db.session.commit()
    
    log_activity(current_user.id, 'withdraw_stake', f'Withdrew stake #{stake.id} - Principal: {stake.amount}, Earnings: {current_return}')
    flash(f'Stake withdrawn successfully! Total: {total_amount} USDT (Earnings: {current_return} USDT)', 'success')
    return redirect(url_for('stake'))

# Assets routes
@app.route('/assets', methods=['GET', 'POST'])
@login_required
def assets():
    deposit_form = DepositForm()
    withdrawal_form = WithdrawalForm()
    
    if request.method == 'POST':
        if 'deposit' in request.form and deposit_form.validate_on_submit():
            try:
                # Import blockchain verifier
                from blockchain_utils import BlockchainVerifier
                blockchain_verifier = BlockchainVerifier()
                
                tx_hash = deposit_form.transaction_id.data.strip()
                amount = deposit_form.amount.data
                network = request.form.get('network', 'BEP20')  # Get selected network
                
                # Validate transaction hash format
                if not tx_hash or len(tx_hash.strip()) < 40:
                    flash('❌ Invalid transaction hash format. Please provide a valid transaction hash.', 'error')
                    return redirect(url_for('assets'))
                
                # Clean the transaction hash
                tx_hash = tx_hash.strip()
                if not tx_hash.startswith('0x'):
                    tx_hash = '0x' + tx_hash
                
                # Get the correct payment address based on network
                payment_address = PaymentAddress.query.filter_by(network=network, is_active=True).first()
                if not payment_address:
                    flash(f'❌ {network} network is not currently available. Please contact support.', 'error')
                    return redirect(url_for('assets'))
                
                target_address = payment_address.address
                
                # Enhanced duplicate transaction prevention
                existing_deposit = Deposit.query.filter_by(transaction_id=tx_hash).first()
                if existing_deposit:
                    # If transaction was already successfully processed by anyone
                    if existing_deposit.status in ['verified', 'approved']:
                        flash('❌ This transaction has already been successfully processed and cannot be reused.', 'error')
                        log_activity(current_user.id, 'duplicate_transaction_attempt', f'Attempted to reuse verified transaction: {tx_hash}')
                        return redirect(url_for('assets'))
                    # If transaction was submitted by another user (even if rejected)
                    elif existing_deposit.user_id != current_user.id:
                        flash('❌ This transaction ID has already been submitted by another user and cannot be reused.', 'error')
                        log_activity(current_user.id, 'duplicate_transaction_attempt', f'Attempted to use transaction from another user: {tx_hash}')
                        return redirect(url_for('assets'))
                    # If same user submitted but was rejected, allow retry
                    elif existing_deposit.status == 'rejected' and existing_deposit.user_id == current_user.id:
                        flash('⚠️ Retrying previously rejected transaction...', 'info')
                        log_activity(current_user.id, 'retry_rejected_transaction', f'Retrying rejected transaction: {tx_hash}')
                        # Delete the rejected deposit to allow retry
                        db.session.delete(existing_deposit)
                        db.session.commit()
                
                # Minimum deposit check
                if amount < payment_address.min_deposit:
                    flash(f'❌ Minimum deposit amount is ${payment_address.min_deposit} USDT', 'error')
                    return redirect(url_for('assets'))
                
                # Log verification attempt
                log_activity(current_user.id, 'deposit_attempt', f'Attempting to verify {network} deposit: {tx_hash}, Amount: {amount}')
                
                # Verify transaction on blockchain with correct address
                verification_result = blockchain_verifier.verify_usdt_transaction(
                    tx_hash,
                    amount,
                    target_address,
                    network
                )
                
                # Log verification result for debugging
                log_activity(current_user.id, 'verification_result', f'Verification result: {verification_result}')
                
                if verification_result['success']:
                    # Check if payment was sent to correct address
                    if verification_result.get('to_address', '').lower() != target_address.lower():
                        flash(f'❌ Payment sent to wrong address. Please send to: {target_address}', 'error')
                        log_activity(current_user.id, 'wrong_address', f'Payment sent to wrong address: {verification_result.get("to_address")}')
                        return redirect(url_for('assets'))
                    
                    # Transaction verified successfully
                    deposit = Deposit(
                        user_id=current_user.id,
                        amount=amount,
                        transaction_id=tx_hash,
                        status='verified',
                        blockchain_verified=True,
                        verification_details=str(verification_result)
                    )
                    
                    # Add balance to user FIRST (before commission processing)
                    current_user.usdt_balance += amount
                    db.session.add(deposit)
                    
                    # Commit the deposit and balance update first
                    db.session.commit()
                    
                    # Automatic referral commission processing (separate transaction)
                    commission_message = ""
                    try:
                        from referral_commission_system import process_deposit_commission
                        commission_result = process_deposit_commission(current_user.id, amount)
                        if commission_result and commission_result.get('success'):
                            commission_message = f" 🎉 Referral commission of ${commission_result['commission_amount']} USDT automatically awarded to your referrer!"
                            log_activity(current_user.id, 'auto_referral_commission', 
                                       f"Automatic referral commission: ${commission_result['commission_amount']} USDT awarded to referrer")
                    except Exception as e:
                        print(f"Error processing automatic referral commission: {e}")
                        log_activity(current_user.id, 'auto_referral_commission_error', f"Error: {str(e)}")
                        # Don't let commission errors affect the deposit
                        commission_message = ""
                    
                    log_activity(current_user.id, 'deposit_verified', f'{network} deposit verified: {amount} USDT')
                    flash(f'✅ {network} deposit verified successfully! ${amount} USDT added to your balance.{commission_message}', 'success')
                else:
                    # Transaction verification failed
                    deposit = Deposit(
                        user_id=current_user.id,
                        amount=amount,
                        transaction_id=tx_hash,
                        status='rejected',
                        blockchain_verified=False,
                        verification_details=str(verification_result)
                    )
                    
                    db.session.add(deposit)
                    db.session.commit()
                    
                    error_msg = verification_result.get("error", "Unknown verification error")
                    log_activity(current_user.id, 'deposit_failed', f'Failed {network} deposit verification: {error_msg}')
                    flash(f'❌ {network} deposit verification failed: {error_msg}', 'error')
                    
            except Exception as e:
                # Handle any unexpected errors
                log_activity(current_user.id, 'deposit_error', f'Deposit processing error: {str(e)}')
                flash('❌ An error occurred while processing your deposit. Please try again.', 'error')
            
            return redirect(url_for('assets'))
        
        elif 'withdrawal' in request.form and withdrawal_form.validate_on_submit():
            
            # Get withdrawal settings for fee calculation
            settings = WithdrawalSettings.get_settings()
            base_amount = withdrawal_form.amount.data
            
            # Check if user qualifies for fee waiver
            fee_percentage = 0 if current_user.has_two_referrals() else settings.processing_fee
            fee_amount = base_amount * (fee_percentage / 100)
            net_amount = base_amount - fee_amount
            
            if current_user.has_two_referrals():
                flash('No withdrawal fee - You have 2+ referrals!', 'success')
            
            # Check balance against gross amount
            if base_amount > current_user.usdt_balance:
                flash(f'Insufficient balance. Need {base_amount:.2f} USDT (fee: {fee_percentage}% = ${fee_amount:.2f})', 'error')
                return redirect(url_for('assets'))
            
            # Deduct the full amount from user balance immediately
            current_user.usdt_balance -= base_amount
            
            # Handle withdrawal
            withdrawal = Withdrawal(
                user_id=current_user.id,
                amount=base_amount,
                fee_amount=fee_amount,
                net_amount=net_amount,
                wallet_address=withdrawal_form.wallet_address.data,
                network=withdrawal_form.network.data
            )
            
            db.session.add(withdrawal)
            db.session.commit()
            
            log_activity(current_user.id, 'withdrawal_request', f'Withdrawal request for {withdrawal_form.amount.data} USDT')
            flash('Withdrawal request submitted for admin approval', 'success')
            return redirect(url_for('assets'))
    
    # Get user transaction history
    deposits = Deposit.query.filter_by(user_id=current_user.id).order_by(Deposit.created_at.desc()).all()
    withdrawals = Withdrawal.query.filter_by(user_id=current_user.id).order_by(Withdrawal.created_at.desc()).all()
    
    # Get active payment addresses with QR codes for deposit section
    payment_addresses = PaymentAddress.query.filter_by(is_active=True).all()
    
    return render_template('assets_new.html', 
                         deposit_form=deposit_form, 
                         withdrawal_form=withdrawal_form,
                         deposits=deposits, 
                         withdrawals=withdrawals,
                         payment_addresses=payment_addresses)

# Profile routes
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    referral_tree = current_user.get_referral_tree()
    total_referrals = len([r for r in User.query.filter_by(referred_by=current_user.id).all()])
    
    # Real-time salary eligibility check - based on current balance
    current_balance = current_user.get_total_balance_including_stakes()
    qualified_referrals = current_user.get_qualified_referrals_count()  # Real-time active referrals
    is_salary_eligible = current_user.is_salary_eligible()  # Only salary eligible get blue tick
    
    # Get current eligible salary plan
    current_salary_plan = None
    if is_salary_eligible:
        salary_plans = [
            {'min_referrals': 7, 'min_balance': 350, 'monthly_salary': 50, 'name': 'Plan 1'},
            {'min_referrals': 13, 'min_balance': 680, 'monthly_salary': 110, 'name': 'Plan 2'},
            {'min_referrals': 27, 'min_balance': 960, 'monthly_salary': 230, 'name': 'Plan 3'},
            {'min_referrals': 46, 'min_balance': 1340, 'monthly_salary': 480, 'name': 'Plan 4'}
        ]
        
        for plan in reversed(salary_plans):  # Check highest plans first
            if qualified_referrals >= plan['min_referrals'] and current_balance >= plan['min_balance']:
                current_salary_plan = plan
                break
    
    # Get available default avatars
    default_avatars = [
        'default_animal_1.svg',
        'default_animal_2.svg', 
        'default_animal_3.svg',
        'default_tree_1.svg',
        'default_tree_2.svg',
        'default_car_1.svg',
        'default_car_2.svg'
    ]
    
    if form.validate_on_submit():
        # Update basic info
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.phone_number = form.phone_number.data
        
        # Handle profile picture upload
        if form.profile_picture.data:
            file = form.profile_picture.data
            if file.filename:
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{current_user.id}_{timestamp}_{filename}"
                file_path = os.path.join('static', 'uploads', 'profiles', filename)
                
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                file.save(file_path)
                current_user.profile_picture = f"uploads/profiles/{filename}"
        
        # Handle password change
        if form.current_password.data and form.new_password.data:
            if current_user.check_password(form.current_password.data):
                current_user.set_password(form.new_password.data)
                flash('Password updated successfully!', 'success')
            else:
                flash('Current password is incorrect', 'error')
                return redirect(url_for('profile'))
        
        db.session.commit()
        log_activity(current_user.id, 'profile_update', 'Profile updated successfully')
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    # Pre-populate form with current data
    form.username.data = current_user.username
    form.email.data = current_user.email
    form.phone_number.data = current_user.phone_number
    
    return render_template('profile.html', 
                         form=form,
                         referral_tree=referral_tree, 
                         total_referrals=total_referrals,
                         default_avatars=default_avatars,
                         timedelta=timedelta,
                         current_balance=current_balance,
                         qualified_referrals=qualified_referrals,
                         is_salary_eligible=is_salary_eligible,
                         current_salary_plan=current_salary_plan)

@app.route('/api/salary-eligibility-check')
@login_required
def salary_eligibility_check():
    """API endpoint for real-time salary eligibility check - Blue tick ONLY for salary eligible users"""
    try:
        # Get real-time data - check actual eligibility based on current balance
        current_balance = current_user.get_total_balance_including_stakes()
        qualified_referrals = current_user.get_qualified_referrals_count()  # Real-time active referrals
        
        # Check eligibility based on actual requirements (NO admin override)
        salary_plans = [
            {'min_referrals': 7, 'min_balance': 350, 'monthly_salary': 50, 'name': 'Plan 1'},
            {'min_referrals': 13, 'min_balance': 680, 'monthly_salary': 110, 'name': 'Plan 2'},
            {'min_referrals': 27, 'min_balance': 960, 'monthly_salary': 230, 'name': 'Plan 3'},
            {'min_referrals': 46, 'min_balance': 1340, 'monthly_salary': 480, 'name': 'Plan 4'}
        ]
        
        # Determine eligibility and current plan - STRICT checking
        is_salary_eligible = False
        current_salary_plan = None
        
        for plan in reversed(salary_plans):  # Check highest plans first
            if qualified_referrals >= plan['min_referrals'] and current_balance >= plan['min_balance']:
                is_salary_eligible = True
                current_salary_plan = plan
                break
        
        return jsonify({
            'success': True,
            'is_salary_eligible': is_salary_eligible,
            'qualified_referrals': qualified_referrals,
            'current_balance': current_balance,
            'current_salary_plan': current_salary_plan,
            'real_time_check': True,  # Indicates this is real-time balance checking
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/set_avatar/<avatar_name>')
@login_required
def set_avatar(avatar_name):
    # List of allowed default avatars
    allowed_avatars = [
        'default_animal_1.svg',
        'default_animal_2.svg', 
        'default_animal_3.svg',
        'default_tree_1.svg',
        'default_tree_2.svg',
        'default_car_1.svg',
        'default_car_2.svg'
    ]
    
    if avatar_name in allowed_avatars:
        current_user.profile_picture = avatar_name
        db.session.commit()
        log_activity(current_user.id, 'avatar_change', f'Changed avatar to {avatar_name}')
        flash('Avatar updated successfully!', 'success')
    else:
        flash('Invalid avatar selection', 'error')
    
    return redirect(url_for('profile'))

@app.route('/generate_referral_qr')
@login_required
def generate_referral_qr():
    referral_link = url_for('register', referral_code=current_user.referral_code, _external=True)
    qr_code = generate_qr_code(referral_link)
    return qr_code

# API endpoints for profile history
@app.route('/api/history/<history_type>')
@login_required
def get_history(history_type):
    """Get user's transaction history"""
    try:
        if history_type == 'deposits':
            deposits = Deposit.query.filter_by(user_id=current_user.id).order_by(Deposit.created_at.desc()).all()
            data = []
            for deposit in deposits:
                data.append({
                    'amount': deposit.amount,
                    'transaction_id': deposit.transaction_id,
                    'status': deposit.status,
                    'date': deposit.created_at.strftime('%Y-%m-%d %H:%M'),
                    'blockchain_verified': deposit.blockchain_verified
                })
            return jsonify(data)
        
        elif history_type == 'withdrawals':
            withdrawals = Withdrawal.query.filter_by(user_id=current_user.id).order_by(Withdrawal.created_at.desc()).all()
            data = []
            for withdrawal in withdrawals:
                data.append({
                    'amount': withdrawal.amount,
                    'wallet_address': withdrawal.wallet_address,
                    'network': withdrawal.network,
                    'status': withdrawal.status,
                    'date': withdrawal.created_at.strftime('%Y-%m-%d %H:%M'),
                    'fee_amount': withdrawal.fee_amount if hasattr(withdrawal, 'fee_amount') else 0
                })
            return jsonify(data)
        
        elif history_type == 'stakes':
            stakes = Stake.query.filter_by(user_id=current_user.id).order_by(Stake.created_at.desc()).all()
            data = []
            for stake in stakes:
                data.append({
                    'coin': stake.coin.symbol,
                    'amount': stake.amount,
                    'duration': stake.plan.duration_days,
                    'rate': stake.plan.interest_rate,
                    'status': stake.status,
                    'date': stake.created_at.strftime('%Y-%m-%d %H:%M'),
                    'current_return': stake.calculate_current_return(),
                    'is_mature': stake.is_mature
                })
            return jsonify(data)
        
        else:
            return jsonify({'error': 'Invalid history type'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Admin access with proper authentication
@app.route('/adminaccess', methods=['GET', 'POST'])
def admin_access():
    """Secure admin login with password verification"""
    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        admin_user = User.query.filter_by(email=form.email.data).first()
        if admin_user and admin_user.check_password(form.password.data) and admin_user.is_admin and admin_user.is_active:
            login_user(admin_user, remember=True)
            log_activity(admin_user.id, 'admin_login', 'Admin logged in via admin access')
            flash('Admin login successful', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials or access denied', 'error')
    
    return render_template('auth/admin_login.html', form=form)

# Admin routes - Secure access only
@app.route('/admin')
@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    stats = {
        'total_users': User.query.count(),
        'total_stakes': Stake.query.count(),
        'total_staked_amount': db.session.query(db.func.sum(Stake.amount)).scalar() or 0,
        'pending_deposits': Deposit.query.filter_by(status='pending').count(),
        'pending_withdrawals': Withdrawal.query.filter_by(status='pending').count(),
    }
    
    return render_template('admin/dashboard.html', stats=stats)

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/stakes')
@login_required
@admin_required
def admin_stakes():
    stakes = Stake.query.order_by(Stake.created_at.desc()).all()
    return render_template('admin/stakes.html', stakes=stakes)

@app.route('/admin/transactions')
@login_required
@admin_required
def admin_transactions():
    deposits = Deposit.query.order_by(Deposit.created_at.desc()).all()
    withdrawals = Withdrawal.query.order_by(Withdrawal.created_at.desc()).all()
    return render_template('admin/transactions.html', deposits=deposits, withdrawals=withdrawals)

@app.route('/admin/approve_deposit/<int:deposit_id>')
@login_required
@admin_required
def admin_approve_deposit(deposit_id):
    deposit = Deposit.query.get_or_404(deposit_id)
    
    if deposit.status == 'pending':
        deposit.status = 'approved'
        deposit.processed_at = datetime.utcnow()
        
        # Add balance to user
        user = User.query.get(deposit.user_id)
        user.usdt_balance += deposit.amount
        
        # Automatic referral commission processing on deposit approval
        from referral_commission_system import process_deposit_commission
        try:
            commission_result = process_deposit_commission(user.id, deposit.amount)
            if commission_result['success']:
                flash(f'✅ Deposit approved! Automatic referral commission: ${commission_result["commission_amount"]} USDT awarded to {commission_result["referrer"]}', 'success')
                log_activity(None, 'admin_auto_commission', 
                           f'Auto-approved deposit #{deposit.id} and awarded ${commission_result["commission_amount"]} USDT commission')
            else:
                flash('✅ Deposit approved successfully!', 'success')
        except Exception as e:
            print(f"Error processing automatic referral commission: {e}")
            log_activity(None, 'admin_auto_commission_error', f'Error processing auto-commission: {str(e)}')
            flash('✅ Deposit approved successfully!', 'success')
        
        db.session.commit()
        
        log_activity(None, 'admin_approve_deposit', f'Approved deposit #{deposit.id} for user {user.username}')
    
    return redirect(url_for('admin_transactions'))

@app.route('/admin/reject_deposit/<int:deposit_id>')
@login_required
@admin_required
def admin_reject_deposit(deposit_id):
    deposit = Deposit.query.get_or_404(deposit_id)
    
    if deposit.status == 'pending':
        deposit.status = 'rejected'
        deposit.processed_at = datetime.utcnow()
        db.session.commit()
        
        log_activity(None, 'admin_reject_deposit', f'Rejected deposit #{deposit.id}')
        flash('Deposit rejected', 'success')
    
    return redirect(url_for('admin_transactions'))

@app.route('/admin/approve_withdrawal/<int:withdrawal_id>')
@login_required
@admin_required
def admin_approve_withdrawal(withdrawal_id):
    withdrawal = Withdrawal.query.get_or_404(withdrawal_id)
    
    if withdrawal.status == 'pending':
        withdrawal.status = 'approved'
        withdrawal.processed_at = datetime.utcnow()
        
        # Check and update referral status after withdrawal (balance already deducted)
        from referral_utils import check_and_update_referral_balance
        check_and_update_referral_balance(withdrawal.user)
        
        db.session.commit()
        
        log_activity(None, 'admin_approve_withdrawal', f'Approved withdrawal #{withdrawal.id} for user {withdrawal.user.username}')
        flash('Withdrawal approved successfully', 'success')
    
    return redirect(url_for('admin_transactions'))

@app.route('/admin/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_settings():
    form = AdminSettingsForm()
    
    if form.validate_on_submit():
        PlatformSettings.set_setting('platform_name', form.platform_name.data)
        PlatformSettings.set_setting('referral_level_1', str(form.referral_level_1.data))
        PlatformSettings.set_setting('referral_level_2', str(form.referral_level_2.data))
        PlatformSettings.set_setting('referral_level_3', str(form.referral_level_3.data))
        PlatformSettings.set_setting('min_referral_activation', str(form.min_referral_activation.data))
        PlatformSettings.set_setting('withdrawal_fee', str(form.withdrawal_fee.data))
        
        flash('Settings updated successfully', 'success')
        return redirect(url_for('admin_settings'))
    
    # Load current settings
    settings = PlatformSettings.get_all_settings()
    # Only set fields that exist in the form
    if hasattr(form, 'platform_name'):
        form.platform_name.data = settings.get('platform_name', 'USDT Staking Platform')
    form.referral_level_1.data = float(settings.get('referral_level_1', 5))
    form.referral_level_2.data = float(settings.get('referral_level_2', 3))
    form.referral_level_3.data = float(settings.get('referral_level_3', 2))
    form.min_referral_activation.data = float(settings.get('min_referral_activation', 100))
    form.withdrawal_fee.data = float(settings.get('withdrawal_fee', 0))
    
    return render_template('admin/settings.html', form=form, current_settings=settings)

@app.route('/admin/password', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_change_password():
    form = AdminPasswordChangeForm()
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            log_activity(current_user.id, 'admin_password_change', 'Admin password changed')
            flash('Password changed successfully', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Current password is incorrect', 'error')
    
    return render_template('admin/password_change.html', form=form)

@app.route('/admin/coins')
@login_required
@admin_required
def admin_coins():
    coins = Coin.query.all()
    return render_template('admin/coins.html', coins=coins)

@app.route('/admin/coins/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_coin():
    form = AdminCoinForm()
    if form.validate_on_submit():
        # Handle file upload
        logo_url = form.logo_url.data
        if form.logo_file.data:
            from werkzeug.utils import secure_filename
            import uuid
            filename = secure_filename(form.logo_file.data.filename)
            # Add unique identifier to filename
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            form.logo_file.data.save(file_path)
            logo_url = f"/static/uploads/{unique_filename}"
        
        coin = Coin(
            symbol=form.symbol.data,
            name=form.name.data,
            min_stake=form.min_stake.data,
            logo_url=logo_url,
            icon_emoji=form.icon_emoji.data,
            daily_return_rate=form.daily_return_rate.data,
            active=form.active.data
        )
        db.session.add(coin)
        db.session.commit()
        log_activity(current_user.id, 'admin_add_coin', f'Added coin {form.symbol.data}')
        flash('Coin added successfully', 'success')
        return redirect(url_for('admin_coins'))
    return render_template('admin/coin_form.html', form=form, title='Add Coin')

@app.route('/admin/coins/edit/<int:coin_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_coin(coin_id):
    coin = Coin.query.get_or_404(coin_id)
    form = AdminCoinForm(obj=coin)
    if form.validate_on_submit():
        # Handle file upload
        logo_url = form.logo_url.data or coin.logo_url
        if form.logo_file.data:
            from werkzeug.utils import secure_filename
            import uuid
            filename = secure_filename(form.logo_file.data.filename)
            # Add unique identifier to filename
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            form.logo_file.data.save(file_path)
            logo_url = f"/static/uploads/{unique_filename}"
        
        coin.symbol = form.symbol.data
        coin.name = form.name.data
        coin.min_stake = form.min_stake.data
        coin.logo_url = logo_url
        coin.icon_emoji = form.icon_emoji.data
        coin.daily_return_rate = form.daily_return_rate.data
        coin.active = form.active.data
        db.session.commit()
        log_activity(current_user.id, 'admin_edit_coin', f'Edited coin {coin.symbol}')
        flash('Coin updated successfully', 'success')
        return redirect(url_for('admin_coins'))
    return render_template('admin/coin_form.html', form=form, title='Edit Coin', coin=coin)

@app.route('/admin/plans')
@login_required
@admin_required
def admin_plans():
    """Display individual coin staking plans with return rates"""
    coins = Coin.query.filter_by(active=True).all()
    
    # Get coin return rates organized by coin and duration
    plans_by_coin = {}
    coin_return_rates = CoinReturnRate.query.filter_by(is_active=True).all()
    
    for rate in coin_return_rates:
        if rate.coin_id not in plans_by_coin:
            plans_by_coin[rate.coin_id] = {}
        
        # Map duration to daily return rate using actual model fields
        plans_by_coin[rate.coin_id][rate.duration_days] = rate.daily_return_rate
    
    return render_template('admin/plans.html', coins=coins, plans_by_coin=plans_by_coin)

@app.route('/admin/plans/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_plan():
    form = AdminStakingPlanForm()
    if form.validate_on_submit():
        plan = StakingPlan(
            duration_days=form.duration_days.data,
            interest_rate=form.interest_rate.data,
            active=form.active.data
        )
        db.session.add(plan)
        db.session.commit()
        log_activity(current_user.id, 'admin_add_plan', f'Added staking plan {form.duration_days.data} days')
        flash('Staking plan added successfully', 'success')
        return redirect(url_for('admin_plans'))
    return render_template('admin/plan_form.html', form=form, title='Add Staking Plan')

@app.route('/admin/plans/edit/<int:plan_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_plan(plan_id):
    plan = StakingPlan.query.get_or_404(plan_id)
    form = AdminStakingPlanForm(obj=plan)
    if form.validate_on_submit():
        plan.duration_days = form.duration_days.data
        plan.interest_rate = form.interest_rate.data
        plan.active = form.active.data
        db.session.commit()
        log_activity(current_user.id, 'admin_edit_plan', f'Edited staking plan {plan.duration_days} days')
        flash('Staking plan updated successfully', 'success')
        return redirect(url_for('admin_plans'))
    return render_template('admin/plan_form.html', form=form, title='Edit Staking Plan', plan=plan)

@app.route('/admin/activity')
@login_required
@admin_required
def admin_activity():
    page = request.args.get('page', 1, type=int)
    activities = ActivityLog.query.order_by(ActivityLog.created_at.desc()).paginate(
        page=page, per_page=50, error_out=False
    )
    return render_template('admin/activity.html', activities=activities)

@app.route('/admin/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = AdminUserForm(obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.usdt_balance = form.usdt_balance.data
        user.is_admin = form.is_admin.data
        user.is_active = form.is_active.data
        db.session.commit()
        log_activity(current_user.id, 'admin_edit_user', f'Edited user {user.username}')
        flash('User updated successfully', 'success')
        return redirect(url_for('admin_users'))
    return render_template('admin/user_form.html', form=form, title='Edit User', user=user)

# Admin Payment Address Management
@app.route('/admin/payment-addresses')
@login_required
@admin_required
def admin_payment_addresses():
    """Admin payment address management"""
    addresses = PaymentAddress.query.all()
    
    # Ensure QR codes are generated for addresses that don't have them
    for address in addresses:
        if not address.qr_code_path:
            try:
                import qrcode
                import base64
                from io import BytesIO
                
                # Create QR code
                qr = qrcode.QRCode(version=1, box_size=6, border=2)
                qr.add_data(address.address)
                qr.make(fit=True)
                
                # Generate image
                img = qr.make_image(fill_color='black', back_color='white')
                buffer = BytesIO()
                img.save(buffer, format='PNG')
                address.qr_code_path = base64.b64encode(buffer.getvalue()).decode()
                db.session.commit()
            except Exception as e:
                print(f"Error generating QR code for {address.address}: {e}")
    
    return render_template('admin/payment_addresses.html', addresses=addresses)

@app.route('/admin/payment-addresses/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_payment_address():
    form = AdminPaymentAddressForm()
    if form.validate_on_submit():
        # Generate QR code for the address
        import qrcode
        import base64
        from io import BytesIO
        
        # Create QR code
        qr = qrcode.QRCode(version=1, box_size=6, border=2)
        qr.add_data(form.address.data)
        qr.make(fit=True)
        
        # Generate image
        img = qr.make_image(fill_color='black', back_color='white')
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        qr_code_data = base64.b64encode(buffer.getvalue()).decode()
        
        address = PaymentAddress(
            network=form.network.data,
            address=form.address.data,
            min_deposit=form.min_deposit.data,
            is_active=form.is_active.data,
            qr_code_path=qr_code_data  # Store QR code as base64 data
        )
        db.session.add(address)
        db.session.commit()
        log_activity(current_user.id, 'admin_add_address', f'Added {form.network.data} payment address: {form.address.data}')
        flash('Payment address added successfully with QR code generated', 'success')
        return redirect(url_for('admin_payment_addresses'))
    return render_template('admin/payment_address_form.html', form=form, title='Add Payment Address')

@app.route('/admin/payment-addresses/edit/<int:address_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_payment_address(address_id):
    address = PaymentAddress.query.get_or_404(address_id)
    form = AdminPaymentAddressForm(obj=address)
    if form.validate_on_submit():
        # Check if address changed, regenerate QR code if needed
        if address.address != form.address.data:
            import qrcode
            import base64
            from io import BytesIO
            
            # Create QR code
            qr = qrcode.QRCode(version=1, box_size=6, border=2)
            qr.add_data(form.address.data)
            qr.make(fit=True)
            
            # Generate image
            img = qr.make_image(fill_color='black', back_color='white')
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            address.qr_code_path = base64.b64encode(buffer.getvalue()).decode()
            
        address.network = form.network.data
        address.address = form.address.data
        address.min_deposit = form.min_deposit.data
        address.is_active = form.is_active.data
        db.session.commit()
        log_activity(current_user.id, 'admin_edit_address', f'Edited {form.network.data} payment address: {form.address.data}')
        flash('Payment address updated successfully', 'success')
        return redirect(url_for('admin_payment_addresses'))
    return render_template('admin/payment_address_form.html', form=form, title='Edit Payment Address', address=address)

@app.route('/admin/payment-addresses/delete/<int:address_id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_payment_address(address_id):
    address = PaymentAddress.query.get_or_404(address_id)
    network = address.network
    address_value = address.address
    db.session.delete(address)
    db.session.commit()
    log_activity(current_user.id, 'admin_delete_address', f'Deleted {network} payment address: {address_value}')
    flash('Payment address deleted successfully', 'success')
    return redirect(url_for('admin_payment_addresses'))



@app.route('/admin/users/ban/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def admin_ban_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        flash('Cannot ban admin users', 'error')
        return redirect(url_for('admin_users'))
    
    user.is_active = False
    db.session.commit()
    log_activity(current_user.id, 'admin_ban_user', f'Banned user {user.username}')
    flash(f'User {user.username} has been banned successfully', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/users/unban/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def admin_unban_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = True
    db.session.commit()
    log_activity(current_user.id, 'admin_unban_user', f'Unbanned user {user.username}')
    flash(f'User {user.username} has been unbanned successfully', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/users/limit/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def admin_set_limit(user_id):
    user = User.query.get_or_404(user_id)
    # For now, we'll redirect to edit user page where limits can be set
    return redirect(url_for('admin_edit_user', user_id=user_id))


@app.route('/admin/content')
@login_required
@admin_required
def admin_content():
    contents = ContentSection.query.order_by(ContentSection.page_name, ContentSection.section_name).all()
    return render_template('admin/content.html', contents=contents)


@app.route('/admin/content/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_content():
    form = AdminContentForm()
    if form.validate_on_submit():
        ContentSection.set_content(
            form.page_name.data,
            form.section_name.data,
            form.content.data,
            form.content_type.data
        )
        
        log_activity(current_user.id, 'add_content', f'Added content section: {form.page_name.data}/{form.section_name.data}', request.remote_addr)
        flash('Content added successfully!', 'success')
        return redirect(url_for('admin_content'))
    
    return render_template('admin/content_form.html', form=form, title='Add Content')


@app.route('/admin/content/<int:content_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_content(content_id):
    content = ContentSection.query.get_or_404(content_id)
    form = AdminContentForm(obj=content)
    
    if form.validate_on_submit():
        content.page_name = form.page_name.data
        content.section_name = form.section_name.data
        content.content = form.content.data
        content.content_type = form.content_type.data
        content.is_active = form.is_active.data
        content.updated_at = datetime.utcnow()
        db.session.commit()
        
        log_activity(current_user.id, 'edit_content', f'Edited content section: {content.page_name}/{content.section_name}', request.remote_addr)
        flash('Content updated successfully!', 'success')
        return redirect(url_for('admin_content'))
    
    return render_template('admin/content_form.html', form=form, content=content, title='Edit Content')


@app.route('/admin/content/<int:content_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_content(content_id):
    content = ContentSection.query.get_or_404(content_id)
    page_section = f'{content.page_name}/{content.section_name}'
    
    db.session.delete(content)
    db.session.commit()
    
    log_activity(current_user.id, 'delete_content', f'Deleted content section: {page_section}', request.remote_addr)
    flash('Content deleted successfully!', 'success')
    return redirect(url_for('admin_content'))


@app.route('/admin/payment-address/<int:address_id>/toggle', methods=['POST'])
@login_required
@admin_required
def admin_toggle_payment_address(address_id):
    address = PaymentAddress.query.get_or_404(address_id)
    data = request.get_json()
    
    if data and 'is_active' in data:
        address.is_active = data['is_active']
        address.updated_at = datetime.utcnow()
        db.session.commit()
        
        status = 'activated' if data['is_active'] else 'deactivated'
        log_activity(current_user.id, 'toggle_payment_address', f'{status.capitalize()} payment address: {address.network}', request.remote_addr)
        
        return jsonify({'success': True, 'message': f'Payment address {status} successfully'})
    
    return jsonify({'success': False, 'message': 'Invalid request'})

@app.route('/admin/blockchain-settings', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_blockchain_settings():
    try:
        from forms import AdminBlockchainSettingsForm
        
        form = AdminBlockchainSettingsForm()
        
        # Pre-populate form with current settings
        if request.method == 'GET':
            try:
                # Try to read current settings from blockchain_utils.py
                with open('blockchain_utils.py', 'r') as f:
                    content = f.read()
                    
                # Extract current API key with regex
                import re
                api_key_match = re.search(r'self\.moralis_api_key = ["\']([^"\']*)["\']', content)
                api_url_match = re.search(r'self\.moralis_api_url = os\.environ\.get\([\'"]MORALIS_API_URL[\'"], ["\']([^"\']*)["\']', content)
                
                if api_key_match:
                    form.moralis_api_key.data = api_key_match.group(1)
                else:
                    form.moralis_api_key.data = os.environ.get('MORALIS_API_KEY', '')
                    
                if api_url_match:
                    form.moralis_api_url.data = api_url_match.group(1)
                else:
                    form.moralis_api_url.data = os.environ.get('MORALIS_API_URL', 'https://deep-index.moralis.io/api/v2.2')
                    
                form.bscscan_api_key.data = os.environ.get('BSCSCAN_API_KEY', '')
            except Exception as e:
                print(f"Error reading blockchain_utils.py: {e}")
                # Fallback to environment variables
                form.moralis_api_key.data = os.environ.get('MORALIS_API_KEY', '')
                form.moralis_api_url.data = os.environ.get('MORALIS_API_URL', 'https://deep-index.moralis.io/api/v2.2')
                form.bscscan_api_key.data = os.environ.get('BSCSCAN_API_KEY', '')
        
        if form.validate_on_submit():
            try:
                # Validate API key format (basic validation)
                api_key = form.moralis_api_key.data.strip()
                if not api_key:
                    flash('Moralis API key cannot be empty', 'error')
                    return render_template('admin/blockchain_settings.html', form=form)
                
                # Update blockchain_utils.py with new settings
                blockchain_utils_path = 'blockchain_utils.py'
                
                # Read current file
                with open(blockchain_utils_path, 'r') as f:
                    content = f.read()
                
                # Update API key in the content with proper escaping
                import re
                
                # Escape special regex characters in the new API key
                escaped_api_key = re.escape(api_key)
                escaped_api_url = re.escape(form.moralis_api_url.data)
                
                # Replace moralis_api_key (handle both single and double quotes)
                content = re.sub(
                    r'self\.moralis_api_key = ["\'][^"\']*["\']',
                    f'self.moralis_api_key = "{api_key}"',
                    content
                )
                
                # Replace moralis_api_url
                content = re.sub(
                    r'self\.moralis_api_url = os\.environ\.get\([\'"]MORALIS_API_URL[\'"], ["\'][^"\']*["\']',
                    f'self.moralis_api_url = os.environ.get(\'MORALIS_API_URL\', "{form.moralis_api_url.data}")',
                    content
                )
                
                # Write back to file
                with open(blockchain_utils_path, 'w') as f:
                    f.write(content)
                
                # Update environment variables for current session
                os.environ['MORALIS_API_KEY'] = api_key
                os.environ['MORALIS_API_URL'] = form.moralis_api_url.data
                if form.bscscan_api_key.data:
                    os.environ['BSCSCAN_API_KEY'] = form.bscscan_api_key.data
                
                log_activity(current_user.id, 'admin_update_blockchain_settings', 'Updated blockchain API settings')
                flash('Blockchain settings updated successfully', 'success')
                
            except Exception as e:
                print(f"Error updating blockchain settings: {str(e)}")
                flash(f'Error updating blockchain settings: {str(e)}', 'error')
            
            return redirect(url_for('admin_blockchain_settings'))
        
        return render_template('admin/blockchain_settings.html', form=form)
        
    except Exception as e:
        print(f"General error in admin_blockchain_settings: {str(e)}")
        flash(f'Error loading blockchain settings page: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/test-blockchain-connection', methods=['POST'])
@login_required
@admin_required
def admin_test_blockchain_connection():
    """Test blockchain API connection"""
    try:
        data = request.get_json()
        api_key = data.get('api_key')
        api_url = data.get('api_url')
        
        if not api_key:
            return jsonify({'success': False, 'message': 'API key is required'})
        
        # Test Moralis API connection
        import requests
        headers = {
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        }
        
        # Simple test endpoint
        test_url = f"{api_url.rstrip('/')}/block/latest"
        response = requests.get(test_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return jsonify({'success': True, 'message': 'Connection successful'})
        else:
            return jsonify({'success': False, 'message': f'API returned status {response.status_code}'})
    
    except requests.exceptions.Timeout:
        return jsonify({'success': False, 'message': 'Connection timeout'})
    except requests.exceptions.ConnectionError:
        return jsonify({'success': False, 'message': 'Unable to connect to API'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})


@app.route('/nfts')
@login_required
def nfts():
    # Always show NFT marketplace with all features
    try:
        db_nfts = NFT.query.filter_by(is_active=True).order_by(NFT.display_order, NFT.created_at).all()
        featured_nfts = []
        if db_nfts:
            for nft in db_nfts:
                featured_nfts.append({
                    'id': nft.unique_id,
                    'name': nft.name,
                    'icon': nft.icon,
                    'gradient': nft.gradient,
                    'rarity': nft.rarity,
                    'owner': nft.owner_name,
                    'price': nft.price,
                    'last_sale': nft.last_sale_price or (nft.price * 0.9),
                    'collection': nft.collection.name,
                    'verified': nft.is_verified,
                    'image': nft.image_url
                })
        return render_template('nfts.html', featured_nfts=featured_nfts)
    except Exception as e:
        # Return with empty featured_nfts if database error
        return render_template('nfts.html', featured_nfts=[])
    
    # Fallback hardcoded data
    featured_nfts = []
    
    nft_data = [
        {"name": "Mosu #1930", "icon": "🎭", "gradient": "from-purple-600 to-pink-600", "rarity": 5, "owner": "CryptoPunks"},
        {"name": "Alien #2847", "icon": "👽", "gradient": "from-green-500 to-blue-500", "rarity": 5, "owner": "CryptoPunks"},
        {"name": "Punk #5672", "icon": "🎨", "gradient": "from-red-500 to-orange-500", "rarity": 4, "owner": "CryptoPunks"},
        {"name": "Zombie #3421", "icon": "🧟", "gradient": "from-gray-600 to-green-600", "rarity": 4, "owner": "CryptoPunks"},
        {"name": "Ape #8901", "icon": "🦍", "gradient": "from-brown-500 to-yellow-500", "rarity": 3, "owner": "CryptoPunks"},
        {"name": "Robot #1234", "icon": "🤖", "gradient": "from-silver-400 to-gray-600", "rarity": 4, "owner": "CryptoPunks"},
        {"name": "Demon #6789", "icon": "👹", "gradient": "from-red-600 to-black", "rarity": 5, "owner": "CryptoPunks"},
        {"name": "Angel #4567", "icon": "👼", "gradient": "from-white to-gold", "rarity": 4, "owner": "CryptoPunks"},
        {"name": "Cyborg #9876", "icon": "🔧", "gradient": "from-blue-500 to-gray-500", "rarity": 4, "owner": "CryptoPunks"},
        {"name": "Witch #2345", "icon": "🧙‍♀️", "gradient": "from-purple-800 to-black", "rarity": 4, "owner": "CryptoPunks"},
        {"name": "Pirate #7890", "icon": "🏴‍☠️", "gradient": "from-black to-red-800", "rarity": 3, "owner": "CryptoPunks"},
        {"name": "Ninja #5432", "icon": "🥷", "gradient": "from-black to-gray-800", "rarity": 4, "owner": "CryptoPunks"},
        {"name": "Samurai #8765", "icon": "⚔️", "gradient": "from-red-600 to-yellow-600", "rarity": 4, "owner": "CryptoPunks"},
        {"name": "Viking #3456", "icon": "🪓", "gradient": "from-brown-600 to-orange-600", "rarity": 3, "owner": "CryptoPunks"},
        {"name": "Pharaoh #6543", "icon": "👑", "gradient": "from-gold to-yellow-600", "rarity": 5, "owner": "CryptoPunks"},
        {"name": "Vampire #9012", "icon": "🦇", "gradient": "from-red-900 to-black", "rarity": 4, "owner": "CryptoPunks"},
        {"name": "Werewolf #2109", "icon": "🐺", "gradient": "from-brown-700 to-gray-700", "rarity": 4, "owner": "CryptoPunks"},
        {"name": "Ghost #4321", "icon": "👻", "gradient": "from-gray-300 to-white", "rarity": 3, "owner": "CryptoPunks"},
        {"name": "Skeleton #7654", "icon": "💀", "gradient": "from-gray-400 to-black", "rarity": 3, "owner": "CryptoPunks"},
        {"name": "Mummy #0987", "icon": "🏺", "gradient": "from-yellow-700 to-brown-700", "rarity": 3, "owner": "CryptoPunks"},
        {"name": "Genie #1357", "icon": "🧞‍♂️", "gradient": "from-blue-600 to-purple-600", "rarity": 4, "owner": "CryptoPunks"},
        {"name": "Dragon #2468", "icon": "🐉", "gradient": "from-green-600 to-red-600", "rarity": 5, "owner": "CryptoPunks"},
        {"name": "Phoenix #3579", "icon": "🔥", "gradient": "from-orange-500 to-red-500", "rarity": 5, "owner": "CryptoPunks"},
        {"name": "Unicorn #4680", "icon": "🦄", "gradient": "from-pink-400 to-purple-400", "rarity": 4, "owner": "CryptoPunks"},
        {"name": "Pegasus #5791", "icon": "🐴", "gradient": "from-white to-sky-400", "rarity": 4, "owner": "CryptoPunks"},
        {"name": "Griffin #6802", "icon": "🦅", "gradient": "from-brown-600 to-yellow-600", "rarity": 4, "owner": "CryptoPunks"},
        {"name": "Kraken #7913", "icon": "🐙", "gradient": "from-blue-800 to-black", "rarity": 5, "owner": "CryptoPunks"},
        {"name": "Titan #8024", "icon": "⚡", "gradient": "from-yellow-500 to-orange-500", "rarity": 5, "owner": "CryptoPunks"}
    ]
    
    collections = ["Legendary Heroes", "Cyber Punk", "Fantasy Realm", "Space Odyssey", "Elemental Force"]
    
    for i, nft_info in enumerate(nft_data):
        nft = {
            'id': f"{1000 + i}",
            'name': nft_info['name'],
            'icon': nft_info['icon'],
            'gradient': nft_info['gradient'],
            'rarity': 5 if i % 3 == 0 else (2 + (i % 3)),  # Blue tick = 5 stars, others 2-4
            'owner': nft_info['owner'],
            'price': round(50 + (i * 25) + (i % 7 * 100), 2),
            'last_sale': round(45 + (i * 20) + (i % 5 * 80), 2),
            'collection': collections[i % len(collections)],
            'verified': i % 3 == 0,
            'image': f'https://picsum.photos/300/300?random={i+300}'  # Square NFT images
        }
        featured_nfts.append(nft)
    
    return render_template('nfts.html', featured_nfts=featured_nfts)

@app.route('/api/user/notifications')
@login_required
def api_user_notifications():
    """Get user notifications for dropdown"""
    try:
        from models import Notification
        notifications = []
        unread_count = 0
        
        # Try to get actual notifications from database if Notification model exists
        try:
            user_notifications = Notification.query.filter_by(
                user_id=current_user.id
            ).order_by(Notification.created_at.desc()).limit(10).all()
            
            for notification in user_notifications:
                notifications.append({
                    'id': notification.id,
                    'title': notification.title,
                    'message': notification.message,
                    'type': notification.notification_type,
                    'is_read': notification.is_read,
                    'created_at': notification.created_at.isoformat()
                })
                
                if not notification.is_read:
                    unread_count += 1
                    
        except Exception as e:
            # If no notification system exists, create sample notifications for demo
            print(f"No notification system found: {e}")
            notifications = [
                {
                    'id': 1,
                    'title': 'Welcome!',
                    'message': 'Welcome to the platform! Start by making your first deposit.',
                    'type': 'info',
                    'is_read': False,
                    'created_at': datetime.now().isoformat()
                },
                {
                    'id': 2,
                    'title': 'System Update',
                    'message': 'Platform maintenance scheduled for tonight.',
                    'type': 'warning',
                    'is_read': False,
                    'created_at': datetime.now().isoformat()
                }
            ]
            unread_count = 2
        
        return jsonify({
            'success': True,
            'notifications': notifications,
            'unread_count': unread_count
        })
        
    except Exception as e:
        print(f"Error in api_user_notifications: {e}")
        return jsonify({
            'success': False,
            'message': 'Error loading notifications',
            'notifications': [],
            'unread_count': 0
        })

@app.route('/api/user/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """Mark a notification as read"""
    try:
        from models import Notification
        notification = Notification.query.filter_by(
            id=notification_id,
            user_id=current_user.id
        ).first()
        
        if notification:
            notification.is_read = True
            db.session.commit()
            return jsonify({'success': True, 'message': 'Notification marked as read'})
        else:
            return jsonify({'success': False, 'message': 'Notification not found'})
            
    except Exception as e:
        print(f"Error marking notification as read: {e}")
        return jsonify({'success': True, 'message': 'Marked as read'})  # Silent success for demo

@app.route('/support')
@login_required
def support():
    """Simple popup-based support chat interface"""
    return render_template('support.html')

@app.route('/support-premium')
@login_required
def support_premium():
    """Premium AI-powered support with step-by-step guidance"""
    return render_template('support_premium.html')

@app.route('/submit_support_ticket', methods=['POST'])
@login_required
def submit_support_ticket():
    """Submit a new support ticket"""
    try:
        ticket = SupportMessage(
            user_id=current_user.id,
            problem_type=request.form.get('problem_type', 'general'),
            subject=request.form.get('subject'),
            message=request.form.get('message'),
            priority=request.form.get('priority', 'normal'),
            status='open'
        )
        
        db.session.add(ticket)
        db.session.commit()
        
        log_activity(current_user.id, 'support_ticket', f'Created support ticket: {ticket.subject}')
        flash('Support ticket submitted successfully! We will respond soon.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error submitting ticket: {str(e)}', 'error')
    
    return redirect(url_for('support'))

@app.route('/api/ai-support', methods=['POST'])
@login_required
def ai_support():
    """AI support API endpoint"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        # Get user information for AI response
        user = current_user
        
        # Get salary information
        if any(word in message.lower() for word in ['salary', 'plan', 'monthly', 'payment']):
            referral_count = len([r for r in user.referrals if r.usdt_balance + sum(s.amount for s in r.stakes if s.status == 'active') >= 100])
            total_balance = user.usdt_balance + sum(s.amount for s in user.stakes if s.status == 'active')
            
            salary_plans = [
                {'plan': 'Plan 1', 'referrals_needed': 7, 'balance_needed': 350, 'monthly_salary': 50},
                {'plan': 'Plan 2', 'referrals_needed': 13, 'balance_needed': 680, 'monthly_salary': 110},
                {'plan': 'Plan 3', 'referrals_needed': 27, 'balance_needed': 960, 'monthly_salary': 230},
                {'plan': 'Plan 4', 'referrals_needed': 46, 'balance_needed': 1340, 'monthly_salary': 480}
            ]
            
            eligible_plans = []
            for plan in salary_plans:
                if referral_count >= plan['referrals_needed'] and total_balance >= plan['balance_needed']:
                    eligible_plans.append(plan)
            
            response = f"""
            <div class="ai-response">
                <h4>💰 Your Salary Eligibility Status</h4>
                <p><strong>Current Referrals:</strong> {referral_count}</p>
                <p><strong>Current Balance:</strong> ${total_balance:.2f} USDT</p>
                
                <h5>📋 Salary Plans Available:</h5>
                <ul>
            """
            
            for plan in salary_plans:
                eligible = plan in eligible_plans
                status = "✅ ELIGIBLE" if eligible else "❌ Not Eligible"
                response += f"""
                    <li>
                        <strong>{plan['plan']}</strong> - ${plan['monthly_salary']}/month {status}<br>
                        Requires: {plan['referrals_needed']} referrals + ${plan['balance_needed']} balance
                    </li>
                """
            
            response += """
                </ul>
                <p><em>Salary is paid automatically on the 1st of each month for eligible users.</em></p>
            </div>
            """
            
        # Get referral information
        elif any(word in message.lower() for word in ['referral', 'commission', 'refer']):
            referrals = user.referrals
            active_referrals = [r for r in referrals if r.usdt_balance + sum(s.amount for s in r.stakes if s.status == 'active') >= 100]
            total_commission = sum(r.usdt_balance * 0.05 for r in active_referrals)
            
            response = f"""
            <div class="ai-response">
                <h4>👥 Your Referral Information</h4>
                <p><strong>Total Referrals:</strong> {len(referrals)}</p>
                <p><strong>Active Referrals:</strong> {len(active_referrals)} (with 100+ USDT balance)</p>
                <p><strong>Commission Rate:</strong> 5% per referral</p>
                <p><strong>Total Commission Earned:</strong> ${total_commission:.2f} USDT</p>
                
                <h5>📋 Referral Benefits:</h5>
                <ul>
                    <li>Earn 5% commission on each referral's balance</li>
                    <li>Commission awarded when referral reaches 100+ USDT</li>
                    <li>Commission remains permanent even if balance drops</li>
                    <li>2+ referrals = Premium benefits (no withdrawal fees)</li>
                </ul>
            </div>
            """
            
        # Get stake information
        elif any(word in message.lower() for word in ['stake', 'investment', 'unlock', 'earnings']):
            stakes = user.stakes
            response = f"""
            <div class="ai-response">
                <h4>📊 Your Staking Information</h4>
            """
            
            if stakes:
                response += "<h5>🎯 Active Stakes:</h5><ul>"
                for stake in stakes:
                    unlock_date = stake.created_at + timedelta(days=stake.plan.duration_days)
                    days_remaining = (unlock_date - datetime.utcnow()).days
                    
                    response += f"""
                        <li>
                            <strong>{stake.coin.symbol}</strong> - ${stake.amount:.2f}<br>
                            Duration: {stake.plan.duration_days} days | Daily: {stake.plan.interest_rate}%<br>
                            Current Earnings: ${stake.calculate_current_return():.2f}<br>
                            Unlock Date: {unlock_date.strftime('%Y-%m-%d')} ({max(0, days_remaining)} days remaining)<br>
                            Status: {stake.status}
                        </li>
                    """
                response += "</ul>"
            else:
                response += "<p>You don't have any active stakes currently.</p>"
            
            response += """
                <h5>📋 Staking Benefits:</h5>
                <ul>
                    <li>Daily returns from 0.5% to 2.0%</li>
                    <li>Multiple duration options (7-180 days)</li>
                    <li>Automatic profit calculation</li>
                    <li>Early unlock available after 50% duration</li>
                </ul>
            </div>
            """
            
        # Get balance information
        elif any(word in message.lower() for word in ['balance', 'wallet', 'money', 'funds']):
            total_staked = sum(s.amount for s in user.stakes if s.status == 'active')
            total_earnings = sum(s.calculate_current_return() for s in user.stakes if s.status == 'active')
            response = f"""
            <div class="ai-response">
                <h4>💳 Your Account Balance</h4>
                <p><strong>Available Balance:</strong> ${user.usdt_balance:.2f} USDT</p>
                <p><strong>Total Staked:</strong> ${total_staked:.2f} USDT</p>
                <p><strong>Current Earnings:</strong> ${total_earnings:.2f} USDT</p>
                <p><strong>Total Portfolio:</strong> ${user.usdt_balance + total_staked + total_earnings:.2f} USDT</p>
                
                <h5>📋 Account Summary:</h5>
                <ul>
                    <li>Referral Bonus: ${user.referral_bonus:.2f} USDT</li>
                    <li>Total Earned: ${user.total_earned:.2f} USDT</li>
                    <li>Active Stakes: {len([s for s in user.stakes if s.status == 'active'])}</li>
                    <li>Premium Member: {'Yes' if user.has_two_referrals() else 'No'}</li>
                </ul>
            </div>
            """
            
        # Default response
        else:
            response = """
            <div class="ai-response">
                <h4>🤖 AI Assistant</h4>
                <p>I can help you with information about:</p>
                <ul>
                    <li><strong>Salary</strong> - Check your eligibility and plans</li>
                    <li><strong>Referrals</strong> - View commission and benefits</li>
                    <li><strong>Stakes</strong> - Check your investments and earnings</li>
                    <li><strong>Balance</strong> - View your account details</li>
                </ul>
                <p>Try asking: "What's my salary status?" or "Show my stake details"</p>
            </div>
            """
        
        return jsonify({'response': response})
        
    except Exception as e:
        return jsonify({'response': f'<p>Error: {str(e)}</p>'}), 500


@app.route('/admin/support')
@login_required
@admin_required
def admin_support():
    """Admin support chat management - using SupportMessage as fallback"""
    try:
        # Try to use SupportChat if available, otherwise fallback to SupportMessage
        try:
            # Check if SupportChat model exists and has data
            from models import SupportChat
            SupportChat.cleanup_expired_chats()
            
            # Get all active user conversations
            users_with_messages = db.session.query(User).join(SupportChat).filter(
                SupportChat.expires_at > datetime.utcnow()
            ).distinct().all()
            
            # Get unread message counts per user
            user_conversations = []
            for user in users_with_messages:
                unread_count = SupportChat.query.filter_by(
                    user_id=user.id,
                    sender_type='user',
                    is_read=False
                ).filter(SupportChat.expires_at > datetime.utcnow()).count()
                
                last_message = SupportChat.query.filter_by(user_id=user.id).filter(
                    SupportChat.expires_at > datetime.utcnow()
                ).order_by(SupportChat.created_at.desc()).first()
                
                user_conversations.append({
                    'user': user,
                    'unread_count': unread_count,
                    'last_message': last_message
                })
            
            # Sort by unread messages first, then by latest activity
            user_conversations.sort(key=lambda x: (x['unread_count'], x['last_message'].created_at if x['last_message'] else datetime.min), reverse=True)
            
            stats = {
                'total_conversations': len(user_conversations),
                'unread_conversations': len([uc for uc in user_conversations if uc['unread_count'] > 0]),
                'total_messages': SupportChat.query.filter(SupportChat.expires_at > datetime.utcnow()).count()
            }
            
        except (ImportError, AttributeError, Exception):
            # Fallback to SupportMessage system
            support_messages = SupportMessage.query.order_by(SupportMessage.created_at.desc()).all()
            
            # Group by user
            users_with_messages = {}
            for msg in support_messages:
                if msg.user_id not in users_with_messages:
                    users_with_messages[msg.user_id] = {
                        'user': msg.user,
                        'messages': [],
                        'unread_count': 0,
                        'last_message': None
                    }
                
                users_with_messages[msg.user_id]['messages'].append(msg)
                if not msg.admin_reply:
                    users_with_messages[msg.user_id]['unread_count'] += 1
                
                if not users_with_messages[msg.user_id]['last_message'] or msg.created_at > users_with_messages[msg.user_id]['last_message'].created_at:
                    users_with_messages[msg.user_id]['last_message'] = msg
            
            user_conversations = list(users_with_messages.values())
            user_conversations.sort(key=lambda x: (x['unread_count'], x['last_message'].created_at if x['last_message'] else datetime.min), reverse=True)
            
            stats = {
                'total_conversations': len(user_conversations),
                'unread_conversations': len([uc for uc in user_conversations if uc['unread_count'] > 0]),
                'total_messages': len(support_messages)
            }
        
        return render_template('admin/support_chat_management.html', 
                             user_conversations=user_conversations, 
                             stats=stats)
                             
    except Exception as e:
        flash(f'Error loading support dashboard: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/support-tickets')
@login_required
@admin_required
def admin_support_tickets():
    """Admin support ticket management"""
    tickets = SupportMessage.query.order_by(SupportMessage.created_at.desc()).all()
    
    # Stats
    total_tickets = len(tickets)
    open_tickets = len([t for t in tickets if t.status == 'open'])
    urgent_tickets = len([t for t in tickets if t.priority == 'urgent'])
    replied_tickets = len([t for t in tickets if t.status == 'replied'])
    closed_tickets = len([t for t in tickets if t.status == 'closed'])
    
    stats = {
        'total': total_tickets,
        'open': open_tickets,
        'urgent': urgent_tickets,
        'replied': replied_tickets,
        'closed': closed_tickets
    }
    
    return render_template('admin/support_tickets.html', tickets=tickets, stats=stats)

@app.route('/admin/ticket/<int:ticket_id>/reply', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_ticket_reply(ticket_id):
    """Reply to support ticket"""
    ticket = SupportMessage.query.get_or_404(ticket_id)
    form = AdminSupportReplyForm(obj=ticket)
    
    if form.validate_on_submit():
        ticket.admin_reply = form.admin_reply.data
        ticket.status = form.status.data
        ticket.replied_at = datetime.utcnow()
        db.session.commit()
        
        log_activity(current_user.id, 'ticket_reply', f'Replied to ticket: {ticket.subject}')
        flash('Reply sent successfully!', 'success')
        return redirect(url_for('admin_support_tickets'))
    
    return render_template('admin/ticket_reply.html', ticket=ticket, form=form)

@app.route('/admin/ticket/<int:ticket_id>/close', methods=['POST'])
@login_required
@admin_required
def admin_close_ticket(ticket_id):
    """Close support ticket"""
    ticket = SupportMessage.query.get_or_404(ticket_id)
    ticket.status = 'closed'
    db.session.commit()
    
    log_activity(current_user.id, 'ticket_close', f'Closed ticket: {ticket.subject}')
    flash('Ticket closed successfully!', 'success')
    return redirect(url_for('admin_support_tickets'))

# Commented out - using admin_comprehensive.py instead
# @app.route('/admin/support-responses')
# @login_required
# @admin_required
def admin_support_responses_old():
    """Admin AI support responses management"""
    responses = SupportResponse.query.order_by(SupportResponse.priority.desc(), SupportResponse.created_at.desc()).all()
    return render_template('admin/support_responses.html', responses=responses)

# @app.route('/admin/support-responses/add', methods=['GET', 'POST'])
# @login_required
# @admin_required
def admin_add_support_response_old():
    """Add new AI support response"""
    form = AdminSupportResponseForm()
    
    if form.validate_on_submit():
        response = SupportResponse(
            trigger_words=form.trigger_words.data,
            category=form.category.data,
            response_text=form.response_text.data,
            priority=form.priority.data,
            is_active=form.is_active.data,
            created_by=current_user.id
        )
        
        db.session.add(response)
        db.session.commit()
        
        log_activity(current_user.id, 'support_response_add', f'Added AI response for: {form.trigger_words.data}')
        flash('AI response added successfully!', 'success')
        return redirect(url_for('admin_support_responses_old'))
    
    return render_template('admin/edit_support_response.html', form=form, response=None)

# @app.route('/admin/support-responses/<int:response_id>/edit', methods=['GET', 'POST'])
# @login_required
# @admin_required
def admin_edit_support_response_old(response_id):
    """Edit AI support response"""
    response = SupportResponse.query.get_or_404(response_id)
    form = AdminSupportResponseForm(obj=response)
    
    if form.validate_on_submit():
        response.trigger_words = form.trigger_words.data
        response.category = form.category.data
        response.response_text = form.response_text.data
        response.priority = form.priority.data
        response.is_active = form.is_active.data
        response.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        log_activity(current_user.id, 'support_response_edit', f'Updated AI response: {response.trigger_words}')
        flash('AI response updated successfully!', 'success')
        return redirect(url_for('admin_support_responses_old'))
    
    return render_template('admin/edit_support_response.html', form=form, response=response)

# @app.route('/admin/support-responses/<int:response_id>/toggle', methods=['POST'])
# @login_required
# @admin_required
def admin_toggle_support_response_old(response_id):
    """Toggle AI support response status"""
    response = SupportResponse.query.get_or_404(response_id)
    response.is_active = not response.is_active
    db.session.commit()
    
    status = 'activated' if response.is_active else 'deactivated'
    log_activity(current_user.id, 'support_response_toggle', f'AI response {status}: {response.trigger_words}')
    flash(f'AI response {status} successfully!', 'success')
    return redirect(url_for('admin_support_responses_old'))


@app.route('/admin/support/<int:message_id>/reply', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_support_reply(message_id):
    message = SupportMessage.query.get_or_404(message_id)
    form = AdminSupportReplyForm(obj=message)
    
    if form.validate_on_submit():
        message.admin_reply = form.admin_reply.data
        message.status = form.status.data
        message.replied_at = datetime.utcnow()
        db.session.commit()
        
        log_activity(current_user.id, 'support_reply', f'Replied to support message: {message.subject}', request.remote_addr)
        flash('Reply sent successfully!', 'success')
        return redirect(url_for('admin_support'))
    
    return render_template('admin/support_reply.html', message=message, form=form)


# Admin UI Customization Routes
@app.route('/admin/ui-customization')
@login_required
@admin_required
def admin_ui_customization():
    ui_elements = UICustomization.query.all()
    return render_template('admin/ui_customization.html', ui_elements=ui_elements)

@app.route('/admin/ui-customization/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_ui_customization():
    form = AdminUICustomizationForm()
    if form.validate_on_submit():
        ui_element = UICustomization(
            element_type=form.element_type.data,
            element_name=form.element_name.data,
            icon_class=form.icon_class.data,
            icon_emoji=form.icon_emoji.data,
            background_color=form.background_color.data,
            text_color=form.text_color.data,
            is_active=form.is_active.data
        )
        db.session.add(ui_element)
        db.session.commit()
        
        log_activity(current_user.id, 'add_ui_customization', f'Added UI element: {form.element_type.data}:{form.element_name.data}')
        flash('UI element added successfully!', 'success')
        return redirect(url_for('admin_ui_customization'))
    
    return render_template('admin/ui_customization_form.html', form=form, title='Add UI Element')

@app.route('/admin/ui-customization/<int:ui_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_ui_customization(ui_id):
    ui_element = UICustomization.query.get_or_404(ui_id)
    form = AdminUICustomizationForm(obj=ui_element)
    
    if form.validate_on_submit():
        ui_element.element_type = form.element_type.data
        ui_element.element_name = form.element_name.data
        ui_element.icon_class = form.icon_class.data
        ui_element.icon_emoji = form.icon_emoji.data
        ui_element.background_color = form.background_color.data
        ui_element.text_color = form.text_color.data
        ui_element.is_active = form.is_active.data
        ui_element.updated_at = datetime.utcnow()
        db.session.commit()
        
        log_activity(current_user.id, 'edit_ui_customization', f'Edited UI element: {ui_element.element_type}:{ui_element.element_name}')
        flash('UI element updated successfully!', 'success')
        return redirect(url_for('admin_ui_customization'))
    
    return render_template('admin/ui_customization_form.html', form=form, ui_element=ui_element, title='Edit UI Element')

@app.route('/admin/ui-customization/<int:ui_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_ui_customization(ui_id):
    ui_element = UICustomization.query.get_or_404(ui_id)
    element_name = f'{ui_element.element_type}:{ui_element.element_name}'
    
    db.session.delete(ui_element)
    db.session.commit()
    
    log_activity(current_user.id, 'delete_ui_customization', f'Deleted UI element: {element_name}')
    flash('UI element deleted successfully!', 'success')
    return redirect(url_for('admin_ui_customization'))


# Admin NFT Management Routes
@app.route('/admin/nfts')
@login_required
@admin_required
def admin_nfts():
    nfts = NFT.query.order_by(NFT.display_order, NFT.created_at.desc()).all()
    collections = NFTCollection.query.all()
    return render_template('admin/nfts.html', nfts=nfts, collections=collections)

@app.route('/admin/nfts/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_nft():
    form = AdminNFTForm()
    # Populate collection choices
    collections = NFTCollection.query.all()
    form.collection_id.choices = [(c.id, c.name) for c in collections]
    
    if form.validate_on_submit():
        nft = NFT(
            name=form.name.data,
            collection_id=form.collection_id.data,
            icon=form.icon.data,
            image_url=form.image_url.data,
            gradient=form.gradient.data,
            price=form.price.data,
            last_sale_price=form.last_sale_price.data,
            rarity=form.rarity.data,
            owner_name=form.owner_name.data,
            unique_id=form.unique_id.data,
            is_verified=form.is_verified.data,
            is_active=form.is_active.data,
            display_order=form.display_order.data
        )
        db.session.add(nft)
        db.session.commit()
        
        log_activity(current_user.id, 'add_nft', f'Added NFT: {form.name.data}')
        flash('NFT added successfully!', 'success')
        return redirect(url_for('admin_nfts'))
    
    return render_template('admin/nft_form.html', form=form, title='Add NFT')

@app.route('/admin/nfts/<int:nft_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_nft(nft_id):
    nft = NFT.query.get_or_404(nft_id)
    form = AdminNFTForm(obj=nft)
    
    # Populate collection choices
    collections = NFTCollection.query.all()
    form.collection_id.choices = [(c.id, c.name) for c in collections]
    
    if form.validate_on_submit():
        nft.name = form.name.data
        nft.collection_id = form.collection_id.data
        nft.icon = form.icon.data
        nft.image_url = form.image_url.data
        nft.gradient = form.gradient.data
        nft.price = form.price.data
        nft.last_sale_price = form.last_sale_price.data
        nft.rarity = form.rarity.data
        nft.owner_name = form.owner_name.data
        nft.unique_id = form.unique_id.data
        nft.is_verified = form.is_verified.data
        nft.is_active = form.is_active.data
        nft.display_order = form.display_order.data
        nft.updated_at = datetime.utcnow()
        db.session.commit()
        
        log_activity(current_user.id, 'edit_nft', f'Edited NFT: {nft.name}')
        flash('NFT updated successfully!', 'success')
        return redirect(url_for('admin_nfts'))
    
    return render_template('admin/nft_form.html', form=form, nft=nft, title='Edit NFT')

@app.route('/admin/nfts/<int:nft_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_nft(nft_id):
    nft = NFT.query.get_or_404(nft_id)
    nft_name = nft.name
    
    db.session.delete(nft)
    db.session.commit()
    
    log_activity(current_user.id, 'delete_nft', f'Deleted NFT: {nft_name}')
    flash('NFT deleted successfully!', 'success')
    return redirect(url_for('admin_nfts'))


# Admin Notices Routes
@app.route('/admin/notices')
@login_required
@admin_required
def admin_notices():
    notices = PlatformNotice.query.order_by(PlatformNotice.page_location, PlatformNotice.display_order).all()
    return render_template('admin/notices.html', notices=notices)

@app.route('/admin/notices/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_notice():
    form = AdminNoticeForm()
    if form.validate_on_submit():
        notice = PlatformNotice(
            page_location=form.page_location.data,
            title=form.title.data,
            message=form.message.data,
            notice_type=form.notice_type.data,
            is_active=form.is_active.data,
            display_order=form.display_order.data
        )
        db.session.add(notice)
        db.session.commit()
        
        log_activity(current_user.id, 'add_notice', f'Added notice: {form.title.data}')
        flash('Notice added successfully!', 'success')
        return redirect(url_for('admin_notices'))
    
    return render_template('admin/notice_form.html', form=form, title='Add Notice')

@app.route('/admin/notices/<int:notice_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_notice(notice_id):
    notice = PlatformNotice.query.get_or_404(notice_id)
    form = AdminNoticeForm(obj=notice)
    
    if form.validate_on_submit():
        notice.page_location = form.page_location.data
        notice.title = form.title.data
        notice.message = form.message.data
        notice.notice_type = form.notice_type.data
        notice.is_active = form.is_active.data
        notice.display_order = form.display_order.data
        notice.updated_at = datetime.utcnow()
        db.session.commit()
        
        log_activity(current_user.id, 'edit_notice', f'Edited notice: {notice.title}')
        flash('Notice updated successfully!', 'success')
        return redirect(url_for('admin_notices'))
    
    return render_template('admin/notice_form.html', form=form, notice=notice, title='Edit Notice')

@app.route('/admin/notices/<int:notice_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_notice(notice_id):
    notice = PlatformNotice.query.get_or_404(notice_id)
    notice_title = notice.title
    
    db.session.delete(notice)
    db.session.commit()
    
    log_activity(current_user.id, 'delete_notice', f'Deleted notice: {notice_title}')
    flash('Notice deleted successfully!', 'success')
    return redirect(url_for('admin_notices'))


# Admin Withdrawal Management Routes
@app.route('/admin/withdrawal-settings', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_withdrawal_settings():
    """Manage withdrawal settings and policies"""
    settings = WithdrawalSettings.get_settings()
    form = AdminWithdrawalSettingsForm(obj=settings)
    
    if form.validate_on_submit():
        settings.min_withdrawal = form.min_withdrawal.data
        settings.max_withdrawal = form.max_withdrawal.data
        settings.daily_limit = form.daily_limit.data
        settings.processing_fee = form.processing_fee.data
        settings.auto_approval_limit = form.auto_approval_limit.data
        settings.require_admin_approval = form.require_admin_approval.data
        settings.processing_time_hours = form.processing_time_hours.data
        settings.is_maintenance_mode = form.is_maintenance_mode.data
        settings.maintenance_message = form.maintenance_message.data
        settings.updated_at = datetime.utcnow()
        db.session.commit()
        
        log_activity(current_user.id, 'update_withdrawal_settings', 'Updated withdrawal settings')
        flash('Withdrawal settings updated successfully!', 'success')
        return redirect(url_for('admin_withdrawal_settings'))
    
    return render_template('admin/withdrawal_settings.html', form=form, settings=settings)


@app.route('/admin/withdrawals')
@login_required
@admin_required
def admin_withdrawals():
    """Manage withdrawal requests"""
    status_filter = request.args.get('status', 'all')
    withdrawals = Withdrawal.query
    
    if status_filter != 'all':
        withdrawals = withdrawals.filter_by(status=status_filter)
    
    withdrawals = withdrawals.order_by(Withdrawal.created_at.desc()).all()
    
    stats = {
        'pending': Withdrawal.query.filter_by(status='pending').count(),
        'approved': Withdrawal.query.filter_by(status='approved').count(),
        'completed': Withdrawal.query.filter_by(status='completed').count(),
        'rejected': Withdrawal.query.filter_by(status='rejected').count()
    }
    
    return render_template('admin/withdrawals.html', withdrawals=withdrawals, stats=stats, status_filter=status_filter)


@app.route('/admin/withdrawals/<int:withdrawal_id>/manage', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_manage_withdrawal(withdrawal_id):
    """Approve, reject, or complete withdrawal"""
    withdrawal = Withdrawal.query.get_or_404(withdrawal_id)
    form = AdminWithdrawalApprovalForm(obj=withdrawal)
    
    if form.validate_on_submit():
        old_status = withdrawal.status
        withdrawal.status = form.status.data
        withdrawal.admin_notes = form.admin_notes.data
        withdrawal.transaction_hash = form.transaction_hash.data
        withdrawal.processed_at = datetime.utcnow()
        
        if form.status.data == 'completed' and old_status != 'completed':
            withdrawal.completed_at = datetime.utcnow()
            
        if form.status.data == 'rejected' and old_status != 'rejected':
            # Refund the amount to user's balance
            withdrawal.user.usdt_balance += withdrawal.amount
            
        db.session.commit()
        
        log_activity(current_user.id, 'manage_withdrawal', 
                    f'Changed withdrawal #{withdrawal.id} status from {old_status} to {form.status.data}')
        flash(f'Withdrawal status updated to {form.status.data}!', 'success')
        return redirect(url_for('admin_withdrawals'))
    
    return render_template('admin/withdrawal_approval.html', withdrawal=withdrawal, form=form)


# Admin Social Media Management Routes
@app.route('/admin/social-media')
@login_required
@admin_required
def admin_social_media():
    """Manage social media links for footer"""
    links = SocialMediaLink.query.order_by(SocialMediaLink.display_order, SocialMediaLink.created_at).all()
    return render_template('admin/social_media.html', links=links)


@app.route('/admin/social-media/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_social_media():
    """Add new social media link"""
    form = AdminSocialMediaForm()
    
    if form.validate_on_submit():
        link = SocialMediaLink(
            platform=form.platform.data,
            icon_class=form.icon_class.data,
            url=form.url.data,
            display_text=form.display_text.data,
            is_active=form.is_active.data,
            display_order=form.display_order.data
        )
        db.session.add(link)
        db.session.commit()
        
        log_activity(current_user.id, 'add_social_media', f'Added social media link: {form.platform.data}')
        flash('Social media link added successfully!', 'success')
        return redirect(url_for('admin_social_media'))
    
    return render_template('admin/social_media_form.html', form=form, title='Add Social Media Link')


@app.route('/admin/social-media/<int:link_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_social_media(link_id):
    """Edit social media link"""
    link = SocialMediaLink.query.get_or_404(link_id)
    form = AdminSocialMediaForm(obj=link)
    
    if form.validate_on_submit():
        link.platform = form.platform.data
        link.icon_class = form.icon_class.data
        link.url = form.url.data
        link.display_text = form.display_text.data
        link.is_active = form.is_active.data
        link.display_order = form.display_order.data
        link.updated_at = datetime.utcnow()
        db.session.commit()
        
        log_activity(current_user.id, 'edit_social_media', f'Edited social media link: {link.platform}')
        flash('Social media link updated successfully!', 'success')
        return redirect(url_for('admin_social_media'))
    
    return render_template('admin/social_media_form.html', form=form, link=link, title='Edit Social Media Link')


@app.route('/admin/social-media/<int:link_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_social_media(link_id):
    """Delete social media link"""
    link = SocialMediaLink.query.get_or_404(link_id)
    platform_name = link.platform
    
    db.session.delete(link)
    db.session.commit()
    
    log_activity(current_user.id, 'delete_social_media', f'Deleted social media link: {platform_name}')
    flash('Social media link deleted successfully!', 'success')
    return redirect(url_for('admin_social_media'))

# Admin Notification Management Routes
@app.route('/admin/notifications')
@login_required
@admin_required
def admin_notifications():
    """Admin notification management"""
    notifications = Notification.query.order_by(Notification.created_at.desc()).all()
    
    stats = {
        'total': len(notifications),
        'active': len([n for n in notifications if n.is_active]),
        'high_priority': len([n for n in notifications if n.priority == 'high']),
        'recent': len([n for n in notifications if (datetime.utcnow() - n.created_at).days <= 7])
    }
    
    return render_template('admin/notifications.html', notifications=notifications, stats=stats)

@app.route('/admin/notifications/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_notification():
    """Add new notification"""
    from forms import AdminNotificationForm
    form = AdminNotificationForm()
    
    if form.validate_on_submit():
        notification = Notification(
            title=form.title.data,
            message=form.message.data,
            type=form.type.data,
            priority=form.priority.data,
            is_active=form.is_active.data
        )
        
        db.session.add(notification)
        db.session.commit()
        
        log_activity(current_user.id, 'admin_add_notification', f'Added notification: {form.title.data}')
        flash('Notification created successfully!', 'success')
        return redirect(url_for('admin_notifications'))
    
    return render_template('admin/notification_form.html', form=form, title='Create Notification')

@app.route('/admin/notifications/<int:notification_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_notification(notification_id):
    """Edit notification"""
    from forms import AdminNotificationForm
    notification = Notification.query.get_or_404(notification_id)
    form = AdminNotificationForm(obj=notification)
    
    if form.validate_on_submit():
        notification.title = form.title.data
        notification.message = form.message.data
        notification.type = form.type.data
        notification.priority = form.priority.data
        notification.is_active = form.is_active.data
        notification.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        log_activity(current_user.id, 'admin_edit_notification', f'Edited notification: {notification.title}')
        flash('Notification updated successfully!', 'success')
        return redirect(url_for('admin_notifications'))
    
    return render_template('admin/notification_form.html', form=form, notification=notification, title='Edit Notification')

@app.route('/admin/notifications/<int:notification_id>/toggle', methods=['POST'])
@login_required
@admin_required
def admin_toggle_notification(notification_id):
    """Toggle notification active status"""
    notification = Notification.query.get_or_404(notification_id)
    notification.is_active = not notification.is_active
    notification.updated_at = datetime.utcnow()
    db.session.commit()
    
    status = 'activated' if notification.is_active else 'deactivated'
    log_activity(current_user.id, 'admin_toggle_notification', f'Notification {status}: {notification.title}')
    flash(f'Notification {status} successfully!', 'success')
    return redirect(url_for('admin_notifications'))

@app.route('/admin/notifications/<int:notification_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_notification(notification_id):
    """Delete notification"""
    notification = Notification.query.get_or_404(notification_id)
    title = notification.title
    
    db.session.delete(notification)
    db.session.commit()
    
    log_activity(current_user.id, 'admin_delete_notification', f'Deleted notification: {title}')
    flash('Notification deleted successfully!', 'success')
    return redirect(url_for('admin_notifications'))

# API endpoint for getting user notifications
@app.route('/api/notifications')
@login_required
def api_get_notifications():
    """Get notifications for current user"""
    try:
        # Get active notifications ordered by priority and recency
        notifications = Notification.query.filter_by(is_active=True).order_by(
            Notification.priority.desc(),
            Notification.created_at.desc()
        ).limit(10).all()
        
        # Convert to JSON format
        notification_data = []
        for notification in notifications:
            notification_data.append({
                'id': notification.id,
                'title': notification.title,
                'message': notification.message,
                'type': notification.type,
                'priority': notification.priority,
                'icon': notification.get_icon(),
                'time': notification.created_at.strftime('%Y-%m-%d %H:%M'),
                'time_ago': get_time_ago(notification.created_at)
            })
        
        return jsonify({
            'success': True,
            'notifications': notification_data,
            'count': len(notification_data)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def get_time_ago(dt):
    """Helper function to get human readable time difference"""
    now = datetime.utcnow()
    diff = now - dt
    
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "Just now"

# REMOVED - This function is now handled by enhanced_routes.py to avoid conflicts

# REMOVED - This function is now handled by enhanced_routes.py to avoid conflicts

# Import admin referral commission routes
from admin_referral_commission_routes import *

# Support System API Routes
@app.route('/api/support/send-message', methods=['POST'])
@login_required
def send_support_message():
    """Send message from user to support"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'success': False, 'error': 'Message cannot be empty'})
        
        # Try to create SupportChat, fallback to SupportMessage
        try:
            from models import SupportChat
            # Create new support chat message
            chat = SupportChat(
                user_id=current_user.id,
                message=message,
                sender_type='user'
            )
            
            db.session.add(chat)
            db.session.commit()
            
            timestamp = chat.created_at.strftime('%H:%M')
            chat_id = chat.id
            
        except (ImportError, AttributeError, Exception):
            # Fallback to SupportMessage
            support_msg = SupportMessage(
                user_id=current_user.id,
                subject='User Support Request',
                message=message,
                status='open'
            )
            
            db.session.add(support_msg)
            db.session.commit()
            
            timestamp = support_msg.created_at.strftime('%H:%M')
            chat_id = support_msg.id
        
        # Log activity
        log_activity(current_user.id, 'support_message_sent', f'User sent support message: {message[:50]}...')
        
        return jsonify({
            'success': True,
            'message': 'Message sent successfully',
            'chat_id': chat_id,
            'timestamp': timestamp
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/support/get-messages')
@login_required
def get_support_messages():
    """Get user's support chat messages"""
    try:
        messages = []
        
        # Try SupportChat first, fallback to SupportMessage
        try:
            from models import SupportChat
            SupportChat.cleanup_expired_chats()
            
            # Get user's messages (not expired)
            chats = SupportChat.query.filter_by(user_id=current_user.id).filter(
                SupportChat.expires_at > datetime.utcnow()
            ).order_by(SupportChat.created_at.asc()).all()
            
            for chat in chats:
                messages.append({
                    'id': chat.id,
                    'message': chat.message,
                    'sender_type': chat.sender_type,
                    'timestamp': chat.created_at.strftime('%H:%M'),
                    'is_read': chat.is_read,
                    'auto_response': getattr(chat, 'auto_response_sent', False)
                })
                
        except (ImportError, AttributeError, Exception):
            # Fallback to SupportMessage
            support_msgs = SupportMessage.query.filter_by(user_id=current_user.id).order_by(SupportMessage.created_at.asc()).all()
            
            for msg in support_msgs:
                # Add user message
                messages.append({
                    'id': msg.id,
                    'message': msg.message,
                    'sender_type': 'user',
                    'timestamp': msg.created_at.strftime('%H:%M'),
                    'is_read': True,
                    'auto_response': False
                })
                
                # Add admin reply if exists
                if msg.admin_reply:
                    messages.append({
                        'id': f"{msg.id}_reply",
                        'message': msg.admin_reply,
                        'sender_type': 'admin',
                        'timestamp': msg.replied_at.strftime('%H:%M') if msg.replied_at else msg.created_at.strftime('%H:%M'),
                        'is_read': True,
                        'auto_response': False
                    })
        
        return jsonify({
            'success': True,
            'messages': messages,
            'count': len(messages)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/admin/support/reply', methods=['POST'])
@login_required
@admin_required
def admin_reply_support():
    """Admin reply to user support message"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        message = data.get('message', '').strip()
        
        if not user_id or not message:
            return jsonify({'success': False, 'error': 'User ID and message are required'})
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'})
        
        # Try SupportChat first, fallback to SupportMessage
        try:
            from models import SupportChat
            # Create admin reply
            admin_chat = SupportChat(
                user_id=user_id,
                message=message,
                sender_type='admin',
                is_read=False
            )
            
            db.session.add(admin_chat)
            
            # Mark user's unread messages as read
            unread_messages = SupportChat.query.filter_by(
                user_id=user_id,
                sender_type='user',
                is_read=False
            ).all()
            
            for msg in unread_messages:
                msg.is_read = True
            
            db.session.commit()
            timestamp = admin_chat.created_at.strftime('%H:%M')
            
        except (ImportError, AttributeError, Exception):
            # Fallback to updating SupportMessage
            latest_msg = SupportMessage.query.filter_by(user_id=user_id).order_by(SupportMessage.created_at.desc()).first()
            if latest_msg:
                latest_msg.admin_reply = message
                latest_msg.status = 'replied'
                latest_msg.replied_at = datetime.utcnow()
                db.session.commit()
                timestamp = latest_msg.replied_at.strftime('%H:%M')
            else:
                return jsonify({'success': False, 'error': 'No message found to reply to'})
        
        log_activity(current_user.id, 'admin_support_reply', f'Admin replied to {user.username}: {message[:50]}...')
        
        return jsonify({
            'success': True,
            'message': 'Reply sent successfully',
            'timestamp': timestamp
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/admin/support/conversations')
@login_required
@admin_required
def get_admin_conversations():
    """Get all support conversations for admin"""
    try:
        # Clean up expired chats first
        SupportChat.cleanup_expired_chats()
        
        # Get all users with active conversations
        conversations = []
        users_with_messages = db.session.query(User).join(SupportChat).filter(
            SupportChat.expires_at > datetime.utcnow()
        ).distinct().all()
        
        for user in users_with_messages:
            messages = SupportChat.query.filter_by(user_id=user.id).filter(
                SupportChat.expires_at > datetime.utcnow()
            ).order_by(SupportChat.created_at.asc()).all()
            
            unread_count = SupportChat.query.filter_by(
                user_id=user.id,
                sender_type='user',
                is_read=False
            ).filter(SupportChat.expires_at > datetime.utcnow()).count()
            
            conversations.append({
                'user_id': user.id,
                'username': user.username,
                'unread_count': unread_count,
                'messages': [{
                    'id': msg.id,
                    'message': msg.message,
                    'sender_type': msg.sender_type,
                    'timestamp': msg.created_at.strftime('%H:%M'),
                    'is_read': msg.is_read
                } for msg in messages]
            })
        
        return jsonify({
            'success': True,
            'conversations': conversations
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/admin/support/user-messages/<int:user_id>')
@login_required
@admin_required
def get_user_messages(user_id):
    """Get messages for specific user (admin only)"""
    try:
        user = User.query.get_or_404(user_id)
        message_data = []
        
        # Try SupportChat first, fallback to SupportMessage
        try:
            from models import SupportChat
            messages = SupportChat.query.filter_by(user_id=user_id).filter(
                SupportChat.expires_at > datetime.utcnow()
            ).order_by(SupportChat.created_at.asc()).all()
            
            # Mark user messages as read
            for msg in messages:
                if msg.sender_type == 'user':
                    msg.is_read = True
            
            db.session.commit()
            
            for msg in messages:
                message_data.append({
                    'id': msg.id,
                    'message': msg.message,
                    'sender_type': msg.sender_type,
                    'timestamp': msg.created_at.strftime('%H:%M'),
                    'is_read': msg.is_read
                })
                
        except (ImportError, AttributeError, Exception):
            # Fallback to SupportMessage
            support_msgs = SupportMessage.query.filter_by(user_id=user_id).order_by(SupportMessage.created_at.asc()).all()
            
            for msg in support_msgs:
                # Add user message
                message_data.append({
                    'id': msg.id,
                    'message': msg.message,
                    'sender_type': 'user',
                    'timestamp': msg.created_at.strftime('%H:%M'),
                    'is_read': True
                })
                
                # Add admin reply if exists
                if msg.admin_reply:
                    message_data.append({
                        'id': f"{msg.id}_reply",
                        'message': msg.admin_reply,
                        'sender_type': 'admin',
                        'timestamp': msg.replied_at.strftime('%H:%M') if msg.replied_at else msg.created_at.strftime('%H:%M'),
                        'is_read': True
                    })
        
        return jsonify({
            'success': True,
            'messages': message_data,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/admin/support/get-conversation/<int:user_id>')
@login_required
@admin_required
def get_admin_conversation(user_id):
    """Get conversation with specific user for admin"""
    try:
        user = User.query.get_or_404(user_id)
        conversation = []
        
        # Try SupportChat first, fallback to SupportMessage
        try:
            from models import SupportChat
            messages = SupportChat.query.filter_by(user_id=user_id).filter(
                SupportChat.expires_at > datetime.utcnow()
            ).order_by(SupportChat.created_at.asc()).all()
            
            for msg in messages:
                conversation.append({
                    'id': msg.id,
                    'message': msg.message,
                    'sender_type': msg.sender_type,
                    'timestamp': msg.created_at.strftime('%H:%M - %d/%m/%Y'),
                    'is_read': msg.is_read
                })
                
        except (ImportError, AttributeError, Exception):
            # Fallback to SupportMessage
            support_msgs = SupportMessage.query.filter_by(user_id=user_id).order_by(SupportMessage.created_at.asc()).all()
            
            for msg in support_msgs:
                # Add user message
                conversation.append({
                    'id': msg.id,
                    'message': msg.message,
                    'sender_type': 'user',
                    'timestamp': msg.created_at.strftime('%H:%M - %d/%m/%Y'),
                    'is_read': True
                })
                
                # Add admin reply if exists
                if msg.admin_reply:
                    conversation.append({
                        'id': f"{msg.id}_reply",
                        'message': msg.admin_reply,
                        'sender_type': 'admin',
                        'timestamp': msg.replied_at.strftime('%H:%M - %d/%m/%Y') if msg.replied_at else msg.created_at.strftime('%H:%M - %d/%m/%Y'),
                        'is_read': True
                    })
        
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            },
            'conversation': conversation,
            'message_count': len(conversation)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/admin/support/mark-all-read', methods=['POST'])
@login_required
@admin_required
def mark_all_support_read():
    """Mark all support messages as read"""
    try:
        # Try SupportChat first, fallback to SupportMessage
        try:
            from models import SupportChat
            unread_messages = SupportChat.query.filter_by(
                sender_type='user',
                is_read=False
            ).filter(SupportChat.expires_at > datetime.utcnow()).all()
            
            for msg in unread_messages:
                msg.is_read = True
            
            db.session.commit()
            count = len(unread_messages)
            
        except (ImportError, AttributeError, Exception):
            # For SupportMessage, mark all as having admin reply
            unread_messages = SupportMessage.query.filter_by(status='open').all()
            for msg in unread_messages:
                if not msg.admin_reply:
                    msg.admin_reply = "Message acknowledged"
                    msg.status = 'replied'
                    msg.replied_at = datetime.utcnow()
            
            db.session.commit()
            count = len(unread_messages)
        
        return jsonify({
            'success': True,
            'message': f'Marked {count} messages as read'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Enhanced Referral System Management
@app.route('/admin/referral-system/recalculate')
@login_required
@admin_required
def admin_recalculate_referrals():
    """Recalculate all referral commissions based on current balances"""
    try:
        from referral_utils import recalculate_all_referral_commissions
        recalculate_all_referral_commissions()
        
        log_activity(current_user.id, 'admin_recalculate_referrals', 'Recalculated all referral commissions')
        flash('All referral commissions recalculated successfully based on current user balances!', 'success')
        
    except Exception as e:
        flash(f'Error recalculating referral commissions: {str(e)}', 'error')
        log_activity(current_user.id, 'admin_recalculate_referrals_error', f'Error: {str(e)}')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/referral-system/stats')
@login_required
@admin_required
def admin_referral_stats():
    """View detailed referral system statistics"""
    try:
        from enhanced_referral_system import get_referral_stats
        
        # Get all users with referrals
        users_with_referrals = User.query.filter(User.referrals.any()).all()
        
        referral_data = []
        for user in users_with_referrals:
            stats = get_referral_stats(user.id)
            if stats:
                referral_data.append({
                    'user': user,
                    'stats': stats
                })
        
        return render_template('admin/referral_stats.html', referral_data=referral_data)
        
    except Exception as e:
        flash(f'Error loading referral statistics: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

# Health check for Render deployment
@app.route('/health')
def health_check():
    """Health check endpoint for Render deployment"""
    return jsonify({
        'status': 'healthy',
        'service': 'usdt-staking-platform',
        'version': '1.0.0'
    }), 200

# Error handlers
@app.errorhandler(403)
def forbidden(error):
    return render_template('403.html'), 403

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# Template helper functions
@app.template_global()
def get_crypto_icon(symbol):
    icons = {
        'BTC': '₿',
        'ETH': '⧫',
        'BNB': '🟡',
        'LTC': 'Ł',
        'USDT': '₮',
        'SOL': '◉',
        'TRX': '⚡',
        'DOT': '●'
    }
    return icons.get(symbol, '●')

@app.template_global()
def get_crypto_gradient(symbol):
    gradients = {
        'BTC': 'linear-gradient(135deg, #f7931a 0%, #ff6b35 100%)',
        'ETH': 'linear-gradient(135deg, #627eea 0%, #4f46e5 100%)',
        'BNB': 'linear-gradient(135deg, #f3ba2f 0%, #f59e0b 100%)',
        'LTC': 'linear-gradient(135deg, #345d9d 0%, #1e40af 100%)',
        'USDT': 'linear-gradient(135deg, #26a17b 0%, #059669 100%)',
        'SOL': 'linear-gradient(135deg, #00d4aa 0%, #10b981 100%)',
        'TRX': 'linear-gradient(135deg, #ff060a 0%, #dc2626 100%)',
        'DOT': 'linear-gradient(135deg, #e6007a 0%, #ec4899 100%)'
    }
    return gradients.get(symbol, 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)')


@app.template_global()
def get_social_media_links():
    """Get active social media links for footer"""
    return SocialMediaLink.get_active_links()

# Fixed Bonus Referral System Routes
@app.route('/admin/fixed-bonus-referrals')
@login_required
@admin_required
def admin_fixed_bonus_referrals():
    """Admin interface for fixed bonus referral system"""
    from deposit_based_bonus_system import DepositBasedBonusSystem
    
    # Get comprehensive referral statistics
    total_users = User.query.count()
    users_with_referrals = User.query.filter(User.referred_by.isnot(None)).count()
    total_bonuses = 0
    bonus_count = 0
    
    # Calculate total bonuses paid
    bonus_logs = ActivityLog.query.filter_by(action='referral_bonus').all()
    for log in bonus_logs:
        try:
            if '$' in log.description:
                amount_str = log.description.split('$')[1].split(' ')[0]
                total_bonuses += float(amount_str)
                bonus_count += 1
        except:
            continue
    
    stats = {
        'total_users': total_users,
        'users_with_referrals': users_with_referrals,
        'total_bonuses': total_bonuses,
        'bonus_count': bonus_count,
        'bonus_tiers': DepositBasedBonusSystem.BONUS_TIERS,
        'min_deposit': MultiLevelReferralSystem.MIN_DEPOSIT_AMOUNT
    }
    
    # Get top referrers with detailed information
    top_referrers = []
    for user in User.query.all():
        active_count = MultiLevelReferralSystem.get_active_referrals_count(user.id)
        if active_count > 0:
            top_referrers.append({
                'user': user,
                'active_referrals': active_count,
                'total_referrals': User.query.filter_by(referred_by=user.id).count(),
                'total_bonus': user.referral_bonus
            })
    
    top_referrers = sorted(top_referrers, key=lambda x: x['active_referrals'], reverse=True)[:20]
    
    return render_template('admin/multi_level_referrals.html', stats=stats, top_referrers=top_referrers)

# Referral routes removed as per user request

@app.route('/api/referral/tree/<int:user_id>')
@login_required
def api_referral_tree(user_id):
    """Get detailed referral tree for a specific user"""
    try:
        # Only allow users to see their own tree or admins to see any tree
        if not current_user.is_admin and current_user.id != user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        from multi_level_referral_system import get_user_referral_tree
        tree = get_user_referral_tree(user_id)
        return jsonify({'success': True, 'tree': tree})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/referral/validate-commission', methods=['POST'])
@login_required
@admin_required
def api_validate_referral_commission():
    """Validate and recalculate all referral commissions"""
    try:
        from multi_level_referral_system import MultiLevelReferralSystem
        result = MultiLevelReferralSystem.validate_and_recalculate_all_commissions()
        
        if result['success']:
            log_activity(current_user.id, 'admin_validate_commissions', 
                        f'Validated and recalculated commissions: ${result.get("total_recalculated", 0):.2f}')
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/referral/stats/<int:user_id>')
@login_required
def api_referral_stats(user_id):
    """Get referral statistics for a specific user"""
    try:
        # Only allow users to see their own stats or admins to see any stats
        if not current_user.is_admin and current_user.id != user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        from multi_level_referral_system import MultiLevelReferralSystem
        
        user = User.query.get_or_404(user_id)
        
        # Get detailed statistics
        stats = {
            'user_id': user.id,
            'username': user.username,
            'referral_code': user.referral_code,
            'active_referrals': MultiLevelReferralSystem.get_active_referrals_count(user.id),
            'total_referrals': User.query.filter_by(referred_by=user.id).count(),
            'referral_bonus': user.referral_bonus,
            'is_eligible': MultiLevelReferralSystem.is_eligible_referral(user.id),
            'commission_rates': MultiLevelReferralSystem.COMMISSION_RATES,
            'min_deposit_requirement': MultiLevelReferralSystem.MIN_DEPOSIT_AMOUNT
        }
        
        # Get recent commission logs
        commission_logs = ActivityLog.query.filter_by(
            user_id=user.id,
            action='referral_commission'
        ).order_by(ActivityLog.created_at.desc()).limit(10).all()
        
        stats['recent_commissions'] = [
            {
                'description': log.description,
                'date': log.created_at.isoformat(),
                'amount': float(log.description.split('$')[1].split(' ')[0]) if '$' in log.description else 0
            }
            for log in commission_logs
        ]
        
        return jsonify({'success': True, 'stats': stats})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500