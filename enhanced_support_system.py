
#!/usr/bin/env python3
"""
Enhanced Support System - Popup Chat with Admin Integration
Features:
1. Support popup interface
2. User messages go to admin automatically  
3. Admin can reply to users
4. Auto-delete chats after 24 hours
5. Auto-response if admin doesn't reply within 1 minute
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from app import app, db
from models import SupportChat, User, ActivityLog
from utils import admin_required, log_activity
import threading
import time

support_bp = Blueprint('enhanced_support', __name__)

# Auto-response message
AUTO_RESPONSE_MESSAGE = "Thank you for contacting our support team. You will receive a reply soon from our administrators."

def send_auto_response(chat_id):
    """Send auto-response after 1 minute if admin hasn't replied"""
    def delayed_response():
        time.sleep(60)  # Wait 1 minute
        
        with app.app_context():
            chat = SupportChat.query.get(chat_id)
            if chat and not chat.admin_reply and not chat.auto_response_sent:
                # Send auto-response
                auto_chat = SupportChat(
                    user_id=chat.user_id,
                    message=AUTO_RESPONSE_MESSAGE,
                    sender_type='admin',
                    is_read=False,
                    auto_response_sent=True
                )
                
                # Mark original message as having auto-response sent
                chat.auto_response_sent = True
                
                db.session.add(auto_chat)
                db.session.commit()
                
                log_activity(None, 'auto_support_response', f'Auto-response sent to user {chat.user.username}')
    
    # Start background thread for auto-response
    thread = threading.Thread(target=delayed_response)
    thread.daemon = True
    thread.start()

@app.route('/api/support/send-message', methods=['POST'])
@login_required
def send_support_message():
    """Send message from user to support"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'success': False, 'error': 'Message cannot be empty'})
        
        # Create new support chat message
        chat = SupportChat(
            user_id=current_user.id,
            message=message,
            sender_type='user'
        )
        
        db.session.add(chat)
        db.session.commit()
        
        # Log activity
        log_activity(current_user.id, 'support_message_sent', f'User sent support message: {message[:50]}...')
        
        # Start auto-response timer
        send_auto_response(chat.id)
        
        return jsonify({
            'success': True,
            'message': 'Message sent successfully',
            'chat_id': chat.id,
            'timestamp': chat.created_at.strftime('%H:%M')
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/support/get-messages')
@login_required
def get_support_messages():
    """Get user's support chat messages"""
    try:
        # Clean up expired chats first
        SupportChat.cleanup_expired_chats()
        
        # Get user's messages (not expired)
        chats = SupportChat.query.filter_by(user_id=current_user.id).filter(
            SupportChat.expires_at > datetime.utcnow()
        ).order_by(SupportChat.created_at.asc()).all()
        
        messages = []
        for chat in chats:
            messages.append({
                'id': chat.id,
                'message': chat.message,
                'sender_type': chat.sender_type,
                'timestamp': chat.created_at.strftime('%H:%M'),
                'is_read': chat.is_read,
                'auto_response': chat.auto_response_sent
            })
        
        return jsonify({
            'success': True,
            'messages': messages,
            'count': len(messages)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/support-chat')
@login_required
@admin_required
def admin_support_chat():
    """Admin support chat management"""
    try:
        # Clean up expired chats first
        expired_count = SupportChat.cleanup_expired_chats()
        
        # Get all active support chats grouped by user
        chats_by_user = {}
        active_chats = SupportChat.query.filter(
            SupportChat.expires_at > datetime.utcnow()
        ).order_by(SupportChat.created_at.desc()).all()
        
        for chat in active_chats:
            if chat.user_id not in chats_by_user:
                chats_by_user[chat.user_id] = {
                    'user': chat.user,
                    'messages': [],
                    'unread_count': 0,
                    'last_message_time': chat.created_at
                }
            
            chats_by_user[chat.user_id]['messages'].append(chat)
            
            if not chat.is_read and chat.sender_type == 'user':
                chats_by_user[chat.user_id]['unread_count'] += 1
            
            if chat.created_at > chats_by_user[chat.user_id]['last_message_time']:
                chats_by_user[chat.user_id]['last_message_time'] = chat.created_at
        
        # Sort by last message time (newest first)
        sorted_chats = sorted(
            chats_by_user.values(), 
            key=lambda x: x['last_message_time'], 
            reverse=True
        )
        
        stats = {
            'total_conversations': len(chats_by_user),
            'total_messages': len(active_chats),
            'unread_messages': sum(chat['unread_count'] for chat in chats_by_user.values()),
            'expired_cleaned': expired_count
        }
        
        return render_template('admin/support_chat_management.html', 
                             chats_by_user=sorted_chats, 
                             stats=stats)
        
    except Exception as e:
        flash(f'Error loading support chats: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

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
        
        log_activity(current_user.id, 'admin_support_reply', f'Admin replied to {user.username}: {message[:50]}...')
        
        return jsonify({
            'success': True,
            'message': 'Reply sent successfully',
            'timestamp': admin_chat.created_at.strftime('%H:%M')
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/admin/support/get-conversation/<int:user_id>')
@login_required
@admin_required
def get_user_conversation(user_id):
    """Get conversation with specific user"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Get all messages for this user (not expired)
        messages = SupportChat.query.filter_by(user_id=user_id).filter(
            SupportChat.expires_at > datetime.utcnow()
        ).order_by(SupportChat.created_at.asc()).all()
        
        conversation = []
        for msg in messages:
            conversation.append({
                'id': msg.id,
                'message': msg.message,
                'sender_type': msg.sender_type,
                'timestamp': msg.created_at.strftime('%H:%M - %d/%m/%Y'),
                'is_read': msg.is_read,
                'auto_response': msg.auto_response_sent
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

# Background task to clean expired chats
@app.route('/api/cleanup-support-chats')
def cleanup_support_chats():
    """API endpoint to manually trigger chat cleanup (can be called by cron)"""
    try:
        expired_count = SupportChat.cleanup_expired_chats()
        return jsonify({
            'success': True,
            'expired_chats_deleted': expired_count,
            'message': f'Cleaned up {expired_count} expired support chats'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

# Register blueprint
app.register_blueprint(support_bp)

print("Enhanced Support System with Popup Chat Created Successfully!")
