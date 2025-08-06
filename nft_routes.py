"""
Simple NFT Routes
Clean implementation without database conflicts
"""

from flask import render_template, request, redirect, url_for, flash
from app import app, db
from models import NFT, NFTCollection
from nft_forms import SimpleNFTForm
from utils import admin_required
from imgbb_upload import imgbb_uploader
import os
import uuid
from werkzeug.utils import secure_filename

@app.route('/admin/nfts-simple')
@admin_required
def admin_nfts_simple():
    """Simple NFT management page"""
    try:
        nfts = NFT.query.order_by(NFT.created_at.desc()).all()
        return render_template('admin/nfts_simple.html', nfts=nfts, title='NFT Management')
    except Exception as e:
        flash(f'Error loading NFTs: {str(e)}', 'error')
        return render_template('admin/nfts_simple.html', nfts=[], title='NFT Management')

@app.route('/admin/nfts-gallery')
@admin_required
def admin_nfts_gallery():
    """NFT gallery view with images"""
    try:
        nfts = NFT.query.order_by(NFT.created_at.desc()).all()
        return render_template('admin/nft_gallery.html', nfts=nfts, title='NFT Gallery')
    except Exception as e:
        flash(f'Error loading NFTs: {str(e)}', 'error')
        return render_template('admin/nft_gallery.html', nfts=[], title='NFT Gallery')

