import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Configure ImgBB API key
os.environ.setdefault('IMGBB_API_KEY', '8f8ec31fde8a226663f6f8edef74f6da')
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database - PostgreSQL support added
database_url = os.environ.get("DATABASE_URL", "postgresql://neondb_owner:npg_4sSItw5JkLZM@ep-falling-firefly-afxbamco-pooler.c-2.us-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require")
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# File upload configuration
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize the app with the extension
db.init_app(app)

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

with app.app_context():
    # Import models and create tables
    import models
    import models_enhanced  # noqa: F401
    from utils import get_crypto_icon, get_crypto_gradient
    
    try:
        # Create all tables
        db.create_all()
        
        # Check if salary_wallet_address column exists and add it if not
        from sqlalchemy import text
        result = db.session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='user' AND column_name='salary_wallet_address'
        """))
        
        if result.fetchone() is None:
            # Column doesn't exist, add it
            db.session.execute(text("""
                ALTER TABLE "user" 
                ADD COLUMN salary_wallet_address VARCHAR(255)
            """))
            db.session.commit()
            print("✓ Added salary_wallet_address column to user table")
        
    except Exception as e:
        print(f"Database setup error: {e}")
        # Continue anyway - app might still work
        pass
    
    # Make helper functions available in templates
    app.jinja_env.globals['get_crypto_icon'] = get_crypto_icon
    app.jinja_env.globals['get_crypto_gradient'] = get_crypto_gradient

@app.route("/")
def index():
    return "🚀 Flask App Running Successfully!"
