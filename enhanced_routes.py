# Enhanced routes for new admin functionality
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import uuid
from app import app, db
from models import Coin, StakingPlan, NFT, NFTCollection
from models_enhanced import CoinReturnRate
from enhanced_forms import AdminCoinStakingPlanForm, AdminDepositAPIForm, AdminNFTEnhancedForm, AdminCoinReturnRateForm
from utils import admin_required, log_activity

# Enhanced Coin Management with Individual Return Rates
@app.route('/admin/coin-return-rates')
@login_required
@admin_required
def admin_coin_return_rates():
    """Manage individual coin return rates by duration"""
    coins = Coin.query.filter_by(active=True).all()
    coin_plans = {}
    
    for coin in coins:
        # Get only coin-specific plans, exclude global plans (coin_id = None)
        plans = StakingPlan.query.filter_by(coin_id=coin.id, active=True).all()
        coin_plans[coin.id] = {plan.duration_days: plan.interest_rate for plan in plans}
    
    return render_template('admin/coin_return_rates.html', coins=coins, coin_plans=coin_plans)

@app.route('/admin/coin-return-rates/edit/<int:coin_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_coin_return_rates(coin_id):
    """Edit return rates with proper UPDATE instead of DELETE+INSERT"""
    coin = Coin.query.get_or_404(coin_id)
    form = AdminCoinReturnRateForm()
    
    if form.validate_on_submit():
        try:
            # Get existing plans for this specific coin
            existing_plans = StakingPlan.query.filter_by(coin_id=coin_id).all()
            existing_by_duration = {plan.duration_days: plan for plan in existing_plans}
            
            durations_rates = {
                7: form.rate_7_days.data,
                15: form.rate_15_days.data,
                30: form.rate_30_days.data,
                90: form.rate_90_days.data,
                120: form.rate_120_days.data,
                180: form.rate_180_days.data,
                365: form.rate_365_days.data
            }
            
            updated_count = 0
            created_count = 0
            
            for duration, rate in durations_rates.items():
                if rate is not None and rate > 0:
                    if duration in existing_by_duration:
                        # UPDATE existing plan
                        plan = existing_by_duration[duration]
                        plan.interest_rate = float(rate)
                        plan.active = bool(form.is_active.data)
                        updated_count += 1
                        print(f"DEBUG: Updated plan for coin_id {coin_id}, duration {duration}, rate {rate}")
                    else:
                        # CREATE new plan
                        new_plan = StakingPlan(
                            coin_id=int(coin_id),
                            duration_days=int(duration),
                            interest_rate=float(rate),
                            active=bool(form.is_active.data)
                        )
                        db.session.add(new_plan)
                        created_count += 1
                        print(f"DEBUG: Created new plan for coin_id {coin_id}, duration {duration}, rate {rate}")
                else:
                    # DELETE plan if rate is 0 or None
                    if duration in existing_by_duration:
                        db.session.delete(existing_by_duration[duration])
                        print(f"DEBUG: Deleted plan for coin_id {coin_id}, duration {duration}")
            
            # Commit all changes
            db.session.commit()
            
            log_activity(current_user.id, 'admin_update_coin_rates', 
                        f'Updated return rates for {coin.symbol} - Updated: {updated_count}, Created: {created_count}')
            flash(f'✅ Return rates updated for {coin.symbol}! Updated: {updated_count}, Created: {created_count}', 'success')
            return redirect(url_for('admin_coin_return_rates'))
            
        except Exception as e:
            db.session.rollback()
            print(f"ERROR: {str(e)}")
            flash(f'❌ Error updating return rates: {str(e)}', 'error')
    
    # Pre-fill form with existing rates for this specific coin only
    existing_plans = StakingPlan.query.filter_by(coin_id=coin_id).all()
    for plan in existing_plans:
        if plan.duration_days == 7:
            form.rate_7_days.data = plan.interest_rate
        elif plan.duration_days == 15:
            form.rate_15_days.data = plan.interest_rate
        elif plan.duration_days == 30:
            form.rate_30_days.data = plan.interest_rate
        elif plan.duration_days == 90:
            form.rate_90_days.data = plan.interest_rate
        elif plan.duration_days == 120:
            form.rate_120_days.data = plan.interest_rate
        elif plan.duration_days == 180:
            form.rate_180_days.data = plan.interest_rate
        elif plan.duration_days == 365:
            form.rate_365_days.data = plan.interest_rate
        form.is_active.data = plan.active
    
    return render_template('admin/coin_return_rates_form.html', form=form, coin=coin)

# Enhanced NFT Management
@app.route('/admin/nfts-enhanced')
@login_required
@admin_required
def admin_nfts_enhanced():
    """Enhanced NFT management with full control"""
    nfts = NFT.query.order_by(NFT.display_order, NFT.created_at.desc()).all()
    collections = NFTCollection.query.all()
    return render_template('admin/nfts_enhanced.html', nfts=nfts, collections=collections)

@app.route('/admin/nfts-enhanced/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_nft_enhanced():
    """Add new NFT with enhanced features"""
    form = AdminNFTEnhancedForm()
    form.collection_id.choices = [(c.id, c.name) for c in NFTCollection.query.all()]
    
    if form.validate_on_submit():
        # Handle image upload
        image_url = form.image_url.data
        image_file_path = None
        
        if form.image_file.data:
            filename = secure_filename(form.image_file.data.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'nfts', unique_filename)
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            form.image_file.data.save(file_path)
            image_file_path = f"/static/uploads/nfts/{unique_filename}"
            image_url = image_file_path
        
        # Handle blue tick upload
        blue_tick_path = None
        if form.blue_tick_file.data:
            filename = secure_filename(form.blue_tick_file.data.filename)
            unique_filename = f"bluetick_{uuid.uuid4().hex}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'blueticks', unique_filename)
            
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            form.blue_tick_file.data.save(file_path)
            blue_tick_path = f"/static/uploads/blueticks/{unique_filename}"
        
        # Generate automatic values for simplified form
        import random
        unique_id = f"NFT{random.randint(1000, 9999)}"
        
        nft = NFT(
            collection_id=form.collection_id.data,
            name=form.name.data,
            image_url=image_url or 'https://picsum.photos/300/300?random=' + str(random.randint(1, 100)),
            price=form.price.data,
            last_sale_price=form.price.data * 0.9,  # Auto set to 90% of current price
            unique_id=unique_id,
            is_verified=form.is_verified.data,
            is_active=form.is_active.data
        )
        
        # Add custom fields for enhanced model
        nft.description = f"Premium NFT: {nft.name}"
        nft.blue_tick_url = blue_tick_path
        
        db.session.add(nft)
        db.session.commit()
        
        log_activity(current_user.id, 'admin_add_nft', f'Added NFT {nft.name}')
        flash('NFT added successfully', 'success')
        return redirect(url_for('admin_nfts_enhanced'))
    
    return render_template('admin/nft_simple_form.html', form=form, title='Add NFT')

@app.route('/admin/nfts-enhanced/edit/<int:nft_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_nft_enhanced(nft_id):
    """Edit NFT with enhanced features"""
    nft = NFT.query.get_or_404(nft_id)
    form = AdminNFTEnhancedForm(obj=nft)
    form.collection_id.choices = [(c.id, c.name) for c in NFTCollection.query.all()]
    
    if form.validate_on_submit():
        try:
            # Handle image upload
            if form.image_file.data:
                filename = secure_filename(form.image_file.data.filename)
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                file_path = os.path.join(app.config.get('UPLOAD_FOLDER', 'static/uploads'), 'nfts', unique_filename)
                
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                form.image_file.data.save(file_path)
                nft.image_url = f"/static/uploads/nfts/{unique_filename}"
            elif form.image_url.data:
                nft.image_url = form.image_url.data
            
            # Handle blue tick upload
            if form.blue_tick_file.data:
                filename = secure_filename(form.blue_tick_file.data.filename)
                unique_filename = f"bluetick_{uuid.uuid4().hex}_{filename}"
                file_path = os.path.join(app.config.get('UPLOAD_FOLDER', 'static/uploads'), 'blueticks', unique_filename)
                
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                form.blue_tick_file.data.save(file_path)
                
                # Set blue tick URL in NFT model
                nft.blue_tick_url = f"/static/uploads/blueticks/{unique_filename}"
            
            # Update basic fields
            nft.collection_id = form.collection_id.data
            nft.name = form.name.data
            nft.price = form.price.data
            nft.last_sale_price = form.price.data * 0.9  # Auto set to 90% of current price
            nft.is_verified = form.is_verified.data
            nft.is_active = form.is_active.data
            
            # Update enhanced fields
            nft.description = f"Premium NFT: {nft.name}"
            
            db.session.commit()
            
            log_activity(current_user.id, 'admin_edit_nft', f'Updated NFT {nft.name}')
            flash(f'NFT "{nft.name}" updated successfully!', 'success')
            return redirect(url_for('admin_nfts_enhanced'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating NFT: {str(e)}', 'error')
    
    # Pre-fill form with existing data
    if not form.is_submitted():
        form.collection_id.data = nft.collection_id
        form.name.data = nft.name
        form.price.data = nft.price
        form.is_verified.data = nft.is_verified
        form.is_active.data = nft.is_active
    
    return render_template('admin/nft_simple_form.html', form=form, nft=nft, title='Edit NFT')

@app.route('/admin/nfts-enhanced/delete/<int:nft_id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_nft_enhanced(nft_id):
    """Delete NFT"""
    nft = NFT.query.get_or_404(nft_id)
    nft_name = nft.name
    
    try:
        # Delete associated files if they exist
        if nft.image_url and nft.image_url.startswith('/static/uploads/'):
            file_path = nft.image_url.replace('/static/', '')
            full_path = os.path.join('static', file_path.lstrip('/'))
            if os.path.exists(full_path):
                os.remove(full_path)
        
        if nft.blue_tick_url and nft.blue_tick_url.startswith('/static/uploads/'):
            file_path = nft.blue_tick_url.replace('/static/', '')
            full_path = os.path.join('static', file_path.lstrip('/'))
            if os.path.exists(full_path):
                os.remove(full_path)
        
        db.session.delete(nft)
        db.session.commit()
        
        log_activity(current_user.id, 'admin_delete_nft', f'Deleted NFT {nft_name}')
        return jsonify({'success': True, 'message': f'NFT "{nft_name}" deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error deleting NFT: {str(e)}'}, 500)

# Deposit API Management
@app.route('/admin/deposit-apis')
@login_required
@admin_required
def admin_deposit_apis():
    """Manage deposit verification APIs"""
    from models_enhanced import DepositAPI
    apis = DepositAPI.query.order_by(DepositAPI.is_primary.desc(), DepositAPI.created_at).all()
    return render_template('admin/deposit_apis.html', apis=apis)

@app.route('/admin/deposit-apis/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_deposit_api():
    """Add new deposit verification API"""
    form = AdminDepositAPIForm()
    
    if form.validate_on_submit():
        from models_enhanced import DepositAPI
        
        # If setting as primary, remove primary from others
        if form.is_primary.data:
            DepositAPI.query.filter_by(is_primary=True, network=form.network.data).update({'is_primary': False})
        
        api = DepositAPI(
            api_name=form.api_name.data,
            api_url=form.api_url.data,
            api_key=form.api_key.data,
            network=form.network.data,
            is_active=form.is_active.data,
            is_primary=form.is_primary.data
        )
        
        db.session.add(api)
        db.session.commit()
        
        log_activity(current_user.id, 'admin_add_api', f'Added deposit API {api.api_name}')
        flash('Deposit API added successfully', 'success')
        return redirect(url_for('admin_deposit_apis'))
    
    return render_template('admin/deposit_api_form.html', form=form, title='Add Deposit API')

# Health check route already exists in routes.py - no duplicate needed