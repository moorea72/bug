"""
Render.com Deployment Configuration
For USDT Staking Platform
"""
import os

class RenderConfig:
    """Production configuration for Render.com deployment"""
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://localhost/staking_platform')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20
    }
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'production-secret-key-change-me')
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # File uploads
    UPLOAD_FOLDER = '/opt/render/project/src/static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # Cache settings for performance
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 year
    
    # API Configuration
    MORALIS_API_KEY = os.environ.get('MORALIS_API_KEY')
    BSCSCAN_API_KEY = os.environ.get('BSCSCAN_API_KEY')
    
    # Performance optimizations
    COMPRESS_ALGORITHM = 'gzip'
    COMPRESS_LEVEL = 6
    COMPRESS_MIN_SIZE = 500

def get_render_requirements():
    """Generate requirements.txt for Render deployment"""
    return """
flask==3.0.0
flask-sqlalchemy==3.1.1
flask-login==0.6.3
flask-wtf==1.2.1
wtforms==3.1.0
werkzeug==3.0.1
gunicorn==21.2.0
psycopg2-binary==2.9.9
email-validator==2.1.0
qrcode==7.4.2
pillow==10.1.0
requests==2.31.0
python-dotenv==1.0.0
sqlalchemy==2.0.23
trafilatura==1.6.4
web3==6.11.4
pyjwt==2.8.0
oauthlib==3.2.2
flask-dance==7.0.0
flask-compress==1.14
"""

def create_render_yaml():
    """Create render.yaml for automatic deployment"""
    return """
services:
  - type: web
    name: usdt-staking-platform
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 main:app"
    envVars:
      - key: DATABASE_URL
        sync: false
      - key: SECRET_KEY
        generateValue: true
      - key: MORALIS_API_KEY
        sync: false
      - key: BSCSCAN_API_KEY
        sync: false
    healthCheckPath: /health

databases:
  - name: staking-platform-db
    databaseName: staking_platform
    user: staking_user
"""