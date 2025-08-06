from app import db
from datetime import datetime

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), default='info')  # info, success, warning, error
    priority = db.Column(db.String(20), default='medium')  # low, medium, high
    is_active = db.Column(db.Boolean, default=True)
    view_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_icon(self):
        icons = {
            'info': 'fas fa-info-circle',
            'success': 'fas fa-check-circle',
            'warning': 'fas fa-exclamation-triangle',
            'error': 'fas fa-times-circle'
        }
        return icons.get(self.type, 'fas fa-bell')
    
    def get_color_class(self):
        colors = {
            'info': 'text-blue-600',
            'success': 'text-green-600',
            'warning': 'text-yellow-600',
            'error': 'text-red-600'
        }
        return colors.get(self.type, 'text-gray-600')
    
    def get_bg_color_class(self):
        colors = {
            'info': 'bg-blue-100 border-blue-300',
            'success': 'bg-green-100 border-green-300',
            'warning': 'bg-yellow-100 border-yellow-300',
            'error': 'bg-red-100 border-red-300'
        }
        return colors.get(self.type, 'bg-gray-100 border-gray-300')

class UserNotificationView(db.Model):
    __tablename__ = 'user_notification_views'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    notification_id = db.Column(db.Integer, db.ForeignKey('notifications.id'), nullable=False)
    viewed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='notification_views')
    notification = db.relationship('Notification', backref='user_views')