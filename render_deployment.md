# Render.com Deployment Guide for USDT Staking Platform

## Prerequisites

1. **GitHub Repository**: Push your code to GitHub
2. **Render Account**: Sign up at https://render.com
3. **Environment Variables**: Prepare the following secrets

## Required Environment Variables

```bash
# Database
DATABASE_URL=postgresql://username:password@hostname:port/database_name

# Security
SECRET_KEY=your-super-secret-key-here

# Blockchain APIs
MORALIS_API_KEY=your-moralis-api-key
BSCSCAN_API_KEY=your-bscscan-api-key-optional

# Session Security
SESSION_SECRET=another-secret-key-for-sessions
```

## Deployment Steps

### 1. Create PostgreSQL Database on Render

1. Go to Render Dashboard
2. Click "New" → "PostgreSQL"
3. Name: `usdt-staking-db`
4. Plan: Choose your preferred plan
5. Note down the database credentials

### 2. Create Web Service

1. Click "New" → "Web Service"
2. Connect your GitHub repository
3. Configure the following:

**Basic Settings:**
- Name: `usdt-staking-platform`
- Environment: `Python 3`
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 main:app`

**Environment Variables:**
Add all the required environment variables from the list above.

### 3. Required Files

Ensure these files are in your repository:

**requirements.txt:**
```
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
sqlalchemy==2.0.23
trafilatura==1.6.4
web3==6.11.4
pyjwt==2.8.0
oauthlib==3.2.2
flask-dance==7.0.0
```

**runtime.txt** (optional):
```
python-3.11.6
```

### 4. Database Migration

After first deployment, run database migration:

1. Go to your Render service dashboard
2. Open the "Shell" tab
3. Run: `python -c "from app import app, db; app.app_context().push(); db.create_all()"`

### 5. Admin User Setup

Create the first admin user:

```python
from app import app, db
from models import User

with app.app_context():
    admin = User(
        username='admin',
        email='admin@yourdomain.com',
        phone_number='+1234567890',
        is_admin=True
    )
    admin.set_password('your-secure-password')
    db.session.add(admin)
    db.session.commit()
```

## Post-Deployment Configuration

### 1. Update Blockchain Settings

1. Login to admin panel: `https://yourapp.onrender.com/admin-access`
2. Go to "Deposit APIs" section
3. Update Moralis API settings
4. Configure wallet addresses

### 2. Add Initial Coins

Add cryptocurrency data:
- USDT (min: $10)
- BTC (min: $250)
- ETH (min: $170)
- BNB (min: $90)
- LTC (min: $130)

### 3. Configure Staking Plans

Set up staking durations and rates:
- 7 days: 0.5% daily
- 15 days: 0.8% daily
- 30 days: 1.0% daily
- 90 days: 1.5% daily
- 120 days: 1.7% daily
- 180 days: 2.0% daily

## Performance Optimizations

### 1. Static File Serving

Render automatically serves static files, but consider using a CDN for better performance:

```python
# In app.py
if os.environ.get('RENDER'):
    app.config['STATIC_URL_PATH'] = '/static'
```

### 2. Database Connection Pooling

Already configured in `app.py`:

```python
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
    "pool_size": 10,
    "max_overflow": 20
}
```

### 3. Gunicorn Configuration

Optimized for Render in start command:
- 2 workers for basic plan
- 120-second timeout for blockchain operations
- Proper port binding

## Security Considerations

1. **HTTPS**: Automatically provided by Render
2. **Environment Variables**: Never commit secrets to repository
3. **Database**: Use strong passwords and restrict access
4. **API Keys**: Rotate periodically

## Monitoring

### Health Check Endpoint

Available at: `https://yourapp.onrender.com/health`

Returns:
```json
{
    "status": "healthy",
    "service": "usdt-staking-platform",
    "version": "1.0.0"
}
```

### Logs

Access logs through Render dashboard:
1. Go to your service
2. Click "Logs" tab
3. Monitor for errors and performance issues

## Troubleshooting

### Common Issues

1. **Build Failed**: Check requirements.txt syntax
2. **Database Connection**: Verify DATABASE_URL format
3. **Static Files**: Ensure UPLOAD_FOLDER permissions
4. **API Errors**: Check MORALIS_API_KEY validity

### Debug Mode

For debugging, temporarily add:
```bash
FLASK_DEBUG=1
```

**Remember to remove before production!**

## Backup Strategy

1. **Database**: Render provides automatic backups
2. **Uploaded Files**: Consider external storage (AWS S3)
3. **Configuration**: Keep environment variables documented

## Custom Domain (Optional)

1. Go to service settings
2. Add custom domain
3. Configure DNS CNAME record
4. SSL certificate automatically provided

Your USDT Staking Platform will be live at: `https://yourapp.onrender.com`