@app.route('/admin/nfts-simple/add', methods=['GET', 'POST'])
@admin_required
def admin_add_nft_simple():
    """Add new NFT - simple version"""
    form = SimpleNFTForm()
    
    # Populate collection choices
    collections = NFTCollection.query.all()
    form.collection_id.choices = [(c.id, c.name) for c in collections]
    
    if form.validate_on_submit():
        print(f"DEBUG: Form validation passed for NFT add")
        try:
            # Handle image upload - Fast local storage first
            image_url = None
            if form.image_file.data:
                try:
                    # Try ImgBB upload with timeout
                    upload_result = imgbb_uploader.upload_image(
                        form.image_file.data, 
                        name=f"nft_{form.name.data.replace(' ', '_')}"
                    )
                    
                    if upload_result['success']:
                        image_url = upload_result['url']
                        flash(f'Image uploaded successfully!', 'success')
                    else:
                        raise Exception("ImgBB upload failed")
                        
                except Exception as e:
                    # Fallback to local storage for faster response
                    filename = secure_filename(form.image_file.data.filename)
                    unique_filename = f"{uuid.uuid4().hex}_{filename}"
                    file_path = os.path.join('static/uploads/nfts', unique_filename)
                    
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    form.image_file.data.save(file_path)
                    image_url = f"/static/uploads/nfts/{unique_filename}"
                    flash(f'Image uploaded locally', 'success')
            
            # Handle blue tick upload - Fast local storage first
            blue_tick_url = None
            if form.blue_tick_file.data and form.is_verified.data:
                try:
                    # Try ImgBB upload with timeout
                    upload_result = imgbb_uploader.upload_image(
                        form.blue_tick_file.data, 
                        name=f"bluetick_{form.name.data.replace(' ', '_')}"
                    )
                    
                    if upload_result['success']:
                        blue_tick_url = upload_result['url']
                        flash(f'Blue tick uploaded successfully!', 'success')
                    else:
                        raise Exception("ImgBB upload failed")
                        
                except Exception as e:
                    # Fallback to local storage for faster response
                    filename = secure_filename(form.blue_tick_file.data.filename)
                    unique_filename = f"bluetick_{uuid.uuid4().hex}_{filename}"
                    file_path = os.path.join('static/uploads/blueticks', unique_filename)
                    
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    form.blue_tick_file.data.save(file_path)
                    blue_tick_url = f"/static/uploads/blueticks/{unique_filename}"
                    flash(f'Blue tick uploaded locally', 'success')
            
            # Create NFT
            nft = NFT(
                collection_id=form.collection_id.data,
                name=form.name.data,
                image_url=image_url or f'https://picsum.photos/300/300?random={uuid.uuid4().hex[:8]}',
                price=form.price.data,
                last_sale_price=form.price.data * 0.9,
                unique_id=f"NFT{uuid.uuid4().hex[:8].upper()}",
                is_verified=form.is_verified.data,
                blue_tick_url=blue_tick_url,
                rarity=5 if form.is_verified.data else 3,
                description=f"Premium NFT: {form.name.data}",
                is_active=form.is_active.data
            )
            
            db.session.add(nft)
            db.session.commit()
            
            flash('NFT added successfully!', 'success')
            print(f"DEBUG: NFT added successfully")
            return redirect(url_for('admin_nfts_simple'))
            
        except Exception as e:
            db.session.rollback()
            print(f"DEBUG: Error adding NFT: {str(e)}")
            flash(f'Error adding NFT: {str(e)}', 'error')
    else:
        if form.errors:
            print(f"DEBUG: Form validation failed for NFT add: {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'{field}: {error}', 'error')
    
    return render_template('admin/nft_form_simple.html', form=form, title='Add NFT')

@app.route('/admin/nfts-simple/edit/<int:nft_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_nft_simple(nft_id):
    """Edit NFT - simple version"""
    nft = NFT.query.get_or_404(nft_id)
    form = SimpleNFTForm()
    
    # Populate collection choices
    collections = NFTCollection.query.all()
    form.collection_id.choices = [(c.id, c.name) for c in collections]
    
    if form.validate_on_submit():
        print(f"DEBUG: Form validation passed for NFT edit {nft_id}")
        try:
            # Handle image upload - Fast local storage first
            if form.image_file.data:
                try:
                    # Try ImgBB upload with timeout
                    upload_result = imgbb_uploader.upload_image(
                        form.image_file.data, 
                        name=f"nft_{form.name.data.replace(' ', '_')}"
                    )
                    
                    if upload_result['success']:
                        nft.image_url = upload_result['url']
                        flash(f'Image updated successfully!', 'success')
                    else:
                        raise Exception("ImgBB upload failed")
                        
                except Exception as e:
                    # Fallback to local storage for faster response
                    filename = secure_filename(form.image_file.data.filename)
                    unique_filename = f"{uuid.uuid4().hex}_{filename}"
                    file_path = os.path.join('static/uploads/nfts', unique_filename)
                    
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    form.image_file.data.save(file_path)
                    nft.image_url = f"/static/uploads/nfts/{unique_filename}"
                    flash(f'Image uploaded locally', 'success')
            
            # Handle blue tick upload - Fast local storage first
            if form.blue_tick_file.data and form.is_verified.data:
                try:
                    # Try ImgBB upload with timeout
                    upload_result = imgbb_uploader.upload_image(
                        form.blue_tick_file.data, 
                        name=f"bluetick_{form.name.data.replace(' ', '_')}"
                    )
                    
                    if upload_result['success']:
                        nft.blue_tick_url = upload_result['url']
                        flash(f'Blue tick updated successfully!', 'success')
                    else:
                        raise Exception("ImgBB upload failed")
                        
                except Exception as e:
                    # Fallback to local storage for faster response
                    filename = secure_filename(form.blue_tick_file.data.filename)
                    unique_filename = f"bluetick_{uuid.uuid4().hex}_{filename}"
                    file_path = os.path.join('static/uploads/blueticks', unique_filename)
                    
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    form.blue_tick_file.data.save(file_path)
                    nft.blue_tick_url = f"/static/uploads/blueticks/{unique_filename}"
                    flash(f'Blue tick uploaded locally', 'success')
            
            # Update NFT fields
            nft.collection_id = form.collection_id.data
            nft.name = form.name.data
            nft.price = form.price.data
            nft.last_sale_price = form.price.data * 0.9
            nft.is_verified = form.is_verified.data
            nft.is_active = form.is_active.data
            nft.rarity = 5 if form.is_verified.data else 3
            nft.description = f"Premium NFT: {form.name.data}"
            
            db.session.commit()
            
            flash('NFT updated successfully!', 'success')
            print(f"DEBUG: NFT {nft_id} updated successfully")
            return redirect(url_for('admin_nfts_simple'))
            
        except Exception as e:
            db.session.rollback()
            print(f"DEBUG: Error updating NFT {nft_id}: {str(e)}")
            flash(f'Error updating NFT: {str(e)}', 'error')
    else:
        if form.errors:
            print(f"DEBUG: Form validation failed for NFT edit {nft_id}: {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'{field}: {error}', 'error')
    
    # Pre-populate form
    if not form.is_submitted():
        form.collection_id.data = nft.collection_id
        form.name.data = nft.name
        form.price.data = nft.price
        form.is_verified.data = nft.is_verified
        form.is_active.data = nft.is_active
    
    return render_template('admin/nft_form_simple.html', form=form, nft=nft, title='Edit NFT')

@app.route('/admin/nfts-simple/delete/<int:nft_id>', methods=['POST'])
@admin_required
def admin_delete_nft_simple(nft_id):
    """Delete NFT"""
    try:
        nft = NFT.query.get_or_404(nft_id)
        db.session.delete(nft)
        db.session.commit()
        flash('NFT deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting NFT: {str(e)}', 'error')
    
    return redirect(url_for('admin_nfts_simple'))